from __future__ import annotations

from pathlib import Path
import json

from .intent import classify, explain
from .workflow import prepare, run


def chat(root: str | Path, message: str, execute: bool = False) -> dict:
    root = Path(root).resolve()
    intent = classify(message)
    route = explain(intent)
    if intent.action == "plan":
        from .planning import create_plan
        result=create_plan(root,intent.request)
        return {"ok":True,"mode":"PLAN","intent":route,"mission":result,"next":"BUILD.md ready"}
    if intent.action == "status" or intent.action == "verify":
        from .verify import verify
        result=verify(root)
        return {"ok":result["verified"],"mode":"STATUS","intent":route,"phase":"VERIFIED" if result["verified"] else "BLOCKED","result":result}
    if intent.action == "discover":
        from .discovery import write_discovery
        result=write_discovery(root)
        return {"ok":True,"mode":"DISCOVER","intent":route,"phase":"COMPLETE","result":result}
    if intent.action == "deploy":
        if not execute:
            return {"ok":True,"mode":"PLAN","intent":route,"mission":{"status":"READY"},"next":"run with --execute to verify and deploy"}
        from .mcp_server import finish_verified
        result=finish_verified("DreamSync natural-language deployment",str(root))
        return {"ok":result["ok"],"mode":"EXECUTE","intent":route,"phase":result["phase"],"result":result}
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
