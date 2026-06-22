"""The product backlog — an ordered list of real features the agents build.

This is the "pre-authored intelligence" that replaces an LLM: each feature is a
concrete, working slice of the product (source + tests). The Planner picks the
next undone feature every run; the Coder writes its source; the Tester writes
its tests. Over successive runs the `ledgerloop` package grows for real.

Each module uses package-relative imports and is imported in tests as
``src.ledgerloop.<module>`` (pytest runs with ``pythonpath = ["."]``).
"""

from __future__ import annotations

from dataclasses import dataclass, field

PRODUCT_NAME = "LedgerLoop"
PRODUCT_PITCH = (
    "An automated reconciliation toolkit that matches transactions across "
    "sources and reports the result — built incrementally by the agent pipeline."
)


@dataclass(frozen=True)
class Feature:
    id: str
    title: str
    summary: str
    spec_points: tuple[str, ...]
    source_files: dict[str, str] = field(default_factory=dict)
    test_files: dict[str, str] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# F1 — domain models
# --------------------------------------------------------------------------- #
_INIT_PY = '''"""LedgerLoop — automated reconciliation toolkit (built by the agents)."""

__version__ = "0.1.0"
'''

_MODELS_PY = '''"""Core domain models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Transaction:
    id: str
    amount: int  # minor units (cents) to avoid float drift
    date: str    # ISO yyyy-mm-dd


@dataclass
class Reconciliation:
    matched: list[tuple[str, str]] = field(default_factory=list)
    unmatched_left: list[str] = field(default_factory=list)
    unmatched_right: list[str] = field(default_factory=list)

    @property
    def summary(self) -> dict[str, int]:
        return {
            "matched": len(self.matched),
            "unmatched_left": len(self.unmatched_left),
            "unmatched_right": len(self.unmatched_right),
        }
'''

_TEST_MODELS = '''from src.ledgerloop.models import Reconciliation, Transaction


def test_transaction_fields():
    t = Transaction("t1", 100, "2026-01-01")
    assert t.amount == 100 and t.id == "t1"


def test_empty_reconciliation_summary():
    assert Reconciliation().summary == {
        "matched": 0,
        "unmatched_left": 0,
        "unmatched_right": 0,
    }
'''


# --------------------------------------------------------------------------- #
# F2 — matching engine
# --------------------------------------------------------------------------- #
_MATCHER_PY = '''"""Matching engine: reconcile transactions across two sources."""

from __future__ import annotations

from .models import Reconciliation, Transaction


def reconcile(
    left: list[Transaction], right: list[Transaction]
) -> Reconciliation:
    """Match by (amount, date). Each right tx matches at most one left tx."""
    result = Reconciliation()
    remaining = list(right)
    for tx in left:
        match = next(
            (r for r in remaining if r.amount == tx.amount and r.date == tx.date),
            None,
        )
        if match is not None:
            result.matched.append((tx.id, match.id))
            remaining.remove(match)
        else:
            result.unmatched_left.append(tx.id)
    result.unmatched_right = [r.id for r in remaining]
    return result
'''

_TEST_MATCHER = '''from src.ledgerloop.matcher import reconcile
from src.ledgerloop.models import Transaction


def test_all_matched():
    r = reconcile([Transaction("l1", 100, "d")], [Transaction("r1", 100, "d")])
    assert r.summary["matched"] == 1


def test_unmatched_both_sides():
    r = reconcile([Transaction("l1", 100, "d")], [Transaction("r1", 200, "d")])
    assert r.unmatched_left == ["l1"] and r.unmatched_right == ["r1"]


def test_one_right_matches_only_once():
    r = reconcile(
        [Transaction("l1", 100, "d"), Transaction("l2", 100, "d")],
        [Transaction("r1", 100, "d")],
    )
    assert r.summary["matched"] == 1 and r.unmatched_left == ["l2"]
'''


