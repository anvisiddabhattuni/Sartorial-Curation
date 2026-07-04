# Muse

Turn fashion inspiration images into a shoppable page of real clothes.

Upload 5–30 inspiration images → Muse analyzes the whole board's aesthetic
(FashionCLIP embeddings + a vision-LLM) → shows a "Your Vibe" summary and a
grid of shoppable products ranked by similarity to your board.

## Stack

- **Frontend:** Next.js + React + Tailwind CSS (`frontend/`)
- **Backend:** FastAPI, Python (`backend/`)
- **Embeddings:** FashionCLIP, self-hosted (stub fallback)
- **Vibe summary:** Gemini Flash (stub fallback)
- **Vector search:** Postgres + pgvector (in-memory fallback)
- **Products:** MockProductProvider (real provider swappable via env)

## Run it

### 1. Backend (port 8000)

```bash
cd backend
python3 -m venv .venv            # first time only
.venv/bin/pip install -r requirements.txt
cp ../.env.example .env          # then fill in GEMINI_API_KEY etc.
.venv/bin/uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (port 3000)

```bash
cd frontend
npm install
cp ../.env.example .env.local   # optional; defaults to http://localhost:8000
npm run dev
```

Open http://localhost:3000, drop in 5–30 JPG/PNG/WebP images, and go.

### Optional: Postgres + pgvector

```bash
brew install postgresql@17 pgvector
brew services start postgresql@17
/opt/homebrew/opt/postgresql@17/bin/createdb muse
```

If Postgres is unreachable the API automatically falls back to an in-memory
vector store and JSONL event logging — the app still works end to end.

## Configuration

All keys and provider choices live in `backend/.env` (template:
[.env.example](.env.example)). Providers are swappable without code changes:
`EMBEDDING_PROVIDER`, `VIBE_PROVIDER`, `PRODUCT_PROVIDER`, `VECTOR_STORE`.

| Variable | Options | Notes |
|---|---|---|
| `EMBEDDING_PROVIDER` | `fashionclip`, `stub` | FashionCLIP self-hosted; stub if model unavailable |
| `VIBE_PROVIDER` | `gemini`, `stub` | Set `GEMINI_API_KEY` for real summaries |
| `PRODUCT_PROVIDER` | `mock`, `serpapi` | Set `SERPAPI_API_KEY` for real products; mock supplements on failure |
| `VECTOR_STORE` | `pgvector`, `memory` | Postgres preferred; auto-falls back to in-memory |

## Demo smoke test

With the API running on port 8000:

```bash
cd backend
.venv/bin/python scripts/smoke_test.py
```

Uploads 5 test images, runs analysis, and asserts ≥12 products with buy links.

## Events

Logged to Postgres (or `backend/data/events.jsonl` fallback):
`board_submitted`, `results_rendered`, `card_clicked`.
