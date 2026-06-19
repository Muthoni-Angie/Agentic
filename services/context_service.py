"""Assembles the execution context handed to every agent.

Agents must NOT gather their own context — they receive a fully-built
``AgentContext`` so they stay decoupled from the filesystem layout, git, and
each other. This service is the single place that knows how to read the world.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

from models.run_state import RunState, Stage
from services.artifact_service import ArtifactService
from services.state_service import StateService


class AgentContext(BaseModel):
    """Everything an agent needs to do its job, read-only."""

    run_id: str
    stage: Stage
    state: RunState

    # filename -> rendered markdown for every prior artifact in the run.
    artifacts: dict[str, str] = Field(default_factory=dict)

    repo_tree: list[str] = Field(default_factory=list)
    git_diff: str = ""
    source_files: dict[str, str] = Field(default_factory=dict)

    def artifact(self, filename: str) -> str | None:
        return self.artifacts.get(filename)


class ContextService:
    def __init__(
        self,
        artifact_service: ArtifactService,
        state_service: StateService,
        project_root: Path,
        src_dir: Path,
    ) -> None:
        self.artifacts = artifact_service
        self.state = state_service
        self.project_root = Path(project_root)
        self.src_dir = Path(src_dir)

    def build(self, run_id: str) -> AgentContext:
        state = self.state.load(run_id)
        if state is None:
            raise ValueError(f"unknown run_id: {run_id}")

        artifacts = {
            name: self.artifacts.read_markdown(run_id, name) or ""
            for name in self.artifacts.list_artifacts(run_id)
        }

        return AgentContext(
            run_id=run_id,
            stage=state.stage,
            state=state,
            artifacts=artifacts,
            repo_tree=self._repo_tree(),
            git_diff=self._git_diff(),
            source_files=self._source_files(),
        )

    # ---- world readers -------------------------------------------------- #
    def _repo_tree(self) -> list[str]:
        if not self.src_dir.exists():
            return []
        return sorted(
            str(p.relative_to(self.project_root))
            for p in self.src_dir.rglob("*")
            if p.is_file()
        )

    def _source_files(self, max_bytes: int = 50_000) -> dict[str, str]:
        files: dict[str, str] = {}
        if not self.src_dir.exists():
            return files
        for path in sorted(self.src_dir.rglob("*")):
            if path.is_file() and path.stat().st_size <= max_bytes:
                rel = str(path.relative_to(self.project_root))
                try:
                    files[rel] = path.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
        return files

    def _git_diff(self) -> str:
        try:
            result = subprocess.run(
                ["git", "diff", "--stat"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout
        except (OSError, subprocess.SubprocessError):
            return ""
