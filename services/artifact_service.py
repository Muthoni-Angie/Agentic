"""Reads and writes pipeline artifacts under ``.pipeline/<run_id>/``.

This is the only component that touches the artifact filesystem. Both a typed
JSON sidecar and a rendered Markdown file are written for every artifact so the
UI can show prose while downstream agents consume strong types.
"""

from __future__ import annotations

import json
from pathlib import Path

from models.artifact import BaseArtifact


class ArtifactService:
    def __init__(self, pipeline_root: Path) -> None:
        self.pipeline_root = Path(pipeline_root)
        self.pipeline_root.mkdir(parents=True, exist_ok=True)

    # ---- paths ---------------------------------------------------------- #
    def run_dir(self, run_id: str) -> Path:
        path = self.pipeline_root / run_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _json_path(self, run_id: str, filename: str) -> Path:
        return self.run_dir(run_id) / f"{Path(filename).stem}.json"

    # ---- raw markdown --------------------------------------------------- #
    def write_markdown(self, run_id: str, filename: str, content: str) -> Path:
        path = self.run_dir(run_id) / filename
        path.write_text(content, encoding="utf-8")
        return path

    def read_markdown(self, run_id: str, filename: str) -> str | None:
        path = self.run_dir(run_id) / filename
        return path.read_text(encoding="utf-8") if path.exists() else None

    # ---- typed artifacts ------------------------------------------------ #
    def write_artifact(self, artifact: BaseArtifact) -> Path:
        """Persist Markdown + JSON sidecar; return the Markdown path."""
        md_path = self.write_markdown(
            artifact.run_id, artifact.filename, artifact.to_markdown()
        )
        json_path = self._json_path(artifact.run_id, artifact.filename)
        json_path.write_text(
            artifact.model_dump_json(indent=2), encoding="utf-8"
        )
        return md_path

    def read_artifact(self, run_id: str, model: type[BaseArtifact]):
        """Re-hydrate a typed artifact from its JSON sidecar, or None."""
        json_path = self._json_path(run_id, model.filename)
        if not json_path.exists():
            return None
        data = json.loads(json_path.read_text(encoding="utf-8"))
        return model.model_validate(data)

    def list_artifacts(self, run_id: str) -> list[str]:
        run = self.run_dir(run_id)
        return sorted(
            p.name
            for p in run.glob("*.md")
        )

    def list_runs(self) -> list[str]:
        return sorted(
            p.name for p in self.pipeline_root.iterdir() if p.is_dir()
        )
