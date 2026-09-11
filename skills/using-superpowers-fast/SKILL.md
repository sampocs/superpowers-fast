---
name: using-superpowers-fast
description: Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response, and sizes work before building
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT. This is not negotiable.
</EXTREMELY-IMPORTANT>

## The Rule

**Invoke relevant or requested skills BEFORE any response or action** — including clarifying questions, exploring the codebase, or checking files. If it turns out wrong for the situation, you don't have to use it.

Then announce "Using [skill] to [purpose]" and follow the skill exactly.

## Size the work

Before building or changing anything, size the task, announce it in one line naming the other two tiers, and proceed without waiting:

`Sizing as Medium: <reason>. Say "simple" or "large" to override.`

| Tier | Test | Examples | Route |
|---|---|---|---|
| **Simple** | Nothing to decide; you'd do it without asking. | fix a misaligned button · patch a missing null check · add a field to an existing form | `quick-change` |
| **Medium** | A few answers shape the build; fits in 1–3 chunks. | admin page with summary metrics · new endpoint + its UI · retry/backoff for a flaky integration | `brainstorming` → `lean-build` |
| **Large** | New subsystem or cross-cutting change; needs a sequenced plan. | a backtesting engine · new order type across engine, API, UI · swapping auth providers | `brainstorming` → `writing-plans` → `subagent-driven-development` |

- **Bugs with an unknown cause:** `systematic-debugging` first; size the fix once the root cause is known.
- **Risk** (money, auth, state machines) doesn't raise the tier; it strengthens review within it.
- **Tiers can change** mid-task. Re-announce when they do.
- **Before entering plan mode:** size first; Medium or Large → `brainstorming` first.
- Process skills (`brainstorming`, `systematic-debugging`) come before implementation skills (e.g. frontend-design).

## Models

Skills name model tiers: cheap, standard, most capable. The session model is the most capable tier. Map standard and cheap with the user's instructions (keyed by the session model's family); with no mapping, use the session model for every tier. Always set a model explicitly when dispatching a subagent.

## Red Flags

These thoughts mean STOP — you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "The skill is overkill" | Simple tasks have `quick-change`. Use it. |
| "I remember this skill" | Skills evolve. Read the current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |

## Platform Adaptation

Codex: read `references/codex-tools.md`.

## User Instructions

User instructions (CLAUDE.md, AGENTS.md, direct requests) take precedence over skills, which override default behavior. Skip a skill workflow only when your human partner explicitly says to.
