from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Intent:
    action: str
    request: str


RULES = (
    ("status", ("status", "where are we")),
    ("verify", ("verify", "test", "check")),
    ("deploy", ("deploy", "publish", "release")),
    ("plan", ("plan", "design", "build.md")),
    ("discover", ("discover", "inspect", "adopt")),
    ("debug", ("fix", "bug", "broken", "error", "debug", "not working")),
    ("upgrade", ("add", "upgrade", "improve", "change", "update", "feature")),
    ("build", ("build", "create", "make", "implement")),
)


def classify(text: str) -> Intent:
    request = re.sub(r"\s+", " ", text).strip()
    if not request:
        raise ValueError("request is empty")
    lowered = request.lower()
    for action, words in RULES:
        if any(word in lowered for word in words):
            return Intent(action, request)
    return Intent("build", request)


def explain(intent: Intent) -> dict:
    return {
        "action": intent.action,
        "request": intent.request,
        "routing": "DreamSync deterministic workflow",
    }
