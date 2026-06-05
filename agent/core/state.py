from agent.core.registry import get_tools_for_api, get_tool
import anthropic
import json

def load_state():
    try:
        with open ('state/state.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_state(tool_name, result):
    state = load_state()
    state[tool_name] = result
    with open('state/state.json', 'w') as f:
        json.dumps(state)
    

    





