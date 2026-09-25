from __future__ import annotations
import argparse, json
from pathlib import Path
from .config import load_project
from .dream_api import DreamAPIClient
from .scanner import scan_repo
from .verify import verify
from .gitops import status

def main():
    p=argparse.ArgumentParser(prog="dreamsync")
    p.add_argument("command",choices=["status","scan","verify","ai-health","mission-observe","promote","deploy"]); p.add_argument("--root",default="."); p.add_argument("--plan"); p.add_argument("--objective",default="inspect and verify repository"); p.add_argument("--message",default="DreamSync verified promotion"); p.add_argument("--sha")
    a=p.parse_args(); cfg=load_project(a.root); root=cfg.root
    if a.command=="status": print(status(root),end="")
    elif a.command=="scan": print(json.dumps(scan_repo(root),indent=2))
    elif a.command=="verify":
        r=verify(root); print(json.dumps(r,indent=2)); raise SystemExit(0 if r["verified"] else 2)
    elif a.command=="ai-health": print(json.dumps(DreamAPIClient(cfg.ai.get("base_url","http://127.0.0.1:8275")).health(),indent=2))
    elif a.command=="mission-observe":
        from .mission import Mission, run_observe
        print(json.dumps(run_observe(root,Mission("observe",a.objective,a.plan)),indent=2))
    elif a.command=="promote":
        from .promotion import promote
        print(json.dumps(promote(root,a.message,True),indent=2))
    elif a.command=="deploy":
        from .deployment import deploy_exact
        sha=a.sha or __import__("subprocess").run(["git","rev-parse","HEAD"],cwd=root,text=True,capture_output=True,check=True).stdout.strip()
        r=deploy_exact(root,sha); print(json.dumps(r,indent=2)); raise SystemExit(0 if r["ok"] else 3)
if __name__=="__main__": main()
