from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from ..events import log_event

router = APIRouter(prefix="/events", tags=["events"])


class EventIn(BaseModel):
    name: str
    properties: dict[str, Any] = {}


@router.post("")
async def create_event(event: EventIn):
    log_event(event.name, event.properties)
    return {"ok": True}
