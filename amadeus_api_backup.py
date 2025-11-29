import os
import requests
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

# Get access token
def get_access_token():
    token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    resp = requests.post(token_url, headers=headers, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]

def search_flight_offers(origin: str, destination: str, departDate: str, returnDate: str = None, adults: int = 1, maxResults: int = 5):
    token = get_access_token()
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departDate,
        "adults": adults,
        "max": maxResults
    }
    if returnDate:
        params["returnDate"] = returnDate

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()
    offers = data.get("data", [])
    result = []
    for offer in offers:
        price = offer.get("price", {}).get("grandTotal")
        itineraries = offer.get("itineraries", [])
        result.append({
            "price": price,
            "itineraries": itineraries
        })
    return result

def search_hotels_by_city(city_code: str, radius: int = 5):
    """
    Get hotels around a city using Amadeus Hotel List.
    city_code example:
        - "PAR" for Paris
        - "BER" for Berlin
        - "AMS" for Amsterdam
    """

    token = get_access_token()
    url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"

    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "cityCode": city_code,
        "radius": radius,
        "radiusUnit": "KM"
    }

    resp = requests.get(url, headers=headers, params=params)
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



def search_hotel_offers(city_code: str, check_in: str, check_out: str, adults: int = 1, max_results: int = 5):
    """
    Real hotel price + availability search using Amadeus.
    This returns actual bookable hotel offers.

    city_code examples:
        - PAR (Paris)
        - BER (Berlin)
    """

    token = get_access_token()
    url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"

    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "cityCode": city_code,
        "checkInDate": check_in,
        "checkOutDate": check_out,
        "adults": adults,
        "roomQuantity": 1,
        "bestRateOnly": False
    }

    resp = requests.get(url, headers=headers, params=params)
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
