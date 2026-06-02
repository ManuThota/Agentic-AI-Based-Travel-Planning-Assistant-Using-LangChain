import os
import json
import re
from typing import Dict, Any, Tuple, Optional
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_groq import ChatGroq

# Load local environment variables (.env)
load_dotenv()

SYSTEM_PROMPT = """You are an expert, highly detail-oriented AI Travel Planner. Your goal is to construct a comprehensive, realistic, and optimized travel itinerary for the user based on their travel query.

CRITICAL RULES:
1. SINGLE TOOL CALL PER TURN: You must only call ONE tool per response turn. Do not call multiple tools in parallel or sequence in the same message. If you need information from multiple tools, call them one by one across multiple turns.
2. NO MIXED OUTPUT: When calling a tool, your response must contain ONLY the tool call, with absolutely no other text, JSON, or markdown itinerary.
3. SEQUENTIAL ORDER:
   - First, query flights, hotels, attractions, and weather (one per turn).
   - Once you have the results for all of them, call `estimate_trip_budget` with the actual prices discovered.
   - Finally, after budget estimation, output the final itinerary.
4. BUDGET OVERRUN RULE: If the user's budget is mathematically too low to support the duration of the trip, select the cheapest options available from the tool outputs. Do not try to call tools recursively in a loop to find cheaper options. Proceed directly to compile the final itinerary and explain the budget overrun in the reasoning section.
5. TRAVEL STYLE PREFERENCES: Always pass the user's travel style preferences (e.g. 'Nature', 'Heritage', 'Beach', 'Shopping', 'Adventure') as the 'attraction_type' parameter in `discover_places` to recommend matching places.
6. COMPLETE ITINERARY: The "day_wise_itinerary" array in your output JSON must contain exactly one entry for every single day of the trip (e.g., from Day 1 to Day N, where N is the total duration of the trip). Never truncate, skip, or summarize days. Keep all activity descriptions short and concise (e.g., 1 sentence per activity) to stay compact.
7. FINAL RESPONSE FORMAT: Once all tools have run and you are ready to output the final itinerary, output it in TWO distinct parts in a single response (without any tool calls in this turn):
   - Part 1: A structured JSON code block containing the exact travel details.
   - Part 2: A beautiful, human-readable markdown itinerary with justification for choices.

Part 1 JSON Format:
```json
{
  "trip_summary": {
    "destination": "Goa",
    "source": "Delhi",
    "duration": "3 Days, 2 Nights",
    "dates": "Feb 12 - Feb 14"
  },
  "flight_selected": {
    "flight_number": "6E-501",
    "airline": "IndiGo",
    "price": 4800,
    "departure_time": "06:15",
    "arrival_time": "08:55",
    "duration": "2h 40m",
    "class": "Economy"
  },
  "hotel_selected": {
    "hotel_name": "Sea View Resort",
    "price_per_night": 3200,
    "rating": 4.2,
    "amenities": ["Pool", "Free WiFi", "Beach Access"],
    "total_hotel_cost": 6400
  },
  "day_wise_itinerary": [
    {
      "day": 1,
      "weather": "Clear Sky / Sunny (Temp: 22°C to 31°C)",
      "activities": [
        {
          "time": "Morning",
          "place": "Calangute Beach",
          "description": "Relax and enjoy water sports on the sandy shores."
        },
        {
          "time": "Afternoon",
          "place": "Fort Aguada",
          "description": "Explore the historic 17th-century Portuguese lighthouse."
        }
      ]
    }
  ],
  "budget_breakdown": {
    "flight": 4800,
    "accommodation": 6400,
    "food_and_local_transport": 3000,
    "activities_and_sightseeing": 500,
    "total_cost": 14700
  },
  "reasoning": "Indigo flight 6E-501 was selected as it is the cheapest morning flight. Sea View Resort offers beach access within the budget limit."
}
```

Part 2 Markdown format follows the JSON block immediately. Use a premium, professional structure with no emojis.
"""

def compile_agent_graph(model_name: str):
    """Compiles the LangChain ReAct agent graph for a specific Groq model."""
    from tools.flight_tool import search_flights
    from tools.hotel_tool import recommend_hotels
    from tools.places_tool import discover_places
    from tools.weather_tool import get_weather_forecast
    from tools.budget_tool import estimate_trip_budget
    
    tools = [
        search_flights,
        recommend_hotels,
        discover_places,
        get_weather_forecast,
        estimate_trip_budget
    ]
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment or .env file.")
        
    llm = ChatGroq(
        model=model_name,
        temperature=0.2,
        groq_api_key=api_key
    )
    
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )

