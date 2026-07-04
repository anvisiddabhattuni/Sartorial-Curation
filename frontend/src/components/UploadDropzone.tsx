"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const MIN_IMAGES = 5;
const MAX_IMAGES = 30;
const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];

interface Preview {
  file: File;
  url: string;
}

export default function UploadDropzone({
  onSubmit,
  submitting,
}: {
  onSubmit: (files: File[]) => void;
  submitting: boolean;
}) {
  const [previews, setPreviews] = useState<Preview[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const previewsRef = useRef(previews);

  useEffect(() => {
    previewsRef.current = previews;
  }, [previews]);

  useEffect(() => {
    return () => previewsRef.current.forEach((p) => URL.revokeObjectURL(p.url));
  }, []);

  const addFiles = useCallback(
    (incoming: FileList | File[]) => {
      setError(null);
      const files = Array.from(incoming);
      const rejected = files.filter((f) => !ALLOWED_TYPES.includes(f.type));
      const accepted = files.filter((f) => ALLOWED_TYPES.includes(f.type));
      setPreviews((prev) => {
        const room = MAX_IMAGES - prev.length;
        if (accepted.length > room) {
          setError(`That's over the ${MAX_IMAGES}-image limit — kept the first ${room}.`);
        }
        const next = accepted
          .slice(0, room)
          .map((file) => ({ file, url: URL.createObjectURL(file) }));
        return [...prev, ...next];
      });
      if (rejected.length > 0) {
        setError(
          `${rejected.length} file${rejected.length > 1 ? "s" : ""} skipped — only JPG, PNG, or WebP.`
        );
      }
    },
    []
  );

  const removeAt = (idx: number) => {
    setPreviews((prev) => {
      URL.revokeObjectURL(prev[idx].url);
      return prev.filter((_, i) => i !== idx);
    });
    setError(null);
  };

  const count = previews.length;
  const ready = count >= MIN_IMAGES && count <= MAX_IMAGES;

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div
        role="button"
        tabIndex={0}
        aria-label="Upload inspiration images"
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          addFiles(e.dataTransfer.files);
        }}
        className={`cursor-pointer rounded-2xl border-2 border-dashed px-8 py-12 text-center transition-colors ${
          dragging
            ? "border-accent bg-accent/5"
            : "border-line bg-card hover:border-accent/50"
        }`}
      >
        <p className="font-display text-xl">Drop your inspiration here</p>
        <p className="mt-2 text-sm text-muted">
          {MIN_IMAGES}–{MAX_IMAGES} images · JPG, PNG, or WebP
        </p>
        <input
          ref={inputRef}
          type="file"
          accept={ALLOWED_TYPES.join(",")}
          multiple
          hidden
          onChange={(e) => {
            if (e.target.files) addFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </div>

      {error && (
        <p className="mt-3 text-sm text-accent" role="alert">
          {error}
        </p>
      )}

      {count > 0 && (
        <div className="mt-6 animate-fade-up">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted">
              <span className={count < MIN_IMAGES ? "text-accent" : "text-foreground"}>
                {count}
              </span>
              {" / "}
              {MAX_IMAGES} images
              {count < MIN_IMAGES && ` — add ${MIN_IMAGES - count} more to continue`}
            </p>
            <button
              onClick={() => {
                previews.forEach((p) => URL.revokeObjectURL(p.url));
                setPreviews([]);
                setError(null);
              }}
              className="text-sm text-muted underline underline-offset-2 hover:text-foreground"
            >
              Clear all
            </button>
          </div>

          <div className="mt-3 grid grid-cols-4 gap-2 sm:grid-cols-6">
            {previews.map((p, i) => (
              <div key={p.url} className="group relative aspect-square">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={p.url}
                  alt={p.file.name}
                  className="h-full w-full rounded-lg object-cover"
                />
                <button
                  aria-label={`Remove ${p.file.name}`}
                  onClick={() => removeAt(i)}
                  className="absolute right-1 top-1 hidden h-6 w-6 items-center justify-center rounded-full bg-foreground/70 text-xs text-white group-hover:flex"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>

          <button
            disabled={!ready || submitting}
            onClick={() => onSubmit(previews.map((p) => p.file))}
            className="mt-8 w-full rounded-full bg-foreground px-8 py-4 font-medium text-background transition-opacity hover:opacity-85 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {submitting ? "Uploading…" : "Read my vibe"}
          </button>
        </div>
      )}
    </div>
  );
}
