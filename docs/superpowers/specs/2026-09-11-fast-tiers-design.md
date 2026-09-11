# superpowers-fast: Tiered Workflow

**Date:** 2026-09-11 · **Branch:** `fast-tiers`

## Problem

Superpowers produces high-quality work but is too slow: full-flow features take 2–5 agent-hours to reach a PR, then more for review loops. Teammates ship comparable changes in ~20 minutes without it. The fix is to size each task up front and spend process only where it pays.

## Evidence

From 33 PR-producing sessions (tenor-studio, diffalo) plus the review and fix transcripts of 13 full-flow runs:

- **Full flow:** median 145 agent-min to PR, then 145 more after it. Raw sessions: 31.
- **Overhead is fixed, not per-line:** per 100 lines of production code the full flow (13.5 min) is no slower than raw (14.4). But 4 of 12 full-flow PRs had <500 code LOC and still took 100–133 min; comparable raw PRs took ~30.
- **Fastest observed flow:** brainstorm → implement inline, 17 min median (n=3).
- **Subagent time:** implementing 28%; reviews, fix agents, and the Codex loop ~60%.
- **Parallelism:** waves reached 1.0–1.7× concurrency.
- **Turns dominate:** 75–98% of subagent time is model turns (~8 s/call main, ~4 s subagent). Full-suite runs are still ⅔ of test time.
- **Review yield:** final whole-branch review found real bugs nearly every time, often at the seams between parallel tasks. Per-task review found ~0.4 Critical/Important bugs per review, concentrated in stateful and money-path code. Re-reviews are cheap (~2 min) and catch fixer regressions. Codex passes 3+ mostly chase the previous fixer's regressions.
- **What reviews flag:** real bugs 35%, test gaps and weak tests 21%, stale comments 12%; typing, naming, and style ~10%, almost all Minor. 21% were preventable by a written rule, clustered in four rules (see Shared rules).
- **Debugging:** diagnosis took ~6 min; time went to delegated fix round trips (39–67 min), stale bases (~28 min of rework), re-triaging failures that already existed on `main`, and full suites inside the loop.

## Tiers

| Tier | Test | Examples |
|---|---|---|
| **Simple** | Nothing to decide; you'd do it without asking. | fix a misaligned button · patch a missing null check · add a field to an existing form |
| **Medium** | A few answers shape the build; fits in 1–3 chunks. | admin page with summary metrics · new endpoint + its UI · retry/backoff for a flaky integration |
| **Large** | New subsystem or cross-cutting change; needs a sequenced plan. | a backtesting engine · new order type across engine, API, UI · swapping auth providers |

- The agent sizes the task, announces it in one line, and proceeds without waiting: `Sizing as Medium: <reason>. Say "simple" or "large" to override.`
- Risk (money, auth, state machines) does not raise the tier. It strengthens review within the tier.
- Tiers can shift mid-flight: Simple's tripwires eject to Medium; brainstorming re-announces the tier if scope changes.

## Routing

- **Bootstrap:** `using-superpowers-fast` (injected at session start in Claude Code, Cursor, OpenCode) carries the rubric and routing:
  - build/change → size → Simple: `quick-change`; Medium/Large: `brainstorming`.
  - bug → `systematic-debugging` → root cause → size the fix → that tier.
- **Codex safety net:** Codex has no session-start hook (native skill discovery). `brainstorming` and `quick-change` open with "If no tier was announced, size first."

## Tier flows

### Simple — `quick-change` (replaces sp-lite)

1. **Align:** one line: what, which files, the riskiest assumption. Ask only if a wrong guess means redoing the work.
2. **Pre-flight.**
3. **Do:** follow existing patterns; apply the right-first-time checklist.
4. **Prove:** targeted test or run. Bug fix → failing regression test first.
5. **Review:** one fresh-eyes reviewer subagent, standard tier (most capable if the diff touches money, auth, or state machines). The main agent fixes findings inline.
6. **Finish.**

- **Tripwires → Medium:** more than ~150 lines of logic; a design choice with more than one reasonable answer; an ambiguity one question can't settle; the work stops feeling small.
- Keeps sp-lite's branching rule (follow the repo's or user's worktree policy) and its production-grade comment rule.
- Drops sp-lite's red-flags row that calls a review subagent "over-processing"; it contradicts the Review step.

