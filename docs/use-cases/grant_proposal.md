# KA220 proposal draft with a separate budget reviewer

A coordinator asks a programme writer and an independent budget specialist for an illustrative KA220 draft.

[QAgents implementation](../../src/qagents_examples/cases/grant_proposal.py) | [Example input](../../samples/inputs/grant_proposal.json) | [Recorded output](../../samples/outputs/grant_proposal/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run grant_proposal --input samples/inputs/grant_proposal.json --output .runs/grant_proposal-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

Required sections, project/work-package identities, leads and the budget sum are checked. The draft retains explicit evidence gaps.

## Scope and limits

New proposal-writing adaptation of specialist research/writing. It is a fictional draft. Prose quality, current call compliance, eligibility and partner commitments require human review.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[openai/openai-agents-python · examples/agent_patterns/agents_as_tools_structured.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/agent_patterns/agents_as_tools_structured.py), [crewAIInc/crewAI-examples · crews/prep-for-a-meeting/tasks.py](https://github.com/crewAIInc/crewAI-examples/blob/da94a91e691e1cf5b3151416bb15b5b62729bea8/crews/prep-for-a-meeting/tasks.py)
