# Experiments — testing a change on real visitors before keeping it

Added in 2.2.0. Optional (`options.md`), part of the growth loop: offered by `/pf-grow --experiment` when a growth item is a guess worth checking. Recorded in `factory.json.options.experiments` (`off` / `on`) and one entry per test in `factory.json.experiments[]`. It adds no new machinery: a variant is a feature flag (`rollout.md` A).

## When it is offered — and when it is not
- The product is live, analytics is set up with consent, and the page gets **enough visitors to finish in four weeks**. Work out the number first (below).
- When there are not enough visitors, say so and offer the plain alternative: ship the change and compare the same weeks before and after — weaker evidence, and described as that.
- Never for: prices shown differently to different people (unless the owner explicitly asks, knowing the risk), legal, consent, security or sign-in flows, or anything that works by confusing or pressuring the visitor.

## One experiment
| Part | Rule |
|---|---|
| Hypothesis | "Because <the signal>, changing <one thing> will raise <the metric> by at least <the smallest lift worth having>." One change per experiment. |
| Primary metric | One, chosen before the start, counted per visitor. |
| Guardrails | One or two things that must not get worse (errors, refunds, unsubscribes). A breach stops the test. |
| Split | Half and half, decided on the server, the same for a visitor every time, no flicker. A visitor who has not consented to analytics sees the original and is not counted. |
| Sample | Per variant, about `16 × p × (1 − p) ÷ d²`, where `p` is today's rate and `d` the absolute lift to detect (95% confidence, 80% power). State the number and the weeks it needs at current traffic. |
| Length | Whole weeks, at least one, at most four. |

## While it runs
No peeking for a winner and no early stop for a good-looking lead; stop early only for a guardrail breach or a bug. One experiment per page at a time. Variants share one URL with the same canonical tag and the same content for search engines (`seo-ai-visibility.md`).

## The result
Reported with the numbers and the interval: **keep the change**, **keep the original**, or **no clear difference** — which is a real result and means keep the original. The losing code and the flag are removed in the next build (`rollout.md` — a stale flag is a failure). Record `{ id, hypothesis, metric, start, end, sample, result }`; experiments are numbered X1, X2 …

## The builder's part
Only when the SPEC's Brief has an `Experiment:` line: the flag, the server-side assignment keyed on an anonymous id, one assignment event and one conversion event (consent-gated), both variants covered by e2e. Reports `experiment: <id> running | removed`.
