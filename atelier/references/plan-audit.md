# Plan audit — Atelier's own planning rigor (self-contained)

This is the factory's **own** method for the two planning-stage checks `pf-plan` runs: the idea-stage **SWOT** pressure-test (§A) and the pre-build **11-lens audit under different roles** (§B). It lives **inside** the plugin so `pf-plan` performs both itself, at full depth, with **no external skill required** — the factory is a one-stop shop.

These methods are written to be complete on their own: framing, evidence discipline, ranking, strategy, verdict and output are all specified here, so no other tool is needed to run them.

---

## A. Idea-stage SWOT pressure-test (run at discovery, `pf-plan` §1)

A SWOT is only useful if someone can make a decision from it. The failure modes to avoid: generic bullets that would fit any idea, internal and external factors muddled together, every point weighted the same, no "so what do I do now", and flattery of the person who brought the idea. Hold every line to the opposite of those.

### A1. Frame it first
"Strength" and "weakness" mean nothing without a subject and a goal. Pin down, from the conversation or by stated inference:
- **The idea**, in one sentence.
- **The actor** — who would do this (solo founder, existing company, a team inside a larger org, an individual deciding). Strengths/weaknesses belong to the actor plus the concept.
- **The decision** this SWOT informs (go/no-go, choose between options, where to invest, how to de-risk).
- **Stage, geography, time horizon.**
If the idea is too thin to name the actor or goal, ask — at most two or three questions in one message, only ones whose answer would change the analysis. If there's enough to work with, or the user says proceed, state assumptions in the Framing block and go. Never stall a user who wants it now.

### A2. Pick depth
- **Quick** — a fast take, or a small/casual idea → the quick format at the end.
- **Standard** — the default for any real idea.
- **Deep** — the user asks for thorough, is about to commit real money/time, or wants a doc/deck → more research, quantify where possible, expand the strategy section.

### A3. Gather evidence
Opportunities and threats describe the outside world, so source them from it: with web search available, check the things that date — competitors and substitutes, market size and growth, pricing, regulation, tech shifts, recent funding or failures. Use shared files / connected data for the internal quadrants. With no search, work from general knowledge, say so, and flag the factors most likely stale.

