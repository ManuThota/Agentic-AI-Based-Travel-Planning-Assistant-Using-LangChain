import sys
import os

# Adjust path to make sure local packages can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.flight_tool import search_flights
from tools.hotel_tool import recommend_hotels
from tools.places_tool import discover_places
from tools.weather_tool import get_weather_forecast
from tools.budget_tool import estimate_trip_budget

def run_tests():
    print("====================================================")
    print("RUNNING TRAVEL ASSISTANT TOOL INTEGRATION TESTS")
    print("====================================================\n")
    
    # 1. Test Flights Tool (Database & Simulated Fallbacks)
    print("1a. Testing Flight Search Tool - Static Path (Delhi -> Goa)...")
    flights_static = search_flights.invoke({
        "source": "Delhi",
        "destination": "Goa",
        "preferred_class": "Economy",
        "sort_by": "price"
    })
    print(flights_static[:300] + "\n...\n")
    
    print("1b. Testing Flight Search Tool - Dynamic Sim Path (Delhi -> Kochi)...")
    flights_dynamic = search_flights.invoke({
        "source": "Delhi",
        "destination": "Kochi",
        "preferred_class": "Economy",
        "sort_by": "price"
    })
    print(flights_dynamic[:300] + "\n...\n")
    
    # 2. Test Hotels Tool (Database & Nominatim Fallbacks)
    print("2a. Testing Hotel Recommendation Tool - Static Path (Goa)...")
    hotels_static = recommend_hotels.invoke({
        "city": "Goa",
        "max_price": 6000.0,
        "min_rating": 4.0
    })
    print(hotels_static[:300] + "\n...\n")
    
    print("2b. Testing Hotel Recommendation Tool - Dynamic Nominatim (Kochi)...")
    hotels_dynamic = recommend_hotels.invoke({
        "city": "Kochi",
        "max_price": 6000.0,
        "min_rating": 4.0
    })
    print(hotels_dynamic[:300] + "\n...\n")
    
    # 3. Test Places Tool
    print("3a. Testing Places Discovery Tool - Static Path (Goa, Heritage)...")
    places_static = discover_places.invoke({
        "city": "Goa",
        "attraction_type": "Heritage"
    })
    print(places_static[:300] + "\n...\n")
    
    print("3b. Testing Places Discovery Tool - Dynamic Nominatim (Kochi, Nature)...")
    places_dynamic = discover_places.invoke({
        "city": "Kochi",
        "attraction_type": "Nature"
    })
    print(places_dynamic[:300] + "\n...\n")
    
    # 4. Test Weather Tool (Kochi)
    print("4. Testing Weather Forecast Tool (Kochi)...")
    weather_res = get_weather_forecast.invoke({
        "city": "Kochi"
    })
    print(weather_res + "\n")
    
    # 5. Test Budget Tool
    print("5. Testing Budget Calculator Tool...")
    budget_res = estimate_trip_budget.invoke({
        "flight_cost": 4800.0,
        "hotel_rate_per_night": 3200.0,
        "num_nights": 2,
        "food_and_local_transport_per_day": 1500.0,
        "activity_fees": 150.0
    })
    print(budget_res + "\n")
    
    print("====================================================")
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("====================================================")

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    run_tests()
