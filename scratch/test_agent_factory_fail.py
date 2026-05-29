import os
import sys
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from agent.travel_agent import compile_agent_graph

def test_agent_graph():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY is not set.")
        return

    model_name = "llama-3.3-70b-versatile"
    print(f"Compiling agent graph with ChatGroq({model_name})...")
    graph = compile_agent_graph(model_name)
    
    query = (
        "I want to plan a trip from 'Delhi' to 'Goa' starting from 2026-05-29 to 2026-06-01. "
        "This is a 4 days, 3 nights trip. My maximum budget limit is INR 30000. "
        "My flight class preference is Economy. I prefer activities and places matching these styles: Beach, Heritage. "
        "Specific preferences: Suggest the cheapest flight and a highly rated hotel. Plan a balanced, relaxed vacation."
    )
    
    try:
        result = graph.invoke({"messages": [{"role": "user", "content": query}]})
        print("Success!")
        print("Result:", result)
    except Exception as e:
        print("Failed with error:")
        print(e)

if __name__ == "__main__":
    test_agent_graph()
