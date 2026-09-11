# superpowers-fast

A tiered fork of [Superpowers](https://github.com/obra/superpowers) by Jesse Vincent. Same skills library, but every task gets sized first and pays only for the process it needs.

## Why

Full Superpowers produces great work but spends 2–5 agent-hours per feature: detailed plans, a subagent and a review per task, and review loops after the PR. Session analysis showed that overhead is fixed — medium-sized changes paid it too, and reviews cost about twice what implementation did. superpowers-fast keeps the rigor where it pays and drops it where it doesn't.

## Tiers

| Tier | When | Flow |
|---|---|---|
| **Simple** | Nothing to decide — a misaligned button, a missing null check, a new form field | `quick-change`: align → do → prove → one fresh-eyes review |
| **Medium** | A few answers shape the build; fits in 1–3 chunks — an admin page with metrics, an endpoint plus its UI | `brainstorming` → spec with a Build plan → `lean-build`: 1–3 implementers, one final review |
| **Large** | A new subsystem or cross-cutting change — a backtesting engine, an order type across engine, API, and UI | `brainstorming` → `writing-plans` → `subagent-driven-development` |

The agent announces the tier in one line (`Sizing as Medium: …`) and proceeds; name another tier to override. Bugs go through `systematic-debugging` first; then the fix is sized.

Every tier shares one build loop: targeted tests while building, the full suite, a review, fixes, a scoped re-review of fixes that touched logic, and the full suite again only if fixes changed code. See `skills/using-superpowers-fast/references/build-loop.md`.

## Install

Uninstall upstream `superpowers` in each harness first — two bootstraps conflict.

**Claude Code**

```
/plugin marketplace add sampocs/superpowers-fast
/plugin install superpowers-fast@superpowers-fast
```

**Cursor** — link the repo as a local plugin:

```bash
ln -s /path/to/superpowers-fast ~/.cursor/plugins/local/superpowers-fast
```

**Codex** — add this repo as a plugin marketplace (it ships `.agents/plugins/marketplace.json`) and install `superpowers-fast`. Codex has no session-start hook; the entry skills size the task themselves.

**OpenCode** — see [.opencode/INSTALL.md](.opencode/INSTALL.md).

## Models

Skills name model tiers — cheap, standard, most capable — never vendor models. Map them to your harness's models in your own `AGENTS.md`; without a mapping, subagents use the session model.

## Skills

| Skill | Purpose |
|---|---|
| `using-superpowers-fast` | Bootstrap: skill discipline, sizing, routing |
| `quick-change` | Simple tier |
| `brainstorming` | Medium and Large design |
| `lean-build` | Medium build |
| `writing-plans`, `subagent-driven-development` | Large plan and build |
| `systematic-debugging` | Root cause first, then size the fix |
| `test-driven-development` | TDD for Large implementers |
| `requesting-code-review`, `receiving-code-review` | Review dispatch and handling |
| `verification-before-completion` | Evidence before claims |
| `writing-skills` | Editing these skills |

## Measuring

`scripts/session-analysis/report.py` reports agent-minutes and bugs that got through (CI failures after the PR, follow-up fix PRs) per tier from your Claude Code transcripts.

## License

MIT — see `LICENSE`. Based on obra/superpowers.
