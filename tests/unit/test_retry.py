import unittest
import os
from agent.core.state import save_state , load_state
from scaffolding.retry import retry_with_backoff
class TestRetry(unittest.TestCase):
    
    def test_succeeds_on_first_try(self):
        result = retry_with_backoff(lambda: "success")
        self.assertEqual(result, "success")
        pass
    
    def test_fails_after_max_retries(self):
        def always_fails():
            raise Exception("broken")
        
        with self.assertRaises(Exception):
            retry_with_backoff(always_fails, max_retries=2)