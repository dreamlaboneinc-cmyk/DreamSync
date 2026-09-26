import tempfile
import unittest
from pathlib import Path

from dreamsync.config import load_project


class ConfigTests(unittest.TestCase):
    def test_local_config_merges_without_replacing_project_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / ".dreamsync"
            config_dir.mkdir()

            (config_dir / "project.yml").write_text(
                """
project:
  name: TestProject
mode: AUTONOMOUS
verification:
  test:
    - python -m unittest
"""
            )

            (config_dir / "local.yml").write_text(
                """
controller:
  platform: windows
  ssh_target: sacredlight
  remote_project: /root/apps/DreamSync
"""
            )

            cfg = load_project(root)

            self.assertEqual(cfg.raw["project"]["name"], "TestProject")
            self.assertEqual(cfg.raw["mode"], "AUTONOMOUS")
            self.assertEqual(cfg.controller["platform"], "windows")
            self.assertEqual(cfg.controller["ssh_target"], "sacredlight")
            self.assertEqual(
                cfg.controller["remote_project"],
                "/root/apps/DreamSync",
            )


if __name__ == "__main__":
    unittest.main()
