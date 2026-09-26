from __future__ import annotations

from pathlib import Path
import json
import time

from .autonomous import run_autonomous
from .discovery import write_discovery
from .projects import adopt_project


MISSION_FILES = {
    "build": "BUILD.md",
    "debug": "BUILD.md",
    "upgrade": "BUILD.md",
}


def prepare(root: str | Path, mission: str, request: str) -> dict:
    root = Path(root).resolve()
    if mission not in MISSION_FILES:
        raise RuntimeError("unsupported mission type")

    adopt_project(root)
    discovery = write_discovery(root)
    mission_dir = root / ".dreamsync" / "missions"
    mission_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "type": mission,
        "request": request,
        "created": time.time(),
        "project_type": discovery["primary_type"],
        "status": "READY",
    }
    (mission_dir / "current.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def run(root: str | Path, mission: str, request: str) -> dict:
    root = Path(root).resolve()
    record = prepare(root, mission, request)
    objective = (
        f"{mission.upper()} mission. User request: {request}. "
        "Read BUILD.md, ARCHITECTURE.md, DECISIONS.md, .dreamsync/project.yml, "
        "and discovery evidence. Preserve existing behavior unless the mission "
        "explicitly changes it. Do not guess project-specific verification or "
        "deployment details; leave ambiguous infrastructure unchanged."
    )
    result = run_autonomous(root, objective, MISSION_FILES[mission])
    record["status"] = "VERIFIED" if result["ok"] else "BLOCKED"
    record["result_phase"] = result["phase"]
    (root / ".dreamsync" / "missions" / "current.json").write_text(
        json.dumps(record, indent=2) + "\n"
    )
    return result
