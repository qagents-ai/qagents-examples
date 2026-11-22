"""Calculate a reorder quantity and queue a local purchase request with human approval."""

from pydantic import Field
from qagents import RunContext, tool
from qagents.models.testing import call

from ..runtime import Context, Outbox, Record, encoded, require

DEFAULT = {"sku": "KIT-4", "on_hand": 8, "target": 30, "unit_cents": 1200}


class Input(Record):
    sku: str
    on_hand: int = Field(ge=0, strict=True)
    target: int = Field(ge=0, le=10000, strict=True)
    unit_cents: int = Field(ge=0, strict=True)


class Answer(Record):
    sku: str
    quantity: int
    cost_cents: int
    queued: bool


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)
    needed = max(0, data.target - data.on_hand)
    box = Outbox(ctx.directory / "procurement.sqlite3")

    @tool(read_only=True)
    def stock_position() -> dict:
        """Read stock, target and unit cost for the application-selected SKU."""
        return data.model_dump()

    @tool(requires_approval=True, idempotent=True)
    def request_purchase(context: RunContext, quantity: int) -> dict:
        """Queue the exact replenishment quantity for approval; no supplier is contacted."""
        require(quantity == needed and needed > 0, "purchase exceeds the required replenishment")
        return box.put(
            context.operation_id,
            "purchase",
            {
                "sku": data.sku,
                "quantity": needed,
                "cost_cents": needed * data.unit_cents,
            },
        )

    replies = [call("stock_position")]
    if needed:
        replies.append(call("request_purchase", quantity=needed))
    replies.append(
        lambda request: encoded(
            Answer(
                sku=data.sku,
                quantity=needed,
                cost_cents=needed * data.unit_cents,
                queued=bool(box.rows()),
            )
        )
    )
    agent = ctx.agent(
        "inventory_planner",
        replies,
        tools=[stock_position, request_purchase],
        output_type=Answer,
        instructions="Read stock and compute max(0,target-on_hand). Request approval for that "
        "quantity only when positive. Report the quantity, cost and actual queued state.",
    )
    answer = await ctx.execute(agent, "Prepare a replenishment request.")
    require(
        (answer.sku, answer.quantity, answer.cost_cents)
        == (data.sku, needed, needed * data.unit_cents),
        "incorrect replenishment arithmetic",
    )
    allowed = any(d["tool"] == "request_purchase" and d["approved"] for d in ctx.decisions)
    require(not needed or bool(ctx.decisions), "purchase approval was skipped")
    require(answer.queued == bool(box.rows()) == allowed, "incorrect purchase destination state")
    require(len(box.rows()) == int(allowed), "duplicate purchase request")
    ctx.artifact("purchase-plan.json", answer)
    return answer.model_dump()
