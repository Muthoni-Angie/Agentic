"""Shared pytest fixtures: an isolated pipeline rooted in a temp directory."""

from __future__ import annotations

from pathlib import Path

import pytest

from agents.coder.agent import CoderAgent
from agents.planner.agent import PlannerAgent
from agents.reviewer.agent import ReviewerAgent
from agents.tester.agent import TesterAgent
from orchestrator.orchestrator import Orchestrator
from services.artifact_service import ArtifactService
from services.context_service import ContextService
from services.state_service import StateService


@pytest.fixture
def project(tmp_path: Path):
    """A throwaway project root with isolated .pipeline / src / tests dirs."""
    pipeline = tmp_path / ".pipeline"
    src = tmp_path / "src"
    tests = tmp_path / "tests"
    for d in (pipeline, src, tests):
        d.mkdir(parents=True, exist_ok=True)

    artifacts = ArtifactService(pipeline)
    state = StateService(pipeline)
    context = ContextService(artifacts, state, tmp_path, src)
    return {
        "root": tmp_path,
        "artifacts": artifacts,
        "state": state,
        "context": context,
        "src": src,
        "tests": tests,
    }


@pytest.fixture
def orchestrator(project):
    deps = (project["artifacts"], project["context"], project["src"],
            project["tests"])
    return Orchestrator(
        state_service=project["state"],
        planner=PlannerAgent(*deps),
        coder=CoderAgent(*deps),
        tester=TesterAgent(*deps),
        reviewer=ReviewerAgent(*deps),
    )
