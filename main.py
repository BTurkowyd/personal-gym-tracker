import os
from silka_agent.workflow import run_agent

if __name__ == "__main__":
    query = "on what days i did my squats with barbell, where the average rep weight in the single set was above 90kg. list all the sets with the date, weight and reps."
    os.environ["PROMPT"] = query
    response = run_agent(query)
    print("Final Response:")
    print(response)