# --------------------------------------------------------------------------- #
# F3 — CSV import
# --------------------------------------------------------------------------- #
_CSV_PY = '''"""Load transactions from CSV text."""

from __future__ import annotations

import csv
import io

from .models import Transaction


def load_transactions(csv_text: str) -> list[Transaction]:
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    return [
        Transaction(id=row["id"], amount=int(row["amount"]), date=row["date"])
        for row in reader
        if row.get("id")
    ]
'''

_TEST_CSV = '''from src.ledgerloop.csv_io import load_transactions


def test_load_basic():
    txns = load_transactions("id,amount,date\\nt1,100,2026-01-01\\nt2,250,2026-01-02\\n")
    assert len(txns) == 2 and txns[0].id == "t1" and txns[1].amount == 250


def test_load_header_only_is_empty():
    assert load_transactions("id,amount,date\\n") == []
'''


# --------------------------------------------------------------------------- #
# F4 — reporting
# --------------------------------------------------------------------------- #
_REPORT_PY = '''"""Render a reconciliation as a Markdown report."""

from __future__ import annotations

from .models import Reconciliation


def render_report(rec: Reconciliation) -> str:
    s = rec.summary
    return (
        "# Reconciliation Report\\n\\n"
        f"- Matched: {s['matched']}\\n"
        f"- Unmatched (left): {s['unmatched_left']}\\n"
        f"- Unmatched (right): {s['unmatched_right']}\\n"
    )
'''

_TEST_REPORT = '''from src.ledgerloop.models import Reconciliation
from src.ledgerloop.report import render_report


def test_report_contains_counts():
    out = render_report(Reconciliation(matched=[("a", "b")]))
    assert "Matched: 1" in out and "# Reconciliation Report" in out
'''


# --------------------------------------------------------------------------- #
# F5 — CLI tying it together
# --------------------------------------------------------------------------- #
_CLI_PY = '''"""CLI: reconcile two CSV files and print a report."""

from __future__ import annotations

import argparse

from .csv_io import load_transactions
from .matcher import reconcile
from .report import render_report


def run(left_csv: str, right_csv: str) -> str:
    rec = reconcile(load_transactions(left_csv), load_transactions(right_csv))
    return render_report(rec)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Reconcile two CSV files.")
    parser.add_argument("left")
    parser.add_argument("right")
    args = parser.parse_args(argv)
    with open(args.left) as f:
        left = f.read()
    with open(args.right) as f:
        right = f.read()
    print(run(left, right))


if __name__ == "__main__":
    main()
'''

_TEST_CLI = '''from src.ledgerloop.cli import run


def test_run_end_to_end():
    left = "id,amount,date\\nl1,100,2026-01-01\\n"
    right = "id,amount,date\\nr1,100,2026-01-01\\n"
    assert "Matched: 1" in run(left, right)
'''


# =========================================================================== #
# Web app — LedgerLoop becomes a self-contained, clickable reconciliation tool #
# built entirely from static files (no server, no build step). Each feature   #
# below is a real increment the agents materialise into src/webapp/.           #
# =========================================================================== #

_WEB_INDEX = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LedgerLoop — Reconciliation</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <header class="app-header">
    <div class="brand">
      <span class="brand-mark">L</span>
      <div>
        <h1>LedgerLoop</h1>
        <p>Match transactions across two sources in seconds.</p>
      </div>
    </div>
  </header>

  <main class="container">
    <section class="inputs">
      <div class="panel">
        <label for="source-a">Source A <span>(CSV: id, amount, date)</span></label>
        <textarea id="source-a" spellcheck="false" placeholder="id,amount,date&#10;a1,1000,2026-01-01"></textarea>
      </div>
      <div class="panel">
        <label for="source-b">Source B <span>(CSV: id, amount, date)</span></label>
        <textarea id="source-b" spellcheck="false" placeholder="id,amount,date&#10;b1,1000,2026-01-01"></textarea>
      </div>
    </section>

    <div class="toolbar">
      <button id="reconcile" class="btn btn-primary">Reconcile</button>
      <button id="load-sample" class="btn">Load sample data</button>
      <button id="clear" class="btn btn-ghost">Clear</button>
      <button id="export" class="btn btn-ghost" hidden>Export report</button>
    </div>

    <p id="error" class="error" hidden></p>

    <section id="summary" class="cards" hidden></section>
    <section id="results" class="results" hidden></section>
    <p id="empty" class="empty">Paste two CSVs (or load the sample) and hit Reconcile.</p>
  </main>

  <footer class="app-footer">
    Built autonomously by the <strong>Agentic</strong> pipeline — Planner → Coder → Tester → Reviewer.
  </footer>

  <script src="parse.js"></script>
  <script src="engine.js"></script>
  <script src="report.js"></script>
  <script src="sample.js"></script>
  <script src="app.js"></script>
