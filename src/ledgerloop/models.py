"""Core domain models."""

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
