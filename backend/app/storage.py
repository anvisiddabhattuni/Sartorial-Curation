"""Session-scoped board storage. Uploaded images are downscaled and kept on
local disk under backend/data/boards/<board_id>/; analysis results are cached
in memory so re-runs of the same board are free."""

import shutil
import uuid
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .services.vibe.base import VibeResult

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BOARDS_DIR = DATA_DIR / "boards"

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


@dataclass
class Board:
    id: str
    image_paths: list[Path]
    analysis: dict[str, Any] | None = None
    # Cached so /refine can nudge toward new feedback without re-embedding images.
    profile: np.ndarray | None = None
    vibe: VibeResult | None = None


_boards: dict[str, Board] = {}


class InvalidImageError(Exception):
    pass


def _process_image(raw: bytes, dest: Path, max_px: int) -> None:
    try:
        img = Image.open(BytesIO(raw))
        img_format = img.format
    except Exception as exc:
        raise InvalidImageError(f"could not read image: {exc}") from exc
    if img_format not in ALLOWED_FORMATS:
        raise InvalidImageError(f"unsupported format {img_format}; use JPG, PNG, or WebP")
    img = img.convert("RGB")
    img.thumbnail((max_px, max_px))
    img.save(dest, "JPEG", quality=88)


def create_board(files: list[bytes], max_px: int) -> Board:
    board_id = uuid.uuid4().hex[:12]
    board_dir = BOARDS_DIR / board_id
    board_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    try:
        for i, raw in enumerate(files):
            dest = board_dir / f"{i:03d}.jpg"
            _process_image(raw, dest, max_px)
            paths.append(dest)
    except InvalidImageError:
        shutil.rmtree(board_dir, ignore_errors=True)
        raise
    board = Board(id=board_id, image_paths=paths)
    _boards[board_id] = board
    return board


def get_board(board_id: str) -> Board | None:
    return _boards.get(board_id)
