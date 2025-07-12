import os
from silka_agent.workflow import run_agent

if __name__ == "__main__":
    query = "show me the 20 latest squat with barbells workouts. Dates should be in YYYY-MM-DD format and volume in kg."
    os.environ["PROMPT"] = query
    response = run_agent(query)
    print("Final Response:")
    print(response)
