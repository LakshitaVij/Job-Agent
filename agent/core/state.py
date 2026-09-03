from agent.core.registry import get_tools_for_api, get_tool
import anthropic
import json

def load_state():
    try:
        with open ('state/state.json', 'r') as file:
            content = file.read()
            if not content:
                return {}
            return json.loads(content)
    except FileNotFoundError:
        return {}

def save_state(tool_name, result):
    state = load_state()
    state[tool_name] = result
    with open('state/state.json', 'w') as f:
        json.dump(state, f)

def save_messages(messages):
    serializable = []
    for msg in messages:
        if isinstance(msg["content"], str):
            serializable.append(msg)
        elif isinstance(msg["content"], list):
            content = []
            for block in msg["content"]:
                if hasattr(block, "model_dump"):
                    content.append(block.model_dump())
                elif isinstance(block, dict):
                    content.append(block)
            serializable.append({"role": msg["role"], "content": content})
        else:
            serializable.append(msg)
    
    with open('state/messages.json', 'w') as f:
        json.dump(serializable, f)
def load_messages():
    try:
        with open('state/messages.json', 'r') as f:
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except FileNotFoundError:
        return []

    





