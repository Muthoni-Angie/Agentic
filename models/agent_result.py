"""The structured result every agent returns from ``run()``."""

from __future__ import annotations

from pydantic import BaseModel, Field

from models.run_state import Stage


class AgentResult(BaseModel):
    """Outcome of a single agent execution.

    Agents never mutate run state directly — they return this and the
    orchestrator is the sole authority that advances the state machine.
    """

    agent: str
    success: bool = True

    # Only meaningful for gatekeeper agents (Tester, Reviewer). ``None`` means
    # "this agent does not vote on approval".
    approved: bool | None = None

    # Canonical filenames the agent produced/updated inside the run folder.
    artifacts: list[str] = Field(default_factory=list)

    # Source/test files touched on disk (outside the run folder).
    files_written: list[str] = Field(default_factory=list)

    # Human-readable log lines surfaced in the UI.
    messages: list[str] = Field(default_factory=list)

    # Optional explicit next stage. When None the orchestrator decides.
    next_stage: Stage | None = None

    @property
    def rejected(self) -> bool:
        return self.approved is False
