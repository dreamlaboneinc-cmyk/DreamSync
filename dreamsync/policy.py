from __future__ import annotations
from pathlib import Path

PROTECTED_DEFAULT={".env","data","state",".git","backups","venv",".venv","handoff_20260925","legacy"}
def assert_patch_path(root: Path, relative: str, protected=None) -> Path:
    root=root.resolve(); p=(root/relative).resolve()
    if p!=root and root not in p.parents: raise ValueError("path escapes repository")
    parts=Path(relative).parts; protected=set(protected or PROTECTED_DEFAULT)
    if parts and parts[0] in protected: raise PermissionError(f"protected path: {relative}")
    return p
