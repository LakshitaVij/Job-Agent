from agent.core.registry import get_tools_for_api, get_tool
from agent.core.state import load_state, save_state
import anthropic
import json
import importlib


def execute_tool(tool_name, tool_input):
    namespace, name = tool_name.split("__")
    module = importlib.import_module(f"agent.tools.{namespace}")
    func = getattr(module,name)
    result = func(**tool_input)
    return result