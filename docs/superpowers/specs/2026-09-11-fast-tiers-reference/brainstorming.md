---
name: brainstorming
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Sizes the task, then explores user intent, requirements and design before implementation."
---
# Brainstorming Ideas Into Designs

Turn ideas into fully formed designs and specs through collaborative dialogue: understand the project context, ask questions one at a time, then present the design and get approval.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it.
</HARD-GATE>
**Tier first.** If no tier has been announced, size the task per using-superpowers-fast. Simple → use quick-change instead; brainstorming is for Medium and Large.
## Checklist

Complete in order:

1. **Explore project context** — files, docs, recent commits.
2. **Offer the visual companion just-in-time** — only when a question would genuinely be clearer shown than described (see Visual Companion). Never upfront.
3. **Ask clarifying questions** — one per message; understand purpose, constraints, success criteria.
4. **Propose 2-3 approaches** — with trade-offs and your recommendation.
5. **Present design** — in sections scaled to their complexity; get approval after each.
6. **Write design doc** — `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`; commit. Medium: include the Build plan.
7. **Spec self-review** — fix inline (see below).
8. **User reviews written spec** — wait for approval.
9. **Hand off** — Medium → lean-build. Large → writing-plans. Never frontend-design or any other implementation skill.
## Understanding the idea

- Assess scope before detailed questions. If the request describes multiple independent subsystems (e.g. "a platform with chat, file storage, billing, and analytics"), flag it immediately and help decompose: the independent pieces, how they relate, what order to build them. Brainstorm the first sub-project; each gets its own spec → plan → build cycle.
- One question per message; multiple choice when possible.
- Skip any question with only one reasonable answer.
## Exploring approaches

Propose 2-3 approaches with trade-offs. Lead with your recommendation and why.

## Presenting the design

- Scale each section: a few sentences if straightforward, up to 200-300 words if nuanced. Ask whether it looks right after each.
- Cover architecture, components, data flow, error handling, testing.
- Be ready to go back and clarify.

**Design for isolation and clarity:**
- Units with one clear purpose, well-defined interfaces, testable independently. For each: what does it do, how do you use it, what does it depend on?
- If a consumer must read a unit's internals to use it, the boundary needs work.
- Smaller, focused files are easier to reason about and edit reliably; a growing file is a signal it's doing too much.

**In existing codebases:**
- Explore the structure first; follow existing patterns.
- Include targeted improvements where existing problems affect the work (an oversized file, tangled responsibilities). No unrelated refactoring.
- YAGNI ruthlessly.

## After the design

**Spec:** save to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` (user preferences override), commit.
**Build plan (Medium only)** — append to the spec, ~30-80 lines, no code:
- 1-3 chunks. Each: files, interfaces produced/consumed, key decisions, tests to add.
- `Depends on:` per chunk (other chunks, or none). Independent chunks build in parallel.
**Self-review** — with fresh eyes; fix inline, no re-review:
1. Placeholders: "TBD", "TODO", incomplete sections, vague requirements.
2. Consistency: sections that contradict each other; architecture vs. features.
3. Scope: focused enough for one plan, or needs decomposition?
4. Ambiguity: any requirement readable two ways? Pick one; make it explicit.

**User review gate:**
> "Spec written and committed to `<path>`. Please review it and let me know if you want any changes before we start building."

If they request changes, make them and re-run the self-review. Proceed only on approval.

## Visual Companion

A browser companion for mockups, diagrams, and visual options. A tool, not a mode: accepting it doesn't route every question through the browser.

**Offer just-in-time** — the first time a question is genuinely clearer shown than told: a real mockup / layout / diagram question, not merely a UI *topic*. The offer MUST be its own message, nothing else in it:
> "This next part might be easier if I show you — I can put together mockups, diagrams, and comparisons in a browser tab as we go. It's still new and can be token-intensive. Want me to? I'll open it for you."

If accepted, read `skills/brainstorming/visual-companion.md` and start the server with `--open`. If declined, continue text-only and don't offer again unless they raise it.

**Per question:** would the user understand this better by seeing it than reading it? Mockups, wireframes, layout comparisons, architecture diagrams → browser. Requirements, conceptual choices, tradeoff lists, scope decisions → terminal. "What does personality mean here?" is conceptual; "Which wizard layout works better?" is visual.
