"""Service-layer behaviour: artifact IO, state persistence, run id allocation."""

from models.artifact import IdeaArtifact
from models.run_state import Stage


def test_artifact_service_writes_md_and_json(project):
    art = IdeaArtifact(
        run_id="001", created_by="planner", name="X", pitch="p",
        problem="q", target_market="m",
    )
    project["artifacts"].write_artifact(art)

    assert "idea.md" in project["artifacts"].list_artifacts("001")
    restored = project["artifacts"].read_artifact("001", IdeaArtifact)
    assert restored is not None and restored.name == "X"


def test_state_service_run_id_increments(project):
    s = project["state"]
    first = s.create_run()
    second = s.create_run()
    assert first.run_id == "001"
    assert second.run_id == "002"


def test_state_roundtrip(project):
    s = project["state"]
    state = s.create_run("042")
    state.stage = Stage.CODING
    state.coder_complete = True
    s.save(state)

    loaded = s.load("042")
    assert loaded is not None
    assert loaded.stage == Stage.CODING
    assert loaded.coder_complete is True


def test_context_includes_repo_tree(project):
    project["state"].create_run("001")
    (project["src"] / "a.py").write_text("x = 1\n", encoding="utf-8")
    ctx = project["context"].build("001")
    assert any(p.endswith("a.py") for p in ctx.repo_tree)
    assert any("a.py" in k for k in ctx.source_files)
