"use client";

import { useCallback, useEffect, useState } from "react";
import { Product } from "./api";

const STORAGE_KEY = "museCart";

export interface CartGroup {
  retailer: string;
  items: Product[];
  subtotal: number;
}

export function useCart() {
  const [items, setItems] = useState<Product[]>([]);
  const [loaded, setLoaded] = useState(false);

  // Load once on mount — reading localStorage during the initial render would
  // mismatch the server-rendered (window-less) markup.
  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) setItems(JSON.parse(raw));
    } catch {
      // corrupt/blocked storage — start with an empty cart rather than crash
    }
    setLoaded(true);
  }, []);

  useEffect(() => {
    if (!loaded) return;
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }, [items, loaded]);

  const has = useCallback((id: string) => items.some((p) => p.id === id), [items]);

  const add = useCallback((product: Product) => {
    setItems((prev) => (prev.some((p) => p.id === product.id) ? prev : [...prev, product]));
  }, []);

  const remove = useCallback((id: string) => {
    setItems((prev) => prev.filter((p) => p.id !== id));
  }, []);

  const toggle = useCallback((product: Product) => {
    setItems((prev) =>
      prev.some((p) => p.id === product.id)
        ? prev.filter((p) => p.id !== product.id)
        : [...prev, product]
    );
  }, []);

  const clear = useCallback(() => setItems([]), []);

  const groups: CartGroup[] = Object.values(
    items.reduce<Record<string, CartGroup>>((acc, item) => {
      const g = acc[item.retailer] ?? { retailer: item.retailer, items: [], subtotal: 0 };
      g.items.push(item);
      g.subtotal += item.price;
      acc[item.retailer] = g;
      return acc;
    }, {})
  ).sort((a, b) => a.retailer.localeCompare(b.retailer));

  const total = items.reduce((sum, p) => sum + p.price, 0);

  return { items, groups, total, count: items.length, has, add, remove, toggle, clear };
}