class AgentGraphWrapper:
    """Wrapper around CompiledStateGraph to match standard AgentExecutor invoke signature and support automatic TPD fallback."""
    def __init__(self, default_model: str = "llama-3.3-70b-versatile", fallback_model: str = "llama-3.1-8b-instant"):
        self.default_model = default_model
        self.fallback_model = fallback_model
        self.graph = None

    def invoke(self, inputs: dict) -> dict:
        user_input = inputs.get("input", "")
        
        # Lazy compile graph
        if self.graph is None:
            try:
                self.graph = compile_agent_graph(self.default_model)
            except Exception as e:
                print(f"Error compiling default graph: {e}. Trying fallback model.")
                self.graph = compile_agent_graph(self.fallback_model)
                
        try:
            # Attempt invocation
            result = self.graph.invoke({"messages": [{"role": "user", "content": user_input}]})
        except Exception as e:
            err_msg = str(e).lower()
            # If 429 rate limit is reached or 400 tool-use failure occurs, seamlessly fall back to Llama 8B
            if any(term in err_msg for term in ["429", "rate_limit", "quota", "exhausted", "400", "tool_use_failed", "failed to call a function"]):
                print(f"Rate limit or tool use failure ({err_msg}) reached for {self.default_model}. Seamlessly falling back to {self.fallback_model}.")
                try:
                    fallback_graph = compile_agent_graph(self.fallback_model)
                    result = fallback_graph.invoke({"messages": [{"role": "user", "content": user_input}]})
                    self.graph = fallback_graph  # Cache fallback graph for current run/session context
                except Exception as fallback_err:
                    print(f"Fallback model also failed: {fallback_err}")
                    raise fallback_err
            else:
                raise e
                
        messages = result.get("messages", [])
        if messages:
            last_msg = messages[-1]
            content = ""
            if hasattr(last_msg, "content"):
                content = last_msg.content
            elif isinstance(last_msg, dict):
                content = last_msg.get("content", "")
                
            # Parse list of text parts if returned by the model
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, str):
                        text_parts.append(part)
                    elif isinstance(part, dict):
                        if "text" in part:
                            text_parts.append(part["text"])
                        elif "content" in part:
                            text_parts.append(part["content"])
                content = "".join(text_parts)
                
            return {"output": content}
        return {"output": "No response generated."}

def get_travel_agent_executor(model_name: str = "llama-3.3-70b-versatile") -> AgentGraphWrapper:
    """Configures and returns the wrapped CompiledStateGraph for travel planning."""
    # Note: model_name parameter is preserved for backwards compatibility, but fallback is handled dynamically
    fallback_model = "llama-3.1-8b-instant" if model_name != "llama-3.1-8b-instant" else "llama-3.3-70b-versatile"
    return AgentGraphWrapper(default_model=model_name, fallback_model=fallback_model)

def robust_json_loads(json_str: str) -> Optional[Dict[str, Any]]:
    """Robust parser that cleans and repairs common JSON errors before loading."""
    # 1. Remove comments
    json_str_clean = re.sub(r'(?<!:)\/\/.*$', '', json_str, flags=re.MULTILINE)
    json_str_clean = re.sub(r'\/\*.*?\*\/', '', json_str_clean, flags=re.DOTALL)
    
    # 2. Clean trailing commas in structures
    json_str_clean = re.sub(r',\s*\}', '}', json_str_clean)
    json_str_clean = re.sub(r',\s*\]', ']', json_str_clean)
    
    # 3. Try standard json.loads with strict=False (allows unescaped control chars like raw newlines)
    try:
        return json.loads(json_str_clean, strict=False)
    except Exception:
        pass
        
    # 4. Try ast.literal_eval fallback for single-quoted keys/values or python literals
    try:
        import ast
        py_str = json_str_clean
        py_str = re.sub(r'\btrue\b', 'True', py_str)
        py_str = re.sub(r'\bfalse\b', 'False', py_str)
        py_str = re.sub(r'\bnull\b', 'None', py_str)
        
        parsed = ast.literal_eval(py_str)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
        
    return None

def parse_agent_response(response_text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Parses the agent's text response to separate the JSON block from the Markdown body.
    
    Returns:
        Tuple[Optional[Dict[str, Any]], str]: (parsed_json_dict, markdown_content)
    """
    parsed_json = None
    markdown_content = response_text
    
    # 1. Try to find the JSON block inside markdown backticks
    json_pattern = r"```json\s*(.*?)\s*```"
    match = re.search(json_pattern, response_text, re.DOTALL)
    
    if match:
        json_str = match.group(1).strip()
        parsed_json = robust_json_loads(json_str)
        if parsed_json is not None:
            markdown_content = re.sub(json_pattern, "", response_text, flags=re.DOTALL).strip()
            return parsed_json, markdown_content
            
    # 2. Try generic code block backticks without "json" label
    generic_pattern = r"```\s*(\{.*?\})\s*```"
    match_generic = re.search(generic_pattern, response_text, re.DOTALL)
    if match_generic:
        json_str = match_generic.group(1).strip()
        parsed_json = robust_json_loads(json_str)
        if parsed_json is not None:
            markdown_content = re.sub(generic_pattern, "", response_text, flags=re.DOTALL).strip()
            return parsed_json, markdown_content
            
    # 3. Dynamic search: Find the first '{' and the last '}' to extract raw JSON
    try:
        first_brace = response_text.find('{')
        last_brace = response_text.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            json_str = response_text[first_brace:last_brace+1].strip()
            parsed_json = robust_json_loads(json_str)
            if parsed_json is not None:
                markdown_content = (response_text[:first_brace] + response_text[last_brace+1:]).strip()
                return parsed_json, markdown_content
    except Exception as e:
        print(f"Failed to extract raw JSON braces: {e}")
        
    return parsed_json, markdown_content
