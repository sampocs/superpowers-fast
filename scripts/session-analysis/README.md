# Session analysis

Measures how long sessions take and how many bugs get through, per tier, from Claude Code transcripts in `~/.claude/projects`.

```bash
python3 scripts/session-analysis/report.py --projects tenor-studio,diffalo --since 2026-09-11
python3 scripts/session-analysis/report.py --no-github   # skip gh calls
```

| Column | Meaning |
|---|---|
| tier | From the skills a session invoked: `simple` (quick-change), `medium` (lean-build), `large` (superpowers-fast SDD); `legacy-*` and `brainstorm-only` for pre-fork flows |
| min→PR | Agent-active minutes from the first prompt to the first PR; waits for human replies excluded |
| after | Agent-active minutes after the PR opened (review loops, fixes) |
| ext | External-review subagents (e.g. Codex passes) |
| ext#1 | Numbered findings handed to the first external-review fixer — a proxy for pass-1 findings |
| CI✗ | Failed CI runs on the PR branch after it opened |
| fixPRs | Merged `fix…` PRs within 14 days that touch the same code files |

Baseline before the fork (2026-08): medium-sized full-flow features took 100–130 agent-minutes to PR. Target for Medium: 50–65.
