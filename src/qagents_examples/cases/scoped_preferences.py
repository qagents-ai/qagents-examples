"""Approve a preference, reopen SQLite, and recall only the application's tenant/user scope."""

import json

from pydantic import Field
from qagents import RunContext, Session, SQLiteStore, tool
from qagents.models.testing import call

from ..runtime import Context, Record, encoded, require

DEFAULT = {"tenant": "demo-org", "user": "alex", "preferences": {"language": "el"}}


class Input(Record):
    tenant: str = Field(min_length=1)
    user: str = Field(min_length=1)
    preferences: dict[str, str]


class Profile(Record):
    preferences: dict[str, str]


def scope(tenant: str, user: str) -> str:
    return "profile:" + json.dumps([tenant, user], ensure_ascii=True)


@tool(requires_approval=True, idempotent=True)
def remember_preferences(context: RunContext, preferences: dict[str, str]) -> dict:
    """Replace approved preferences in the host-selected session."""
    require(set(preferences) <= {"language", "timezone"}, "unsupported preference key")
    context.state["preferences"] = preferences.copy()
    return {"preferences": preferences}


@tool(read_only=True)
def read_preferences(context: RunContext) -> dict:
    """Read preferences from this session's scope, never from a model-selected user."""
    return {"preferences": dict(context.state.get("preferences", {}))}


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)
    require(set(data.preferences) <= {"language", "timezone"}, "unsupported preference key")
    database = ctx.directory / "profiles.sqlite3"
    writer = ctx.agent(
        "preference_writer",
        [
            call("remember_preferences", preferences=data.preferences),
            lambda request: encoded(
                Profile(
                    preferences=data.preferences
                    if any(d["approved"] for d in ctx.decisions)
                    else {}
                )
            ),
        ],
        tools=[remember_preferences],
        output_type=Profile,
        instructions="Request approval to store the supplied "
        "preferences. Return their actual state; "
        "if approval is declined return an empty preferences object.",
    )
    async with SQLiteStore(database) as store:
        await ctx.execute(
            writer,
            encoded(data.preferences),
            session=Session(store, id=scope(data.tenant, data.user)),
        )

    async def recall(store, tenant, user):
        reader = ctx.agent(
            "preference_reader",
            [
                call("read_preferences"),
                lambda request: request.messages[-1].tool_results[0].content,
            ],
            tools=[read_preferences],
            output_type=Profile,
            instructions="Call read_preferences and return its JSON object exactly.",
        )
        answer = await ctx.execute(
            reader, "Read my saved preferences.", session=Session(store, id=scope(tenant, user))
        )
        return answer.preferences

    async with SQLiteStore(database) as store:
        same = await recall(store, data.tenant, data.user)
        other_user = await recall(store, data.tenant, data.user + "-other")
        other_tenant = await recall(store, data.tenant + "-other", data.user)
    expected = data.preferences if any(d["approved"] for d in ctx.decisions) else {}
    require(bool(ctx.decisions), "preference approval was skipped")
    require(same == expected, "preferences did not survive reopen")
    require(other_user == other_tenant == {}, "preferences leaked across identity scopes")
    outcome = {
        "same_user": same,
        "other_user": other_user,
        "other_tenant": other_tenant,
        "reopened": True,
    }
    ctx.artifact("preference-recall.json", outcome)
    return outcome
