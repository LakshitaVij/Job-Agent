from agent.core.registry import get_tools_for_api, get_tool
from agent.core.state import load_state, save_state
from agent.core.executor import execute_tool
import anthropic
import json
import time
from scaffolding.observability import log_tool_call
from scaffolding.retry import retry_with_backoff
from scaffolding.rate_limiter import RateLimiter


def run_agent(user_message: str) -> dict:
    state = load_state()
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_message}]
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        tools=get_tools_for_api(),
        messages=messages
    )
    rate_limiter = RateLimiter(max_calls=50)

    while response.stop_reason == "tool_use":
        tool_uses = [block for block in response.content if block.type == 'tool_use']
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for tool_use in tool_uses:
            start = time.time()
            try:
                rate_limiter.wait_if_needed()
                result = retry_with_backoff(lambda: execute_tool(tool_use.name, tool_use.input))
                duration = time.time() - start
                log_tool_call(tool_use.name, tool_use.input, result, duration, "success")
            except Exception as e:
                duration = time.time() - start
                log_tool_call(tool_use.name, tool_use.input, str(e), duration, "error")
                result = {"error": str(e)}

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": json.dumps(result)
            })
            save_state(tool_use.name, result)

        messages.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            tools=get_tools_for_api(),
            messages=messages
        )

    return next(block for block in response.content if block.type == "text").text