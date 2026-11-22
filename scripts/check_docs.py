"""Check local Markdown links and source/sample provenance without network access."""

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = [*root.glob("*.md"), *(root / "docs").rglob("*.md"), *(root / "samples").rglob("*.md")]
    checked = 0
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for reference in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            url = urlsplit(reference)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.exists():
                raise ValueError(f"Broken link in {path.relative_to(root)}: {reference}")
            if url.fragment and target.suffix == ".md":
                headings = re.findall(r"(?m)^#{1,6}\s+(.+)$", target.read_text(encoding="utf-8"))
                slugs = {re.sub(r"[^\w\s-]", "", h.lower()).replace(" ", "-") for h in headings}
                if unquote(url.fragment) not in slugs:
                    raise ValueError(f"Broken heading link: {reference}")
            checked += 1
    provenance = json.loads((root / "research/sample-provenance.json").read_text())
    for relative, digest in provenance["source_sha256"].items():
        actual = hashlib.sha256((root / relative).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        if actual != digest:
            raise ValueError(f"Sample source changed: {relative}")
    for relative, digest in provenance["output_sha256"].items():
        actual = hashlib.sha256((root / "samples/outputs" / relative).read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f"Sample output changed: {relative}")
    print(f"Checked {checked} local links in {len(paths)} Markdown files and all sample hashes.")


if __name__ == "__main__":
    main()
