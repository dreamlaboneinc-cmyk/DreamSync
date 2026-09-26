import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from dreamsync.controller import remote_deploy

GOOD_SHA = "a" * 40


class ControllerTests(unittest.TestCase):
    def config(self, controller=None):
        return SimpleNamespace(
            root=Path(".").resolve(),
            controller=controller or {
                "ssh_target": "sacredlight",
                "remote_project": "/root/apps/DreamSync",
            },
        )

    @patch("dreamsync.controller.subprocess.run")
    @patch("dreamsync.controller._git")
    @patch("dreamsync.controller.load_project")
    def test_remote_deploy_uses_exact_sha_and_project_venv(
        self, mock_load, mock_git, mock_run
    ):
        mock_load.return_value = self.config()
        mock_git.side_effect = ["", GOOD_SHA]
        mock_run.return_value = SimpleNamespace(
            returncode=0, stdout='{"ok": true}', stderr=""
        )

        result = remote_deploy(".", GOOD_SHA)

        self.assertTrue(result["ok"])
        args = mock_run.call_args.args[0]
        self.assertEqual(args[0:2], ["ssh", "sacredlight"])
        self.assertIn("/root/apps/DreamSync/venv/bin/python", args[2])
        self.assertIn(GOOD_SHA, args[2])

    @patch("dreamsync.controller.load_project")
    def test_rejects_unsafe_remote_path(self, mock_load):
        mock_load.return_value = self.config({
            "ssh_target": "sacredlight",
            "remote_project": "/root/apps/DreamSync; touch /tmp/nope",
        })
        with self.assertRaisesRegex(RuntimeError, "invalid remote project path"):
            remote_deploy(".", GOOD_SHA)


if __name__ == "__main__":
    unittest.main()
