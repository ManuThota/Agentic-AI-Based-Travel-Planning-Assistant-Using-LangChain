import os
import json
import datetime
import math
from typing import List, Dict, Any, Optional
import requests
from langchain_core.tools import tool

# Local city code mapping for popular destinations
CITY_IATA_CODES = {
    "delhi": "DEL",
    "mumbai": "BOM",
    "bangalore": "BLR",
    "goa": "GOI",
    "srinagar": "SXR",
    "jaipur": "JAI"
}

CARRIER_AIRLINES = {
    "6E": "IndiGo",
    "AI": "Air India",
    "UK": "Vistara",
    "QP": "Akasa Air",
    "SG": "SpiceJet"
}

def stable_hash(s: str) -> int:
    """A simple deterministic polynomial rolling hash to keep values stable across Python executions."""
    h = 0
    for char in s:
        h = (h * 31 + ord(char)) & 0xFFFFFFFF
    return h

def parse_duration_pt(duration_str: str) -> str:
    """Helper to convert ISO 8601 duration 'PT2H40M' to human-readable '2h 40m'."""
    try:
        clean = duration_str.replace("PT", "")
        hours = ""
        minutes = ""
        if "H" in clean:
            parts = clean.split("H")
            hours = parts[0] + "h"
            clean = parts[1]
        if "M" in clean:
            minutes = clean.replace("M", "") + "m"
        return f"{hours} {minutes}".strip()
    except Exception:
        return duration_str

def parse_duration_to_minutes(duration_str: str) -> int:
    """Helper to convert duration '2h 40m' or 'PT2H40M' to minutes for sorting."""
    try:
        minutes = 0
        # Handle ISO format
        clean = duration_str.replace("PT", "")
        if "H" in clean:
            parts = clean.split("H")
            minutes += int(parts[0]) * 60
            clean = parts[1]
        if "M" in clean:
            minutes += int(clean.replace("M", ""))
            return minutes
            
        # Handle human-readable format like "2h 40m"
        norm_str = duration_str.lower()
        if "h" in norm_str:
            parts = norm_str.split("h")
            minutes += int(parts[0].strip()) * 60
            norm_str = parts[1]
        if "m" in norm_str:
            minutes += int(norm_str.replace("m", "").strip())
        return minutes if minutes > 0 else 9999
    except Exception:
        return 9999

