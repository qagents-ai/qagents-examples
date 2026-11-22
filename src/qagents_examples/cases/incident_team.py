"""Coordinate triage and review through separately opened persistent TeamMailbox instances."""

import asyncio
import json

from pydantic import Field
from qagents import RunContext, TeamMailbox, tool
from qagents.models.testing import call

from ..runtime import Context, Record, encoded, require

DEFAULT = {"incident_id": "INC-42", "service": "demo-api", "p95_ms": 1200, "budget_ms": 500}
MEMBERS = ["coordinator", "triager", "reviewer"]


class Input(Record):
    incident_id: str
    service: str
    p95_ms: int = Field(ge=0, strict=True)
    budget_ms: int = Field(gt=0, strict=True)


class Answer(Record):
    incident_id: str
    service: str
    latency_budget_exceeded: bool


def received(result) -> list[dict]:
    return [
        item
        for message in result.new_messages
        for part in message.tool_results
        if part.name == "receive_messages"
        for item in json.loads(part.content)
    ]


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)
    database = ctx.directory / "team.sqlite3"
    lead_box = TeamMailbox(MEMBERS, db_path=database)
    kickoff = {"incident_id": data.incident_id, "service": data.service}
    diagnostic = data.model_dump()
    golden = Answer(
        incident_id=data.incident_id,
        service=data.service,
        latency_budget_exceeded=data.p95_ms > data.budget_ms,
    )
    children = {}

    @tool(read_only=True)
    def read_service_metrics() -> dict:
        """Read supplied service telemetry; no production system is contacted."""
        return diagnostic

    @tool
    async def coordinate(parent: RunContext) -> str:
        """Start triage and review workers against freshly opened durable inboxes."""
        triage_box = TeamMailbox(MEMBERS, db_path=database)
        review_box = TeamMailbox(MEMBERS, db_path=database)
        triager = ctx.agent(
            "triager",
            [
                call("receive_messages", wait_s=2),
                call("read_service_metrics"),
                call("send_message", recipient="reviewer", text=encoded(diagnostic)),
                "Sent.",
            ],
            tools=[*triage_box.endpoint("triager").tools(), read_service_metrics],
            instructions="Receive the coordinator's incident, read its metrics, then send the "
            "metrics JSON unchanged to reviewer. Finish after sending.",
        )
        reviewer = ctx.agent(
            "reviewer",
            [
                call("receive_messages", wait_s=2),
                call("send_message", recipient="coordinator", text=encoded(golden)),
                "Reviewed.",
            ],
            tools=review_box.endpoint("reviewer").tools(),
            instructions="Receive triager's JSON. Send coordinator JSON with incident_id, service "
            "and latency_budget_exceeded=(p95_ms>budget_ms). Do not change any service.",
        )
        async with asyncio.TaskGroup() as group:
            triage = group.create_task(
                triager.run("Triage the incident in your inbox.", parent=parent)
            )
            review = group.create_task(
                reviewer.run("Review the diagnostic evidence.", parent=parent)
            )
        children.update(triager=triage.result(), reviewer=review.result())
        require(all(r.status == "completed" for r in children.values()), "incident worker stopped")
        return "Triage and peer review completed. Read the coordinator inbox for the result."

    leader = ctx.agent(
        "coordinator",
        [
            call("send_message", recipient="triager", text=encoded(kickoff)),
            call("coordinate"),
            call("receive_messages"),
            encoded(golden),
        ],
        tools=[*lead_box.endpoint("coordinator").tools(), coordinate],
        output_type=Answer,
        instructions="Send incident_id/service JSON to triager, run coordinate, receive reviewer "
        "messages and return the reviewed JSON. No service restart is available.",
    )
    answer = await ctx.execute(leader, encoded(kickoff))
    require(answer == golden, "incident summary contradicts telemetry")
    for result, sender, recipient, payload in [
        (children["triager"], "coordinator", "triager", kickoff),
        (children["reviewer"], "triager", "reviewer", diagnostic),
        (ctx.results[-1], "reviewer", "coordinator", golden.model_dump()),
    ]:
        messages = received(result)
        require(len(messages) == 1, "incident message missing or duplicated")
        require(
            messages[0]["sender"] == sender and messages[0]["recipient"] == recipient,
            "incident sender or recipient mismatch",
        )
        require(json.loads(messages[0]["text"]) == payload, "incident message payload changed")
    ctx.artifact("incident-review.json", answer)
    return {**answer.model_dump(), "verified_routes": 3, "persistent_mailbox": True}
