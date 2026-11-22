# Explicit inbound-lead scoring rubric

Read fictional inbound leads and apply the published sector/size/demo rubric.

[QAgents implementation](../../src/qagents_examples/cases/lead_qualification.py) | [Example input](../../samples/inputs/lead_qualification.json) | [Recorded output](../../samples/outputs/lead_qualification/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run lead_qualification --input samples/inputs/lead_qualification.json --output .runs/lead_qualification-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

Every lead has the exact calculated score and the qualified ID set meets the selected threshold.

## Scope and limits

Produces a human-review artifact. It does not scrape people, enrich profiles or send outreach.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[crewAIInc/crewAI-examples · flows/lead-score-flow/src/lead_score_flow/main.py](https://github.com/crewAIInc/crewAI-examples/blob/da94a91e691e1cf5b3151416bb15b5b62729bea8/flows/lead-score-flow/src/lead_score_flow/main.py)
