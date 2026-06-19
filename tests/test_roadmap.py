"""Roadmap-driven incremental build: the product grows feature by feature."""

from agents.coder.agent import CoderAgent
from agents.planner.agent import PlannerAgent
from agents.reviewer.agent import ReviewerAgent
from agents.tester.agent import TesterAgent
from models.run_state import Stage
from orchestrator.orchestrator import Orchestrator
from product.backlog import BACKLOG
from services.roadmap_service import RoadmapService


def _roadmap(project):
    return RoadmapService(project["root"] / "roadmap.json", BACKLOG)


def _orchestrator(project, roadmap):
    deps = (project["artifacts"], project["context"], project["src"],
            project["tests"], roadmap)
    return Orchestrator(
        state_service=project["state"],
        planner=PlannerAgent(*deps),
        coder=CoderAgent(*deps),
        tester=TesterAgent(*deps),
        reviewer=ReviewerAgent(*deps),
        roadmap=roadmap,
    )


def test_roadmap_picks_first_then_advances(project):
    rm = _roadmap(project)
    assert rm.current_feature().id == "F1"
    rm.mark_done("F1")
    assert rm.current_feature().id == "F2"


def test_render_marks_done_and_current(project):
    rm = _roadmap(project)
    rm.mark_done("F1")
    md = rm.render_markdown(current_id="F2")
    assert "- [x] **F1**" in md
    assert "building now" in md and "F2" in md


def test_run_builds_current_feature_and_advances(project):
    rm = _roadmap(project)
    state = _orchestrator(project, rm).run()

    assert state.stage == Stage.DONE
    # F1 wrote the package + models on disk...
    assert (project["src"] / "ledgerloop" / "models.py").exists()
    assert (project["tests"] / "test_ledgerloop_models.py").exists()
    # ...and the roadmap advanced to F2.
    assert rm.current_feature().id == "F2"
    assert "roadmap.md" in project["artifacts"].list_artifacts("001")


def test_two_runs_build_two_features(project):
    rm = _roadmap(project)
    orch = _orchestrator(project, rm)
    orch.run()  # F1
    orch.run()  # F2

    assert (project["src"] / "ledgerloop" / "models.py").exists()
    assert (project["src"] / "ledgerloop" / "matcher.py").exists()
    assert rm.current_feature().id == "F3"


def test_spec_reflects_the_chosen_feature(project):
    rm = _roadmap(project)
    _orchestrator(project, rm).run()
    spec = project["artifacts"].read_markdown("001", "spec.md")
    assert "F1" in spec and "Domain models" in spec
