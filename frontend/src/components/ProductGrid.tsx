"use client";

import { logEvent, Product } from "@/lib/api";

function ProductCard({ product, boardId }: { product: Product; boardId: string }) {
  return (
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
      className="group flex flex-col overflow-hidden rounded-2xl border border-line bg-card transition-shadow hover:shadow-md"
    >
      <div className="relative aspect-[3/4] overflow-hidden bg-background">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={product.image_url}
          alt={product.title}
          loading="lazy"
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
        />
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
        <p className="mt-auto pt-3 text-xs font-medium underline underline-offset-2 opacity-0 transition-opacity group-hover:opacity-100">
          Shop at {product.retailer} ↗
        </p>
      </div>
    </a>
  );
}

export default function ProductGrid({
  products,
  boardId,
}: {
  products: Product[];
  boardId: string;
}) {
  if (products.length === 0) {
    return (
      <p className="mt-12 text-center text-muted">
        No matches found for this board — try a different set of images.
      </p>
    );
  }
  return (
    <div className="mt-12">
      <h2 className="font-display text-2xl">Shop the vibe</h2>
      <p className="mt-1 text-sm text-muted">
        {products.length} pieces matched to your board
      </p>
      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} boardId={boardId} />
        ))}
      </div>
    </div>
  );
}