### A4. Generate factors — four tests on every one
- **Internal vs external.** Strengths/weaknesses are what the actor controls or holds today (skills, assets, cost structure, relationships, the concept's inherent properties). Opportunities/threats are outside conditions the actor can only respond to. Quick check: "would this still be true if the actor didn't exist?" → yes means external. The classic mis-sort is writing an *action* ("we could expand to Europe") as an opportunity; the opportunity is the external condition ("European demand is unserved"), the action belongs in strategy.
- **Specificity.** "Would this bullet be equally true of a competitor's version?" If yes, sharpen until it isn't, or cut it.
- **So what.** Each factor carries its consequence: "No marketing budget" → "No marketing budget — first-year growth is capped at the founder's personal network."
- **Evidence tag.** Mark each `Fact` (verifiable/sourced), `Assumption` (plausible, untested), or `Unknown` (must be found out). Early ideas are mostly assumptions; showing that plainly is one of the most valuable things the SWOT does.
Don't pad quadrants for balance — one real strength against six real weaknesses is shown as such. For an idea that doesn't exist yet, strengths/weaknesses are what the actor brings and the concept's inherent properties, not hoped-for achievements.

### A5. Prioritize
Rate each factor's **impact** on the decision (High / Medium / Low). Keep the top three to five per quadrant, ranked, drop the rest. Flag any **make-or-break** factor — one that alone could sink or make the idea.

### A6. Turn it into strategy (TOWS)
Four lists are an inventory, not an analysis. Cross the quadrants into moves, each naming the factors it uses:
- **Pursue (S×O)** — use a strength to capture an opportunity.
- **Fix (W×O)** — shore up a weakness that blocks an opportunity.
- **Defend (S×T)** — use a strength to blunt a threat.
- **Avoid (W×T)** — where a weakness meets a threat, decide what to stay away from or exit.
One or two strong moves per pairing beats a full grid of weak ones.

### A7. Stress-test from different seats
Before presenting, reread the draft as each of these and note what they'd object to or find missing: a **skeptical investor / budget holder**; the **target customer**; the **strongest competitor** planning their response; the **operator** who delivers it daily; a **regulator or lawyer** where the domain is regulated; and **one role specific to this idea** (a channel partner, a spouse for a career move, the IT head for an internal tool). Revise factors and rankings with what surfaces; in the output report only what changed or stays contested — a few lines, not a transcript.

### A8. Verdict
End with a position: **Go / Go with conditions / Rework / Don't pursue** (or an equivalent clear read for a non-binary question), a few sentences grounded in the make-or-break factors, then: the **assumptions to validate first**, each with the *cheapest test* that confirms or kills it; and the **next three steps**. It's the user's decision, framed as a reasoned view they can disagree with — but don't hedge everything into "it depends."

### A9. Output (inline by default)
```
# SWOT: <idea in ≤10 words>
**Framing:** <what, who, the decision, horizon, assumptions made>
## At a glance   (2×2: Internal/External × Helpful/Harmful, top 3 short labels each)
## Strengths / ## Weaknesses / ## Opportunities / ## Threats
  1. **<Label>** — <what it is, why it matters>. `Fact` · Impact: High  [**(make-or-break)** where it applies]
## Strategic moves   Pursue (S×O) / Fix (W×O) / Defend (S×T) / Avoid (W×T)
## Stress test   <what changed or stays contested>
## Verdict: <Go / Go with conditions / Rework / Don't pursue>  + reasoning
**Validate first** — <assumption> → <cheapest test>
**Next steps** — 1, 2, 3
```
**Quick format:** Framing line + the 2×2 + Verdict (2–3 sentences) + next three steps; run the stress test silently. Cite sources for anything from search. Be straight: acknowledge what's good and be equally direct about what could kill it; critique the idea, never the person. Where a regulated area is touched (financial, health, food, legal, data privacy, import/export), name the regulatory factor in the right quadrant and note professional advice is needed — don't give definitive legal/tax conclusions. 

### A10. Factor-generation bank (use in A4 to get past obvious bullets)
Skim the quadrant probes every time; read only the idea-type lens that applies.

**Strengths** — what does the actor have a well-funded newcomer couldn't get within a year (expertise, relationships, data, reputation, licences, IP)? what's structurally cheaper/faster/better than how the problem is solved today? an existing audience or distribution to start from? what's already proven (paying customers, a prototype, a track record)? how long can they self-fund?
**Weaknesses** — which critical skill is missing from the team (sales, technical, regulatory, ops)? where does it depend on one person/supplier/customer/platform? do the unit economics work at small scale? what would a competitor attack first? what does this require them to do well that they've never done? how much time can they really give it?
**Opportunities** — what changed recently (tech, regulation, behaviour, costs, demographics) that makes this timely *now*? which segment is underserved/overcharged/ignored? are incumbents distracted, slow, disliked, exiting? adjacent markets/geographies/partnerships once the core works? public money, grants, favourable policy?
**Threats** — who already does this and what happens when they notice; how copyable is it? what substitute (including doing nothing) does the customer use, and how strong is the habit? which platform/supplier/regulator could change one rule and break the model? how sensitive is demand to economy/FX/seasonality? what makes the timing wrong (too early, too late)? the customer-acquisition reality (crowded channels, rising ad costs, long cycles)?

**Idea-type lenses** — *startup:* founder-market fit, first ten customers, unit economics, runway, defensibility, why-now (make-or-break is usually distribution + is-the-problem-painful-enough-to-pay). *New product inside a company:* S/W are the company's (customers, brand permission, eng capacity, channel fit); add cannibalization + internal competition for resources. *Market/geo expansion:* what transfers vs not (brand, approvals, pricing power, supply chain, local partners, culture, FX/tax); entry mode. *Services/agency:* differentiation in a crowded field, founder-network dependence, utilisation/bench, client concentration, hiring/retention, offshore price pressure. *Physical product:* manufacturing + MOQs, working capital in inventory, certification/labelling, shelf life, shipping/returns, channel margins, brand cost. *Side hustle:* the scarce resource is the person's time; day-job conflict, scale-without-them, opportunity cost. *Career/personal:* actor is the individual; non-financial values count. *Partnership/acquisition/investment:* strategic fit, what each side truly brings, integration effort, dependence created, exit options. *Internal project:* sponsorship, budget cycles, competing initiatives, change fatigue, compliance deadlines. *Nonprofit/public:* funding sustainability + impact over revenue; donor/grant dependence, volunteer capacity, community trust.

**Common mis-sorts** — "launch a mobile app" (action, not a condition → the opportunity is "users are mobile-first and incumbents have no app"; the launch is a strategic move) · "huge growing market" as a strength (external → Opportunities) · "limited funding" as a threat (internal → Weaknesses) · "competitors are well funded" as a weakness (external → Threats) · "we'll have the best support" as a strength (a hope → cut or restate what exists today) · "the idea might fail" as a threat (name the specific external cause).
**Sharpen generic → specific** — "experienced team" → "founder spent 8 years selling to hospital procurement, can reach the first 20 buyers directly"; "growing market" → "category +~18%/yr on a 2025 rule change forcing SMEs to file digitally (source)"; "limited budget" → "6 months personal runway, must reach paying customers before any hire". If a factor can't be sharpened for missing information, keep it, tag `Unknown`, and add it to *Validate first*.

### A11. Variations
- **Several ideas at once** — a compact SWOT each, then a comparison table (top strength, biggest risk, verdict, effort to validate) and a recommended priority order.
- **User brings their own SWOT** — review it with the four tests in A4 (mis-sorted / generic / missing / unevidenced), then supply what's absent (prioritization, TOWS, verdict) rather than rewriting from scratch.
- **Existing business or product** (not a new idea) — everything applies; lean harder on real data for the internal quadrants.
- **Follow-ups** — when new information arrives or a factor is disputed, update the affected factors, rankings and verdict, not the whole analysis.

---

## B. Eleven-lens pre-build audit (run before plan sign-off, `pf-plan` §7)

The real pre-build gate, and the "audit under different roles before publishing" discipline built into the stage. The goal: **no gap survives the audit** — nothing that later forces a rebuild, a security incident, a missed regulatory obligation, a cost blowout, or a product nobody wants. Delivered inline unless a doc is asked for.

### B0. Operating rules
1. **Read the whole input first** — the architecture, requirements, MVP and stack decision end to end; a one-line idea is audited for its unstated assumptions (a thin input produces *more* findings, not fewer).
2. **Never invent facts about the system.** If the plan doesn't say which datastore it uses, that's a finding (an unknown), not a blank to fill.
3. **Every finding is falsifiable** — state what's missing/wrong, the concrete consequence, and the specific fix. "Improve error handling" is not a finding; "no idempotency key on the payment-submit endpoint → a client retry after a 504 double-charges → add an `Idempotency-Key` header persisted 24h" is.
4. **Find gaps and prescribe fixes; don't rewrite the plan.** The fix is a prescription the team executes.
5. **Say when a lens is clean** — one line. Padding a lens with generic advice destroys the signal of the lenses that found something.
6. **Don't stop at the plan's framing.** If it proposes the wrong solution to the stated problem, say that first, before auditing the details of the wrong solution.

### B1. Classify the input (one short block)
Artifact type (idea / PRD / architecture / integration spec / mixed) · stage (concept, pre-build, in-build, pre-launch) · stakes (internal tool, client-facing delivery, regulated/data-sensitive, revenue-critical) · **what it claims to deliver, restated in one sentence** — if you can't restate it, that's finding #1. Stakes and stage set the bar: a concept note isn't held to a production-runbook standard; a client-facing data-sensitive delivery is held higher. This step also sets `brief.data_sensitivity` (`normal`/`high`).

### B2. Run the eleven lenses — each a separate reader with a separate agenda
Don't let one lens soften another (the security architect doesn't care the deadline is tight). For a large/complex plan, fan the lenses out in parallel with the Agent tool (one agent per lens or cluster), then merge and de-duplicate; for a short input, run inline.

