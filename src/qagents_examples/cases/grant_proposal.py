"""Draft an illustrative KA220 cooperation proposal with a separate budget-review specialist."""

from typing import Literal

from pydantic import Field
from qagents import tool
from qagents.models.testing import call

from ..runtime import Context, Record, encoded, require

DEFAULT = {
    "title": "BRIDGE: Community Digital Learning",
    "challenge": "Adult educators need reusable, accessible methods for teaching digital skills.",
    "partners": [
        {"partner_id": "P1", "country": "EL", "role": "coordination and adult learning"},
        {"partner_id": "P2", "country": "IT", "role": "accessible learning design"},
        {"partner_id": "P3", "country": "ES", "role": "piloting and evaluation"},
    ],
    "budget_cents": 12000000,
    "work_packages": [
        {
            "wp_id": "WP1",
            "title": "Management and co-design",
            "lead": "P1",
            "budget_cents": 2000000,
            "deliverables": ["Needs-validation protocol", "Governance and quality plan"],
        },
        {
            "wp_id": "WP2",
            "title": "Accessible toolkit and educator pilots",
            "lead": "P2",
            "budget_cents": 6000000,
            "deliverables": ["Six accessible learning modules", "Three local educator pilots"],
        },
        {
            "wp_id": "WP3",
            "title": "Evaluation and transfer",
            "lead": "P3",
            "budget_cents": 4000000,
            "deliverables": ["Pilot evaluation report", "Adaptation and sustainability handbook"],
        },
    ],
}


class Partner(Record):
    partner_id: str
    country: str
    role: str


class WorkPackage(Record):
    wp_id: str
    title: str
    lead: str
    budget_cents: int = Field(gt=0, strict=True)
    deliverables: list[str] = Field(min_length=1, max_length=10)


class Input(Record):
    title: str
    challenge: str
    partners: list[Partner] = Field(min_length=2, max_length=12)
    budget_cents: int = Field(gt=0, strict=True)
    work_packages: list[WorkPackage] = Field(min_length=1, max_length=10)


class Proposal(Record):
    action: Literal["KA220 cooperation partnership"]
    title: str
    summary: str = Field(min_length=80)
    needs: str = Field(min_length=80)
    objectives: list[str] = Field(min_length=2)
    partnership: str = Field(min_length=80)
    methodology: str = Field(min_length=80)
    work_packages: list[WorkPackage]
    budget_cents: int
    evaluation: str = Field(min_length=80)
    impact: str = Field(min_length=80)
    risks: list[str] = Field(min_length=2)
    evidence_gaps: list[str] = Field(min_length=1)


class BudgetReview(Record):
    total_cents: int
    matches_requested_budget: bool


def draft(data: Input) -> Proposal:
    return Proposal(
        action="KA220 cooperation partnership",
        title=data.title,
        summary=f"{data.title} proposes a practical cooperation programme for adult educators. "
        f"{data.challenge} Partners will co-design a reusable toolkit, test it with local educator "
        "groups and document the adaptations needed in different settings. The project combines "
        "a shared needs-validation protocol, accessible learning resources, supported local pilots "
        "and a transparent evaluation process. Its draft outputs will be reviewed by practitioners "
        "before wider dissemination. This fictional "
        "application exercise uses an illustrative budget "
        "and partner roles. It does not assert that any "
        "applicant is eligible or that a funding call "
        "has been checked. The consortium must substantiate the "
        "need and approve the final application.",
        needs=f"The starting challenge is: {data.challenge} This is a supplied problem statement, "
        "not completed needs research. Before finalising the "
        "intervention, each partner will consult "
        "educators and prospective participants, record "
        "accessibility barriers and compare existing "
        "provision. A common interview guide and consent procedure will support comparison while "
        "leaving room for local context. Partners will "
        "distinguish observed needs from assumptions, "
        "summarise the evidence in a needs matrix and use it to "
        "prioritise modules. Recruitment targets "
        "and learning outcomes will be revised when this "
        "evidence is available. The application should "
        "cite those findings rather than invent baseline statistics or endorsements.",
        objectives=[
            "Validate educator needs and agree observable learning outcomes.",
            "Co-design and pilot six accessible learning modules with practitioner feedback.",
            "Publish an evaluated adaptation handbook and a partner-owned continuation plan.",
        ],
        partnership="The supplied partnership is "
        + "; ".join(f"{p.partner_id} ({p.country}): {p.role}" for p in data.partners)
        + ". A steering group will maintain a decision log, review progress against deliverables "
        "and resolve changes to scope or resources. Each work-package lead will coordinate a small "
        "delivery group with a named deputy. Partners will agree responsibilities, accessibility "
        "checks, evidence retention and review dates before "
        "activities start. Participation in this "
        "fictional plan is not a statement of legal commitment; actual institutions must confirm "
        "capacity, eligibility and their authorised representatives before submission.",
        methodology="Delivery follows a co-design, pilot, review "
        "and transfer cycle. Educators will "
        "help turn the validated needs into short learning tasks with accessible alternatives. "
        "Partners will review draft modules against a shared "
        "checklist, then facilitate small local "
        "pilots and collect consented feedback. Review meetings will compare implementation notes "
        "across sites, decide which changes are supported by evidence and version the toolkit. "
        "Materials will include facilitator notes, adaptable activities and assessment examples. "
        "A final transfer workshop will test whether another educator can use the handbook without "
        "the original authors present. Evaluation findings will shape the final release.",
        work_packages=data.work_packages,
        budget_cents=data.budget_cents,
        evaluation="The evaluation plan will link each objective to a defined output and an "
        "observable outcome. A baseline and follow-up "
        "educator self-assessment will be supplemented "
        "by task demonstrations and facilitator observations. The team will predefine indicators, "
        "collection windows and responsibility for missing data. Quantitative summaries will be "
        "reported alongside participant feedback and accessibility findings. Reviewers will record "
        "limitations and avoid attributing every observed "
        "change to the project. A separate quality "
        "review will check deliverable completeness, evidence provenance and the usability of the "
        "adaptation handbook. Indicator targets require agreement after needs validation.",
        impact="Expected benefits are more consistent educator practice, reusable accessible "
        "materials and stronger cooperation between the participating organisations. These are "
        "intended outcomes rather than measured achievements. The dissemination plan will identify "
        "specific practitioner audiences, appropriate channels and opportunities to demonstrate "
        "the materials in use. Each partner will nominate an owner for maintaining its adapted "
        "resources and explain the staff time needed after the funded period. The final handbook "
        "will distinguish mandatory project elements from local adaptations and include evidence "
        "limitations. Long-term uptake will require later "
        "follow-up rather than an assumed multiplier.",
        risks=[
            "Recruitment delays: agree reserve recruitment "
            "channels and review participation early.",
            "Accessibility gaps: test draft resources with users and budget time for revision.",
            "Partner delivery delays: use deputies, milestone "
            "reviews and a documented change process.",
        ],
        evidence_gaps=[
            "Current official call, eligibility and funding rules have not been verified.",
            "Needs-validation evidence, partner commitments and "
            "approved indicator targets are required.",
            "Budget eligibility and justification require review against the selected actual call.",
        ],
    )


