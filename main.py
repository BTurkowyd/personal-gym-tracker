import os
from silka_agent.workflow import run_agent

if __name__ == "__main__":
    query = "how many workouts in total are recorded?"
    os.environ["PROMPT"] = query
    response = run_agent(query)
    print("Final Response:")
    print(response)
