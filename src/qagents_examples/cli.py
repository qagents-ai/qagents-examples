"""List applications, run one with a model, or replay the complete offline collection."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import stat
import sys
import uuid
from pathlib import Path

from .catalog import CATALOG, load
from .runtime import Context, encoded, openai_capabilities


def reserve(path: Path) -> Path:
    for parent in (path, *path.parents):
        if parent.exists():
            attrs = parent.lstat()
            if parent.is_symlink() or getattr(attrs, "st_file_attributes", 0) & getattr(
                stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0
            ):
                raise ValueError("output must not traverse symlinks or junctions")
    path.mkdir(parents=True, exist_ok=False)
    return path.resolve()


def read_input(path: Path) -> dict:
    if path.stat().st_size > 100000:
        raise ValueError("input JSON exceeds 100,000 bytes")

    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate input JSON key")
            value[key] = item
        return value

    def nonfinite(value):
        raise ValueError(f"non-finite input JSON number: {value}")

    value = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=unique, parse_constant=nonfinite
    )
    if not isinstance(value, dict):
        raise ValueError("example input must be a JSON object")
    return value


def error_text(error: Exception) -> str:
    # Provider errors can quote request details. Keep only their class in CLI output.
    if not isinstance(error, (ValueError, FileExistsError)):
        return type(error).__name__
    text = str(error)
    for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "QCLOUD_API_KEY"):
        value = os.environ.get(key)
        if value:
            text = text.replace(value, "[redacted]")
    return f"{type(error).__name__}: {text[:500]}"


async def run_one(
    name: str, directory: Path, *, provider="offline", model=None, approval="approve", raw=None
) -> dict:
    ctx = Context(directory, provider=provider, model_id=model, approval=approval)
    try:
        outcome = await load(name).run(ctx, raw)
        report = ctx.summary(name, outcome)
        ctx.artifact("report.json", report)
        return report
    except Exception as error:
        ctx.artifact(
            "failure.json", {"example": name, "verified": False, "error": error_text(error)}
        )
        raise
    finally:
        await ctx.close()


async def dispatch(args) -> dict:
    if args.command == "run":
        raw = read_input(args.input) if args.input else None
        if args.provider != "offline" and not args.model:
            raise ValueError("configured providers require --model")
        if args.provider == "openai":
            openai_capabilities()
        directory = reserve(
            args.output or Path(".runs") / (args.example + "-" + uuid.uuid4().hex[:8])
        )
        report = await run_one(
            args.example,
            directory,
            provider=args.provider,
            model=args.model,
            approval=args.approval or ("approve" if args.provider == "offline" else "prompt"),
            raw=raw,
        )
        return {"output_directory": str(directory), **report}
    directory = reserve(args.output or Path(".runs") / ("all-" + uuid.uuid4().hex[:8]))
    reports = []
    for name in CATALOG:
        reports.append(await run_one(name, reserve(directory / name)))
    summary = {
        "examples": len(reports),
        "verified": all(r["verified"] for r in reports),
        "provider": "offline",
        "reports": reports,
    }
    with (directory / "index.json").open("x", encoding="utf-8") as handle:
        handle.write(encoded(summary) + "\n")
    return {"output_directory": str(directory), **summary}


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List all implemented applications")
    run = commands.add_parser("run", help="Run one application and its verifier")
    run.add_argument("example", choices=CATALOG)
    run.add_argument(
        "--provider", choices=["offline", "openai", "anthropic", "qcloud"], default="offline"
    )
    run.add_argument("--model")
    run.add_argument("--approval", choices=["approve", "decline", "prompt"])
    run.add_argument("--input", type=Path)
    run.add_argument("--output", type=Path)
    all_examples = commands.add_parser("run-all", help="Run all applications with offline fixtures")
    all_examples.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.command == "list":
        print(json.dumps(CATALOG, indent=2))
        return 0
    try:
        report = asyncio.run(dispatch(args))
    except Exception as error:
        print(error_text(error), file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
