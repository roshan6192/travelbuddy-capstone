import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
if not WEATHER_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found in .env")


def get_weather(city_name: str):
    """
    Get current weather and alerts for the city.
    Uses OpenWeather.
    """

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": WEATHER_KEY,
        "units": "metric"
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        result = {
            "city": city_name,
            "temp_c": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "weather": data["weather"][0]["main"],
            "description": data["weather"][0]["description"]
        }

        return result

    except Exception as e:
        return {"city": city_name, "error": str(e)}