### Medium — `brainstorming` → `lean-build` (new)

1. **Brainstorming,** full flow, minus questions with only one reasonable answer.
2. **Spec + Build plan** (a section of the spec): 1–3 chunks, each with files, interfaces produced/consumed, key decisions, tests to add, and `Depends on:` (other chunks, or none). No code; ~30–80 lines. One user review gate, then it runs to the PR without further gates.
3. **Pre-flight.**
4. **Implement:** one lean implementer per chunk.
   - Single chunk → one implementer on the feature branch.
   - Independent chunks → parallel, each in its own worktree (created in one batch).
   - Dependent chunks → in order.
5. **Lean implementer contract:** targeted tests only; tests written alongside the code (no per-step red-green); right-first-time checklist; one commit; report of ≤10 lines. Standard tier by default, most capable for tricky chunks.
6. **Merge** chunk branches one at a time; remove worktrees in the background.
7. **Final review:** one whole-branch review, most capable tier.
8. **Fix, in order:**
   1. One fixer (standard tier) for all Critical/Important findings.
   2. Scoped re-review (fix diff only) if those fixes touched logic.
   3. One cheap-tier fixer patches all Minor findings; no re-review.
9. **Finish.**

### Large — `brainstorming` → `writing-plans` → `subagent-driven-development`

Unchanged except:

- **Per-task review only on risky tasks.** The plan tags each task `Review: yes|no`; `yes` for state machines, money, auth, migrations, concurrency. The final whole-branch review always runs.
- **Minor findings** → cheap-tier fixer, no re-review.
- **Re-review** only after Critical/Important fixes that touched logic, scoped to the fix diff.
- **Tests:** implementers run targeted tests only; the full suite runs at the merge gate and at Finish.
- **Implementer prompt** carries the right-first-time checklist.
- **No execution-choice prompt:** `writing-plans` hands straight to SDD.
- **Kept:** detailed plans with code, TDD, foundation → parallel waves with `Depends on:`, one worktree per wave task.

## Shared rules

- **Pre-flight (~1 min):** `git fetch`; flag recent `main` commits or open PRs touching the target files; record `main`'s failing tests and CI status as the baseline, so later failures are compared, not re-triaged.
- **Tests:** targeted while iterating; the full suite once at Finish, after the last change, run by the main agent (Large also runs it at the merge gate). Every bug fix, any tier: a regression test that fails before the fix.
- **Fix loops:** at most two fix → re-review rounds per review; then surface what's left to the user.
- **Models:** plugin text names tiers only (cheap / standard / most capable), never vendor models. The mapping comes from the user's instructions; with none, use the session model.
- **Right-first-time checklist** (implementer prompts and `quick-change`):
  1. Changed behavior → update the comments and docstrings that describe it.
  2. Each test must fail if the behavior breaks: assert effects, not calls, substrings, or tautologies; test negative cases with non-default values.
  3. Cover every branch, call site, and state transition you touched.
  4. Reuse existing constants and helpers; don't redeclare them.
- **Finish:** full suite, push, open the PR per repo policy, remove worktrees in the background. No merge / PR / keep / discard prompt.
- **Worktrees:** use the repo's or user's tool (e.g. `git gtr`), else `git worktree`.

## Skill map

| Skill | Change |
|---|---|
| `using-superpowers` → `using-superpowers-fast` | Rubric, routing, model-tier rule; trimmed |
| `quick-change` | New (from sp-lite) |
| `brainstorming` | Tier check, skip one-answer questions, Build plan, tier-aware handoff; trimmed |
| `lean-build` | New |
| `writing-plans` | `Review: yes|no` per task; no execution-choice prompt |
| `subagent-driven-development` | Large changes above; drops references to cut skills |
| `requesting-code-review` | Shared final-review prompt; tier-based model wording |
| `systematic-debugging` | Hands the fix to a tier; trimmed |
| `verification-before-completion` | Trimmed; "execute the FULL command" → "execute it fresh" |
| `test-driven-development`, `receiving-code-review`, `writing-skills` | Unchanged |
| **Cut** | `executing-plans`, `dispatching-parallel-agents`, `using-git-worktrees`, `finishing-a-development-branch`, orphaned spec/plan reviewer prompts |

