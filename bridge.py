#!/usr/bin/env python3
"""DreamSync V2 compatibility bridge.

Status remains available. Mutating restart/deploy actions are intentionally routed
through the verified DreamSync V2 deployment engine instead of legacy direct control.
"""
from pathlib import Path
import subprocess, yaml

CFG=Path("/root/config/dreamlab.yml")

def load():
    return yaml.safe_load(CFG.read_text()) if CFG.exists() else {}

def active(alias: str, systemd: bool) -> str:
    if not systemd:
        return "manual"
    p=subprocess.run(["systemctl","is-active",f"{alias}.service"],text=True,capture_output=True)
    return p.stdout.strip() or "unknown"

def main() -> int:
    import sys
    if len(sys.argv)==1 or sys.argv[1]=="status":
        for alias,meta in (load() or {}).items():
            print(f"[{alias}] {active(alias,bool((meta or {}).get('systemd',False)))}")
        return 0
    print("BLOCKED: legacy bridge mutation retired; use DreamSync V2 verified promotion/deployment.")
    return 3

if __name__=="__main__":
    raise SystemExit(main())
