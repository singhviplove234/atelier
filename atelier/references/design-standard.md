# Design standard — the best design for each project, built on an Apple-grade foundation

Standing requirement: every product the factory designs carries Apple-level craft — the taste from Apple's Human Interface Guidelines (hierarchy, harmony, consistency) — but the **look is chosen to fit the project**, not forced into one style. A luxury brand site, a SaaS dashboard, an editorial site and a marketing landing page each deserve a different, best-in-class design; the factory evaluates the project and picks the right **design direction**, then executes it to the same high bar. Implemented for the web with free, correctly-licensed assets, never Apple's own fonts or symbols. This guides the `pf-design-system` artifact and the build; it never overrides the performance, SEO, security, compliance or simplicity contracts.

## Pick the design direction (evaluate the project first)
`/pf-design` judges what the product is and sets `brief.design_direction` to the best fit; the design-system and build then execute that direction on the shared foundation below. Directions:
- **brand** — a premium/luxury or lifestyle brand, D2C, portfolio, or anything sold on feel. Cinematic and generous: large hero (image or motion), scroll-reveal and parallax, refined type pairing (a display serif/grotesque + Inter), big whitespace, tasteful micro-interactions, optional frosted glass. **Motion-led** (see below).
- **product** — a SaaS app, dashboard, internal tool. Clarity and density over flourish: strong information hierarchy, compact components, fast subtle motion only (state changes, not decoration). Apple-HIG minimal.
- **editorial** — a blog, docs, media or content site. Typography-first: a real reading rhythm, measured line length, clear headings, restrained motion.
- **marketing** — a landing/conversion page. Bold hero and one clear CTA, social proof, sectioned storytelling, light purposeful motion that guides the eye to the action.

The **foundation** (tokens, accessibility, licensed fonts/icons, the non-negotiables below) is identical across directions; only the expression — type pairing, scale of whitespace, amount and style of motion, use of imagery/glass — changes. When unsure between two directions, `/pf-design` asks one short question; otherwise it states the chosen direction in one line and proceeds.

## The principles we borrow (HIG, platform-neutral)
- **Hierarchy** — one clear focal point per screen; size, weight and spacing do the work, not boxes and lines. Primary action is obvious; secondary actions recede.
- **Harmony** — one type family, one accent colour, one spacing rhythm used everywhere; nothing arbitrary.
- **Consistency** — the same component looks and behaves the same on every screen; predictable placement of nav, actions and feedback.
- **Deference** — content first; chrome, colour and effects stay quiet so the content leads.
- **Clarity** — legible text at every size, generous whitespace, honest state and feedback.

## The system (what `pf-design-system` encodes, and the build implements)
- **Type:** `Inter` (an SF-style, open-licence web font) via `next/font`, self-hosted; optional `Newsreader`/serif for display only. A small, strict scale — about `12·14·16·18·20·24·30·36·48` px — with line-heights ~1.5 for body and ~1.1 for display. One family for UI, two weights (400/600) plus 700 for display. Never Apple's SF Pro / New York (licensed for Apple-platform apps only).
- **Spacing:** a 4-pt grid (`4·8·12·16·24·32·48·64`), used for padding, gaps and section rhythm. Consistent page gutters (16px mobile, more on desktop).
- **Colour:** one accent, a neutral grey ramp (bg / surface / border / muted-text / text), semantic success/warn/error, in light **and** dark. Contrast meets WCAG AA (body ≥ 4.5:1) — this ties into the accessibility checks already in the build.
- **Radii & elevation:** 2–3 radii (e.g. 8 / 12 / full); shadows soft and sparing for depth, not decoration.
- **Components:** Button (primary/secondary/ghost), Card, Input + field states, Nav, Hero, Footer, plus whatever the brief needs — each with hover/focus/active/disabled states and a visible keyboard focus ring.
- **Icons:** an open set — **Lucide** or **Heroicons** — never Apple SF Symbols.
- **Motion (baseline):** short, purposeful transitions (~150–250 ms, ease-out); respect `prefers-reduced-motion`; never block interaction.
- **"Liquid-glass" look (optional, tasteful):** a frosted translucent surface (`backdrop-blur` + translucent bg) may be used for a nav bar or an overlay when the direction wants a premium feel — but sparingly, always with a solid fallback and AA text contrast over it, and it must not break the performance budget (blur is costly) or `prefers-reduced-transparency`.

