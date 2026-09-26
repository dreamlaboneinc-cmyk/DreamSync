from __future__ import annotations

from pathlib import Path
import re
import shlex
import subprocess
import base64

from .config import load_project


_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_SSH_TARGET_RE = re.compile(r"^[A-Za-z0-9_.@-]+$")
_REMOTE_PATH_RE = re.compile(r"^/[A-Za-z0-9_./-]+$")


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()



def remote_ai_complete(root: str | Path, prompt: str) -> str:
    """Run Dream API inference on the trusted Linode without exporting its credential."""
    cfg = load_project(root)
    controller = cfg.controller
    ssh_target = controller.get("ssh_target")
    if not ssh_target or not _SSH_TARGET_RE.fullmatch(ssh_target):
        raise RuntimeError("valid SSH target required for remote AI")
    runtime_root = controller.get("dreamsync_runtime", "/root/apps/DreamSync")
    if not _REMOTE_PATH_RE.fullmatch(runtime_root):
        raise RuntimeError("invalid DreamSync runtime path")
    command = f"cd {runtime_root} && PYTHONPATH={runtime_root} {runtime_root}/venv/bin/python -m dreamsync.cli ai-relay --root {runtime_root}"
    result = subprocess.run(
        [controller.get("ssh_executable", "ssh"), ssh_target, command],
        input=prompt, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=180
    )
    if result.returncode != 0:
        raise RuntimeError("remote FREE_ONLY AI failed: " + (result.stderr.strip() or "unknown error"))
    return result.stdout.strip()

def remote_deploy(root: str | Path = ".", sha: str | None = None) -> dict:
    cfg = load_project(root)
    root = cfg.root
    controller = cfg.controller

    ssh_target = controller.get("ssh_target")
    remote_project = controller.get("remote_project")

    if not ssh_target or not remote_project:
        raise RuntimeError("local controller configuration is incomplete")
    if not _SSH_TARGET_RE.fullmatch(ssh_target):
        raise RuntimeError("invalid SSH target")
    if not _REMOTE_PATH_RE.fullmatch(remote_project):
        raise RuntimeError("invalid remote project path")

    status = _git(root, "status", "--porcelain")
    dirty = []
    for line in status.splitlines():
        rel = line[3:].replace("\\", "/") if len(line) > 3 else ""
        if rel == ".env" or rel.startswith(("data/","state/","backups/","backup/","venv/",".venv/","__pycache__/")):
            continue
        dirty.append(line)
    if dirty:
        raise RuntimeError("local worktree must be clean before deployment")

    requested_sha = sha or _git(root, "rev-parse", "HEAD")
    if not _SHA_RE.fullmatch(requested_sha):
        raise RuntimeError("invalid deployment SHA")

    remote_sha = _git(root, "ls-remote", "origin", "refs/heads/main").split()[0]
    if remote_sha != requested_sha:
        raise RuntimeError(
            "deployment blocked: local HEAD does not match GitHub main"
        )

    project = shlex.quote(remote_project)
    runtime_root = controller.get("dreamsync_runtime", "/root/apps/DreamSync")
    if not _REMOTE_PATH_RE.fullmatch(runtime_root):
        raise RuntimeError("invalid DreamSync runtime path")
    python = shlex.quote(f"{runtime_root}/venv/bin/python")
    pythonpath = shlex.quote(runtime_root)
    command = (
        f"cd {project} && "
        f"PYTHONPATH={pythonpath} {python} -m dreamsync.cli "
        f"deploy-receive --sha {requested_sha}"
    )

    result = subprocess.run(
        [controller.get("ssh_executable", "ssh"), ssh_target, command],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "remote deployment failed: "
            + (result.stderr.strip() or result.stdout.strip())
        )

    return {
        "ok": True,
        "sha": requested_sha,
        "ssh_target": ssh_target,
        "remote_project": remote_project,
        "remote_output": result.stdout.strip(),
    }
