# Launch pack — being ready on the day, and having something to show

Added in 2.2.0. Optional (`options.md`): offered after the first live deploy of a product that will be announced. Recorded in `factory.json.options.launch_pack` (`off` / `on`) and `factory.json.launch`. Run by `/pf-launch`. It is **not a gate**: launching is the owner's decision. Anything it finds that needs code goes through a normal build.

## A. The launch checklist — read from the record, not re-run
Each line is `done`, `missing` or `not applicable`, with the field or file that proves it. Numbered L1, L2 … so the owner can answer by number.
| # | Ready when | Proof |
|---|---|---|
| L1 | The live version is the approved one | `deploy.live_tag`, the deploy result |
| L2 | The preview passed its e2e suite | the deploy result |
| L3 | Monitoring and an alert that reaches the owner are on, and the alert was tested | `monitoring.*` |
| L4 | Backups exist and a restore was tested (products with data) | `maintenance.backups`, `restore_tested` |
| L5 | Privacy notice, terms, and consent for analytics are live and accurate | `compliance.md`, the pages |
| L6 | The custom domain serves over HTTPS and every old address redirects in one hop | `deploy.custom_domain`, the harden result |
| L7 | Search engines can find it: sitemap submitted, no page blocked by mistake | `/pf-setup seo`, the harden result |
| L8 | Every key page has a title, a description and a share image that shows correctly | B below |
| L9 | The icon set, the not-found page and the error page exist | the build result |
| L10 | Mail arrives (products that send any) | `email.verified` (`email.md`) |
| L11 | People can get help | `options.support` or a contact route (`support.md`) |
| L12 | Payments work in live mode — the owner made one real small payment and refunded it (products that charge) | the owner's word |
| L13 | The last good version can be put back | `monitoring.rollback`, the previous `live-` tag |
| L14 | The performance budget passes on the live site | the harden result |
`missing` lines are offered as numbered fixes, the cheapest first. A line that restates a contract (L2, L14) cannot be waved through here; the others are the owner's call, recorded with the reason.

## B. Share images and store pictures
- **Share image** (1200 × 630) for the home page and every page likely to be shared, drawn in code at build time from one template in the brand kit (`brand.md` C) — the page title in at most two lines, the logo, brand colours. Checked by loading the page's metadata and looking at the image, not by assuming.
- **Store pictures** for a mobile app or an extension come from the e2e screenshots: the real interface with test data. Never a mock-up of a screen that does not exist.
- **Announcement pictures** (square and portrait) from the same template.
All of these are files in the repo, built by a normal build.

## C. Waitlist or newsletter sign-up
One field (email) and one sentence of consent. Double opt-in through `email.md`; the address, the consent wording and the date stored in the product's own table (the public may insert, only an admin may read) or sent to the owner's list tool; an unsubscribe link from the first message; export as CSV for the owner. Any count shown on the page is the real count. No invented scarcity, no fake sign-up numbers.

## D. Announcement drafts
For the places the owner names — a post, an email to the waitlist, a directory listing. Drafts only, from the Brief's `Entity:` block and the product as built; nothing is posted, sent or submitted without the owner doing it or saying yes to that one action. No invented reviews, testimonials, user counts or deadlines. The launch video is its own option (`launch-video.md`).

## E. The first 48 hours
A one-page watch list: where errors and uptime show (`monitoring.md`), where sign-ups and the support inbox are, who is watching and when, and the one line that rolls back. After a week, `/pf-feedback` and `/pf-grow` take over.

Record `launch: { checklist, date, waitlist }` — the checklist's location, the launch date the owner sets, and `none` / `on` for the sign-up.
