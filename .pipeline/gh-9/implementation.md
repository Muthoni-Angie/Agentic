# Implementation Notes

> run: `gh-9` · author: `coder` · 2026-07-02T09:55:25.894982+00:00

## Summary
Implemented a deterministic reconciliation engine that matches transactions across two sources by amount and date.

## Files Changed
- src/reconcile.py
- src/__init__.py

## Key Decisions
- Amounts stored in integer minor units to avoid float drift.
- Matching is a pure function for trivial testability.
- Each right-side transaction matches at most one left-side row.

## Tasks Addressed
- T1
- T2
- T3

