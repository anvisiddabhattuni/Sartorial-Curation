"use client";

import { useMemo, useState } from "react";
import { logEvent, Product } from "@/lib/api";

const PAGE_SIZE = 12;

function ProductCard({
  product,
  boardId,
  inCart,
  onToggleCart,
}: {
  product: Product;
  boardId: string;
  inCart: boolean;
  onToggleCart: (product: Product) => void;
}) {
  return (
    <div className="group flex flex-col overflow-hidden rounded-2xl border border-line bg-card transition-shadow hover:shadow-md">
      <div className="relative aspect-[3/4] overflow-hidden bg-background">
        <a
          href={product.buy_link}
          target="_blank"
          rel="noopener noreferrer"
          onClick={() =>
            logEvent("card_clicked", {
              board_id: boardId,
              product_id: product.id,
              retailer: product.retailer,
              price: product.price,
            })
          }
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={product.image_url}
            alt={product.title}
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
          />
        </a>
        <button
          onClick={() => onToggleCart(product)}
          aria-label={inCart ? `Remove ${product.title} from cart` : `Add ${product.title} to cart`}
          aria-pressed={inCart}
          className={`absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded-full text-sm shadow-sm transition-colors ${
            inCart
              ? "bg-accent text-white"
              : "bg-background/90 text-foreground hover:bg-background"
          }`}
        >
          {inCart ? "✓" : "+"}
        </button>
      </div>
      <div className="flex flex-1 flex-col p-4">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-sm font-medium leading-snug">{product.title}</h3>
          <p className="shrink-0 text-sm font-semibold">
            ${product.price.toFixed(0)}
          </p>
        </div>
        <p className="mt-1 text-xs text-muted capitalize">{product.retailer} · {product.category}</p>
        <p className="mt-2 line-clamp-2 text-xs text-muted">{product.details}</p>
        {product.why_matched && product.why_matched.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {product.why_matched.map((reason) => (
              <span
                key={reason}
                className="rounded-full bg-accent/10 px-2.5 py-0.5 text-[11px] text-accent"
              >
                {reason}
              </span>
            ))}
          </div>
        )}
        <a
          href={product.buy_link}
          target="_blank"
          rel="noopener noreferrer"
          onClick={() =>
            logEvent("card_clicked", {
              board_id: boardId,
              product_id: product.id,
              retailer: product.retailer,
              price: product.price,
            })
          }
          className="mt-auto pt-3 text-xs font-medium underline underline-offset-2"
        >
          Shop at {product.retailer} ↗
        </a>
      </div>
    </div>
  );
}

export default function ProductGrid({
  products,
  boardId,
  cartHas,
  onToggleCart,
}: {
  products: Product[];
  boardId: string;
  cartHas: (id: string) => boolean;
  onToggleCart: (product: Product) => void;
}) {
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  const priceBounds = useMemo(() => {
    if (products.length === 0) return { min: 0, max: 0 };
    const prices = products.map((p) => p.price);
    return { min: Math.floor(Math.min(...prices)), max: Math.ceil(Math.max(...prices)) };
  }, [products]);

  const filtered = useMemo(() => {
    const min = minPrice === "" ? -Infinity : Number(minPrice);
    const max = maxPrice === "" ? Infinity : Number(maxPrice);
    return products.filter((p) => p.price >= min && p.price <= max);
  }, [products, minPrice, maxPrice]);

  if (products.length === 0) {
    return (
      <p className="mt-12 text-center text-muted">
        No matches found for this board — try a different set of images.
      </p>
    );
  }

  const visible = filtered.slice(0, visibleCount);

  return (
    <div className="mt-12">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="font-display text-2xl">Shop the vibe</h2>
          <p className="mt-1 text-sm text-muted">
            {filtered.length} of {products.length} pieces
            {filtered.length !== products.length ? " match your price range" : " matched to your board"}
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <label className="text-muted" htmlFor="price-min">Price</label>
          <input
            id="price-min"
            type="number"
            inputMode="numeric"
            placeholder={`${priceBounds.min}`}
            value={minPrice}
            onChange={(e) => {
              setMinPrice(e.target.value);
              setVisibleCount(PAGE_SIZE);
            }}
            className="w-20 rounded-full border border-line bg-card px-3 py-1.5 outline-none focus:border-accent/50"
          />
          <span className="text-muted">–</span>
          <input
            type="number"
            inputMode="numeric"
            placeholder={`${priceBounds.max}`}
            value={maxPrice}
            onChange={(e) => {
              setMaxPrice(e.target.value);
              setVisibleCount(PAGE_SIZE);
            }}
            className="w-20 rounded-full border border-line bg-card px-3 py-1.5 outline-none focus:border-accent/50"
          />
          {(minPrice !== "" || maxPrice !== "") && (
            <button
              onClick={() => {
                setMinPrice("");
                setMaxPrice("");
              }}
              className="text-xs text-muted underline underline-offset-2 hover:text-foreground"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {filtered.length === 0 ? (
        <p className="mt-12 text-center text-muted">
          Nothing in that price range — try widening it.
        </p>
      ) : (
        <>
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {visible.map((p) => (
              <ProductCard
                key={p.id}
                product={p}
                boardId={boardId}
                inCart={cartHas(p.id)}
                onToggleCart={onToggleCart}
              />
            ))}
          </div>
          {visibleCount < filtered.length && (
            <div className="mt-8 text-center">
              <button
                onClick={() => setVisibleCount((c) => c + PAGE_SIZE)}
                className="rounded-full border border-line bg-card px-6 py-3 text-sm hover:border-accent/50"
              >
                Show more ({filtered.length - visibleCount} left)
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
