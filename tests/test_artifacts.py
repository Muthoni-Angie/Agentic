"""Artifact models are strongly typed, serializable and render to Markdown."""

from models.artifact import (
    DefectArtifact,
    FeedbackArtifact,
    FeedbackItem,
    IdeaArtifact,
    SpecArtifact,
    Task,
    TaskArtifact,
)


def test_idea_renders_markdown():
    idea = IdeaArtifact(
        run_id="001", created_by="planner", name="X", pitch="p",
        problem="prob", target_market="mkt", revenue_streams=["a", "b"],
    )
    md = idea.to_markdown()
    assert "# Idea" in md and "## X" in md and "- a" in md


def test_artifact_roundtrip_serialization():
    spec = SpecArtifact(
        run_id="001", created_by="planner", overview="o",
        architecture="arch", requirements=["r1"],
    )
    restored = SpecArtifact.model_validate_json(spec.model_dump_json())
    assert restored.requirements == ["r1"]
    assert restored.filename == "spec.md"


def test_task_checkbox_state():
    art = TaskArtifact(
        run_id="001", created_by="planner",
        tasks=[Task(id="T1", title="do", done=True)],
    )
    assert "- [x] **T1**" in art.to_markdown()


def test_defect_blocker_detection():
    from models.artifact import Defect

    art = DefectArtifact(
        run_id="001", created_by="tester",
        defects=[Defect(id="D1", severity="blocker", summary="boom")],
    )
    assert art.has_blockers is True


def test_feedback_verdict_in_markdown():
    fb = FeedbackArtifact(
        run_id="001", created_by="reviewer", approved=True,
        items=[FeedbackItem(severity="suggestion", message="nit")],
    )
    assert "APPROVED" in fb.to_markdown()
    assert fb.has_blockers is False
