from __future__ import annotations
from pathlib import Path
import json, re, time
from .config import load_project
from .dream_api import DreamAPIClient
from .policy import assert_patch_path
from .scanner import repo_files, scan_repo
from .verify import verify
from .state import State

TEXT_EXT={".py",".md",".txt",".json",".yml",".yaml",".toml",".ini",".cfg",".html",".css",".js",".ts",".tsx",".jsx",".sh",".ps1"}

def _json_object(text: str) -> dict:
    text=text.strip()
    if text.startswith("```"):
        text=re.sub(r"^```(?:json)?\s*|\s*```$","",text,flags=re.S)
    try: return json.loads(text)
    except json.JSONDecodeError:
        a=text.find("{"); b=text.rfind("}")
        if a<0 or b<=a: raise ValueError("AI response did not contain JSON")
        return json.loads(text[a:b+1])
def _context(root: Path, plan_file: str|None, objective: str, failures: list|None=None) -> str:
    files=repo_files(root); chunks=[]; used=0; budget=30000
    for rel in files:
        p=root/rel
        if p.suffix.lower() not in TEXT_EXT: continue
        if rel.startswith(("state/","data/","backups/","handoff_","legacy/")): continue
        try: body=p.read_text(errors="replace")
        except OSError: continue
        if len(body)>5000: body=body[:5000]+"\n...[truncated]"
        item=f"\n--- FILE {rel} ---\n{body}"
        if used+len(item)>budget: break
        chunks.append(item); used+=len(item)
    plan=""
    if plan_file:
        pp=(root/plan_file).resolve()
        if root not in pp.parents and pp!=root: raise ValueError("plan outside repo")
        plan=pp.read_text(errors="replace")[:16000]
    failed=json.dumps(failures or [],indent=2)[:10000]
    return f"OBJECTIVE:\n{objective}\n\nPLAN:\n{plan}\n\nREPO SUMMARY:\n{json.dumps(scan_repo(root))}\n\nLAST FAILURES:\n{failed}\n"+''.join(chunks)
def propose(root: Path, objective: str, plan_file: str|None=None, failures: list|None=None) -> dict:
    cfg=load_project(root)
    prompt='''You are the coding brain for DreamSync. Return ONLY JSON, no markdown.
Schema: {"summary":"short","operations":[{"action":"write","path":"relative/path","content":"full file content"}]}
Rules: solve the objective using the supplied repository and plan. Use only write operations. Never write secrets, .env, credentials, state, data, backups, .git, or virtual environments. Do not propose shell commands. Preserve working code unless a change is needed. Include complete content for every file you change. If verification failures are supplied, repair them.
CONTEXT:
'''+_context(root,plan_file,objective,failures)
    raw=DreamAPIClient(cfg.ai.get("base_url","http://127.0.0.1:8275"),timeout=120).complete(prompt)
    obj=_json_object(raw)
    if not isinstance(obj.get("operations"),list): raise ValueError("AI operations must be a list")
    return obj
def apply_operations(root: Path, proposal: dict) -> list[str]:
    changed=[]
    for op in proposal.get("operations",[]):
        if op.get("action")!="write": raise ValueError("unsupported AI operation")
        rel=str(op.get("path",""))
        target=assert_patch_path(root,rel)
        content=op.get("content")
        if not isinstance(content,str): raise ValueError(f"invalid content for {rel}")
        target.parent.mkdir(parents=True,exist_ok=True)
        old=target.read_text(errors="replace") if target.exists() else None
        if old!=content:
            target.write_text(content); changed.append(rel)
    return changed

def run_autonomous(root: Path, objective: str, plan_file: str|None=None, retries: int=3) -> dict:
    root=root.resolve(); state=State(root); started=time.time(); history=[]
    for attempt in range(retries+1):
        failures=history[-1].get("failed_gates",[]) if history else []
        proposal=propose(root,objective,plan_file,failures)
        changed=apply_operations(root,proposal)
        result=verify(root)
        failed=[g for g in result["gates"] if not g["ok"]]
        item={"attempt":attempt+1,"summary":proposal.get("summary",""),"changed":changed,"verified":result["verified"],"failed_gates":failed}
        history.append(item); state.event("autonomous_attempt",item)
        if result["verified"]:
            out={"ok":True,"phase":"COMPLETE","objective":objective,"attempts":history,"verification":result,"started":started,"finished":time.time()}
            (root/"state"/"last_autonomous_mission.json").write_text(json.dumps(out,indent=2)); return out
    out={"ok":False,"phase":"BLOCKED","objective":objective,"attempts":history,"verification":result,"started":started,"finished":time.time()}
    (root/"state"/"last_autonomous_mission.json").write_text(json.dumps(out,indent=2)); return out
