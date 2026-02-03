import os
import requests
import json

# Configuration
SITE_NAME = "Carbon Sleuth"
OPENROUTER_API_KEY = os.getenv("VITE_OPENROUTER_API_KEY") or "sk-or-v1-..." # Fallback or load from .env if possible
AI_MODEL = os.getenv("VITE_AI_MODEL") or "google/gemma-2-9b-it:free"

def generate_ai_response(user_query: str, context_data: dict) -> dict:
    """
    Generates an AI response based on the user query and dashboard context.
    Mirroring the logic from web-frontend/src/services/aiService.js.
    
    This function:
    1. Constructs a system prompt with the current data context.
    2. Sends a request to the LLM provider (OpenRouter).
    3. Parses the response for 'Action Tags' (e.g., |ACTION:SEARCH:X|).
    
    :param user_query: The question or command from the user.
    :param context_data: JSON object containing current dashboard statistics/data.
    :return: Dict containing 'response' (text) and 'action' (parsed command).
    """
    if not user_query:
        return None

    # Construct System Prompt
    system_prompt = f"""
    You are Carbon Sleuth AI, an expert industrial analyst.
    Current Site: {SITE_NAME}
    
    EXPLICIT INSTRUCTION FOR "SHOW ME" / FILTERING REQUESTS:
    If the user asks to "Show me", "List", "Filter", or "Find" items (e.g., "Show me warning items", "List high pressure pumps"):
    1. FIRST, generate a Markdown Table containing the relevant data items.
    2. THEN, after the table, append the action tag: |ACTION:SEARCH:<filter_term>|
    
    DO NOT just say "Here are the items". YOU MUST DISPLAY THE TABLE.
    
    CONTEXT DATA:
    {json.dumps(context_data, indent=2)}
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000", # Dummy for desktop
        "X-Title": SITE_NAME,
    }

    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        
        content = data['choices'][0]['message']['content']
        
        # Parse Action Tags (Simple parser)
        action = None
        if "|ACTION:SEARCH:" in content:
            parts = content.split("|ACTION:SEARCH:")
            term = parts[1].split("|")[0].strip()
            action = {"type": "SEARCH", "payload": term}
            # Remove tag from display
            content = content.replace(f"|ACTION:SEARCH:{term}|", "")
            
        return {"response": content, "action": action}

    except Exception as e:
        print(f"AI Service Error: {e}")
        import traceback
        traceback.print_exc()
        return {"response": f"I encountered an error connecting to the AI service: {str(e)}", "action": None}
