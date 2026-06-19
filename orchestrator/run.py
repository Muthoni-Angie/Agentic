"""CLI entrypoint — wires dependencies and runs a pipeline.

Usage:
    python -m orchestrator.run            # start a new run
    python -m orchestrator.run --run 001  # resume/replay a specific run
"""

from __future__ import annotations

import argparse
from pathlib import Path

from agents.coder.agent import CoderAgent
from agents.planner.agent import PlannerAgent
from agents.reviewer.agent import ReviewerAgent
from agents.tester.agent import TesterAgent
from services.artifact_service import ArtifactService
from services.context_service import ContextService
from services.state_service import StateService

from orchestrator.orchestrator import Orchestrator

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def build_orchestrator(project_root: Path = PROJECT_ROOT) -> Orchestrator:
    """Composition root — the single place dependencies are wired."""
    pipeline_root = project_root / ".pipeline"
    src_dir = project_root / "src"
    tests_dir = project_root / "tests"

    artifact_service = ArtifactService(pipeline_root)
    state_service = StateService(pipeline_root)
    context_service = ContextService(
        artifact_service, state_service, project_root, src_dir
    )

    deps = (artifact_service, context_service, src_dir, tests_dir)
    return Orchestrator(
        state_service=state_service,
        planner=PlannerAgent(*deps),
        coder=CoderAgent(*deps),
        tester=TesterAgent(*deps),
        reviewer=ReviewerAgent(*deps),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Agentic pipeline.")
    parser.add_argument("--run", dest="run_id", default=None,
                        help="existing run id to resume")
    args = parser.parse_args()

    orchestrator = build_orchestrator()
    state = orchestrator.run(args.run_id)

    print(f"\nRun {state.run_id} finished in stage: {state.stage.value}")
    print(f"  tester_approved={state.tester_approved} "
          f"reviewer_approved={state.reviewer_approved} "
          f"iterations={state.iteration}")
    for log in orchestrator.logs:
        for msg in log.result.messages:
            print(f"  [{log.stage.value:<9}] {log.agent}: {msg}")


if __name__ == "__main__":
    main()
