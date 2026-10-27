# Performance budget — every Atelier site must be fast, whatever it weighs

Standing requirement: "regardless how heavy our website is it should load quickly and stay superfast without lagging." This file is the contract. The builder enforces it before a build may report `status: ok`; `/pf-harden` re-checks it on the **live** site and fixes regressions.

## Targets (measured on Lighthouse **mobile** preset, throttled, median of 3 runs)

| Metric | Budget | Why |
|---|---|---|
| Lighthouse Performance score | >= 90 | the single number the user will look at |
| LCP (largest content visible) | <= 2.5 s | "loads quickly" |
| INP (reaction to taps/clicks) | <= 200 ms | "without lagging" |
| CLS (layout jumping) | <= 0.1 | nothing moves under the finger |
| TTFB from the primary-audience region | <= 800 ms | server/CDN placement |
| First-load JavaScript per route | <= 200 KB gzipped | heavy pages must still start fast |
| Largest image on any screen | <= 200 KB, served as AVIF/WebP, correctly sized | images are 80% of "heavy" |
| Third-party scripts on first load | 0 unless the SPEC names them (analytics loads after interaction / idle) | each one costs 100-500 ms |

A heavy site is allowed to be heavy **in total**; it is not allowed to make the visitor wait for the heavy part. The rule is: show the screen now, load the rest lazily.

## How the builder meets it (do these by default, not when asked)

1. **Render ahead of time.** Every page that does not depend on the signed-in user is statically generated at build time (or ISR with `revalidate`). Dynamic data goes in a small client island, never blocks the page.
2. **Images.** Always `next/image` with explicit `width`/`height` (or `fill` + `sizes`), `priority` only on the LCP image, everything below the fold lazy. Source images are resized and converted at build (sharp) — never ship a 4 MB camera photo.
3. **Fonts.** `next/font` (self-hosted, `display: swap`, subset `latin`), at most 2 families, no Google Fonts `<link>`.
4. **JavaScript.** Server components by default; `"use client"` only on the leaf that needs state. Heavy widgets (maps, charts, editors, video players, carousels) via `next/dynamic` with `ssr: false` and a lightweight placeholder. No moment.js/lodash-whole/jQuery; check `npx @next/bundle-analyzer` when a route exceeds the JS budget.
5. **Video and 3D.** Poster image first, media loads on interaction or when in view; use the host's CDN or a storage bucket, never commit media to the repo.
6. **Caching headers.** Static assets immutable with long `max-age`; HTML/ISR pages `s-maxage` + `stale-while-revalidate`; API responses that are the same for everyone get `Cache-Control` too. This is the free caching layer — no Redis (see deploy-rule.md cost posture).
7. **Database.** Every query that a screen depends on has an index on its WHERE/JOIN/ORDER BY columns (migration file); serverless hosts connect through the pooler (Supabase port 6543). Lists are paginated (<= 50 rows per request).
8. **No layout shift.** Reserve space for images, ads, embeds and web fonts; skeletons instead of spinners that pop.
9. **Hosting placement.** the provider region nearest the primary audience (for Azure, pick the closest region); a global CDN serves static files everywhere.

## Scroll-motion weight budget (for motion-led / heavy brand sites)

Learned on a real motion-led build: on a scroll-animated site the thing that makes it feel laggy is **total weight, not the motion engine**. A site's scroll motion was re-tuned repeatedly with no effect; the lag only stopped once the page's bytes came down (one page went from ~19 MB to ~4 MB for a full scroll, ~3.6 MB to ~1.2 MB on first visit). So for any `brand`/motion-led page the builder holds a weight budget on top of the metrics above:

- **First visit ≤ ~2.5 MB** transferred (what paints before the reader scrolls).
- **Full scroll of the heaviest page ≤ ~9 MB** transferred, loaded progressively as scenes approach — never up front.
- **Text and nav visible ≤ ~1.5 s.**
- **No frame over ~50 ms during a continuous scroll** (no stutter under the finger).
- **No empty rectangle ever on screen** — a poster/placeholder is always painted while heavier media loads; hold the last frame rather than jump.

How the builder meets it: images/sheets re-encoded to AVIF (WebP fallback) and sized per device (never full-size on a phone); heavy scene assets fetched in scroll order within ~150 % of the viewport, a couple in flight; posters (~≤ 40 KB, with an inlined blurred placeholder) paint first; media decoded off the main thread and released when far off-screen (see the canvas/lazy-load rules in `design-standard.md`).

**Measure on a cold cache, a second browser (Edge/Safari) and a real phone before calling it done** — a warm-cache desktop hides every real complaint. This budget is a `brand`/motion-led add-on; a plain `product`/`editorial` page is bound by the metrics table above, not these payload ceilings.

## How it is checked

- Build time (`pf-build-from-spec` step 6): `npx lighthouse <preview-url> --preset=perf --form-factor=mobile --throttling-method=simulate --only-categories=performance --output=json --quiet --chrome-flags="--headless"` on the home page and every screen in the SPEC; `npm run build` output's "First Load JS" column against the 200 KB budget. Any miss → fix and re-measure, up to 3 attempts, then `status: failed` with `failures: perf budget: <metric> <value> on <route>`.
- Live (`/pf-harden` pass "perf"): the same Lighthouse run against `deploy.live_url`, plus TTFB from the Azure region via `curl -w "%{time_starttransfer}"`.

Results are always reported as a table: route | score | LCP | INP | CLS | JS KB — before and after.
