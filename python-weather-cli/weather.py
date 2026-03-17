"""
🌤️ Weather CLI App
Fetches real-time weather data using the Open-Meteo API (no API key needed)
and geocoding via Nominatim. Works out of the box!
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import ssl
import sys
from datetime import datetime

# Fix for macOS SSL certificate issues
ssl_context = ssl.create_default_context()
try:
    import certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

def get_coordinates(city: str) -> tuple[float, float, str]:
    """Get latitude, longitude, and display name for a city."""
    encoded = urllib.parse.quote(city)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1"
    req = urllib.request.Request(url, headers={"User-Agent": "WeatherCLI/1.0"})
    with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
        data = json.loads(response.read())
    if not data:
        raise ValueError(f"City '{city}' not found.")
    return float(data[0]["lat"]), float(data[0]["lon"]), data[0]["display_name"]

def get_weather(lat: float, lon: float) -> dict:
    """Fetch weather data from Open-Meteo API (free, no key needed)."""
    params = (
        f"latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        "precipitation,weather_code,wind_speed_10m,wind_direction_10m"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
        "&timezone=auto&forecast_days=5"
    )
    url = f"https://api.open-meteo.com/v1/forecast?{params}"
    with urllib.request.urlopen(url, timeout=10, context=ssl_context) as response:
        return json.loads(response.read())

def weather_code_to_emoji(code: int) -> tuple[str, str]:
    """Convert WMO weather code to emoji and description."""
    mapping = {
        0: ("☀️", "Clear sky"),
        1: ("🌤️", "Mainly clear"), 2: ("⛅", "Partly cloudy"), 3: ("☁️", "Overcast"),
        45: ("🌫️", "Foggy"), 48: ("🌫️", "Icy fog"),
        51: ("🌦️", "Light drizzle"), 53: ("🌦️", "Drizzle"), 55: ("🌧️", "Heavy drizzle"),
        61: ("🌧️", "Slight rain"), 63: ("🌧️", "Rain"), 65: ("🌧️", "Heavy rain"),
        71: ("🌨️", "Slight snow"), 73: ("❄️", "Snow"), 75: ("❄️", "Heavy snow"), 77: ("🌨️", "Snowfall"),
        80: ("🌦️", "Rain showers"), 81: ("🌧️", "Heavy showers"), 82: ("⛈️", "Violent showers"),
        95: ("⛈️", "Thunderstorm"), 96: ("⛈️", "Thunderstorm with hail"), 99: ("🌩️", "Thunderstorm"),
    }
    return mapping.get(code, ("🌡️", f"Code {code}"))

def wind_direction_label(deg: float) -> str:
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[int((deg + 22.5) / 45) % 8]

def display_weather(city: str, data: dict, display_name: str):
    curr = data["current"]
    daily = data["daily"]

    emoji, desc = weather_code_to_emoji(curr["weather_code"])
    temp = curr["temperature_2m"]
    feels = curr["apparent_temperature"]
    humidity = curr["relative_humidity_2m"]
    wind = curr["wind_speed_10m"]
    wind_dir = wind_direction_label(curr["wind_direction_10m"])
    precip = curr["precipitation"]

    print("\n" + "═" * 56)
    print(f"  {emoji}  WEATHER FOR: {city.upper()}")
    print(f"  📍 {display_name[:52]}")
    print(f"  🕐 {datetime.now().strftime('%A, %d %B %Y %H:%M')}")
    print("═" * 56)
    print(f"  Condition:   {desc}")
    print(f"  Temperature: {temp}°C  (Feels like {feels}°C)")
    print(f"  Humidity:    {humidity}%")
    print(f"  Wind:        {wind} km/h {wind_dir}")
    print(f"  Rainfall:    {precip} mm")
    print("═" * 56)

    print("\n  📅  5-DAY FORECAST")
    print(f"  {'Date':<14} {'Condition':<18} {'High':>6} {'Low':>6} {'Rain':>7}")
    print("  " + "-" * 52)

    for i in range(5):
        date_str = daily["time"][i]
        date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%a %d %b")
        code = daily["weather_code"][i]
        fc_emoji, fc_desc = weather_code_to_emoji(code)
        hi = daily["temperature_2m_max"][i]
        lo = daily["temperature_2m_min"][i]
        rain = daily["precipitation_sum"][i]
        print(f"  {date:<14} {fc_emoji} {fc_desc:<15} {hi:>5}°C {lo:>5}°C {rain:>5}mm")

    print()

def main():
    print("🌤️  Weather CLI — Powered by Open-Meteo (No API Key Needed!)")
    print("-" * 56)

    if len(sys.argv) > 1:
        city = " ".join(sys.argv[1:])
    else:
        city = input("  Enter city name: ").strip()

    if not city:
        print("❌ Please provide a city name.")
        sys.exit(1)

    print(f"\n  🔍 Fetching weather for '{city}'...")

    try:
        lat, lon, display_name = get_coordinates(city)
        data = get_weather(lat, lon)
        display_weather(city, data, display_name)
    except ValueError as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
