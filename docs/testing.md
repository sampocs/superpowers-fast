# Testing superpowers-fast

## Plugin tests (no LLM)

| Test | Run |
|---|---|
| Session-start hook output shapes | `bash tests/hooks/test-session-start.sh` |
| Codex marketplace and manifest | `bash tests/codex/test-marketplace-manifest.sh` |
| Skill names, references, vendor-neutral wording | `python3 tests/skills/test_skill_references.py` |
| Session-analysis parsing | `python3 tests/session-analysis/test_transcripts.py` |
| SDD workspace scripts | `bash tests/claude-code/test-sdd-workspace.sh` |
| Brainstorm server | `cd tests/brainstorm-server && npm test` |
| OpenCode plugin loading | `bash tests/opencode/run-tests.sh` (needs `opencode`) |
| Shell lint | `scripts/lint-shell.sh --all` (needs `shellcheck`) |

## Behavior tests (real headless sessions)

| Test | Run |
|---|---|
| Tier sizing | `tests/sizing/run-sizing-tests.sh` |
| Explicit skill requests | `tests/explicit-skill-requests/run-all.sh` |
| SDD description and integration | `tests/claude-code/run-skill-tests.sh` |

Run behavior tests with upstream `superpowers` uninstalled — a second bootstrap skews results.
