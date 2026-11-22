# Invoice line arithmetic and discrepancy detection

Extract invoice values into a typed audit and recompute every line in integer cents.

[QAgents implementation](../../src/qagents_examples/cases/invoice_audit.py) | [Example input](../../samples/inputs/invoice_audit.json) | [Recorded output](../../samples/outputs/invoice_audit/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run invoice_audit --input samples/inputs/invoice_audit.json --output .runs/invoice_audit-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

Invoice ID, subtotal, expected total and discrepancy labels match independent arithmetic.

## Scope and limits

This is a new invoice use case of typed extraction, not a copy of an upstream invoice application. Tax amount is supplied. Tax law is not evaluated.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[pydantic/pydantic-ai · examples/pydantic_ai_examples/pydantic_model.py](https://github.com/pydantic/pydantic-ai/blob/f1d7eeb952951bd8944f7579560a121a111178f7/examples/pydantic_ai_examples/pydantic_model.py)
