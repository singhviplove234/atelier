# Growth loop — read what the live site is actually doing, propose the next fix

Standing requirement: Phase 3. The factory gives every site a measurement foundation (GA4 + Search Console, `seo-ai-visibility.md` F) and monitoring (`monitoring.md`); the growth loop **consumes** that data and proposes the next improvement, so a live product keeps getting better instead of sitting still. Run by `/pf-grow`. **Recommend-only** — it proposes; The user picks what to action, and each chosen item goes through the normal build/harden flow and gates.

## What it reads (free sources already set up)
- **Google Search Console** — queries you rank for, impressions vs clicks, pages with impressions but low CTR, average position, coverage/indexing issues.
- **Google Analytics 4** — traffic, top and underperforming pages, where visitors drop off, conversions/key events (form submits, calls).
- **Microsoft Clarity** (if set up) — heatmaps / session replay for where people get stuck.
- **The site + its contracts** — current titles/meta, content, Core Web Vitals, llms.txt.

## What it proposes (prioritized, with the signal and the expected gain)
A short ranked list, each item with the data behind it and the fix:
- **SEO:** pages ranking on page 2 a better title / answer-first intro / FAQ could push up; high-impression low-CTR pages needing a better title/description; missing pages for queries people already search; internal links to add; schema gaps.
- **Content:** the next page/post to write (a real query with demand and no good page yet); refreshing stale content (`dateModified`); the location/service pages a local site is missing.
- **Conversion / UX:** a page with traffic but no conversions; a drop-off point from Clarity; a slow page hurting both ranking and conversion.
- **AI visibility:** where the AI engines are not citing the site (crawlable? answer-first? llms.txt current?).

## How it runs
`/pf-grow <slug>` reads the sources (via their free APIs / the connectors; guide any auth the `/pf-setup` way), produces the ranked list as a living doc (or rows on the project dashboard), and stops — **nothing is changed**. The user picks items; each chosen item becomes a normal change (a `/pf-build` fix or a `/pf-harden` pass), so every growth change still goes through the contracts and gates. Free-first: the data sources are free; **no paid SEO tool is required** — paid only on an explicit ask. Can be scheduled (like maintenance) to post a monthly "here's what to do next" — proposes only, never acts.
