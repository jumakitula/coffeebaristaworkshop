import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv
from google import genai
from google.genai import types
from .retriever import hybrid_menu_search

CURRENT_DIR = Path(__file__).resolve().parent
# Load .env from project root
load_dotenv(CURRENT_DIR.parent / ".env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please check your .env or Streamlit Secrets.")

client = genai.Client(api_key=api_key)

# Stable, valid Gemini models with free-tier access
CANDIDATE_MODELS = [
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
]

SYSTEM_INSTRUCTION = (
    "You are an authentic, cheerful coffee barista assistant at the Coffee Shop. "
    "When customers ask about drinks, pastries, dietary restrictions, prices, or recommendations, "
    "always invoke the `get_menu_recommendations` tool to query the grounded database. "
    "Never invent prices or mention drinks/pastries that are not returned by the tool."
)

def get_menu_recommendations(
    user_query: str, 
    max_price: Optional[float] = None, 
    exclude_dairy: bool = False
) -> str:
    """Searches the coffee shop menu using hybrid semantic vector search and SQLite filtering.
    
    Args:
        user_query: Description of what the customer wants (e.g. 'sweet iced drink', 'cinnamon pastry').
        max_price: Maximum price ceiling in dollars (e.g. 5.0).
        exclude_dairy: True if the user wants dairy-free or is lactose intolerant.
    """
    allergens = ["dairy", "milk"] if exclude_dairy else []
    results = hybrid_menu_search(
        query_text=user_query,
        max_price=max_price,
        exclude_allergens=allergens,
        limit=3
    )

    if not results:
        return "No menu items match those exact criteria."

    formatted = []
    for item in results:
        formatted.append(
            f"- {item['name']} (${item['price']:.2f}): Category: {item['category']} | Tags: {item['tags']} | Allergens: {item['allergens'] or 'None'}"
        )
    return "\n".join(formatted)

def create_barista_chat():
    """Initializes a chat session using the first available working model."""
    last_error = None
    for model_name in CANDIDATE_MODELS:
        try:
            chat = client.chats.create(
                model=model_name,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=[get_menu_recommendations],
                    temperature=0.7,
                ),
            )
            return chat
        except Exception as e:
            last_error = e
            continue
            
    raise RuntimeError(f"Could not connect to any candidate model. Last error: {last_error}")
