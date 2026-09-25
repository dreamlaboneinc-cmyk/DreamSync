from __future__ import annotations
from pathlib import Path
import subprocess, time
from .verify import verify, fingerprint
from .state import State

def _git(root: Path, *args: str, check: bool=True) -> subprocess.CompletedProcess:
    return subprocess.run(["git",*args],cwd=root,text=True,capture_output=True,check=check)

def promote(root: Path, message: str, push: bool=True) -> dict:
    before=verify(root)
    if not before["verified"]:
        raise RuntimeError("verification failed; promotion blocked")
    expected=before["worktree_fingerprint"]
    _git(root,"add","-A")
    staged=_git(root,"diff","--cached","--name-only").stdout.splitlines()
    protected=(".env","data/","state/","backups/","venv/",".venv/")
    bad=[p for p in staged if p==".env" or p.startswith(protected)]
    if bad:
        _git(root,"reset")
        raise RuntimeError("protected paths staged: "+", ".join(bad))
    after=verify(root)
    if not after["verified"] or after["worktree_fingerprint"] != expected or fingerprint(root) != expected:
        _git(root,"reset")
        raise RuntimeError("verified snapshot changed during staging")
    if not staged:
        return {"ok":True,"changed":False,"sha":_git(root,"rev-parse","HEAD").stdout.strip(),"verification_id":after["verification_id"]}
    body=f"{message}\n\nDreamSync-Verified: true\nDreamSync-Verification-ID: {after['verification_id']}\nDreamSync-Fingerprint: {expected}"
    _git(root,"commit","-m",body)
    sha=_git(root,"rev-parse","HEAD").stdout.strip()
    if push:
        _git(root,"push","origin","HEAD:main")
        remote=_git(root,"ls-remote","origin","refs/heads/main").stdout.split()[0]
        if remote != sha:
            raise RuntimeError("GitHub main does not match promoted SHA")
    State(root).release(sha,"promoted",after["verification_id"])
    State(root).event("promotion",{"sha":sha,"verification_id":after["verification_id"],"pushed":push,"ts":time.time()})
    return {"ok":True,"changed":True,"sha":sha,"verification_id":after["verification_id"],"pushed":push}
