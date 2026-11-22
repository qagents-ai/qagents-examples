# Source map

These original QAgents applications draw on the upstream patterns linked below. The upstream frameworks were inspected without executing them. Source links are pinned to the inspected commits. Repository license metadata is retained in the [catalog](../research/sources.json). No upstream source modules or assets are bundled.

## Research brief with exact source quotes

[Implementation](../src/qagents_examples/cases/citation_research.py)

[openai/openai-agents-python · examples/research_bot/manager.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/research_bot/manager.py)

Read sources, produce a typed brief and attach exact quotations.

Local corpus replaces web search. Quotes are checked. open-ended research quality is not scored.

## Customer support with an approved case queue

[Implementation](../src/qagents_examples/cases/support_case.py)

[openai/openai-agents-python · examples/customer_service/main.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/customer_service/main.py), [pydantic/pydantic-ai · examples/pydantic_ai_examples/bank_support.py](https://github.com/pydantic/pydantic-ai/blob/f1d7eeb952951bd8944f7579560a121a111178f7/examples/pydantic_ai_examples/bank_support.py)

Triage hands the conversation to a specialist, who inspects an authorized order and requests approval to queue a support case.

A local idempotent SQLite queue replaces CRM integration. No refund or customer message is sent.

## Invoice line arithmetic and discrepancy detection

[Implementation](../src/qagents_examples/cases/invoice_audit.py)

[pydantic/pydantic-ai · examples/pydantic_ai_examples/pydantic_model.py](https://github.com/pydantic/pydantic-ai/blob/f1d7eeb952951bd8944f7579560a121a111178f7/examples/pydantic_ai_examples/pydantic_model.py)

Extract invoice values into a typed audit and recompute every line in integer cents.

This is a new invoice use case of typed extraction, not a copy of an upstream invoice application. Tax amount is supplied. Tax law is not evaluated.

## Bounded read-only SQLite revenue analysis

[Implementation](../src/qagents_examples/cases/sql_analyst.py)

[huggingface/smolagents · examples/text_to_sql.py](https://github.com/huggingface/smolagents/blob/2689e450364d451a0afa0a5e883d12a031c125dd/examples/text_to_sql.py)

Create a local sales database, let the agent query it and verify regional totals in Python.

SQLite replaces an external database. Queries are limited to the supplied sales schema.

## Explicit inbound-lead scoring rubric

[Implementation](../src/qagents_examples/cases/lead_qualification.py)

[crewAIInc/crewAI-examples · flows/lead-score-flow/src/lead_score_flow/main.py](https://github.com/crewAIInc/crewAI-examples/blob/da94a91e691e1cf5b3151416bb15b5b62729bea8/flows/lead-score-flow/src/lead_score_flow/main.py)

Read fictional inbound leads and apply the published sector/size/demo rubric.

Produces a human-review artifact. It does not scrape people, enrich profiles or send outreach.

## Commitments with transcript evidence and owners

[Implementation](../src/qagents_examples/cases/meeting_actions.py)

[crewAIInc/crewAI-examples · flows/meeting_assistant_flow/src/meeting_assistant_flow/main.py](https://github.com/crewAIInc/crewAI-examples/blob/da94a91e691e1cf5b3151416bb15b5b62729bea8/flows/meeting_assistant_flow/src/meeting_assistant_flow/main.py)

Extract explicit commitments with owners, due dates and full transcript quotes.

The verifier recognizes 'Name: I will TASK by YYYY-MM-DD.' statements. General meeting understanding needs a broader evaluator. No Trello or Slack writes occur.

## Flight planning within route and budget constraints

[Implementation](../src/qagents_examples/cases/flight_planner.py)

[pydantic/pydantic-ai · examples/pydantic_ai_examples/flight_booking.py](https://github.com/pydantic/pydantic-ai/blob/f1d7eeb952951bd8944f7579560a121a111178f7/examples/pydantic_ai_examples/flight_booking.py)

Search supplied flight quotes and choose the cheapest feasible option.

Quotes are fictional local data. No live pricing, reservation or purchase is performed.

## CV skill-mention evidence for human review

[Implementation](../src/qagents_examples/cases/recruitment_review.py)

[crewAIInc/crewAI-examples · crews/recruitment/src/recruitment/crew.py](https://github.com/crewAIInc/crewAI-examples/blob/da94a91e691e1cf5b3151416bb15b5b62729bea8/crews/recruitment/src/recruitment/crew.py)

Collect literal skill mentions from supplied anonymous CVs into an evidence worksheet.

The sample preserves matching/reporting, using local CVs. A mention is not proficiency. This does not rank candidates or make hiring decisions.

## Expense review with an approved local queue

[Implementation](../src/qagents_examples/cases/expense_review.py)

[openai/openai-agents-python · examples/agent_patterns/human_in_the_loop.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/agent_patterns/human_in_the_loop.py), [pydantic/pydantic-ai · examples/pydantic_ai_examples/bank_support.py](https://github.com/pydantic/pydantic-ai/blob/f1d7eeb952951bd8944f7579560a121a111178f7/examples/pydantic_ai_examples/bank_support.py)

Read a fictional receipt/category-limit policy and request approval to queue eligible reimbursements.

New business adaptation of approval and dependency-bound tools. No money is transferred and no legal or tax eligibility is inferred.

## Stock replenishment and approved local purchase request

[Implementation](../src/qagents_examples/cases/inventory_order.py)

[openai/openai-agents-python · examples/agent_patterns/human_in_the_loop.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/agent_patterns/human_in_the_loop.py)

Read stock levels, calculate the exact deficit and request approval for a purchase request.

A new procurement adaptation of human approval. No supplier is contacted. Sufficient stock creates no request.

## Static Python code review

[Implementation](../src/qagents_examples/cases/code_security_review.py)

[microsoft/autogen · python/samples/gitty/src/gitty/_gitty.py](https://github.com/microsoft/autogen/blob/8390985108cb1e3881f5f7297765758d8ad2540c/python/samples/gitty/src/gitty/_gitty.py)

Read source strings without executing them and produce typed file/line findings.

Extends a repository-investigation pattern to a narrow static-review task. It is not a complete security audit and does not run code or modify a checkout.

## English and Greek localization

[Implementation](../src/qagents_examples/cases/greek_localization.py)

[openai/openai-agents-python · examples/agent_patterns/agents_as_tools.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/agent_patterns/agents_as_tools.py), [openai/openai-agents-python · examples/agent_patterns/agents_as_tools_structured.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/agent_patterns/agents_as_tools_structured.py)

A coordinator delegates translation to a specialist and checks its structured result.

Offline mode replays the supplied English/Greek pair in either direction. Use a provider for other text. Semantic translation quality still needs review.

## Answers from local documents

[Implementation](../src/qagents_examples/cases/document_qa.py)

[pydantic/pydantic-ai · examples/pydantic_ai_examples/rag.py](https://github.com/pydantic/pydantic-ai/blob/f1d7eeb952951bd8944f7579560a121a111178f7/examples/pydantic_ai_examples/rag.py)

Retrieve local paragraphs and return verbatim evidence, or abstain when none matches.

Literal phrase retrieval replaces embeddings/pgvector. It demonstrates evidence boundaries and abstention, not a general semantic search service.

## An editorial team with specialist agents

[Implementation](../src/qagents_examples/cases/content_team.py)

[microsoft/autogen · python/samples/core_distributed-group-chat/_agents.py](https://github.com/microsoft/autogen/blob/8390985108cb1e3881f5f7297765758d8ad2540c/python/samples/core_distributed-group-chat/_agents.py), [openai/openai-agents-python · examples/research_bot/manager.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/research_bot/manager.py)

An editor calls a writer, who calls a researcher with the source-reading tool.

QAgents child tools replace distributed group chat. This fixture creates an evidence digest rather than evaluating creative writing quality.

## KA220 proposal draft with a separate budget reviewer

[Implementation](../src/qagents_examples/cases/grant_proposal.py)

[openai/openai-agents-python · examples/agent_patterns/agents_as_tools_structured.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/agent_patterns/agents_as_tools_structured.py), [crewAIInc/crewAI-examples · crews/prep-for-a-meeting/tasks.py](https://github.com/crewAIInc/crewAI-examples/blob/da94a91e691e1cf5b3151416bb15b5b62729bea8/crews/prep-for-a-meeting/tasks.py)

A coordinator asks a programme writer and an independent budget specialist for an illustrative KA220 draft.

New proposal-writing adaptation of specialist research/writing. It is a fictional draft. Prose quality, current call compliance, eligibility and partner commitments require human review.

## Incident review with persistent team messages

[Implementation](../src/qagents_examples/cases/incident_team.py)

[agno-agi/agno · cookbook/05_agent_os/17_slack/hitl_incident_commander.py](https://github.com/agno-agi/agno/blob/365c9c7e74719c1d20b557178add8c65f27a4426/cookbook/05_agent_os/17_slack/hitl_incident_commander.py), [microsoft/autogen · python/samples/core_distributed-group-chat/_agents.py](https://github.com/microsoft/autogen/blob/8390985108cb1e3881f5f7297765758d8ad2540c/python/samples/core_distributed-group-chat/_agents.py)

A coordinator, triager and reviewer exchange evidence through three separately opened persistent inboxes.

Local telemetry/mailboxes replace Slack and production diagnostics. The test suite also receives a durable message in another Python process. No service restart is available.

## Scoped preferences that survive a restart

[Implementation](../src/qagents_examples/cases/scoped_preferences.py)

[openai/openai-agents-python · examples/memory/sqlite_session_example.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/memory/sqlite_session_example.py), [agno-agi/agno · cookbook/00_quickstart/agent_with_memory.py](https://github.com/agno-agi/agno/blob/365c9c7e74719c1d20b557178add8c65f27a4426/cookbook/00_quickstart/agent_with_memory.py)

Approve a profile update, close SQLite, reopen it and recall the current user's preferences.

QAgents session state replaces an upstream memory manager. This example has no vector search or external Mem0 service.

## Company analysis with durable workflow steps

[Implementation](../src/qagents_examples/cases/company_analysis.py)

[openai/openai-agents-python · examples/financial_research_agent/manager.py](https://github.com/openai/openai-agents-python/blob/91fb508a8931016efa793b033147d08cd20308cf/examples/financial_research_agent/manager.py), [crewAIInc/crewAI-examples · crews/stock_analysis/src/stock_analysis/crew.py](https://github.com/crewAIInc/crewAI-examples/blob/da94a91e691e1cf5b3151416bb15b5b62729bea8/crews/stock_analysis/src/stock_analysis/crew.py)

Journal metrics, risk evidence and writing as workflow steps, then reopen the worker store and replay them.

Fictional statements replace financial data APIs. It demonstrates durable orchestration and evidence checks, not investment recommendations or mid-request crash recovery.
