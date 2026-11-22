"""Discoverable applications; IDs are also their runnable module names."""

from importlib import import_module

CATALOG = {
    "citation_research": "Research brief with exact source quotes",
    "support_case": "Approved, customer-bound local support case",
    "invoice_audit": "Invoice line arithmetic and discrepancy detection",
    "sql_analyst": "Bounded read-only SQLite revenue analysis",
    "lead_qualification": "Explicit inbound-lead scoring rubric",
    "meeting_actions": "Commitments with transcript evidence and owners",
    "flight_planner": "Cheapest feasible flight under route/date/budget constraints",
    "recruitment_review": "CV skill-mention evidence for human review",
    "expense_review": "Receipt/policy checks and approved reimbursement queue",
    "inventory_order": "Stock replenishment and approved local purchase request",
    "code_security_review": "Non-executing Python review under three AST rules",
    "greek_localization": "English/Greek specialist delegation with placeholder checks",
    "document_qa": "Local document retrieval with evidence-only answers and abstention",
    "content_team": "Nested editor/writer/researcher team",
    "grant_proposal": "KA220 proposal draft with a separate budget reviewer",
    "incident_team": "Coordinator/triager/reviewer with persistent internal messages",
    "scoped_preferences": "Approved tenant/user memory across SQLite reopen",
    "company_analysis": "Durable analysis with worker reopen and inference-free replay",
}


def load(name: str):
    if name not in CATALOG:
        raise ValueError(f"unknown example: {name}")
    return import_module(f"qagents_examples.cases.{name}")
