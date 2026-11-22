"""Retain only textual results from a completed offline collection, with source hashes."""

import argparse
import hashlib
import json
from pathlib import Path

from qagents_examples.catalog import CATALOG


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collection", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    index = json.loads((args.collection / "index.json").read_text(encoding="utf-8"))
    assert index["verified"] and {r["example"] for r in index["reports"]} == set(CATALOG)
    target = root / "samples/outputs"
    target.mkdir(parents=True, exist_ok=True)
    retained = {}
    for path in args.collection.rglob("*"):
        if not path.is_file() or path.suffix not in {".json", ".md"}:
            continue
        relative = path.relative_to(args.collection)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        text = path.read_text(encoding="utf-8")
        destination.write_text(text, encoding="utf-8", newline="\n")
        retained[relative.as_posix()] = hashlib.sha256(destination.read_bytes()).hexdigest()
    sources = {
        p.relative_to(root).as_posix(): hashlib.sha256(
            p.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        for p in sorted((root / "src").rglob("*.py"))
    }
    manifest = {
        "examples": len(CATALOG),
        "provider": "offline",
        "model_requests": sum(r["usage"]["requests"] for r in index["reports"]),
        "qagents_revision": (root / "QAGENTS_REVISION").read_text().strip(),
        "source_hash_encoding": "SHA-256, source CRLF normalized to LF",
        "source_sha256": sources,
        "output_sha256": retained,
    }
    (root / "research/sample-provenance.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Recorded {len(retained)} textual results from {len(CATALOG)} examples.")


if __name__ == "__main__":
    main()
