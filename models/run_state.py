"""Run state model and the pipeline state machine definition.

The state machine is intentionally explicit and serializable so the entire
lifecycle of a run can be reconstructed from ``.pipeline/<run_id>/status.json``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class Stage(str, Enum):
    """The ordered stages of the autonomous engineering pipeline."""

    PLANNING = "PLANNING"
    CODING = "CODING"
    TESTING = "TESTING"
    REVIEWING = "REVIEWING"
    DONE = "DONE"


# Canonical forward order used by the orchestrator to advance the pipeline.
STAGE_ORDER: tuple[Stage, ...] = (
    Stage.PLANNING,
    Stage.CODING,
    Stage.TESTING,
    Stage.REVIEWING,
    Stage.DONE,
)


class TransitionRecord(BaseModel):
    """An immutable audit entry for a single state transition."""

    iteration: int
    from_stage: Stage
    to_stage: Stage
    agent: str
    note: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RunState(BaseModel):
    """Persisted state for a single pipeline run.

    Mirrors ``status.json`` and is the single source of truth the orchestrator
    uses to decide which agent runs next.
    """

    run_id: str
    stage: Stage = Stage.PLANNING

    planner_complete: bool = False
    coder_complete: bool = False
    tester_complete: bool = False
    reviewer_complete: bool = False

    # Approval gates — the pipeline finishes only when BOTH are true.
    tester_approved: bool = False
    reviewer_approved: bool = False

    iteration: int = 0
    history: list[TransitionRecord] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_complete(self) -> bool:
        """A run is complete only when both approval gates are satisfied."""
        return self.tester_approved and self.reviewer_approved

    def record_transition(self, to_stage: Stage, agent: str, note: str = "") -> None:
        """Append an audit record and move to ``to_stage``."""
        self.history.append(
            TransitionRecord(
                iteration=self.iteration,
                from_stage=self.stage,
                to_stage=to_stage,
                agent=agent,
                note=note,
            )
        )
        self.stage = to_stage
        self.updated_at = datetime.now(timezone.utc)
