"""An editor delegates to a writer, who delegates source collection to a researcher."""

from pydantic import Field
from qagents import tool
from qagents.models.testing import call

from ..runtime import Context, Record, encoded, require

DEFAULT = {
    "topic": "The fictional community learning pilot",
    "sources": {
        "attendance": "Forty learners joined the pilot.",
        "completion": "Thirty-two learners completed the activities.",
    },
}


class Input(Record):
    topic: str
    sources: dict[str, str]


class Paragraph(Record):
    source_id: str
    quote: str = Field(min_length=1)


class Article(Record):
    title: str
    paragraphs: list[Paragraph] = Field(min_length=1, max_length=20)


def verify(answer: Article, data: Input) -> None:
    require(answer.title == data.topic, "editorial topic changed")
    require(len(answer.paragraphs) == len(data.sources), "editorial evidence missing or duplicated")
    require(
        {p.source_id: p.quote for p in answer.paragraphs} == data.sources,
        "article evidence does not match supplied sources",
    )


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)

    @tool(read_only=True)
    def collect_sources() -> dict[str, str]:
        """Read the application's source evidence for the editorial brief."""
        return data.sources

    golden = Article(
        title=data.topic,
        paragraphs=[Paragraph(source_id=k, quote=v) for k, v in data.sources.items()],
    )
    researcher = ctx.agent(
        "source_researcher",
        [call("collect_sources"), encoded(golden)],
        tools=[collect_sources],
        output_type=Article,
        instructions="Read sources. Return the exact topic as title, "
        "and every source as a {source_id,quote} paragraph. Keep evidence verbatim.",
    )
    prompt = encoded({"topic": data.topic})
    writer = ctx.agent(
        "evidence_writer",
        [call("research", task=prompt), encoded(golden)],
        output_type=Article,
        tools=[researcher.as_tool(name="research", read_only=True)],
        instructions="Ask research for the source-backed article. "
        "Preserve its title and all quotes.",
    )
    editor = ctx.agent(
        "editor",
        [call("write_article", task=prompt), encoded(golden)],
        output_type=Article,
        tools=[writer.as_tool(name="write_article", read_only=True)],
        instructions="Delegate to write_article. Return the verified evidence article unchanged.",
    )
    answer = await ctx.execute(editor, prompt)
    verify(answer, data)
    markdown = (
        f"# {answer.title}\n\n"
        + "\n\n".join(f"{p.quote} [{p.source_id}]" for p in answer.paragraphs)
        + "\n"
    )
    ctx.artifact("article.md", markdown)
    return {**answer.model_dump(), "team": ["editor", "evidence_writer", "source_researcher"]}
