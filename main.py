import os
from silka_agent.workflow import run_agent

if __name__ == "__main__":
    query = "how many workouts per month i did where I was doing some leg-related exercises such as squats and leg presses, glutes? return the results in a table format with month, number of workouts, and exercises used"
    os.environ["PROMPT"] = query
    response = run_agent(query)
    print("Final Response:")
    print(response)
