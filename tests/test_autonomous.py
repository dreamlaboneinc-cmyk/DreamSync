import tempfile, unittest
from pathlib import Path
from dreamsync.autonomous import _json_object, apply_operations

class AutonomousTests(unittest.TestCase):
    def test_json_fence_tolerated(self):
        self.assertEqual(_json_object('```json\n{"operations":[]}\n```')["operations"],[])
    def test_safe_write(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            changed=apply_operations(root,{"operations":[{"action":"write","path":"src/a.py","content":"x=1\n"}]})
            self.assertEqual(changed,["src/a.py"])
            self.assertEqual((root/"src/a.py").read_text(),"x=1\n")
