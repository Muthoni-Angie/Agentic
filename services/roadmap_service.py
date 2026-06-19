"""Persistent product roadmap — the agents' memory across runs.

State (which features are done) lives in a single ``roadmap.json`` at the repo
root, so it survives between runs and, in GitHub mode, advances only when a PR
is merged. ``current_feature()`` is the single source of truth every agent in a
run consults, so they all build the same feature without talking directly.
"""

from __future__ import annotations

import json
from pathlib import Path

from product.backlog import PRODUCT_NAME, PRODUCT_PITCH, Feature


class RoadmapService:
    def __init__(self, state_path: Path, backlog: list[Feature]) -> None:
        self.state_path = Path(state_path)
        self.backlog = backlog

    def _done(self) -> list[str]:
        if self.state_path.exists():
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            return list(data.get("done", []))
        return []

    def current_feature(self) -> Feature | None:
        """The first not-yet-built feature, or None when the backlog is done."""
        done = set(self._done())
        return next((f for f in self.backlog if f.id not in done), None)

    def mark_done(self, feature_id: str) -> None:
        done = self._done()
        if feature_id not in done:
            done.append(feature_id)
        self.state_path.write_text(
            json.dumps({"done": done}, indent=2), encoding="utf-8"
        )

    def is_complete(self) -> bool:
        return self.current_feature() is None

    def render_markdown(self, current_id: str | None = None) -> str:
        done = set(self._done())
        lines = [
            f"# {PRODUCT_NAME} Roadmap",
            "",
            f"> {PRODUCT_PITCH}",
            "",
            "## Backlog",
            "",
        ]
        for f in self.backlog:
            box = "x" if f.id in done else " "
            marker = "  ⬅ **building now**" if f.id == current_id else ""
            lines.append(f"- [{box}] **{f.id}** — {f.title}{marker}")
        n_done = len(done & {f.id for f in self.backlog})
        lines += ["", f"_Progress: {n_done}/{len(self.backlog)} features shipped._"]
        return "\n".join(lines) + "\n"