def verify(answer: Proposal, data: Input) -> None:
    ids = {p.partner_id for p in data.partners}
    require(len(ids) == len(data.partners), "duplicate proposal partner IDs")
    require(
        len({w.wp_id for w in data.work_packages}) == len(data.work_packages),
        "duplicate work packages",
    )
    require(all(w.lead in ids for w in data.work_packages), "unknown work-package lead")
    require(
        answer.title == data.title and answer.work_packages == data.work_packages,
        "proposal changed the supplied project plan",
    )
    require(
        answer.budget_cents
        == data.budget_cents
        == sum(w.budget_cents for w in answer.work_packages),
        "proposal budget does not reconcile",
    )


def markdown(answer: Proposal) -> str:
    parts = [
        f"# {answer.title}",
        "**Fictional draft · KA220 cooperation partnership · human review required.**",
    ]
    for heading, text in [
        ("Summary", answer.summary),
        ("Needs", answer.needs),
        ("Objectives", "\n".join(f"- {x}" for x in answer.objectives)),
        ("Partnership", answer.partnership),
        ("Methodology", answer.methodology),
    ]:
        parts.append(f"## {heading}\n\n{text}")
    parts.append(
        "## Work plan and budget\n\n| WP | Lead | Budget (EUR) | "
        "Deliverables |\n| --- | --- | ---: | --- |"
    )
    for wp in answer.work_packages:
        parts.append(
            f"| {wp.wp_id}: {wp.title} | {wp.lead} | {wp.budget_cents / 100:.2f} | "
            + "; ".join(wp.deliverables)
            + " |"
        )
    parts.append(f"\nTotal: EUR {answer.budget_cents / 100:.2f}.")
    for heading, text in [
        ("Evaluation", answer.evaluation),
        ("Impact and sustainability", answer.impact),
        ("Risks and mitigations", "\n".join(f"- {x}" for x in answer.risks)),
        ("Evidence gaps before submission", "\n".join(f"- {x}" for x in answer.evidence_gaps)),
    ]:
        parts.append(f"## {heading}\n\n{text}")
    return "\n\n".join(parts) + "\n"


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)
    golden = draft(data)
    verify(golden, data)

    @tool(read_only=True)
    def check_budget() -> dict:
        """Sum the supplied work-package budgets and compare against the requested budget."""
        total = sum(w.budget_cents for w in data.work_packages)
        return BudgetReview(
            total_cents=total, matches_requested_budget=total == data.budget_cents
        ).model_dump()

    budget = ctx.agent(
        "budget_reviewer",
        [
            call("check_budget"),
            encoded(BudgetReview(total_cents=data.budget_cents, matches_requested_budget=True)),
        ],
        tools=[check_budget],
        output_type=BudgetReview,
        instructions="Call check_budget and return its exact total and match flag.",
    )
    writer = ctx.agent(
        "programme_writer",
        [encoded(golden)],
        output_type=Proposal,
        instructions="Draft every proposal section using the "
        "supplied plan. Keep all work packages, "
        "leads, budgets and title unchanged. Identify missing evidence and call-rule checks; "
        "do not invent participant statistics, partner commitments or funding eligibility.",
    )
    prompt = encoded(data)
    coordinator = ctx.agent(
        "proposal_coordinator",
        [
            [
                call("draft_programme", task=prompt),
                call("review_budget", task="Check the supplied budget."),
            ],
            encoded(golden),
        ],
        tools=[
            writer.as_tool(name="draft_programme", read_only=True),
            budget.as_tool(name="review_budget", read_only=True),
        ],
        output_type=Proposal,
        instructions="Ask draft_programme for all sections and review_budget for a separate check. "
        "Return the complete draft with its original work plan and explicit evidence gaps.",
    )
    answer = await ctx.execute(coordinator, prompt)
    verify(answer, data)
    ctx.artifact("proposal.md", markdown(answer))
    ctx.artifact("proposal.json", answer)
    return {
        "title": answer.title,
        "budget_cents": answer.budget_cents,
        "work_packages": len(answer.work_packages),
        "evidence_gaps": answer.evidence_gaps,
        "verification": "structure, work-package identities and "
        "arithmetic; prose/call compliance need review",
    }
