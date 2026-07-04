import logging
from functools import lru_cache

from ...config import get_settings
from .base import VibeSummarizer
from .stub import StubVibeSummarizer

logger = logging.getLogger("muse.vibe")


@lru_cache
def get_vibe_summarizer() -> VibeSummarizer:
    settings = get_settings()
    if settings.vibe_provider == "gemini":
        try:
            from .gemini import GeminiVibeSummarizer

            summarizer = GeminiVibeSummarizer(settings.gemini_api_key, settings.gemini_model)
            logger.info("Vibe summarizer: Gemini (%s)", settings.gemini_model)
            return summarizer
        except Exception as exc:
            logger.warning("Gemini unavailable (%s) — using stub vibe summarizer", exc)
    logger.info("Vibe summarizer: stub")
    return StubVibeSummarizer()
