from __future__ import annotations

from pathlib import Path
import json

SIGNALS = {
    "python": ("pyproject.toml", "requirements.txt", "setup.py"),
    "node": ("package.json",),
    "php": ("composer.json",),
    "wordpress": ("wp-config.php", "wp-settings.php"),
    "docker": ("Dockerfile", "docker-compose.yml", "compose.yml"),
}


def discover(root: str | Path) -> dict:
    root = Path(root).resolve()
    found = {
        kind: [name for name in names if (root / name).exists()]
        for kind, names in SIGNALS.items()
    }
    found = {kind: files for kind, files in found.items() if files}

    types = list(found)
    if "wordpress" in types:
        primary = "wordpress"
    elif len(types) == 1:
        primary = types[0]
    elif types:
        primary = "hybrid"
    else:
        primary = "unknown"

    tests = [p.name for p in (root / "tests", root / "test") if p.exists()]
    return {
        "root": str(root),
        "primary_type": primary,
        "detected": found,
        "has_git": (root / ".git").exists(),
        "test_dirs": tests,
    }


def write_discovery(root: str | Path) -> dict:
    root = Path(root).resolve()
    data = discover(root)
    out = root / ".dreamsync" / "discovery.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n")
    return data
