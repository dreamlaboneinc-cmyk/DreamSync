import unittest
from pathlib import Path
from dreamsync.config import load_project
from dreamsync.verify import SECRET_RULES

class PromotionDeployTests(unittest.TestCase):
    def setUp(self): self.root=Path(__file__).resolve().parents[1]
    def test_exact_sha_and_rollback_required(self):
        dep=load_project(self.root).raw["deploy"]
        self.assertTrue(dep["exact_sha"]); self.assertTrue(dep["rollback"])
    def test_secret_rules_exist(self):
        self.assertIn("private-key",SECRET_RULES)
        self.assertIn("github-token",SECRET_RULES)
