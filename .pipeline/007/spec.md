# Technical Specification

> run: `007` · author: `planner` · 2026-06-22T09:25:09.313898+00:00

## Overview
This run builds feature F8: Summary & report. Compute summary stats and a downloadable Markdown report.

## Architecture
A small, composable Python package (`ledgerloop`) grown feature by feature.

## Components
- webapp/report.js

## Functional Requirements
- Compute matched/unmatched counts and a match rate
- Render a Markdown report of the result

## Non-Functional Requirements
- Deterministic
- Fully unit-tested
- Strongly typed

