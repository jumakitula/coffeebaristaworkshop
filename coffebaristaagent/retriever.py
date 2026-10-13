import os
import sqlite3
import chromadb
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from google import genai

CURRENT_DIR = Path(__file__).resolve().parent
SQLITE_DB = CURRENT_DIR / "barista.db"
CHROMA_DIR = CURRENT_DIR / "chroma_db"

load_dotenv(CURRENT_DIR.parent / ".env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_query_embedding(text: str):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return response.embeddings[0].values

def hybrid_menu_search(
    query_text: str,
    max_price: Optional[float] = None,
    exclude_allergens: Optional[List[str]] = None,
    limit: int = 4
) -> List[Dict[str, Any]]:
    # Step 1: Semantic search via Gemini Query Embedding
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = chroma_client.get_collection("menu_embeddings")

    count = collection.count()
    if count == 0:
        return []

    q_emb = get_query_embedding(query_text)
    results = collection.query(
        query_embeddings=[q_emb],
        n_results=min(limit * 3, count)
    )

    candidate_ids = results["ids"][0] if results and results["ids"] else []
    if not candidate_ids:
        return []

    # Step 2: Relational constraint filtering via SQLite
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    placeholders = ",".join("?" for _ in candidate_ids)
    sql = f"""
        SELECT id, name, category, price, allergens, tags
        FROM menu_items
        WHERE id IN ({placeholders})
          AND in_stock = 1
    """
    params = list(candidate_ids)

    if max_price is not None:
        sql += " AND price <= ?"
        params.append(max_price)

    cursor.execute(sql, params)
    rows = {row["id"]: dict(row) for row in cursor.fetchall()}
    conn.close()

    # Step 3: Allergen filtering while preserving rank
    final_matches = []
    for cid in candidate_ids:
        if cid in rows:
            item = rows[cid]
            if exclude_allergens:
                item_allergens = (item.get("allergens") or "").lower()
                if any(allergen.lower() in item_allergens for allergen in exclude_allergens):
                    continue
            final_matches.append(item)
            if len(final_matches) >= limit:
                break

    return final_matches
