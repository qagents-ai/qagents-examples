"""Answer a revenue question using a bounded, read-only SQLite query tool."""

import sqlite3
from contextlib import closing
from pathlib import Path
from urllib.parse import quote

from pydantic import Field
from qagents import tool
from qagents.models.testing import call

from ..runtime import Context, Record, encoded, require

DEFAULT = {
    "sales": [
        {"region": "North", "amount_cents": 12000},
        {"region": "South", "amount_cents": 9000},
        {"region": "North", "amount_cents": 5000},
    ]
}
QUERY = (
    "SELECT region, SUM(amount_cents) AS revenue_cents FROM sales GROUP BY region ORDER BY region"
)


class Sale(Record):
    region: str
    amount_cents: int = Field(ge=0, strict=True)


class Input(Record):
    sales: list[Sale] = Field(min_length=1, max_length=200)


class Total(Record):
    region: str
    revenue_cents: int


class Answer(Record):
    totals: list[Total]


def read_query(database: Path, query: str) -> list[dict]:
    if len(query) > 4000:
        raise ValueError("query exceeds the size budget")
    uri = "file:" + quote(database.resolve().as_posix(), safe="/:") + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True, timeout=2)) as connection:

        def authorize(action, first, second, db_name, trigger):
            if action == sqlite3.SQLITE_SELECT:
                return sqlite3.SQLITE_OK
            if (
                action == sqlite3.SQLITE_READ
                and first == "sales"
                and second
                in {
                    "region",
                    "amount_cents",
                    "",
                }
            ):
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_FUNCTION and str(second).lower() in {
                "sum",
                "count",
                "avg",
                "min",
                "max",
                "round",
            }:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        remaining = 100

        def progress():
            nonlocal remaining
            remaining -= 1
            return int(remaining <= 0)

        connection.set_authorizer(authorize)
        connection.set_progress_handler(progress, 1000)
        cursor = connection.execute(query)
        rows = cursor.fetchmany(101)
        require(len(rows) <= 100, "query exceeds the row budget")
        names = [column[0] for column in cursor.description]
        require(len(names) == len(set(names)), "query has ambiguous column names")
        return [dict(zip(names, row, strict=True)) for row in rows]


def verify(answer: Answer, data: Input) -> None:
    expected = {}
    for sale in data.sales:
        expected[sale.region] = expected.get(sale.region, 0) + sale.amount_cents
    require(len(answer.totals) == len(expected), "missing or duplicate revenue regions")
    require(
        {x.region: x.revenue_cents for x in answer.totals} == expected, "revenue totals mismatch"
    )


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)
    database = ctx.directory / "sales.sqlite3"
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute(
            "CREATE TABLE sales(region TEXT NOT NULL, amount_cents INTEGER NOT NULL)"
        )
        connection.executemany(
            "INSERT INTO sales VALUES (?,?)", [(x.region, x.amount_cents) for x in data.sales]
        )

    @tool(read_only=True)
    def query_sales(query: str) -> list[dict]:
        """Read sales with bounded SELECT queries; deny writes and other tables."""
        return read_query(database, query)

    golden = Answer(totals=[Total(**row) for row in read_query(database, QUERY)])
    agent = ctx.agent(
        "sql_analyst",
        [call("query_sales", query=QUERY), encoded(golden)],
        tools=[query_sales],
        output_type=Answer,
        instructions="Use the SQLite tool to sum amount_cents by region. "
        "Return every region as {region,revenue_cents}. "
        "Only sales(region,amount_cents) is available.",
    )
    answer = await ctx.execute(agent, "What is total revenue in cents for each region?")
    verify(answer, data)
    ctx.artifact("revenue-analysis.json", answer)
    return answer.model_dump()
