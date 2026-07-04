#!/usr/bin/env python3
"""Smoke test for the Muse demo pipeline. Run with the API up on :8000.

Usage:
    cd backend && .venv/bin/python scripts/smoke_test.py
"""

from __future__ import annotations

import io
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

API = "http://localhost:8000"
MIN_PRODUCTS = 12


def _health() -> None:
    with urllib.request.urlopen(f"{API}/health", timeout=5) as resp:
        data = json.loads(resp.read())
    assert data.get("status") == "ok", data


def _upload_board() -> str:
    boundary = "----MuseSmokeTest"
    body = b""
    colors = [(210, 195, 180), (190, 205, 215), (120, 115, 110), (230, 225, 220), (160, 140, 125)]
    for i, color in enumerate(colors):
        img = Image.new("RGB", (480, 600), color)
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="files"; filename="smoke{i}.jpg"\r\n'.encode()
        body += b"Content-Type: image/jpeg\r\n\r\n"
        body += buf.getvalue() + b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{API}/boards",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["board_id"]


def _analyze(board_id: str) -> dict:
    req = urllib.request.Request(f"{API}/boards/{board_id}/analyze", method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())


def main() -> int:
    try:
        print("→ health check")
        _health()
        print("→ upload 5 images")
        board_id = _upload_board()
        print(f"  board_id={board_id}")
        print("→ analyze board")
        result = _analyze(board_id)
        tags = result["vibe"]["tags"]
        products = result["products"]
        print(f"  vibe tags: {tags}")
        print(f"  products: {len(products)}")
        assert len(tags) >= 4, "expected at least 4 vibe tags"
        assert len(products) >= MIN_PRODUCTS, f"expected >= {MIN_PRODUCTS} products"
        assert all(p.get("buy_link") for p in products), "missing buy links"
        print("✓ smoke test passed")
        return 0
    except (urllib.error.URLError, AssertionError, KeyError) as exc:
        print(f"✗ smoke test failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
