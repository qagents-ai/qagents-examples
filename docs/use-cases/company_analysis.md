# Company analysis with durable workflow steps

Journal metrics, risk evidence and writing as workflow steps, then reopen the worker store and replay them.

[QAgents implementation](../../src/qagents_examples/cases/company_analysis.py) | [Example input](../../samples/inputs/company_analysis.json) | [Recorded output](../../samples/outputs/company_analysis/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run company_analysis --input samples/inputs/company_analysis.json --output .runs/company_analysis-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

Company identity, integer basis-point arithmetic and risk quotes match inputs. Completed steps replay against models that raise if called.

## Scope and limits

Fictional statements replace financial data APIs. It demonstrates durable orchestration and evidence checks, not investment recommendations or mid-request crash recovery.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[openai/openai-agents-python · examples/financial_research_agent/manager.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/financial_research_agent/manager.py), [crewAIInc/crewAI-examples · crews/stock_analysis/src/stock_analysis/crew.py](https://github.com/crewAIInc/crewAI-examples/blob/da94a91e691e1cf5b3151416bb15b5b62729bea8/crews/stock_analysis/src/stock_analysis/crew.py)
