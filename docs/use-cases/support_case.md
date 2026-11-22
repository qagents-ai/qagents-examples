# Customer support with an approved case queue

Triage hands the conversation to a specialist, who inspects an authorized order and requests approval to queue a support case.

[QAgents implementation](../../src/qagents_examples/cases/support_case.py) | [Example input](../../samples/inputs/support_case.json) | [Recorded output](../../samples/outputs/support_case/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run support_case --input samples/inputs/support_case.json --output .runs/support_case-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

The specialist answered, approval was recorded and local destination state matches the reported outcome.

## Scope and limits

A local idempotent SQLite queue replaces CRM integration. No refund or customer message is sent.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[openai/openai-agents-python · examples/customer_service/main.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/customer_service/main.py), [pydantic/pydantic-ai · examples/pydantic_ai_examples/bank_support.py](https://github.com/pydantic/pydantic-ai/blob/f1d7eeb952951bd8944f7579560a121a111178f7/examples/pydantic_ai_examples/bank_support.py)
