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
from services.github_service import GitHubService
from services.state_service import StateService

from orchestrator.orchestrator import Orchestrator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO = "Muthoni-Angie/Agentic"


def build_orchestrator(
    project_root: Path = PROJECT_ROOT,
    github: GitHubService | None = None,
) -> Orchestrator:
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
        github=github,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Agentic pipeline.")
    parser.add_argument("--run", dest="run_id", default=None,
                        help="existing run id to resume")
    parser.add_argument("--github", action="store_true",
                        help="drive the run through a GitHub PR (branch, PR, "
                             "status check, review, merge)")
    parser.add_argument("--live", action="store_true",
                        help="actually perform git/GitHub actions; without it "
                             "--github only logs the commands it would run")
    parser.add_argument("--repo", default=DEFAULT_REPO,
                        help=f"target GitHub repo (default: {DEFAULT_REPO})")
    args = parser.parse_args()

    github = None
    if args.github:
        github = GitHubService(args.repo, PROJECT_ROOT, live=args.live)

    orchestrator = build_orchestrator(github=github)
    state = orchestrator.run(args.run_id)

    print(f"\nRun {state.run_id} finished in stage: {state.stage.value}")
    print(f"  tester_approved={state.tester_approved} "
          f"reviewer_approved={state.reviewer_approved} "
          f"iterations={state.iteration}")
    if state.pr_url:
        print(f"  PR: {state.pr_url}")
    for log in orchestrator.logs:
        for msg in log.result.messages:
            print(f"  [{log.stage.value:<9}] {log.agent}: {msg}")

    if github:
        mode = "LIVE" if args.live else "DRY-RUN (no side effects)"
        print(f"\nGitHub actions [{mode}]:")
        for call in github.calls:
            print(f"  $ {call}")


if __name__ == "__main__":
    main()
