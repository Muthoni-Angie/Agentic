"""Each agent honours its read/produce/modify contract."""

import pytest

from agents.coder.agent import CoderAgent
from agents.planner.agent import PlannerAgent
from agents.reviewer.agent import ReviewerAgent
from agents.tester.agent import TesterAgent


def _deps(project):
    return (project["artifacts"], project["context"], project["src"],
            project["tests"])


def test_planner_produces_three_artifacts(project):
    project["state"].create_run("001")
    result = PlannerAgent(*_deps(project)).run("001")
    assert set(result.artifacts) == {"idea.md", "spec.md", "tasks.md"}


def test_coder_writes_source(project):
    project["state"].create_run("001")
    PlannerAgent(*_deps(project)).run("001")
    result = CoderAgent(*_deps(project)).run("001")
    assert "implementation.md" in result.artifacts
    assert (project["src"] / "reconcile.py").exists()


def test_tester_approves_after_valid_implementation(project):
    project["state"].create_run("001")
    PlannerAgent(*_deps(project)).run("001")
    CoderAgent(*_deps(project)).run("001")
    result = TesterAgent(*_deps(project)).run("001")
    assert result.approved is True
    assert (project["tests"] / "test_reconcile.py").exists()


def test_tester_rejects_without_implementation(project):
    project["state"].create_run("001")
    PlannerAgent(*_deps(project)).run("001")  # spec exists, but no code
    result = TesterAgent(*_deps(project)).run("001")
    assert result.approved is False


def test_reviewer_is_read_only(project):
    reviewer = ReviewerAgent(*_deps(project))
    with pytest.raises(PermissionError):
        reviewer._write_source("hack.py", "boom")
    with pytest.raises(PermissionError):
        reviewer._write_test("hack.py", "boom")


def test_reviewer_approves_complete_run(project):
    project["state"].create_run("001")
    PlannerAgent(*_deps(project)).run("001")
    CoderAgent(*_deps(project)).run("001")
    TesterAgent(*_deps(project)).run("001")
    result = ReviewerAgent(*_deps(project)).run("001")
    assert result.approved is True
