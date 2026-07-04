"use client";

import { CartGroup } from "@/lib/cart";

export default function CartDrawer({
  open,
  onClose,
  groups,
  total,
  onRemove,
  onClear,
}: {
  open: boolean;
  onClose: () => void;
  groups: CartGroup[];
  total: number;
  onRemove: (id: string) => void;
  onClear: () => void;
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <button
        aria-label="Close cart"
        onClick={onClose}
        className="absolute inset-0 bg-black/30"
      />
      <div className="relative flex h-full w-full max-w-md flex-col bg-background p-6 shadow-xl animate-fade-up">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-2xl">Your Vibe Cart</h2>
          <button
            onClick={onClose}
            aria-label="Close"
            className="rounded-full border border-line px-3 py-1 text-sm hover:border-accent/50"
          >
            ✕
          </button>
        </div>

        {groups.length === 0 ? (
          <p className="mt-10 text-center text-sm text-muted">
            Nothing here yet — add pieces you like from the results grid.
          </p>
        ) : (
          <div className="mt-6 flex-1 space-y-6 overflow-y-auto">
            {groups.map((group) => (
              <div key={group.retailer}>
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold">{group.retailer}</h3>
                  <span className="text-sm text-muted">${group.subtotal.toFixed(0)}</span>
                </div>
                <ul className="mt-2 space-y-2">
                  {group.items.map((item) => (
                    <li
                      key={item.id}
                      className="flex items-center gap-3 rounded-xl border border-line bg-card p-2"
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={item.image_url}
                        alt={item.title}
                        className="h-14 w-14 rounded-lg object-cover"
                      />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-xs font-medium">{item.title}</p>
                        <p className="text-xs text-muted">${item.price.toFixed(0)}</p>
                      </div>
                      <button
                        onClick={() => onRemove(item.id)}
                        aria-label={`Remove ${item.title}`}
                        className="shrink-0 text-xs text-muted underline underline-offset-2 hover:text-foreground"
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
                <a
                  href={group.items[0]?.buy_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 inline-block rounded-full border border-line px-4 py-2 text-xs font-medium hover:border-accent/50"
                >
                  Check out at {group.retailer} ↗
                </a>
              </div>
            ))}
          </div>
        )}

        {groups.length > 0 && (
          <div className="mt-6 border-t border-line pt-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted">Combined total</span>
              <span className="font-semibold">${total.toFixed(0)}</span>
            </div>
            <p className="mt-1 text-xs text-muted">
              Check out each retailer separately — Muse doesn&apos;t process payments.
            </p>
            <button
              onClick={onClear}
              className="mt-4 w-full rounded-full border border-line py-2 text-xs text-muted hover:border-accent/50"
            >
              Clear cart
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
