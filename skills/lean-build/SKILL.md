---
name: lean-build
description: Use to build a Medium-tier spec after brainstorming - executes the spec's Build plan with 1-3 lean implementer subagents, then one final review
---

# Lean Build

Execute a Medium spec's Build plan: 1–3 lean implementers, one final review, straight to a PR. No per-chunk reviews.

**Continuous execution:** the user approved the spec. Don't pause between steps. Stop only for a BLOCKED implementer you can't unblock, a genuine ambiguity, the fix-loop cap, or done.

## 1. Read the spec

Read it once. Note the Build plan's chunks, their `Depends on:` lines, and binding constraints (exact values, formats, names).

## 2. Pre-flight

Per `../using-superpowers-fast/references/build-loop.md`, on the feature branch.

## 3. Implement

Record `BASE=$(git rev-parse HEAD)`, then dispatch one implementer per chunk with [implementer-prompt.md](implementer-prompt.md):

| Chunks | Dispatch |
|---|---|
| One | One implementer on the feature branch. |
| Independent (no `Depends on:` between them) | All in one message, each in its own worktree — created in one batch per Worktrees in build-loop.md. |
| Dependent | In `Depends on:` order; each starts from the previous chunk's commit. |

Model: standard tier by default; most capable for chunks needing design judgment or broad codebase understanding. Always set it explicitly.

| Report | Action |
|---|---|
| DONE | Continue. |
| DONE_WITH_CONCERNS | Read them; resolve correctness or scope concerns before merging. |
| NEEDS_CONTEXT | Answer and re-dispatch. |
| BLOCKED | More context, a more capable model, or a smaller chunk. Spec wrong → ask the user. |

## 4. Merge

Merge chunk branches into the feature branch one at a time, resolving conflicts as they surface. Remove chunk worktrees in the background.

## 5. The loop

Run the build loop from the full suite on, Medium column:

- **Final review:** `../subagent-driven-development/scripts/review-package $BASE HEAD`, then dispatch [code-reviewer.md](../requesting-code-review/code-reviewer.md) on the most capable tier with the spec path and the printed package path.
- **Fixers:** the reviewer's standard-tier fix brief verbatim to one standard-tier fixer, then its cheap-tier brief to one cheap-tier fixer. Add the branch path to each.
- **Scoped re-review:** `review-package` over the fix commits only, same template.

## 6. Finish

Per build-loop.md.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll review each chunk as it lands." | Medium has one final review. |
| "Two chunks touch the same file, so one worktree is fine." | Two agents in one tree race on the git index. One worktree each. |
| "One fixer per finding is cleaner." | One fixer per severity band, full list. |
| "The implementer should run the full suite." | Targeted tests only; the full suite runs once, after the merge. |
| "Let me check in before merging." | The user approved the spec. Keep going. |
