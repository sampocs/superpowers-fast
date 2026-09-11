"""Load Claude Code session transcripts for timing and outcome analysis.

A session lives at `<projects-root>/<project>/<session-id>.jsonl`. Its subagents
live beside it in `<session-id>/subagents/agent-*.jsonl`, each with a
`.meta.json` holding the dispatch description.
"""

import datetime
import glob
import json
import os
from dataclasses import dataclass
from enum import StrEnum

# A gap longer than this before a human message is time spent waiting on the human
IDLE_THRESHOLD_SECONDS = 20
TRANSCRIPT_SUFFIX = ".jsonl"
META_SUFFIX = ".meta.json"
SUBAGENT_META_GLOB = os.path.join("subagents", "*" + META_SUFFIX)
SKILL_TOOL_NAME = "Skill"
TIMESTAMP_KEY = "timestamp"
# User-role records the harness injects rather than a person typing
INJECTED_PREFIXES = (
    "<task-notification",
    "<local-command",
    "<system-reminder",
    "[Request interrupted",
    "Caveat:",
)


class RecordType(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    PR_LINK = "pr-link"


class BlockType(StrEnum):
    TEXT = "text"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"


class Tier(StrEnum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    LARGE = "large"
    LEGACY_FULL = "legacy-full"
    BRAINSTORM_ONLY = "brainstorm-only"
    LEGACY_LITE = "legacy-lite"
    NONE = "none"


# Priority order: the first entry matching any skill the session invoked sets its tier
TIER_BY_SKILLS: list[tuple[frozenset[str], Tier]] = [
    (frozenset({"superpowers-fast:subagent-driven-development"}), Tier.LARGE),
    (frozenset({"superpowers-fast:lean-build", "lean-build"}), Tier.MEDIUM),
    (frozenset({"superpowers-fast:quick-change", "quick-change"}), Tier.SIMPLE),
    (
        frozenset(
            {"superpowers:subagent-driven-development", "subagent-driven-development"}
        ),
        Tier.LEGACY_FULL,
    ),
    (
        frozenset(
            {
                "superpowers:brainstorming",
                "superpowers-fast:brainstorming",
                "brainstorming",
            }
        ),
        Tier.BRAINSTORM_ONLY,
    ),
    (frozenset({"sp-lite"}), Tier.LEGACY_LITE),
]


@dataclass
class Subagent:
    description: str
    start: datetime.datetime
    end: datetime.datetime
    first_prompt: str

    @property
    def minutes(self) -> float:
        return (self.end - self.start).total_seconds() / 60


@dataclass
class PullRequestLink:
    repo: str
    number: int
    linked_at: datetime.datetime


@dataclass
class Session:
    session_id: str
    project: str
    tier: Tier
    records: list[dict]
    pull_requests: list[PullRequestLink]
    subagents: list[Subagent]

    @property
    def start(self) -> datetime.datetime:
        return parse_record_time(record=self.records[0])

    @property
    def end(self) -> datetime.datetime:
        return parse_record_time(record=self.records[-1])


def load_sessions(
    projects_root: str, project_filter: list[str], since: datetime.date | None
) -> list[Session]:
    """Sessions whose project directory matches the filter and that started on or after since."""
    paths = [
        path
        for path in glob.glob(os.path.join(projects_root, "*", "*" + TRANSCRIPT_SUFFIX))
        if not project_filter
        or any(
            name in os.path.basename(os.path.dirname(path)) for name in project_filter
        )
    ]
    sessions = [session for path in paths if (session := load_session(path=path))]
    if since is None:
        return sessions
    return [session for session in sessions if session.start.date() >= since]


def load_session(path: str) -> Session | None:
    """Parse one transcript; None for sessions no human ever prompted."""
    records = [record for record in read_jsonl(path=path) if TIMESTAMP_KEY in record]
    if not any(is_human_message(record=record) for record in records):
        return None

    return Session(
        session_id=os.path.basename(path).removesuffix(TRANSCRIPT_SUFFIX),
        project=os.path.basename(os.path.dirname(path)),
        tier=detect_tier(skills=invoked_skills(records=records)),
        records=records,
        pull_requests=pull_request_links(records=records),
        subagents=load_subagents(session_path=path),
    )


def is_human_message(record: dict) -> bool:
    """A real human prompt — not a tool result, meta record, sidechain, or injected notice."""
    if (
        record.get("type") != RecordType.USER
        or record.get("isMeta")
        or record.get("isSidechain")
    ):
        return False

    content = record["message"].get("content")
    if isinstance(content, list):
        if any(block.get("type") == BlockType.TOOL_RESULT for block in content):
            return False
        content = " ".join(
            block.get("text", "")
            for block in content
            if block.get("type") == BlockType.TEXT
        )

    text = (content or "").strip()
    return bool(text) and not text.startswith(INJECTED_PREFIXES)


def active_minutes(
    records: list[dict], start: datetime.datetime, end: datetime.datetime
) -> float:
    """Wall minutes between start and end, minus gaps spent waiting on a human reply."""
    window = [
        record for record in records if start <= parse_record_time(record=record) <= end
    ]
    waiting_seconds = sum(
        gap
        for previous, current in zip(window, window[1:])
        if is_human_message(record=current)
        and (gap := seconds_between(earlier=previous, later=current))
        > IDLE_THRESHOLD_SECONDS
    )
    return ((end - start).total_seconds() - waiting_seconds) / 60


def detect_tier(skills: set[str]) -> Tier:
    return next((tier for names, tier in TIER_BY_SKILLS if names & skills), Tier.NONE)


def invoked_skills(records: list[dict]) -> set[str]:
    return {
        block["input"].get("skill", "")
        for record in records
        if record.get("type") == RecordType.ASSISTANT
        for block in record["message"].get("content") or []
        if block.get("type") == BlockType.TOOL_USE
        and block.get("name") == SKILL_TOOL_NAME
    }


def pull_request_links(records: list[dict]) -> list[PullRequestLink]:
    """Distinct PRs the session linked, in order of first appearance."""
    links: dict[tuple[str, int], PullRequestLink] = {}
    for record in records:
        if record.get("type") != RecordType.PR_LINK:
            continue
        key = (record["prRepository"], record["prNumber"])
        links.setdefault(
            key,
            PullRequestLink(
                repo=key[0], number=key[1], linked_at=parse_record_time(record=record)
            ),
        )
    return list(links.values())


def load_subagents(session_path: str) -> list[Subagent]:
    session_dir = session_path.removesuffix(TRANSCRIPT_SUFFIX)
    subagents = [
        subagent
        for meta_path in glob.glob(os.path.join(session_dir, SUBAGENT_META_GLOB))
        if (subagent := load_subagent(meta_path=meta_path))
    ]
    return sorted(subagents, key=lambda subagent: subagent.start)


def load_subagent(meta_path: str) -> Subagent | None:
    with open(meta_path) as handle:
        meta = json.load(handle)
    transcript_path = meta_path.removesuffix(META_SUFFIX) + TRANSCRIPT_SUFFIX
    records = [
        record for record in read_jsonl(path=transcript_path) if TIMESTAMP_KEY in record
    ]
    if not records:
        return None

    return Subagent(
        description=meta.get("description", ""),
        start=parse_record_time(record=records[0]),
        end=parse_record_time(record=records[-1]),
        first_prompt=first_prompt_text(records=records),
    )


def first_prompt_text(records: list[dict]) -> str:
    first_user = next(
        (record for record in records if record.get("type") == RecordType.USER), None
    )
    if first_user is None:
        return ""

    content = first_user["message"].get("content")
    if isinstance(content, str):
        return content
    return "\n".join(
        block.get("text", "")
        for block in content or []
        if block.get("type") == BlockType.TEXT
    )


def read_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path) as handle:
        return [
            record
            for line in handle
            if (record := parse_json_line(line=line)) is not None
        ]


def parse_json_line(line: str) -> dict | None:
    # An interrupted session can leave a truncated final line
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def seconds_between(earlier: dict, later: dict) -> float:
    return (
        parse_record_time(record=later) - parse_record_time(record=earlier)
    ).total_seconds()


def parse_record_time(record: dict) -> datetime.datetime:
    return parse_iso(raw=record[TIMESTAMP_KEY])


def parse_iso(raw: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
