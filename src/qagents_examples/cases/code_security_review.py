"""Inspect supplied Python text without executing it; check a small explicit AST rule set."""

import ast
from typing import Literal

from pydantic import Field
from qagents import tool
from qagents.models.testing import call

from ..runtime import Context, Record, encoded, require

DEFAULT = {
    "files": {
        "calculator.py": "def calculate(text):\n    return eval(text)\n",
        "safe.py": "def total(values):\n    return sum(values)\n",
    }
}


class Input(Record):
    files: dict[str, str]


class Finding(Record):
    file: str
    line: int = Field(ge=1)
    rule: Literal["dynamic-eval", "dynamic-exec", "shell-command"]


class Answer(Record):
    findings: list[Finding]


def scan(data: Input) -> list[Finding]:
    findings = []
    for filename, text in data.files.items():
        for node in ast.walk(ast.parse(text, filename=filename)):
            if not isinstance(node, ast.Call):
                continue
            rule = None
            if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                rule = "dynamic-" + node.func.id
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                shell = any(
                    k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True
                    for k in node.keywords
                )
                if node.func.value.id == "subprocess" and node.func.attr == "run" and shell:
                    rule = "shell-command"
            if rule:
                findings.append(Finding(file=filename, line=node.lineno, rule=rule))
    return findings


def verify(answer: Answer, data: Input) -> None:
    def signature(findings):
        return sorted((f.file, f.line, f.rule) for f in findings)

    require(
        signature(answer.findings) == signature(scan(data)), "code review differs from AST evidence"
    )


async def run(ctx: Context, raw=None) -> dict:
    data = Input.model_validate(DEFAULT if raw is None else raw)

    @tool(read_only=True)
    def read_python_sources() -> dict[str, str]:
        """Read the supplied source strings. No host paths are opened and no code runs."""
        return data.files

    agent = ctx.agent(
        "code_reviewer",
        [call("read_python_sources"), encoded(Answer(findings=scan(data)))],
        tools=[read_python_sources],
        output_type=Answer,
        instructions="Inspect the Python text. Report direct eval/exec calls and literal "
        "subprocess.run(...,shell=True), using rules dynamic-eval, dynamic-exec, shell-command "
        "and one-based line numbers. Report only these rules. Do not execute source code.",
    )
    answer = await ctx.execute(agent, "Review the supplied source under the three explicit rules.")
    verify(answer, data)
    ctx.artifact("code-findings.json", answer)
    return {
        **answer.model_dump(),
        "scope": "three literal AST rules; not a complete security audit",
    }
