"""SerpAPI Google Shopping provider — real products behind the same interface.

Falls back to the mock catalog automatically when the API key is missing,
quota is exceeded, or the request fails. Selected via PRODUCT_PROVIDER=serpapi."""

import hashlib
import json
import logging
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import certifi

from .base import Product, ProductSearchProvider

logger = logging.getLogger("muse.products.serpapi")

# Some Python builds (notably python.org installers on macOS) don't wire up
# the system trust store for urllib, so HTTPS requests fail with
# CERTIFICATE_VERIFY_FAILED. Use certifi's bundle explicitly.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

_CATEGORY_KEYWORDS: list[tuple[str, list[str]]] = [
    ("dresses", ["dress", "gown", "slip dress", "midi dress"]),
    ("outerwear", ["jacket", "coat", "blazer", "cardigan", "parka", "vest"]),
    ("bottoms", ["pant", "trouser", "jean", "denim", "skirt", "short", "legging"]),
    ("shoes", ["shoe", "sneaker", "boot", "heel", "sandal", "loafer", "flat"]),
    ("accessories", ["bag", "belt", "scarf", "hat", "jewelry", "earring", "necklace", "sunglasses"]),
    ("tops", ["shirt", "top", "tee", "blouse", "sweater", "knit", "hoodie", "tank"]),
]


def _infer_category(title: str) -> str:
    t = title.lower()
    for category, keywords in _CATEGORY_KEYWORDS:
        if any(k in t for k in keywords):
            return category
    return "tops"


def _parse_price(raw: Any) -> float:
    if raw is None:
        return 0.0
    if isinstance(raw, (int, float)):
        return float(raw)
    text = str(raw)
    match = re.search(r"[\d,]+\.?\d*", text.replace(",", ""))
    return float(match.group()) if match else 0.0


def _product_id(link: str, title: str) -> str:
    digest = hashlib.sha256(f"{link}|{title}".encode()).hexdigest()[:12]
    return f"serp-{digest}"


class SerpApiProductProvider(ProductSearchProvider):
    name = "serpapi"

    def __init__(self, api_key: str, fallback: ProductSearchProvider) -> None:
        if not api_key:
            raise ValueError("SERPAPI_API_KEY is not set")
        self._api_key = api_key
        self._fallback = fallback
        self._cache: dict[str, Product] = {}

    def _fetch_query(self, query: str) -> list[dict[str, Any]]:
        params = urllib.parse.urlencode(
            {
                "engine": "google_shopping",
                "q": query,
                "api_key": self._api_key,
                "num": 20,
            }
        )
        url = f"https://serpapi.com/search.json?{params}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=20, context=_SSL_CONTEXT) as resp:
            return json.loads(resp.read()).get("shopping_results", [])

    def _to_product(self, item: dict[str, Any], query: str) -> Product | None:
        title = str(item.get("title") or "").strip()
        link = str(item.get("link") or item.get("product_link") or "").strip()
        if not title or not link:
            return None
        retailer = str(item.get("source") or item.get("seller") or "Retailer").strip()
        image = str(item.get("thumbnail") or item.get("image") or "").strip()
        if not image:
            return None
        price = _parse_price(item.get("extracted_price") or item.get("price"))
        pid = _product_id(link, title)
        return Product(
            id=pid,
            title=title,
            price=price,
            retailer=retailer,
            image_url=image,
            buy_link=link,
            details=str(item.get("snippet") or item.get("description") or title),
            category=_infer_category(title),
            source_query=query,
        )

    def search(self, queries: list[str], filters: dict[str, Any] | None = None) -> list[Product]:
        seen: set[str] = set()
        products: list[Product] = []
        for query in queries[:6]:
            try:
                items = self._fetch_query(query)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
                logger.warning("SerpAPI query %r failed (%s)", query, exc)
                continue
            for item in items:
                product = self._to_product(item, query)
                if product is None or product.id in seen:
                    continue
                seen.add(product.id)
                products.append(product)
                self._cache[product.id] = product
                if len(products) >= 48:
                    break
            if len(products) >= 48:
                break

        if len(products) < 12:
            logger.warning(
                "SerpAPI returned %d products (<12) — supplementing with mock catalog",
                len(products),
            )
            mock = self._fallback.search(queries, filters)
            for p in mock:
                if p.id not in seen:
                    products.append(p)
                    seen.add(p.id)
                if len(products) >= 48:
                    break
        logger.info("SerpAPI provider: %d candidate products", len(products))
        return products

    def get(self, product_id: str) -> Product | None:
        return self._cache.get(product_id)
