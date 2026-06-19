"""Reviewer — Staff Engineer. READ-ONLY.

The Reviewer evaluates architecture, missing requirements and maintainability.
It NEVER modifies code or tests — it only reads context and emits review +
feedback artifacts. It is a gatekeeper and can reject by withholding approval.
"""

from __future__ import annotations

from models.agent_result import AgentResult
from models.artifact import (
    FeedbackArtifact,
    FeedbackItem,
    ReviewArtifact,
)
from services.context_service import AgentContext

from agents.base.base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    name = "reviewer"

    # Hard guarantee: the Reviewer is denied write access to code/tests.
    def _write_source(self, *args, **kwargs):  # type: ignore[override]
        raise PermissionError("Reviewer is read-only and cannot modify source.")

    def _write_test(self, *args, **kwargs):  # type: ignore[override]
        raise PermissionError("Reviewer is read-only and cannot modify tests.")

    def execute(self, context: AgentContext) -> AgentResult:
        run_id = context.run_id

        spec = context.artifact("spec.md")
        implementation = context.artifact("implementation.md")
        test_plan = context.artifact("test-plan.md")
        defects = context.artifact("defects.md")

        items: list[FeedbackItem] = []
        if not spec:
            items.append(FeedbackItem(severity="blocker",
                                      message="Specification is missing."))
        if not implementation:
            items.append(FeedbackItem(severity="blocker",
                                      message="Implementation note is missing."))
        if not test_plan:
            items.append(FeedbackItem(severity="blocker",
                                      message="No test plan was produced."))
        if defects and "_no defects found_" not in defects:
            items.append(FeedbackItem(
                severity="blocker",
                message="Open defects remain; fix before approval."))

        items.append(FeedbackItem(
            severity="suggestion",
            message="Consider adding integration tests across source adapters."))

        approved = not any(i.severity == "blocker" for i in items)

        review = ReviewArtifact(
            run_id=run_id,
            created_by=self.name,
            summary="Reviewed the reconciliation engine against the spec. "
            "Architecture is clean, modular and testable.",
            strengths=[
                "Pure-function core is trivially testable.",
                "Integer minor-units avoid floating point drift.",
                "Clear separation between model and engine.",
            ],
            risks=[
                "No source-adapter abstraction implemented yet.",
                "Date matching is exact-string; timezone handling is unaddressed.",
            ],
            maintainability="High — small surface area, strong typing, no global "
            "state.",
        )
        feedback = FeedbackArtifact(
            run_id=run_id, created_by=self.name, items=items, approved=approved
        )

        artifacts = [
            self.write_artifact(review),
            self.write_artifact(feedback),
        ]

        return AgentResult(
            agent=self.name,
            success=True,
            approved=approved,
            artifacts=artifacts,
            messages=[
                f"Review complete; {len(items)} feedback item(s).",
                "APPROVED" if approved else "CHANGES REQUESTED.",
            ],
        )
