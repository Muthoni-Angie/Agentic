"""GitHubService dry-run behaviour and the orchestrator's PR flow.

Everything here runs in dry-run (live=False): commands are recorded but never
executed, so the suite stays hermetic and never touches a real repo.
"""

import pytest

from agents.coder.agent import CoderAgent
from agents.planner.agent import PlannerAgent
from agents.reviewer.agent import ReviewerAgent
from agents.tester.agent import TesterAgent
from models.agent_result import AgentResult
from models.run_state import Stage
from orchestrator.orchestrator import Orchestrator
from services.github_service import GitHubService


def _boom(cmd):
    raise AssertionError(f"dry-run must not execute commands, got: {cmd}")


def test_dry_run_records_but_never_executes(tmp_path):
    gh = GitHubService("owner/repo", tmp_path, live=False, runner=_boom)
    branch = gh.ensure_run_branch("001")
    sha = gh.commit_paths([".pipeline/001"], "msg")
    gh.push(branch)
    number, url = gh.open_pr(branch, "title", "body")

    assert branch == "run/001"
    assert sha == "DRYRUN_SHA"
    assert number == 0 and url.endswith("/pull/0")
    assert any(c.startswith("git checkout -B run/001") for c in gh.calls)
    assert any("push -u origin run/001" in c for c in gh.calls)
    assert any(c.startswith("gh pr create") for c in gh.calls)


def test_status_and_review_command_shapes(tmp_path):
    gh = GitHubService("owner/repo", tmp_path, live=False, runner=_boom)
    gh.post_status("abc123", "success", "agentic/tester", "ok")
    gh.post_review(7, "APPROVE", "looks good")
    gh.merge_pr(7)

    joined = "\n".join(gh.calls)
    assert "repos/owner/repo/statuses/abc123" in joined
    assert "state=success" in joined
    assert "repos/owner/repo/pulls/7/reviews" in joined
    assert "event=APPROVE" in joined
    assert "gh pr merge 7 --repo owner/repo --squash --delete-branch" in joined


def _gh_orchestrator(project, github, **kwargs):
    deps = (project["artifacts"], project["context"], project["src"],
            project["tests"])
    return Orchestrator(
        state_service=project["state"],
        planner=PlannerAgent(*deps),
        coder=CoderAgent(*deps),
        tester=TesterAgent(*deps),
        reviewer=ReviewerAgent(*deps),
        github=github,
        **kwargs,
    )


def test_full_pr_flow_reaches_done_and_merges(project):
    gh = GitHubService("owner/repo", project["root"], live=False, runner=_boom)
    state = _gh_orchestrator(project, gh).run()

    assert state.stage == Stage.DONE
    assert state.branch == "run/001"
    assert state.pr_number == 0  # dry-run stub
    assert state.pr_url and "pull/0" in state.pr_url

    joined = "\n".join(gh.calls)
    # Branch created, PR opened, tester check green, reviewer approved, merged.
    assert "git checkout -B run/001" in joined
    assert "gh pr create" in joined
    assert "state=success" in joined
    assert "event=APPROVE" in joined
    assert "gh pr merge 0" in joined


def test_rejection_posts_failing_check_and_does_not_merge(project):
    class RejectingTester:
        name = "tester"

        def run(self, run_id):
            return AgentResult(agent="tester", approved=False,
                               messages=["forced rejection"])

    gh = GitHubService("owner/repo", project["root"], live=False, runner=_boom)
    orch = _gh_orchestrator(project, gh, max_iterations=1)
    orch.tester = RejectingTester()
    state = orch.run()

    joined = "\n".join(gh.calls)
    assert state.stage != Stage.DONE
    assert "state=failure" in joined        # tester posted a failing check
    assert "event=APPROVE" not in joined    # reviewer never approved
    assert "gh pr merge" not in joined       # nothing merged
