from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_reconcile_defined():
    js = (ROOT / "src/webapp/engine.js").read_text(encoding="utf-8")
    assert "reconcile" in js and "unmatchedRight" in js
