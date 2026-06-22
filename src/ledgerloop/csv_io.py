"""Load transactions from CSV text."""

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
