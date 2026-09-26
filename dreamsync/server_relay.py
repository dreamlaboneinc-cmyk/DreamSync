from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

from .receiver import receive_exact


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=True
    ).stdout.strip()


def sync_once(apps_root: str | Path = "/root/apps") -> list[dict]:
    apps = Path(apps_root)
    results: list[dict] = []
    for root in sorted(apps.iterdir()):
        if not root.is_dir() or not (root / ".git").exists():
            continue
        if root.name == "DreamSync_qualification":
            continue
        try:
            if _git(root, "status", "--porcelain"):
                results.append({"project": root.name, "status": "BLOCKED_DIRTY"})
                continue
            _git(root, "fetch", "origin", "main")
            head = _git(root, "rev-parse", "HEAD")
            remote = _git(root, "rev-parse", "origin/main")
            if head == remote:
                continue
            result = receive_exact(root, remote)
            results.append(
                {"project": root.name, "status": "DEPLOYED", "sha": remote, "ok": result["ok"]}
            )
        except Exception as exc:
            results.append({"project": root.name, "status": "ERROR", "error": str(exc)[:500]})
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apps-root", default="/root/apps")
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    while True:
        for result in sync_once(args.apps_root):
            print(result, flush=True)
        if args.once:
            return
        time.sleep(max(args.interval, 5))


if __name__ == "__main__":
    main()
