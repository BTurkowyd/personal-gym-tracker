from silka_agent.workflow import run_agent

if __name__ == "__main__":
    query = "when i did my 5 last workouts?"
    response = run_agent(query)
    print("Final Response:")
    print(response)
