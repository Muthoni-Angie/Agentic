"""Render a reconciliation as a Markdown report."""

from __future__ import annotations

from .models import Reconciliation


def render_report(rec: Reconciliation) -> str:
    s = rec.summary
    return (
        "# Reconciliation Report\n\n"
        f"- Matched: {s['matched']}\n"
        f"- Unmatched (left): {s['unmatched_left']}\n"
        f"- Unmatched (right): {s['unmatched_right']}\n"
    )
