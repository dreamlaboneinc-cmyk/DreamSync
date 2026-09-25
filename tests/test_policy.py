import unittest
from pathlib import Path
from dreamsync.policy import assert_patch_path
ROOT=Path(__file__).resolve().parents[1]
class PolicyTests(unittest.TestCase):
    def test_reject_escape(self):
        with self.assertRaises(ValueError): assert_patch_path(ROOT,"../outside")
    def test_reject_env(self):
        with self.assertRaises(PermissionError): assert_patch_path(ROOT,".env")
    def test_reject_backup(self):
        with self.assertRaises(PermissionError): assert_patch_path(ROOT,"backups/a.py")
    def test_allow_source(self):
        self.assertTrue(str(assert_patch_path(ROOT,"dreamsync/cli.py")).endswith("dreamsync/cli.py"))
