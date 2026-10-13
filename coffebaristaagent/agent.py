import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
from .retriever import hybrid_menu_search

CURRENT_DIR = Path(__file__).resolve().parent
load_dotenv(CURRENT_DIR.parent / ".env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Preferred models in priority order based on availability
CANDIDATE_MODELS = [
    "gemini-flash-latest",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
]

def get_menu_recommendations(user_query: str, max_price: float = None, exclude_dairy: bool = False) -> str:
    """
    Searches the coffee shop menu using hybrid semantic vector search and SQLite filtering.
    Call this when a customer asks for drink recommendations, ingredients, prices, or menu items.
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

SYSTEM_INSTRUCTION = (
    "You are an authentic, cheerful coffee barista assistant. "
    "When customers ask about drinks, menu options, prices, or recommendations, "
    "always invoke the `get_menu_recommendations` tool to query the grounded database. "
    "Never invent prices or mention drinks not returned by the tool."
)

def create_barista_chat():
    """Initializes chat session with the first available working model."""
    last_error = None
    for model_name in CANDIDATE_MODELS:
        try:
            chat = client.chats.create(
                model=model_name,
                config={
                    "system_instruction": SYSTEM_INSTRUCTION,
                    "tools": [get_menu_recommendations],
                }
            )
            return chat
        except Exception as e:
            last_error = e
            continue
    raise RuntimeError(f"All candidate models unavailable. Last error: {last_error}")
