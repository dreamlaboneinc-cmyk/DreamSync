from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib, json, re, subprocess, time, uuid
from .config import load_project
from .gitops import tracked_files, head_sha
from .scanner import repo_files
from .state import State

@dataclass
class Gate:
    name: str
    ok: bool
    detail: str

SECRET_RULES={
 "private-key":re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
 "openai-key":re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
 "github-token":re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
}
TEXT_SUFFIX={'.py','.js','.ts','.tsx','.jsx','.json','.yml','.yaml','.toml','.ini','.cfg','.md','.txt','.sh','.ps1','.html','.css','.env'}

def _run(root: Path, cmd: str) -> Gate:
    p=subprocess.run(cmd,cwd=root,shell=True,text=True,capture_output=True)
    detail=(p.stdout+p.stderr).strip()[-4000:]
    return Gate(cmd,p.returncode==0,detail)

def fingerprint(root: Path) -> str:
    h=hashlib.sha256()
    for rel in repo_files(root):
        p=root/rel
        if not p.is_file(): continue
        h.update(rel.encode()+b'\0'); h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()

def _secret_gate(root: Path) -> Gate:
    hits=[]
    for rel in repo_files(root):
        p=root/rel
        if p.suffix.lower() not in TEXT_SUFFIX and p.name not in {'.env','.env.example'}: continue
        if p.name=='.env' or rel.startswith(('data/','state/','backups/','handoff_')): continue
        try: text=p.read_text(errors='replace')
        except OSError: continue
        for name,rule in SECRET_RULES.items():
            if rule.search(text): hits.append(f"{rel}:{name}")
    return Gate('secret scan',not hits,', '.join(hits) if hits else 'clean')

def verify(root: str|Path='.') -> dict:
    cfg=load_project(root); root=cfg.root; gates=[]
    tracked=set(tracked_files(root)); forbidden=cfg.verification.get('forbidden_tracked',[])
    bad=sorted(f for f in tracked if any(f==x or f.startswith(x.rstrip('/')+'/') for x in forbidden))
    gates.append(Gate('forbidden tracked files',not bad,', '.join(bad) if bad else 'clean'))
    gates.append(_secret_gate(root))
    gates.append(_run(root,'git diff --check'))
    gates.append(_run(root,'./venv/bin/python -m pip check'))
    for group in ('compile','lint','test','acceptance'):
        for cmd in cfg.verification.get(group,[]) or []: gates.append(_run(root,cmd))
    vid=str(uuid.uuid4())
    result={'verification_id':vid,'verified':all(g.ok for g in gates),'base_sha':head_sha(root),'worktree_fingerprint':fingerprint(root),'timestamp':time.time(),'gates':[asdict(g) for g in gates]}
    out=root/'state'/'last_verification.json'; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(result,indent=2))
    State(root).event('verification',{'id':vid,'verified':result['verified'],'fingerprint':result['worktree_fingerprint']})
    return result
