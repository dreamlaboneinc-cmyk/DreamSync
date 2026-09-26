import tempfile
import unittest
from pathlib import Path

from dreamsync.discovery import discover
from dreamsync.projects import adopt_project, new_project


class ProjectProtocolTests(unittest.TestCase):
    def test_discovery_distinguishes_app_types(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "package.json").write_text("{}")
            data = discover(root)
            self.assertEqual(data["primary_type"], "node")
            self.assertIn("node", data["detected"])

    def test_adopt_preserves_existing_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "ExistingApp"
            root.mkdir()
            source = root / "app.py"
            source.write_text("print('keep me')\n")
            result = adopt_project(root)
            self.assertTrue(result["ok"])
            self.assertEqual(source.read_text(), "print('keep me')\n")
            self.assertTrue((root / "BUILD.md").exists())
            self.assertTrue((root / ".dreamsync" / "project.yml").exists())
            self.assertTrue((root / ".dreamsync" / "discovery.json").exists())

    def test_new_creates_durable_protocol(self):
        with tempfile.TemporaryDirectory() as td:
            result = new_project(td, "SampleApp")
            root = Path(result["root"])
            self.assertTrue((root / ".git").exists())
            self.assertTrue((root / "BUILD.md").exists())
            self.assertTrue((root / "ARCHITECTURE.md").exists())
            self.assertTrue((root / "DECISIONS.md").exists())


if __name__ == "__main__":
    unittest.main()
