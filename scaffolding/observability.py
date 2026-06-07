import json
import datetime
import os
os.makedirs('logs', exist_ok=True)


def log_tool_call(tool_name, inputs, result, duration, status):
    os.makedirs('logs', exist_ok=True)
    entry= {
        "tool name": tool_name,
        "inputs": inputs,
        "result": result,
        "timestamp" : datetime.datetime.now().isoformat(),
        "duration": duration,
        "status": status
    }
    with open('logs/agent.log', 'a') as f:
        f.write(json.dumps(entry)+ '\n')
