"""Unit tests for scripts/session-analysis/transcripts.py.

Run: python3 tests/session-analysis/test_transcripts.py
"""

import datetime
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "session-analysis"),
)
import transcripts  # noqa: E402

START = datetime.datetime(2026, 9, 11, 12, 0, tzinfo=datetime.timezone.utc)


def at(minutes: float) -> str:
    return (
        (START + datetime.timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")
    )


def after(minutes: float) -> datetime.datetime:
    return START + datetime.timedelta(minutes=minutes)


def human(minutes: float, text: str) -> dict:
    return {"type": "user", "timestamp": at(minutes), "message": {"content": text}}


def assistant(minutes: float, skill: str | None = None) -> dict:
    block = (
        {"type": "tool_use", "name": "Skill", "input": {"skill": skill}}
        if skill
        else {"type": "text", "text": "ok"}
    )
    return {
        "type": "assistant",
        "timestamp": at(minutes),
        "message": {"content": [block]},
    }


class ActiveMinutesTest(unittest.TestCase):
    def test_excludes_wait_before_human_reply(self) -> None:
        records = [
            human(minutes=0, text="build it"),
            assistant(minutes=5),
            human(minutes=65, text="looks good"),
            assistant(minutes=70),
        ]

        # 70 wall minutes; the 60-minute gap before the second prompt is the human thinking
        self.assertAlmostEqual(
            transcripts.active_minutes(
                records=records, start=START, end=after(minutes=70)
            ),
            10,
        )

    def test_short_gap_before_human_reply_counts_as_active(self) -> None:
        records = [
            human(minutes=0, text="go"),
            assistant(minutes=1),
            human(minutes=1.1, text="and this"),
        ]

        self.assertAlmostEqual(
            transcripts.active_minutes(
                records=records, start=START, end=after(minutes=1.1)
            ),
            1.1,
        )


class DetectTierTest(unittest.TestCase):
    def test_large_outranks_brainstorming(self) -> None:
        skills = {
            "superpowers-fast:brainstorming",
            "superpowers-fast:subagent-driven-development",
        }
        self.assertEqual(transcripts.detect_tier(skills=skills), transcripts.Tier.LARGE)

    def test_legacy_sdd_is_not_large(self) -> None:
        skills = {"superpowers:subagent-driven-development"}
        self.assertEqual(
            transcripts.detect_tier(skills=skills), transcripts.Tier.LEGACY_FULL
        )

    def test_no_workflow_skill_is_none(self) -> None:
        self.assertEqual(
            transcripts.detect_tier(skills={"cm-rename"}), transcripts.Tier.NONE
        )


class HumanMessageTest(unittest.TestCase):
    def test_task_notification_is_not_human(self) -> None:
        record = human(minutes=0, text="<task-notification>done</task-notification>")
        self.assertFalse(transcripts.is_human_message(record=record))

    def test_tool_result_is_not_human(self) -> None:
        record = {
            "type": "user",
            "timestamp": at(0),
            "message": {"content": [{"type": "tool_result", "content": "x"}]},
        }
        self.assertFalse(transcripts.is_human_message(record=record))

    def test_plain_prompt_is_human(self) -> None:
        self.assertTrue(
            transcripts.is_human_message(record=human(minutes=0, text="add a page"))
        )


class LoadSessionTest(unittest.TestCase):
    def test_reads_tier_and_distinct_pull_requests(self) -> None:
        records = [
            human(minutes=0, text="add the admin page"),
            assistant(minutes=1, skill="superpowers-fast:lean-build"),
            {
                "type": "pr-link",
                "timestamp": at(30),
                "prNumber": 7,
                "prRepository": "acme/app",
            },
            {
                "type": "pr-link",
                "timestamp": at(31),
                "prNumber": 7,
                "prRepository": "acme/app",
            },
        ]
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "proj", "abc.jsonl")
            os.makedirs(os.path.dirname(path))
            with open(path, "w") as handle:
                handle.write("\n".join(json.dumps(record) for record in records))
            session = transcripts.load_session(path=path)

        self.assertEqual(session.tier, transcripts.Tier.MEDIUM)
        self.assertEqual(
            [(link.repo, link.number) for link in session.pull_requests],
            [("acme/app", 7)],
        )
        self.assertEqual(session.pull_requests[0].linked_at, after(minutes=30))


if __name__ == "__main__":
    unittest.main()