1. **Technology Director** — alignment to business strategy; build vs buy vs partner; three-year TCO, not three-month; who owns it after launch; does the team actually have the skills; what does this foreclose; what if the key vendor re-prices or is acquired; a measurable success definition with an accountable owner.
2. **Product Owner** — the user problem and the evidence for it; who the user is and what they do today instead; v1 scope in and explicitly out; testable acceptance criteria; rollout and adoption plan; sunset/migration for whatever this replaces; which "requirements" are assumptions in disguise; success in numbers at 30/90/180 days.
3. **Senior Developer** — buildable as written? where would two developers build two different things? the hard parts glossed over — error handling, retries, idempotency, partial failure, concurrency, ordering, pagination, timeouts, backpressure; data contracts and versioning; test strategy (unit / integration / contract / only-in-prod); local dev and test-data story; where the first production bug comes from.
4. **Solution Architect** — boundaries, coupling, cohesion, blast radius; system-of-record for each entity and where it's duplicated; sync vs async and what breaks when a dependency is *slow* not down; consistency model vs what the business rules tolerate; the first bottleneck and the load at which it bites; failure modes and degradation path; integration patterns (for API/integration work: layered API design, governance, reuse, rate limits, bulk vs real-time, error handling at each layer); migration/cutover; the exit strategy from each major tech choice.
5. **Cyber Security Architect** — threat model: who attacks this and how (walk STRIDE across the trust boundaries); authN and authZ at every entry point including service-to-service; secrets management and rotation; data classification, encryption at rest and in transit, key ownership; tenant isolation; session/token lifetime and revocation; input validation and injection surfaces; supply chain (dependencies, base images, build provenance); logging that's enough for forensics without capturing secrets/PII; **account-recovery, password-reset and email-change flows as a top takeover path** (`security.md`); the single worst realistic breach and whether the design contains it. This lens decides whether a **deep** security pass is warranted later.
6. **UI/UX Expert** — who uses it, in what context, on what device, under what pressure; primary flows and step counts; error / empty / loading / offline / partial-data states (almost always missing); accessibility to **WCAG 2.2 AA** (contrast, keyboard path, focus order, screen-reader semantics, target size — `design-standard.md`); information hierarchy and "what do I do next"; onboarding/first-run; copy that explains failures in actionable terms; i18n/l10n if relevant; the most likely moment a user abandons.
7. **Site Reliability Engineer** — SLIs/SLOs and error budget; availability target and whether the architecture supports it; observability enough to answer "is it broken and why" at 3am; actionable (not noisy) alerting; capacity and load (peak vs average, growth); backup and restore *tested* not just configured, with RTO/RPO numbers; DR / region failure; runbooks for the top five failure modes; on-call ownership; the weekly manual toil and whether it can be automated (`monitoring.md`, `deploy-rule.md`).
8. **DevOps Engineer** — environment parity; infrastructure as code (anything hand-built?); CI/CD build, test gates, artifact promotion, approvals; deploy strategy (blue/green, canary, rolling) and a *rehearsed* rollback; DB migration strategy including backward-compatible deploys and rollback-with-schema-changes; config and secrets per environment; feature flags; release cadence and change management; **free-first cost controls, tagging, and who sees the bill** (`cost-posture.md`).
9. **DevSecOps Engineer** — pipeline security gates (SAST, DAST, SCA/dependency scan, container and IaC scan, secret scan on commit); the policy when a scan fails (block or warn, who can override); patch/vuln SLA by severity; SBOM; signed artifacts and provenance; least-privilege for the pipeline itself (the CI runner is a high-value target — credential isolation, `security.md` rule 16); drift detection; an audit trail from commit to production.
10. **AI/ML Engineer & Architect** — *run whenever the plan involves AI/ML/LLMs/agents/automated decisioning; otherwise write "n/a" and move on.* Is ML the right tool or would rules be cheaper and more predictable; data availability, quality, labeling, volume, licensing and rights; train/serve skew; a baseline to beat; evaluation (offline metrics, a golden set, an online measure tied to the business outcome); drift monitoring and retraining trigger. For LLM systems: prompt-injection and tool-abuse surface, grounding/retrieval quality, hallucination handling, output validation, human-in-the-loop for consequential actions, token cost and latency at expected volume, model-version pinning and migration, fallback when the provider is down; guardrails, bias testing, explainability where a decision affects a person; who is accountable for a wrong automated decision.
11. **Data & Compliance Reviewer** *(mandatory every audit)* — what personal data is collected, why, on what lawful basis, retained how long; data residency (where it lives and transits) — apply explicitly for **India (DPDP Act)**, **US (state privacy + sectoral rules)**, and **GDPR** where EU subjects are involved, calling out cross-border transfer mechanisms and localization for India–US workloads; consent, withdrawal, and data-subject rights (access, correction, erasure, portability) — can the architecture honor an erasure request; sectoral obligations if relevant (HIPAA, PCI-DSS, SOC 2, ISO 27001, FedRAMP); subprocessor/DPA chain; breach-notification timelines and who declares; retention and deletion actually implemented; the audit evidence that proves each control works (`compliance.md`).

