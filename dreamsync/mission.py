from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json, time
from .scanner import scan_repo
from .verify import verify

@dataclass
class Mission:
    kind: str
    objective: str
    plan_file: str|None=None

def discover(root: Path, mission: Mission) -> dict:
    plan=""
    if mission.plan_file:
        p=(root/mission.plan_file).resolve()
        if root not in p.parents and p!=root: raise ValueError("plan outside repo")
        plan=p.read_text()
    return {"mission":asdict(mission),"repo":scan_repo(root),"plan":plan[:20000]}

def run_observe(root: Path, mission: Mission) -> dict:
    result={"phase":"DISCOVER","started":time.time(),"context":discover(root,mission)}
    result["verification"]=verify(root); result["phase"]="COMPLETE" if result["verification"]["verified"] else "BLOCKED"
    out=root/"state"/"last_mission.json"; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(result,indent=2))
    return result
