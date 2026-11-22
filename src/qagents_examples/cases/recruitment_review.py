"""Prepare a human-review worksheet of literal skill mentions in supplied CVs."""

from pydantic import Field
from qagents import tool
from qagents.models.testing import call

from ..runtime import Context, Record, encoded, require

DEFAULT = {
    "skills": ["Python", "PostgreSQL"],
    "resumes": {"C1": "Built Python services backed by PostgreSQL.", "C2": "Built Python reports."},
}


class Input(Record):
    skills: list[str] = Field(min_length=1, max_length=20)
    resumes: dict[str, str]


class Mention(Record):
    skill: str
    quote: str


class Candidate(Record):
    candidate_id: str
    mentions: list[Mention]
    unmentioned_skills: list[str]


class Answer(Record):
    candidates: list[Candidate]


def worksheet(data: Input) -> Answer:
    return Answer(
        candidates=[
            Candidate(
                candidate_id=k,
                mentions=[
                    Mention(skill=s, quote=text)
                    for s in data.skills
                    if s.casefold() in text.casefold()
                ],
                unmentioned_skills=[s for s in data.skills if s.casefold() not in text.casefold()],
            )
            for k, text in data.resumes.items()
        ]
    )


def verify(answer: Answer, data: Input) -> None:
    require(len(answer.candidates) == len(data.resumes), "missing candidate worksheet")
    require(
        {c.candidate_id for c in answer.candidates} == set(data.resumes), "candidate IDs mismatch"
    )
    for candidate in answer.candidates:
        text = data.resumes[candidate.candidate_id]
        expected = {s for s in data.skills if s.casefold() in text.casefold()}
        require(len(candidate.mentions) == len(expected), "missing or duplicated skill mention")
        require({m.skill for m in candidate.mentions} == expected, "skill mention mismatch")
        require(
            sorted(candidate.unmentioned_skills) == sorted(set(data.skills) - expected),
            "unmentioned skills mismatch",
        )
        for mention in candidate.mentions:
            require(bool(mention.quote) and mention.quote in text, "invented resume evidence")
            require(mention.skill.casefold() in mention.quote.casefold(), "quote lacks the skill")


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)

    @tool(read_only=True)
    def read_resumes() -> dict[str, str]:
        """Read CV text for the supplied anonymous candidate IDs."""
        return data.resumes

    agent = ctx.agent(
        "recruitment_reviewer",
        [call("read_resumes"), encoded(worksheet(data))],
        tools=[read_resumes],
        output_type=Answer,
        instructions="List literal case-insensitive mentions of required skills, with exact quotes "
        "and unmentioned skills, for every CV ID. A mention is not proof of proficiency. "
        "Produce a human-review worksheet; never rank people or make hiring decisions.",
    )
    answer = await ctx.execute(agent, encoded({"skills": data.skills}))
    verify(answer, data)
    ctx.artifact("candidate-evidence.json", answer)
    return answer.model_dump()
