import unittest
from unittest.mock import patch

from dreamsync.receiver import receive_exact


GOOD_SHA = "a" * 40
OLD_SHA = "b" * 40


class ReceiverTests(unittest.TestCase):
    def test_rejects_invalid_sha(self):
        with self.assertRaisesRegex(RuntimeError, "invalid deployment SHA"):
            receive_exact(".", "not-a-sha")

    @patch("dreamsync.receiver.deploy_exact")
    @patch("dreamsync.receiver._git")
    def test_exact_sha_deployment(self, mock_git, mock_deploy):
        def git_result(_root, *args):
            if args == ("status", "--porcelain"):
                return ""
            if args == ("fetch", "origin", "main"):
                return ""
            if args == ("rev-parse", "origin/main"):
                return GOOD_SHA
            if args == ("rev-parse", "HEAD"):
                return OLD_SHA
            if args == ("reset", "--hard", GOOD_SHA):
                return ""
            raise AssertionError(f"unexpected git command: {args}")

        mock_git.side_effect = git_result
        mock_deploy.return_value = {"ok": True, "sha": GOOD_SHA}

        result = receive_exact(".", GOOD_SHA)

        self.assertTrue(result["ok"])
        self.assertEqual(result["sha"], GOOD_SHA)
        mock_deploy.assert_called_once()

    @patch("dreamsync.receiver.deploy_exact")
    @patch("dreamsync.receiver._git")
    def test_refuses_sha_not_on_github_main(self, mock_git, mock_deploy):
        def git_result(_root, *args):
            if args == ("status", "--porcelain"):
                return ""
            if args == ("fetch", "origin", "main"):
                return ""
            if args == ("rev-parse", "origin/main"):
                return OLD_SHA
            raise AssertionError(f"unexpected git command: {args}")

        mock_git.side_effect = git_result

        with self.assertRaisesRegex(RuntimeError, "does not match GitHub"):
            receive_exact(".", GOOD_SHA)

        mock_deploy.assert_not_called()

    @patch("dreamsync.receiver.deploy_exact")
    @patch("dreamsync.receiver._git")
    def test_restores_previous_head_if_deployer_raises(
        self, mock_git, mock_deploy
    ):
        calls = []

        def git_result(_root, *args):
            calls.append(args)
            if args == ("status", "--porcelain"):
                return ""
            if args == ("fetch", "origin", "main"):
                return ""
            if args == ("rev-parse", "origin/main"):
                return GOOD_SHA
            if args == ("rev-parse", "HEAD"):
                return OLD_SHA
            if args in (
                ("reset", "--hard", GOOD_SHA),
                ("reset", "--hard", OLD_SHA),
            ):
                return ""
            raise AssertionError(f"unexpected git command: {args}")

        mock_git.side_effect = git_result
        mock_deploy.side_effect = RuntimeError("deployment exploded")

        with self.assertRaisesRegex(RuntimeError, "deployment exploded"):
            receive_exact(".", GOOD_SHA)

        self.assertIn(("reset", "--hard", OLD_SHA), calls)


if __name__ == "__main__":
    unittest.main()
