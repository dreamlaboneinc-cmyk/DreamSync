from __future__ import annotations
from pathlib import Path
import subprocess

def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=check)

def head_sha(root: Path) -> str:
    return git(root, "rev-parse", "HEAD").stdout.strip()

def tracked_files(root: Path) -> list[str]:
    return [x for x in git(root, "ls-files").stdout.splitlines() if x]

def status(root: Path) -> str:
    return git(root, "status", "--short", "--branch").stdout
