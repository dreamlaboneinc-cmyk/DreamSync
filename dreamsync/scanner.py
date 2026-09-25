from __future__ import annotations
from pathlib import Path
import ast, subprocess

MANIFESTS={"requirements.txt","requirements-core.txt","pyproject.toml","package.json","package-lock.json","pnpm-lock.yaml","yarn.lock","go.mod","Cargo.toml"}
PLANS={"BUILD.md","PROJECT_BUILD.md","DREAMSYNC_V2_BUILD.md"}

def _git(root: Path, *args: str) -> list[str]:
    p=subprocess.run(["git",*args],cwd=root,text=True,capture_output=True,check=True)
    return [x for x in p.stdout.splitlines() if x]

def repo_files(root: Path) -> list[str]:
    # Tracked + untracked/non-ignored files; Git itself defines exclusions.
    return sorted(set(_git(root,"ls-files") + _git(root,"ls-files","--others","--exclude-standard")))

def _imports(root: Path, files: list[str]) -> dict[str,list[str]]:
    out={}
    for rel in files:
        if not rel.endswith('.py'): continue
        try: tree=ast.parse((root/rel).read_text(errors='replace'))
        except (OSError,SyntaxError): continue
        names=set()
        for n in ast.walk(tree):
            if isinstance(n,ast.Import): names.update(a.name.split('.')[0] for a in n.names)
            elif isinstance(n,ast.ImportFrom) and n.module: names.add(n.module.split('.')[0])
        out[rel]=sorted(names)
    return out

def scan_repo(root: Path) -> dict:
    files=repo_files(root); suffixes={}
    for f in files:
        s=Path(f).suffix.lower() or "<none>"; suffixes[s]=suffixes.get(s,0)+1
    return {
        "files":len(files), "languages":suffixes,
        "manifests":[f for f in files if Path(f).name in MANIFESTS],
        "plans":[f for f in files if Path(f).name in PLANS],
        "tests":[f for f in files if "test" in Path(f).name.lower()],
        "python_imports":_imports(root,files),
        "recent_commits":_git(root,"log","-5","--oneline"),
    }
