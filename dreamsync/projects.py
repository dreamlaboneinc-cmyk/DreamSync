from __future__ import annotations

from pathlib import Path
import subprocess
import yaml

from .discovery import write_discovery


def _safe_name(name: str) -> str:
    if not name or any(c in name for c in '<>:"/\\|?*'):
        raise RuntimeError("invalid project name")
    return name.strip()


def _protocol(root: Path, name: str, discovery: dict) -> None:
    ds = root / ".dreamsync"
    ds.mkdir(parents=True, exist_ok=True)
    project = {
        "version": 1,
        "project": {"name": name, "branch": "main", "type": discovery["primary_type"]},
        "mode": "AUTONOMOUS",
        "ai": {"provider": "dream-api", "billing_mode_required": "FREE_ONLY"},
        "verification": {"forbidden_tracked": [".env", "venv", ".venv"]},
        "protected_paths": [".env", "data", "state", ".git", "backups"],
    }
    (ds / "project.yml").write_text(yaml.safe_dump(project, sort_keys=False))
    (root / "BUILD.md").write_text(
        f"# {name} Build Contract\n\n## Goal\nDescribe the intended app or change.\n\n"
        "## Requirements\n- Define required behavior.\n\n## Acceptance Criteria\n"
        "- Define observable proof that the mission is complete.\n"
    )
    (root / "DECISIONS.md").write_text(
        "# Project Decisions\n\nRecord durable decisions that future chats and agents must preserve.\n"
    )
    (root / "ARCHITECTURE.md").write_text(
        f"# Architecture\n\nDetected project type: **{discovery['primary_type']}**.\n\n"
        "This file is refined as DreamSync learns the project.\n"
    )


def new_project(workspace: str | Path, name: str) -> dict:
    name = _safe_name(name)
    root = Path(workspace).resolve() / name
    if root.exists() and any(root.iterdir()):
        raise RuntimeError("project directory already exists and is not empty")
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
    discovery = write_discovery(root)
    _protocol(root, name, discovery)
    return {"ok": True, "action": "new", "root": str(root), "discovery": discovery}


def adopt_project(root: str | Path) -> dict:
    root = Path(root).resolve()
    if not root.is_dir():
        raise RuntimeError("project directory does not exist")
    discovery = write_discovery(root)
    name = root.name
    ds = root / ".dreamsync"
    if not (ds / "project.yml").exists():
        _protocol(root, name, discovery)
    else:
        for filename, text in {
            "BUILD.md": f"# {name} Build Contract\n\n## Goal\nDocument the existing app and next mission.\n",
            "DECISIONS.md": "# Project Decisions\n\n",
            "ARCHITECTURE.md": f"# Architecture\n\nDetected project type: **{discovery['primary_type']}**.\n",
        }.items():
            p = root / filename
            if not p.exists():
                p.write_text(text)
    return {"ok": True, "action": "adopt", "root": str(root), "discovery": discovery}
