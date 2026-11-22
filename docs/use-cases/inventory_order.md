# Stock replenishment and approved local purchase request

Read stock levels, calculate the exact deficit and request approval for a purchase request.

[QAgents implementation](../../src/qagents_examples/cases/inventory_order.py) | [Example input](../../samples/inputs/inventory_order.json) | [Recorded output](../../samples/outputs/inventory_order/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run inventory_order --input samples/inputs/inventory_order.json --output .runs/inventory_order-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

SKU, quantity, integer-cent cost, approval and payload-bound local destination state reconcile.

## Scope and limits

A new procurement adaptation of human approval. No supplier is contacted. Sufficient stock creates no request.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[openai/openai-agents-python · examples/agent_patterns/human_in_the_loop.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/agent_patterns/human_in_the_loop.py)
