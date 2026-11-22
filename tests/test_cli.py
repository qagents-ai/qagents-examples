import json
import subprocess
import sys

import pytest

from qagents_examples.catalog import CATALOG
from qagents_examples.cli import main, read_input, reserve


def test_catalog_and_list_command(capsys):
    assert main(["list"]) == 0
    assert set(json.loads(capsys.readouterr().out)) == set(CATALOG)
    assert len(CATALOG) == 18


def test_complete_cli_collection_executes_and_retains_artifacts(tmp_path):
    destination = tmp_path / "collection"
    result = subprocess.run(
        [sys.executable, "-m", "qagents_examples", "run-all", "--output", str(destination)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
        check=True,
    )
    report = json.loads(result.stdout)
    assert report["examples"] == 18 and report["verified"] is True
    index = json.loads((destination / "index.json").read_text(encoding="utf-8"))
    assert {r["example"] for r in index["reports"]} == set(CATALOG)
    assert all(r["usage"]["requests"] > 0 for r in index["reports"])
    for name in CATALOG:
        assert (destination / name / "report.json").is_file()
    original_index = (destination / "index.json").read_bytes()
    repeated = subprocess.run(
        [sys.executable, "-m", "qagents_examples", "run-all", "--output", str(destination)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    assert repeated.returncode == 1
    assert (destination / "index.json").read_bytes() == original_index


def test_alternate_input_and_decline_from_cli(tmp_path, capsys):
    source = tmp_path / "input.json"
    source.write_text('{"sku":"ALT-9","on_hand":2,"target":7,"unit_cents":300}')
    target = tmp_path / "run"
    assert (
        main(
            [
                "run",
                "inventory_order",
                "--input",
                str(source),
                "--output",
                str(target),
                "--approval",
                "decline",
            ]
        )
        == 0
    )
    report = json.loads(capsys.readouterr().out)
    assert report["outcome"]["quantity"] == 5 and not report["outcome"]["queued"]


@pytest.mark.parametrize("text", ['{"x":1,"x":2}', '{"x":NaN}', "[]"])
def test_invalid_input_json_fails(text, tmp_path):
    path = tmp_path / "input.json"
    path.write_text(text)
    with pytest.raises(ValueError):
        read_input(path)


def test_existing_output_is_never_reused(tmp_path):
    with pytest.raises(FileExistsError):
        reserve(tmp_path)


def test_live_model_must_be_selected_before_output_is_reserved(tmp_path, capsys):
    target = tmp_path / "not-created"
    assert main(["run", "invoice_audit", "--provider", "openai", "--output", str(target)]) == 1
    assert "--model" in capsys.readouterr().err and not target.exists()
