import unittest.mock as mock
from agent.core import executor
from agent.core.loop import run_agent

SCENARIOS = [
    {
        "name": "find ML jobs",
        "input": "find me ML engineering jobs in NYC",
        "expected_tools": ["search__search_jobs"],
        "min_tool_calls": 3
    },
    {
        "name": "evaluate resume fit",
        "input": "how well does my resume fit the ML engineer role at OpenBCI?",
        "expected_tools": ["evaluate__evaluate_resume_fit"],
        "min_tool_calls": 2
    },
    {
        "name": "first year plan",
        "input": "what would my first year look like as ML engineer at OpenBCI?",
        "expected_tools": ["evaluate__evaluate_first_year_plan"],
        "min_tool_calls": 2
    }
]

class EvalHarness:
    def __init__(self):
        self.results = []
    def run_scenario(self, scenario):
        tools_called = []
        original_execute = executor.execute_tool

        def tracking_execute(tool_name, tool_input):
            tools_called.append(tool_name)
            return original_execute(tool_name, tool_input)
        executor.execute_tool = tracking_execute

        try:
            run_agent(scenario["input"])
        except Exception as e:
            pass
        finally:
            executor.execute_tool = original_execute
        
        self.results.append({
            "scenario": scenario["name"],
            "tools_called": tools_called,
            "passed" : self._score(scenario, tools_called)
        })
    def _score(self, scenario, tools_called):
        expected_met = all(tool in tools_called for tool in scenario["expected_tools"])
        min_calls_met = len(tools_called) >= scenario["min_tool_calls"]
        return expected_met and min_calls_met
    def report(self):
        print("\n=== EVAL RESULTS ===")
        for result in self.results:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status} - {result['scenario']}")
            print(f"  Tools called: {result['tools_called']}")
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        print(f"\n{passed}/{total} scenarios passed")
    def run_all(self):
        for scenario in SCENARIOS:
            self.run_scenario(scenario)
        self.report()

if __name__ == "__main__":
    harness = EvalHarness()
    harness.run_all()
    







