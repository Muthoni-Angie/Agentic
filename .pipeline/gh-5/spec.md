# Technical Specification

> run: `gh-5` · author: `planner` · 2026-06-22T08:43:22.735199+00:00

## Overview
This run builds feature F3: CSV import. Load transactions from CSV text into the domain model.

## Architecture
A small, composable Python package (`ledgerloop`) grown feature by feature.

## Components
- ledgerloop/csv_io.py

## Functional Requirements
- Parse CSV with id, amount, date columns
- Skip blank rows; coerce amount to int

## Non-Functional Requirements
- Deterministic
- Fully unit-tested
- Strongly typed