def geocode_city_coordinates(city: str) -> Optional[tuple]:
    """Helper to geocode city name using local database coordinates or Open-Meteo/Nominatim APIs."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Try Nominatim with India restriction first (biases towards domestic cities)
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city}&countrycodes=in&format=json&limit=1"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200 and resp.json():
            data = resp.json()[0]
            return float(data.get("lat")), float(data.get("lon"))
    except Exception:
        pass
        
    # Try geocoding city using local coordinates from weather tool helper first if possible
    try:
        from tools.weather_tool import geocode_city
        coords = geocode_city(city)
        if coords:
            return coords["lat"], coords["lon"]
    except Exception:
        pass
        
    # Fallback to keyless Nominatim Search API (global)
    try:
        url_global = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
        resp_global = requests.get(url_global, headers=headers, timeout=10)
        if resp_global.status_code == 200 and resp_global.json():
            data = resp_global.json()[0]
            return float(data.get("lat")), float(data.get("lon"))
    except Exception:
        pass
        
    return None

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the physical distance in kilometers between two coordinates using the Haversine formula."""
    R = 6371.0  # Radius of Earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def generate_simulated_flights(source: str, destination: str, distance_km: float, preferred_class: str) -> List[Dict[str, Any]]:
    """Generates 5 realistic simulated flights based on physical distance between cities."""
    airlines_pool = [
        {"carrier": "6E", "name": "IndiGo"},
        {"carrier": "AI", "name": "Air India"},
        {"carrier": "UK", "name": "Vistara"},
        {"carrier": "QP", "name": "Akasa Air"},
        {"carrier": "SG", "name": "SpiceJet"}
    ]
    
    # Calculate flight duration (cruising speed 750 km/h + 30 mins take-off/landing)
    duration_mins = int(30 + (distance_km / 750) * 60)
    duration_mins = max(45, duration_mins)
    
    hours = duration_mins // 60
    mins = duration_mins % 60
    duration_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
    
    time_slots = [
        ("06:15", "08:55"),  # Morning
        ("11:30", "14:10"),  # Midday
        ("15:45", "18:25"),  # Afternoon
        ("18:20", "21:00"),  # Evening
        ("21:45", "00:25")   # Night
    ]
    
    # Price estimation: minimum 2200 INR + 3.8 INR per km
    base_price = int(2200 + distance_km * 3.8)
    
    flights = []
    h_base = stable_hash(f"{source.lower()}-{destination.lower()}-{preferred_class.lower()}")
    
    for i in range(5):
        airline = airlines_pool[(h_base + i) % len(airlines_pool)]
        time_idx = (h_base + i) % len(time_slots)
        dep_time, _ = time_slots[time_idx]
        
        # Calculate arrival time
        dep_h, dep_m = map(int, dep_time.split(":"))
        arr_total_mins = (dep_h * 60 + dep_m + duration_mins) % (24 * 60)
        arr_h = arr_total_mins // 60
        arr_m = arr_total_mins % 60
        arr_time = f"{arr_h:02d}:{arr_m:02d}"
        
        # Add slight variance to prices
        price_factor = 0.9 + (i * 0.15)
        # Class multiplier
        class_multiplier = 2.5 if preferred_class.lower() == "business" else 1.0
        final_price = int(base_price * price_factor * class_multiplier)
        
        flight_num = f"{airline['carrier']}-{100 + (h_base + i) % 900}"
        
        flights.append({
            "flight_number": flight_num,
            "airline": airline["name"],
            "source": source.title(),
            "destination": destination.title(),
            "departure_time": dep_time,
            "arrival_time": arr_time,
            "price": final_price,
            "duration": duration_str,
            "class": preferred_class.title()
        })
        
    return flights

