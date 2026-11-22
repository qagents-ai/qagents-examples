import copy

import pytest

from qagents_examples.cases import grant_proposal
from qagents_examples.runtime import Context, VerificationError


async def test_proposal_has_all_sections_and_real_specialist_runs(tmp_path):
    ctx = Context(tmp_path)
    try:
        answer = await grant_proposal.run(ctx)
        assert answer["work_packages"] == 3 and answer["budget_cents"] == 12000000
        text = (tmp_path / "proposal.md").read_text(encoding="utf-8")
        assert text.count("## ") == 10
        assert len(text.split()) >= 700
        assert len(ctx.models) == 3
        assert ctx.summary("grant_proposal", answer)["usage"]["requests"] == 5
    finally:
        await ctx.close()


async def test_unbalanced_project_input_fails_before_model_calls(tmp_path):
    raw = copy.deepcopy(grant_proposal.DEFAULT)
    raw["budget_cents"] += 100
    ctx = Context(tmp_path)
    with pytest.raises(VerificationError, match="budget"):
        await grant_proposal.run(ctx, raw)
    assert ctx.models == []
