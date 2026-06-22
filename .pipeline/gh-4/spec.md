# Technical Specification

> run: `gh-4` · author: `planner` · 2026-06-22T08:18:29.392691+00:00

## Overview
This run builds feature F2: Matching engine. Reconcile transactions across two sources by amount and date.

## Architecture
A small, composable Python package (`ledgerloop`) grown feature by feature.

## Components
- ledgerloop/matcher.py

## Functional Requirements
- Match left/right transactions on equal amount and date
- Each right transaction matches at most one left transaction
- Report unmatched transactions on both sides

## Non-Functional Requirements
- Deterministic
- Fully unit-tested
- Strongly typed

