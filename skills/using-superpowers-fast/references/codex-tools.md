## Subagent dispatch requires multi-agent support

Add to your Codex config (`~/.codex/config.toml`):

```toml
[features]
multi_agent = true
```

This enables `spawn_agent`, `wait_agent`, and `close_agent` for `lean-build` and `subagent-driven-development`. Close implementer and reviewer subagents when they finish.

## Bootstrap

Codex discovers skills natively and has no session-start hook. If no tier has been announced, size the task per `using-superpowers-fast` before building.

## Environment Detection

Before creating worktrees or finishing a branch, detect the environment with read-only git commands:

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

- `GIT_DIR != GIT_COMMON` → already in a linked worktree (skip creation)
- `BRANCH` empty → detached HEAD (cannot branch/push/PR from sandbox)

## Codex App Finishing

When the sandbox blocks branch/push operations (detached HEAD in an externally managed worktree), commit all work and tell the user to use the App's controls:

- **"Create branch"** — names the branch, then commit/push/PR via the App UI
- **"Hand off to local"** — transfers work to the user's local checkout

You can still run tests, stage files, and suggest branch names, commit messages, and PR descriptions.
