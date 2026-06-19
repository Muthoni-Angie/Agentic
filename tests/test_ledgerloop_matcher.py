from src.ledgerloop.matcher import reconcile
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