</body>
</html>
'''

_WEB_STYLES = ''':root {
  --bg: #0a0c10; --surface: #11141b; --surface-2: #161a23;
  --border: #232834; --text: #e6e9ef; --muted: #8b93a7; --faint: #5b6273;
  --brand: #6d8bff; --ok: #46c98b; --warn: #f0b35a; --danger: #f0688a;
  --radius: 14px;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.app-header { border-bottom: 1px solid var(--border); padding: 18px 20px; }
.brand { display: flex; align-items: center; gap: 12px; max-width: 1000px; margin: 0 auto; }
.brand-mark {
  width: 38px; height: 38px; border-radius: 10px; display: grid; place-items: center;
  font-weight: 800; color: #fff; background: linear-gradient(135deg, var(--brand), var(--danger));
}
.brand h1 { font-size: 18px; margin: 0; letter-spacing: -0.01em; }
.brand p { font-size: 12px; margin: 2px 0 0; color: var(--faint); }
.container { max-width: 1000px; margin: 0 auto; padding: 24px 20px 60px; }
.inputs { display: grid; gap: 14px; grid-template-columns: 1fr 1fr; }
@media (max-width: 680px) { .inputs { grid-template-columns: 1fr; } }
.panel label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.panel label span { color: var(--faint); font-weight: 400; }
textarea {
  width: 100%; min-height: 170px; resize: vertical; padding: 12px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text); font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 13px;
}
textarea:focus { outline: none; border-color: var(--brand); }
.toolbar { display: flex; flex-wrap: wrap; gap: 10px; margin: 18px 0; }
.btn {
  padding: 9px 16px; border-radius: 10px; border: 1px solid var(--border);
  background: var(--surface-2); color: var(--text); font-size: 14px; font-weight: 600; cursor: pointer;
}
.btn:hover { filter: brightness(1.15); }
.btn-primary { background: var(--brand); border-color: var(--brand); color: #fff; }
.btn-ghost { background: transparent; }
.error { color: var(--danger); font-size: 13px; margin: 0 0 14px; }
.empty { color: var(--faint); font-size: 14px; text-align: center; padding: 32px 0; }
.cards { display: grid; gap: 12px; grid-template-columns: repeat(4, 1fr); margin-bottom: 22px; }
@media (max-width: 680px) { .cards { grid-template-columns: repeat(2, 1fr); } }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px; }
.card .value { font-size: 26px; font-weight: 800; }
.card .label { font-size: 12px; color: var(--muted); margin-top: 2px; }
.results { display: grid; gap: 18px; }
.result-block h3 { font-size: 14px; margin: 0 0 8px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border); }
th { color: var(--muted); font-weight: 600; }
td { font-family: ui-monospace, Menlo, monospace; }
.app-footer { border-top: 1px solid var(--border); padding: 18px 20px; text-align: center; color: var(--faint); font-size: 12px; }
'''

_WEB_PARSE = '''// CSV parsing for LedgerLoop.
window.LedgerLoop = window.LedgerLoop || {};

