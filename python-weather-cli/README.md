# 🌤️ Weather CLI

A terminal weather app that fetches **real-time weather data** using the free [Open-Meteo API](https://open-meteo.com/) — **no API key required!**

## ✨ Features
- 🌡️ Current temperature, feels-like, humidity, wind speed & direction
- 📅 5-day weather forecast with highs & lows
- 🌍 Search any city worldwide via Nominatim geocoding
- 🌦️ WMO weather code to Emoji mapping
- 🆓 Completely free, no sign-up needed

## 🚀 How to Run

```bash
# Interactive mode
python3 weather.py

# With city as argument
python3 weather.py Mumbai
python3 weather.py New York
```

No external dependencies. Works with Python 3.10+.

## 📸 Preview

```
════════════════════════════════════════════════════════
  ⛅  WEATHER FOR: MUMBAI
  📍 Mumbai, Maharashtra, India
  🕐 Monday, 17 March 2026 06:24
════════════════════════════════════════════════════════
  Condition:   Partly cloudy
  Temperature: 29°C  (Feels like 34°C)
  Humidity:    74%
  Wind:        18 km/h SW
  Rainfall:    0.0 mm
════════════════════════════════════════════════════════
```

## 🏗️ Tech Stack
- **Language**: Python 3
- **APIs**: Open-Meteo (weather), Nominatim/OSM (geocoding)
- **Libraries**: `urllib`, `json` (standard library only)
