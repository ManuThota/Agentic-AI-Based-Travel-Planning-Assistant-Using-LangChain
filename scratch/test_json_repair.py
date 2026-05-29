import json
import re
import ast
from typing import Optional, Dict, Any

def robust_json_loads(json_str: str) -> Optional[Dict[str, Any]]:
    # Step 1: Remove single-line and multi-line comments
    # Remove // comments
    json_str_clean = re.sub(r'(?<!:)\/\/.*$', '', json_str, flags=re.MULTILINE)
    # Remove /* ... */ comments
    json_str_clean = re.sub(r'\/\*.*?\*\/', '', json_str_clean, flags=re.DOTALL)
    
    # Step 2: Clean trailing commas before closing braces and brackets
    json_str_clean = re.sub(r',\s*\}', '}', json_str_clean)
    json_str_clean = re.sub(r',\s*\]', ']', json_str_clean)
    
    # Step 3: Try standard json.loads with strict=False
    try:
        return json.loads(json_str_clean, strict=False)
    except Exception as e1:
        print(f"Standard json.loads failed: {e1}")
        
    # Step 4: Try ast.literal_eval fallback for single quotes/trailing commas
    try:
        # Convert JSON keywords to Python counterparts
        py_str = json_str_clean
        py_str = re.sub(r'\btrue\b', 'True', py_str)
        py_str = re.sub(r'\bfalse\b', 'False', py_str)
        py_str = re.sub(r'\bnull\b', 'None', py_str)
        
        parsed = ast.literal_eval(py_str)
        if isinstance(parsed, dict):
            return parsed
    except Exception as e2:
        print(f"ast.literal_eval fallback failed: {e2}")
        
    return None

def test_repair():
    # 1. Trailing comma test
    t1 = '{"name": "Goa", "amenities": ["Pool", "WiFi",],}'
    # 2. Raw newline test
    t2 = '{"name": "Goa", "desc": "Beautiful \n beach"}'
    # 3. Single quote test
    t3 = "{'name': 'Goa', 'price': 5000}"
    # 4. Comment test
    t4 = '{\n  "name": "Goa", // target city\n  "price": 3000\n}'
    
    print("t1 result:", robust_json_loads(t1))
    print("t2 result:", robust_json_loads(t2))
    print("t3 result:", robust_json_loads(t3))
    print("t4 result:", robust_json_loads(t4))

if __name__ == "__main__":
    test_repair()
