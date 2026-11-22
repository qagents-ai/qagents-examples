"""Extract invoice lines, then independently reconcile printed totals in integer cents."""

from pydantic import Field

from ..runtime import Context, Record, encoded, require

DEFAULT = {
    "invoice_id": "INV-204",
    "currency": "EUR",
    "lines": [{"description": "Workshop", "quantity": 3, "unit_cents": 12500}],
    "printed_subtotal_cents": 37000,
    "tax_cents": 7400,
    "printed_total_cents": 44400,
}


class Line(Record):
    description: str
    quantity: int = Field(gt=0, strict=True)
    unit_cents: int = Field(ge=0, strict=True)


class Input(Record):
    invoice_id: str
    currency: str = Field(pattern="^[A-Z]{3}$")
    lines: list[Line] = Field(min_length=1, max_length=100)
    printed_subtotal_cents: int = Field(ge=0, strict=True)
    tax_cents: int = Field(ge=0, strict=True)
    printed_total_cents: int = Field(ge=0, strict=True)


class Audit(Record):
    invoice_id: str
    computed_subtotal_cents: int
    expected_total_cents: int
    discrepancies: list[str]


def verify(answer: Audit, data: Input) -> None:
    subtotal = sum(line.quantity * line.unit_cents for line in data.lines)
    issues = []
    if data.printed_subtotal_cents != subtotal:
        issues.append("subtotal")
    if data.printed_total_cents != subtotal + data.tax_cents:
        issues.append("total")
    require(answer.invoice_id == data.invoice_id, "invoice identity mismatch")
    require(answer.computed_subtotal_cents == subtotal, "incorrect invoice line arithmetic")
    require(answer.expected_total_cents == subtotal + data.tax_cents, "incorrect invoice total")
    require(sorted(answer.discrepancies) == issues, "missed or invented invoice discrepancy")


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)
    subtotal = sum(x.quantity * x.unit_cents for x in data.lines)
    expected = Audit(
        invoice_id=data.invoice_id,
        computed_subtotal_cents=subtotal,
        expected_total_cents=subtotal + data.tax_cents,
        discrepancies=(["subtotal"] if subtotal != data.printed_subtotal_cents else [])
        + (["total"] if subtotal + data.tax_cents != data.printed_total_cents else []),
    )
    agent = ctx.agent(
        "invoice_auditor",
        [encoded(expected)],
        output_type=Audit,
        instructions="Audit the invoice. Compute every line and total; flag subtotal/total errors.",
    )
    answer = await ctx.execute(agent, encoded(data))
    verify(answer, data)
    ctx.artifact("invoice-audit.json", answer)
    return answer.model_dump()
