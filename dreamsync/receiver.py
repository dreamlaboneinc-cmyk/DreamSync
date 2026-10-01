from __future__ import annotations

from pathlib import Path
import re
import subprocess

from .deployment import deploy_exact


_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def receive_exact(root: str | Path, sha: str) -> dict:
    root = Path(root).resolve()

    if not _SHA_RE.fullmatch(sha):
        raise RuntimeError("invalid deployment SHA")

    status = _git(root, "status", "--porcelain")
    dirty=[]
    for line in status.splitlines():
        rel=line[3:].replace("\\", "/") if len(line)>3 else ""
        if rel==".env" or rel.startswith(("data/","state/","backups/","backup/","venv/",".venv/","__pycache__/")):
            continue
        dirty.append(line)
    if dirty:
        raise RuntimeError("server worktree must be clean before deployment")

    _git(root, "fetch", "origin", "main")

    remote_sha = _git(root, "rev-parse", "origin/main")

    if remote_sha != sha:
        raise RuntimeError(
            "requested SHA does not match GitHub origin/main"
        )

    previous_sha = _git(root, "rev-parse", "HEAD")

    # SAFETY: deployments are forward-only. Never silently rewind or
    # replace a running application's verified Git history.
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", previous_sha, sha],
        cwd=root, text=True, capture_output=True,
    )
    if ancestry.returncode != 0:
        raise RuntimeError(
            f"refusing non-forward deployment: current {previous_sha[:12]} -> requested {sha[:12]}"
        )

    try:
        _git(root, "reset", "--hard", sha)
        result = deploy_exact(root, sha)
    except Exception:
        _git(root, "reset", "--hard", previous_sha)
        raise

    return result
