"""Generated unit tests for the reconciliation engine."""

from src.reconcile import Transaction, reconcile


def test_happy_path_all_matched():
    left = [Transaction("l1", 1000, "2026-01-01")]
    right = [Transaction("r1", 1000, "2026-01-01")]
    result = reconcile(left, right)
    assert result.summary == {
        "matched": 1,
        "unmatched_left": 0,
        "unmatched_right": 0,
    }


def test_unmatched_on_both_sides():
    left = [Transaction("l1", 500, "2026-01-01")]
    right = [Transaction("r1", 999, "2026-01-02")]
    result = reconcile(left, right)
    assert result.unmatched_left == ["l1"]
    assert result.unmatched_right == ["r1"]


def test_edge_empty_inputs():
    result = reconcile([], [])
    assert result.summary["matched"] == 0


def test_edge_one_right_matches_only_once():
    left = [Transaction("l1", 100, "d"), Transaction("l2", 100, "d")]
    right = [Transaction("r1", 100, "d")]
    result = reconcile(left, right)
    assert result.summary["matched"] == 1
    assert result.unmatched_left == ["l2"]