### B3. Score every finding — three tags
- **Severity:** `BLOCKER` (don't start building — proceeding means rework, legal exposure, or an unrecoverable design choice) · `HIGH` (resolve before launch, can run parallel to build) · `MEDIUM` (first iteration after launch; document the accepted risk if deferred) · `ADVISORY` (worth doing, no material risk if skipped).
- **Impact** — one line on what concretely goes wrong unfixed ("an authenticated user can read another tenant's invoices", not "security risk").
- **Cost & effort of the fix** (not the feature) — rough engineering effort (hours/days/weeks), any recurring cost, and whether fixing later costs materially more than now. Say "unknown — depends on X" rather than invent a number.

### B4. Unknowns register
Every question the plan can't answer goes in an explicit register: the question (stated so it has a definite answer) · **who must answer it** (client, product, security, legal, vendor, the team) · what's blocked until then · a reasonable default to proceed on, marked clearly as a default. An empty register on a real plan means the audit wasn't thorough — recheck.

### B5. Verdict
A direct call: **Ready to build / Ready with conditions / Not ready — resolve blockers first / Wrong approach — reconsider**; the shortest path to ready (the fixes ordered to unblock the most work); and **the one thing most likely to sink this that nobody in the plan is currently worried about.** Fold every gap into the brief before sign-off.

### B6. Output (inline)
```
## Audit: <plan name>   <artifact type> · <stage> · <stakes>
What it proposes: <one sentence, restated>
### Verdict  <Ready / Ready with conditions / Not ready / Wrong approach> + 2–3 sentences
### Blockers (N)   **B1 — <title>** · <lens> · <effort, cost> — Gap / Impact / Fix
### High (N)        **H1 — <title>** · <lens> · <effort, cost> — …
### Medium & Advisory   <one–two lines each, grouped by lens>
### Clean lenses   <lenses that found nothing material, one line each>
### Unknowns register   | # | Question | Owner | Blocks | Default if unanswered |
### Shortest path to ready   1, 2, 3
### The thing nobody is worried about yet   <one paragraph>
```
Scale to the input — a one-paragraph idea gets the same sections, shorter; never drop the verdict, the unknowns register, or the blockers.

### B7. Self-check before folding gaps in
- Would a skeptical practitioner in each role agree their concerns were represented, or say "you missed the obvious one"?
- Is every finding specific enough to action tomorrow without a follow-up question?
- Is any finding actually an assumption I invented rather than a real gap?
- Did I rank by real risk, or by how easy each was to write?
- Is there a BLOCKER hiding in the MEDIUM pile because it was uncomfortable to call?
- If this ships exactly as planned, what breaks first — and did I say so?

---

## C. Hard-decision council (only for a real fork — never routine)

Most planning choices have a clear answer once the facts are on the table, and convening a debate for them wastes the user's time. A council is for the rare decision that is **expensive to reverse and honestly contested**: which platform to commit to, build versus buy, go or no-go after a mixed SWOT, one product or two. If a reasonable person could decide it in a minute, do not run this.

### C1. Frame the question
One sentence, phrased as a choice between named options (two to four). State what is already fixed, what the decision will cost to undo, and the date by which it must be made. If the options are not really different, say so and stop.

### C2. Seat five advisers — each argues from one agenda and is not allowed to be balanced
1. **The operator** — who has to run this every day; what breaks at 3 a.m.; what it costs to staff.
2. **The customer** — what the person paying for it will actually notice, and what they will never forgive.
3. **The accountant** — total cost over three years, cash timing, what is sunk, what is still optional.
4. **The sceptic** — the strongest case that every option on the table is wrong, and what is being assumed without evidence.
5. **The builder** — what is truly hard to build, what is hard to change later, and what the team has never done before.
Each adviser writes a short position: the option they back, the single best reason, the evidence it rests on, and what would change their mind. Positions are written independently — an adviser does not see the others first.

### C3. Cross-examine
Each adviser reads the others and answers one question: *which claim here is weakest, and why?* Claims that nobody can support with evidence are struck out, whichever option they favoured. Disagreements that remain after this are the real ones; list them plainly rather than smoothing them over.

### C4. Chair's ruling
A sixth voice, with no agenda, writes the ruling: the recommended option; the two or three reasons that survived cross-examination; the strongest remaining objection, stated fairly; what would have to be true for the other option to win; and the cheapest experiment that would settle it, if one exists. The recommendation is one option, not a blend, unless a blend is itself a named option.

### C5. Output
```
## Decision: <the question>
Recommended: <option> — <one sentence>
Why (survived cross-examination): 1 · 2 · 3
Strongest objection: <stated fairly>
Would flip if: <condition>
Cheapest test first: <experiment, or "none — decide now">
Where the advisers still disagree: <one line each>
```
The user decides. The council informs the decision; it never makes it, and it never overrides the cost posture or a contract.

---

## The rule
Atelier owns these three methods and runs them itself, in full, with nothing else installed: the same framing, evidence discipline, ranking, strategy, scoring, unknowns register, verdict and self-check on every plan. They are part of the planning contract (`planning.md`), not an add-on.
