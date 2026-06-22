"""Matching engine: reconcile transactions across two sources."""

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
