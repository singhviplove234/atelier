# Support basics — a help page, a contact form, and a way to answer

Added in 2.2.0. Optional (`options.md`): offered when the product will have users who are not the owner. Recorded in `factory.json.options.support` (`off` / `on`). It is built by a normal build from a `Support:` line in the SPEC's Brief, so it meets every contract like any other screen. Deliberately small: no chat widget and no help-desk subscription by default.

## A. Help page and FAQ
- Written from the product's own flows: every step in the user-journey diagram where someone can get stuck or fail gets a question and a plain answer. Eight to fifteen questions; more belongs in documentation.
- In the user's words, not the product's ("I did not get the email", not "Email deliverability"). Each answer says what to do first, then why.
- The content lives in one file in the repo, so growth drafts and feedback (`growth.md`, `feedback.md`) can update it without a redesign.
- Filterable on the page by typing; every answer reachable by a link.
- Structured data (`FAQPage`) only when every question and answer is visible on the page exactly as marked up (`seo-ai-visibility.md`). Its value is clarity for people and for AI answers; a rich result in search is not promised.

## B. Contact form
- Fields: email, message, and a topic list drawn from the FAQ headings; name optional. No file upload by default.
- Validated on the server. Spam is handled without a puzzle: a hidden trap field, a minimum time before submit, and a rate limit per address and per network address. A challenge is added only if spam actually arrives, and then a privacy-respecting one.
- A message is stored in a `support_messages` table (the public may insert; only an admin may read — `security.md`) and, when `email.md` C is set up, also sent to the support address. The sender gets one acknowledgement with an honest reply time.
- One line of consent with a link to the privacy notice; messages are deleted on the schedule the notice states (`compliance.md`).
- The failure path is designed and tested: if the message cannot be saved or sent, the page says so and shows the support address.

## C. The support address and the promise
`support@` on the domain (`email.md` A). The help page states a reply time the owner can actually keep, and links to the status page when the product has one (`monitoring.md` F).

## D. The runbook — `docs/SUPPORT.md`
Where messages arrive and who answers; five saved replies for the five most likely problems; how a message becomes a fix (`/pf-feedback`); what to do with a request to export or delete someone's data (`compliance.md`); when to raise an incident (`monitoring.md`).

## E. Checks the builder reports
`support: on — faq <n> questions, form <ok>, e2e <success, validation, spam trap, send failure>`. The four e2e paths are required.

## Offered later, never by default
A live-chat or help-desk tool — a third-party script on every page, a monthly fee, and someone who must be there to answer. Raise it only when message volume shows the need, with its price and its cost to page speed (`performance-budget.md`).
