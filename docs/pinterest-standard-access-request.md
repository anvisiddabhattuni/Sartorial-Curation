# Pinterest Standard Access — application draft

Use this as the copy source for the "use case" field on Pinterest's Standard access request form. Fill in the bracketed placeholders before submitting.

## Use case description

Muse is a web application that helps a Pinterest user turn a mood board they've already built into real, purchasable clothing. A user signs in with Pinterest, selects one of their own boards (e.g. a "capsule wardrobe" or aesthetic board), and grants Muse read-only access to that board's pins.

Muse reads the pin images from the selected board (via `GET /boards/{board_id}/pins`, scopes `boards:read` + `pins:read`), analyzes the aesthetic of the board as a whole using a self-hosted vision model, and returns a page of real, in-stock clothing items that match the board's overall style — with images, prices, retailers, and buy links. The user never leaves the flow they started: they picked the board, we show them clothes that match it.

We request only `boards:read` and `pins:read`. Muse does not create, modify, or delete any Pinterest content, and does not request write scopes. Per Pinterest's developer policy, pin data retrieved via the API is used only for the duration of the user's active session to generate results and is never persisted, cached, or reused afterward — image upload remains the primary, always-available ingestion path, and Pinterest connect is an enhancement for users who prefer not to re-upload images they've already curated on Pinterest.

## Data flow summary (for reviewers)

1. User clicks "Connect Pinterest" → redirected to Pinterest's OAuth consent screen.
2. User authorizes `boards:read`, `pins:read` and selects a board.
3. Muse calls the Pinterest API once to fetch that board's pin images for the current session only.
4. Images are analyzed (self-hosted embeddings + a vision-LLM summary) to produce a style profile.
5. The style profile is used to query a separate, non-Pinterest product-search API for real shoppable items.
6. Pinterest-sourced images are discarded at the end of the session. Nothing from Pinterest is stored, displayed publicly, or shared with third parties beyond this one-time analysis step.

## Video demo checklist (record before submitting)

- [ ] Show the actual "Connect Pinterest" button in the deployed app (not a mockup)
- [ ] Complete the real OAuth consent screen live
- [ ] Show a board being selected and pins being pulled into Muse
- [ ] Show the resulting "Your Vibe" summary + product grid generated from that board
- [ ] Do **not** show manually entering a Pinterest password or session cookie anywhere — Pinterest explicitly flags this as a rejection reason; the OAuth redirect must be visibly used

## Prerequisites before submitting

- [ ] App deployed at a public URL (Standard access reviewers need to see the live integration, not localhost)
- [ ] Privacy policy published at a public, working URL — see [privacy-policy.md](privacy-policy.md); link it from the app
- [ ] Trial access already approved and the OAuth flow tested end-to-end at least once
- [ ] `[Your name / business name]`, `[app name in Pinterest console]`, `[public app URL]`, `[privacy policy URL]` filled in on the actual form
