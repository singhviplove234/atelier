---
name: pf-promo
description: "Optional step for a live Atelier product: prepares a launch-video brief pack (one-sentence product, audience, length, format, ending, verbatim on-screen lines, logo, brand colours and fonts, test-data screenshots, and four safety rules) for a motion-graphics tool that runs on the user's own computer, tells the user exactly how to start it there, and records the finished video. Use when the user says /pf-promo, 'make a launch video', 'promo video', 'product animation', 'motion graphic for the launch', or 'video for the landing page'. Supports --check and --dry-run. It never renders, bundles or publishes anything itself, and it is never a gate."
---

# /pf-promo [slug] [--check] [--dry-run]

Turn what the factory already holds about a live product into a ready brief pack for a launch video. Read first:
- `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md`
- `${CLAUDE_PLUGIN_ROOT}/references/launch-video.md` (this step's contract — follow it)

## 0. Flags
`--check`: print `options.launch_video` and `promo` from `factory.json` and stop — read only `state-schema.md`. `--dry-run`: print the `brief.md` that would be written and the asset list; write nothing; stop.

## 1. Gate
Locate the project (the one the user names, else the only one; if several and none named, ask with AskUserQuestion). Read `factory.json`. Require `deploy.live_url` — "Deploy the product first (`/pf-deploy`); a launch video ends on a live address." and stop if it is empty. (For a store app the ending is the store listing once it is public, not the test link.) If `<folder>/screens/` is missing or empty (a project built before 0.4.0), say "Run `/pf-build` once so the screens are captured, or give me screenshots you own" and stop. This is an option (`references/options.md`): if `options.launch_video` is not `on`, say in one line what it is, that the tool is free but separate and needs the user's PC's graphics card, and ask with AskUserQuestion (Yes / Not now). On yes set `options.launch_video = "on"`.

## 2. Decisions — asked, a few at a time, skipping what is already known
Where it will play (site hero or presentation → 16:9; reels or stories → 9:16; both → two packs); length (default 10 seconds; 8–15 recommended); which two to four screens to feature (list the screens in `<folder>/screens/`); the ending (default: the live URL). Tone comes from `brief.design_direction`. Never invent a tagline, a statistic or a testimonial — on-screen lines come from the SPEC's verbatim copy, or from the user's own words here.

## 3. Write the brief pack
Per `launch-video.md` B, into `<folder>/promo/` (a second format goes in `promo-9x16/`): `brief.md`, `assets/` (logo and wordmark, a `brand.txt` with the colours and fonts from the SPEC's tokens, the chosen screenshots copied from `<folder>/screens/`) and `rules.md` with the four rules exactly as the contract words them. If the logo is not available as a vector or a large image, say so and ask for a better file rather than cropping one out of a screenshot. Record `promo.brief` (the folder path) and append `log {stage: "promo", event: "brief pack written"}`.

## 4. Hand over — the tool runs on the user's computer, directed by the user
Tell the user, per `launch-video.md` A and C: the default tool is the Motion Design skill, which the user downloads themselves from its author's page and which is **not** part of this plugin (no licence, so it is never bundled); it needs Node, Python with Pillow, numpy and scipy, ffmpeg and Chrome, and a real graphics card — `/pf-next doctor <slug>` checks these when this option is on. Then the exact words: open the Motion Design folder in Claude on the user's computer and type **`start motion design — use the brief pack at <promo.brief>`**. Mention once: give storyboard notes by shot number; render one video at a time; an interrupted render starts over. Do not try to run the tool from this seat, and do not copy its files anywhere.

## 5. Record
When the user says it is done, ask for the path of the finished file and record `promo.video`; append `log {stage: "promo", event: "video recorded"}`. If the user wants it on the site, say it is a normal change — `/pf-build` with a note — and that it loads as a poster first (`references/performance-budget.md` rule 5). Remind the user once that the tool leaves temporary browser-profile folders in the system temp folder, safe to delete.

## Never
- Render, bundle, copy or redistribute the tool, or run it from the cloud.
- Publish, post or upload the video.
- Put anything in the brief that the project's own brief and SPEC do not contain.
- Treat this as a gate or a required stage — a product is complete without it.
