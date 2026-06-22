# Technical Specification

> run: `005` · author: `planner` · 2026-06-22T09:17:07.621710+00:00

## Overview
This run builds feature F6: CSV parser (web). Parse pasted CSV text into transaction objects in the browser.

## Architecture
A small, composable Python package (`ledgerloop`) grown feature by feature.

## Components
- webapp/parse.js

## Functional Requirements
- Read id, amount, date columns by header name
- Skip blank rows; coerce amount to integer

## Non-Functional Requirements
- Deterministic
- Fully unit-tested
- Strongly typed

