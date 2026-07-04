from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from ..config import get_settings
from ..events import log_event
from ..services.pipeline import analyze_board
from ..storage import InvalidImageError, create_board, get_board

router = APIRouter(prefix="/boards", tags=["boards"])


@router.post("")
async def submit_board(files: list[UploadFile]):
    settings = get_settings()
    if len(files) < settings.min_images or len(files) > settings.max_images:
        raise HTTPException(
            status_code=422,
            detail=f"Please upload between {settings.min_images} and {settings.max_images} images.",
        )
    raw_files = [await f.read() for f in files]
    try:
        board = create_board(raw_files, settings.max_image_px)
    except InvalidImageError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    log_event("board_submitted", {"board_id": board.id, "image_count": len(board.image_paths)})
    return {"board_id": board.id, "image_count": len(board.image_paths)}


@router.post("/{board_id}/analyze")
async def analyze(board_id: str):
    board = get_board(board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    # CPU-bound (embeddings) — keep the event loop free.
    return await run_in_threadpool(analyze_board, board)


@router.get("/{board_id}")
async def board_status(board_id: str):
    board = get_board(board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return {
        "board_id": board.id,
        "image_count": len(board.image_paths),
        "analyzed": board.analysis is not None,
    }
