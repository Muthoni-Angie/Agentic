from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_app_wires_reconcile():
    js = (ROOT / "src/webapp/app.js").read_text(encoding="utf-8")
    assert "addEventListener" in js and "render" in js


def test_sample_data_present():
    js = (ROOT / "src/webapp/sample.js").read_text(encoding="utf-8")
    assert "SAMPLE_A" in js and "SAMPLE_B" in js
