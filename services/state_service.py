"""Persists and mutates run state via ``.pipeline/<run_id>/status.json``."""

from __future__ import annotations

import json
from pathlib import Path

from models.run_state import RunState, Stage


class StateService:
    def __init__(self, pipeline_root: Path) -> None:
        self.pipeline_root = Path(pipeline_root)
        self.pipeline_root.mkdir(parents=True, exist_ok=True)

    def _status_path(self, run_id: str) -> Path:
        run_dir = self.pipeline_root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir / "status.json"

    def next_run_id(self) -> str:
        existing = [
            int(p.name)
            for p in self.pipeline_root.iterdir()
            if p.is_dir() and p.name.isdigit()
        ]
        return f"{(max(existing) + 1) if existing else 1:03d}"

    def create_run(self, run_id: str | None = None) -> RunState:
        run_id = run_id or self.next_run_id()
        state = RunState(run_id=run_id, stage=Stage.PLANNING)
        self.save(state)
        return state

    def load(self, run_id: str) -> RunState | None:
        path = self._status_path(run_id)
        if not path.exists():
            return None
        return RunState.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, state: RunState) -> Path:
        path = self._status_path(state.run_id)
        path.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        return path
