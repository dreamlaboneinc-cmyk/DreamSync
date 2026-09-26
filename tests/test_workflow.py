import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dreamsync.workflow import prepare, run


class WorkflowTests(unittest.TestCase):
    def test_prepare_creates_mission_record(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "App"
            root.mkdir()
            record = prepare(root, "debug", "fix login")
            self.assertEqual(record["type"], "debug")
            self.assertEqual(record["status"], "READY")
            self.assertTrue((root / ".dreamsync" / "missions" / "current.json").exists())

    @patch("dreamsync.workflow.run_autonomous")
    def test_run_routes_to_autonomous_engine(self, auto):
        auto.return_value = {"ok": True, "phase": "COMPLETE"}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "App"
            root.mkdir()
            result = run(root, "upgrade", "add search")
            self.assertTrue(result["ok"])
            self.assertTrue(auto.called)


if __name__ == "__main__":
    unittest.main()
