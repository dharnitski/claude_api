# AGENTS.md

Guidance for AI coding agents working in this repository.

- Keep artifacts (commits, PRs, code, docs) vendor-agnostic: no AI-tool
  attribution (e.g. `Co-Authored-By: Claude ...`, "Generated with ..." footers).
- Use type hints in Python code, including the `anthropic` SDK's own types
  (e.g. `anthropic.types.Message`) for request/response objects.
