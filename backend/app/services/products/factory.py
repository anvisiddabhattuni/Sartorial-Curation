import logging
from functools import lru_cache

from ...config import get_settings
from .base import ProductSearchProvider
from .mock import MockProductProvider

logger = logging.getLogger("muse.products")


def _mock_provider() -> MockProductProvider:
    return MockProductProvider(get_settings().api_base_url)


@lru_cache
def get_product_provider() -> ProductSearchProvider:
    settings = get_settings()
    mock = _mock_provider()

    if settings.product_provider == "serpapi":
        try:
            from .serpapi import SerpApiProductProvider

            provider = SerpApiProductProvider(settings.serpapi_api_key, fallback=mock)
            logger.info("Product provider: serpapi (mock fallback on failure)")
            return provider
        except Exception as exc:
            logger.warning("SerpAPI unavailable (%s) — using mock catalog", exc)

    logger.info("Product provider: mock")
    return mock
