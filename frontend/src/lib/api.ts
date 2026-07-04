const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface VibeSummary {
  tags: string[];
  palette: string[]; // hex colors
  sentence: string;
  stubbed?: boolean;
}

export interface Product {
  id: string;
  title: string;
  price: number;
  currency: string;
  retailer: string;
  image_url: string;
  buy_link: string;
  details: string;
  category: string;
  similarity: number;
  why_matched?: string[];
}

export interface AnalyzeResponse {
  board_id: string;
  vibe: VibeSummary;
  products: Product[];
}

export async function submitBoard(files: File[]): Promise<{ board_id: string }> {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  const res = await fetch(`${API_URL}/boards`, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Upload failed (${res.status})`);
  }
  return res.json();
}

export async function analyzeBoard(boardId: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_URL}/boards/${boardId}/analyze`, {
    method: "POST",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Analysis failed (${res.status})`);
  }
  return res.json();
}

export function logEvent(name: string, properties: Record<string, unknown> = {}) {
  // Fire-and-forget; instrumentation must never break the flow.
  fetch(`${API_URL}/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, properties }),
  }).catch(() => {});
}
