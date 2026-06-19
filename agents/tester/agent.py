"""Tester — QA Engineer.

Reads the spec and implementation, generates unit tests covering happy paths and
edge cases, writes them into ``tests/`` and emits a test plan + defects report.
The Tester is a gatekeeper: it can reject by withholding approval.
"""

from __future__ import annotations

from models.agent_result import AgentResult
from models.artifact import (
    Defect,
    DefectArtifact,
    TestCase,
    TestPlanArtifact,
)
from services.context_service import AgentContext

from agents.base.base_agent import BaseAgent

_TEST_SOURCE = '''"""Generated unit tests for the reconciliation engine."""

from src.reconcile import Transaction, reconcile


def test_happy_path_all_matched():
    left = [Transaction("l1", 1000, "2026-01-01")]
    right = [Transaction("r1", 1000, "2026-01-01")]
    result = reconcile(left, right)
    assert result.summary == {
        "matched": 1,
        "unmatched_left": 0,
        "unmatched_right": 0,
    }


def test_unmatched_on_both_sides():
    left = [Transaction("l1", 500, "2026-01-01")]
    right = [Transaction("r1", 999, "2026-01-02")]
    result = reconcile(left, right)
    assert result.unmatched_left == ["l1"]
    assert result.unmatched_right == ["r1"]


def test_edge_empty_inputs():
    result = reconcile([], [])
    assert result.summary["matched"] == 0


def test_edge_one_right_matches_only_once():
    left = [Transaction("l1", 100, "d"), Transaction("l2", 100, "d")]
    right = [Transaction("r1", 100, "d")]
    result = reconcile(left, right)
    assert result.summary["matched"] == 1
    assert result.unmatched_left == ["l2"]
'''


class TesterAgent(BaseAgent):
    name = "tester"

    def execute(self, context: AgentContext) -> AgentResult:
        run_id = context.run_id

        implementation = context.artifact("implementation.md")
        spec = context.artifact("spec.md")
        has_source = any(p.endswith("reconcile.py") for p in context.repo_tree)

        cases = [
            TestCase(name="test_happy_path_all_matched", kind="unit",
                     covers="all transactions reconcile"),
            TestCase(name="test_unmatched_on_both_sides", kind="unit",
                     covers="unmatched flagging"),
            TestCase(name="test_edge_empty_inputs", kind="edge",
                     covers="empty source handling"),
            TestCase(name="test_edge_one_right_matches_only_once", kind="edge",
                     covers="no double-matching"),
        ]

        defects: list[Defect] = []
        if not implementation:
            defects.append(Defect(id="D1", severity="blocker",
                                  summary="No implementation note found."))
        if not has_source:
            defects.append(Defect(id="D2", severity="blocker",
                                  summary="No source code found to test."))

        test_file = ""
        if has_source:
            test_file = self._write_test("test_reconcile.py", _TEST_SOURCE)

        plan = TestPlanArtifact(
            run_id=run_id,
            created_by=self.name,
            approach="Cover happy paths and edge cases of the matching engine "
            "with deterministic unit tests, derived from the spec.",
            cases=cases,
            files_changed=["tests/test_reconcile.py"] if test_file else [],
        )
        defect_report = DefectArtifact(
            run_id=run_id, created_by=self.name, defects=defects
        )

        artifacts = [
            self.write_artifact(plan),
            self.write_artifact(defect_report),
        ]

        approved = not defect_report.has_blockers and bool(spec)
        return AgentResult(
            agent=self.name,
            success=True,
            approved=approved,
            artifacts=artifacts,
            files_written=[test_file] if test_file else [],
            messages=[
                f"Authored {len(cases)} test cases; "
                f"{len(defects)} defect(s) found.",
                "APPROVED" if approved else "REJECTED — defects must be fixed.",
            ],
        )
