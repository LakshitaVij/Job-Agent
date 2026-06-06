
from dotenv import load_dotenv
from agent.core.loop import run_agent

load_dotenv()


if __name__ == "__main__":
    user_message = input("What would you like to do? ")
    result = run_agent(user_message)
    print(result)