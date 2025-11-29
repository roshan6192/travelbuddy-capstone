# amadeus_api.py  (merged, improved, beginner-friendly)
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("AMADEUS_CLIENT_ID/AMADEUS_CLIENT_SECRET not found in .env")

# Endpoints (test environment)
TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
FLIGHT_OFFERS_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"
LOCATION_SEARCH_URL = "https://test.api.amadeus.com/v1/reference-data/locations"
HOTEL_BY_CITY_URL = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
HOTEL_OFFERS_URL = "https://test.api.amadeus.com/v3/shopping/hotel-offers"

# Simple in-memory token cache (for demo)
_token_cache = {"access_token": None, "expires_at": 0}


def _get_new_token():
    resp = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data["access_token"]
    # expiry in seconds (if provided)
    expires_in = data.get("expires_in", 1800)
    _token_cache["access_token"] = token
    _token_cache["expires_at"] = time.time() + expires_in - 60  # refresh 60s before expiry
    return token


def get_access_token():
    """
    Return a cached token if valid, otherwise request a new one.
    """
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["access_token"]
    return _get_new_token()


def city_to_iata(city_name: str, country_code: str = None):
    """
    Use Amadeus Reference Data Locations endpoint to find a CITY or AIRPORT iataCode.
    Returns e.g. 'PAR' or 'CDG' or None.
    """
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"keyword": city_name, "subType": "CITY", "page[limit]": 10}
    if country_code:
        params["countryCode"] = country_code

    try:
        resp = requests.get(LOCATION_SEARCH_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        for item in data:
            iata = item.get("iataCode")
            if iata:
                return iata
        # fallback to AIRPORT subtype
        params["subType"] = "AIRPORT"
        resp = requests.get(LOCATION_SEARCH_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        for item in resp.json().get("data", []):
            iata = item.get("iataCode")
            if iata:
                return iata
    except Exception as e:
        # Return None on failure — higher-level code will handle it
        return None
    return None


def search_flight_offers(origin: str, destination: str, departDate: str, returnDate: str = None, adults: int = 1, maxResults: int = 5):
    """
    Simple wrapper around Amadeus Flight Offers search (test endpoint).
    origin/destination: IATA codes like 'PAR', 'BER'
    departDate / returnDate: 'YYYY-MM-DD'
    """
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departDate,
        "adults": adults,
        "max": maxResults,
    }
    if returnDate:
        params["returnDate"] = returnDate

    try:
        resp = requests.get(FLIGHT_OFFERS_URL, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        offers = data.get("data", [])
        result = []
        for offer in offers:
            price = offer.get("price", {}).get("grandTotal")
            itineraries = offer.get("itineraries", [])
            result.append({
                "price": price,
                "itineraries": itineraries,
                "raw": offer
            })
        return result
    except requests.HTTPError as e:
        # Provide readable error for debugging
        try:
            return [{"error": f"HTTPError: {e.response.status_code} {e.response.text}"}]
        except Exception:
            return [{"error": str(e)}]
    except Exception as e:
        return [{"error": str(e)}]


def search_hotels_by_city(city_code: str, radius: int = 5):
    """
    Get hotels around a city using Amadeus Hotel List (reference data).
    city_code example: 'PAR' for Paris
    """
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"cityCode": city_code, "radius": radius, "radiusUnit": "KM"}

    try:
        resp = requests.get(HOTEL_BY_CITY_URL, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        hotels = []
        for item in data.get("data", []):
            hotels.append({
                "hotelId": item.get("hotelId"),
                "name": item.get("name"),
                "latitude": item.get("geoCode", {}).get("latitude"),
                "longitude": item.get("geoCode", {}).get("longitude"),
            })
        return hotels
    except Exception as e:
        return [{"error": str(e)}]


def search_hotel_offers(city_code: str, check_in: str, check_out: str, adults: int = 1, max_results: int = 5):
    """
    Hotel offers using Amadeus /v3/shopping/hotel-offers
    check_in/check_out format: 'YYYY-MM-DD'
    """
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "cityCode": city_code,
        "checkInDate": check_in,
        "checkOutDate": check_out,
        "adults": adults,
        "roomQuantity": 1,
        "bestRateOnly": False
    }

    try:
        resp = requests.get(HOTEL_OFFERS_URL, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        offers_result = []
        for hotel in data.get("data", []):
            hotel_info = hotel.get("hotel", {})
            hotel_offers = hotel.get("offers", [])
            for offer in hotel_offers[:max_results]:
                offers_result.append({
                    "hotel_name": hotel_info.get("name"),
                    "rating": hotel_info.get("rating"),
                    "address": hotel_info.get("address", {}).get("lines", []),
                    "price": offer.get("price", {}).get("total"),
                    "currency": offer.get("price", {}).get("currency"),
                    "check_in": offer.get("checkInDate"),
                    "check_out": offer.get("checkOutDate")
                })
        return offers_result
    except Exception as e:
        return [{"error": str(e)}]
