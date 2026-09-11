"""Static checks on skill text.

Run: python3 tests/skills/test_skill_references.py

- Every skill's frontmatter name matches its directory.
- Every `superpowers-fast:<name>` reference names an existing skill.
- No plugin text mentions a cut skill.
- Relative paths in skill markdown resolve.
- Skill text names model tiers, never vendor models.
"""

import glob
import os
import re
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
SKILL_FILE = "SKILL.md"
CUT_SKILLS = (
    "executing-plans",
    "dispatching-parallel-agents",
    "using-git-worktrees",
    "finishing-a-development-branch",
)
TOP_LEVEL_FILES = (
    "hooks/session-start",
    ".opencode/plugins/superpowers-fast.js",
    "README.md",
    "CLAUDE.md",
)
# writing-skills carries Anthropic's skill-authoring guide, which discusses models by name
VENDOR_CHECK_EXCLUDES = ("skills/writing-skills/",)
VENDOR_MODEL_PATTERN = re.compile(
    r"\b(opus|sonnet|haiku|gpt-\d|gemini)\b", re.IGNORECASE
)
NAMESPACED_SKILL_PATTERN = re.compile(r"superpowers-fast:([a-z0-9-]+)")
RELATIVE_PATH_PATTERN = re.compile(r"(?:\]\(|`)(\.\.?/[^)`\s#]+)")
FRONTMATTER_NAME_PATTERN = re.compile(r"^name:\s*(\S+)", re.MULTILINE)


def skill_names() -> set[str]:
    return {
        name
        for name in os.listdir(SKILLS_DIR)
        if os.path.isfile(os.path.join(SKILLS_DIR, name, SKILL_FILE))
    }


def skill_markdown_files() -> list[str]:
    return sorted(glob.glob(os.path.join(SKILLS_DIR, "**", "*.md"), recursive=True))


def scanned_files() -> list[str]:
    return skill_markdown_files() + [
        os.path.join(REPO_ROOT, name) for name in TOP_LEVEL_FILES
    ]


def read(path: str) -> str:
    with open(path) as handle:
        return handle.read()


def relative(path: str) -> str:
    return os.path.relpath(path, REPO_ROOT)


class SkillReferenceTest(unittest.TestCase):
    def test_frontmatter_name_matches_directory(self) -> None:
        for name in skill_names():
            match = FRONTMATTER_NAME_PATTERN.search(
                read(path=os.path.join(SKILLS_DIR, name, SKILL_FILE))
            )
            self.assertIsNotNone(match, f"{name}/{SKILL_FILE} has no frontmatter name")
            self.assertEqual(match.group(1), name)

    def test_namespaced_references_exist(self) -> None:
        known = skill_names()
        for path in scanned_files():
            for referenced in NAMESPACED_SKILL_PATTERN.findall(read(path=path)):
                self.assertIn(
                    referenced,
                    known,
                    f"{relative(path=path)} references missing skill {referenced}",
                )

    def test_no_cut_skill_references(self) -> None:
        for path in scanned_files():
            text = read(path=path)
            for cut in CUT_SKILLS:
                self.assertNotIn(
                    cut, text, f"{relative(path=path)} still mentions cut skill {cut}"
                )

    def test_relative_paths_resolve(self) -> None:
        for path in skill_markdown_files():
            for target in RELATIVE_PATH_PATTERN.findall(read(path=path)):
                resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
                self.assertTrue(
                    os.path.exists(resolved),
                    f"{relative(path=path)} → {target} does not exist",
                )

    def test_no_vendor_model_names(self) -> None:
        paths = skill_markdown_files() + [
            os.path.join(REPO_ROOT, "hooks", "session-start")
        ]
        for path in paths:
            if relative(path=path).startswith(VENDOR_CHECK_EXCLUDES):
                continue
            match = VENDOR_MODEL_PATTERN.search(read(path=path))
            self.assertIsNone(
                match,
                f"{relative(path=path)} names a vendor model: {match.group(0) if match else ''}",
            )


if __name__ == "__main__":
    unittest.main()
