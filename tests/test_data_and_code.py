import sqlite3
from contextlib import closing

import pytest

from qagents_examples.cases import code_security_review, document_qa, sql_analyst
from qagents_examples.runtime import Context


@pytest.mark.parametrize("module", [sql_analyst, document_qa, code_security_review])
async def test_native_data_tools_run(module, tmp_path):
    ctx = Context(tmp_path)
    try:
        assert await module.run(ctx)
        assert any(p.tool_results for r in ctx.results for p in r.new_messages)
    finally:
        await ctx.close()


@pytest.mark.parametrize(
    "query",
    [
        "DELETE FROM sales",
        "DROP TABLE sales",
        "PRAGMA user_version=7",
        "ATTACH DATABASE ':memory:' AS other",
        "SELECT * FROM sqlite_master",
        "SELECT load_extension('anything')",
        "SELECT * FROM sales; DELETE FROM sales",
    ],
)
def test_sql_model_queries_cannot_escape_read_boundary(query, tmp_path):
    database = tmp_path / "data.sqlite3"
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("CREATE TABLE sales(region TEXT,amount_cents INTEGER)")
        connection.execute("INSERT INTO sales VALUES('North',700)")
    with pytest.raises(sqlite3.Error):
        sql_analyst.read_query(database, query)
    assert sql_analyst.read_query(database, sql_analyst.QUERY) == [
        {"region": "North", "revenue_cents": 700}
    ]


async def test_document_agent_abstains_without_a_match(tmp_path):
    ctx = Context(tmp_path)
    try:
        assert await document_qa.run(ctx, {**document_qa.DEFAULT, "query": "warranty"}) == {
            "answer": None,
            "source_id": None,
        }
    finally:
        await ctx.close()


async def test_source_code_is_never_executed(tmp_path):
    marker = tmp_path / "must-not-exist.txt"
    source = f"from pathlib import Path\nPath({str(marker)!r}).write_text('unsafe')\n"
    ctx = Context(tmp_path)
    try:
        assert (await code_security_review.run(ctx, {"files": {"hostile.py": source}}))[
            "findings"
        ] == []
        assert not marker.exists()
    finally:
        await ctx.close()
