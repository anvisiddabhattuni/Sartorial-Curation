# Muse — Build Log & Progress Notes

Kept against the [Muse PRD v1.0](../Muse_PRD.pdf). Written from the PM seat (Anvi); engineering execution by Claude. Updated as work happens, not reconstructed after the fact — dates are actual commit/session dates.

**Live:** frontend on Vercel, API on Railway + Supabase (Postgres/pgvector). Both deployed as of Jul 5.

## Status vs. the roadmap (PRD §8)

| Phase | Plan | Status |
|---|---|---|
| 0 — Foundations | Repo, Next.js + FastAPI scaffold, deploy pipeline, event logging skeleton, landing/upload screen | **Done** (Jul 3) |
| 1 — Core pipeline / MVP | Upload → FashionCLIP embeddings → board profile → "Your Vibe" → ranked results | **Done** (Jul 3). Milestone hit: upload a board, get a shoppable page, demo-able end to end. |
| 2 — Cart & refinement | Vibe Cart, filters, why-matched chips, "more like this," Pinterest connect | **Partial.** Vibe Cart, price filter, why-matched chips, and text-feedback refine are live. Category/retailer filters and Pinterest connect are not built yet — see Scope notes. |
| 3 — Polish, test, present | Empty/error states, responsive pass, deploy, 10–15 person user test, case study | **In progress.** Deployed Jul 5–6; a live-traffic bug found and fixed Jul 7 (below). Error states exist for bad uploads. User testing and the case study haven't started. |
| 4 — Stretch | Affiliate monetization, accounts, Stripe demo, outfit builder | Not started. |

## Build log

**Jul 3 — MVP pipeline, end to end.** Next.js + FastAPI scaffold, providers built behind swappable interfaces from day one (FashionCLIP embeddings with a stub fallback, Gemini vibe summarizer with a stub fallback, mock product catalog with a SerpAPI real-provider path, pgvector with an in-memory fallback). Smoke-tested end to end same day.

**Jul 3 — Real-provider bugs, once live keys were in.** Wiring in actual API keys surfaced three issues the stub path had hidden: a local SSL cert bundle problem on outbound HTTPS calls, product results silently going stale because vector-store re-indexing was gated on a count match instead of always re-running, and the default Gemini model having zero free-tier quota. All three fixed and verified same day. Lesson: the fallback-first architecture is good for uptime, but it also means real-provider bugs stay invisible until you actually flip the key on — worth testing with live keys earlier next time, not just before a deploy.

**Jul 3 — Vibe Cart, refine, price filter.** Shipped the Vibe Cart (localStorage-backed — no accounts exist yet — grouped by retailer with subtotals and per-retailer checkout links), a price-range filter, and text-feedback refine ("no black, more skirts") that nudges the board profile without re-uploading images. Also caught and fixed a real bug this surfaced: the product vector-store namespace was shared across every board in a session, so an older board's leftover vectors could outrank a new board's own results and get silently dropped — occasionally zeroing out a board's results entirely. Fixed by namespacing per board.

**Jul 3 — Pinterest access paperwork.** Drafted the privacy policy and Pinterest Standard-access application write-up — both prerequisites Pinterest's developer review requires before board-connect (FR-1.1) can ship. The actual registration and review submission is a manual step gated on my own Pinterest developer login, so it's still open.

**Jul 5 — Deploy prep.** Railway config (Procfile, health check, restart policy), CORS widened to accept a comma-separated origin list so local dev and the deployed Vercel frontend can both be allowed at once, CPU-only torch wheels pinned for the deploy target.

**Jul 5 — PgBouncer prepared-statement bug.** Supabase's pooler runs in transaction-pooling mode, which doesn't reliably support psycopg3's automatic server-side prepared statements — a statement prepared on one pooled connection can get invoked against a different one and fail. Disabled server-side prepare; verified against the live Supabase instance.

