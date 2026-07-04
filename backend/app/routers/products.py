from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..services.products import get_product_provider
from ..services.products.imagery import product_svg
from ..services.products.mock import MockProductProvider

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}/image.svg")
async def product_image(product_id: str):
    provider = get_product_provider()
    product = provider.get(product_id) if isinstance(provider, MockProductProvider) else None
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return Response(
        content=product_svg(product),
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=86400"},
    )
