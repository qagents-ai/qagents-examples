import copy

import pytest
from qagents.models.testing import ScriptedModel

from qagents_examples.cases import citation_research, invoice_audit
from qagents_examples.runtime import Context, Outbox, VerificationError


@pytest.mark.parametrize("module", [citation_research, invoice_audit])
async def test_real_agent_loops_with_artifacts(module, tmp_path):
    ctx = Context(tmp_path)
    try:
        outcome = await module.run(ctx)
        assert outcome and ctx.results
        assert ctx.summary(module.__name__, outcome)["usage"]["requests"] >= 1
        assert list(tmp_path.glob("*.json"))
    finally:
        await ctx.close()


async def test_invented_citation_fails_application_verifier(tmp_path):
    bad = '{"title":"Invented","claims":[{"source":"other","quote":"false"}]}'
    ctx = Context(tmp_path, model_factory=lambda name, replies: ScriptedModel([bad]))
    try:
        with pytest.raises(VerificationError, match="unknown research citation"):
            await citation_research.run(ctx)
        assert not list(tmp_path.glob("*.json"))
    finally:
        await ctx.close()


async def test_invoice_alternate_data_is_computed_not_canned(tmp_path):
    raw = copy.deepcopy(invoice_audit.DEFAULT)
    raw.update(printed_subtotal_cents=37500, printed_total_cents=44900)
    ctx = Context(tmp_path)
    try:
        assert (await invoice_audit.run(ctx, raw))["discrepancies"] == []
    finally:
        await ctx.close()


def test_outbox_is_payload_bound(tmp_path):
    box = Outbox(tmp_path / "outbox.sqlite3")
    first = box.put("op-1", "case", {"order": "A"})
    assert box.put("op-1", "case", {"order": "A"}) == first
    with pytest.raises(ValueError, match="another payload"):
        box.put("op-1", "case", {"order": "B"})
    assert len(box.rows()) == 1
