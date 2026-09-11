---
name: requesting-code-review
description: Use when completing tasks, implementing major features, or before merging to verify work meets requirements
---

# Requesting Code Review

Dispatch a reviewer subagent with precisely crafted context — never your session's history — so it judges the work product, not your thought process.

## When

- **In a tier flow:** as the build loop says (`../using-superpowers-fast/references/build-loop.md`): Simple — one fresh-eyes reviewer; Medium — one final whole-branch review; Large — tasks tagged `Review: yes`, plus a final whole-branch review.
- **Ad hoc:** before merging, when stuck, or after fixing a complex bug.

## How

1. Pick the range. Whole branch: `BASE=$(git merge-base origin/main HEAD)`. One task: the commit recorded before it started — never `HEAD~1`, which drops all but the last commit.
2. Package the diff: `../subagent-driven-development/scripts/review-package $BASE HEAD` prints the file it wrote.
3. Dispatch a `general-purpose` subagent with [code-reviewer.md](code-reviewer.md). Fill in:
   - `[MODEL]` — most capable tier for whole-branch reviews
   - `[DESCRIPTION]` — what was built
   - `[PLAN_OR_REQUIREMENTS]` — spec or plan path, or the requirements
   - `[BASE_SHA]`, `[HEAD_SHA]` — the range
   - `[DIFF_FILE]` — the path `review-package` printed

## Act on the findings

Simple fixes inline. Medium and Large:

- **Critical/Important** → one standard-tier fixer with the reviewer's standard-tier fix brief.
- **Minor** → then one cheap-tier fixer with the cheap-tier fix brief.
- **Re-review** only the fix diffs, only when a fix touched logic. At most two rounds, then tell the user what's left.
- **Reviewer wrong?** Push back with technical reasoning and the code or tests that prove it.

## Red Flags

- Skipping review because "it's simple" — Simple still gets one fresh-eyes review.
- Ignoring Critical findings, or proceeding with unfixed Important ones.
- One fixer per finding instead of one per severity band.
- Arguing with valid technical feedback.
