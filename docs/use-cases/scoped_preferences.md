# Scoped preferences that survive a restart

Approve a profile update, close SQLite, reopen it and recall the current user's preferences.

[QAgents implementation](../../src/qagents_examples/cases/scoped_preferences.py) | [Example input](../../samples/inputs/scoped_preferences.json) | [Recorded output](../../samples/outputs/scoped_preferences/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run scoped_preferences --input samples/inputs/scoped_preferences.json --output .runs/scoped_preferences-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

The approved preferences survive reopen. Another user and another tenant see empty profiles. Identity is host-bound, outside model tool arguments.

## Scope and limits

QAgents session state replaces an upstream memory manager. This example has no vector search or external Mem0 service.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[openai/openai-agents-python · examples/memory/sqlite_session_example.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/memory/sqlite_session_example.py), [agno-agi/agno · cookbook/00_quickstart/agent_with_memory.py](https://github.com/agno-agi/agno/blob/365c9c7e74719c1d20b557178add8c65f27a4426/cookbook/00_quickstart/agent_with_memory.py)
