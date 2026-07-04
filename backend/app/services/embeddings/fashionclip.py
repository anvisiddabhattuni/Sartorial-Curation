from pathlib import Path

import numpy as np
from PIL import Image

from .base import EmbeddingProvider, normalize

FASHION_CLIP_ID = "patrickjohncyh/fashion-clip"
STOCK_CLIP_ID = "openai/clip-vit-base-patch32"


class CLIPEmbeddingProvider(EmbeddingProvider):
    """Self-hosted CLIP-family embeddings via transformers. No per-image cost.

    Used for FashionCLIP (preferred, fashion-tuned) and stock OpenAI CLIP
    (fallback). Construction runs a self-test on both towers; a failure makes
    the factory drop to the next rung of the fallback ladder."""

    dim = 512

    def __init__(self, model_id: str = FASHION_CLIP_ID) -> None:
        import torch
        from transformers import CLIPModel, CLIPProcessor

        self.model_id = model_id
        self._torch = torch
        self._model = CLIPModel.from_pretrained(model_id)
        self._processor = CLIPProcessor.from_pretrained(model_id)
        self._model.eval()
        self._self_test()

    @property
    def key(self) -> str:
        # Basename so hub ids and local repaired copies share a namespace.
        return f"clip:{Path(self.model_id).name}"

    def _self_test(self) -> None:
        """Some torch/macOS/checkpoint combinations produce NaN embeddings or
        crash in the text tower. Verify both towers on dummy inputs so a broken
        provider is rejected at startup instead of serving 500s later."""
        img = Image.new("RGB", (224, 224), (180, 170, 160))
        fi = self._embed_image_batch([img])
        ft = self.embed_texts(["beige linen blazer"])
        if np.isnan(fi).any() or np.isnan(ft).any():
            raise RuntimeError(f"{self.model_id} self-test produced NaN embeddings")

    def _embed_image_batch(self, images: list[Image.Image]) -> np.ndarray:
        vectors: list[np.ndarray] = []
        batch_size = 8
        with self._torch.no_grad():
            for i in range(0, len(images), batch_size):
                inputs = self._processor(
                    images=images[i : i + batch_size], return_tensors="pt"
                )
                feats = self._model.get_image_features(**inputs)
                vectors.append(feats.cpu().numpy())
        return normalize(np.concatenate(vectors, axis=0).astype(np.float32))

    def embed_images(self, paths: list[Path]) -> np.ndarray:
        images = [Image.open(p).convert("RGB") for p in paths]
        return self._embed_image_batch(images)

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        with self._torch.no_grad():
            inputs = self._processor(
                text=texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=77,
            )
            feats = self._model.get_text_features(**inputs)
        return normalize(feats.cpu().numpy().astype(np.float32))
