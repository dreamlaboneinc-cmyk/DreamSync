from __future__ import annotations
from pathlib import Path
import json, yaml

def build_registry(workspace: str|Path) -> dict:
    base=Path(workspace).resolve(); projects=[]
    for root in sorted(base.iterdir()):
        cfg=root/".dreamsync"/"project.yml"
        if not (root/".git").exists() or not cfg.exists(): continue
        data=yaml.safe_load(cfg.read_text()) or {}
        local=root/".dreamsync"/"local.yml"
        loc=yaml.safe_load(local.read_text()) if local.exists() else {}
        dep=data.get("deploy",{}); ctl=(loc or {}).get("controller",{})
        projects.append({"name":data.get("project",{}).get("name",root.name),"laptop":str(root),"github":"origin/main","canonical_linode":ctl.get("remote_project"),"live":dep.get("sync_to"),"services":dep.get("services",[]),"health_urls":dep.get("health_urls",[]),"type":data.get("project",{}).get("type","unknown"),"runtime_exclusions":data.get("protected_paths",[])})
    return {"version":1,"count":len(projects),"projects":projects}

def write_registry(workspace: str|Path, output: str|Path) -> dict:
    data=build_registry(workspace); Path(output).write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8",newline="\n"); return data
