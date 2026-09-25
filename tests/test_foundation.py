import unittest
from pathlib import Path
from dreamsync.config import load_project
from dreamsync.scanner import scan_repo

ROOT=Path(__file__).resolve().parents[1]
class FoundationTests(unittest.TestCase):
    def test_manifest_is_autonomous_free_core(self):
        c=load_project(ROOT)
        self.assertEqual(c.raw["mode"],"AUTONOMOUS")
        self.assertEqual(c.ai["provider"],"dream-api")
        self.assertEqual(c.ai["billing_mode_required"],"FREE_ONLY")
    def test_repo_scan(self):
        s=scan_repo(ROOT)
        self.assertGreater(s["files"],0)
        self.assertIn("requirements.txt",s["manifests"])
if __name__=="__main__": unittest.main()
