"""Choose the cheapest feasible fixture flight; verify every route/date/budget constraint."""

from datetime import date

from pydantic import Field
from qagents import tool
from qagents.models.testing import call

from ..runtime import Context, Record, encoded, require

DEFAULT = {
    "origin": "ATH",
    "destination": "BRU",
    "day": "2026-12-10",
    "budget_cents": 22000,
    "flights": [
        {
            "flight_id": "Q101",
            "origin": "ATH",
            "destination": "BRU",
            "day": "2026-12-10",
            "price_cents": 19000,
        },
        {
            "flight_id": "Q102",
            "origin": "ATH",
            "destination": "BRU",
            "day": "2026-12-10",
            "price_cents": 21000,
        },
        {
            "flight_id": "Q103",
            "origin": "ATH",
            "destination": "MAD",
            "day": "2026-12-10",
            "price_cents": 14000,
        },
    ],
}


class Flight(Record):
    flight_id: str
    origin: str = Field(pattern="^[A-Z]{3}$")
    destination: str = Field(pattern="^[A-Z]{3}$")
    day: str
    price_cents: int = Field(ge=0, strict=True)


class Input(Record):
    origin: str
    destination: str
    day: str
    budget_cents: int = Field(ge=0, strict=True)
    flights: list[Flight] = Field(max_length=100)


class Answer(Record):
    flight_id: str | None
    price_cents: int | None


def feasible(data: Input) -> list[Flight]:
    date.fromisoformat(data.day)
    return sorted(
        [
            f
            for f in data.flights
            if f.origin == data.origin
            and f.destination == data.destination
            and f.day == data.day
            and f.price_cents <= data.budget_cents
        ],
        key=lambda f: (f.price_cents, f.flight_id),
    )


def verify(answer: Answer, data: Input) -> None:
    flights = feasible(data)
    expected = (flights[0].flight_id, flights[0].price_cents) if flights else (None, None)
    require(len({f.flight_id for f in data.flights}) == len(data.flights), "duplicate flight IDs")
    require(
        (answer.flight_id, answer.price_cents) == expected,
        "flight violates cheapest feasible choice",
    )


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)

    @tool(read_only=True)
    def search_flights() -> list[dict]:
        """Read supplied fictional flight quotes; this is not a live airline search."""
        return [f.model_dump() for f in data.flights]

    options = feasible(data)
    golden = (
        Answer(flight_id=options[0].flight_id, price_cents=options[0].price_cents)
        if options
        else Answer(flight_id=None, price_cents=None)
    )
    agent = ctx.agent(
        "flight_planner",
        [call("search_flights"), encoded(golden)],
        tools=[search_flights],
        output_type=Answer,
        instructions="Search quotes and select the cheapest matching origin, "
        "destination and day within budget; tie-break by flight ID. "
        "Return nulls if none. Never book.",
    )
    prompt = data.model_dump(exclude={"flights"})
    answer = await ctx.execute(agent, encoded(prompt))
    verify(answer, data)
    ctx.artifact("flight-plan.json", answer)
    return answer.model_dump()
