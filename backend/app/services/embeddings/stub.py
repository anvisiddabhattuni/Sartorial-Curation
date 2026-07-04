"""Stub embedding provider — keeps the pipeline moving without FashionCLIP.

Images: a deterministic vector built from real color/luminance statistics, so
visually similar boards still land near each other. Text: a seeded hash-based
pseudo-vector mixed with keyword color cues so ranking stays deterministic.
"""

import hashlib
from pathlib import Path

import numpy as np
from PIL import Image

from .base import EmbeddingProvider, normalize

_COLOR_WORDS = {
    "black": (0, 0, 0), "white": (255, 255, 255), "cream": (245, 240, 225),
    "beige": (222, 210, 185), "brown": (120, 85, 60), "tan": (200, 170, 130),
    "navy": (25, 35, 80), "blue": (60, 100, 200), "denim": (80, 105, 150),
    "grey": (128, 128, 128), "gray": (128, 128, 128), "green": (70, 120, 80),
    "olive": (110, 115, 70), "red": (180, 40, 40), "pink": (230, 170, 190),
    "lavender": (200, 180, 225),
}


def _stats_vector(pixels: np.ndarray, dim: int, seed_key: str) -> np.ndarray:
    """Blend real color statistics with a deterministic pseudo-random tail."""
    mean = pixels.mean(axis=0) / 255.0
    std = pixels.std(axis=0) / 128.0
    lum = pixels.mean() / 255.0
    head = np.concatenate([mean, std, [lum]])

    seed = int.from_bytes(hashlib.sha256(seed_key.encode()).digest()[:4], "big")
    tail = np.random.default_rng(seed).normal(size=dim - len(head)) * 0.15
    return np.concatenate([head, tail]).astype(np.float32)


class StubEmbeddingProvider(EmbeddingProvider):
    dim = 512

    @property
    def key(self) -> str:
        return "stub"

    def embed_images(self, paths: list[Path]) -> np.ndarray:
        vecs = []
        for p in paths:
            img = Image.open(p).convert("RGB").resize((64, 64))
            pixels = np.asarray(img, dtype=np.float32).reshape(-1, 3)
            vecs.append(_stats_vector(pixels, self.dim, p.name))
        return normalize(np.stack(vecs))

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        vecs = []
        for text in texts:
            lower = text.lower()
            hits = [np.array(rgb, dtype=np.float32) for w, rgb in _COLOR_WORDS.items() if w in lower]
            pixels = np.stack(hits) if hits else np.full((1, 3), 128.0, dtype=np.float32)
            vecs.append(_stats_vector(pixels, self.dim, text))
        return normalize(np.stack(vecs))
