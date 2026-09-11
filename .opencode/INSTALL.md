# Installing superpowers-fast for OpenCode

Add it to the `plugin` array in your `opencode.json` (global or project-level):

```json
{
  "plugin": ["superpowers-fast@git+https://github.com/sampocs/superpowers-fast.git"]
}
```

Remove upstream `superpowers` from the same array — two bootstraps conflict. Restart OpenCode; the plugin registers all skills and injects the bootstrap.

Verify by asking: "What tier would an admin metrics page be?"
