"""GitHub-native publishing for the pipeline.

This is the ONLY component that knows about git and GitHub. Agents stay pure —
the orchestrator calls this service at stage boundaries to map the file-based
workflow onto a real PR:

    run/<id> branch  →  Coder opens PR  →  Tester posts a status check
    →  Reviewer posts a PR review (APPROVE / REQUEST_CHANGES)  →  merge on both

Every action is recorded in ``self.calls`` (a human-readable log). When
``live=False`` (the default) the service is a **dry run**: it records the exact
git/gh commands it *would* run and performs no side effects.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

# Credential helper so HTTPS pushes use the active `gh` account's token.
_GH_CRED = ["-c", "credential.helper=!gh auth git-credential"]


class GitHubService:
    def __init__(
        self,
        repo: str,
        project_root: Path,
        *,
        live: bool = False,
        base_branch: str = "main",
        runner: Callable[[Sequence[str]], str] | None = None,
    ) -> None:
        self.repo = repo
        self.root = Path(project_root)
        self.live = live
        self.base_branch = base_branch
        self.calls: list[str] = []
        self._runner = runner or self._default_runner

    # ---- execution ------------------------------------------------------ #
    def _default_runner(self, cmd: Sequence[str]) -> str:
        result = subprocess.run(
            list(cmd),
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    def _exec(self, cmd: Sequence[str], *, stub: str = "") -> str:
        """Record the command; run it only when live."""
        self.calls.append(" ".join(cmd))
        if not self.live:
            return stub
        return self._runner(cmd)

    # ---- git ------------------------------------------------------------ #
    def run_branch(self, run_id: str) -> str:
        return f"run/{run_id}"

    def ensure_run_branch(self, run_id: str) -> str:
        branch = self.run_branch(run_id)
        # -B creates or resets the branch at the current HEAD.
        self._exec(["git", "checkout", "-B", branch])
        return branch

    def commit_paths(self, paths: Sequence[str], message: str) -> str:
        self._exec(["git", "add", *paths])
        self._exec(["git", "commit", "-m", message], stub="DRYRUN_SHA")
        return self._exec(["git", "rev-parse", "HEAD"], stub="DRYRUN_SHA")

    def push(self, branch: str) -> None:
        self._exec(["git", *_GH_CRED, "push", "-u", "origin", branch])

    # ---- github (gh CLI) ------------------------------------------------ #
    def open_pr(self, branch: str, title: str, body: str) -> tuple[int, str]:
        url = self._exec(
            [
                "gh", "pr", "create",
                "--repo", self.repo,
                "--head", branch,
                "--base", self.base_branch,
                "--title", title,
                "--body", body,
            ],
            stub=f"https://github.com/{self.repo}/pull/0",
        )
        number = self._pr_number_from_url(url)
        return number, url

    def post_status(
        self, sha: str, state: str, context: str, description: str
    ) -> None:
        """Post a commit status check (Statuses API — needs only `repo` scope)."""
        self._exec(
            [
                "gh", "api", "--method", "POST",
                f"repos/{self.repo}/statuses/{sha}",
                "-f", f"state={state}",            # success | failure | pending
                "-f", f"context={context}",
                "-f", f"description={description[:140]}",
            ]
        )

    def post_review(self, pr_number: int, event: str, body: str) -> None:
        """Post a PR review. event ∈ {APPROVE, REQUEST_CHANGES, COMMENT}."""
        self._exec(
            [
                "gh", "api", "--method", "POST",
                f"repos/{self.repo}/pulls/{pr_number}/reviews",
                "-f", f"event={event}",
                "-f", f"body={body}",
            ]
        )

    def merge_pr(self, pr_number: int) -> None:
        self._exec(
            [
                "gh", "pr", "merge", str(pr_number),
                "--repo", self.repo,
                "--squash", "--delete-branch",
            ]
        )

    # ---- helpers -------------------------------------------------------- #
    @staticmethod
    def _pr_number_from_url(url: str) -> int:
        try:
            return int(url.rstrip("/").rsplit("/", 1)[-1])
        except (ValueError, IndexError):
            return 0
