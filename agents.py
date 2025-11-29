from agent_client import ask_gemini
from utils import cleanup_json
from date_utils import extract_dates_from_text
from amadeus_api import search_flight_offers, search_hotel_offers, city_to_iata
from country_info_api import get_country_info
from weather_api import get_weather
from datetime import datetime, timedelta

class TripPlannerAgent:
    def plan_trip(self, user_request: str) -> dict:
        """
        Ask Gemini to create a structured trip plan and return it as a dict.
        """
        prompt = f"""
        You are the Trip Planner Agent in a multi-agent travel system.

        User request and preferences:
        {user_request}

        Your job:
        - Propose a structured trip plan.
        - Use a list of cities, number of days, and daily activities.
        - Include a constraints section (budget, travel_style, transportation, accommodation).

        Respond STRICTLY in valid JSON with this structure:

        {{
          "summary": "string",
          "city": ["Paris", "Brussels"],
          "days": 7,
          "daily_plan": [
            {{
              "day": 1,
              "city": "Paris",
              "activities": [
                "Visit Eiffel Tower",
                "Walk along the Seine"
              ]
            }}
          ],
          "constraints": {{
            "budget": "string",
            "travel_style": "string",
            "transportation": "string",
            "accommodation": "string"
          }}
        }}
        """

        raw = ask_gemini(prompt)
        data = cleanup_json(raw)
        # If parsing failed, still wrap in dict
        if not isinstance(data, dict):
            return {"summary": str(data)}
        return data


class BookingAgent:
    def suggest_bookings(self, trip_plan: dict) -> dict:
        """
        Uses:
        - LLM for hotel/activity ideas
        - Amadeus API for real flights
        - Date parser for dynamic departure/return dates
        """

        # Extract original user request for date parsing
        user_request_text = trip_plan.get("user_request", "")

        # 1. Parse dates
        depart_date, return_date = extract_dates_from_text(user_request_text)

        # 2. Identify cities
        cities = trip_plan.get("city", [])
        flights = []
        hotels = []
        activities = []

        # LLM for hotel/activity content (you already have this)
        llm_prompt = f"""
        You are the Booking Agent. Based on this trip plan:
        {trip_plan}

        Return JSON:
        {{
            "hotels": [...],
            "activities": [...]
        }}
        """
        raw = ask_gemini(llm_prompt)
        parsed = cleanup_json(raw)

        if isinstance(parsed, dict):
            hotels = parsed.get("hotels", [])
            activities = parsed.get("activities", [])

        # 3. Flight search: first→last city
        if len(cities) >= 2:
            origin_city = cities[0]
            dest_city = cities[-1]

            origin_iata = city_to_iata(origin_city)
            dest_iata = city_to_iata(dest_city)

            if origin_iata and dest_iata:
                flights = search_flight_offers(
                    origin=origin_iata,
                    destination=dest_iata,
                    departDate=depart_date,
                    returnDate=return_date,
                    adults=1,
                    maxResults=5
                )
            else:
                flights = [{
                    "error": "Could not map city to IATA",
                    "origin_city": origin_city,
                    "dest_city": dest_city,
                    "origin_iata": origin_iata,
                    "dest_iata": dest_iata
                }]
        else:
            flights = [{"error": "Not enough cities for flight search"}]

        return {
            "depart_date": depart_date,
            "return_date": return_date,
            "flights": flights,
            "hotels": hotels,
            "activities": activities
        }


