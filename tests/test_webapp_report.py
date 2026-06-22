from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_summarize_and_markdown():
    js = (ROOT / "src/webapp/report.js").read_text(encoding="utf-8")
    assert "summarize" in js and "toMarkdown" in js
