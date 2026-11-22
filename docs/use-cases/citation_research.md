# Research brief with exact source quotes

Read sources, produce a typed brief and attach exact quotations.

[QAgents implementation](../../src/qagents_examples/cases/citation_research.py) | [Example input](../../samples/inputs/citation_research.json) | [Recorded output](../../samples/outputs/citation_research/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run citation_research --input samples/inputs/citation_research.json --output .runs/citation_research-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

Citation IDs exist and each quote appears in its referenced document.

## Scope and limits

Local corpus replaces web search. Quotes are checked. open-ended research quality is not scored.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[openai/openai-agents-python · examples/research_bot/manager.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/research_bot/manager.py)
