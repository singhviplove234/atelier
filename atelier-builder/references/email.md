# Email — an address on the domain, and mail the product sends

Added in 2.2.0. Optional (`options.md`): offered when the product has a custom domain and either the owner wants a contact address on it or the product must send mail (sign-up, reset, receipts, a contact form). Recorded in `factory.json.options.email`: `none`, `address` (receiving only), `transactional` (the product sends), or `both`. Which messages a product sends is decided elsewhere (`saas-blueprint.md` for a SaaS, the SPEC for everything else); this file is **how** any of them is set up so it arrives.

## A. An address on the domain (receiving)
- Start with **forwarding**: `hello@` and `support@` on the domain forward to a mailbox the owner already has. Free with many DNS hosts and registrars. It receives; replying *from* the address needs a real mailbox or a sending service.
- A **real mailbox** on the domain is a paid service in most cases. Offer it only when the owner will reply from that address daily; state the monthly price from the provider's page, per `cost-posture.md`.
- Use addresses people can answer. A `no-reply@` sender is avoided: replies are feedback.

## B. The sending identity (before the product sends a single message)
Mail from a domain without these is filtered or refused by the large mailbox providers.
1. **SPF** — exactly one SPF record on the sending domain, naming every service that sends for it.
2. **DKIM** — the sending service's keys published as DNS records, and signing switched on.
3. **DMARC** — a policy record. Start at `p=none` with a report address; after two weeks of clean reports move to `quarantine`, then `reject`. Never start at `reject`.
4. **A sending subdomain** (for example `mail.<domain>`) for product mail, so a problem there does not damage mail from people at the root domain.
DNS is the owner's: Claude prepares the exact records and the owner pastes them at the DNS host (`/pf-setup email`, the same way as `/pf-setup domain`). **Check:** send one test message to a mailbox the owner controls and read its headers — `spf=pass`, `dkim=pass`, `dmarc=pass`, all aligned with the visible From domain. Record the date in `factory.json.email.verified`.

## C. Mail the product sends (transactional)
- One sending service behind **one small function** (`sendEmail(template, to, data)`), so the service can be swapped. Its API key is an env var **name** in the SPEC; the value is set by the owner at the host.
- Free tier first (`cost-posture.md`): read the current limit on the provider's page and compare it with the plan's expected volume; say when the plan would outgrow it.
- Templates are files in the repo, each with a plain-text version, a real subject, and the copy approved in the SPEC. No images that carry the message; no tracking pixels unless the privacy notice says so.
- Sending is **idempotent** (a repeated request does not send twice), retried with back-off on a temporary failure, and rate-limited per recipient.
- **Bounces and complaints** come back by webhook (signature verified); a hard bounce or a complaint suppresses the address for good.
- An unverified sign-up gets the verification message and nothing else.
- **Tests never send to real people.** The test environment uses the provider's test mode or a capture mailbox; e2e asserts that the right message was requested with the right data (`verification.md`), including the failure path when the provider is down.

## D. Newsletters and marketing mail are a different thing
They need **consent** recorded with its date and wording, confirmed by a second message (double opt-in); an unsubscribe link in every message and the one-click unsubscribe header; a real postal address where the law asks for one; and their own sending stream, apart from product mail. The factory builds the sign-up, the consent record and the unsubscribe (`launch.md` C). Which tool sends the newsletter is the owner's choice. Rules differ by country — ask where the recipients are, follow `compliance.md`, and say that this is not legal advice.

## E. Checks the builder reports
`email: address | transactional | both — spf/dkim/dmarc <pass|pending owner DNS>, templates <n>, bounce webhook <ok|n/a>`. A product that sends mail is not marked ready for launch while the identity check is pending.

## Never
Send from a domain without SPF, DKIM and DMARC in place. Buy, rent or import an address list. Send marketing mail without recorded consent. Put a key or a DNS password in the repo or in a request file. Type a registrar or DNS password. Use a real customer address in a test.
