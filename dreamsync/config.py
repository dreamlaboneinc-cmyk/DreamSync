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

    @property
    def controller(self) -> dict:
        return self.raw.get("controller", {})


def _merge(base: dict, override: dict) -> dict:
    result = dict(base)

    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value

    return result


def load_project(root: str | Path = ".") -> ProjectConfig:
    root = Path(root).resolve()
    config_dir = root / ".dreamsync"

    project_path = config_dir / "project.yml"
    data = yaml.safe_load(project_path.read_text()) or {}

    local_path = config_dir / "local.yml"

    if local_path.exists():
        local_data = yaml.safe_load(local_path.read_text()) or {}
        data = _merge(data, local_data)

    return ProjectConfig(root=root, raw=data)