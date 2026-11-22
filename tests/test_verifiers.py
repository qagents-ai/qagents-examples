import copy

import pytest
from qagents.models.testing import FunctionModel, ScriptedModel, call

from qagents_examples.cases import (
    citation_research,
    code_security_review,
    company_analysis,
    content_team,
    document_qa,
    flight_planner,
    grant_proposal,
    greek_localization,
    invoice_audit,
    lead_qualification,
    meeting_actions,
    recruitment_review,
    support_case,
)
from qagents_examples.runtime import Context, Outbox, VerificationError


def invalid_examples():
    invoice = invoice_audit.Input.model_validate(invoice_audit.DEFAULT)
    yield (
        invoice_audit.verify,
        invoice_audit.Audit(
            invoice_id=invoice.invoice_id,
            computed_subtotal_cents=37000,
            expected_total_cents=44400,
            discrepancies=[],
        ),
        invoice,
    )
    leads = lead_qualification.Input.model_validate(lead_qualification.DEFAULT)
    yield lead_qualification.verify, lead_qualification.Answer(scores=[], qualified_ids=[]), leads
    meeting = meeting_actions.Input.model_validate(meeting_actions.DEFAULT)
    yield (
        meeting_actions.verify,
        meeting_actions.Answer(actions=meeting_actions.commitments(meeting)[:1]),
        meeting,
    )
    flights = flight_planner.Input.model_validate(flight_planner.DEFAULT)
    yield flight_planner.verify, flight_planner.Answer(flight_id="Q103", price_cents=14000), flights
    recruitment = recruitment_review.Input.model_validate(recruitment_review.DEFAULT)
    worksheet = recruitment_review.worksheet(recruitment)
    worksheet.candidates[0].mentions[0].quote = "Invented experience."
    yield recruitment_review.verify, worksheet, recruitment
    documents = document_qa.Input.model_validate(document_qa.DEFAULT)
    yield (
        document_qa.verify,
        document_qa.Answer(answer="Refund anytime.", source_id="returns-v1"),
        documents,
    )
    article = content_team.Input.model_validate(content_team.DEFAULT)
    yield (
        content_team.verify,
        content_team.Article(
            title=article.topic,
            paragraphs=[content_team.Paragraph(source_id="other", quote="Invented.")],
        ),
        article,
    )
    source = code_security_review.Input.model_validate(code_security_review.DEFAULT)
    yield code_security_review.verify, code_security_review.Answer(findings=[]), source
    company = company_analysis.Input.model_validate(company_analysis.DEFAULT)
    yield (
        company_analysis.verify,
        company_analysis.Memo(
            company=company.company, metrics=company_analysis.metrics(company), risks=[]
        ),
        company,
    )
    project = grant_proposal.Input.model_validate(grant_proposal.DEFAULT)
    yield (
        grant_proposal.verify,
        grant_proposal.draft(project).model_copy(update={"budget_cents": 1}),
        project,
    )
    translation = greek_localization.Input.model_validate(greek_localization.DEFAULT)
    yield (
        greek_localization.verify,
        greek_localization.Translation(
            target="el", text="Γεια σου {name}. Το προϊόν {order_id} είναι έτοιμο."
        ),
        translation,
    )
    research = citation_research.Input.model_validate(citation_research.DEFAULT)
    yield (
        citation_research.verify,
        citation_research.Brief(
            title="Bad", claims=[citation_research.Claim(source="pilot", quote="999 learners")]
        ),
        research,
    )


@pytest.mark.parametrize("verify,answer,data", list(invalid_examples()))
def test_well_shaped_but_wrong_outputs_fail_verification(verify, answer, data):
    with pytest.raises(VerificationError):
        verify(answer, data)


async def test_native_agent_turn_budget_is_not_reported_as_success(tmp_path):
    ctx = Context(
        tmp_path,
        model_factory=lambda name, replies: FunctionModel(lambda request: call("read_sources")),
    )
    try:
        with pytest.raises(VerificationError, match="limit_reached"):
            await citation_research.run(ctx)
        assert len(ctx.models[0].requests) == 12
        assert not (tmp_path / "brief.json").exists()
    finally:
        await ctx.close()


async def test_model_cannot_queue_another_customers_order(tmp_path):
    def factory(name, replies):
        if name == "support_triage":
            return ScriptedModel(replies)
        return ScriptedModel(
            [
                call("inspect_order", order_id="ALIEN"),
                call("queue_case", order_id="ALIEN"),
                '{"order_id":"ORD-7","queued":false}',
            ]
        )

    ctx = Context(tmp_path, model_factory=factory)
    try:
        with pytest.raises(VerificationError):
            await support_case.run(ctx)
        assert Outbox(tmp_path / "support.sqlite3").rows() == []
        assert any(p.is_error for r in ctx.results for m in r.new_messages for p in m.tool_results)
    finally:
        await ctx.close()


async def test_changed_meeting_input_is_not_a_fixed_answer(tmp_path):
    raw = copy.deepcopy(meeting_actions.DEFAULT)
    raw["transcript"] = "Maria: I will publish the notes by 2027-01-10."
    ctx = Context(tmp_path)
    try:
        answer = await meeting_actions.run(ctx, raw)
        assert answer["actions"][0]["task"] == "publish the notes"
        assert answer["actions"][0]["due"] == "2027-01-10"
    finally:
        await ctx.close()
