from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def test_index_has_inputs_and_buttons():
    html = _read("src/webapp/index.html")
    assert 'id="source-a"' in html and 'id="source-b"' in html
    assert 'id="reconcile"' in html


def test_styles_present():
    assert ".btn-primary" in _read("src/webapp/styles.css")
