import unittest
from unittest.mock import patch
from agent.tools.search import search_jobs, fetch_job_description

class TestSearchFlow(unittest.TestCase):
    
    @patch('agent.tools.search.requests.get')
    def test_search_jobs_returns_results(self, mock_get):
        mock_get.return_value.json.return_value = {
            "data": [
                {"job_title": "ML Engineer", "employer_name": "OpenBCI"}
            ]
        }
        result = search_jobs("ML Engineer", location="NYC")
        self.assertIn("data", result)
    
    @patch('agent.tools.search.requests.get')
    def test_fetch_job_description_returns_text(self, mock_get):
        mock_get.return_value.text = "<html><body>We are hiring a ML Engineer</body></html>"
        result = fetch_job_description("https://example.com/job")
        self.assertIn("ML Engineer", result)

if __name__ == '__main__':
    unittest.main()