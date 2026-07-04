from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np


class EmbeddingProvider(ABC):
    """Produces L2-normalized vectors for images and text in a shared space.

    Implementations: FashionCLIPProvider (self-hosted, no per-image cost) and
    StubEmbeddingProvider (color-statistics pseudo-vectors, keeps the pipeline
    moving if the model can't load).
    """

    dim: int

    @property
    @abstractmethod
    def key(self) -> str:
        """Stable identifier used to namespace stored vectors."""

    @abstractmethod
    def embed_images(self, paths: list[Path]) -> np.ndarray:
        """Return an (n, dim) array of normalized image embeddings."""

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Return an (n, dim) array of normalized text embeddings."""


def normalize(mat: np.ndarray) -> np.ndarray:
    return mat / (np.linalg.norm(mat, axis=-1, keepdims=True) + 1e-9)