class SafetyAgent:
    def check_safety(self, trip_plan: dict) -> dict:
        """
        Combines:
        - Real weather data (OpenWeather)
        - Country profile data (REST Countries)
        - Gemini safety reasoning
        """

        # 1) Get cities from trip plan
        cities = trip_plan.get("city") or []

        # 2) Real-time weather data
        weather_data = [get_weather(city) for city in cities]

        # Map city to country code
        city_to_country = {
            "Paris": "FR",
            "Brussels": "BE",
            "Amsterdam": "NL",
            "Berlin": "DE",
            "Kyoto": "JP"
        }

        # 3) Country info data
        country_profiles = []
        for city in cities:
            code = city_to_country.get(city)
            if code:
                country_profiles.append(get_country_info(code))
            else:
                country_profiles.append({"city": city, "error": "no country mapping"})

        # 4) Ask Gemini to reason about risks
        prompt = f"""
        You are the Safety and Compliance Agent.

        TRIP PLAN:
        {trip_plan}

        REAL WEATHER DATA:
        {weather_data}

        COUNTRY PROFILES:
        {country_profiles}

        Based on all this information, return STRICT JSON:

        {{
          "overall_risk": "Low | Moderate | High",
          "city_safety_notes": [
            {{
              "city": "string",
              "weather_risk": "string",
              "country_risk": "string",
              "guidelines": ["string", "string"]
            }}
          ],
          "general_recommendations": ["string", "string"]
        }}
        """

        raw = ask_gemini(prompt)
        data = cleanup_json(raw)

        # ensure robustness
        if not isinstance(data, dict):
            return {
                "overall_risk": "unknown",
                "city_safety_notes": [{"error": str(data)}],
                "general_recommendations": [],
                "weather_data": weather_data,
                "country_profiles": country_profiles
            }

        # Always attach real data to final output
        data["weather_data"] = weather_data
        data["country_profiles"] = country_profiles

        return data

class BudgetAgent:
    """
    Estimate trip costs and compare to user budget.
    Returns a structured dict:
    {
      "estimated_total": {
         "accommodation": "...",
         "transportation": "...",
         "food": "...",
         "activities": "...",
         "total_estimate": "..."
      },
      "within_budget": "yes"|"no"|"unknown",
      "adjustments": ["..."]
    }
    """

    def check_budget(self, trip_plan: dict, bookings: dict, budget: float) -> dict:
        # Defensive defaults
        if not isinstance(trip_plan, dict):
            trip_plan = {"summary": str(trip_plan)}
        if not isinstance(bookings, dict):
            bookings = {}

        prompt = f"""
        You are the Budget Agent in a travel assistant system.

        Trip plan (structured):
        {trip_plan}

        Booking suggestions (flights/hotels/activities):
        {bookings}

        User budget (USD): {budget}

        Tasks:
        - Provide an estimated cost breakdown for accommodation, transportation, food, and activities.
        - Provide a total estimate.
        - Indicate whether the total is within the user's budget ("yes" or "no").
        - Suggest 2-3 practical adjustments to fit budget if it's over.

        Respond STRICTLY in valid JSON with the following keys:
        {{
          "estimated_total": {{
            "accommodation": "string",
            "transportation": "string",
            "food": "string",
            "activities": "string",
            "total_estimate": "string"
          }},
          "within_budget": "yes" or "no" or "unknown",
          "adjustments": ["string", "string"]
        }}
        """

        raw = ask_gemini(prompt)
        parsed = cleanup_json(raw)

        # If parsed JSON is not dict, return safe fallback
        if not isinstance(parsed, dict):
            return {
                "estimated_total": {"total_estimate": str(parsed)},
                "within_budget": "unknown",
                "adjustments": []
            }

        # Ensure keys exist
        estimated = parsed.get("estimated_total", {})
        within = parsed.get("within_budget", "unknown")
        adjustments = parsed.get("adjustments", [])

        return {
            "estimated_total": estimated,
            "within_budget": within,
            "adjustments": adjustments
        }   


