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

Record the SHA from `git rev-parse HEAD` as BASE, then dispatch one implementer per chunk with [implementer-prompt.md](implementer-prompt.md):

- **One chunk:** one implementer on the feature branch.
- **Two or three chunks:** one worktree per chunk (Worktrees in build-loop.md — without worktrees, run them one at a time on the branch). Dispatch every chunk whose `Depends on:` is satisfied in one message. When a chunk merges (step 4), dispatch the chunks waiting on it, branched from the updated feature branch.

Model: standard tier by default; most capable for chunks needing design judgment or broad codebase understanding. Always set it explicitly.

| Report | Action |
|---|---|
| DONE | Continue. |
| DONE_WITH_CONCERNS | Read them; resolve correctness or scope concerns before merging. |
| NEEDS_CONTEXT | Answer and re-dispatch. |
| BLOCKED | More context, a more capable model, or a smaller chunk. Spec wrong → ask the user. |

## 4. Merge

As each chunk reports DONE, merge its branch into the feature branch — one at a time, resolving conflicts as they surface — and remove its worktree in the background. Continue until every chunk has merged.

## 5. The loop

Run the build loop from the full suite on, Medium column:

- **Final review:** `../subagent-driven-development/scripts/review-package <BASE> HEAD`, then dispatch [code-reviewer.md](../requesting-code-review/code-reviewer.md) on the most capable tier with the spec path and the printed package path.
- **Fixers:** the reviewer's standard-tier fix brief verbatim to one standard-tier fixer, then its cheap-tier brief to one cheap-tier fixer. Add the branch path to each.
- **Scoped re-review:** `review-package <pre-fix SHA> HEAD`, same template, with `[PLAN_OR_REQUIREMENTS]` = the findings list.

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
