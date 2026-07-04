"""MockProductProvider — a curated, realistic fake catalog spanning multiple
aesthetics, categories, and price points. Product images are served by the
backend itself (/products/{id}/image.svg) so the demo never depends on an
external CDN. Buy links point at real retailer search pages so click-through
feels genuine."""

from typing import Any
from urllib.parse import quote_plus

from .base import Product, ProductSearchProvider

_RETAILER_SEARCH = {
    "Aritzia": "https://www.aritzia.com/us/en/search?q={q}",
    "Zara": "https://www.zara.com/us/en/search?searchTerm={q}",
    "COS": "https://www.cos.com/en_usd/search.html?q={q}",
    "Everlane": "https://www.everlane.com/search?q={q}",
    "Uniqlo": "https://www.uniqlo.com/us/en/search/?q={q}",
    "Madewell": "https://www.madewell.com/search?q={q}",
    "Reformation": "https://www.thereformation.com/search?q={q}",
    "Urban Outfitters": "https://www.urbanoutfitters.com/search?q={q}",
    "Free People": "https://www.freepeople.com/search?q={q}",
    "Mango": "https://shop.mango.com/us/search?q={q}",
    "Massimo Dutti": "https://www.massimodutti.com/us/search?q={q}",
    "Levi's": "https://www.levi.com/US/en_US/search/{q}",
}

