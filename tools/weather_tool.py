import requests
from typing import Dict, Any, Optional
from langchain_core.tools import tool

# Local coordinate database for reliability & speed
CITY_COORDINATES = {
    "goa": {"lat": 15.2993, "lon": 74.1240},
    "delhi": {"lat": 28.7041, "lon": 77.1025},
    "mumbai": {"lat": 19.0760, "lon": 72.8777},
    "bangalore": {"lat": 12.9716, "lon": 77.5946},
    "srinagar": {"lat": 34.0837, "lon": 74.7973},
    "jaipur": {"lat": 26.9124, "lon": 75.7873}
}

# WMO Weather Codes mapping to human-readable strings
WMO_WEATHER_CODES = {
    0: "Clear Sky / Sunny",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Slight Snowfall",
    73: "Moderate Snowfall",
    75: "Heavy Snowfall",
    77: "Snow Grains",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    85: "Slight Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail"
}

def geocode_city(city: str) -> Optional[Dict[str, float]]:
    """Helper to geocode city name using Open-Meteo geocoding API or local fallback."""
    city_clean = city.strip().lower()
    
    # Try local database first
    if city_clean in CITY_COORDINATES:
        return CITY_COORDINATES[city_clean]
        
    # Call free geocoding API
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results")
            if results and len(results) > 0:
                return {
                    "lat": results[0]["latitude"],
                    "lon": results[0]["longitude"]
                }
    except Exception:
        pass
        
    return None

@tool
def get_weather_forecast(city: str) -> str:
    """
    Get 7-day weather forecast (max/min temp and description) for any city using Open-Meteo.
    
    Args:
        city (str): Name of the city to get weather for (e.g. 'Goa', 'Srinagar', 'Jaipur', 'Delhi')
        
    Returns:
        str: A clean, human-readable summary of the weather forecast, or error message.
    """
    coords = geocode_city(city)
    if not coords:
        return f"Error: Could not find coordinates for city: {city}."
        
    lat = coords["lat"]
    lon = coords["lon"]
    
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weather_code&timezone=auto"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return f"Error connecting to weather service: Status code {response.status_code}."
            
        data = response.json()
        daily = data.get("daily", {})
        
        if not daily or "time" not in daily:
            return f"Error: Weather data not available for {city}."
            
        forecast_lines = [f"7-Day Weather Forecast for {city.title()}:"]
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        codes = daily.get("weather_code", [])
        
        for i in range(len(dates)):
            date = dates[i]
            tmax = max_temps[i] if i < len(max_temps) else "N/A"
            tmin = min_temps[i] if i < len(min_temps) else "N/A"
            code = codes[i] if i < len(codes) else 0
            desc = WMO_WEATHER_CODES.get(code, "Unknown Weather")
            forecast_lines.append(f"- {date}: {desc} (Temp: {tmin}°C to {tmax}°C)")
            
        return "\n".join(forecast_lines)
        
    except Exception as e:
        return f"Exception in weather lookup: {str(e)}"
