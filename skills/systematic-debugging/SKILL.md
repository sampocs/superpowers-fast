---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
---

# Systematic Debugging

Random fixes waste time and create new bugs. **Always find the root cause before attempting a fix.** Symptom fixes are failure.

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

Use for any technical issue: test failures, production bugs, unexpected behavior, performance, build failures, integration issues. Especially under time pressure, when "one quick fix" seems obvious, or when a previous fix didn't work. Simple bugs have root causes too; systematic is faster than thrashing.

## Phase 1: Root Cause Investigation

Before attempting ANY fix:

1. **Read error messages carefully** — full stack traces, line numbers, file paths, error codes. They often contain the answer.
2. **Reproduce consistently** — exact steps, every time? If not reproducible, gather more data; don't guess.
3. **Check recent changes** — git diff, recent commits, new dependencies, config, environment. `git fetch` and `git log origin/main -- <paths>`: a teammate may already have fixed it. For a test failure, check whether it already fails on `main` (CI or the pre-flight baseline) before treating it as new.
4. **Gather evidence across components** — when the system has layers (CI → build → signing, API → service → database), instrument each boundary before proposing fixes: log what enters and exits, verify config propagation, check state per layer. Run once to find WHERE it breaks, then investigate that component.

   ```bash
   # Layer 1: workflow
   echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"
   # Layer 2: build script
   env | grep IDENTITY || echo "IDENTITY not in environment"
   # Layer 3: signing
   security find-identity -v
   ```

5. **Trace data flow** — for errors deep in the call stack, trace backward: where does the bad value originate, what called this with it? Fix at the source, not the symptom. Full technique: `root-cause-tracing.md`.

## Phase 2: Pattern Analysis

1. **Find working examples** of similar code in the same codebase.
2. **Read references completely** when implementing a pattern — every line, no skimming.
3. **List every difference** between working and broken, however small. Don't assume "that can't matter."
4. **Understand dependencies** — components, settings, config, environment, assumptions.

## Phase 3: Hypothesis and Testing

1. **Form a single hypothesis:** "I think X is the root cause because Y." Be specific.
2. **Test minimally** — the smallest change, one variable at a time.
3. **Verify before continuing** — worked → Phase 4; didn't → new hypothesis. Don't stack fixes.
4. **When you don't know,** say "I don't understand X." Ask or research; don't pretend.

## Phase 4: Fix

**Already inside a tier flow** (a build loop's full-suite step, a fixer, an implementer)? Don't re-size — fix within that flow and return to it. Otherwise, **size the fix** per `using-superpowers-fast` and announce it. Simple → fix within `quick-change`. Medium or Large → `brainstorming`, with the root cause as context. In every tier:

1. **Failing test first** — the simplest reproduction, automated if possible, a one-off script if there's no framework. It must fail before the fix.
2. **One fix** for the root cause. No "while I'm here" changes, no bundled refactoring.
3. **Verify** — the test passes, nothing else broke (targeted tests; full suite per the build loop), and the issue is actually resolved.
4. **If the fix doesn't work,** count your attempts. Fewer than 3 → back to Phase 1 with the new information. **3 or more → stop and question the architecture:** each fix revealing new coupling elsewhere, fixes needing massive refactoring, or new symptoms per fix mean the pattern is wrong, not the hypothesis. Discuss with your human partner before attempting more.

## When There's No Root Cause

If investigation shows the issue is truly environmental, timing-dependent, or external: document what you investigated, add appropriate handling (retry, timeout, clear error), and add logging for next time. But 95% of "no root cause" cases are incomplete investigation.

## Red Flags — STOP and return to Phase 1

| Thought | Reality |
|---------|---------|
| "Quick fix for now, investigate later" | The first fix sets the pattern. Do it right. |
| "Just try changing X and see" | That's guessing. Form a hypothesis. |
| "Add multiple changes, run tests" | You can't isolate what worked. |
| "Skip the test, I'll verify manually" | Untested fixes don't stick. |
| "It's probably X, let me fix that" | Seeing symptoms ≠ understanding the cause. |
| "Pattern says X but I'll adapt it" | Partial understanding guarantees bugs. Read it all. |
| "Here are the main problems: [fixes]" | That's proposing fixes before tracing data flow. |
| "One more fix attempt" (after 2+) | 3+ failures = architecture problem. Stop. |

**Your human partner's signals you're off track:** "Is that not happening?" (you assumed), "Will it show us…?" (add evidence gathering), "Stop guessing", "Ultra-think this" (question fundamentals), "We're stuck?" Any of these → Phase 1.

## Supporting Techniques (this directory)

- `root-cause-tracing.md` — trace a bug backward through the call stack
- `defense-in-depth.md` — add validation at multiple layers after finding the root cause
- `condition-based-waiting.md` — replace arbitrary timeouts with condition polling

Related: `test-driven-development` (writing the failing test), `verification-before-completion` (before claiming it's fixed).
