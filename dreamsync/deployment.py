from __future__ import annotations
from pathlib import Path
import json, subprocess, urllib.request
from .config import load_project
from .state import State

def _run(args, cwd: Path, check=True):
    return subprocess.run(args,cwd=cwd,text=True,capture_output=True,check=check)

def _service_active(name: str) -> bool:
    return subprocess.run(["systemctl","is-active","--quiet",name]).returncode == 0

def _health(url: str) -> bool:
    try:
        with urllib.request.urlopen(url,timeout=8) as r:
            return 200 <= r.status < 400
    except Exception:
        return False

def deploy_exact(root: Path, sha: str) -> dict:
    cfg=load_project(root); root=cfg.root; dep=cfg.raw.get("deploy",{})
    if _run(["git","status","--porcelain"],root).stdout.strip():
        raise RuntimeError("deployment requires a clean working tree")
    _run(["git","fetch","origin","main"],root)
    remote=_run(["git","rev-parse","origin/main"],root).stdout.strip()
    head=_run(["git","rev-parse","HEAD"],root).stdout.strip()
    if remote != sha or head != sha:
        raise RuntimeError(f"exact-SHA invariant failed: head={head[:12]} remote={remote[:12]} requested={sha[:12]}")
    state=State(root)
    known=root/"state"/"known_good.json"
    previous=None
    if known.exists():
        try: previous=json.loads(known.read_text()).get("sha")
        except Exception: previous=None
    services=dep.get("services",[])
    for svc in services:
        subprocess.run(["systemctl","restart",svc],check=True)
    checks={svc:_service_active(svc) for svc in services}
    urls={url:_health(url) for url in dep.get("health_urls",[])}
    ok=all(checks.values()) and all(urls.values())
    if ok:
        known.parent.mkdir(exist_ok=True); known.write_text(json.dumps({"sha":sha},indent=2))
        state.release(sha,"known-good"); state.event("deploy",{"sha":sha,"ok":True,"services":checks,"urls":urls})
        return {"ok":True,"sha":sha,"services":checks,"health":urls,"rollback":False}
    state.release(sha,"failed-health")
    if dep.get("rollback") and previous and previous != sha:
        _run(["git","reset","--hard",previous],root)
        for svc in services: subprocess.run(["systemctl","restart",svc],check=False)
        state.event("rollback",{"failed_sha":sha,"restored_sha":previous})
        return {"ok":False,"sha":sha,"services":checks,"health":urls,"rollback":True,"restored":previous}
    state.event("deploy",{"sha":sha,"ok":False,"services":checks,"urls":urls})
    return {"ok":False,"sha":sha,"services":checks,"health":urls,"rollback":False}
