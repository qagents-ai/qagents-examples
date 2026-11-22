import pytest

from qagents_examples.cases import content_team, scoped_preferences
from qagents_examples.runtime import Context


async def test_nested_editorial_agents_share_parent_usage(tmp_path):
    ctx = Context(tmp_path)
    try:
        answer = await content_team.run(ctx)
        assert len(answer["team"]) == len(ctx.models) == 3
        assert ctx.summary("content_team", answer)["usage"]["requests"] == 6
        assert (tmp_path / "article.md").read_text().count("[") == 2
    finally:
        await ctx.close()


@pytest.mark.parametrize("approval,expected", [("approve", {"language": "el"}), ("decline", {})])
async def test_persistent_scoped_preference_state(approval, expected, tmp_path):
    ctx = Context(tmp_path, approval=approval)
    try:
        answer = await scoped_preferences.run(ctx)
        assert answer["same_user"] == expected
        assert answer["other_user"] == answer["other_tenant"] == {}
        assert answer["reopened"]
    finally:
        await ctx.close()


def test_identity_encoding_has_no_delimiter_collision():
    assert scoped_preferences.scope("a:b", "c") != scoped_preferences.scope("a", "b:c")
