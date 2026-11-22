"""Journal company-analysis steps, reopen the worker store and replay without model calls."""

import hashlib

from pydantic import Field
from qagents import Agent, Limits, SQLiteStore, Workflow, tool
from qagents.models.testing import ScriptedModel, call

from ..runtime import Context, Record, encoded, require

DEFAULT = {
    "company": "Fictional Helios Labs",
    "source_id": "statement-demo-v1",
    "revenue_cents": 1250000,
    "prior_revenue_cents": 1000000,
    "operating_cost_cents": 1000000,
    "risk_notes": [
        "A single supplier provides 60% of parts.",
        "The pilot contract expires in six months.",
    ],
}


class Input(Record):
    company: str
    source_id: str
    revenue_cents: int = Field(gt=0, strict=True)
    prior_revenue_cents: int = Field(gt=0, strict=True)
    operating_cost_cents: int = Field(ge=0, strict=True)
    risk_notes: list[str] = Field(max_length=20)


class Metrics(Record):
    source_id: str
    revenue_growth_bps: int
    operating_margin_bps: int


class Risks(Record):
    quotes: list[str]


class Memo(Record):
    company: str
    metrics: Metrics
    risks: list[str]


def metrics(data: Input) -> Metrics:
    return Metrics(
        source_id=data.source_id,
        revenue_growth_bps=(data.revenue_cents - data.prior_revenue_cents)
        * 10000
        // data.prior_revenue_cents,
        operating_margin_bps=(data.revenue_cents - data.operating_cost_cents)
        * 10000
        // data.revenue_cents,
    )


def verify(answer: Memo, data: Input) -> None:
    require(
        answer.company == data.company and answer.metrics == metrics(data),
        "company arithmetic mismatch",
    )
    require(sorted(answer.risks) == sorted(data.risk_notes), "company risk evidence changed")


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)
    database = ctx.directory / "analysis.sqlite3"
    workflow_id = "company:" + hashlib.sha256(encoded(data).encode()).hexdigest()

    @tool(read_only=True)
    def read_statement() -> dict:
        """Read supplied fictional company statement values in integer cents."""
        return data.model_dump(exclude={"risk_notes"})

    analyst = ctx.agent(
        "company_metrics",
        [call("read_statement"), encoded(metrics(data))],
        tools=[read_statement],
        output_type=Metrics,
        instructions="Read the statement. Compute growth=(revenue-prior)*10000//prior "
        "and operating margin=(revenue-cost)*10000//revenue in "
        "integer basis points. Preserve source_id.",
    )
    risk_reader = ctx.agent(
        "company_risks",
        [encoded(Risks(quotes=data.risk_notes))],
        output_type=Risks,
        instructions="Return all supplied risk notes verbatim as "
        "quotes. Do not infer investment advice.",
    )
    golden = Memo(company=data.company, metrics=metrics(data), risks=data.risk_notes)
    writer = ctx.agent(
        "company_writer",
        [encoded(golden)],
        output_type=Memo,
        instructions="Combine the supplied company name, metrics "
        "and exact risk quotes into a memo.",
    )
    async with SQLiteStore(database) as store:
        first = await Workflow(store, id=workflow_id).run_agent(
            "metrics", analyst, "Analyze the statement."
        )
        ctx.accept(first)

    async with SQLiteStore(database) as store:
        workflow = Workflow(store, id=workflow_id)
        resumed = await workflow.run_agent("metrics", analyst, "Analyze the statement.")
        require(
            resumed.status == "completed" and resumed.run_id == first.run_id,
            "completed metrics step was not restored",
        )
        risks = ctx.accept(await workflow.run_agent("risks", risk_reader, encoded(data.risk_notes)))
        memo = ctx.accept(
            await workflow.run_agent(
                "memo",
                writer,
                encoded(
                    {
                        "company": data.company,
                        "metrics": resumed.output.model_dump(),
                        "risks": risks.quotes,
                    }
                ),
            )
        )
    verify(memo, data)

    async with SQLiteStore(database) as store:
        workflow = Workflow(store, id=workflow_id)
        for step, name, schema in [
            ("metrics", "company_metrics", Metrics),
            ("risks", "company_risks", Risks),
            ("memo", "company_writer", Memo),
        ]:
            guard = Agent(
                ScriptedModel([AssertionError("replay must not infer")]),
                name=name,
                output_type=schema,
                limits=Limits(max_turns=1, timeout_s=5),
            )
            replay = await workflow.run_agent(step, guard, "This prompt must not run.")
            require(replay.status == "completed", "workflow replay failed")
        require(
            set(await workflow.completed_steps()) == {"metrics", "risks", "memo"},
            "workflow journal is incomplete",
        )
    ctx.artifact("company-memo.json", memo)
    return {
        **memo.model_dump(),
        "worker_store_reopened": True,
        "replay_model_calls": 0,
        "scope": "fictional statement analysis; no investment recommendation",
    }
