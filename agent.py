import json
import os
from google import genai
from google.genai import types


def get_menu() -> str:
    try:
        with open("coffeebaristaagent/menu.json", "r") as f:
            menu_data = json.load(f)
            return json.dumps(menu_data)
    except Exception as e:
        return json.dumps({"error": f"Could not retrieve menu: {str(e)}"})

API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def run_barista_agent(user_message, history=None):
    system_instruction = """You are a friendly barista at ☕Coffee Shop. Your job is to recommend drinks and pastries to customers based on their preferences.

    Rules you MUST follow:
    1.You must recommend items ONLY from the menu returned by get_menu().
    2.Do NOT recommend or suggest any item that is not present in the menu.
    3.If a User's preference is Vague or unclear, ask exactly ONE friendly clarifying question to narrow down what they want (e.g., cold or hot, sweet or strong, coffee or pastry).
    4.Be warm and welcoming, but remain professional.
    5.Ground your recommendations in the actual tags, descriptions, and allergens listed in the menu (e.g., if a user is dairy-free, recommend ONLY items tagged 'dairy-free' or with no dairy allergens)."""

    chat = client.chats.create(
    model="gemini-3.5-flash", 
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[get_menu],
        temperature=0.4
    ),
    history=history
    )
    response = chat.send_message(user_message)
    return response.text, chat.get_history()

