# Feature flags and gradual rollout — only when a release needs them

Added in 0.4.0. Most projects need neither: preview-first deploys, e2e tests and auto-rollback already make an ordinary release safe (`deploy-rule.md`). A flag or a gradual rollout is added when the plan or a build names a reason — an unfinished feature that must merge to `main`, a risky change to a product with real users, or a client who wants to switch something on themselves. Free-first: no paid flag service.

## A. Feature flags
1. **One typed list, in the repo.** `flags.ts` (or the stack's equivalent): each flag has a name, a default (**off**), an owner, the date it was added and a **remove-by date**. Values come from the host's environment/config, so flipping a flag is a config change, not a code change — and the previous value is the rollback. (On a fully static site the value is read at build time, so a flip is a redeploy of the same commit; say so in the runbook.)
2. **Evaluated on the server.** The client is told the result, never the rule. **A flag is never the security boundary**: the route behind a hidden feature still checks auth and role (`security.md`) — hiding a button protects nothing.
3. **Both states are tested.** Every flag adds its on-path to the feature's e2e test and keeps the off-path passing; `verify` runs both. A flag whose off-state is broken fails the build.
4. **Kill switches are flags too.** Anything that calls a paid or fragile third party (payments, email, AI) may get a kill switch; each one is listed in `docs/RUNBOOK.md` "When something breaks" with the exact config name to flip.
5. **Flags expire.** Once a flag has been fully on (or off) in production past its remove-by date, `/pf-maintain` lists it as stale and the next build deletes the flag and the dead branch. A flag list only grows by decision, never by neglect.
6. **Per-user targeting** (a percentage, a named tester list) is done by hashing a stable user id against the percentage in code. No personal data leaves the app for it.

## B. Gradual rollout (canary)
Chosen per deploy with the request's `rollout:` line — `full` (default) or `canary`. Canary means: the new version takes a small share of real traffic, is watched, then takes the rest.
| Target | How a canary runs |
|---|---|
| `azure-container-apps` | the preview revision takes 10% (`az containerapp ingress traffic set … --revision-weight <new>=10 <previous>=90`), then 100% |
| `gcp-cloud-run` | `gcloud run services update-traffic … --to-tags preview=10`, then `preview=100` |
| every other target | no traffic splitting on the free tier — a canary is done with a percentage **flag** (A6) around the change, or the release goes `full` |
A canary needs a previous live version to share traffic with, so a product's **first** deploy is always `full`. Steps: 10% → **bake** (the monitoring bake window, at least 15 minutes for a canary, watching error rate and latency against the previous version) → 100%. A regression at 10% sends traffic back to the previous version automatically and records `rolled_back: yes`; nothing is retried without a new yes. The go-live question names the rollout: "Deploy now — as a 10% canary first?".
**Migrations do not canary.** The database is shared by both versions, which is exactly why migrations are expand-then-contract (`migrations.md` B): the expand step must be safe for the old version before any canary starts.

## C. Checks
A flag without owner, default or remove-by date fails the gate; a flag read in client code as the only guard on a protected route fails the security gate; both states covered by e2e; kill switches listed in the runbook. Result line: `flags: <n> (<k> stale)`.

## Never
- Gate a security or billing decision on a client-side flag.
- Leave a canary at a partial percentage unattended past its bake window.
- Add a paid flag or experimentation service without a stated price and a yes.
