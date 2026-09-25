import unittest
from unittest.mock import patch, MagicMock
from dreamsync.deployment import _health

class DeploymentHealthTests(unittest.TestCase):
    @patch("dreamsync.deployment.time.sleep",return_value=None)
    @patch("dreamsync.deployment.urllib.request.urlopen")
    def test_health_retries_until_ready(self,mock_open,_sleep):
        response=MagicMock(); response.status=200
        cm=MagicMock(); cm.__enter__.return_value=response
        mock_open.side_effect=[OSError("warming"),cm]
        self.assertTrue(_health("http://example.invalid",attempts=2,delay=0))
        self.assertEqual(mock_open.call_count,2)
