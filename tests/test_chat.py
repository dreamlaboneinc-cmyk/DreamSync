import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dreamsync.chat import chat
from dreamsync.intent import classify


class ChatTests(unittest.TestCase):
    def test_intent_routes_bug_to_debug(self):
        self.assertEqual(classify("fix the login bug").action, "debug")

    def test_intent_routes_feature_to_upgrade(self):
        self.assertEqual(classify("add CSV export").action, "upgrade")

    def test_plan_does_not_run_agent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "App"
            root.mkdir()
            result = chat(root, "fix card ordering", execute=False)
            self.assertEqual(result["mode"], "PLAN")
            self.assertEqual(result["intent"]["action"], "debug")
            self.assertTrue(
                (root / ".dreamsync" / "missions" / "current.json").exists()
            )

    @patch("dreamsync.chat.run")
    def test_execute_routes_to_workflow(self, runner):
        runner.return_value = {"ok": True, "phase": "COMPLETE"}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "App"
            root.mkdir()
            result = chat(root, "add search", execute=True)
            self.assertEqual(result["mode"], "EXECUTE")
            self.assertTrue(runner.called)


if __name__ == "__main__":
    unittest.main()