window.LedgerLoop.parseCsv = function parseCsv(text) {
  const lines = String(text || "").trim().split(/\\r?\\n/).filter(Boolean);
  if (lines.length === 0) return [];
  const header = lines[0].split(",").map((h) => h.trim().toLowerCase());
  const idx = { id: header.indexOf("id"), amount: header.indexOf("amount"), date: header.indexOf("date") };
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const cells = lines[i].split(",");
    const id = (cells[idx.id] || "").trim();
    if (!id) continue;
    rows.push({
      id,
      amount: parseInt((cells[idx.amount] || "0").trim(), 10) || 0,
      date: (cells[idx.date] || "").trim(),
    });
  }
  return rows;
};
'''

_WEB_ENGINE = '''// Matching engine for LedgerLoop (mirrors the Python core).
window.LedgerLoop = window.LedgerLoop || {};

window.LedgerLoop.reconcile = function reconcile(left, right) {
  const matched = [];
  const unmatchedLeft = [];
  const remaining = right.slice();
  for (const tx of left) {
    const j = remaining.findIndex((r) => r.amount === tx.amount && r.date === tx.date);
    if (j >= 0) {
      matched.push([tx.id, remaining[j].id]);
      remaining.splice(j, 1);
    } else {
      unmatchedLeft.push(tx.id);
    }
  }
  return { matched, unmatchedLeft, unmatchedRight: remaining.map((r) => r.id) };
};
'''

_WEB_REPORT = '''// Summary + Markdown report for a reconciliation result.
window.LedgerLoop = window.LedgerLoop || {};

window.LedgerLoop.summarize = function summarize(rec) {
  const matched = rec.matched.length;
  const ul = rec.unmatchedLeft.length;
  const ur = rec.unmatchedRight.length;
  const total = matched + ul + ur;
  const rate = total === 0 ? 0 : Math.round((matched / total) * 100);
  return { matched, unmatchedLeft: ul, unmatchedRight: ur, rate };
};

window.LedgerLoop.toMarkdown = function toMarkdown(rec) {
  const s = window.LedgerLoop.summarize(rec);
  return [
    "# LedgerLoop Reconciliation Report",
    "",
    "- Matched: " + s.matched,
    "- Unmatched (A): " + s.unmatchedLeft,
    "- Unmatched (B): " + s.unmatchedRight,
    "- Match rate: " + s.rate + "%",
  ].join("\\n");
};
'''

_WEB_SAMPLE = '''// Sample data for a one-click demo.
window.LedgerLoop = window.LedgerLoop || {};
window.LedgerLoop.SAMPLE_A =
  "id,amount,date\\na1,1000,2026-01-01\\na2,2550,2026-01-02\\na3,800,2026-01-03\\na4,4200,2026-01-05";
window.LedgerLoop.SAMPLE_B =
  "id,amount,date\\nb1,1000,2026-01-01\\nb2,2550,2026-01-02\\nb3,9999,2026-01-04\\nb4,4200,2026-01-05";