## Motion & animation (the motion-led layer — strongest in the `brand` direction)
Motion is a design tool, used in proportion to the direction (rich for `brand`, light for `marketing`/`editorial`, minimal for `product`). The craft below is distilled from a real shipped motion-led brand site (a premium-brand site shipped in 2026); the **grammar, defaults and rules are generalizable** — re-tune the exact numbers to each project's footage and feel.

**The grammar (the discipline that makes it feel calm, not busy):** the reader's **scroll is the clock**. Every motion is one of two things — (a) **scrubbed by scroll position** (tied to how far down the page you are, via a scroll library like GSAP ScrollTrigger) or (b) a **one-shot reveal** when an element enters the viewport (a CSS transition fired once). **Nothing runs on a loop or a timer** except short in-view videos, which play only while they are actually visible and pause otherwise. Smooth-scroll weighting (e.g. Lenis `lerp ≈ 0.11`) eases fast flicks instead of snapping — optional, `brand`-only, and off under reduced-motion.

**Generalizable default values (sensible starting points — re-tune per project):**
- **Scroll-reveal:** `opacity 0 → 1`, `translateY ~24px → 0`, **~0.9 s** `cubic-bezier(.2,.7,.2,1)`; fired once by an `IntersectionObserver` (`rootMargin '0px 0px -10% 0px'`, unobserve each element after it reveals). Stagger grouped lines ~80 ms apart via `transition-delay`.
- **Parallax / depth:** move a background/hero still **~±4%** inside an `overflow:hidden` frame, with the image at **scale ~1.1** so its edges never show. Small amounts only; never on text being read.
- **Scroll-scrubbed scenes (brand hero/story):** tie a value (a frame number, a transform) to scroll with a short **scrub lag ~0.35 for a pinned scene, ~0.6 inline** (lag smooths the motion). A pinned scene is a tall section (**~175–190 vh**, footage-dependent) with a `position:sticky; top:0; height:100svh` stage inside it. Frame counts and exact scrub are **footage-tuned, not fixed**.
- **Hero element depth:** scrub a gentle `scale` (e.g. `1.04 → 0.94`) — not position jumps.
- **In-view video:** play from the start when **≥ 50 % visible**, pause when not; `playbackRate ~0.8` reads as expensive; `<video muted playsinline preload="metadata" poster>`, and call `.load()` only when the element is ~150 % of the viewport away (not on page load).
- **Nav / chrome:** toggle a `scrolled` class past **scrollY > ~64px** (background + border transition ~0.4 s) via a passive scroll listener.
- **Micro-interactions:** hover/press/focus on buttons, cards, inputs respond in **~150–350 ms** on `transform`/`opacity`/`color`; a resting still may sit slightly zoomed (`scale 1.06`) and calm to `1.02` on hover; loading, success and error states animate, never pop.
- **Page transitions:** for a static site, **none by design** — instant navigation, the hero poster paints first; add route transitions only when the direction truly needs them.

