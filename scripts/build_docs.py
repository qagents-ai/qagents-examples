"""Generate per-use-case guides, fixture inputs and the immutable upstream source map."""

import argparse
import json
from pathlib import Path

from qagents_examples.catalog import CATALOG, load

# source indexes refer to research/sources.json, whose inspected file order is retained.
DETAILS = {
    "citation_research": (
        [0],
        "Read sources, produce a typed brief and attach exact quotations.",
        "Citation IDs exist and each quote appears in its referenced document.",
        "Local corpus replaces web search. Quotes are checked. "
        "open-ended research quality is not scored.",
    ),
    "support_case": (
        [1, 8],
        "Triage hands the conversation to a specialist, who inspects an "
        "authorized order and requests approval to queue a support case.",
        "The specialist answered, approval was recorded and local "
        "destination state matches the reported outcome.",
        "A local idempotent SQLite queue replaces CRM "
        "integration. No refund or customer message is sent.",
    ),
    "invoice_audit": (
        [7],
        "Extract invoice values into a typed audit and recompute every line in integer cents.",
        "Invoice ID, subtotal, expected total and discrepancy labels match independent arithmetic.",
        "This is a new invoice use case of typed extraction, not a copy of an upstream "
        "invoice application. Tax amount is supplied. Tax law is not evaluated.",
    ),
    "sql_analyst": (
        [11],
        "Create a local sales database, let the agent query "
        "it and verify regional totals in Python.",
        "Every region and total is correct. SQLite denies writes, schema access, "
        "extensions and other tables. Query work and result rows are bounded.",
        "SQLite replaces an external database. Queries are limited to the supplied sales schema.",
    ),
    "lead_qualification": (
        [12],
        "Read fictional inbound leads and apply the published sector/size/demo rubric.",
        "Every lead has the exact calculated score and the "
        "qualified ID set meets the selected threshold.",
        "Produces a human-review artifact. It does not scrape "
        "people, enrich profiles or send outreach.",
    ),
    "meeting_actions": (
        [13],
        "Extract explicit commitments with owners, due dates and full transcript quotes.",
        "The complete recognized commitment set is present, "
        "owners exist and dates are valid ISO dates.",
        "The verifier recognizes 'Name: I will TASK by YYYY-MM-DD.' statements. General meeting "
        "understanding needs a broader evaluator. No Trello or Slack writes occur.",
    ),
    "flight_planner": (
        [9],
        "Search supplied flight quotes and choose the cheapest feasible option.",
        "Route, date, budget, price and deterministic tie-breaking agree "
        "with the feasible set. The answer contains nulls when no option matches.",
        "Quotes are fictional local data. No live pricing, reservation or purchase is performed.",
    ),
    "recruitment_review": (
        [14],
        "Collect literal skill mentions from supplied anonymous CVs into an evidence worksheet.",
        "All candidate IDs, skill mentions, exact quotes and "
        "unmentioned skills match the supplied text.",
        "The sample preserves matching/reporting, using local CVs. A mention is not "
        "proficiency. This does not rank candidates or make hiring decisions.",
    ),
    "expense_review": (
        [4, 8],
        "Read a fictional receipt/category-limit policy and "
        "request approval to queue eligible reimbursements.",
        "Eligible IDs and integer-cent totals match the policy, and "
        "approval/destination state agrees with the answer.",
        "New business adaptation of approval and dependency-bound tools. No money "
        "is transferred and no legal or tax eligibility is inferred.",
    ),
    "inventory_order": (
        [4],
        "Read stock levels, calculate the exact deficit and "
        "request approval for a purchase request.",
        "SKU, quantity, integer-cent cost, approval and "
        "payload-bound local destination state reconcile.",
        "A new procurement adaptation of human approval. No supplier is "
        "contacted. Sufficient stock creates no request.",
    ),
    "code_security_review": (
        [18],
        "Read source strings without executing them and produce typed file/line findings.",
        "Findings match the explicit AST rules for direct eval, "
        "exec and literal subprocess.run(shell=True).",
        "Extends a repository-investigation pattern to a narrow static-review task. It is not "
        "a complete security audit and does not run code or modify a checkout.",
    ),
    "greek_localization": (
        [2, 3],
        "A coordinator delegates translation to a specialist and checks its structured result.",
        "Target language, exact placeholder multiplicities and "
        "required glossary terms are preserved.",
        "Offline mode replays the supplied English/Greek pair in either direction. Use a "
        "provider for other text. Semantic translation quality still needs review.",
    ),
    "document_qa": (
        [10],
        "Retrieve local paragraphs and return verbatim evidence, or abstain when none matches.",
        "Answer is an exact paragraph from the bounded retrieved set, "
        "with its source ID. Missing evidence requires nulls.",
        "Literal phrase retrieval replaces embeddings/pgvector. It demonstrates evidence "
        "boundaries and abstention, not a general semantic search service.",
    ),
    "content_team": (
        [17, 0],
        "An editor calls a writer, who calls a researcher with the source-reading tool.",
        "The title and every source paragraph remain intact. The "
        "parent usage includes all specialist model calls.",
        "QAgents child tools replace distributed group chat. This fixture creates an "
        "evidence digest rather than evaluating creative writing quality.",
    ),
    "grant_proposal": (
        [3, 15],
        "A coordinator asks a programme writer and an independent "
        "budget specialist for an illustrative KA220 draft.",
        "Required sections, project/work-package identities, leads and the budget "
        "sum are checked. The draft retains explicit evidence gaps.",
        "New proposal-writing adaptation of specialist "
        "research/writing. It is a fictional draft. Prose "
        "quality, current call compliance, eligibility and "
        "partner commitments require human review.",
    ),
    "incident_team": (
        [19, 17],
        "A coordinator, triager and reviewer exchange evidence "
        "through three separately opened persistent inboxes.",
        "Telemetry conclusion and all three actual "
        "sender/recipient/payload routes are verified from executed tool results.",
        "Local telemetry/mailboxes replace Slack and production diagnostics. The test suite also "
        "receives a durable message in another Python process. No service restart is available.",
    ),
    "scoped_preferences": (
        [5, 20],
        "Approve a profile update, close SQLite, reopen it and "
        "recall the current user's preferences.",
        "The approved preferences survive reopen. Another user and another tenant see "
        "empty profiles. Identity is host-bound, outside model tool arguments.",
        "QAgents session state replaces an upstream memory manager. This "
        "example has no vector search or external Mem0 service.",
    ),
    "company_analysis": (
        [6, 16],
        "Journal metrics, risk evidence and writing as workflow "
        "steps, then reopen the worker store and replay them.",
        "Company identity, integer basis-point arithmetic and risk quotes match "
        "inputs. Completed steps replay against models that raise if called.",
        "Fictional statements replace financial data APIs. It "
        "demonstrates durable orchestration and "
        "evidence checks, not investment recommendations or mid-request crash recovery.",
    ),
}

