---
name: pf-promo
description: "Optional step for a live Atelier product: makes a short launch video with Atelier's own tools. Writes a brief pack from what the project already holds (one-sentence product, format, ending, verbatim on-screen lines, logo, brand colours and fonts, test-data screenshots), drafts a numbered storyboard for approval, hands the build to the Code session, shows review stills before the full render, and records the finished file. Use when the user says /pf-promo, 'make a launch video', 'promo video', 'product animation', 'motion graphic for the launch', or 'video for the landing page'. Supports --check and --dry-run. Nothing extra is installed, it never publishes anything, and it is never a gate."
---

# /pf-promo [slug] [--check] [--dry-run]

Turn what Atelier already holds about a live product into a short launch video. Read first:
- `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md`
- `${CLAUDE_PLUGIN_ROOT}/references/launch-video.md` (this step's contract — follow it)
- `${CLAUDE_PLUGIN_ROOT}/references/bridge.md` (the hand-off and the `PF-PROMO` file shapes)

## 0. Flags
`--check`: print `options.launch_video` and `promo` from `factory.json`, or pick up a waiting `PROMO-RESULT.md`, and stop. `--dry-run`: print the `brief.md` and storyboard that would be written; write nothing; stop.

## 1. Gate
Locate the project (the one the user names, else the only one; if several and none named, ask with AskUserQuestion). Read `factory.json`. Require `deploy.live_url` — "Deploy the product first (`/pf-deploy`); a launch video ends on a live address." and stop if it is empty. (For a store app the ending is the store listing once it is public, not the test link.) If `<folder>/screens/` is missing or empty, say "Run `/pf-build` once so the screens are captured, or give me screenshots you own" and stop. This is an option (`references/options.md`): if `options.launch_video` is not `on`, say in one line what it is — a short silent animation built in code from the product's own assets; competent on the first draft, good after your notes — and ask with AskUserQuestion (Yes / Not now). On yes set `options.launch_video = "on"`.

## 2. Decisions — asked a few at a time, skipping what is already known
Where it will play (site hero or presentation → 16:9; reels or stories → 9:16; both → two runs); length (default 10 seconds; 8–15 recommended); which two to four screens to feature (list those in `<folder>/screens/`); the ending (default: the live URL); 1080p (default) or 4K. Tone comes from `brief.design_direction`. Never invent a tagline, a statistic or a testimonial — on-screen lines come from the SPEC's verbatim copy or the user's own words here.

## 3. Brief pack and storyboard
Per `launch-video.md` B and C, write `<folder>/promo/brief.md`, `assets/` (logo and wordmark, `brand.txt` from the SPEC's tokens, the chosen screens) and `storyboard.md` — five to eight numbered shots written to the seven storyboard rules. If the logo is not available as a vector or a large image, ask for a better file rather than cropping one out of a screenshot. Show the storyboard as a table. **GATE — storyboard:** "Approve, or give notes by shot number." Nothing is built before an approval word (`state-schema.md`); notes are applied and the table shown again. Record `promo.brief`.

## 4. Stills, then the render (hand-off per `bridge.md`)
Write `<folder>/PROMO-REQUEST.md` with `stage: stills` and hand off exactly as a build is handed off — `/pf-next <slug> promo --go` typed into the PM lane's Code session through Chrome, or the fallback line for the user to type. On `PROMO-RESULT.md`: show the stills beside the storyboard, numbered by shot. **GATE — stills:** approve, or notes by shot number (a new request with `notes:`). Only on approval write a request with `stage: video` and hand off again. Renders run one at a time.

## 5. Record
On a `status: ok` video result: show the file path, duration and resolution; record `promo.video`; append `log {stage: "promo", event: "video recorded"}`. Say plainly that the master is silent and how sound is added (`launch-video.md` E: an audio file the user owns or has licensed, placed in `<folder>/promo/audio/`, then one more `stage: video` run). If the user wants it on the site, that is a normal `/pf-build` change, loaded as a poster first (`references/performance-budget.md` rule 5).

## Never
- Build before the storyboard is approved, or run the full render before the stills are.
- Put anything on screen that the project's brief and SPEC do not contain, or any asset or sound the user does not own or have licensed.
- Publish, post or upload the video.
- Treat this as a gate or a required stage — a product is complete without it.
