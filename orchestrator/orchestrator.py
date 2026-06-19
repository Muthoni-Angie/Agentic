"""The orchestrator — the only authority over the state machine.

It creates run folders, runs agents sequentially, persists ``status.json`` after
every step, handles the rejection loop (Tester/Reviewer can send work back to the
Coder), and stops ONLY when both the Tester and the Reviewer approve.

Agents are injected, never imported by stage — this keeps the orchestrator open
for extension (Architect, Security Auditor, …) without modification.
"""

from __future__ import annotations

from dataclasses import dataclass

from agents.base.base_agent import BaseAgent
from models.agent_result import AgentResult
from models.run_state import RunState, Stage
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
    ) -> None:
        self.state = state_service
        self.planner = planner
        self.coder = coder
        self.tester = tester
        self.reviewer = reviewer
        self.max_iterations = max_iterations

    def start(self, run_id: str | None = None) -> RunState:
        return self.state.create_run(run_id)

    def run(self, run_id: str | None = None) -> RunState:
        state = self.state.load(run_id) if run_id else None
        if state is None:
            state = self.start(run_id)

        self.logs: list[StepLog] = []

        while state.stage != Stage.DONE:
            if state.iteration > self.max_iterations:
                state.record_transition(state.stage, "orchestrator",
                                        "max iterations reached; halting")
                self.state.save(state)
                break

            if state.stage == Stage.PLANNING:
                self._step(state, self.planner)
                state.planner_complete = True
                state.record_transition(Stage.CODING, self.planner.name)

            elif state.stage == Stage.CODING:
                self._step(state, self.coder)
                state.coder_complete = True
                state.record_transition(Stage.TESTING, self.coder.name)

            elif state.stage == Stage.TESTING:
                result = self._step(state, self.tester)
                state.tester_complete = True
                state.tester_approved = bool(result.approved)
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
                if state.is_complete:
                    state.record_transition(Stage.DONE, self.reviewer.name,
                                            "tester + reviewer approved")
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
