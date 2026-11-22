import pytest

from qagents_examples.cases import expense_review, inventory_order, lead_qualification, support_case
from qagents_examples.runtime import Context, Outbox


@pytest.mark.parametrize(
    "module", [support_case, expense_review, inventory_order, lead_qualification]
)
async def test_business_agents_run_real_tools_and_verify(module, tmp_path):
    ctx = Context(tmp_path)
    try:
        outcome = await module.run(ctx)
        assert outcome and ctx.results and ctx.summary(module.__name__, outcome)["verified"]
        assert any(p.tool_results for r in ctx.results for p in r.new_messages)
    finally:
        await ctx.close()


@pytest.mark.parametrize(
    "module,db",
    [
        (support_case, "support.sqlite3"),
        (expense_review, "reimbursements.sqlite3"),
        (inventory_order, "procurement.sqlite3"),
    ],
)
async def test_declining_never_writes_a_destination_action(module, db, tmp_path):
    ctx = Context(tmp_path, approval="decline")
    try:
        outcome = await module.run(ctx)
        assert outcome["queued"] is False
        assert ctx.decisions and all(not x["approved"] for x in ctx.decisions)
        assert Outbox(tmp_path / db).rows() == []
    finally:
        await ctx.close()


async def test_inventory_with_sufficient_stock_never_requests_approval(tmp_path):
    ctx = Context(tmp_path)
    try:
        outcome = await inventory_order.run(ctx, {**inventory_order.DEFAULT, "on_hand": 40})
        assert outcome["quantity"] == 0 and not outcome["queued"]
        assert ctx.decisions == []
    finally:
        await ctx.close()
