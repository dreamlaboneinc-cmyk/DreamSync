import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dreamsync.drift import save, compare_saved
from dreamsync.intent import classify
import dreamsync.autonomous as autonomous

class Phase2Tests(unittest.TestCase):
    def test_extended_intents(self):
        expected={'plan this':'plan','verify this':'verify','deploy this':'deploy','inspect this':'discover','fix bug':'debug','upgrade feature':'upgrade','build app':'build','status':'status'}
        for text,action in expected.items(): self.assertEqual(classify(text).action,action)

    def test_drift_detection(self):
        base=Path(tempfile.mkdtemp()); repo=base/'repo'; live=base/'live'; repo.mkdir(); live.mkdir()
        (live/'app.py').write_text('good')
        save(repo,live,'a'*40)
        self.assertTrue(compare_saved(repo,live)['ok'])
        (live/'app.py').write_text('changed')
        result=compare_saved(repo,live)
        self.assertFalse(result['ok']); self.assertEqual(result['drift'],['app.py'])

    def test_ask_user_state(self):
        root=Path(tempfile.mkdtemp())
        with patch.object(autonomous,'propose',return_value={'operations':[],'ask_user':'Which database?'}):
            result=autonomous.run_autonomous(root,'dangerous operation')
        self.assertEqual(result['phase'],'ASK_USER')
        self.assertEqual(result['question'],'Which database?')

if __name__ == '__main__': unittest.main()
