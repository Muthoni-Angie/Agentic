"""The orchestrator drives the state machine and the rejection loop correctly."""

from models.run_state import Stage


def test_full_run_reaches_done(orchestrator):
    state = orchestrator.run()
    assert state.stage == Stage.DONE
    assert state.tester_approved and state.reviewer_approved
    assert state.is_complete


def test_status_json_persisted(orchestrator, project):
    state = orchestrator.run()
    loaded = project["state"].load(state.run_id)
    assert loaded is not None
    assert loaded.stage == Stage.DONE


def test_history_records_transitions(orchestrator):
    state = orchestrator.run()
    stages = [r.to_stage for r in state.history]
    assert Stage.CODING in stages
    assert Stage.TESTING in stages
    assert Stage.REVIEWING in stages
    assert state.history[-1].to_stage == Stage.DONE


def test_rejection_loop_routes_back_to_coder(orchestrator, project):
    """A rejecting tester must send the run back to CODING and bump iteration."""

    class RejectingTester:
        name = "tester"

        def run(self, run_id):
            from models.agent_result import AgentResult
            return AgentResult(agent="tester", approved=False,
                               messages=["forced rejection"])

    # Patch in a tester that always rejects, then ensure we loop and halt.
    orchestrator.tester = RejectingTester()
    orchestrator.max_iterations = 2
    state = orchestrator.run()

    assert state.iteration >= 1
    # Never approved -> never DONE; orchestrator halts at max iterations.
    assert state.stage != Stage.DONE
    assert any(r.to_stage == Stage.CODING and r.iteration >= 0
               for r in state.history)


def test_pipeline_only_done_when_both_approve(orchestrator):
    class RejectingReviewer:
        name = "reviewer"

        def run(self, run_id):
            from models.agent_result import AgentResult
            return AgentResult(agent="reviewer", approved=False,
                               messages=["changes requested"])

    orchestrator.reviewer = RejectingReviewer()
    orchestrator.max_iterations = 2
    state = orchestrator.run()

    assert not state.reviewer_approved
    assert state.stage != Stage.DONE