**Jul 6 — Rate limiting and budget caps.** Ahead of sharing the deployed link, added per-IP rate limiting (stricter on the two endpoints that cost real money — analyze and refine) and a shared daily budget per provider (Gemini, SerpAPI). Once a budget's exhausted, the pipeline serves the stub summary / mock catalog instead of erroring — same fallback-first pattern as everywhere else. Verified by exhausting a budget of 1 locally.

**Jul 7 — Production bug: Vibe Cart never loaded on the deployed link.** Reported symptom: uploading photos on the Vercel domain didn't get to the point of populating the cart. Diagnosis ruled out the two obvious deploy-config suspects first — frontend was correctly pointed at the Railway API, and CORS was configured correctly for the exact Vercel origin — then reproduced it directly in a real browser against the live deployment. The upload step (`POST /boards`) was consistently fast; the analyze step hung indefinitely on 3 of 4 attempts, while `/health` stayed fast and responsive the whole time, which ruled out a server-wide freeze and pointed at one specific call. Root cause: the Gemini API client had no request timeout, so an occasional stall on Gemini's end hung the whole analyze call forever — the existing try/except around the Gemini call only catches raised exceptions, not a call that never returns, so the stub-summary fallback (built for exactly this) never got a chance to run. Fix: added an explicit 20s timeout, matching the timeout SerpAPI's client already had. **Deployed:** pushed Jul 7. (Note while retesting: the fix itself burned through the per-IP analyze rate limit added Jul 6 — a reminder that automated verification against a live deploy competes with real traffic for the same budget.)

## Scope decisions vs. PRD

- **Refine ships as text-feedback, not per-item "more like this."** The PRD lists both (refine is implicit in the flow, "more like this" is FR-4.6, P2). Text-feedback refine covers the higher-value case and shipped Jul 3; the P2 per-item anchor hasn't been started.
- **Filters: price only.** Category and retailer filters (FR-4.2, P1) aren't built yet — price was the one that mattered most for the "student budget" persona and shipped first.
- **Pinterest connect (FR-1.1, P0) isn't live.** Paperwork prerequisites are done (Jul 3); the developer registration and review submission are still open, manual, gated on my own Pinterest login. Upload (FR-1.2) is the only ingestion path right now — which matches the PRD's own call to treat upload as the reliable path and Pinterest connect as an enhancement layered on top, so this isn't off-plan, just not started.
- **Dedup (FR-3.5) and affiliate link wrapping (FR-4.7)** — both P2, correctly behind everything else.
- **Unified checkout** — out of scope per PRD §4.2, as planned. Vibe Cart shipped instead.

## Metrics instrumentation (PRD §2.2)

Live: `board_submitted`, `results_rendered`, `card_clicked`, `cart_add`.

**Gap: `match_rated` isn't wired up.** There's no "does this match your board? 1–5" UI yet. This is one of only two rating-based success metrics in the PRD (the other, click-through rate, is covered by `card_clicked`), and it's cheap to add — should land before any user test, or that test can't produce the number the PRD asks for.

## Open risks

- **Single global Postgres connection, no pooling library.** Works today, but it's a concurrency ceiling worth knowing about before sending real simultaneous traffic at it (e.g. a user test).
- **Provider timeouts:** Gemini now has one (Jul 7 fix); SerpAPI already did. Neither has been chaos-tested beyond the one real incident — the degrade path (serve stub/mock content) is the intended behavior, not a bug, but it's only been proven under one failure mode so far.
- **Pinterest Standard access:** not yet submitted for review — board-connect can't ship until that clears, and Pinterest's review timelines aren't in my control.
- **User testing and case study haven't started.** These are the two Phase 3 deliverables that actually turn this from a working app into a portfolio artifact (PRD §9) — everything above is groundwork for them.

## Next up

1. Wire `match_rated` (simple 1–5 on the "Your Vibe" card) — needed before any user test.
2. Ship the Jul 7 Gemini-timeout fix to production.
3. Category/retailer filters (P1, still open).
4. Recruit and run the 10–15 person test; pull real funnel numbers from the events already live.
5. Submit Pinterest Standard access for review.
6. Draft the case study once real funnel data exists.
