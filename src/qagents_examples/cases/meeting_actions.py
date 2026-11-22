"""Extract explicit meeting commitments with owners, ISO dates and exact transcript evidence."""

import re
from datetime import date

from pydantic import Field

from ..runtime import Context, Record, encoded, require

DEFAULT = {
    "transcript": "Maria: I will prepare the agenda by 2026-12-01.\n"
    "Nikos: I will review the budget by 2026-12-03.\nMaria: We should meet again.",
    "participants": ["Maria", "Nikos"],
}
COMMITMENT = re.compile(r"^([^:\n]+): I will (.+?) by (\d{4}-\d{2}-\d{2})\.$", re.MULTILINE)


class Input(Record):
    transcript: str
    participants: list[str] = Field(min_length=1, max_length=30)


class Action(Record):
    owner: str
    task: str
    due: str
    quote: str


class Answer(Record):
    actions: list[Action] = Field(min_length=1, max_length=30)


def commitments(data: Input) -> list[Action]:
    return [
        Action(owner=m[1], task=m[2], due=m[3], quote=m[0])
        for m in COMMITMENT.finditer(data.transcript)
    ]


def verify(answer: Answer, data: Input) -> None:
    expected = commitments(data)
    require(bool(expected), "no explicit supported commitment found")
    for action in answer.actions:
        require(action.owner in data.participants, "unknown meeting owner")
        require(action.quote in data.transcript, "invented meeting quote")
        date.fromisoformat(action.due)
    observed = sorted((a.owner, a.task, a.due, a.quote) for a in answer.actions)
    required = sorted((a.owner, a.task, a.due, a.quote) for a in expected)
    require(observed == required, "meeting commitments are missing, changed or duplicated")


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)
    golden = Answer(actions=commitments(data))
    agent = ctx.agent(
        "meeting_secretary",
        [encoded(golden)],
        output_type=Answer,
        instructions="Extract explicit 'Name: I will TASK by YYYY-MM-DD.' commitments. "
        "Return owner, task (without 'I will' or due clause), ISO due and exact full quote. "
        "Ignore speculative discussion. Do not create tasks in external services.",
    )
    answer = await ctx.execute(agent, encoded(data))
    verify(answer, data)
    ctx.artifact("meeting-actions.json", answer)
    return answer.model_dump()
