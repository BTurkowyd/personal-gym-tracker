from silka_agent.workflow import run_agent

if __name__ == "__main__":
    query = (
        "in what exercise I had the largest volume (the weight lifted in all exercises in a single workout) in my workouts? "
        "give me the day, the exercise name, and the volume in a human-readable format, not JSON or code blocks."
    )
    response = run_agent(query)
    print("Final Response:")
    print(response)
