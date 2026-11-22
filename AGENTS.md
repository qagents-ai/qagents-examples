# Working on QAgents examples

- Keep this repository separate from qagents and qagent-gym. Do not vendor their code.
- Use the installed QAgents docs API before writing a QAgents call:
  `python -m qagents.docs_mcp api Agent.run`. Run its code checker on new Python files.
- Every example must run the real QAgents Agent loop with finite Limits. Offline
  models are explicit test fixtures; provider model quality is a separate evaluation.
- Each use case owns its tools, input/output schemas and independent verifier.
  Do not replace different agents with a single prompt template.
- External writes require explicit approval. Demonstrations write only local artifacts.
  Provider credentials come from environment variables and never enter reports.
- Keep source attribution in research/sources.json and docs/source-map.md. Link to
  inspected immutable commits. Implement original QAgents code rather than copying
  upstream modules, assets or brand marks.
- Test real behavior, malformed input, verification failures, declined approvals,
  persistence and resource limits. Do not call paid services in default tests.

Checks: `pytest -q`, `ruff check src tests scripts`, `ruff format --check src tests scripts`,
`python scripts/check_qagents_api.py`, `qagents-examples run-all --output .runs/fresh-name`.
