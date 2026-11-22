"""Build a research brief whose factual claims carry exact source quotes."""

from pydantic import Field
from qagents import tool
from qagents.models.testing import call

from ..runtime import Context, Record, encoded, require

DEFAULT = {
    "question": "How did the fictional pilot perform?",
    "documents": {"pilot": "The pilot served 40 learners.", "review": "32 learners completed."},
}


class Input(Record):
    question: str
    documents: dict[str, str]


class Claim(Record):
    source: str
    quote: str = Field(min_length=1)


class Brief(Record):
    title: str
    claims: list[Claim] = Field(min_length=1, max_length=12)


def verify(value: Brief, data: Input) -> None:
    for claim in value.claims:
        require(claim.source in data.documents, "unknown research citation")
        require(claim.quote in data.documents[claim.source], "unsupported research quote")


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)

    @tool(read_only=True)
    def read_sources() -> dict[str, str]:
        """Read the supplied research corpus, keyed by stable citation IDs."""
        return data.documents

    expected = Brief(
        title="Pilot evidence", claims=[Claim(source=k, quote=v) for k, v in data.documents.items()]
    )
    agent = ctx.agent(
        "researcher",
        [call("read_sources"), encoded(expected)],
        tools=[read_sources],
        instructions="Read sources. Return a brief with exact, nonempty evidence quotes and IDs.",
        output_type=Brief,
    )
    answer = await ctx.execute(agent, data.question)
    verify(answer, data)
    ctx.artifact("brief.json", answer)
    return answer.model_dump()
