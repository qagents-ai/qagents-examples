"""Check every application module against the installed QAgents API."""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    checked = 0
    files = [*(root / "src").rglob("*.py"), *(root / "tests").rglob("*.py")]
    for path in sorted(files):
        if "qagents" not in path.read_text(encoding="utf-8"):
            continue
        result = subprocess.run(
            [sys.executable, "-m", "qagents.docs_mcp", "check", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            raise SystemExit(result.returncode)
        checked += 1
    print(f"QAgents API checker passed for {checked} application and test modules.")


if __name__ == "__main__":
    main()
