# superpowers-fast — Contributor Guide

A personal fork of [obra/superpowers](https://github.com/obra/superpowers), restructured around task tiers. Don't open PRs against upstream from this repo.

## Writing skill text

- **Concise.** Verbose skill text leaks into agent output. Cut duplication (diagrams restating a checklist, rationale sections, closing restatements) and anything the tiers overrule; keep every specific instruction, tightened. Tables over prose.
- **Model tiers, not vendors.** Say cheap / standard / most capable — never a vendor model name. Users map tiers in their own `AGENTS.md`.
- **Keep the teeth.** Red-flag tables and hard gates shape behavior; tighten their wording, don't remove them.
- "Your human partner" is deliberate phrasing — keep it.

## Structure

- Sizing and routing: `skills/using-superpowers-fast/SKILL.md`
- Shared build loop: `skills/using-superpowers-fast/references/build-loop.md`
- Paths written into user repos keep the old name: `docs/superpowers/`, `.superpowers/`.
- Harnesses: Claude Code, Cursor, Codex, OpenCode. Codex has no session-start hook, so entry skills must work without the bootstrap.

## Testing

See `docs/testing.md`. Minimum before committing skill changes: `python3 tests/skills/test_skill_references.py` and `bash tests/hooks/test-session-start.sh`.
