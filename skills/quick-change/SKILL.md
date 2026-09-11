---
name: quick-change
description: Use for Simple-tier changes - one clear fix or feature, nothing to decide, a handful of files and up to ~150 lines of logic. Align, do, prove, one fresh-eyes review; ejects to Medium when the work stops being small.
---

# Quick Change

The Simple tier: align on intent, make the change, prove it, get one fresh-eyes review. No spec, no plan, no implementer subagents.

**Tier check.** If no tier was announced, size the task per `using-superpowers-fast` first. Anything that isn't Simple → `brainstorming`.

Agents already "know" to align and verify; under momentum they skip both. This skill makes them non-optional and evidence-bearing. Keep the teeth.

## Use when ALL hold

- One clear fix or feature; you can name it in one sentence without hedging.
- No design choice with more than one reasonable answer.
- A handful of files, up to ~150 lines of logic.

**Below the floor** (typo, rename, comment-only): just do it — no review — but still prove anything provable.

## 1. Align (before any code)

One short message: **what** you'll change, **which files**, and **the single assumption most likely to be wrong**.

- Low-stakes assumption → proceed in the same turn; the user can interrupt.
- Load-bearing (wrong means redoing the work) → ask that one question first. Usually there are zero questions.

Never skip the one-liner.

## 2. Pre-flight

Per `../using-superpowers-fast/references/build-loop.md` — including its branching rule.

## 3. Do

- Follow existing patterns. Small diff, in scope — "while I'm here" changes are a tripwire.
- Apply the right-first-time checklist (build-loop.md).
- Comments are production-grade: sparse, *why* not *what*, matching the file's density. Delete anything that narrates the edit ("now also handles X"). Test: would it make sense to a cold reader a year from now?
- **Prove it:** run the targeted test or exercise the change and read the real output. Bug fix → a regression test that fails before the fix. No runtime surface (docs, config) → say so and show the diff reads correctly.

## 4. The loop

Run the build loop from the full suite on, Simple column. The reviewer is one fresh-eyes subagent that gets the diff and the one-sentence task, nothing else:

> Read this diff cold. What interaction or code path could be wrong that a happy-path test wouldn't catch? Report Critical / Important / Minor with file:line.

Standard tier; most capable if the diff touches money, auth, or state machines. Fix findings inline; re-review per the loop's rules.

## 5. Finish

Per build-loop.md.

## Tripwires — eject to Medium

The moment ANY becomes true, STOP, say "This grew past Simple — switching to Medium," and invoke `brainstorming`. Don't push through:

- More than ~150 lines of logic, or it sprawls across many files.
- A design choice with more than one reasonable answer.
- An ambiguity one quick question can't settle.
- The risk demands a test harness that doesn't exist yet.
- It stopped feeling small.

Ejecting is a success, not a failure.

## Skip (permission granted)

- ❌ Spec and plan documents.
- ❌ Implementer subagents and worktree fan-out — the reviewer is the one subagent.
- ❌ TDD red-green ritual beyond the bug-fix regression test.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll infer what they meant and start." | State the one-liner first. |
| "This obviously works." | Prove it with real output. |
| "While I'm in here, let me also fix…" | Scope creep. Do the one thing. |
| "A comment here would explain this change." | Narration. Comment the *why* or delete it. |
| "I should write a spec to be safe." | Over-processing. You're in Simple. |
| "It's getting big but I'm almost done." | Tripwire. Eject to Medium. |
| "It's tiny, skip the review." | The review catches the path you didn't run. Dispatch it. |
