# Bounded read-only SQLite revenue analysis

Create a local sales database, let the agent query it and verify regional totals in Python.

[QAgents implementation](../../src/qagents_examples/cases/sql_analyst.py) | [Example input](../../samples/inputs/sql_analyst.json) | [Recorded output](../../samples/outputs/sql_analyst/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run sql_analyst --input samples/inputs/sql_analyst.json --output .runs/sql_analyst-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

Every region and total is correct. SQLite denies writes, schema access, extensions and other tables. Query work and result rows are bounded.

## Scope and limits

SQLite replaces an external database. Queries are limited to the supplied sales schema.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[huggingface/smolagents · examples/text_to_sql.py](https://github.com/huggingface/smolagents/blob/2689e450364d451a0afa0a5e883d12a031c125dd/examples/text_to_sql.py)
