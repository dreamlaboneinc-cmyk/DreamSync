from __future__ import annotations
from pathlib import Path
import json, subprocess, time, urllib.request
from .config import load_project
from .state import State

def _run(args, cwd: Path, check=True):
    return subprocess.run(args,cwd=cwd,text=True,capture_output=True,check=check)

def _service_active(name: str) -> bool:
    return subprocess.run(["systemctl","is-active","--quiet",name]).returncode == 0

def _service_healthy(name: str, mode: str = "auto") -> bool:
    show = subprocess.run(["systemctl","show",name,"--property=LoadState,ActiveState,Type,Result,ExecMainStatus","--no-pager"], text=True, capture_output=True)
    props = dict(line.split("=",1) for line in show.stdout.splitlines() if "=" in line)
    if show.returncode != 0 or props.get("LoadState") != "loaded": return False
    if mode == "persistent": return props.get("ActiveState") == "active"
    if mode == "successful_exit": return props.get("Result") == "success" and props.get("ExecMainStatus") == "0"
    if props.get("Type") == "oneshot": return props.get("Result") == "success" and props.get("ExecMainStatus") == "0"
    return props.get("ActiveState") == "active"

def _health(url: str, attempts: int=8, delay: float=1.0) -> bool:
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url,timeout=4) as r:
                if 200 <= r.status < 400: return True
        except Exception:
            pass
        time.sleep(delay)
    return False

def _sync_target(root: Path, target: str | None) -> None:
    if not target:
        return
    target_path = Path(target)
    if not target_path.is_absolute():
        raise RuntimeError("deploy sync_to must be an absolute path")
    excludes = [".git", ".env", "venv", ".venv", "data", "state", "backups", "backup", "uploads", "models", "__pycache__"]
    args = ["rsync", "-a", "--delete"]
    for item in excludes:
        args += ["--exclude", item]
    args += [str(root) + "/", str(target_path) + "/"]
    subprocess.run(args, check=True)


def deploy_exact(root: Path, sha: str) -> dict:
    cfg=load_project(root); root=cfg.root; dep=cfg.raw.get("deploy",{})
    status=_run(["git","status","--porcelain"],root).stdout.strip()
    dirty=[]
    for line in status.splitlines():
        rel=line[3:].replace("\\", "/") if len(line)>3 else ""
        if rel==".env" or rel.startswith(("data/","state/","backups/","backup/","venv/",".venv/","__pycache__/")): continue
        dirty.append(line)
    if dirty:
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
    _sync_target(root, dep.get("sync_to"))
    for svc in services:
        subprocess.run(["systemctl","restart",svc],check=True)
    service_modes=dep.get("service_health",{})
    checks={svc:_service_healthy(svc, service_modes.get(svc,"auto")) for svc in services}
    urls={url:_health(url) for url in dep.get("health_urls",[])}
    ok=all(checks.values()) and all(urls.values())
    if ok:
        known.parent.mkdir(exist_ok=True); known.write_text(json.dumps({"sha":sha},indent=2))
        state.release(sha,"known-good"); state.event("deploy",{"sha":sha,"ok":True,"services":checks,"urls":urls})
        return {"ok":True,"sha":sha,"services":checks,"health":urls,"rollback":False}
    state.release(sha,"failed-health")
    if dep.get("rollback") and previous and previous != sha:
        _run(["git","reset","--hard",previous],root)
        _sync_target(root, dep.get("sync_to"))
        for svc in services: subprocess.run(["systemctl","restart",svc],check=False)
        state.event("rollback",{"failed_sha":sha,"restored_sha":previous})
        return {"ok":False,"sha":sha,"services":checks,"health":urls,"rollback":True,"restored":previous}
    state.event("deploy",{"sha":sha,"ok":False,"services":checks,"urls":urls})
    return {"ok":False,"sha":sha,"services":checks,"health":urls,"rollback":False}
