# Technical Specification

> run: `gh-18` · author: `planner` · 2026-08-31T16:25:29.147110+00:00

## Overview
A service that ingests transactions from multiple sources and produces a reconciled ledger with an audit trail.

## Architecture
Modular Python core with a pure-function matching engine, a pluggable source adapter layer, and a thin API surface.

## Components
- Matching engine (deterministic, pure functions)
- Source adapters (bank, processor, ledger)
- Reconciliation report builder

## Functional Requirements
- Match transactions across two sources by amount and date
- Flag unmatched transactions on both sides
- Produce a summary with matched/unmatched counts

## Non-Functional Requirements
- Deterministic and side-effect-free core
- 100% unit-test coverage of the matching engine
- Strong typing throughout

