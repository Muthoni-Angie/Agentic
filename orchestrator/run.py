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
from product.backlog import BACKLOG
from services.artifact_service import ArtifactService
from services.context_service import ContextService
from services.github_service import GitHubService
from services.roadmap_service import RoadmapService
from services.state_service import StateService

from orchestrator.orchestrator import Orchestrator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO = "Muthoni-Angie/Agentic"


def build_orchestrator(
    project_root: Path = PROJECT_ROOT,
    github: GitHubService | None = None,
    auto_merge: bool = True,
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
    roadmap = RoadmapService(project_root / "roadmap.json", BACKLOG)

    deps = (artifact_service, context_service, src_dir, tests_dir, roadmap)
    return Orchestrator(
        state_service=state_service,
        planner=PlannerAgent(*deps),
        coder=CoderAgent(*deps),
        tester=TesterAgent(*deps),
        reviewer=ReviewerAgent(*deps),
        github=github,
        auto_merge=auto_merge,
        roadmap=roadmap,
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
    parser.add_argument("--no-merge", action="store_true",
                        help="open/update the PR but do not merge it "
                             "(leave it for human review)")
    args = parser.parse_args()

    github = None
    if args.github:
        github = GitHubService(args.repo, PROJECT_ROOT, live=args.live)

    orchestrator = build_orchestrator(
        github=github, auto_merge=not args.no_merge
    )
    feature = orchestrator.roadmap.current_feature() if orchestrator.roadmap else None
    state = orchestrator.run(args.run_id)

    if feature:
        print(f"\nBuilt roadmap feature: {feature.id} — {feature.title}")
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
