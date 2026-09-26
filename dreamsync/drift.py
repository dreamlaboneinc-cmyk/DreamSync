from __future__ import annotations
from pathlib import Path
import hashlib, json

DEFAULT_EXCLUDES={'.git','.env','venv','.venv','data','state','backups','backup','uploads','models','__pycache__','node_modules','.next','cache','logs'}

def manifest(root: str|Path, extra_excludes=None) -> dict[str,str]:
    root=Path(root); excluded=DEFAULT_EXCLUDES|set(extra_excludes or [])
    out={}
    if not root.exists(): return out
    for p in root.rglob('*'):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if any(part in excluded for part in rel.parts): continue
        try: out[str(rel).replace('\\','/')]=hashlib.sha256(p.read_bytes()).hexdigest()
        except OSError: continue
    return out

def compare_saved(root: str|Path, live: str|Path, extra_excludes=None) -> dict:
    saved=Path(root)/'state'/'deployed_manifest.json'
    if not saved.exists(): return {'ok':True,'initialized':False,'drift':[]}
    expected=json.loads(saved.read_text()).get('files',{})
    actual=manifest(live,extra_excludes)
    drift=sorted(set(expected)^set(actual) | {k for k in set(expected)&set(actual) if expected[k]!=actual[k]})
    return {'ok':not drift,'initialized':True,'drift':drift[:100]}

def save(root: str|Path, live: str|Path, sha: str, extra_excludes=None) -> None:
    p=Path(root)/'state'/'deployed_manifest.json'; p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps({'sha':sha,'files':manifest(live,extra_excludes)},indent=2)+'\n',encoding='utf-8')