**How it is kept honest (non-negotiable — these are the rules that stop motion from wrecking the site):**
- **GPU-only.** Animate `transform`, `opacity`, `background-position` or a `<canvas>` frame — **never** layout properties, **never** `filter`, and **never** `mix-blend-mode` over a moving element (a full-screen blend costs a composite per frame and is the first thing to lag).
- **Position overlay/hero elements with the CSS `translate` property + a viewport-relative size** (e.g. `translate` with `width: min(80vw, 1500px)`), **not** a scroll library's `x`/`y` on top of a CSS transform — stacking the two **doubles the offset** and pushes the element off-screen. Verify the whole element stays visible at every width.
- **Honour `prefers-reduced-motion: reduce` fully:** don't start smooth-scroll, don't pin scenes (show the poster still), render reveal elements already-visible with no transition, keep in-view videos on their poster, and don't register parallax/sweeps. The site stays fully usable and keyboard-reachable with a visible focus ring. (A11y Lighthouse 100 is still required.)
- **Motion never gates the site** — it enhances; every action works with motion off.
- **Lazy-load heavy media in scroll order.** Load document, CSS, fonts, text and stills first; fetch heavy scene assets at `fetchpriority="low"`, only for scenes within ~150 % of the viewport, a couple in flight at most, in order; if an asset isn't ready, **hold the last frame** rather than jumping. Stays within the performance budget and its **scroll-motion weight budget** (see `performance-budget.md`).
- **Canvas (only if a scene uses one):** cap the backing store (effective DPR ~1.25 phone / ~1.5 desktop so Retina doesn't draw 2×), never wider than ~2000 px, `contain:strict; will-change:transform; backface-visibility:hidden`, 2D context `desynchronized:true`. Decode images off the main thread (a worker + `createImageBitmap`); the main thread only draws, and release bitmaps (`ImageBitmap.close()`) for scenes far off-screen so memory holds two or three scenes, not all of them.
- **Third-party scripts never run on load** — start them on interaction (e.g. a form's bot-check on focus/click), never at idle on first paint.
- **Library budget:** a scroll/animation library is added only if it earns its weight under the simplicity + JS-budget rules; prefer CSS transitions + `IntersectionObserver` for reveals and reserve a library (GSAP ScrollTrigger, Motion/Framer Motion) for scrubbed scenes or a form swap where CSS can't do it.
- **Avoid (these all shipped lag once):** full-size image sets on every device; preloading every scene at once (starves text and video); `mix-blend-mode` on canvases; a CSS image mask scrubbed every frame on a large canvas (bake the effect into the frames instead); library `x`/`y` stacked on CSS `translate`; starting third-party scripts at idle; cover-cropping square frames on portrait; and **measuring only on a warm-cache desktop** — every real lag complaint came from a cold cache, a second browser (Edge/Safari) or a real phone.

## How it is checked (build step 6; a `design` lens in `/pf-harden` reuses this)
Mostly reuses tools already in the build — this adds taste rules, not new scanners:
- Tokens from `pf-design-system` are the only source of colour/type/spacing; grep for hard-coded hex colours or arbitrary `px` font sizes outside the token set → fix.
- Exactly one `<h1>` per page and a visible type hierarchy (reuse the SEO heading check).
- Every interactive element has a visible focus state and AA contrast (reuse the accessibility/Lighthouse check; a11y ≥ 95 already required).
- `prefers-reduced-motion` and, where glass is used, `prefers-reduced-transparency` are honoured; animations use only `transform`/`opacity`/`background-position`/a canvas frame (no layout-animating jank, no `filter` or `mix-blend-mode` over a moving element) and cause no CLS. Under reduced-motion the site shows posters/already-revealed content and stays fully usable.
- Scrubbed/parallax/in-view-video scenes lazy-load their heavy media (in-view or `fetchpriority="low"`, not on first paint), and the **scroll-motion weight budget** in `performance-budget.md` is met (first-visit and full-scroll payload ceilings, no frame > 50 ms during a continuous scroll, no empty rectangle on screen). Overlay/hero elements are positioned with CSS `translate`, not library `x`/`y` stacked on it.
- The chosen `brief.design_direction` is actually expressed (a `brand` site looks premium/motion-led, a `product` app looks clean and dense) — not every project rendered as the same minimal template.
- Fonts are self-hosted `Inter` (or the chosen open font), not Apple fonts; icons are the chosen open set — no SF Symbols, no SF Pro/New York files in the repo.
- Spacing and radii come from the scale (no stray values). Report a short design table in `notes:`: tokens-only? · one-h1? · focus states? · reduced-motion? · fonts/icons licensed? — fix any "no" within the simplicity/perf/a11y limits.

The aim is Apple-grade feel — clear, calm, consistent, premium — using only assets we may freely ship, and never at the cost of speed, accessibility or the other contracts.