GUIDE_TITLES = {
    "code_security_review": "Static Python code review",
    "company_analysis": "Company analysis with durable workflow steps",
    "content_team": "An editorial team with specialist agents",
    "document_qa": "Answers from local documents",
    "expense_review": "Expense review with an approved local queue",
    "flight_planner": "Flight planning within route and budget constraints",
    "greek_localization": "English and Greek localization",
    "incident_team": "Incident review with persistent team messages",
    "scoped_preferences": "Scoped preferences that survive a restart",
    "support_case": "Customer support with an approved case queue",
}


def generated(root: Path) -> dict[Path, str]:
    sources = json.loads((root / "research/sources.json").read_text(encoding="utf-8"))[
        "source_files"
    ]
    files = {}
    rows = [
        "# Source map",
        "",
        "These original QAgents applications draw on the upstream patterns linked below. "
        "The upstream frameworks were inspected without executing them. Source "
        "links are pinned to the inspected commits. "
        "Repository license metadata is retained in the "
        "[catalog](../research/sources.json). No upstream source modules or assets are bundled.",
        "",
    ]
    for name, title in CATALOG.items():
        title = GUIDE_TITLES.get(name, title)
        indexes, flow, checks, limits = DETAILS[name]
        refs = [sources[index] for index in indexes]
        links = ", ".join(f"[{r['repository']} · {r['path']}]({r['url']})" for r in refs)
        module = load(name)
        files[root / f"samples/inputs/{name}.json"] = (
            json.dumps(module.DEFAULT, indent=2, ensure_ascii=False) + "\n"
        )
        guide = (
            f"# {title}\n\n{flow}\n\n"
            f"[QAgents implementation](../../src/qagents_examples/cases/{name}.py) | "
            f"[Example input](../../samples/inputs/{name}.json) | "
            f"[Recorded output](../../samples/outputs/{name}/report.json)\n\n"
            "![Task input, tool execution and independent application verification]"
            "(../../assets/diagrams/application-flow.svg)\n\n"
            "## Run\n\nFrom the checkout after the "
            "[setup](../../README.md#start-in-a-fresh-workspace):\n\n"
            f"```console\nuv run --locked qagents-examples run {name} "
            f"--input samples/inputs/{name}.json --output .runs/{name}-demo\n```\n\n"
            "Choose a fresh output path for every run. Offline mode supplies recorded "
            "model replies. QAgents still executes the tools, session journals and "
            "application checks. "
            "The [provider guide](../providers.md) shows how to use the "
            "same implementation with a configured model.\n\n"
            f"## What is checked\n\n{checks}\n\n"
            f"## Scope and limits\n\n{limits}\n\n"
            "Every agent has finite turns, tokens, tool calls and "
            "deadlines. A failed verifier or incomplete "
            "run returns a nonzero CLI exit. Local action tools "
            "pause for approval. Use `--approval decline` "
            "to inspect the refusal path.\n\n"
            f"## Inspected source\n\n{links}\n"
        )
        files[root / f"docs/use-cases/{name}.md"] = guide
        rows += [
            f"## {title}",
            "",
            f"[Implementation](../src/qagents_examples/cases/{name}.py)",
            "",
            links,
            "",
            flow,
            "",
            limits,
            "",
        ]
    files[root / "docs/source-map.md"] = "\n".join(rows)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    files = generated(root)
    mismatches = []
    for path, text in files.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                mismatches.append(path.relative_to(root).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
    if mismatches:
        raise SystemExit("Regenerate documentation: " + ", ".join(mismatches))
    print(
        f"{'Checked' if args.check else 'Generated'} {len(files)} "
        "guides/source maps/fixture inputs."
    )


if __name__ == "__main__":
    main()
