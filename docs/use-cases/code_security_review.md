# Static Python code review

Read source strings without executing them and produce typed file/line findings.

[QAgents implementation](../../src/qagents_examples/cases/code_security_review.py) | [Example input](../../samples/inputs/code_security_review.json) | [Recorded output](../../samples/outputs/code_security_review/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run code_security_review --input samples/inputs/code_security_review.json --output .runs/code_security_review-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

Findings match the explicit AST rules for direct eval, exec and literal subprocess.run(shell=True).

## Scope and limits

Extends a repository-investigation pattern to a narrow static-review task. It is not a complete security audit and does not run code or modify a checkout.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[microsoft/autogen · python/samples/gitty/src/gitty/_gitty.py](https://github.com/microsoft/autogen/blob/8390985108cb1e3881f5f7297765758d8ad2540c/python/samples/gitty/src/gitty/_gitty.py)
