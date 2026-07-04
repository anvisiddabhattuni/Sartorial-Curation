import logging
from functools import lru_cache
from pathlib import Path

from ...config import get_settings
from .base import EmbeddingProvider
from .stub import StubEmbeddingProvider

logger = logging.getLogger("muse.embeddings")

# Local re-saved FashionCLIP copy (see probe.repair_clip_model).
FASHION_CLIP_LOCAL_DIR = (
    Path(__file__).resolve().parents[3] / "data" / "models" / "fashion-clip"
)


def _try_clip(model_id: str) -> EmbeddingProvider | None:
    from .probe import probe_clip_model

    # Probe in a subprocess first: a broken checkpoint can SIGBUS the whole
    # process, which an in-process try/except cannot catch.
    if not probe_clip_model(model_id):
        return None
    try:
        from .fashionclip import CLIPEmbeddingProvider

        provider = CLIPEmbeddingProvider(model_id)
        logger.info("Embedding provider: %s", model_id)
        return provider
    except Exception as exc:
        logger.warning("Embedding model %s unavailable (%s)", model_id, exc)
        return None


def _fashionclip_source() -> str:
    """Prefer the locally repaired FashionCLIP copy; repair it on first use.
    The original hub checkpoint SIGBUSes at inference on some torch/macOS
    combos — re-saving as fresh safetensors fixes it (verified by probe)."""
    from .fashionclip import FASHION_CLIP_ID
    from .probe import repair_clip_model

    local = FASHION_CLIP_LOCAL_DIR
    if not (local / "config.json").exists():
        if not repair_clip_model(FASHION_CLIP_ID, str(local)):
            return FASHION_CLIP_ID
    return str(local)


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """Fallback ladder: FashionCLIP (locally repaired) -> stock CLIP -> stub.
    Each rung must pass a subprocess probe (a bad checkpoint can crash, not
    just error), so whichever tier actually works on this machine gets used."""
    from .fashionclip import STOCK_CLIP_ID

    settings = get_settings()
    if settings.embedding_provider == "stub":
        ladder: list[str] = []
    elif settings.embedding_provider == "clip":
        ladder = [STOCK_CLIP_ID]
    else:
        ladder = [_fashionclip_source(), STOCK_CLIP_ID]

    for model_id in ladder:
        provider = _try_clip(model_id)
        if provider is not None:
            return provider

    logger.info("Embedding provider: stub")
    return StubEmbeddingProvider()
