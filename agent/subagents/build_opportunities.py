from agent.core.registry import get_tools_for_api, get_tool
from agent.core.state import load_state, save_state
from agent.core.executor import execute_tool
import anthropic
import json
from agent.tools.search import fetch_job_description, fetch_my_resume, search_company_pain_points, search_press_coverage
tools = get_tools_for_api("search")


def build_opportunities_subagent(company_name, role, job_url):
    user_message = f"""
You are a research assistant. Your job is to figure out what {company_name} needs and what the candidate could build for them.

1. Fetch the job description from {job_url}
2. Fetch the candidate's resume
3. Search for {company_name}'s pain points
4. Synthesize everything into concrete build opportunities

Return a JSON with:
- build_ideas: list of specific things the candidate could build
- relevant_experiences: which experiences from the resume are most relevant
- talking_points: 3 bullet points for the cold email
"""
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_message}]
    response = client.messages.create(
            model ="claude-sonnet-4-20250514",
            max_tokens = 1000,
            tools = tools,
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
            tools = tools,
            messages = messages
        )
    return next(block for block in response.content if block.type == "text").text