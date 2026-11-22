"""Apply a supplied expense policy, then queue eligible reimbursements after approval."""

from pydantic import Field
from qagents import RunContext, tool
from qagents.models.testing import call

from ..runtime import Context, Outbox, Record, encoded, require

DEFAULT = {
    "limits_cents": {"rail": 6000, "hotel": 10000},
    "expenses": [
        {"expense_id": "E1", "category": "rail", "amount_cents": 4500, "receipt": True},
        {"expense_id": "E2", "category": "hotel", "amount_cents": 13000, "receipt": True},
    ],
}


class Expense(Record):
    expense_id: str
    category: str
    amount_cents: int = Field(ge=0, strict=True)
    receipt: bool


class Input(Record):
    limits_cents: dict[str, int]
    expenses: list[Expense] = Field(min_length=1, max_length=100)


class Answer(Record):
    eligible_ids: list[str]
    total_cents: int
    queued: bool


def eligible(data: Input) -> list[Expense]:
    return [
        x
        for x in data.expenses
        if x.receipt
        and x.category in data.limits_cents
        and x.amount_cents <= data.limits_cents[x.category]
    ]


def verify(answer: Answer, data: Input) -> None:
    items = eligible(data)
    require(len({x.expense_id for x in data.expenses}) == len(data.expenses), "duplicate expenses")
    require(
        sorted(answer.eligible_ids) == sorted(x.expense_id for x in items),
        "expense policy mismatch",
    )
    require(
        answer.total_cents == sum(x.amount_cents for x in items), "incorrect reimbursement total"
    )


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)
    box = Outbox(ctx.directory / "reimbursements.sqlite3")
    items = eligible(data)
    ids = sorted(x.expense_id for x in items)
    total = sum(x.amount_cents for x in items)

    @tool(read_only=True)
    def expense_policy() -> dict:
        """Read supplied receipt rules, category limits and expense evidence."""
        return data.model_dump()

    @tool(requires_approval=True, idempotent=True)
    def request_reimbursement(context: RunContext, expense_ids: list[str]) -> dict:
        """Queue all and only eligible expense IDs for local review; never pays money."""
        require(sorted(expense_ids) == ids and bool(ids), "ineligible reimbursement request")
        return box.put(context.operation_id, "reimbursement", {"ids": ids, "total_cents": total})

    replies = [call("expense_policy")]
    if ids:
        replies.append(call("request_reimbursement", expense_ids=ids))
    replies.append(
        lambda request: encoded(
            Answer(eligible_ids=ids, total_cents=total, queued=bool(box.rows()))
        )
    )
    agent = ctx.agent(
        "expense_reviewer",
        replies,
        tools=[expense_policy, request_reimbursement],
        output_type=Answer,
        instructions="Read policy. An expense needs a receipt, known category and amount <= limit. "
        "Request approval to queue eligible IDs. Return their sum and actual queued flag.",
    )
    answer = await ctx.execute(agent, "Review these expenses under the supplied fictional policy.")
    verify(answer, data)
    allowed = any(d["tool"] == "request_reimbursement" and d["approved"] for d in ctx.decisions)
    require(not ids or bool(ctx.decisions), "reimbursement approval was skipped")
    require(answer.queued == bool(box.rows()) == allowed, "reimbursement destination mismatch")
    require(len(box.rows()) == int(allowed), "duplicate reimbursement batch")
    ctx.artifact("expense-review.json", answer)
    return answer.model_dump()
