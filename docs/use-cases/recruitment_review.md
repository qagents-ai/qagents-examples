# CV skill-mention evidence for human review

Collect literal skill mentions from supplied anonymous CVs into an evidence worksheet.

[QAgents implementation](../../src/qagents_examples/cases/recruitment_review.py) | [Example input](../../samples/inputs/recruitment_review.json) | [Recorded output](../../samples/outputs/recruitment_review/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run recruitment_review --input samples/inputs/recruitment_review.json --output .runs/recruitment_review-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

All candidate IDs, skill mentions, exact quotes and unmentioned skills match the supplied text.

## Scope and limits

The sample preserves matching/reporting, using local CVs. A mention is not proficiency. This does not rank candidates or make hiring decisions.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[crewAIInc/crewAI-examples · crews/recruitment/src/recruitment/crew.py](https://github.com/crewAIInc/crewAI-examples/blob/da94a91e691e1cf5b3151416bb15b5b62729bea8/crews/recruitment/src/recruitment/crew.py)
