# English and Greek localization

A coordinator delegates translation to a specialist and checks its structured result.

[QAgents implementation](../../src/qagents_examples/cases/greek_localization.py) | [Example input](../../samples/inputs/greek_localization.json) | [Recorded output](../../samples/outputs/greek_localization/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run greek_localization --input samples/inputs/greek_localization.json --output .runs/greek_localization-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

Target language, exact placeholder multiplicities and required glossary terms are preserved.

## Scope and limits

Offline mode replays the supplied English/Greek pair in either direction. Use a provider for other text. Semantic translation quality still needs review.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[openai/openai-agents-python · examples/agent_patterns/agents_as_tools.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/agent_patterns/agents_as_tools.py), [openai/openai-agents-python · examples/agent_patterns/agents_as_tools_structured.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/agent_patterns/agents_as_tools_structured.py)
