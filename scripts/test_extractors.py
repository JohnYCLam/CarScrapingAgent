from car_agent.agent import CarScraperAgent

def main():
    agent = CarScraperAgent(enable_aws=False)

    msg = "I'm looking for a Mazda CX-3 from 2020 onwards under $25000."
    criteria = agent.extract_car_details(msg)
    print("criteria =", criteria)

    sched_msg = "Send me weekly updates to john@example.com, stop after 2026-01-31"
    schedule = agent.extract_schedule_details(sched_msg)
    print("schedule =", schedule)

if __name__ == "__main__":
    main()
