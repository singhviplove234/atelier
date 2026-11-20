---
name: pf-launch
description: "Optional step for a live product that is about to be announced: a launch checklist read from the project's own record (live version, preview tests, monitoring and alerts, backups, legal pages, domain and redirects, search setup, share images, mail delivery, a way to get help, live payments, rollback, speed), with each missing item offered as a numbered fix; share images and store pictures made from the brand template and real screens; an honest waitlist or newsletter sign-up with double opt-in; announcement drafts; and a watch list for the first 48 hours. Use when the user says /pf-launch, 'am I ready to launch', 'launch checklist', 'launch pack', 'social images', 'OG image', 'waitlist', 'coming soon page', or 'announcement post'. Supports --check and --dry-run. Posts and sends nothing itself, and is never a gate."
---

# /pf-launch <slug> [--check] [--dry-run]

Read first:
- `${CLAUDE_PLUGIN_ROOT}/references/launch.md` (this step's contract — follow it)
- `${CLAUDE_PLUGIN_ROOT}/references/state-schema.md`, `options.md`

## 0. Flags
`--check`: print `options.launch_pack` and `launch` from `factory.json` and stop. `--dry-run`: print the checklist with its current answers; write nothing; stop.

## 1. Locate
Find the project; read `factory.json` and the latest deploy, harden and monitor results. A waitlist page can be made **before** the product is live (section 4); everything else needs `deploy.live_url` — otherwise say "Deploy first (`/pf-deploy`)" and offer only the waitlist. Set `options.launch_pack` to `on`.

## 2. The checklist
Fill L1–L14 from `launch.md` A using the record — do not re-run stages to answer it. Show it as a table: done / missing / not applicable, with the proof. For each `missing` line give the one command or build that closes it, cheapest first. Ask which to close now with AskUserQuestion (by number). L2 and L14 restate contracts and cannot be waved through; for any other line the owner may say "accept", and the reason is recorded.

## 3. Share images and store pictures
Per `launch.md` B. If the template is missing, add it through the brand kit (`/pf-brand`) or propose a plain one from the design tokens. The images are code and files in the repository: write a `Launch:` note for `/pf-build` naming the pages and sizes, and run that build. Afterwards load each page's metadata and look at the image before calling L8 done.

## 4. Waitlist or newsletter sign-up (only if wanted)
Per `launch.md` C, and `email.md` for the confirmation message — if `options.email` is not `transactional` or `both`, set that up first (`/pf-setup email`). It is a normal build from the SPEC. Record `launch.waitlist`.

## 5. Announcement drafts
Per `launch.md` D: ask where the owner will announce, then draft for those places only, from the Brief's `Entity:` block and the product as built. Show them as drafts. Posting, sending or submitting is the owner's action; if they ask for one to be sent through a connected tool, confirm that one message and its recipient first. For a video, mention `/pf-promo` in one line.

## 6. Launch day
Write the 48-hour watch list (`launch.md` E). Ask for the launch date and record `launch.date` and `launch.checklist`; append `log {stage: "launch", event: "pack ready"}`. Say that `/pf-feedback` and `/pf-grow` are the next steps a week after.

## Never
- Post, send, submit or publish anything without the owner's yes to that one action.
- Invent a review, a testimonial, a user count, a deadline or a waitlist number.
- Mark a checklist line done without its proof, or wave through a contract line.
- Treat this as a gate — the launch decision is the owner's.
