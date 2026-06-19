from src.ledgerloop.models import Reconciliation, Transaction


def test_transaction_fields():
    t = Transaction("t1", 100, "2026-01-01")
    assert t.amount == 100 and t.id == "t1"


def test_empty_reconciliation_summary():
    assert Reconciliation().summary == {
        "matched": 0,
        "unmatched_left": 0,
        "unmatched_right": 0,
    }
