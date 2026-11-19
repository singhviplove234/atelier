# Launch video — a short product animation from what the factory already holds (optional)

Added in 0.5.0. An option (`options.md`), run by `/pf-promo` after a product is live. It does not make the video itself: it prepares everything a motion-graphics run needs, hands it to a **separate tool on the user's own computer**, and records the result. Nothing here is a gate, and no build depends on it.

## A. The tool, stated honestly
- The factory's default is the **Motion Design** skill (by Mr. Pynk, built on work credited to Rourke Heath): a folder the user downloads and adds to Claude on their computer, which builds an 8–20 second animation as code and renders it locally with Node, Python (Pillow, numpy, scipy), ffmpeg and Chrome. It is free to use.
- **It is not part of this plugin and never will be bundled:** it carries no licence. The user downloads it themselves from the author's page; the factory only points to it.
- **It needs a real graphics card**, so it runs in Claude Code or the desktop app on the user's PC — not in a cloud session. A render is heavy: one at a time.
- Known rough edges the factory tells the user up front: its notes mention helper scripts that are not in the download; an interrupted render starts again from the beginning; its starter template is plain, so quality comes from the storyboard notes, not from the first draft.
- Any other tool the user prefers can take the same brief pack — the pack is plain files.

## B. The brief pack (what `/pf-promo` writes — `<project folder>/promo/`)
Everything comes from what the project already recorded; nothing is invented:
- `brief.md` — the product in one sentence and who it is for (from the brief); length (default 10 s, 8–15 s recommended); where it will play and the format that implies (16:9 for a site or presentation, 9:16 for reels); tone, from the design direction; **the ending** — the live URL as the call to action; and the on-screen lines, each one taken from the SPEC's verbatim copy.
- `assets/` — the logo and wordmark (from the design system / repo), the brand colours and fonts as a small text file (from the SPEC's tokens), and the chosen screens (from `<project folder>/screens/`, which are test-data-only by rule — `verification.md` F — so no real user's data can appear in a video).
- `rules.md` — four lines the tool must follow, written into the pack because the tool's own instructions are broader: use only the files in this folder (do not search the computer for assets); every claim on screen comes from `brief.md`; no music, sound or font without a licence that covers advertising; show the storyboard and wait before building.

## C. How it runs
1. `/pf-promo` checks the product is live, writes the pack, and gives the user the exact words to say on their computer: open the Motion Design folder in Claude and type `start motion design — use the brief pack at <path>`.
2. The user directs it there: brief, assets, storyboard notes **by shot number**, stills, render, sound. Those approvals are the tool's own and stay with the user.
3. Back in the factory, the user gives the path of the finished file; it is recorded as `promo.video`. If the page should show it, that is a normal build change (a poster image first, the video on interaction — `performance-budget.md` rule 5).
4. Housekeeping the factory reminds the user of once: the tool leaves temporary browser-profile folders in the system temp folder after each render; they are safe to delete.

## Never
- Bundle, copy or redistribute the tool, or present it as part of the factory.
- Publish, post or upload a video on the user's behalf.
- Put a claim, statistic, review or logo of another brand in a brief that the project's own brief does not contain.
