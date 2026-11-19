# Design craft — how Atelier reaches the bar the design standard sets

`design-standard.md` is the contract: tokens, contrast, fonts, motion limits, the checks a build must pass. This page is the craft that gets a design *to* that bar without looking like a template. It is Atelier's own guide and is complete on its own — nothing else needs to be installed to use it. Where the two ever disagree, the standard wins.

## A. Start from the direction, not from a component library
The brief names one design direction. Each has a different centre of gravity; designing every project the same way is what makes generated sites look alike.
- **Brand** — one idea carried through the whole page. Large confident type, real photography or one strong visual motif, long vertical rhythm, generous empty space. Motion is part of the identity, not decoration. Fewer sections than you think; each one earns its place.
- **Product** — the interface is the hero. Dense but calm: a strict grid, small type that still reads, quiet colour with one accent used only for the primary action and for state. Every screen answers "what can I do here?" within a second.
- **Editorial** — typography does the work. A real measure (60–75 characters), a clear scale with few sizes, strong hierarchy from weight and space rather than boxes. Images support the text; they do not interrupt it.
- **Marketing** — one promise, one action. A headline that says what the visitor gets, proof directly under it, the call to action visible without scrolling and repeated after each block of proof.
Two variants a direction may take when the brief asks for them: **minimal** (remove until removing more would lose meaning — one typeface, one accent, hairline rules, no shadows) and **raw / brutalist** (visible structure — hard edges, monospaced or grotesque type, exposed grid, high contrast, deliberate bluntness). Both are commitments: half-applied, they read as unfinished.

## B. The details that separate finished from generated
1. **Type.** Two sizes carry most of a screen; a third is an event. Tighten tracking on large headings, loosen it slightly on small capitals, set body line-height by measure not by habit. Never let a heading end on a single orphaned word.
2. **Space.** Use the spacing scale, and use *more* of it between groups than within them — proximity is the first signal of structure. Align to a small number of vertical edges.
3. **Colour.** One accent. Greys with a slight tint of the accent sit better than neutral grey. State colours (success, warning, danger) are functional and never decorative.
4. **Depth.** One light source. Either borders or shadows as the main separator, not both. Shadows are soft, low and few.
5. **Touch and focus.** Every control has a visible focus state designed on purpose, a comfortable hit area, and a pressed state. Hover is an enhancement, never the only signal.
6. **Empty, loading, error.** Design these three for every screen that has data. A skeleton that matches the final layout beats a spinner; an error says what happened and what to do next.
7. **Copy.** Buttons say what happens ("Send message", not "Submit"). Headlines state a benefit a person would say out loud. User-facing copy gets a pass with the bundled `humanizer` skill so it reads like a person wrote it — plain, specific, no filler — and never to fake a review or mislead.

## C. Motion that reads as intent
- **Purpose first.** Motion explains a change (where something came from, what is now active) or carries brand feeling. If it does neither, remove it.
- **Timing.** Small state changes 120–200 ms; elements entering or leaving 200–400 ms; large scene changes up to ~600 ms. Things leave faster than they arrive.
- **Easing.** Decelerate on entry, accelerate on exit; never linear except for continuous progress. One easing family across the product.
- **Choreography.** Stagger related items by a few tens of milliseconds; move the most important thing first; keep what the eye is following in roughly the same place across a transition.
- **Restraint.** One signature moment per page is memorable; five is noise. Scroll-linked motion stays light and never hijacks the scroll.
- **Limits.** Everything in `design-standard.md` about GPU-only properties, layout shift, reduced motion and total weight applies — craft works inside those limits, never around them. Reach for a motion library only when plain CSS genuinely cannot do the job within the JavaScript budget.

## D. Upgrading an existing site
When the work is a redesign rather than a first build: (1) screenshot every screen first — that is the baseline; (2) fix hierarchy and spacing before touching colour or adding motion, because most "it looks dated" is structure; (3) replace components with the design system's, one screen at a time, keeping every route and every piece of copy that ranks; (4) re-run the full contracts — a redesign that loses search position or speed is a regression, however good it looks.

## E. A brand kit, when a project needs one
For a `brand` direction with no existing identity, assemble one page before any screen is designed: the name and how it is written; a primary mark and a small-size version; two typefaces at most, both properly licensed; a palette of one accent, one dark, one light and a tinted grey ramp, each with its contrast pairings; three example compositions showing the system in use; and a short list of what the brand never does. It becomes the project's design system tokens. Logos and names of other companies are never imitated.

## F. A second look before sign-off
Before the design goes for approval, check it once as each of these people would: someone on a small phone in bright light; someone using only a keyboard; someone who has never heard of the product and gives it five seconds; and the person who has to maintain it in a year. Fix what any of them would trip on. The bundled `design-md` library of real design systems is there for comparison when choosing or pressure-testing a direction — as reference, never to copy a brand.
