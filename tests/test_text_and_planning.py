import pytest

from qagents_examples.cases import (
    flight_planner,
    greek_localization,
    meeting_actions,
    recruitment_review,
)
from qagents_examples.runtime import Context, VerificationError


@pytest.mark.parametrize(
    "module", [meeting_actions, flight_planner, recruitment_review, greek_localization]
)
async def test_typed_text_and_planning_agents(module, tmp_path):
    ctx = Context(tmp_path)
    try:
        assert await module.run(ctx)
        assert ctx.summary(module.__name__, {})["usage"]["requests"] >= 1
    finally:
        await ctx.close()


async def test_flight_budget_without_a_feasible_match(tmp_path):
    ctx = Context(tmp_path)
    try:
        answer = await flight_planner.run(ctx, {**flight_planner.DEFAULT, "budget_cents": 100})
        assert answer == {"flight_id": None, "price_cents": None}
    finally:
        await ctx.close()


async def test_greek_to_english_also_uses_a_child_agent(tmp_path):
    ctx = Context(tmp_path)
    try:
        answer = await greek_localization.run(
            ctx,
            {
                "text": greek_localization.GREEK,
                "target": "en",
                "glossary": {"παραγγελία": "order"},
            },
        )
        assert answer["text"] == greek_localization.ENGLISH
        assert len(ctx.models) == 2
        assert ctx.summary("translation", answer)["usage"]["requests"] == 3
    finally:
        await ctx.close()


def test_glossary_and_placeholder_verifier_rejects_hallucinations():
    data = greek_localization.Input.model_validate(greek_localization.DEFAULT)
    with pytest.raises(VerificationError, match="placeholder"):
        greek_localization.verify(
            greek_localization.Translation(target="el", text="Γεια σου"), data
        )
