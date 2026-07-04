"use client";

import { useState } from "react";
import UploadDropzone from "@/components/UploadDropzone";
import VibeCard from "@/components/VibeCard";
import ProductGrid from "@/components/ProductGrid";
import {
  analyzeBoard,
  AnalyzeResponse,
  logEvent,
  submitBoard,
} from "@/lib/api";

type Phase = "upload" | "analyzing" | "results" | "error";

const LOADING_LINES = [
  "Reading your vibe…",
  "Studying silhouettes and textures…",
  "Pulling the palette from your board…",
  "Curating pieces that match…",
];

export default function Home() {
  const [phase, setPhase] = useState<Phase>("upload");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [lineIdx, setLineIdx] = useState(0);

  async function handleSubmit(files: File[]) {
    setSubmitting(true);
    setErrorMsg("");
    try {
      const { board_id } = await submitBoard(files);
      setPhase("analyzing");
      const ticker = setInterval(
        () => setLineIdx((i) => (i + 1) % LOADING_LINES.length),
        2500
      );
      try {
        const analysis = await analyzeBoard(board_id);
        setResult(analysis);
        setPhase("results");
        logEvent("results_rendered", {
          board_id,
          product_count: analysis.products.length,
        });
      } finally {
        clearInterval(ticker);
      }
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Something went wrong.");
      setPhase("error");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex-1 px-6 py-12 sm:py-16">
      <header className="mx-auto mb-12 max-w-3xl text-center">
        <button
          onClick={() => {
            setPhase("upload");
            setResult(null);
          }}
          className="font-display text-2xl tracking-tight"
        >
          Muse
        </button>
      </header>

      {phase === "upload" && (
        <section className="animate-fade-up">
          <div className="mx-auto mb-10 max-w-2xl text-center">
            <h1 className="font-display text-4xl leading-tight sm:text-5xl">
              Turn inspiration into a wardrobe.
            </h1>
            <p className="mt-4 text-lg text-muted">
              Upload your fashion inspiration. Muse reads the vibe of the whole
              board and finds real clothes to match.
            </p>
          </div>
          <UploadDropzone onSubmit={handleSubmit} submitting={submitting} />
        </section>
      )}

      {phase === "analyzing" && (
        <section className="mx-auto max-w-2xl text-center animate-fade-up">
          <div className="mx-auto mb-8 h-16 w-16 animate-spin rounded-full border-2 border-line border-t-accent" />
          <p className="font-display text-2xl">{LOADING_LINES[lineIdx]}</p>
          <p className="mt-3 text-sm text-muted">
            Embedding every image, synthesizing your style profile, and matching
            products — usually under 30 seconds.
          </p>
          <div className="mx-auto mt-10 grid max-w-md grid-cols-3 gap-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="shimmer aspect-[3/4] rounded-xl" />
            ))}
          </div>
        </section>
      )}

      {phase === "results" && result && (
        <section className="mx-auto max-w-6xl animate-fade-up">
          <VibeCard vibe={result.vibe} />
          <ProductGrid products={result.products} boardId={result.board_id} />
          <div className="mt-12 text-center">
            <button
              onClick={() => {
                setPhase("upload");
                setResult(null);
              }}
              className="rounded-full border border-line bg-card px-6 py-3 text-sm hover:border-accent/50"
            >
              Start over with a new board
            </button>
          </div>
        </section>
      )}

      {phase === "error" && (
        <section className="mx-auto max-w-xl text-center animate-fade-up">
          <p className="font-display text-2xl">That didn&apos;t work.</p>
          <p className="mt-3 text-muted">{errorMsg}</p>
          <button
            onClick={() => setPhase("upload")}
            className="mt-8 rounded-full bg-foreground px-8 py-3 text-background hover:opacity-85"
          >
            Try again
          </button>
        </section>
      )}
    </main>
  );
}