**Concision standard** for all new and edited text: cut pure duplication (diagrams restating a checklist, rationale sections, closing restatements) and anything the tiers overrule; keep every specific instruction, tightened. Reference: the approved middle-ground texts in `2026-09-11-fast-tiers-reference/` (verification-before-completion 668 → 406 words; brainstorming 1,553 → 790) are the starting point for those two skills. Large-only skills get only the targeted edits listed above.

## Rename

- **Plugin identity → `superpowers-fast`:** plugin and marketplace manifests (Claude Code, Cursor, Codex dev marketplace, OpenCode plugin), `package.json`, skill namespace `superpowers-fast:*`, bootstrap skill directory, hook text, README.
- **Paths written into user repos keep the old name:** `docs/superpowers/specs|plans`, `.superpowers/` scratch.
- **Repo `CLAUDE.md`** (upstream contributor rules) → short fork guidelines, including the concision standard and the vendor-neutral model rule.
- **History:** release notes and historical docs stay; add a new release-notes entry.

## Harnesses

- **Keep:** Claude Code, Cursor, Codex, OpenCode.
- **Cut:** Pi, Kimi, Gemini, Antigravity — packaging, reference docs, tests.
- **Also cut:** Codex portal-packaging scripts (`package-codex-plugin.sh`, `sync-to-codex-plugin.sh`, their tests) and upstream community files (`.github` templates, `FUNDING.yml`). The Codex dev marketplace (`.agents/plugins/marketplace.json`) stays.

## Rollout (after the plugin lands)

Steps 1–3 and 5 are plan tasks. Step 4 runs afterwards as its own Medium task through the new plugin.

1. Install `superpowers-fast` in all four harnesses. Uninstall upstream `superpowers` (Claude Code; Codex ×2) and the current drop-in fork (installed as `superpowers` from the `superpowers-fast` marketplace).
2. Delete `~/.claude/skills/sp-lite`.
3. In `~/.claude/AGENTS.md`: delete "Subagent Parallelization"; update superpowers skill names. Update `~/.cursor/rules/brainstorm-via-superpowers-only.mdc` and both `/green-light` copies (Claude Code, OpenCode).
4. **Dogfood (Medium): unify agent rules at `~/.agents/AGENTS.md`**, the real file:
   - Merge `~/.claude/AGENTS.md`, `~/.codex/AGENTS.md` (stale copy), and the three Cursor rules.
   - Add a per-harness model-tier table, replacing "Subagent Model Selection" and `subagent-model-selection.mdc`.
   - Label Claude-only sections (claude-mux, `cm-rename`); put Cursor's `alwaysApply` frontmatter at the top.
   - Symlink `~/.claude/AGENTS.md`, `~/.codex/AGENTS.md`, `~/.config/opencode/AGENTS.md`, `~/.cursor/rules/agents.mdc` to it (a sync script if Cursor won't follow symlinks).
   - Copy it into `~/setup` (replacing `~/setup/CLAUDE.md`) and add an "Agent rules" section with the link commands to `~/setup/README.md`. `~/setup` stays a quarterly snapshot, not a link target.
5. **Optional, user's call:** cap tenor-studio's Codex review loop at 2 passes in its `AGENTS.md`.

## Verification

- **Plugin tests:** session-start hook test and shell lint pass after the rename; tests for cut harnesses and skills are removed.
- **Sizing smoke test:** six headless prompts (two per tier, from the rubric examples) through `tests/explicit-skill-requests`; each must announce the expected tier.
- **Measurement:** commit the transcript-analysis scripts to `scripts/session-analysis/`. Record agent-minutes per phase for the dogfood run, then re-run the per-tier numbers after a few weeks. Target for a Medium code feature: 50–65 agent-min (baseline 100–130).

## Out of scope

- Rewriting Large-only skill content beyond the changes listed.
- Syncing future upstream changes (manual cherry-picks from here on).
- Repo-specific policies beyond the optional tenor-studio cap.
