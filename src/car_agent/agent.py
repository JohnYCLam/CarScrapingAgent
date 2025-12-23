from __future__ import annotations

from typing import Any, Dict, List

from car_agent.aws.clients import build_dynamodb, build_scheduler, build_ses
from car_agent.aws.emailer import Emailer
from car_agent.aws.scheduler import Scheduler
from car_agent.aws.storage import Storage
from car_agent.config import Settings
from car_agent.llm.client import build_llm
from car_agent.llm.extractors import extract_car_criteria, extract_schedule_details
from car_agent.scraping.drive_scraper import scrape_drive


class CarScraperAgent:
    def __init__(self, settings: Settings | None = None, enable_aws: bool = True):
        self.settings = settings or Settings()

        # LLM
        self.llm = build_llm(self.settings)

        # AWS
        if enable_aws:
            dynamodb = build_dynamodb(self.settings)
            ses = build_ses(self.settings)
            scheduler_client = build_scheduler(self.settings)

            self.storage = Storage(dynamodb, self.settings)
            self.emailer = Emailer(ses, self.settings)
            self.scheduler = Scheduler(scheduler_client, self.settings)
        else:
            self.storage = None
            self.emailer = None
            self.scheduler = None

    def extract_car_details(self, user_input: str) -> Dict[str, Any]:
        return extract_car_criteria(self.llm, user_input)

    def extract_schedule_details(self, user_input: str) -> Dict[str, Any]:
        return extract_schedule_details(self.llm, user_input)

    def scrape_cars(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        # You can add other sources later; keep this method stable.
        results = scrape_drive(criteria, llm=self.llm, max_results=3, max_page=1)
        return results
    # ----- Conversation flow (mostly unchanged, just cleaned) -----

    def ask_update_preference(self) -> str:
        return (
            "Would you like this to be:\n"
            "1. A one-time search (I'll show results right away)\n"
            "2. Regular updates (I'll email you new listings periodically)\n\n"
            "Please specify 1 or 2."
        )

    def format_criteria(self, criteria: Dict[str, Any]) -> str:
        parts = []
        if criteria.get("make"):
            parts.append(criteria["make"])
        if criteria.get("model"):
            parts.append(criteria["model"])

        y_min, y_max = criteria.get("year_min"), criteria.get("year_max")
        if y_min or y_max:
            if y_min and y_max:
                parts.append(f"{y_min}-{y_max}")
            elif y_min:
                parts.append(f"{y_min} or newer")
            else:
                parts.append(f"up to {y_max}")

        if criteria.get("price_max"):
            parts.append(f"under ${criteria['price_max']:,}")
        if criteria.get("mileage_max"):
            parts.append(f"under {criteria['mileage_max']:,} km")
        if criteria.get("location"):
            parts.append(f"in {criteria['location']}")

        return " ".join(parts)

    def format_results(self, results: List[Dict[str, Any]]) -> str:
        if not results:
            return "No listings found matching your criteria."

        out = [f"Found {len(results)} listings:\n"]
        for i, car in enumerate(results[:10], 1):
            price = car.get("price")
            price_str = f"${price:,}" if isinstance(price, int) else "N/A"
            out.append(
                f"{i}. {car.get('name','N/A')}\n"
                f"   Price: {price_str}\n"
                f"   Mileage: {car.get('mileage','N/A')} km\n"
                f"   Year: {car.get('year','N/A')}\n"
                f"   Location: {car.get('location','N/A')}\n"
                f"   URL: {car.get('url','N/A')}\n"
            )
        if len(results) > 10:
            out.append(f"... and {len(results)-10} more listings")
        return "\n".join(out)

    def process_conversation(self, user_id: str, message: str, session_data: Dict[str, Any]) -> Dict[str, Any]:

        print(f"[DEBUG] Input - user: {user_id}, msg: '{message}', session keys: {list(session_data.keys())}")

        state = session_data.get("state", "INITIAL")
        criteria = session_data.get("criteria", {})

        # === ALWAYS RE-PARSE MESSAGE for potential criteria updates ===
        fresh_criteria = self.extract_car_details(message)
        if fresh_criteria:
            print(f"[DEBUG] Fresh criteria from LLM: {fresh_criteria}")
            # MERGE: fresh overrides stale session criteria
            criteria = {**criteria, **fresh_criteria}
            print(f"[DEBUG] Merged criteria: {criteria}")


        if state == "INITIAL" or not criteria:
            if fresh_criteria:
                session_data["criteria"] = criteria
                session_data["state"] = "ASK_UPDATE_TYPE"
                return {
                    "response": f"Got it! You're looking for: {self.format_criteria(criteria)}\n\n"
                            f"Would you like this to be:\n"
                            f"1. A one-time search (I'll show results right away)\n"
                            f"2. Regular updates (I'll email you new listings periodically)\n\n"
                            f"Please specify 1 or 2.",
                    "session_data": session_data,
                    "action": "continue"
                }
            else:
                return {
                    "response": "I couldn't understand your search criteria. Example: '2018 Toyota Camry under $25,000 in Sydney'.",
                    "session_data": session_data,
                    "action": "continue"
                }

        if state == "ASK_UPDATE_TYPE":
            msg = (message or "").lower().strip()

            if msg in ("1", "one", "one time", "one-time"):
                results = self.scrape_cars(session_data["criteria"])

                if self.storage:
                    self.storage.store_search(user_id, session_data["criteria"], results, "one-time")
                return {"response": f"Here are the results:\n\n{self.format_results(results)}", "session_data": {}, "action": "complete"}

            if msg in ("2", "regular", "updates", "regular updates"):
                session_data["state"] = "ASK_SCHEDULE"
                return {
                    "response": (
                        "Please provide:\n"
                        "1) How often? (daily/weekly/every 3 days)\n"
                        "2) Your email\n"
                        "3) Optional end date (YYYY-MM-DD)\n\n"
                        "Example: 'Send me daily updates to john@example.com, stop after 2025-12-31'"
                    ),
                    "session_data": session_data,
                    "action": "continue",
                }

            return {"response": "Please choose 1 (one-time) or 2 (regular updates).", "session_data": session_data, "action": "continue"}

        if state == "ASK_SCHEDULE":
            sched = self.extract_schedule_details(message)
            if not (sched.get("email") and sched.get("frequency")):
                return {"response": "I need both your email and frequency (e.g., daily/weekly).", "session_data": session_data, "action": "continue"}
            
            query_id = None
            if self.storage:
                query_id = self.storage.store_recurring_query(user_id, session_data["criteria"], sched)
            if query_id:
                self.scheduler.create_schedule(query_id, sched)

            return {"response": f"Set up {sched['frequency']} updates to {sched['email']}.", "session_data": {}, "action": "complete"}

        return {"response": "Something went wrong. Let's start over. What car are you looking for?", "session_data": {}, "action": "restart"}
