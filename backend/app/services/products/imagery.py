"""Generates clean editorial SVG product imagery for the mock catalog:
a stylized garment silhouette in the product's color on a tinted background.
Keeps the demo fully self-contained — no external image CDN to break."""

from .base import Product

_SILHOUETTES = {
    "tops": (
        '<path d="M240,175 Q300,225 360,175 L425,200 L485,265 L440,335 '
        'L392,295 L392,600 Q300,625 208,600 L208,295 L160,335 L115,265 '
        'L175,200 Z" fill="{c}"/>'
    ),
    "bottoms": (
        '<path d="M205,170 L395,170 L418,630 L322,630 L300,330 L278,630 '
        'L182,630 Z" fill="{c}"/>'
        '<rect x="205" y="170" width="190" height="26" fill="{c}" '
        'stroke="{bg}" stroke-width="3"/>'
    ),
    "outerwear": (
        '<path d="M238,160 Q300,205 362,160 L430,185 L490,255 L442,328 '
        'L396,288 L396,665 Q300,690 204,665 L204,288 L158,328 L110,255 '
        'L170,185 Z" fill="{c}"/>'
        '<line x1="300" y1="205" x2="300" y2="672" stroke="{bg}" stroke-width="5"/>'
    ),
    "dresses": (
        '<path d="M245,160 L355,160 L372,300 L455,655 L145,655 L228,300 Z" fill="{c}"/>'
        '<path d="M245,160 L232,120 M355,160 L368,120" stroke="{c}" '
        'stroke-width="9" fill="none" stroke-linecap="round"/>'
    ),
    "shoes": (
        '<path d="M185,290 L305,290 L318,500 Q400,520 452,552 Q490,572 '
        '478,608 L172,608 Z" fill="{c}"/>'
        '<path d="M172,608 L478,608 L478,630 L172,630 Z" fill="{c}" opacity="0.55"/>'
    ),
    "accessories": (
        '<path d="M195,360 L405,360 L438,625 L162,625 Z" fill="{c}"/>'
        '<path d="M245,360 Q300,235 355,360" fill="none" stroke="{c}" stroke-width="12"/>'
    ),
}


def _tint(hex_color: str, factor: float = 0.86) -> str:
    """Mix a color toward warm white for the background."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    base = (250, 247, 242)
    mixed = tuple(int(c * (1 - factor) + w * factor) for c, w in zip((r, g, b), base))
    return "#%02x%02x%02x" % mixed


def product_svg(product: Product) -> str:
    color = product.color or "#c9bda9"
    bg = _tint(color)
    silhouette = _SILHOUETTES.get(product.category, _SILHOUETTES["accessories"])
    shape = silhouette.format(c=color, bg=bg)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 800">'
        f'<rect width="600" height="800" fill="{bg}"/>'
        f"{shape}"
        f'<text x="300" y="742" text-anchor="middle" font-family="Georgia, serif" '
        f'font-size="24" fill="{color}" opacity="0.85">{product.retailer}</text>'
        "</svg>"
    )
