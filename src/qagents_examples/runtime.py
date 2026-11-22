"""Small shared execution helpers; use-case tools and verification live in each example."""

from __future__ import annotations

import asyncio
import json
import math
import os
import sqlite3
import sys
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict
from qagents import Agent, Approval, Limits, ModelSettings, RunResult, Session, Usage
from qagents.models.base import Model, ModelCapabilities
from qagents.models.testing import ScriptedModel


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, str_max_length=20000)


class VerificationError(ValueError):
    """The application verifier rejected a model result."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def encoded(value: Any) -> str:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def openai_capabilities() -> ModelCapabilities:
    keys = ("QAGENTS_INPUT_USD_PER_MILLION", "QAGENTS_OUTPUT_USD_PER_MILLION")
    values = [os.environ.get(key) for key in keys]
    if any(value is None for value in values):
        raise ValueError(
            "Set QAGENTS_INPUT_USD_PER_MILLION and QAGENTS_OUTPUT_USD_PER_MILLION "
            "to your model's prices; explicit 0 is allowed for a free local endpoint."
        )
    prices = [float(value) for value in values]
    if any(not math.isfinite(value) or value < 0 for value in prices):
        raise ValueError("model prices must be finite and nonnegative")
    return ModelCapabilities(input_price_per_million=prices[0], output_price_per_million=prices[1])


class Outbox:
    """A local destination with atomic, payload-bound idempotency keys."""

    def __init__(self, path: Path):
        self.path = path
        with closing(sqlite3.connect(path)) as connection, connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS actions (id INTEGER PRIMARY KEY, "
                "operation_id TEXT UNIQUE NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL)"
            )

    def put(self, operation_id: str, kind: str, payload: dict) -> dict:
        if not operation_id:
            raise ValueError("a journaled operation_id is required")
        text = encoded(payload)
        with closing(sqlite3.connect(self.path, timeout=5)) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            old = connection.execute(
                "SELECT id, kind, payload FROM actions WHERE operation_id=?", (operation_id,)
            ).fetchone()
            if old:
                if old[1:] != (kind, text):
                    raise ValueError("idempotency key was already bound to another payload")
                return {"id": old[0], "kind": kind, "payload": payload}
            cursor = connection.execute(
                "INSERT INTO actions(operation_id,kind,payload) VALUES(?,?,?)",
                (operation_id, kind, text),
            )
            return {"id": cursor.lastrowid, "kind": kind, "payload": payload}

    def rows(self) -> list[dict]:
        with closing(sqlite3.connect(self.path)) as connection:
            return [
                {"id": row[0], "kind": row[1], "payload": json.loads(row[2])}
                for row in connection.execute("SELECT id,kind,payload FROM actions ORDER BY id")
            ]


@dataclass
class Context:
    directory: Path
    provider: str = "offline"
    model_id: str | None = None
    approval: Literal["approve", "decline", "prompt"] = "approve"
    models: list[Model] = field(default_factory=list, repr=False)
    results: list[RunResult] = field(default_factory=list, repr=False)
    decisions: list[dict] = field(default_factory=list)
    model_factory: Any = field(default=None, repr=False)

    def model(self, name: str, replies: list) -> Model:
        if self.model_factory is not None:
            model = self.model_factory(name, replies)
        elif self.provider == "offline":
            model = ScriptedModel(replies, name=name)
        elif self.provider == "openai":
            from qagents import OpenAIChatModel

            base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            parameter = os.environ.get("OPENAI_MAX_TOKENS_PARAM") or (
                "max_completion_tokens"
                if urlsplit(base_url).hostname == "api.openai.com"
                else "max_tokens"
            )
            if parameter not in ("max_tokens", "max_completion_tokens"):
                raise ValueError("OPENAI_MAX_TOKENS_PARAM must name a supported token limit field")
            model = OpenAIChatModel(
                self._model_id(),
                base_url=base_url,
                api_key=os.environ.get("OPENAI_API_KEY"),
                timeout=60,
                max_retries=0,
                capabilities=openai_capabilities(),
                max_tokens_param=parameter,
            )
        elif self.provider == "anthropic":
            from qagents import AnthropicModel

            model = AnthropicModel(self._model_id(), timeout=60, max_retries=0, max_tokens=2000)
        elif self.provider == "qcloud":
            from qagents import QCloudModel

            model = QCloudModel(self._model_id(), timeout=60, max_retries=0)
        else:
            raise ValueError("unknown provider")
        self.models.append(model)
        return model

    def _model_id(self) -> str:
        if not self.model_id:
            raise ValueError("a configured provider requires --model")
        return self.model_id

    def agent(self, name: str, replies: list, **options: Any) -> Agent:
        return Agent(
            self.model(name, replies),
            name=name,
            limits=Limits(
                max_turns=12,
                max_total_tokens=16000,
                max_cost_usd=0.50,
                max_tool_calls=16,
                timeout_s=90,
                tool_timeout_s=10,
                max_depth=4,
            ),
            output_mode="prompted",
            settings=ModelSettings(max_tokens=4000),
            **options,
        )

    async def execute(self, agent: Agent, prompt: str, *, session=None, deps=None) -> Any:
        session = session or Session()
        result = await agent.run(prompt, session=session, deps=deps)
        pauses = 0
        while result.status == "paused" and result.pending_approvals:
            pauses += 1
            require(pauses <= 8, "too many approval pauses")
            decisions = {}
            for pending in result.pending_approvals:
                approved = self.approval == "approve"
                if self.approval == "prompt":
                    print(
                        f"Approve {pending.name} {encoded(pending.arguments)}? [y/N]",
                        file=sys.stderr,
                    )
                    approved = (await asyncio.to_thread(input)).strip().lower() == "y"
                self.decisions.append({"tool": pending.name, "approved": approved})
                decisions[pending.tool_call_id] = Approval.for_call(
                    pending, approved, by="example operator"
                )
            result = await agent.resume(session, approvals=decisions, deps=deps)
        return self.accept(result)

    def accept(self, result: RunResult) -> Any:
        self.results.append(result)
        require(
            result.status == "completed", f"agent stopped: {result.status}/{result.stop_reason}"
        )
        require(result.output is not None, "agent returned no output")
        return result.output

    def artifact(self, name: str, value: Any) -> str:
        if Path(name).name != name or name in (".", ".."):
            raise ValueError("artifact name must be one filename")
        text = value if isinstance(value, str) else encoded(value) + "\n"
        with (self.directory / name).open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        return name

    def summary(self, example: str, outcome: Any) -> dict:
        usage = Usage()
        for result in self.results:
            usage = usage.add(result.usage)
        return {
            "example": example,
            "provider": self.provider,
            "verified": True,
            "outcome": outcome,
            "usage": usage.model_dump(mode="json"),
            "verification_scope": "application checks; offline replies are scripted fixtures"
            if self.provider == "offline"
            else "application checks; review generated prose separately",
            "approvals": self.decisions,
            "artifacts": sorted(p.name for p in self.directory.iterdir() if p.is_file()),
        }

    async def close(self) -> None:
        for model in self.models:
            await model.aclose()