@tool
def search_flights(
    source: str, 
    destination: str, 
    departure_date: Optional[str] = None, 
    preferred_class: Optional[str] = "Economy", 
    sort_by: Optional[str] = "price"
) -> str:
    """
    Search for flights between source and destination cities.
    Can query real-time flights via Amadeus API if credentials are set, otherwise falls back to dynamic simulation.
    
    Args:
        source (str): Starting city (e.g., 'Delhi', 'Mumbai', 'Bangalore')
        destination (str): Travel destination city (e.g., 'Goa', 'Srinagar', 'Jaipur')
        departure_date (str, optional): Departure date in YYYY-MM-DD format. Defaults to tomorrow if not provided.
        preferred_class (str, optional): Flight class preferred, either 'Economy' or 'Business'. Defaults to 'Economy'.
        sort_by (str, optional): Sorting criteria, either 'price' (cheapest) or 'duration' (fastest). Defaults to 'price'.
        
    Returns:
        str: JSON string of matching flights, or an error/fallback warning message.
    """
    # 1. Check for Amadeus Credentials
    client_id = os.getenv("AMADEUS_CLIENT_ID")
    client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
    
    # Resolve departure date
    if not departure_date:
        departure_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
    # Check if we should use local fallback
    if not client_id or not client_secret:
        print("Amadeus API credentials not set. Falling back to dynamic flight simulation.")
        return search_flights_local(source, destination, preferred_class, sort_by)
        
    try:
        from amadeus import Client
        amadeus = Client(client_id=client_id, client_secret=client_secret)
        
        # Resolve source and destination IATA Codes
        source_iata = CITY_IATA_CODES.get(source.strip().lower())
        dest_iata = CITY_IATA_CODES.get(destination.strip().lower())
        
        # If not in local mapping, lookup dynamically via Amadeus Location Search API
        if not source_iata:
            loc_res = amadeus.reference_data.locations.get(keyword=source, subType='CITY,AIRPORT')
            if loc_res.data:
                source_iata = loc_res.data[0].get('iataCode')
        if not dest_iata:
            loc_res = amadeus.reference_data.locations.get(keyword=destination, subType='CITY,AIRPORT')
            if loc_res.data:
                dest_iata = loc_res.data[0].get('iataCode')
                
        if not source_iata or not dest_iata:
            print(f"Could not resolve IATA code for origin '{source}' or destination '{destination}'. Using simulated fallback.")
            return search_flights_local(source, destination, preferred_class, sort_by)
            
        # Map travel class
        travel_class = "ECONOMY" if preferred_class.lower() == "economy" else "BUSINESS"
        
        # Query flight offers
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=source_iata,
            destinationLocationCode=dest_iata,
            departureDate=departure_date,
            adults=1,
            travelClass=travel_class,
            max=10
        )
        
        if not response.data:
            print("No flight offers returned from Amadeus. Using simulated fallback.")
            return search_flights_local(source, destination, preferred_class, sort_by)
            
        # Parse flight offers to match our database schema
        formatted_flights = []
        for offer in response.data:
            price_data = offer.get("price", {})
            total_price = float(price_data.get("total", 0.0))
            currency = price_data.get("currency", "EUR")
            
            # Simple conversion helper to match INR output
            if currency == "EUR":
                total_price_inr = int(total_price * 90)
            elif currency == "USD":
                total_price_inr = int(total_price * 83)
            else:
                total_price_inr = int(total_price)
                
            itinerary = offer.get("itineraries", [{}])[0]
            segments = itinerary.get("segments", [])
            if not segments:
                continue
                
            first_seg = segments[0]
            last_seg = segments[-1]
            carrier = first_seg.get("carrierCode", "")
            airline_name = CARRIER_AIRLINES.get(carrier, f"Airline {carrier}")
            flight_num = f"{carrier}-{first_seg.get('number', '')}"
            
            dep_time = first_seg.get("departure", {}).get("at", "").split("T")[-1][:5]
            arr_time = last_seg.get("arrival", {}).get("at", "").split("T")[-1][:5]
            duration = parse_duration_pt(itinerary.get("duration", ""))
            
            formatted_flights.append({
                "flight_number": flight_num,
                "airline": airline_name,
                "source": source.title(),
                "destination": destination.title(),
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "price": total_price_inr,
                "duration": duration,
                "class": preferred_class.title()
            })
            
        # Sort results
        if sort_by == "duration":
            formatted_flights.sort(key=lambda x: parse_duration_to_minutes(x.get("duration", "")))
        else:
            formatted_flights.sort(key=lambda x: x.get("price", 999999))
            
        return json.dumps(formatted_flights, indent=2)
        
    except Exception as e:
        print(f"Amadeus API Error: {e}. Falling back to dynamic simulation.")
        return search_flights_local(source, destination, preferred_class, sort_by)

def search_flights_local(source: str, destination: str, preferred_class: str, sort_by: str) -> str:
    """Helper local flight search fallback. Calculates physical distance and simulates flights dynamically in real-time."""
    # Dynamic Distance-based Flight Simulation (Global Keyless operation)
    print(f"Simulating flight path '{source} -> {destination}' based on physical distance.")
    
    source_coords = geocode_city_coordinates(source)
    dest_coords = geocode_city_coordinates(destination)
    
    if source_coords and dest_coords:
        distance_km = calculate_haversine_distance(
            source_coords[0], source_coords[1],
            dest_coords[0], dest_coords[1]
        )
        print(f"Physical Distance: {distance_km:.2f} km")
    else:
        # Default fallback distance
        distance_km = 1200.0
        print("Geocoding failed for flight path. Using default distance of 1200 km.")
        
    simulated_flights = generate_simulated_flights(source, destination, distance_km, preferred_class)
    
    if sort_by == "duration":
        simulated_flights.sort(key=lambda x: parse_duration_to_minutes(x.get("duration", "")))
    else:
        simulated_flights.sort(key=lambda x: x.get("price", 999999))
        
    return json.dumps(simulated_flights, indent=2)
