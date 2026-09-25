import tempfile, unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from dreamsync.dream_api import DreamAPIClient, DreamAPIError

class DreamAPIAuthTests(unittest.TestCase):
    def test_missing_key_is_blocked(self):
        with self.assertRaises(DreamAPIError):
            DreamAPIClient(key_path="/definitely/missing")._headers()
    def test_key_loaded_without_embedding(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"client.key"; p.write_text("abc")
            self.assertEqual(DreamAPIClient(key_path=str(p))._headers()["Authorization"],"Bearer abc")
