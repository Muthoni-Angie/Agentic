"""BaseAgent — the contract every agent inherits.

Agents know how to do exactly three things:

* ``read_context()`` — receive an assembled view of the world,
* ``write_artifact()`` — emit typed artifacts into the run folder,
* ``run()`` — orchestrate their own work and return an :class:`AgentResult`.

Agents do not know about each other, do not touch run state, and do not gather
their own context. Subclasses implement :meth:`execute`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from models.agent_result import AgentResult
from models.artifact import BaseArtifact
from services.artifact_service import ArtifactService
from services.context_service import AgentContext, ContextService


class BaseAgent(ABC):
    #: stable identifier used in logs, status history and AgentResult.
    name: str = "base"

    def __init__(
        self,
        artifact_service: ArtifactService,
        context_service: ContextService,
        src_dir: Path,
        tests_dir: Path,
        roadmap=None,
    ) -> None:
        self._artifacts = artifact_service
        self._context = context_service
        self.src_dir = Path(src_dir)
        self.tests_dir = Path(tests_dir)
        # Optional RoadmapService. When present, agents build the current
        # backlog feature; when None they fall back to their default behaviour.
        self.roadmap = roadmap

    # ---- BaseAgent contract -------------------------------------------- #
    def read_context(self, run_id: str) -> AgentContext:
        return self._context.build(run_id)

    def write_artifact(self, artifact: BaseArtifact) -> str:
        self._artifacts.write_artifact(artifact)
        return artifact.filename

    def run(self, run_id: str) -> AgentResult:
        context = self.read_context(run_id)
        return self.execute(context)

    # ---- subclass responsibility --------------------------------------- #
    @abstractmethod
    def execute(self, context: AgentContext) -> AgentResult:
        """Perform the agent's responsibilities and return a result."""

    # ---- helpers -------------------------------------------------------- #
    def _write_source(self, relative_path: str, content: str) -> str:
        path = self.src_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path)

    def _write_test(self, relative_path: str, content: str) -> str:
        path = self.tests_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path)
