import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LegacySafetyTests(unittest.TestCase):

    def test_legacy_deploy_is_blocked(self):
        p = subprocess.run(
            [sys.executable, "deploy.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("BLOCKED", p.stdout + p.stderr)

    def test_bridge_status_works(self):
        p = subprocess.run(
            [sys.executable, "bridge.py", "status"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_bridge_restart_is_blocked(self):
        p = subprocess.run(
            [sys.executable, "bridge.py", "restart", "DreamSync"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(p.returncode, 3)
        self.assertIn("BLOCKED", p.stdout + p.stderr)