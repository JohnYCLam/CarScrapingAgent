from car_agent.agent import CarScraperAgent

def main():
    agent = CarScraperAgent(enable_aws = False)
    user_id = "local_user"
    session = {}

    # Turn 1
    r1 = agent.process_conversation(user_id, "Mazda CX-3 used car from 2020 under $25000 in Victoria", session)
    print("\n--- R1 ---")
    print(r1["response"])
    session = r1["session_data"]

    # Turn 2 (choose one-time)
    r2 = agent.process_conversation(user_id, "1", session)
    print("\n--- R2 ---")
    print(r2["response"])

if __name__ == "__main__":
    main()
