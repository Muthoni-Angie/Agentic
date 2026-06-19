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
        title="CLI",
        summary="Reconcile two CSV files end-to-end from the command line.",
        spec_points=(
            "Load two CSVs, reconcile them, print the report",
            "Expose run() for programmatic use and a main() CLI entrypoint",
        ),
        source_files={"ledgerloop/cli.py": _CLI_PY},
        test_files={"test_ledgerloop_cli.py": _TEST_CLI},
    ),
]
