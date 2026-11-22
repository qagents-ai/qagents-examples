# Commitments with transcript evidence and owners

Extract explicit commitments with owners, due dates and full transcript quotes.

[QAgents implementation](../../src/qagents_examples/cases/meeting_actions.py) | [Example input](../../samples/inputs/meeting_actions.json) | [Recorded output](../../samples/outputs/meeting_actions/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run meeting_actions --input samples/inputs/meeting_actions.json --output .runs/meeting_actions-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

The complete recognized commitment set is present, owners exist and dates are valid ISO dates.

## Scope and limits

The verifier recognizes 'Name: I will TASK by YYYY-MM-DD.' statements. General meeting understanding needs a broader evaluator. No Trello or Slack writes occur.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[crewAIInc/crewAI-examples · flows/meeting_assistant_flow/src/meeting_assistant_flow/main.py](https://github.com/crewAIInc/crewAI-examples/blob/da94a91e691e1cf5b3151416bb15b5b62729bea8/flows/meeting_assistant_flow/src/meeting_assistant_flow/main.py)
