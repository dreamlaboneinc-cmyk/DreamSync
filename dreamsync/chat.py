from __future__ import annotations

from pathlib import Path
import json

from .intent import classify, explain
from .workflow import prepare, run


def chat(root: str | Path, message: str, execute: bool = False) -> dict:
    root = Path(root).resolve()
    intent = classify(message)
    route = explain(intent)
    if not execute:
        mission = prepare(root, intent.action, intent.request)
        return {
            "ok": True,
            "mode": "PLAN",
            "intent": route,
            "mission": mission,
            "next": "run with --execute to let the agent make changes",
        }

    result = run(root, intent.action, intent.request)
    return {
        "ok": result["ok"],
        "mode": "EXECUTE",
        "intent": route,
        "phase": result["phase"],
        "result": result,
    }


def format_chat(result: dict) -> str:
    intent = result["intent"]
    lines = [
        f"DreamSync: {result['mode']}",
        f"Mission: {intent['action'].upper()}",
        f"Request: {intent['request']}",
    ]
    if result["mode"] == "PLAN":
        lines.append("Status: READY")
        lines.append("No source files changed by the agent.")
    else:
        lines.append(f"Status: {result.get('phase', 'UNKNOWN')}")
    return "\n".join(lines)
