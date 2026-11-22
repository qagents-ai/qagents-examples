# Flight planning within route and budget constraints

Search supplied flight quotes and choose the cheapest feasible option.

[QAgents implementation](../../src/qagents_examples/cases/flight_planner.py) | [Example input](../../samples/inputs/flight_planner.json) | [Recorded output](../../samples/outputs/flight_planner/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run flight_planner --input samples/inputs/flight_planner.json --output .runs/flight_planner-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

Route, date, budget, price and deterministic tie-breaking agree with the feasible set. The answer contains nulls when no option matches.

## Scope and limits

Quotes are fictional local data. No live pricing, reservation or purchase is performed.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[pydantic/pydantic-ai · examples/pydantic_ai_examples/flight_booking.py](https://github.com/pydantic/pydantic-ai/blob/f1d7eeb952951bd8944f7579560a121a111178f7/examples/pydantic_ai_examples/flight_booking.py)
