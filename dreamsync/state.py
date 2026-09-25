from __future__ import annotations
from pathlib import Path
import json, sqlite3, time, uuid

SCHEMA="""
CREATE TABLE IF NOT EXISTS audit(
 id TEXT PRIMARY KEY, ts REAL NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS releases(
 sha TEXT PRIMARY KEY, ts REAL NOT NULL, status TEXT NOT NULL, verification_id TEXT
);
"""

class State:
    def __init__(self, root: Path):
        self.path=root/'state'/'dreamsync.db'; self.path.parent.mkdir(exist_ok=True)
        with sqlite3.connect(self.path) as c: c.executescript(SCHEMA)
    def event(self, kind: str, payload: dict) -> str:
        eid=str(uuid.uuid4())
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT INTO audit VALUES(?,?,?,?)",(eid,time.time(),kind,json.dumps(payload,sort_keys=True)))
        return eid
    def release(self, sha: str, status: str, verification_id: str|None=None):
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT OR REPLACE INTO releases VALUES(?,?,?,?)",(sha,time.time(),status,verification_id))
