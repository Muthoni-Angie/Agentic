# Technical Specification

> run: `gh-6` · author: `planner` · 2026-06-22T08:48:35.542413+00:00

## Overview
This run builds feature F4: Reporting. Render a reconciliation result as a Markdown report.

## Architecture
A small, composable Python package (`ledgerloop`) grown feature by feature.

## Components
- ledgerloop/report.py

## Functional Requirements
- Produce a human-readable report of matched/unmatched counts

## Non-Functional Requirements
- Deterministic
- Fully unit-tested
- Strongly typed

