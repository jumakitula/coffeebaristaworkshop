import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from .retriever import hybrid_menu_search

CURRENT_DIR = Path(__file__).resolve().parent
load_dotenv(CURRENT_DIR.parent / ".env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Models with much larger free tier allowances (avoid gemini-3.8-flash free limit of 20)
CANDIDATE_MODELS = [
    "gemini-flash-latest",
    "gemini-2.5-flash",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash-lite",
]

SYSTEM_INSTRUCTION = (
    "You are an authentic, cheerful coffee barista assistant at the Coffee Shop. "
    "When customers ask about drinks, pastries, dietary restrictions, prices, or recommendations, "
    "always invoke the `get_menu_recommendations` tool to query the grounded database. "
    "Never invent prices or mention drinks/pastries that are not returned by the tool."
)

def get_menu_recommendations(user_query: str, max_price: float = None, exclude_dairy: bool = False) -> str:
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
    for model_name in CANDIDATE_MODELS:
        try:
            return client.chats.create(
                model=model_name,
                config={
                    "system_instruction": SYSTEM_INSTRUCTION,
                    "tools": [get_menu_recommendations],
                }
            )
        except Exception:
            continue
    raise RuntimeError("All candidate models currently unavailable or quota exhausted.")
