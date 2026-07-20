# Test Plan

> run: `gh-12` · author: `tester` · 2026-07-20T11:31:25.503895+00:00


## Approach
Cover happy paths and edge cases of the matching engine with deterministic unit tests, derived from the spec.

## Cases

- ✅ `test_happy_path_all_matched` (unit) — all transactions reconcile
- ✅ `test_unmatched_on_both_sides` (unit) — unmatched flagging
- ✅ `test_edge_empty_inputs` (edge) — empty source handling
- ✅ `test_edge_one_right_matches_only_once` (edge) — no double-matching

## Test Files
- tests/test_reconcile.py

