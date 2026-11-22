# Answers from local documents

Retrieve local paragraphs and return verbatim evidence, or abstain when none matches.

[QAgents implementation](../../src/qagents_examples/cases/document_qa.py) | [Example input](../../samples/inputs/document_qa.json) | [Recorded output](../../samples/outputs/document_qa/report.json)

![Task input, tool execution and independent application verification](../../assets/diagrams/application-flow.svg)

## Run

From the checkout after the [setup](../../README.md#start-in-a-fresh-workspace):

```console
uv run --locked qagents-examples run document_qa --input samples/inputs/document_qa.json --output .runs/document_qa-demo
```

Choose a fresh output path for every run. Offline mode supplies recorded model replies. QAgents still executes the tools, session journals and application checks. The [provider guide](../providers.md) shows how to use the same implementation with a configured model.

## What is checked

Answer is an exact paragraph from the bounded retrieved set, with its source ID. Missing evidence requires nulls.

## Scope and limits

Literal phrase retrieval replaces embeddings/pgvector. It demonstrates evidence boundaries and abstention, not a general semantic search service.

Every agent has finite turns, tokens, tool calls and deadlines. A failed verifier or incomplete run returns a nonzero CLI exit. Local action tools pause for approval. Use `--approval decline` to inspect the refusal path.

## Inspected source

[pydantic/pydantic-ai · examples/pydantic_ai_examples/rag.py](https://github.com/pydantic/pydantic-ai/blob/f1d7eeb952951bd8944f7579560a121a111178f7/examples/pydantic_ai_examples/rag.py)
