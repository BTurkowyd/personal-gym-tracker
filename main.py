import os
from silka_agent.workflow import run_agent

if __name__ == "__main__":
    query = (
        "return the five first workouts. Return the days and exercises in each workout."
    )
    os.environ["PROMPT"] = query
    response = run_agent(query)
    print("Final Response:")
    print(response)