'''

_WEB_APP = '''// Wire the UI: parse -> reconcile -> render summary + tables + export.
(function () {
  const LL = window.LedgerLoop;
  const $ = (id) => document.getElementById(id);
  let lastRec = null;

  function table(title, rows, headers) {
    const head = headers.map((h) => "<th>" + h + "</th>").join("");
    const body = rows.length
      ? rows.map((r) => "<tr>" + r.map((c) => "<td>" + c + "</td>").join("") + "</tr>").join("")
      : '<tr><td colspan="' + headers.length + '" style="color:var(--faint)">none</td></tr>';
    return (
      '<div class="result-block"><h3>' + title + " (" + rows.length + ")</h3>" +
      "<table><thead><tr>" + head + "</tr></thead><tbody>" + body + "</tbody></table></div>"
    );
  }

  function render(rec) {
    const s = LL.summarize(rec);
    $("summary").innerHTML = [
      ['<div class="card"><div class="value">' + s.matched + '</div><div class="label">Matched</div></div>'],
      ['<div class="card"><div class="value">' + s.unmatchedLeft + '</div><div class="label">Unmatched A</div></div>'],
      ['<div class="card"><div class="value">' + s.unmatchedRight + '</div><div class="label">Unmatched B</div></div>'],
      ['<div class="card"><div class="value">' + s.rate + '%</div><div class="label">Match rate</div></div>'],
    ].join("");
    $("results").innerHTML =
      table("Matched pairs", rec.matched.map((m) => [m[0], m[1]]), ["Source A", "Source B"]) +
      table("Unmatched in A", rec.unmatchedLeft.map((x) => [x]), ["id"]) +
      table("Unmatched in B", rec.unmatchedRight.map((x) => [x]), ["id"]);
    $("summary").hidden = false;
    $("results").hidden = false;
    $("empty").hidden = true;
    $("export").hidden = false;
  }

  function run() {
    $("error").hidden = true;
    try {
      const a = LL.parseCsv($("source-a").value);
      const b = LL.parseCsv($("source-b").value);
      if (a.length === 0 && b.length === 0) {
        $("error").textContent = "Please enter CSV data in at least one source.";
        $("error").hidden = false;
        return;
      }
      lastRec = LL.reconcile(a, b);
      render(lastRec);
    } catch (e) {
      $("error").textContent = "Could not reconcile: " + e.message;
      $("error").hidden = false;
    }
  }

  $("reconcile").addEventListener("click", run);
  $("load-sample").addEventListener("click", function () {
    $("source-a").value = LL.SAMPLE_A;
    $("source-b").value = LL.SAMPLE_B;
    run();
  });
  $("clear").addEventListener("click", function () {
    $("source-a").value = "";
    $("source-b").value = "";
    $("summary").hidden = true;
    $("results").hidden = true;
    $("export").hidden = true;
    $("empty").hidden = false;
  });
  $("export").addEventListener("click", function () {
    if (!lastRec) return;
    const blob = new Blob([LL.toMarkdown(lastRec)], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "reconciliation-report.md";
    a.click();
    URL.revokeObjectURL(url);
  });
})();
'''

# --- web feature pytest checks (read the built static files) -------------- #
_TEST_WEB_SHELL = '''from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def test_index_has_inputs_and_buttons():
    html = _read("src/webapp/index.html")
    assert 'id="source-a"' in html and 'id="source-b"' in html
    assert 'id="reconcile"' in html


def test_styles_present():
    assert ".btn-primary" in _read("src/webapp/styles.css")
'''

_TEST_WEB_PARSE = '''from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_parse_defined():
    js = (ROOT / "src/webapp/parse.js").read_text(encoding="utf-8")
    assert "parseCsv" in js
'''

_TEST_WEB_ENGINE = '''from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_reconcile_defined():
    js = (ROOT / "src/webapp/engine.js").read_text(encoding="utf-8")
    assert "reconcile" in js and "unmatchedRight" in js
'''

_TEST_WEB_REPORT = '''from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_summarize_and_markdown():
    js = (ROOT / "src/webapp/report.js").read_text(encoding="utf-8")
    assert "summarize" in js and "toMarkdown" in js
'''

_TEST_WEB_APP = '''from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_app_wires_reconcile():
    js = (ROOT / "src/webapp/app.js").read_text(encoding="utf-8")
    assert "addEventListener" in js and "render" in js


def test_sample_data_present():
    js = (ROOT / "src/webapp/sample.js").read_text(encoding="utf-8")
    assert "SAMPLE_A" in js and "SAMPLE_B" in js
'''


BACKLOG: list[Feature] = [
    Feature(
        id="F1",
        title="Domain models",
        summary="Define the Transaction and Reconciliation data models.",
        spec_points=(
            "Transaction has id, amount (integer cents) and ISO date",
            "Reconciliation tracks matched + unmatched ids and a summary",
        ),
        source_files={
            "ledgerloop/__init__.py": _INIT_PY,
            "ledgerloop/models.py": _MODELS_PY,
        },
        test_files={"test_ledgerloop_models.py": _TEST_MODELS},
    ),
    Feature(
        id="F2",
        title="Matching engine",
        summary="Reconcile transactions across two sources by amount and date.",
        spec_points=(
            "Match left/right transactions on equal amount and date",
            "Each right transaction matches at most one left transaction",
            "Report unmatched transactions on both sides",
        ),
        source_files={"ledgerloop/matcher.py": _MATCHER_PY},
        test_files={"test_ledgerloop_matcher.py": _TEST_MATCHER},
    ),
    Feature(
        id="F3",
        title="CSV import",
        summary="Load transactions from CSV text into the domain model.",
        spec_points=(
            "Parse CSV with id, amount, date columns",
            "Skip blank rows; coerce amount to int",
        ),
        source_files={"ledgerloop/csv_io.py": _CSV_PY},
        test_files={"test_ledgerloop_csv_io.py": _TEST_CSV},
    ),
    Feature(
        id="F4",
        title="Reporting",
        summary="Render a reconciliation result as a Markdown report.",
        spec_points=("Produce a human-readable report of matched/unmatched counts",),
        source_files={"ledgerloop/report.py": _REPORT_PY},
        test_files={"test_ledgerloop_report.py": _TEST_REPORT},
    ),
    Feature(
        id="F5",
        title="Web app shell",
        summary="A responsive single-page UI shell with two CSV inputs and a toolbar.",
        spec_points=(
            "Two labelled CSV input areas (Source A / Source B)",
            "Reconcile / Load sample / Clear / Export controls",
            "Responsive, modern dark theme",
        ),
        source_files={
            "webapp/index.html": _WEB_INDEX,
            "webapp/styles.css": _WEB_STYLES,
        },
        test_files={"test_webapp_shell.py": _TEST_WEB_SHELL},
    ),
    Feature(
        id="F6",
        title="CSV parser (web)",
        summary="Parse pasted CSV text into transaction objects in the browser.",
        spec_points=(
            "Read id, amount, date columns by header name",
            "Skip blank rows; coerce amount to integer",
        ),
        source_files={"webapp/parse.js": _WEB_PARSE},
        test_files={"test_webapp_parse.py": _TEST_WEB_PARSE},
    ),
    Feature(
        id="F7",
        title="Matching engine (web)",
        summary="Reconcile two transaction lists in the browser by amount and date.",
        spec_points=(
            "Match on equal amount and date; each B row matches at most one A row",
            "Return matched pairs and unmatched ids on both sides",
        ),
        source_files={"webapp/engine.js": _WEB_ENGINE},
        test_files={"test_webapp_engine.py": _TEST_WEB_ENGINE},
    ),
    Feature(
        id="F8",
        title="Summary & report",
        summary="Compute summary stats and a downloadable Markdown report.",
        spec_points=(
            "Compute matched/unmatched counts and a match rate",
            "Render a Markdown report of the result",
        ),
        source_files={"webapp/report.js": _WEB_REPORT},
        test_files={"test_webapp_report.py": _TEST_WEB_REPORT},
    ),
    Feature(
        id="F9",
        title="Interactive app + results",
        summary="Wire inputs to the engine and render summary cards and result tables.",
        spec_points=(
            "Reconcile button parses inputs, runs the engine and renders results",
            "Show summary cards and matched/unmatched tables; handle errors",
        ),
        source_files={"webapp/app.js": _WEB_APP},
        test_files={"test_webapp_app.py": _TEST_WEB_APP},
    ),
    Feature(
        id="F10",
        title="Sample data & one-click demo",
        summary="Bundle sample CSVs so the tool can be tried in one click.",
        spec_points=(
            "Provide realistic sample data for both sources",
            "Load sample fills both inputs and reconciles immediately",
        ),
        source_files={"webapp/sample.js": _WEB_SAMPLE},
        test_files={},
    ),
]
