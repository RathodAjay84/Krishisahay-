# weather.py
"""Weather integration helpers using OpenWeatherMap API."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()


def fetch_weather(city: str = "Lal Bahadur Nagar,Telangana,IN") -> dict | None:
    """Return current weather data or None if unavailable."""
    weather_api_key = os.getenv("WEATHER_API")
    if not weather_api_key:
        return None
    url = (
        "http://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={weather_api_key}&units=metric"
    )
    try:
        resp = requests.get(url, timeout=8).json()
        if resp.get("cod") != 200:
            return None
        data = {
            "temp": resp["main"]["temp"],
            "feels": resp["main"]["feels_like"],
            "humidity": resp["main"]["humidity"],
            "desc": resp["weather"][0]["description"].title(),
            "icon": f"https://openweathermap.org/img/wn/{resp['weather'][0]['icon']}@2x.png",
        }
        return data
    except Exception:
        return None


def advice_from_weather(weather: dict) -> str:
    """Return a brief farming tip based on weather conditions."""
    if not weather:
        return "No weather information available."
    temp = weather.get("temp", 0)
    desc = weather.get("desc", "").lower()
    if "rain" in desc or temp < 20:
        return "Consider delaying irrigation since it's cold/rainy." \
               "Protect young seedlings from excess moisture."
    elif temp > 35:
        return "High temperatures—mulch soil and irrigate in early morning." \
               "Avoid working in the field during peak heat."
    else:
        return "Weather looks normal. Continue regular farming activities."
