import logging

from agents import TripPlannerAgent, BookingAgent, SafetyAgent, BudgetAgent
from memory import get_user_preferences, update_user_preferences

logging.basicConfig(level=logging.INFO)

class TravelBuddyCoordinator:
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.planner = TripPlannerAgent()
        self.booking = BookingAgent()
        self.safety = SafetyAgent()
        self.budget = BudgetAgent()

    def handle_request(self, user_request: str, budget: float = 1000.0) -> dict:
        logging.info("Starting new TravelBuddy request")
        logging.info(f"User request: {user_request}")

        # 🔹 Load user preferences from memory
        user_prefs = get_user_preferences(self.user_id)
        logging.info(f"Loaded user preferences: {user_prefs}")

        # 🔹 Enrich the request with known preferences
        enriched_request = f"""
        User request: {user_request}
        Known user preferences: {user_prefs}
        """

        logging.info("Calling TripPlannerAgent")
        trip_plan = self.planner.plan_trip(enriched_request)
        if isinstance(trip_plan, dict):
            trip_plan["user_request"] = enriched_request


        logging.info("Calling BookingAgent")
        bookings = self.booking.suggest_bookings(trip_plan)

        logging.info("Calling SafetyAgent")
        safety = self.safety.check_safety(trip_plan)

        logging.info("Calling BudgetAgent")
        budget_result = self.budget.check_budget(trip_plan, bookings, budget)

        # 🔹 Update memory (simple example)
        logging.info("Updating user memory")
        update_user_preferences(self.user_id, {"last_budget": budget})

        logging.info("Finished TravelBuddy request")

        return {
            "trip_plan": trip_plan,
            "bookings": bookings,
            "safety": safety,
            "budget": budget_result,
        }
