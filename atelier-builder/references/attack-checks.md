# Attack checks — what every build is checked against, and where each rule comes from

Twenty rules. Each one was written from a primary source that was opened and read on the date shown; the supporting words from that source are quoted beside it. A rule whose source could not be opened is not in this file. These rules add to `security.md`; they loosen nothing in it.

## A. Checked by code on every build (`scripts/sec-check.mjs`)
The Code session runs `node "${CLAUDE_PLUGIN_ROOT}/scripts/sec-check.mjs" "<code checkout>"` before the reviews step. It is read-only and makes no network call. A `FAIL` line is a failed build and is listed in the result under `sec-check:`. If it cannot be run, the result says `sec-check: not run` and why - never a pass.

| # | Rule | Source (opened 23 Nov 2026) |
|---|---|---|
| A1 | A database view in the exposed schema is created with `security_invoker = true` (or moved out of the exposed schema). Without it the view runs with its owner's rights and can show rows that row level security should hide. | PostgreSQL manual, CREATE VIEW: "checked against the privileges of the user of the view rather than the view owner". Supabase, Row Level Security: "Views bypass RLS by default". |
| A2 | Nothing that guards access (a token, a code, an id, a reset or invite link) is made with `Math.random()`. Use `crypto.getRandomValues` or `crypto.randomBytes`. | MDN, Math.random(): "Do not use them for anything related to security." |
| A3 | Proxy trust is never `true`. Set the exact number of proxies or their addresses, and limit sensitive actions per account as well as per address. | Express, Behind proxies: "the client's IP address is understood as the left-most entry". |
| A4 | A login token (JWT) is verified with a fixed list of allowed algorithms, never the one the token names. | PortSwigger, Algorithm confusion: "an attacker could sign the token using HS256 and the public key". |

## B. Reviewed on every web build (a person-like judgement the reviewer makes)
| # | Rule | Source (opened 23 Nov 2026) |
|---|---|---|
| B1 | A password is hashed on its own. Nothing is put in front of it or joined to it before hashing, and its length is capped at the hash's limit. Prefer the auth provider's own hashing. | OWASP Password Storage Cheat Sheet: "bcrypt has a maximum length input length of 72 bytes". |
| B2 | No text pattern (regular expression) with nested repetition runs on user input. Cap the input length first, or use plain string functions. | OWASP, ReDoS: "work very slowly (exponentially related to input size)". |
| B3 | A request body is never merged into an object unchecked. Validate it against a schema, allow only named keys, and use a Map for user-keyed data. | PortSwigger, Preventing prototype pollution: "Using an allowlist of permitted keys is the most effective way". |
| B4 | User input reaches a template only as a value, never as part of the template's own text. | PortSwigger, Server-side template injection: "not allow any users to modify or submit new templates". |
| B5 | A username or email that allows Unicode is normalized once at sign-up, stored and compared only in that form, and refused if normalizing it a second time changes it. | Spotify Engineering, 2013: "rejects a name if old_prepare(old_prepare(name)) != old_prepare(name)". |
| B6 | Every number from the user that affects money or stock (a quantity, a price, an amount) is checked on the server for its allowed range, including zero and negative values. | PortSwigger, Examples of business logic vulnerabilities: "an attacker may be able to pass in a negative value". |

## C. Reviewed only when the product uses the feature
| # | When | Rule | Source (opened 23 Nov 2026) |
|---|---|---|---|
| C1 | SAML sign-in | The SAML library is on a patched release. For `ruby-saml` that means 1.12.3, or 1.17.0 and later. | GitHub Advisory GHSA-jw9c-mfg7-9rx2: "allow the attacker to log in as arbitrary user". |
| C2 | "Log in with Microsoft" | A user is matched on the token's stable ids (`tid` with `oid`, or `sub`), never on the email claim, and accounts are never merged on an unverified email. | Microsoft Learn, claims validation: "Never use claims like email, preferred_username or unique_name". |
| C3 | Authenticator codes checked in our own code | A code is refused once it has been accepted. Keep the last accepted time step per user. | IETF RFC 6238, section 5.2: "The verifier MUST NOT accept the second attempt of the OTP". |
| C4 | Our own proxy or load balancer | The proxy and the server agree on where a request ends: HTTP/2 end to end where possible, and ambiguous requests are rejected. | PortSwigger, HTTP request smuggling: "crucial that the front-end and back-end systems agree about the boundaries". |
| C5 | A CDN caches pages or API responses | A response is never built from a request header that is not part of the cache key. | PortSwigger, Web cache poisoning: "a harmful HTTP response is served to other users". |
| C6 | We encrypt cookies or tokens ourselves | Use authenticated encryption, and one generic error for any failure. | OWASP Cryptographic Storage Cheat Sheet: "GCM and CCM, which should be used as a first preference". |
| C7 | XML from users (SVG, office files, feeds) | External entities and XInclude are switched off in the parser. | PortSwigger, XXE: "it is sufficient to disable resolution of external entities". |
| C8 | WebSockets with cookie sessions | The handshake checks where the request came from and carries a per-session token. | PortSwigger, Cross-site WebSocket hijacking: "relies solely on HTTP cookies". |
| C9 | Our own HTTP/2 server or proxy | It is on a release patched for CVE-2023-44487. | Google Cloud, Oct 2023: "reached a peak of 398 million requests per second". |
| C10 | Any AI feature that reads user or outside text | That text is treated as data: the feature's tools get the least access they need, and a high-risk action needs a person's yes. | OWASP GenAI, LLM01 Prompt Injection: "user prompts alter the LLM's behavior or output in unintended ways". |

## Left out on purpose
Two rules were considered and are not here because their source could not be confirmed word for word when this file was written: comparing secrets in constant time, and limiting repeated operations inside one GraphQL request. They can be added when their sources are read.

## How the result reports it
`sec-check: pass | FAIL (<n>) | not run (<why>)`, then one line per section B and C rule that applied: the rule number, `ok` or `finding`, and the file. A rule that does not apply is not listed.
