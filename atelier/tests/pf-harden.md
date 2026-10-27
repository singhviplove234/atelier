# Manual test script — /pf-harden

| # | Setup | Do | Expected |
|---|---|---|---|
| 1 | seat is not `pm_lane` | `/pf-harden` | Refuses: PM lane only. |
| 2 | `gates.build == pending` | `/pf-harden` | Refuses: build not approved. |
| 3 | deploy ok, `live_url` set | `/pf-harden --dry-run` | Prints `HARDEN-REQUEST.md` with all six passes; writes nothing; asks nothing. |
| 4 | same | `/pf-harden` | Plain-language explanation, then "Harden <slug> now?"; on Yes writes request, drives Chrome with `/pf-next <slug> harden --go`, polls every 5 min. |
| 5 | `HARDEN-RESULT.md` with `status: ok`, `budget_met: yes` | (poll) | Shows before/after speed table, indexes, caching, load summary, limits with prices, `needs_decision` as "Paid — your call"; asks "Merge + redeploy?". |
| 6 | result has `needs_decision: Redis ~US$16/month` | — | Listed only; nothing created; no Redis in the PR. |
| 7 | `live_url` empty | `/pf-harden` | Says results are indicative (local copy) and continues. |
| 8 | request says `passes: perf` | — | Builder still runs `safety` first. |
| 9 | builder result `budget_met: no` | (poll) | `status: failed` path: shows misses, offers rerun / "tell me what to fix". |
| 10 | passes include `seo` | (poll) | SEO table shown per route; any page failing crawler fetch or SEO < 100 → status failed with the route named. |
| 11 | design brief lacks `Questions:` | `/pf-build` | Asks for the SEO inputs before writing the SPEC; never invents them. |
| 12 | passes include `security` | (poll) | Security table shown; RLS isolation test failing or a missing header → status failed with the check named; attack tooling never run. |
| 13 | product handles payments | security pass | Adds a plain "what a human pentester should still look at" note. |
