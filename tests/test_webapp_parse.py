from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_parse_defined():
    js = (ROOT / "src/webapp/parse.js").read_text(encoding="utf-8")
    assert "parseCsv" in js
