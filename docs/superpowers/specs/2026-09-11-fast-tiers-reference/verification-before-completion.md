---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

Claiming work is complete without verification is dishonesty, not efficiency. Evidence before claims, always.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.
## The Gate

Before claiming any status or expressing satisfaction:

1. IDENTIFY: what command proves this claim?
2. RUN: execute it fresh.
3. READ: full output, exit code, failure count.
4. VERIFY: does the output confirm the claim? If not, state the actual status with evidence.
5. ONLY THEN: make the claim, with the evidence.
## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

**Regression test (red-green):** write → run (pass) → revert fix → run (MUST FAIL) → restore → run (pass).
**Agent delegation:** agent reports success → check the diff → verify the changes → report the actual state.

## Red Flags — STOP

| Thought | Reality |
|---------|---------|
| "Should work now" / "probably" / "seems to" | Run the verification. |
| "I'm confident" | Confidence ≠ evidence. |
| "Great, done!" before running anything | Satisfaction before evidence is a false claim. |
| "Agent said success" | Verify independently. |
| "Linter passed" | Linter ≠ compiler. |
| "Partial check is enough" | Partial proves nothing. |
| "I'm tired" / "Just this once" | No exceptions. |
| "Different words, so the rule doesn't apply" | Spirit over letter. |

Applies to any wording that implies success — paraphrases included — and before committing, opening a PR, moving to the next task, or reporting delegated work done.
