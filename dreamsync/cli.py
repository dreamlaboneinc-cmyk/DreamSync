from __future__ import annotations

import argparse
import json
import subprocess

from .config import load_project
from .dream_api import DreamAPIClient
from .gitops import status
from .scanner import scan_repo
from .verify import verify


def _head_sha(root):
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def main():
    parser = argparse.ArgumentParser(prog="dreamsync")
    parser.add_argument(
        "command",
        choices=[
            "status",
            "scan",
            "verify",
            "ai-health",
            "mission-observe",
            "mission-auto",
            "promote",
            "deploy",
            "deploy-receive",
            "discover",
            "adopt",
            "build",
            "debug",
            "upgrade",
            "chat",
        ],

    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--plan")
    parser.add_argument(
        "--objective",
        default="inspect and verify repository",
    )
    parser.add_argument(
        "--message",
        default="DreamSync verified promotion",
    )
    parser.add_argument("--sha")
    parser.add_argument("--request")
    parser.add_argument("--execute", action="store_true")

    args = parser.parse_args()
    cfg = load_project(args.root)
    root = cfg.root

    if args.command == "status":
        print(status(root), end="")

    elif args.command == "scan":
        print(json.dumps(scan_repo(root), indent=2))

    elif args.command == "verify":
        result = verify(root)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["verified"] else 2)

    elif args.command == "ai-health":
        client = DreamAPIClient(
            cfg.ai.get("base_url", "http://127.0.0.1:8275")
        )
        print(json.dumps(client.health(), indent=2))

    elif args.command == "mission-observe":
        from .mission import Mission, run_observe

        result = run_observe(
            root,
            Mission("observe", args.objective, args.plan),
        )
        print(json.dumps(result, indent=2))

    elif args.command == "mission-auto":
        from .autonomous import run_autonomous

        result = run_autonomous(
            root,
            args.objective,
            args.plan,
        )
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["ok"] else 4)

    elif args.command == "promote":
        from .promotion import promote

        print(
            json.dumps(
                promote(root, args.message, True),
                indent=2,
            )
        )

    elif args.command == "deploy":
        sha = args.sha or _head_sha(root)

        if cfg.controller.get("ssh_target"):
            from .controller import remote_deploy

            result = remote_deploy(root, sha)
        else:
            from .deployment import deploy_exact

            result = deploy_exact(root, sha)

        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["ok"] else 3)

    elif args.command == "discover":
        from .discovery import write_discovery

        print(json.dumps(write_discovery(root), indent=2))

    elif args.command == "adopt":
        from .projects import adopt_project

        print(json.dumps(adopt_project(root), indent=2))

    elif args.command == "chat":
        if not args.request:
            raise SystemExit("chat requires --request")
        from .chat import chat, format_chat
        result = chat(root, args.request, args.execute)
        print(format_chat(result))
        raise SystemExit(0 if result["ok"] else 4)

    elif args.command == "deploy-receive":
        if not args.sha:
            raise SystemExit("deploy-receive requires --sha")

        from .receiver import receive_exact

        result = receive_exact(root, args.sha)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["ok"] else 3)


if __name__ == "__main__":
    main()
