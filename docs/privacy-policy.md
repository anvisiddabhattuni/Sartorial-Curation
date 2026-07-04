# Privacy Policy: Muse

**Last updated:** July 3, 2026

Muse ("we," "our," "the app") turns fashion inspiration images into a shoppable page of real clothing. This policy explains what data Muse collects, why, and what rights you have over it.

Muse is an early-stage / portfolio project operated by a single developer. It is not yet a registered company, and this policy should be read with that in mind — see the legal-review notes at the end before treating it as a finished, enterprise-grade document.

## 1. What data we collect

| Data type | What it is | Why we collect it |
|---|---|---|
| Uploaded images | The 5–30 fashion inspiration images you upload | To generate your board's style embedding and "Your Vibe" summary |
| Pinterest board data (if you connect a board) | Pin images from a Pinterest board you explicitly authorize us to read | Same purpose as uploaded images — an alternate way to supply inspiration |
| Usage events | Anonymous product-analytics events: `board_submitted`, `results_rendered`, `card_clicked` (board ID, product ID, retailer, price, timestamps) | To measure whether the app is working (e.g. click-through rate) and to improve matching quality |
| Technical data | IP address, browser type, request logs (standard web server logs) | Security, abuse prevention, debugging |

We do **not** collect: names, email addresses, payment information, or any account credentials. Muse has no user accounts or persistent login in its current version.

## 2. How we use your data

- Uploaded images and Pinterest pins are sent to our AI providers (Google Gemini, and a self-hosted FashionCLIP model) solely to analyze the aesthetic of your board and generate product matches.
- Board profile data is used to query a product-search provider (SerpAPI / Google Shopping) so we can show you real, in-stock items.
- Usage events are aggregated to understand product performance (e.g., "do people click on matched products?"). They are not used to build an individual profile of you and are not sold.

## 3. Data retention and deletion

- **Uploaded images and Pinterest pin images** are held only for the duration of your session/analysis and are deleted afterward. We do not build a permanent library of your images.
- **Pinterest data specifically**: per Pinterest's developer platform policy, any data retrieved via the Pinterest API is never persisted beyond the active session and is not stored, cached, or reused after your board has been analyzed.
- **Usage events** are retained in aggregate (not tied to your identity) for product-improvement purposes. Since there are no accounts, there is no persistent per-person record to delete on request — but see Section 5 for how to reach us if you have concerns.

## 4. Third parties we share data with

Muse sends board images/pins to the following processors strictly to generate your results:

| Provider | What they receive | Purpose |
|---|---|---|
| Google (Gemini API) | Downscaled, low-detail sample images from your board | Generates the "Your Vibe" tags/palette/summary |
| SerpAPI (Google Shopping) | Text search queries derived from your board's style profile | Retrieves real, in-stock product listings |
| Pinterest (if you connect a board) | Your OAuth authorization | Lets us read pins from a board you explicitly choose |
| Hosting providers (Vercel, Render/Railway) | Standard request/server logs | Runs the application |

We do not sell your data to advertisers or data brokers.

## 5. Your rights

Because Muse does not require an account, most data is transient by design — it exists only for your session. If you have questions about data Muse may hold (e.g., server logs) or want something removed, contact: **[insert contact email — e.g. privacy@yourdomain.com]**.

Depending on where you live, you may have rights to access, correct, delete, or export personal data, or to object to processing (see GDPR/CCPA notes below).

## 6. Cookies

Muse does not currently use tracking or advertising cookies. Any cookies used are limited to what's strictly necessary for the app to function (e.g., session state), if any.

## 7. Children's privacy

Muse is not directed at children under 13 and we do not knowingly collect data from them.

## 8. International users

Muse is operated from the United States. If you use Muse from outside the US, your data (images, board data, usage events) will be processed on US-based (and Google/SerpAPI-operated) servers.

## 9. Changes to this policy

We'll update the "Last updated" date above whenever this policy changes materially, and post the revised policy at this same URL.

## 10. Contact

Questions about this policy: **[insert contact email]**

---

## Compliance checklist

| Regulation | Status | Notes |
|---|---|---|
| GDPR (EU users) | Partial | No account/login reduces exposure, but "legal basis for processing" (Section 3 above, implied consent via upload) should be reviewed by counsel before claiming full compliance. No EU representative currently designated. |
| CCPA (California users) | Partial | No sale of data, which is the main CCPA trigger — but a formal "Do Not Sell My Info" mechanism and a designated contact method should be added if the user base grows. |
| COPPA (children) | Basic disclaimer only | No age-gating mechanism currently exists; fine for a small demo, should be revisited before wider release. |
| Pinterest Developer Policy | Addressed | Explicit no-persistence commitment for Pinterest-sourced data included per platform requirement. |

## Clauses requiring legal review before this is treated as final

| Clause | Why | Priority |
|---|---|---|
| Section 5 (User rights) | GDPR/CCPA give specific, enforceable rights (access, deletion, portability) that a real lawyer should confirm are fully and correctly described | High |
| Contact email placeholder | Must be a real, monitored address before this policy is published or submitted anywhere | High (blocking) |
| Section 8 (International transfers) | GDPR has specific requirements for transferring EU data outside the EU (e.g. Standard Contractual Clauses) not addressed here | Medium |
| Overall entity/liability language | This policy assumes an individual operator; if Muse becomes a registered business, ownership/liability language should be added | Medium |

## Implementation checklist

- [ ] Replace `[insert contact email]` with a real, monitored address
- [ ] Publish this at a stable public URL (e.g. `/privacy` on the deployed frontend) — required before submitting Pinterest's Standard API access review
- [ ] Link to it from the app footer/landing page
- [ ] Have a lawyer (or a legal-review service) sign off before treating it as binding
- [ ] Revisit once user accounts, payments, or EU marketing are added — all materially change what this policy needs to say
