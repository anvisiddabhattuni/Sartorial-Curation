from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class Product(BaseModel):
    id: str
    title: str
    price: float
    currency: str = "USD"
    retailer: str
    image_url: str
    buy_link: str
    details: str
    category: str  # tops | bottoms | outerwear | dresses | shoes | accessories
    color: str = ""  # hex, used for palette matching / mock imagery


class ProductSearchProvider(ABC):
    """Finds candidate products for a set of style queries. Candidates are
    then ranked by vector similarity to the board profile.

    Implementations: MockProductProvider (curated fake catalog, always
    available) and real API providers (e.g. SerpAPI) behind the same
    interface — selected via the PRODUCT_PROVIDER env var."""

    name: str

    @abstractmethod
    def search(self, queries: list[str], filters: dict[str, Any] | None = None) -> list[Product]:
        """Return candidate products across categories and price points."""
