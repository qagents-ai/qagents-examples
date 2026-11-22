# Expense review with an approved local queue

Read a fictional receipt/category-limit policy and request approval to queue eligible reimbursements.

[QAgents implementation](../../src/qagents_examples/cases/expense_review.py) | [Example input](../../samples/inputs/expense_review.json) | [Recorded output](../../samples/outputs/expense_review/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run expense_review --input samples/inputs/expense_review.json --output .runs/expense_review-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

Eligible IDs and integer-cent totals match the policy, and approval/destination state agrees with the answer.

## Scope and limits

New business adaptation of approval and dependency-bound tools. No money is transferred and no legal or tax eligibility is inferred.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[openai/openai-agents-python · examples/agent_patterns/human_in_the_loop.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/agent_patterns/human_in_the_loop.py), [pydantic/pydantic-ai · examples/pydantic_ai_examples/bank_support.py](https://github.com/pydantic/pydantic-ai/blob/f1d7eeb952951bd8944f7579560a121a111178f7/examples/pydantic_ai_examples/bank_support.py)
