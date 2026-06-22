# Technical Specification

> run: `008` · author: `planner` · 2026-06-22T09:25:30.319945+00:00

## Overview
This run builds feature F9: Interactive app + results. Wire inputs to the engine and render summary cards and result tables.

## Architecture
A small, composable Python package (`ledgerloop`) grown feature by feature.

## Components
- webapp/app.js

## Functional Requirements
- Reconcile button parses inputs, runs the engine and renders results
- Show summary cards and matched/unmatched tables; handle errors

## Non-Functional Requirements
- Deterministic
- Fully unit-tested
- Strongly typed

