cat << 'EOF' > README.md
# ☕ Coffee Barista Assistant — Hybrid RAG with Google Gemini

> An intelligent, conversational coffee barista powered by **Google Gemini**, built and demonstrated during the **"Real-World AI with RAG & Gemini"** hands-on developer workshop.

---

## 📌 Project Overview
In retail and hospitality, static menus and keyword matching cannot handle natural, complex customer requests like:
> *"I have $5, want something cold with a cinnamon kick, but I am lactose intolerant."*

This project bridges that gap by combining **Google Gemini's reasoning and function-calling capabilities** with a **Hybrid Retrieval-Augmented Generation (RAG)** architecture:
- **Semantic Layer (ChromaDB):** Retrieves items matching sensory descriptions, flavor profiles, and subjective preferences.
- **Relational Layer (SQLite):** Strictly enforces hard business constraints (budget caps, allergen exclusions, inventory status).

---

## 🏗️ Architecture

```text
User Query (Natural Language)
            │
            ▼
┌─────────────────────────┐
│      Google Gemini      │ ──► Identifies constraints (max price, allergens, flavor notes)
└───────────┬─────────────┘
            │ Tool Call: hybrid_menu_search(...)
            ▼
┌─────────────────────────┐
│   Hybrid Search Engine  │
├─────────────────────────┤
│ 1. Vector Search (Chroma)──► Top semantic matches by flavor/category
│ 2. SQL Filter (SQLite)   ──► Hard filter (Price <= X, In-Stock, Allergen check)
└───────────┬─────────────┘
            │ Grounded Menu Results
            ▼
┌─────────────────────────┐
│     Gemini Response     │ ──► Accurate, conversational barista recommendation
└─────────────────────────┘
