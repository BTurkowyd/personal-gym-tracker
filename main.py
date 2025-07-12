from silka_agent.workflow import run_agent

if __name__ == "__main__":
    query = "can you show me my bench press with a barbell progression ovrer years 2023 and 2024?"
    response = run_agent(query)
    print("Final Response:")
    print(response)
