"""Strongly-typed, serializable artifact models.

Artifacts are the *only* communication channel between agents. Every artifact:

* validates its own shape via Pydantic,
* knows the canonical filename it is written to inside ``.pipeline/<run_id>/``,
* renders to human-friendly Markdown for the UI and for git history.

The JSON form (``model_dump``) is persisted alongside the Markdown as a sidecar
so downstream agents can re-hydrate a typed object instead of parsing prose.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import ClassVar

from pydantic import BaseModel, Field


class BaseArtifact(BaseModel):
    """Common metadata and rendering contract for all artifacts."""

    # Canonical Markdown filename inside the run folder. Overridden per type.
    filename: ClassVar[str] = "artifact.md"
    title: ClassVar[str] = "Artifact"

    run_id: str
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_markdown(self) -> str:  # pragma: no cover - overridden by subclasses
        raise NotImplementedError

    def _header(self) -> str:
        return (
            f"# {self.title}\n\n"
            f"> run: `{self.run_id}` · author: `{self.created_by}` · "
            f"{self.created_at.isoformat()}\n"
        )


def _bullets(items: list[str]) -> str:
    if not items:
        return "_none_\n"
    return "\n".join(f"- {item}" for item in items) + "\n"


# --------------------------------------------------------------------------- #
# Planner artifacts
# --------------------------------------------------------------------------- #
class IdeaArtifact(BaseArtifact):
    filename: ClassVar[str] = "idea.md"
    title: ClassVar[str] = "Idea"

    name: str
    pitch: str
    problem: str
    target_market: str
    revenue_streams: list[str] = Field(default_factory=list)
    scale_potential: str = ""

    def to_markdown(self) -> str:
        return (
            f"{self._header()}\n"
            f"## {self.name}\n\n{self.pitch}\n\n"
            f"### Problem\n{self.problem}\n\n"
            f"### Target Market\n{self.target_market}\n\n"
            f"### Revenue Streams\n{_bullets(self.revenue_streams)}\n"
            f"### Scale Potential\n{self.scale_potential}\n"
        )


class SpecArtifact(BaseArtifact):
    filename: ClassVar[str] = "spec.md"
    title: ClassVar[str] = "Technical Specification"

    overview: str
    architecture: str
    components: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    non_functional: list[str] = Field(default_factory=list)

    def to_markdown(self) -> str:
        return (
            f"{self._header()}\n"
            f"## Overview\n{self.overview}\n\n"
            f"## Architecture\n{self.architecture}\n\n"
            f"## Components\n{_bullets(self.components)}\n"
            f"## Functional Requirements\n{_bullets(self.requirements)}\n"
            f"## Non-Functional Requirements\n{_bullets(self.non_functional)}\n"
        )


class Task(BaseModel):
    id: str
    title: str
    description: str = ""
    done: bool = False


class TaskArtifact(BaseArtifact):
    filename: ClassVar[str] = "tasks.md"
    title: ClassVar[str] = "Task Breakdown"

    tasks: list[Task] = Field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [self._header(), "\n## Tasks\n"]
        if not self.tasks:
            lines.append("_no tasks_\n")
        for task in self.tasks:
            box = "x" if task.done else " "
            lines.append(f"- [{box}] **{task.id}** — {task.title}")
            if task.description:
                lines.append(f"  - {task.description}")
        return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Coder artifact
# --------------------------------------------------------------------------- #
class ImplementationArtifact(BaseArtifact):
    filename: ClassVar[str] = "implementation.md"
    title: ClassVar[str] = "Implementation Notes"

    summary: str
    files_changed: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    addressed_tasks: list[str] = Field(default_factory=list)

    def to_markdown(self) -> str:
        return (
            f"{self._header()}\n"
            f"## Summary\n{self.summary}\n\n"
            f"## Files Changed\n{_bullets(self.files_changed)}\n"
            f"## Key Decisions\n{_bullets(self.decisions)}\n"
            f"## Tasks Addressed\n{_bullets(self.addressed_tasks)}\n"
        )


# --------------------------------------------------------------------------- #
# Tester artifacts
# --------------------------------------------------------------------------- #
class TestCase(BaseModel):
    name: str
    kind: str = "unit"  # unit | edge | integration
    covers: str = ""
    passed: bool = True


class TestPlanArtifact(BaseArtifact):
    filename: ClassVar[str] = "test-plan.md"
    title: ClassVar[str] = "Test Plan"

    approach: str
    cases: list[TestCase] = Field(default_factory=list)
    files_changed: list[str] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(case.passed for case in self.cases)

    def to_markdown(self) -> str:
        lines = [self._header(), f"\n## Approach\n{self.approach}\n", "## Cases\n"]
        if not self.cases:
            lines.append("_no cases_\n")
        for case in self.cases:
            status = "✅" if case.passed else "❌"
            lines.append(f"- {status} `{case.name}` ({case.kind}) — {case.covers}")
        lines.append(f"\n## Test Files\n{_bullets(self.files_changed)}")
        return "\n".join(lines) + "\n"


class Defect(BaseModel):
    id: str
    severity: str = "minor"  # blocker | major | minor
    summary: str
    detail: str = ""


class DefectArtifact(BaseArtifact):
    filename: ClassVar[str] = "defects.md"
    title: ClassVar[str] = "Defects"

    defects: list[Defect] = Field(default_factory=list)

    @property
    def has_blockers(self) -> bool:
        return any(d.severity in {"blocker", "major"} for d in self.defects)

    def to_markdown(self) -> str:
        lines = [self._header(), "\n## Defects\n"]
        if not self.defects:
            lines.append("_no defects found_ 🎉\n")
        for d in self.defects:
            lines.append(f"### [{d.severity.upper()}] {d.id} — {d.summary}")
            if d.detail:
                lines.append(d.detail)
        return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Reviewer artifacts
# --------------------------------------------------------------------------- #
class ReviewArtifact(BaseArtifact):
    filename: ClassVar[str] = "review.md"
    title: ClassVar[str] = "Architecture Review"

    summary: str
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    maintainability: str = ""

    def to_markdown(self) -> str:
        return (
            f"{self._header()}\n"
            f"## Summary\n{self.summary}\n\n"
            f"## Strengths\n{_bullets(self.strengths)}\n"
            f"## Risks\n{_bullets(self.risks)}\n"
            f"## Maintainability\n{self.maintainability}\n"
        )


class FeedbackItem(BaseModel):
    severity: str = "suggestion"  # blocker | improvement | suggestion
    message: str


class FeedbackArtifact(BaseArtifact):
    filename: ClassVar[str] = "feedback.md"
    title: ClassVar[str] = "Reviewer Feedback"

    items: list[FeedbackItem] = Field(default_factory=list)
    approved: bool = False

    @property
    def has_blockers(self) -> bool:
        return any(item.severity == "blocker" for item in self.items)

    def to_markdown(self) -> str:
        verdict = "APPROVED ✅" if self.approved else "CHANGES REQUESTED 🔁"
        lines = [self._header(), f"\n**Verdict: {verdict}**\n", "## Items\n"]
        if not self.items:
            lines.append("_no feedback_\n")
        for item in self.items:
            lines.append(f"- **[{item.severity}]** {item.message}")
        return "\n".join(lines) + "\n"
