"""Score fictional inbound leads against explicit business criteria; create review drafts."""

from pydantic import Field
from qagents import tool
from qagents.models.testing import call

from ..runtime import Context, Record, encoded, require

DEFAULT = {
    "sector": "education",
    "threshold": 70,
    "leads": [
        {"lead_id": "L1", "sector": "education", "employees": 60, "requested_demo": True},
        {"lead_id": "L2", "sector": "retail", "employees": 4, "requested_demo": False},
    ],
}


class Lead(Record):
    lead_id: str
    sector: str
    employees: int = Field(ge=0, strict=True)
    requested_demo: bool


class Input(Record):
    sector: str
    threshold: int = Field(ge=0, le=100)
    leads: list[Lead] = Field(min_length=1, max_length=50)


class Score(Record):
    lead_id: str
    score: int = Field(ge=0, le=100)


class Answer(Record):
    scores: list[Score]
    qualified_ids: list[str]


def score(lead: Lead, sector: str) -> int:
    return (
        25 * (lead.sector == sector) + 25 * (10 <= lead.employees <= 500) + 50 * lead.requested_demo
    )


def verify(answer: Answer, data: Input) -> None:
    expected = {x.lead_id: score(x, data.sector) for x in data.leads}
    require(len(expected) == len(data.leads), "duplicate lead IDs")
    require(len(answer.scores) == len(expected), "missing lead scores")
    require({x.lead_id: x.score for x in answer.scores} == expected, "lead rubric mismatch")
    qualified = sorted(k for k, value in expected.items() if value >= data.threshold)
    require(sorted(answer.qualified_ids) == qualified, "incorrect lead qualification")


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)

    @tool(read_only=True)
    def score_leads() -> list[dict]:
        """Apply the sector/size/demo rubric to supplied inbound leads."""
        return [{"lead_id": x.lead_id, "score": score(x, data.sector)} for x in data.leads]

    expected = Answer(
        scores=[Score(lead_id=x.lead_id, score=score(x, data.sector)) for x in data.leads],
        qualified_ids=[x.lead_id for x in data.leads if score(x, data.sector) >= data.threshold],
    )
    agent = ctx.agent(
        "lead_reviewer",
        [call("score_leads"), encoded(expected)],
        tools=[score_leads],
        output_type=Answer,
        instructions="Use the score tool; return every score and IDs meeting "
        f"threshold {data.threshold}. This creates a review artifact, never sends outreach.",
    )
    answer = await ctx.execute(agent, "Qualify the supplied inbound leads.")
    verify(answer, data)
    ctx.artifact("lead-review.json", answer)
    return answer.model_dump()
