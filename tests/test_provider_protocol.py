import json

import httpx
import pytest
import qagents
from qagents import OpenAIChatModel
from qagents.models.base import ModelCapabilities

from qagents_examples.cases import citation_research
from qagents_examples.cli import error_text
from qagents_examples.runtime import Context, encoded, openai_capabilities


async def test_native_openai_adapter_tool_cycle_with_local_transport(tmp_path):
    requests = []
    final = citation_research.Brief(
        title="Pilot evidence",
        claims=[
            citation_research.Claim(source=k, quote=v)
            for k, v in citation_research.DEFAULT["documents"].items()
        ],
    )

    def respond(request):
        body = json.loads(request.content)
        requests.append(body)
        assert request.headers["authorization"] == "Bearer mock-only"
        assert body["model"] == "protocol-fixture" and body["stream"] is True
        assert body["max_tokens"] == 4000
        if len(requests) == 1:
            assert any(t["function"]["name"] == "read_sources" for t in body["tools"])
            delta = {
                "tool_calls": [
                    {
                        "index": 0,
                        "id": "call-1",
                        "type": "function",
                        "function": {"name": "read_sources", "arguments": "{}"},
                    }
                ]
            }
            reason = "tool_calls"
        else:
            assert body["messages"][-1]["role"] == "tool"
            assert "40 learners" in body["messages"][-1]["content"]
            delta = {"content": encoded(final)}
            reason = "stop"
        chunk = {
            "id": "response-1",
            "model": "protocol-fixture",
            "choices": [{"index": 0, "delta": delta, "finish_reason": reason}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        }
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text="data: " + json.dumps(chunk) + "\n\ndata: [DONE]\n\n",
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        ctx = Context(
            tmp_path,
            provider="openai",
            model_factory=lambda name, replies: OpenAIChatModel(
                "protocol-fixture",
                base_url="https://provider.invalid/v1",
                api_key="mock-only",
                http_client=client,
                max_retries=0,
                capabilities=ModelCapabilities(
                    input_price_per_million=1, output_price_per_million=2
                ),
            ),
        )
        try:
            assert await citation_research.run(ctx)
            assert len(requests) == 2
            usage = ctx.summary("citation_research", {})["usage"]
            assert usage["requests"] == 2 and usage["input_tokens"] == 200
        finally:
            await ctx.close()


def test_credentials_are_redacted_from_validation_errors(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "mock-secret-value-123")
    assert "mock-secret-value-123" not in error_text(ValueError("bad mock-secret-value-123"))
    assert error_text(RuntimeError("mock-secret-value-123")) == "RuntimeError"


@pytest.mark.parametrize("value", ["inf", "nan", "-1"])
def test_unknown_or_invalid_prices_cannot_disable_the_cost_guard(monkeypatch, value):
    monkeypatch.setenv("QAGENTS_INPUT_USD_PER_MILLION", value)
    monkeypatch.setenv("QAGENTS_OUTPUT_USD_PER_MILLION", "1")
    with pytest.raises(ValueError, match="finite and nonnegative"):
        openai_capabilities()


def test_explicit_free_local_model_pricing_is_supported(monkeypatch):
    monkeypatch.setenv("QAGENTS_INPUT_USD_PER_MILLION", "0")
    monkeypatch.setenv("QAGENTS_OUTPUT_USD_PER_MILLION", "0")
    assert openai_capabilities().input_price_per_million == 0


async def test_configured_openai_factory_retains_explicit_prices_and_token_field(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("QAGENTS_INPUT_USD_PER_MILLION", "1.5")
    monkeypatch.setenv("QAGENTS_OUTPUT_USD_PER_MILLION", "4.5")
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MAX_TOKENS_PARAM", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "mock-only")
    payloads = []

    def respond(request):
        payloads.append(json.loads(request.content))
        chunk = {
            "id": "configuration-response",
            "model": "selected-by-user",
            "choices": [{"index": 0, "delta": {"content": "ready"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 1, "total_tokens": 11},
        }
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text="data: " + json.dumps(chunk) + "\n\ndata: [DONE]\n\n",
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        original = OpenAIChatModel
        monkeypatch.setattr(
            qagents,
            "OpenAIChatModel",
            lambda *args, **kwargs: original(*args, http_client=client, **kwargs),
        )
        ctx = Context(tmp_path, provider="openai", model_id="selected-by-user")
        try:
            agent = ctx.agent("configuration", [])
            assert await ctx.execute(agent, "Respond ready.") == "ready"
            capabilities = await ctx.models[0].capabilities()
            assert capabilities.input_price_per_million == 1.5
            assert capabilities.output_price_per_million == 4.5
            assert payloads[0]["max_completion_tokens"] == 4000
            assert "max_tokens" not in payloads[0]
        finally:
            await ctx.close()
