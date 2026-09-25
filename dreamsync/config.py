from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass(frozen=True)
class ProjectConfig:
    root: Path
    raw: dict

    @property
    def verification(self) -> dict:
        return self.raw.get("verification", {})

    @property
    def ai(self) -> dict:
        return self.raw.get("ai", {})

def load_project(root: str | Path = ".") -> ProjectConfig:
    root = Path(root).resolve()
    path = root / ".dreamsync" / "project.yml"
    data = yaml.safe_load(path.read_text()) or {}
    return ProjectConfig(root=root, raw=data)
