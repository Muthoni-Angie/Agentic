# Test Plan

> run: `gh-7` · author: `tester` · 2026-06-22T14:21:13.701648+00:00


## Approach
Cover happy paths and edge cases of the matching engine with deterministic unit tests, derived from the spec.

## Cases

- ✅ `test_happy_path_all_matched` (unit) — all transactions reconcile
- ✅ `test_unmatched_on_both_sides` (unit) — unmatched flagging
- ✅ `test_edge_empty_inputs` (edge) — empty source handling
- ✅ `test_edge_one_right_matches_only_once` (edge) — no double-matching

## Test Files
- tests/test_reconcile.py

