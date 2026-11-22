"""Look up an authorized order and queue a local support case after approval."""

from qagents import RunContext, tool
from qagents.models.testing import call

from ..runtime import Context, Outbox, Record, encoded, require

DEFAULT = {
    "order_id": "ORD-7",
    "owner": "customer-7",
    "principal": "customer-7",
    "delivery_status": "delayed",
    "issue": "Parcel is late.",
}


class Input(Record):
    order_id: str
    owner: str
    principal: str
    delivery_status: str
    issue: str


class Answer(Record):
    order_id: str
    queued: bool


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)
    box = Outbox(ctx.directory / "support.sqlite3")

    @tool(read_only=True)
    def inspect_order(order_id: str) -> dict:
        """Read the order belonging to the application's authenticated customer."""
        require(order_id == data.order_id and data.owner == data.principal, "order access denied")
        return {"order_id": order_id, "status": data.delivery_status}

    @tool(requires_approval=True, idempotent=True)
    def queue_case(context: RunContext, order_id: str) -> dict:
        """Create one local support case for this authorized order, with approval."""
        inspect_order_data = order_id == data.order_id and data.owner == data.principal
        require(inspect_order_data, "order access denied")
        return box.put(
            context.operation_id,
            "support",
            {
                "order_id": order_id,
                "customer": data.principal,
                "issue": data.issue,
            },
        )

    replies = [
        call("inspect_order", order_id=data.order_id),
        call("queue_case", order_id=data.order_id),
        lambda request: encoded(Answer(order_id=data.order_id, queued=bool(box.rows()))),
    ]
    specialist = ctx.agent(
        "support_specialist",
        replies,
        tools=[inspect_order, queue_case],
        output_type=Answer,
        instructions="Inspect the given order, then request approval to queue its support case. "
        "Report queued=false if declined. Do not claim refunds or external messages.",
    )
    triage = ctx.agent(
        "support_triage",
        [call("transfer_to_support_specialist")],
        handoffs=[specialist],
        instructions="Transfer this order support conversation to support_specialist.",
    )
    answer = await ctx.execute(triage, encoded({"order_id": data.order_id, "issue": data.issue}))
    require(ctx.results[-1].agent == "support_specialist", "support handoff did not complete")
    rows = box.rows()
    require(answer.order_id == data.order_id, "support order mismatch")
    require(any(d["tool"] == "queue_case" for d in ctx.decisions), "support approval was skipped")
    allowed = any(d["tool"] == "queue_case" and d["approved"] for d in ctx.decisions)
    require(
        answer.queued == bool(rows) == allowed, "support result does not match local destination"
    )
    if rows:
        require(
            len(rows) == 1 and rows[0]["payload"]["order_id"] == data.order_id,
            "incorrect support destination state",
        )
    ctx.artifact("support-result.json", answer)
    return answer.model_dump()
