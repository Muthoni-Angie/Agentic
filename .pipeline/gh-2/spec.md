# Technical Specification

> run: `gh-2` · author: `planner` · 2026-06-19T18:50:16.290700+00:00

## Overview
This run builds feature F1: Domain models. Define the Transaction and Reconciliation data models.

## Architecture
A small, composable Python package (`ledgerloop`) grown feature by feature.

## Components
- ledgerloop/__init__.py
- ledgerloop/models.py

## Functional Requirements
- Transaction has id, amount (integer cents) and ISO date
- Reconciliation tracks matched + unmatched ids and a summary

## Non-Functional Requirements
- Deterministic
- Fully unit-tested
- Strongly typed

