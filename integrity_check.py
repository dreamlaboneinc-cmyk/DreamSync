#!/usr/bin/env python3
"""DreamSync V2 read-only integrity audit. Never repairs or overwrites application files."""
from pathlib import Path
import sys, yaml
CFG=Path('/root/config/dreamlab.yml')

def audit() -> int:
    if not CFG.exists():
        print('FAIL config missing'); return 2
    data=yaml.safe_load(CFG.read_text()) or {}
    failures=[]
    for alias,meta in data.items():
        path=Path(meta.get('path',''))
        entry=meta.get('entry')
        if not path.is_dir(): failures.append(f'{alias}: missing directory')
        elif entry and not (path/entry).exists(): failures.append(f'{alias}: missing entry')
    for item in failures: print('FAIL',item)
    print(f'Integrity audit: {len(data)} apps, {len(failures)} failures')
    return 2 if failures else 0

if __name__=='__main__':
    if '--fix' in sys.argv:
        print('BLOCKED: --fix was retired in DreamSync V2; integrity audit is read-only.')
        raise SystemExit(3)
    raise SystemExit(audit())
