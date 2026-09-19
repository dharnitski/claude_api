# AGENTS.md

- No AI-tool attribution in commits, PRs, code, or docs.
- Use type hints, including `anthropic` SDK types (e.g. `anthropic.types.Message`).
- Run `make test` before committing. Tests call the real Anthropic API and
  require `ANTHROPIC_API_KEY`; they skip themselves otherwise.
