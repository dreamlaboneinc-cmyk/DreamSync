from __future__ import annotations
from pathlib import Path
from .config import load_project
from .dream_api import DreamAPIClient

def create_plan(root: str | Path, request: str) -> dict:
    root=Path(root).resolve()
    cfg=load_project(root)
    prompt=("You are DreamSync planning an engineering mission. Return a concise BUILD.md in Markdown only. Include Goal, Scope, Requirements, Intended Output, Acceptance Criteria, Verification, Risks, Deployment. User request: "+request)
    client=DreamAPIClient(cfg.ai.get("base_url","http://127.0.0.1:8275"),timeout=120)
    try:
        text=client.complete(prompt)
    except Exception:
        if not cfg.controller.get("ssh_target"):
            raise
        from .controller import remote_ai_complete
        text=remote_ai_complete(root,prompt)
    (root/"BUILD.md").write_text(text.rstrip()+"\n",encoding="utf-8",newline="\n")
    return {"ok":True,"phase":"PLANNED","file":"BUILD.md","billing_mode":"FREE_ONLY"}
