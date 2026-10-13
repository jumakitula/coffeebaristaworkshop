
# ☕ Coffee Barista Assistant — Hybrid RAG with Google Gemini

> An intelligent conversational assistant powered by **Google Gemini**, built and demonstrated during the **"BUILD WITH GOOGLE: RAG & Gemini"** hands-on developer workshop.

---

## 📌 Problem & Overview

When customers order, their requests are often subjective and constraint-heavy at the same time:
> *"I have $5, want something cold with a cinnamon kick to wake me up, but I am lactose intolerant."*

Traditional systems fail on this dual requirement:
- **Keyword / Relational Search** cannot parse subjective sensory notes like *"refreshing with a kick"*.
- **Pure Vector Search (Standard RAG)** understands the vibe, but ignores hard mathematical ceilings or allergen exclusions because similarity scores don't enforce strict boolean safety.

This project implements a **Hybrid Retrieval-Augmented Generation (RAG)** pipeline:
1. **Semantic Search (ChromaDB + Gemini Embeddings):** Retrieves items matching sensory descriptions, mood, and flavor profiles.
2. **Relational Search (SQLite):** Strictly enforces hard constraints (max budget, stock availability, allergen safety).
3. **Agent Orchestration (Google Gemini):** Extracts entities from natural language, calls the hybrid search tool dynamically, and responds conversationally without hallucinations.

---

## 🏗️ Architecture

```text
User Request (Natural Language)
            │
            ▼
┌─────────────────────────┐
│      Google Gemini      │ ──► Extracts price cap, allergens, and flavor notes
└───────────┬─────────────┘
            │ Tool Call: hybrid_menu_search(...)
            ▼
┌─────────────────────────┐
│   Hybrid Search Engine  │
├─────────────────────────┤
│ 1. ChromaDB (Vector)    │ ──► Matches flavor / vibe via embeddings
│ 2. SQLite (Relational)  │ ──► Filters WHERE price <= X AND allergens NOT IN (...)
└───────────┬─────────────┘
            │ Grounded Menu Results
            ▼
┌─────────────────────────┐
│     Gemini Response     │ ──► Accurate, grounded, conversational recommendation
└─────────────────────────┘
