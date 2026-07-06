import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .events import init_events
from .routers import boards, events, products

logging.basicConfig(level=logging.INFO)

settings = get_settings()

app = FastAPI(title="Muse API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    # Comma-separated so both a local dev frontend and a deployed one (e.g.
    # Vercel) can be allowed at once without a code change.
    allow_origins=[o.strip() for o in settings.frontend_origin.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    init_events(settings.database_url)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(boards.router)
app.include_router(events.router)
app.include_router(products.router)