# (title, price, retailer, category, color, details)
_CATALOG: list[tuple[str, float, str, str, str, str]] = [
    # ---- Neutral / minimal / clean tailoring ----
    ("Oversized Cream Cable Knit Sweater", 88, "Aritzia", "tops", "#efe6d8", "Chunky cable knit in ivory wool blend, drop shoulders, relaxed fit"),
    ("Relaxed Linen Blend Blazer", 129, "Zara", "outerwear", "#d8cbb6", "Unstructured single-breasted blazer in oatmeal linen, patch pockets"),
    ("Wide-Leg Pleated Trousers", 98, "COS", "bottoms", "#c9bda9", "High-rise pleated trousers in sand twill, fluid wide leg"),
    ("Boxy White Poplin Shirt", 65, "Everlane", "tops", "#f7f5f0", "Crisp organic cotton poplin, boxy cut, mother-of-pearl buttons"),
    ("Ribbed Tank Bodysuit", 38, "Aritzia", "tops", "#e8e0d4", "Double-lined ribbed jersey bodysuit in bone, square neckline"),
    ("Straight-Leg Ecru Jeans", 78, "Levi's", "bottoms", "#ede5d3", "Rigid cotton straight-leg jean in undyed ecru denim"),
    ("Longline Wool Coat", 220, "COS", "outerwear", "#cfc4b2", "Minimal longline coat in camel wool, hidden placket, side slits"),
    ("Leather Ballet Flats", 95, "Everlane", "shoes", "#d9cfc0", "Buttery leather flats in stone, almond toe, stitched sole"),
    ("Structured Canvas Tote", 68, "Madewell", "accessories", "#e2d8c5", "Heavy canvas tote in natural with leather handles, interior pocket"),
    ("Gold Chunky Hoop Earrings", 28, "Mango", "accessories", "#d4af6a", "14k gold-plated thick hoops, lightweight, tarnish resistant"),
    # ---- Coastal / airy ----
    ("Linen Midi Slip Dress", 118, "Reformation", "dresses", "#e9e2d0", "Bias-cut linen slip in shell, adjustable straps, side slit"),
    ("Striped Boatneck Tee", 45, "Everlane", "tops", "#dfe4e6", "Breton stripe boatneck in cream and navy, heavyweight cotton"),
    ("Drawstring Linen Trousers", 69, "Uniqlo", "bottoms", "#e6dfcd", "Breathable linen-blend pull-on pant in sand, tapered leg"),
    ("Crochet Knit Beach Cardigan", 78, "Free People", "outerwear", "#f0e9d6", "Open-weave crochet cardigan in shell, relaxed longline fit"),
    ("Woven Raffia Market Bag", 58, "Madewell", "accessories", "#d9c48f", "Handwoven raffia carryall with rolled handles"),
    ("Platform Espadrille Sandals", 85, "Free People", "shoes", "#cbb894", "Jute-wrapped platform espadrille with canvas straps in natural"),
    ("Seersucker Camp Shirt", 59, "Mango", "tops", "#dce8ea", "Relaxed camp-collar shirt in pale blue seersucker"),
    ("White Denim Shorts", 55, "Levi's", "bottoms", "#f4f2ec", "High-rise 501 short in white rigid denim, raw hem"),
    # ---- Soft grunge / moody ----
    ("Washed Black Oversized Hoodie", 64, "Urban Outfitters", "tops", "#3a3a3c", "Garment-dyed heavyweight fleece hoodie in washed black"),
    ("Distressed Straight Jeans", 89, "Levi's", "bottoms", "#4d5560", "Mid-rise straight jean in faded black with destructed knees"),
    ("Faux Leather Moto Jacket", 128, "Urban Outfitters", "outerwear", "#2e2b2d", "Cropped vegan leather moto with asymmetric zip, quilted panels"),
    ("Plaid Flannel Overshirt", 69, "Uniqlo", "outerwear", "#5a4a4f", "Brushed flannel shacket in charcoal plaid, chest pockets"),
    ("Chunky Platform Boots", 140, "Urban Outfitters", "shoes", "#232122", "Lug-sole platform combat boot in black leather, side zip"),
    ("Slouchy Graphic Band Tee", 42, "Urban Outfitters", "tops", "#454347", "Washed cotton oversized tee with faded vintage band print"),
    ("Fishnet Layering Top", 29, "Free People", "tops", "#3d3b40", "Sheer open-knit long sleeve in slate, layers under slips and tees"),
    ("Silver Chain Necklace", 35, "Mango", "accessories", "#b8bcc2", "Chunky curb-chain necklace in polished silver tone"),
    # ---- Classic / workwear / preppy ----
    ("Navy Double-Breasted Blazer", 189, "Massimo Dutti", "outerwear", "#22304a", "Tailored double-breasted blazer in navy wool, gold-tone buttons"),
    ("Pinstripe Wide Trousers", 110, "Massimo Dutti", "bottoms", "#39415a", "Fluid wide-leg trouser in navy pinstripe suiting"),
    ("Cashmere Crewneck Sweater", 130, "Uniqlo", "tops", "#95a3b8", "100% cashmere crew in dusty blue, fully fashioned knit"),
    ("Oxford Button-Down Shirt", 72, "Everlane", "tops", "#cfd8e4", "Classic oxford in washed light blue, slightly relaxed fit"),
    ("Pleated Tennis Skirt", 55, "Uniqlo", "bottoms", "#e7e9ee", "A-line pleated mini in off-white ponte, hidden shorts lining"),
    ("Penny Loafers", 148, "Madewell", "shoes", "#5b3a26", "Polished leather penny loafer in chestnut, stacked heel"),
    ("Silk Twill Neck Scarf", 45, "Massimo Dutti", "accessories", "#b8c4d8", "Printed silk twill scarf in blue and cream geometric motif"),
    # ---- Romantic / soft feminine ----
    ("Ruched Floral Midi Dress", 148, "Reformation", "dresses", "#dcc5ce", "Ruched bodice midi in dusty rose ditsy floral, flutter sleeves"),
    ("Satin Bias Skirt", 88, "Aritzia", "bottoms", "#e3ccd6", "Liquid satin midi skirt in blush, bias cut, elastic waist"),
    ("Puff-Sleeve Cropped Cardigan", 58, "Mango", "tops", "#eadbe0", "Soft knit cardigan in rose with puffed shoulders, pearl buttons"),
    ("Lace-Trim Cami", 34, "Urban Outfitters", "tops", "#f0e3e7", "Satin cami in ballet pink with delicate lace neckline"),
    ("Strappy Kitten Heels", 98, "Mango", "shoes", "#d9bfc7", "Wrap-ankle kitten heel in blush suede, square toe"),
    ("Pearl Drop Earrings", 32, "Mango", "accessories", "#ece7e2", "Freshwater pearl drops on gold-filled hooks"),
    # ---- Streetwear / sporty ----
    ("Boxy Heavyweight Tee", 38, "Uniqlo", "tops", "#e3e1dc", "300gsm cotton tee in bone, boxy skater cut, dropped shoulder"),
    ("Cargo Parachute Pants", 79, "Urban Outfitters", "bottoms", "#8a8d82", "Ripstop parachute pant in sage with bungee hem and cargo pockets"),
    ("Oversized Varsity Jacket", 145, "Urban Outfitters", "outerwear", "#3b4a3e", "Wool-blend varsity in forest green with cream leather sleeves"),
    ("Retro Running Sneakers", 110, "Free People", "shoes", "#cdd2c6", "Suede and mesh runner in sage and cream, gum sole"),
    ("Nylon Crossbody Bag", 48, "Uniqlo", "accessories", "#6f7568", "Water-resistant nylon sling in olive, adjustable strap"),
    ("Baggy Carpenter Jeans", 98, "Levi's", "bottoms", "#7d8894", "Loose carpenter jean in medium stonewash, hammer loop"),
    # ---- Earthy / bohemian ----
    ("Suede Fringe Jacket", 198, "Free People", "outerwear", "#8a6647", "Soft suede trucker with western fringe in toffee"),
    ("Corduroy A-Line Skirt", 64, "Madewell", "bottoms", "#9c7a52", "Wide-wale cord mini in caramel, front button placket"),
    ("Embroidered Peasant Blouse", 78, "Free People", "tops", "#e8dcc4", "Airy cotton blouse in cream with tonal embroidery, tie neck"),
    ("Knit Maxi Dress", 128, "Mango", "dresses", "#a5825f", "Ribbed knit maxi in camel, fitted through body, side slit"),
    ("Western Ankle Boots", 168, "Madewell", "shoes", "#6e4f38", "Stacked-heel western boot in tan leather, subtle stitching"),
    ("Woven Leather Belt", 42, "Madewell", "accessories", "#7a5c40", "Hand-braided leather belt in saddle with brass buckle"),
    # ---- Colorful / statement ----
    ("Cherry Red Knit Vest", 49, "Zara", "tops", "#a8302e", "Cropped sweater vest in cherry, V-neck, cropped boxy fit"),
    ("Cobalt Satin Midi Skirt", 69, "Zara", "bottoms", "#2b4bb5", "High-shine satin midi in cobalt, fluid drape"),
    ("Butter Yellow Cropped Cardigan", 55, "Aritzia", "tops", "#e9d489", "Fine-gauge knit cardigan in butter, fitted, shell buttons"),
    ("Emerald Slip Dress", 138, "Reformation", "dresses", "#1f6b4a", "Silky slip in emerald with cowl neck and low back"),
    ("Lavender Wool Scarf", 45, "COS", "accessories", "#b9a8d1", "Brushed wool oversized scarf in soft lavender"),
    ("Tortoise Cat-Eye Sunglasses", 55, "Madewell", "accessories", "#8a5a32", "Acetate cat-eye frame in amber tortoise, UV400"),
    # ---- Extra staples to round out categories ----
    ("Black Slim Turtleneck", 45, "Uniqlo", "tops", "#1e1d1f", "Fitted merino turtleneck in black, breathable fine knit"),
    ("Charcoal Wool Wide Trousers", 118, "COS", "bottoms", "#4a4a4e", "Wide-leg wool trouser in charcoal, pressed crease"),
    ("Trench Coat", 178, "Mango", "outerwear", "#c7b299", "Classic double-breasted trench in khaki with storm flap and belt"),
    ("Denim Chore Jacket", 98, "Madewell", "outerwear", "#5d738c", "Workwear chore coat in indigo denim, three-pocket front"),
    ("White Leather Sneakers", 98, "Everlane", "shoes", "#f2f0ea", "Minimal court sneaker in white leather, cap toe"),
    ("Black Ankle Boots", 158, "Aritzia", "shoes", "#262425", "Sleek heeled ankle boot in black leather, pointed toe"),
    ("Slouchy Shoulder Bag", 88, "COS", "accessories", "#3f3c3a", "Soft leather shoulder bag in black, magnetic close"),
    ("Ribbed Beanie", 24, "Uniqlo", "accessories", "#6b6f75", "Merino-blend ribbed beanie in heather grey"),
    ("Midi Shirt Dress", 96, "Everlane", "dresses", "#d3ccba", "Belted cotton shirt dress in sage-tinted khaki, patch pockets"),
    ("Cropped Denim Jacket", 88, "Levi's", "outerwear", "#6d82a0", "Cropped trucker jacket in mid-wash rigid denim"),
    ("Silk Midi Slip Skirt", 92, "Aritzia", "bottoms", "#cfc7bc", "Bias-cut silk skirt in champagne, elasticated waist"),
    ("Halter Knit Top", 44, "Zara", "tops", "#b4a58e", "Sleeveless halter knit in taupe, open back, fine rib"),
]


def _buy_link(retailer: str, title: str) -> str:
    template = _RETAILER_SEARCH[retailer]
    return template.format(q=quote_plus(title))


def build_catalog(image_base_url: str) -> list[Product]:
    products = []
    for i, (title, price, retailer, category, color, details) in enumerate(_CATALOG):
        pid = f"mock-{i:03d}"
        products.append(
            Product(
                id=pid,
                title=title,
                price=float(price),
                retailer=retailer,
                image_url=f"{image_base_url}/products/{pid}/image.svg",
                buy_link=_buy_link(retailer, title),
                details=details,
                category=category,
                color=color,
            )
        )
    return products


class MockProductProvider(ProductSearchProvider):
    name = "mock"

    def __init__(self, image_base_url: str) -> None:
        self._catalog = build_catalog(image_base_url)

    def search(self, queries: list[str], filters: dict[str, Any] | None = None) -> list[Product]:
        # The mock returns the full catalog; ranking against the board profile
        # happens downstream in the vector store.
        return list(self._catalog)

    def get(self, product_id: str) -> Product | None:
        return next((p for p in self._catalog if p.id == product_id), None)
