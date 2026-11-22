# Incident review with persistent team messages

A coordinator, triager and reviewer exchange evidence through three separately opened persistent inboxes.

[QAgents implementation](../../src/qagents_examples/cases/incident_team.py) | [Example input](../../samples/inputs/incident_team.json) | [Recorded output](../../samples/outputs/incident_team/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run incident_team --input samples/inputs/incident_team.json --output .runs/incident_team-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

Telemetry conclusion and all three actual sender/recipient/payload routes are verified from executed tool results.

## Scope and limits

Local telemetry/mailboxes replace Slack and production diagnostics. The test suite also receives a durable message in another Python process. No service restart is available.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[agno-agi/agno · cookbook/05_agent_os/17_slack/hitl_incident_commander.py](https://github.com/agno-agi/agno/blob/365c9c7e74719c1d20b557178add8c65f27a4426/cookbook/05_agent_os/17_slack/hitl_incident_commander.py), [microsoft/autogen · python/samples/core_distributed-group-chat/_agents.py](https://github.com/microsoft/autogen/blob/8390985108cb1e3881f5f7297765758d8ad2540c/python/samples/core_distributed-group-chat/_agents.py)
