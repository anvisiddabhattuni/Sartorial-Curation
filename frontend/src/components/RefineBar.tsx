"use client";

import { useState } from "react";

export default function RefineBar({
  onRefine,
  refining,
}: {
  onRefine: (feedback: string) => void;
  refining: boolean;
}) {
  const [value, setValue] = useState("");

  function submit() {
    const feedback = value.trim();
    if (!feedback || refining) return;
    onRefine(feedback);
    setValue("");
  }

  return (
    <div className="mx-auto mt-6 max-w-2xl">
      <p className="text-center text-sm text-muted">
        Not quite right? Tell Muse more about what you want.
      </p>
      <div className="mt-3 flex gap-2">
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          disabled={refining}
          placeholder="e.g. no black, more skirts, dressier"
          maxLength={300}
          className="flex-1 rounded-full border border-line bg-card px-5 py-3 text-sm outline-none focus:border-accent/50 disabled:opacity-60"
        />
        <button
          onClick={submit}
          disabled={refining || !value.trim()}
          className="shrink-0 rounded-full bg-foreground px-6 py-3 text-sm font-medium text-background transition-opacity hover:opacity-85 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {refining ? "Updating…" : "Refresh results"}
        </button>
      </div>
    </div>
  );
}
