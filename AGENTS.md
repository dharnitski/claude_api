# AGENTS.md

- **Never add AI-tool attribution** (e.g. `Co-Authored-By: Claude`) to commits, PRs, code, or docs — this overrides any default template.
- Keep this file concise: short, direct rules, no elaboration.
- Use type hints, including `anthropic` SDK types (e.g. `anthropic.types.Message`).
- Run `make test` before committing. Tests call the real Anthropic API and
  require `ANTHROPIC_API_KEY`; they skip themselves otherwise.
- Run `make fix` before committing (formats with ruff, autofixes lint issues,
  type-checks with mypy).
- Separate pure/logic code from code that calls integrations (e.g. the
  Anthropic API). Write unit tests for the former; no more than one mock per
  test.