def _safe_call_amadeus(origin_iata: str, dest_iata: str, depart_date: str, return_date: str = None):
    """
    Validate and sanitize dates, then call Amadeus search_flight_offers.
    Returns either:
      - list of offers (as returned by search_flight_offers)
      - or [{'error': '...'}] on validation or API error
    """
    # Validate depart_date format
    try:
        d_dt = datetime.strptime(depart_date, "%Y-%m-%d")
    except Exception:
        return [{"error": f"Invalid depart_date format: {depart_date}. Expected YYYY-MM-DD"}]

    # Validate / sanitize return_date
    if return_date:
        try:
            r_dt = datetime.strptime(return_date, "%Y-%m-%d")
        except Exception:
            # fallback: set return 7 days after depart
            r_dt = d_dt + timedelta(days=7)
            return_date = r_dt.strftime("%Y-%m-%d")
    else:
        r_dt = d_dt + timedelta(days=7)
        return_date = r_dt.strftime("%Y-%m-%d")

    # Ensure return_date is not earlier than depart_date
    if r_dt < d_dt:
        r_dt = d_dt + timedelta(days=7)
        return_date = r_dt.strftime("%Y-%m-%d")

    # Ensure depart is in the future (if not, push to next reasonable future date)
    now = datetime.utcnow()
    if d_dt < now:
        # If depart is in the past, shift it forward to next year (keeping day/month)
        try:
            d_dt = d_dt.replace(year=now.year if d_dt.month >= now.month else now.year + 1)
        except Exception:
            d_dt = now + timedelta(days=14)
        # Recompute return date relative to new depart
        r_dt = d_dt + timedelta(days=(r_dt - d_dt).days if (r_dt and r_dt > d_dt) else 7)
        depart_date = d_dt.strftime("%Y-%m-%d")
        return_date = r_dt.strftime("%Y-%m-%d")

    # Final sanity: if still invalid, return error
    if not origin_iata or not dest_iata:
        return [{"error": "Missing IATA codes for origin or destination", "origin_iata": origin_iata, "dest_iata": dest_iata}]

    # Call Amadeus (wrapped in try/except by search_flight_offers)
    try:
        offers = search_flight_offers(
            origin=origin_iata,
            destination=dest_iata,
            departDate=d_dt.strftime("%Y-%m-%d"),
            returnDate=r_dt.strftime("%Y-%m-%d"),
            adults=1,
            maxResults=5
        )
        return offers
    except Exception as e:
        return [{"error": f"Amadeus call failed: {str(e)}"}]


class BookingAgent:
    def suggest_bookings(self, trip_plan: dict) -> dict:
        """
        Uses:
        - Gemini for hotel/activity ideas (LLM)
        - Amadeus (via _safe_call_amadeus) for robust flight search
        - date_utils.extract_dates_from_text for dynamic dates
        """

        # 0. Defensive defaults
        if not isinstance(trip_plan, dict):
            trip_plan = {"summary": str(trip_plan)}

        # 1. Extract original user request text (coordinator should have inserted it)
        user_request_text = trip_plan.get("user_request", "") or str(trip_plan.get("summary", ""))

        # 2. Parse dates (depart_date, return_date)
        depart_date, return_date = extract_dates_from_text(user_request_text)

        # 3. Ask Gemini for hotels + activities (LLM)
        llm_prompt = f"""
        You are the Booking Agent. Based on this trip plan:
        {trip_plan}

        Return STRICT JSON with:
        {{
          "hotels": [
            {{
              "city": "string",
              "hotel": "string",
              "approx_price_per_night": number
            }}
          ],
          "activities": [
            {{
              "day": number,
              "city": "string",
              "activities": ["string", "string"]
            }}
          ]
        }}
        """
        llm_raw = ask_gemini(llm_prompt)
        llm_parsed = cleanup_json(llm_raw)
        hotels = llm_parsed.get("hotels", []) if isinstance(llm_parsed, dict) else []
        activities = llm_parsed.get("activities", []) if isinstance(llm_parsed, dict) else []

        # 4. Flights: map first -> last city to IATA and call Amadeus safely
        cities = trip_plan.get("city") or trip_plan.get("cities") or []
        flights = []

        if isinstance(cities, list) and len(cities) >= 2:
            origin_city = cities[0]
            dest_city = cities[-1]

            origin_iata = city_to_iata(origin_city)
            dest_iata = city_to_iata(dest_city)

            # Use the safe wrapper which validates dates and fixes obvious issues
            flights = _safe_call_amadeus(origin_iata, dest_iata, depart_date, return_date)
        else:
            flights = [{"error": "Not enough cities to perform flight search", "cities": cities}]

        # 5. Optionally include hotel offers if check-in/out dates parsed
        hotel_offers = []
        try:
            # if dates are available and hotels are requested, try hotel offers
            if depart_date and return_date and hotels:
                # Try map first hotel's city to IATA/city code (Amadeus expects city codes)
                first_hotel = hotels[0]
                city_name = first_hotel.get("city") if isinstance(first_hotel, dict) else None
                if city_name:
                    city_code = city_to_iata(city_name)
                    if city_code:
                        hotel_offers = search_hotel_offers(city_code, depart_date, return_date, adults=1, max_results=3)
        except Exception:
            # Non-fatal — keep proceeding
            hotel_offers = [{"error": "Hotel offers lookup failed"}]

        return {
            "depart_date": depart_date,
            "return_date": return_date,
            "flights": flights,
            "hotels": hotels,
            "hotel_offers": hotel_offers,
            "activities": activities
        }

