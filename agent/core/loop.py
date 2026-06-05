from agent.core.registry import get_tools_for_api, get_tool
from agent.core.state import load_state, save_state
from agent.core.executor import execute_tool
import anthropic
import json


def run_agent(user_message: str) -> dict: #these act as hints. Ki input should be user_message and output should be a dict. 
    state = load_state()
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_message}]
    response = client.messages.create(
        model ="claude-sonnet-4-20250514",
        max_tokens = 1000,
        tools = get_tools_for_api(),
        messages = messages
    )

    while response.stop_reason == "tool_use":
        tool_use = next(block for block in response.content if block.type == 'tool_use' )
        result = execute_tool(tool_use.name, tool_use.input)
        messages.append({"role": "assistant", "content": response.content})
        messages.append(
            {
                "role": "user",
                "content" : [
                    {
                        "type": "tool_result", 
                        "tool_use_id" : tool_use.id,
                        "content" : json.dumps(result),
                    }
                ],
            }
        )
        save_state(tool_use.name, result)
        response = client.messages.create(
        model ="claude-sonnet-4-20250514",
        max_tokens = 1000,
        tools = get_tools_for_api(),
        messages = messages
    )
    return next(block for block in response.content if block.type == "text").text