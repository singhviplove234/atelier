# Launch video — a short product animation Atelier makes itself (optional)

An option (`options.md`), run by `/pf-promo` after a product is live. Atelier builds the animation as a small web page, renders it frame by frame with its own script, and hands back a video file. Everything it needs is already part of Atelier or already on the build machine for other reasons (Node, Playwright's Chromium, ffmpeg); nothing else is installed, no video or image model is used, and no graphics card is required. It is never a gate, and no build depends on it.

## A. What it is — and is not
- **Is:** an 8–15 second piece (20 at most) built from the product's real logo, colours, type and screens, in 16:9 or 9:16, rendered at 1080p or 4K. Because it is code, a note such as "slower here" is a small edit and a re-render.
- **Is not:** filmed footage, a talking head, generated imagery, or a soundtrack. The result is a **silent master** by default; sound is section E.
- **Honest limit:** the first draft is competent, not remarkable. Quality comes from the storyboard notes — direction is the user's contribution, and the flow is built around it.

## B. The brief pack (written by `/pf-promo` into `<project folder>/promo/`)
Everything comes from what the project already recorded; nothing is invented.
- `brief.md` — the product in one sentence and who it is for; length; format (16:9 for a site or presentation, 9:16 for reels); tone, from the design direction; **the ending** — the live URL as the call to action; the on-screen lines, each taken from the SPEC's verbatim copy or the user's own words.
- `assets/` — logo and wordmark, a `brand.txt` with the colours and fonts from the SPEC's tokens, and the chosen screens copied from `<project folder>/screens/` (test-data only by rule — `verification.md` F — so no real user's data can appear).
- `storyboard.md` — section C.

## C. The storyboard — approved before anything is built
Five to eight **numbered** shots. Each has: a time range; what is on screen, named by asset; the line, if any; what moves; and how it becomes the next shot. It is shown to the user as a table, and nothing is built until they approve it or give notes by shot number ("3 is too fast; swap 5 and 6"). This is the cheapest place to change anything.
Rules the storyboard is written to:
1. **One idea.** The piece says one thing about the product. If it needs a second sentence to explain, it is two videos.
2. **Shots hand over to each other.** Something in each shot — a shape, a position, a colour field — carries into the next, so the eye is never dropped. No hard jumps between unrelated frames.
3. **What matters sits in the middle** of the frame, and stays roughly where the eye already is across a change.
4. **Always a little movement**, even in a hold — a slow push or drift — and direction never reverses mid-move.
5. **Quick to arrive, slow to settle.** The first second earns attention; the product and the ending get time.
6. **Real things only.** The actual logo, the actual screens, the actual words. Nothing redrawn from memory, no invented statistics, reviews, badges or other companies' marks.
7. **It ends on what to do next** — the address, held long enough to read twice.

## D. The build (done on the build machine by `pf-promo-from-spec`)
- **One page, one clock.** `promo/page.html` in the product repo (on its own `promo` branch — it is not product code and never ships with the site) with local assets only. It exposes `window.TOTAL` (seconds) and `window.renderAt(t)`, which draws the whole frame for time `t` from scratch. No timers, no CSS animations that run on their own, no network: every frame must be reproducible from `t` alone. All shot timings sit in one block at the top so re-timing is a one-line change.
- **Plain web technology** — HTML, CSS transforms and opacity, SVG, 2D canvas. Fonts are local files from the project (the same licensed ones the site uses).
- **Review stills first.** `node <plugin>/scripts/render-video.mjs stills promo/page.html promo/out/stills <times>` at the middle of every shot and at two points in every handover. The stills go back to the PM, who shows them against the storyboard; the full render happens only after that approval.
- **Render.** `node <plugin>/scripts/render-video.mjs video promo/page.html promo/out/<slug>-launch.mp4 --fps 30 [--scale 2] [--portrait]`. One render at a time. 1080p by default; `--scale 2` (4K) only when the user asked for it.
- **Check the file**, not the log: duration matches `TOTAL`, the resolution is as requested, and a contact sheet of one frame per second shows no blank or half-drawn frame.

## E. Sound
The master is silent. If the user puts an audio file **they own or have a licence for** in `<project folder>/promo/audio/`, the build adds it under the picture with ffmpeg (trimmed to length, faded out over the last half second) as a second file, keeping the silent master. Atelier does not generate music or voice and does not source audio from anywhere.

## F. Result and after
`PROMO-RESULT.md` (shape in `bridge.md`) reports the stills folder, the video path, duration, resolution and any note. The PM records `promo.video`. If the page should show the video, that is a normal build change — a poster image first, the video on interaction (`performance-budget.md` rule 5).

## Never
- Use an asset, font or sound the project does not own or have a licence for, or put another company's name or mark on screen.
- Put a claim on screen that the project's brief does not contain.
- Publish, post or upload the video — that is the user's action.
- Let the promo page or its branch reach the deployed site.
