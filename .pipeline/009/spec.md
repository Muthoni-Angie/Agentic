# Technical Specification

> run: `009` · author: `planner` · 2026-06-22T09:25:51.346533+00:00

## Overview
This run builds feature F10: Sample data & one-click demo. Bundle sample CSVs so the tool can be tried in one click.

## Architecture
A small, composable Python package (`ledgerloop`) grown feature by feature.

## Components
- webapp/sample.js

## Functional Requirements
- Provide realistic sample data for both sources
- Load sample fills both inputs and reconciles immediately

## Non-Functional Requirements
- Deterministic
- Fully unit-tested
- Strongly typed

