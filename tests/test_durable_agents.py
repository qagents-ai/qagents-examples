import asyncio
import json
import subprocess
import sys

import pytest
from qagents import TeamMailbox

from qagents_examples.cases import company_analysis, incident_team
from qagents_examples.runtime import Context


@pytest.mark.parametrize("module", [incident_team, company_analysis])
async def test_real_durable_agent_examples(module, tmp_path):
    ctx = Context(tmp_path)
    try:
        answer = await module.run(ctx)
        assert answer and ctx.results
        if module is incident_team:
            assert answer["verified_routes"] == 3
        else:
            assert answer["replay_model_calls"] == 0
            assert answer["metrics"]["revenue_growth_bps"] == 2500
            assert sum(len(m.requests) for m in ctx.models) == 4
    finally:
        await ctx.close()


def test_team_message_survives_a_new_python_process(tmp_path):
    database = tmp_path / "mail.sqlite3"
    box = TeamMailbox(["coordinator", "worker"], db_path=database)
    asyncio.run(box.endpoint("coordinator").send("worker", "diagnostic-evidence"))
    code = (
        "import asyncio,json,sys; from dataclasses import asdict; from qagents import TeamMailbox; "
        "b=TeamMailbox(['coordinator','worker'],db_path=sys.argv[1]); "
        "r=asyncio.run(b.endpoint('worker').receive()); print(json.dumps([asdict(x) for x in r]))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code, str(database)],
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
    )
    rows = json.loads(result.stdout)
    assert len(rows) == 1 and rows[0]["sender"] == "coordinator"
    assert rows[0]["text"] == "diagnostic-evidence"
    reopened = TeamMailbox(["coordinator", "worker"], db_path=database)
    assert asyncio.run(reopened.endpoint("worker").receive()) == []
