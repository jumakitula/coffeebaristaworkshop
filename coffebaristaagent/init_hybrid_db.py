import os
import json
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import chromadb

CURRENT_DIR = Path(__file__).resolve().parent
SQLITE_DB = CURRENT_DIR / "barista.db"
CHROMA_DIR = CURRENT_DIR / "chroma_db"
MENU_JSON = CURRENT_DIR / "menu.json"

# Load environment & configure client
load_dotenv(CURRENT_DIR.parent / ".env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_embedding(text: str):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return response.embeddings[0].values

def setup_databases():
    # 1. Setup SQLite
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            in_stock BOOLEAN DEFAULT 1,
            allergens TEXT,
            tags TEXT
        )
    """)
    cursor.execute("DELETE FROM menu_items")

    # 2. Setup ChromaDB
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        chroma_client.delete_collection("menu_embeddings")
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name="menu_embeddings",
        metadata={"hnsw:space": "cosine"}
    )

    # 3. Read menu.json
    with open(MENU_JSON, "r", encoding="utf-8") as f:
        items = json.load(f)

    chroma_docs = []
    chroma_metadatas = []
    chroma_ids = []
    chroma_embeddings = []

    print(f"Generating Gemini embeddings with gemini-embedding-001 for {len(items)} items...")
    for idx, item in enumerate(items):
        item_id = str(item.get("id", idx + 1))
        name = item.get("name", "Unknown")
        description = item.get("description", "")
        price = float(item.get("price", 0.0))
        category = item.get("category", "Beverage")
        
        raw_tags = item.get("tags", [])
        tags = ", ".join(raw_tags) if isinstance(raw_tags, list) else str(raw_tags)
        
        raw_allergens = item.get("allergens", [])
        allergens = ", ".join(raw_allergens) if isinstance(raw_allergens, list) else str(raw_allergens)

        cursor.execute(
            """
            INSERT INTO menu_items (id, name, category, price, in_stock, allergens, tags)
            VALUES (?, ?, ?, ?, 1, ?, ?)
            """,
            (item_id, name, category, price, allergens, tags)
        )

        embed_text = f"Item: {name}. Category: {category}. Description: {description}. Tags: {tags}"
        emb = get_embedding(embed_text)

        chroma_docs.append(embed_text)
        chroma_metadatas.append({"id": item_id, "name": name, "price": price})
        chroma_ids.append(item_id)
        chroma_embeddings.append(emb)

    conn.commit()
    conn.close()

    collection.add(
        documents=chroma_docs,
        embeddings=chroma_embeddings,
        metadatas=chroma_metadatas,
        ids=chroma_ids
    )

    print(f"Hybrid DB initialized: {len(items)} items synced to SQLite & ChromaDB.")

if __name__ == "__main__":
    setup_databases()
