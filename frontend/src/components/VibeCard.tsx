import { VibeSummary } from "@/lib/api";

export default function VibeCard({ vibe }: { vibe: VibeSummary }) {
  return (
    <div className="mx-auto max-w-2xl rounded-2xl border border-line bg-card p-8 text-center shadow-sm">
      <p className="text-xs uppercase tracking-[0.2em] text-muted">Your vibe</p>

      <div className="mt-4 flex flex-wrap justify-center gap-2">
        {vibe.tags.map((tag) => (
          <span
            key={tag}
            className="rounded-full border border-line bg-background px-4 py-1.5 text-sm"
          >
            {tag}
          </span>
        ))}
      </div>

      <div className="mx-auto mt-5 flex h-8 w-full max-w-xs overflow-hidden rounded-full border border-line">
        {vibe.palette.map((hex, i) => (
          <div
            key={`${hex}-${i}`}
            className="flex-1"
            style={{ backgroundColor: hex }}
            title={hex}
          />
        ))}
      </div>

      <p className="mt-5 font-display text-lg leading-relaxed">
        “{vibe.sentence}”
      </p>

      {vibe.stubbed && (
        <p className="mt-3 text-xs text-muted">
          (Preview summary — AI vibe analysis pending)
        </p>
      )}
    </div>
  );
}
