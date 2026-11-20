# Brand basics — a name that is free, a logo that works small, a kit everything else draws from

Added in 2.2.0. Optional (`options.md`): offered at plan time when the product has no name or logo yet, or the owner asks. Recorded in `factory.json.options.brand_kit` (`off` / `on`) and `factory.json.brand`. Run by `/pf-brand`, after the plan and **before** design, so the design system starts from it. It gives a product its identity; it does not run social channels, write content calendars or manage a brand over time.

## A. Name check — before a domain is bought or a logo drawn
Take three to five candidate names (the owner's, or proposed from the brief with the reason for each). For every candidate, look up and report:
1. **Same or similar names in the same kind of product** — a web search and, for an app, the app stores; for an extension or a package, that store or registry.
2. **The domain** — whether the `.com` and the fitting country or product endings appear free. The owner checks the price and buys; Claude never registers or pays.
3. **Trade marks** — a search of the public registers for the owner's country and main markets, reporting any identical or close mark in a related class, with the link.
4. **Handles** on the networks the owner will actually use.
5. **Meaning and sound** in each locale in `brief.locales` — nothing embarrassing, easy to say and spell after hearing it once.
Show one table: candidate · each check as clear / caution / taken · the one-line reason. Recommend one and say why. **State plainly, every time:** this is a screening that finds obvious conflicts; it is not a legal clearance, and a trade-mark professional decides whether a name is safe to register. Never file, register or buy anything.

## B. Logo
- A **wordmark first** (the name set in a licensed typeface, `design-standard.md`), with an optional simple mark. Three directions, numbered B1–B3, each shown on light and dark and at favicon size; the owner picks or mixes.
- It must pass four tests before it is offered: readable at 16 px; works in one colour; works on light and on dark; does not resemble a known mark found in step A.
- The master is a vector file drawn in the design tool. A generated picture is never the master logo, and no protected shape, character or other company's mark is used.

## C. The brand kit — `brand/` in the repo, described in `BRAND.md`
The one-page visual identity itself is put together as `design-craft.md` E describes; this section says what files go with it and where they are kept.
- Logo files: vector, PNG at the usual sizes, the favicon set, app icons for a mobile or desktop product.
- Colour and type: **the design system's tokens are the single source.** The kit names them and shows them; it does not define a second set. Contrast still meets `design-standard.md`.
- Voice in five lines: who we are talking to, three words we sound like, three we never sound like, and one example each of a headline, a button and an error message.
- Pictures: what kind, what never, with the licence rule from `design-standard.md`.
- The share-image template that `launch.md` B fills in.

## D. Where it goes
The chosen name and one-line description become the Brief's `Entity:` block (`seo-ai-visibility.md`); the tokens seed `/pf-design`; the logo and template feed the launch pack (`launch.md`) and the launch video brief (`launch-video.md`). Record `brand: { name, checked, logo, kit }` — the date of the name check, and the paths.

## Never
Present the name check as legal advice or as a guarantee. Register a domain, a handle or a trade mark. Copy another brand's name, mark, colours-and-layout together, or voice. Invent customer quotes, awards or numbers for the kit's examples.
