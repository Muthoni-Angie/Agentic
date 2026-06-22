from src.ledgerloop.models import Reconciliation
from src.ledgerloop.report import render_report


def test_report_contains_counts():
    out = render_report(Reconciliation(matched=[("a", "b")]))
    assert "Matched: 1" in out and "# Reconciliation Report" in out
