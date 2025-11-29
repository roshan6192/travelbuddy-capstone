import requests

def get_country_info(country_code: str):
    """
    Uses REST Countries API to retrieve reliable data about a country.
    https://restcountries.com/v3.1/alpha/{code}
    """

    url = f"https://restcountries.com/v3.1/alpha/{country_code}"

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        country = data[0]

        return {
            "name": country.get("name", {}).get("common"),
            "region": country.get("region"),
            "subregion": country.get("subregion"),
            "population": country.get("population"),
            "capital": country.get("capital", ["Unknown"])[0],
            "languages": list(country.get("languages", {}).values()),
            "borders": country.get("borders", []),
        }

    except Exception as e:
        return {"error": str(e), "country_code": country_code}
