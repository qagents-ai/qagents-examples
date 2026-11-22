# Verification

The collection uses the real QAgents runtime with explicit offline model replies.
Each application validates its own result against application evidence. Checks
cover supported behavior rather than general model intelligence.

## Reproduce

```console
uv sync --locked --extra dev
uv run --locked pytest -q -W error
uv run --locked ruff check src tests scripts
uv run --locked ruff format --check src tests scripts
uv run --locked python scripts/check_qagents_api.py
uv run --locked python scripts/build_docs.py --check
uv run --locked qagents-examples run-all --output .runs/verified-collection
uv audit --locked
```

Use a fresh output path for each CLI run. The checked results are recorded in
[verification.json](../research/verification.json), and the actual sample
reports are in [samples/outputs](../samples/outputs).

## What the suite checks

- Every application runs its native QAgents loop and produces verified artifacts.
- Declined approvals create no support, procurement or reimbursement action.
- Idempotency keys are bound to both destination kind and payload.
- A model cannot access or queue another customer's order.
- SQLite query authorization rejects writes, schema tables, extension loading,
  attachment and multiple statements. Work and returned rows are bounded.
- Well-shaped but incorrect outputs fail for invoices, citations, document
  evidence, meeting commitments, flight constraints, recruitment evidence,
  localization, code findings, proposals and company metrics.
- Tenant/user preference memory survives closing and reopening the store while
  another user and another tenant receive no preferences.
- Actual persistent messages cross a new Python process and are consumed once.
- Completed company-analysis workflow steps replay against models that would
  raise if inference were attempted.
- The native OpenAI-compatible adapter executes a streaming tool-call cycle with
  local HTTPX responses. The configured factory retains explicit prices and the
  expected completion-token field.
- Invalid prices, malformed/ambiguous input JSON, reused output paths and model
  turn exhaustion are rejected. UTF-8 output works for English and Greek.
- SQLite connections and model resources are explicitly closed; warnings are
  treated as errors.

## What these checks do not establish

Live model quality, factual research beyond supplied sources, general semantic
translation quality, official grant-call compliance, legal/tax decisions and
production service integrations require separate evaluation. The per-use-case
guides describe narrower verifier scopes, such as literal CV skill mentions or
the three AST code-review rules.

The package does not contact a live model provider in the default suite.
Local protocol responses are controlled fixtures. The GitHub workflow is manual
and checks out the public runtime at the pinned revision. Hosted CI is
not represented as green unless an actual successful run is recorded.
