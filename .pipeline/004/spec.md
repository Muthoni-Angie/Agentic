# Technical Specification

> run: `004` · author: `planner` · 2026-06-22T09:16:46.316343+00:00

## Overview
This run builds feature F5: Web app shell. A responsive single-page UI shell with two CSV inputs and a toolbar.

## Architecture
A small, composable Python package (`ledgerloop`) grown feature by feature.

## Components
- webapp/index.html
- webapp/styles.css

## Functional Requirements
- Two labelled CSV input areas (Source A / Source B)
- Reconcile / Load sample / Clear / Export controls
- Responsive, modern dark theme

## Non-Functional Requirements
- Deterministic
- Fully unit-tested
- Strongly typed

