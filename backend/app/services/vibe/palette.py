"""Dominant color palette extraction via tiny k-means (numpy only)."""

from pathlib import Path

import numpy as np
from PIL import Image


def extract_palette(image_paths: list[Path], k: int = 5, iters: int = 12) -> list[str]:
    samples = []
    for p in image_paths:
        img = Image.open(p).convert("RGB").resize((48, 48))
        samples.append(np.asarray(img, dtype=np.float32).reshape(-1, 3))
    pixels = np.concatenate(samples, axis=0)

    rng = np.random.default_rng(7)
    centers = pixels[rng.choice(len(pixels), size=k, replace=False)]
    for _ in range(iters):
        dists = ((pixels[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        labels = dists.argmin(axis=1)
        for j in range(k):
            members = pixels[labels == j]
            if len(members) > 0:
                centers[j] = members.mean(axis=0)

    counts = np.bincount(labels, minlength=k)
    order = np.argsort(-counts)
    return ["#%02x%02x%02x" % tuple(int(c) for c in centers[j]) for j in order]
