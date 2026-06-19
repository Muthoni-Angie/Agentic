"""The orchestrator — the only authority over the state machine.

It creates run folders, runs agents sequentially, persists ``status.json`` after
every step, handles the rejection loop (Tester/Reviewer can send work back to the
Coder), and stops ONLY when both the Tester and the Reviewer approve.

Agents are injected, never imported by stage — this keeps the orchestrator open
for extension (Architect, Security Auditor, …) without modification.

When an optional :class:`GitHubService` is injected, the same workflow is mapped
onto a real PR: a ``run/<id>`` branch, the Coder opens the PR, the Tester posts a
status check, the Reviewer posts a PR review, and the PR is merged on approval.
Agents remain pure — only the orchestrator talks to the GitHubService.
"""

from __future__ import annotations

from dataclasses import dataclass

from agents.base.base_agent import BaseAgent
from models.agent_result import AgentResult
from models.run_state import RunState, Stage
from services.github_service import GitHubService
from services.state_service import StateService


@dataclass
class StepLog:
    iteration: int
    stage: Stage
    agent: str
    result: AgentResult


class Orchestrator:
    def __init__(
        self,
        state_service: StateService,
        planner: BaseAgent,
        coder: BaseAgent,
        tester: BaseAgent,
        reviewer: BaseAgent,
        max_iterations: int = 5,
        github: GitHubService | None = None,
    ) -> None:
        self.state = state_service
        self.planner = planner
        self.coder = coder
        self.tester = tester
        self.reviewer = reviewer
        self.max_iterations = max_iterations
        self.github = github

    def start(self, run_id: str | None = None) -> RunState:
        return self.state.create_run(run_id)

    def run(self, run_id: str | None = None) -> RunState:
        state = self.state.load(run_id) if run_id else None
        if state is None:
            state = self.start(run_id)

        self.logs: list[StepLog] = []

        if self.github and state.branch is None:
            state.branch = self.github.ensure_run_branch(state.run_id)
            self.state.save(state)

        while state.stage != Stage.DONE:
            if state.iteration > self.max_iterations:
                state.record_transition(state.stage, "orchestrator",
                                        "max iterations reached; halting")
                self.state.save(state)
                break

            if state.stage == Stage.PLANNING:
                self._step(state, self.planner)
                state.planner_complete = True
                self._gh_planner(state)
                state.record_transition(Stage.CODING, self.planner.name)

            elif state.stage == Stage.CODING:
                self._step(state, self.coder)
                state.coder_complete = True
                self._gh_coder(state)
                state.record_transition(Stage.TESTING, self.coder.name)

            elif state.stage == Stage.TESTING:
                result = self._step(state, self.tester)
                state.tester_complete = True
                state.tester_approved = bool(result.approved)
                self._gh_tester(state, state.tester_approved)
                if state.tester_approved:
                    state.record_transition(Stage.REVIEWING, self.tester.name,
                                            "tests approved")
                else:
                    self._reject_to_coder(state, self.tester.name,
                                          "tester rejected work")

            elif state.stage == Stage.REVIEWING:
                result = self._step(state, self.reviewer)
                state.reviewer_complete = True
                state.reviewer_approved = bool(result.approved)
                self._gh_reviewer(state, state.reviewer_approved, result)
                if state.is_complete:
                    state.record_transition(Stage.DONE, self.reviewer.name,
                                            "tester + reviewer approved")
                    self.state.save(state)
                    self._gh_finalize_and_merge(state)
                else:
                    self._reject_to_coder(state, self.reviewer.name,
                                          "reviewer requested changes")

            self.state.save(state)

        return state

    # ---- internals ------------------------------------------------------ #
    def _step(self, state: RunState, agent: BaseAgent) -> AgentResult:
        result = agent.run(state.run_id)
        self.logs.append(
            StepLog(state.iteration, state.stage, agent.name, result)
        )
        self.state.save(state)
        return result

    def _reject_to_coder(self, state: RunState, agent: str, note: str) -> None:
        """Rejection loop: reset downstream approvals and go back to CODING."""
        state.iteration += 1
        state.tester_approved = False
        state.reviewer_approved = False
        state.coder_complete = False
        state.record_transition(Stage.CODING, agent, note)

    # ---- GitHub-native hooks (no-ops when self.github is None) ---------- #
    def _pipeline_dir(self, state: RunState) -> str:
        return f".pipeline/{state.run_id}"

    def _gh_planner(self, state: RunState) -> None:
        if not self.github:
            return
        self.state.save(state)  # persist current flags before committing them
        self.github.commit_paths(
            [self._pipeline_dir(state)],
            f"run {state.run_id}: planner artifacts (idea, spec, tasks)",
        )

    def _gh_coder(self, state: RunState) -> None:
        if not self.github:
            return
        self.state.save(state)
        gh = self.github
        gh.commit_paths(
            [self._pipeline_dir(state), "src"],
            f"run {state.run_id}: coder implementation",
        )
        gh.push(state.branch or gh.run_branch(state.run_id))
        if state.pr_number is None:
            number, url = gh.open_pr(
                state.branch or gh.run_branch(state.run_id),
                f"run/{state.run_id}: autonomous pipeline",
                self._pr_body(state),
            )
            state.pr_number = number
            state.pr_url = url

    def _gh_tester(self, state: RunState, approved: bool) -> None:
        if not self.github:
            return
        self.state.save(state)
        gh = self.github
        sha = gh.commit_paths(
            [self._pipeline_dir(state), "tests"],
            f"run {state.run_id}: tester tests + report",
        )
        gh.push(state.branch or gh.run_branch(state.run_id))
        gh.post_status(
            sha,
            "success" if approved else "failure",
            "agentic/tester",
            "tests passed" if approved else "defects found — changes requested",
        )

    def _gh_reviewer(
        self, state: RunState, approved: bool, result: AgentResult
    ) -> None:
        if not self.github or state.pr_number is None:
            return
        self.state.save(state)
        gh = self.github
        sha = gh.commit_paths(
            [self._pipeline_dir(state)],
            f"run {state.run_id}: reviewer review + feedback",
        )
        gh.push(state.branch or gh.run_branch(state.run_id))
        # The reviewer's machine-readable gate is a status check (the merge
        # condition), mirroring the tester. A single account cannot formally
        # APPROVE its own PR, so the verdict is also posted as a COMMENT review.
        gh.post_status(
            sha,
            "success" if approved else "failure",
            "agentic/reviewer",
            "approved" if approved else "changes requested",
        )
        verdict = "✅ APPROVED" if approved else "🔁 CHANGES REQUESTED"
        body = verdict + "\n\n" + ("\n".join(result.messages) or "Automated review.")
        gh.post_review(state.pr_number, "COMMENT", body)

    def _gh_finalize_and_merge(self, state: RunState) -> None:
        if not self.github:
            return
        gh = self.github
        # Commit the FINAL status.json (now DONE) onto the branch before merging,
        # so the merged history reflects the completed run — not the mid-flight
        # REVIEWING snapshot captured during the reviewer's commit.
        gh.commit_paths(
            [f"{self._pipeline_dir(state)}/status.json"],
            f"run {state.run_id}: finalize (DONE)",
        )
        gh.push(state.branch or gh.run_branch(state.run_id))
        if state.pr_number is not None:
            gh.merge_pr(state.pr_number)

    def _pr_body(self, state: RunState) -> str:
        lines = [
            f"Autonomous pipeline run **{state.run_id}**.",
            "",
            f"Artifacts live in `.pipeline/{state.run_id}/`. "
            "Each commit on this branch is one agent's handoff.",
            "",
            "### Agent log",
        ]
        for log in self.logs:
            for msg in log.result.messages:
                lines.append(f"- **{log.agent}** ({log.stage.value}): {msg}")
        lines += [
            "",
            "🤖 Generated with [Claude Code](https://claude.com/claude-code)",
        ]
        return "\n".join(lines)
