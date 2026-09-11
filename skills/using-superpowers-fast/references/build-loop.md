# Build Loop

Shared by `quick-change` (Simple), `lean-build` (Medium), and `subagent-driven-development` (Large).

## Pre-flight

About a minute, before writing code:

1. `git fetch`.
2. Look for overlap: `git log --oneline -10 origin/main -- <paths you'll touch>` and, if `gh` is available, `gh pr list --search "<path or keyword>"`. Recent overlap → rebase first. An open PR already doing the work → tell the user before building.
3. Baseline: `gh run list --branch main --limit 3` (or the repo's CI). If `main` is red, note the failing checks in `.superpowers/baseline.md`. Check a later failure against the baseline — and, if unclear, re-run it alone on `origin/main` — before debugging it as yours.
4. Follow the repo's or user's branching policy; never build on `main` directly.

## The loop

```
build — targeted tests as you go
  → full suite; fix until green
  → review
  → fixes; each fixer re-runs the tests covering its change
  → scoped re-review of any fix that touched logic
  → full suite again, only if fixes changed code
  → Finish
```

| | Simple | Medium | Large |
|---|---|---|---|
| **Builds** | main agent | 1–3 lean implementers | SDD tasks, with TDD |
| **Review** | one fresh-eyes reviewer: standard tier; most capable if the diff touches money, auth, or state machines | one final whole-branch review, most capable tier | per-task review on tasks tagged `Review: yes`, plus a final whole-branch review, most capable tier |
| **Fixes** | main agent, inline | Critical/Important → one standard-tier fixer; then Minor → one cheap-tier fixer | same as Medium |

- **Targeted tests** = the tests covering the code you changed. Never the full suite while iterating.
- **Full-suite failures:** check the baseline first. Pre-existing failures are reported, not fixed.
- **Fixers** get their band's complete findings list — never one fixer per finding — plus the covering test commands. Each reports the command it ran and the output.
- **Scoped re-review:** only the fix diffs, only when a fix touched logic, whatever the severity. Fixes that change only comments, tests, or constants skip it.
- **Cap:** at most two fix → re-review rounds. Then stop and tell the user what's left.
- **Bug fixes:** a regression test that fails before the fix.
- A clean review means one full-suite run; a review with fixes means two.

## Right-first-time checklist

Give this to every implementer and fixer; apply it yourself in `quick-change`.

1. Changed behavior → update the comments and docstrings that describe it.
2. Each test must fail if the behavior breaks: assert effects, not calls, substrings, or tautologies; test negative cases with non-default values.
3. Cover every branch, call site, and state transition you touched.
4. Reuse existing constants and helpers; don't redeclare them.

## Finish

1. Push the branch.
2. Open the PR per the repo's policy (AGENTS.md / CLAUDE.md); otherwise `gh pr create` with a summary and the test evidence.
3. Run any repo-specific post-PR steps (e.g. Definition of Done, external review).
4. Remove worktrees in the background.

No merge / PR / keep / discard prompt.

## Worktrees

Use the repo's or user's worktree tool when one is configured (e.g. `git gtr new <branch> --yes`); otherwise `git worktree add`. One worktree per parallel implementer — two agents in one tree race on the git index, even with disjoint files. Create them in one batch and confirm N paths for N implementers before dispatching.
