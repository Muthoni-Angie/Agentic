# Technical Specification

> run: `006` · author: `planner` · 2026-06-22T09:24:43.916183+00:00

## Overview
This run builds feature F7: Matching engine (web). Reconcile two transaction lists in the browser by amount and date.

## Architecture
A small, composable Python package (`ledgerloop`) grown feature by feature.

## Components
- webapp/engine.js

## Functional Requirements
- Match on equal amount and date; each B row matches at most one A row
- Return matched pairs and unmatched ids on both sides

## Non-Functional Requirements
- Deterministic
- Fully unit-tested
- Strongly typed

