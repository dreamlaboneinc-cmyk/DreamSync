#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "DreamSync V2 setup check"
./venv/bin/python -m dreamsync.cli ai-health
./venv/bin/python -m dreamsync.cli verify
echo "DreamSync V2 core prerequisites verified."
echo "External connectors (Cursor/local PC, optional paid GPT/Codex) are configured separately."
