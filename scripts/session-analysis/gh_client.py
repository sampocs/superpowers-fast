"""Thin wrappers over the `gh` CLI for pull-request outcome metrics."""

import datetime
import json
import re
import subprocess
from dataclasses import dataclass

import transcripts

FAILURE_CONCLUSION = "failure"
FIX_TITLE_PATTERN = re.compile(r"^fix\b", re.IGNORECASE)
# Specs and plans change with every feature; overlap there says nothing about follow-up fixes
IGNORED_PATH_PREFIXES = ("docs/",)
LIST_LIMIT = "100"


@dataclass
class PullRequestDetails:
    repo: str
    number: int
    head_ref: str
    created_at: datetime.datetime
    merged_at: datetime.datetime | None
    code_paths: set[str]


def pull_request_details(repo: str, number: int) -> PullRequestDetails | None:
    payload = run_gh(
        args=[
            "pr",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            "headRefName,createdAt,mergedAt,files",
        ]
    )
    if payload is None:
        return None

    merged_raw = payload.get("mergedAt")
    return PullRequestDetails(
        repo=repo,
        number=number,
        head_ref=payload["headRefName"],
        created_at=transcripts.parse_iso(raw=payload["createdAt"]),
        merged_at=transcripts.parse_iso(raw=merged_raw) if merged_raw else None,
        code_paths=code_paths(files=payload["files"]),
    )


def ci_failures_after_open(details: PullRequestDetails) -> int | None:
    """Failed CI runs on the PR's branch after the PR opened."""
    runs = run_gh(
        args=[
            "run",
            "list",
            "--repo",
            details.repo,
            "--branch",
            details.head_ref,
            "--limit",
            LIST_LIMIT,
            "--json",
            "conclusion,createdAt",
        ]
    )
    if runs is None:
        return None
    return sum(
        1
        for run in runs
        if run["conclusion"] == FAILURE_CONCLUSION
        and transcripts.parse_iso(raw=run["createdAt"]) >= details.created_at
    )


def followup_fix_prs(details: PullRequestDetails, window_days: int) -> int | None:
    """Merged `fix…` PRs within window_days of this PR's merge that touch the same code files."""
    if details.merged_at is None:
        return None

    window_end = details.merged_at + datetime.timedelta(days=window_days)
    search = f"merged:{details.merged_at.date().isoformat()}..{window_end.date().isoformat()}"
    candidates = run_gh(
        args=[
            "pr",
            "list",
            "--repo",
            details.repo,
            "--state",
            "merged",
            "--search",
            search,
            "--limit",
            LIST_LIMIT,
            "--json",
            "number,title,files",
        ]
    )
    if candidates is None:
        return None
    return sum(
        1
        for candidate in candidates
        if candidate["number"] != details.number
        and FIX_TITLE_PATTERN.match(candidate["title"])
        and details.code_paths & code_paths(files=candidate["files"])
    )


def code_paths(files: list[dict]) -> set[str]:
    return {
        item["path"]
        for item in files
        if not item["path"].startswith(IGNORED_PATH_PREFIXES)
    }


def run_gh(args: list[str]) -> list | dict | None:
    """Run `gh` and parse its JSON output; None when gh fails (no auth, no access, deleted PR)."""
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)
