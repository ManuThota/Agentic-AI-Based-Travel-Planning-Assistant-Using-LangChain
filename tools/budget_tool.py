import json
from typing import Optional
from langchain_core.tools import tool

@tool
def estimate_trip_budget(
    flight_cost: float,
    hotel_rate_per_night: float,
    num_nights: int,
    food_and_local_transport_per_day: Optional[float] = 1500.0,
    activity_fees: Optional[float] = 0.0
) -> str:
    """
    Calculate the total estimated trip budget and return a breakdown of the costs.
    
    Args:
        flight_cost (float): Price of the selected flight ticket in INR (round trip or one way).
        hotel_rate_per_night (float): Price of the hotel room per night in INR.
        num_nights (int): Number of nights spent at the hotel (usually duration of stay minus 1, or matching dates).
        food_and_local_transport_per_day (float, optional): Estimated daily expenses for meals and local travel (cabs, rickshaws) in INR. Defaults to 1500.0.
        activity_fees (float, optional): Cumulative entry ticket costs or sports activity prices in INR. Defaults to 0.0.
        
    Returns:
        str: JSON string of budget breakdown and total cost.
    """
    accommodation_cost = hotel_rate_per_night * num_nights
    food_transport_cost = food_and_local_transport_per_day * (num_nights + 1)  # food is for total days, which is nights + 1
    total_cost = flight_cost + accommodation_cost + food_transport_cost + activity_fees
    
    breakdown = {
        "flight_cost": flight_cost,
        "hotel_rate_per_night": hotel_rate_per_night,
        "num_nights": num_nights,
        "accommodation_total": accommodation_cost,
        "food_and_local_transport_total": food_transport_cost,
        "sightseeing_and_activities": activity_fees,
        "total_estimated_budget": total_cost
    }
    
    return json.dumps(breakdown, indent=2)
