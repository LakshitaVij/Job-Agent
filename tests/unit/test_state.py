import unittest
import os
from agent.core.state import save_state , load_state


class TestStateFunctions(unittest.TestCase):
    def setUp(self):
        #runs before each test and it basically cleans the slate
        if os.path.exists('state/state.json'):
            os.remove('state/state.json')
    def test_load_state_when_no_file(self):
        #if there's no file, what does our load state return?
        result = load_state()
        self.assertEqual(result, {})
    def test_save_and_load(self):
        save_state("search__search_jobs", {"jobs": ["job1", "job2"]})
        loaded = load_state()
        print(loaded)  # add this
        self.assertEqual(loaded["search__search_jobs"], {"jobs": ["job1", "job2"]})

