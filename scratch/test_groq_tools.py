import os
import sys
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from tools.flight_tool import search_flights
from tools.hotel_tool import recommend_hotels
from tools.places_tool import discover_places
from tools.weather_tool import get_weather_forecast
from tools.budget_tool import estimate_trip_budget
from agent.travel_agent import SYSTEM_PROMPT

def test_groq_tools():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY is not set.")
        return

    model_name = "llama-3.3-70b-versatile"
    print(f"Testing direct tool binding with ChatGroq({model_name})...")
    
    llm = ChatGroq(
        model=model_name,
        temperature=0.2,
        groq_api_key=api_key
    )
    
    tools = [
        search_flights,
        recommend_hotels,
        discover_places,
        get_weather_forecast,
        estimate_trip_budget
    ]
    
    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(tools)
    
    query = (
        "I want to plan a trip from 'Delhi' to 'Goa' starting from 2026-05-29 to 2026-06-01. "
        "This is a 4 days, 3 nights trip. My maximum budget limit is INR 30000. "
        "My flight class preference is Economy. I prefer activities and places matching these styles: Beach, Heritage. "
        "Specific preferences: Suggest the cheapest flight and a highly rated hotel. Plan a balanced, relaxed vacation."
    )
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]
    
    try:
        response = llm_with_tools.invoke(messages)
        print("Success!")
        print("Response type:", type(response))
        print("Content:", response.content)
        print("Tool calls:", response.tool_calls)
    except Exception as e:
        print("Failed with error:")
        print(e)

if __name__ == "__main__":
    test_groq_tools()
