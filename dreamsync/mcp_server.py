from __future__ import annotations

import os
from pathlib import Path

from mcp.server import MCPServer

from .config import load_project
from .deployment import deploy_exact
from .discovery import write_discovery
from .projects import adopt_project, new_project
from .promotion import promote
from .verify import verify
from .workflow import run

mcp = MCPServer(
    "DreamSync",
    description="Verified autonomous engineering tools for Cursor Agent.",
)


def _root(root: str = "") -> Path:
    value = root or os.environ.get("DREAMSYNC_WORKSPACE", "")
    if not value:
        raise RuntimeError("workspace root is required")
    return Path(value).resolve()


@mcp.tool()
def discover_project(root: str = "") -> dict:
    """Discover an existing repository without changing its source code."""
    return write_discovery(_root(root))
@mcp.tool()
def adopt_project_tool(root: str = "") -> dict:
    """Add DreamSync project protocol files to an existing repository."""
    return adopt_project(_root(root))


@mcp.tool()
def verify_project(root: str = "") -> dict:
    """Run deterministic configured verification. VERIFIED only when all gates pass."""
    return verify(_root(root))


@mcp.tool()
def plan_project(request: str, root: str = "") -> dict:
    """Create or update BUILD.md using DreamSync FREE_ONLY reasoning."""
    from .planning import create_plan
    return create_plan(_root(root), request)


@mcp.tool()
def project_status(root: str = "") -> dict:
    """Return deterministic verification for the current project."""
    return verify(_root(root))


@mcp.tool()
def run_mission(kind: str, request: str, root: str = "") -> dict:
    """Run a bounded DreamSync BUILD, DEBUG, or UPGRADE autonomous mission."""
    if kind not in {"build", "debug", "upgrade"}:
        raise RuntimeError("kind must be build, debug, or upgrade")
    return run(_root(root), kind, request)


@mcp.tool()
def create_project(name: str, workspace: str = "") -> dict:
    """Create a new Git repository with the DreamSync project protocol."""
    base = Path(workspace or os.environ.get("DREAMSYNC_WORKSPACE", "")).resolve()
    return new_project(base, name)
@mcp.tool()
def finish_verified(message: str, root: str = "") -> dict:
    """Verify, commit, push, exact-SHA deploy, and health-check a configured project."""
    project_root = _root(root)
    checked = verify(project_root)
    if not checked["verified"]:
        return {"ok": False, "phase": "BLOCKED", "verification": checked}
    release = promote(project_root, message, True)
    cfg = load_project(project_root)
    sha = release["sha"]
    if cfg.controller.get("ssh_target"):
        from .controller import remote_deploy
        deployed = remote_deploy(project_root, sha)
    else:
        deployed = deploy_exact(project_root, sha)
    return {
        "ok": bool(deployed["ok"]),
        "phase": "COMPLETE" if deployed["ok"] else "BLOCKED",
        "release": release,
        "deploy": deployed,
    }


if __name__ == "__main__":
    mcp.run()
