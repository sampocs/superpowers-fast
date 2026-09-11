"""Per-tier speed and bugs-that-got-through report for Claude Code sessions.

Usage:
  python3 scripts/session-analysis/report.py [--projects tenor-studio,diffalo]
      [--since 2026-09-11] [--projects-root ~/.claude/projects] [--no-github]
"""

import argparse
import datetime
import os
import re
import statistics
from dataclasses import dataclass

import gh_client
import transcripts

EXTERNAL_REVIEW_PATTERN = re.compile(r"\bcodex\b", re.IGNORECASE)
EXTERNAL_FIX_PATTERN = re.compile(r"\bfix\b.*\bcodex\b", re.IGNORECASE)
NUMBERED_FINDING_PATTERN = re.compile(r"^\s*\d+\.\s", re.MULTILINE)
FOLLOWUP_WINDOW_DAYS = 14
DEFAULT_PROJECTS_ROOT = "~/.claude/projects"


@dataclass
class SessionOutcome:
    session: transcripts.Session
    minutes_to_pr: float
    minutes_after_pr: float
    external_review_agents: int
    first_external_findings: int | None
    ci_failures_after_pr: int | None
    followup_fix_prs: int | None


def main() -> None:
    args = parse_args()
    sessions = transcripts.load_sessions(
        projects_root=os.path.expanduser(args.projects_root),
        project_filter=args.projects,
        since=args.since,
    )
    outcomes = [
        outcome
        for session in sessions
        if (outcome := measure(session=session, use_github=not args.no_github))
    ]
    print_sessions(outcomes=outcomes)
    print_tier_summary(outcomes=outcomes)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--projects-root", default=DEFAULT_PROJECTS_ROOT)
    parser.add_argument(
        "--projects",
        type=lambda raw: [name for name in raw.split(",") if name],
        default=[],
        help="comma-separated substrings of project directory names",
    )
    parser.add_argument("--since", type=datetime.date.fromisoformat, default=None)
    parser.add_argument(
        "--no-github",
        action="store_true",
        help="skip gh calls (CI failures, follow-up fix PRs)",
    )
    return parser.parse_args()


def measure(session: transcripts.Session, use_github: bool) -> SessionOutcome | None:
    """Speed and outcome metrics for a session's first PR; None if it linked no PR."""
    if not session.pull_requests:
        return None

    first_pr = session.pull_requests[0]
    details = (
        gh_client.pull_request_details(repo=first_pr.repo, number=first_pr.number)
        if use_github
        else None
    )

    return SessionOutcome(
        session=session,
        minutes_to_pr=transcripts.active_minutes(
            records=session.records, start=session.start, end=first_pr.linked_at
        ),
        minutes_after_pr=transcripts.active_minutes(
            records=session.records, start=first_pr.linked_at, end=session.end
        ),
        external_review_agents=sum(
            1
            for agent in session.subagents
            if EXTERNAL_REVIEW_PATTERN.search(agent.description)
        ),
        first_external_findings=first_external_findings(subagents=session.subagents),
        ci_failures_after_pr=gh_client.ci_failures_after_open(details=details)
        if details
        else None,
        followup_fix_prs=gh_client.followup_fix_prs(
            details=details, window_days=FOLLOWUP_WINDOW_DAYS
        )
        if details
        else None,
    )


def first_external_findings(subagents: list[transcripts.Subagent]) -> int | None:
    """Numbered findings handed to the first external-review fixer — a proxy for pass-1 findings."""
    fixer = next(
        (
            agent
            for agent in subagents
            if EXTERNAL_FIX_PATTERN.search(agent.description)
        ),
        None,
    )
    if fixer is None:
        return None
    return len(NUMBERED_FINDING_PATTERN.findall(fixer.first_prompt))


def print_sessions(outcomes: list[SessionOutcome]) -> None:
    print(
        f"{'session':8s} {'project':28s} {'tier':16s} {'pr':>6s} {'min→PR':>7s} {'after':>7s} "
        f"{'ext':>4s} {'ext#1':>5s} {'CI✗':>4s} {'fixPRs':>6s}"
    )
    for outcome in sorted(
        outcomes, key=lambda item: (item.session.tier, item.session.start)
    ):
        session = outcome.session
        print(
            f"{session.session_id[:8]:8s} {session.project[-28:]:28s} {session.tier:16s} "
            f"{session.pull_requests[0].number:>6d} {outcome.minutes_to_pr:7.1f} {outcome.minutes_after_pr:7.1f} "
            f"{outcome.external_review_agents:4d} {format_optional(value=outcome.first_external_findings):>5s} "
            f"{format_optional(value=outcome.ci_failures_after_pr):>4s} {format_optional(value=outcome.followup_fix_prs):>6s}"
        )


def print_tier_summary(outcomes: list[SessionOutcome]) -> None:
    print(
        "\nBY TIER (minutes are medians; CI failures and follow-up fix PRs are means)"
    )
    for tier in transcripts.Tier:
        group = [outcome for outcome in outcomes if outcome.session.tier == tier]
        if not group:
            continue

        ci_values = [
            outcome.ci_failures_after_pr
            for outcome in group
            if outcome.ci_failures_after_pr is not None
        ]
        fix_values = [
            outcome.followup_fix_prs
            for outcome in group
            if outcome.followup_fix_prs is not None
        ]
        print(
            f"  {tier:16s} n={len(group):3d}  "
            f"min→PR={statistics.median(outcome.minutes_to_pr for outcome in group):6.1f}  "
            f"after={statistics.median(outcome.minutes_after_pr for outcome in group):6.1f}  "
            f"CI✗={format_mean(values=ci_values)}  fix PRs={format_mean(values=fix_values)}"
        )


def format_optional(value: int | None) -> str:
    return "-" if value is None else str(value)


def format_mean(values: list[int]) -> str:
    return f"{statistics.mean(values):.2f}" if values else "-"


if __name__ == "__main__":
    main()
