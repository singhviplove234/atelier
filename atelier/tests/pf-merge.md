# Manual test script — /pf-merge

| # | Setup | Do | Expected |
|---|---|---|---|
| 1 | seat with `pm: false` | `/pf-merge --lane frontend` | Refuses: PM seat only. |
| 2 | lane `frontend` status `ok`, `pr_url` set | `/pf-merge --lane frontend` | Shows PR + acceptance; asks "Merge lane/frontend into main?"; on yes writes `MERGE-REQUEST-frontend.md`, drives Chrome, polls. |
| 3 | `MERGE-RESULT-frontend.md` with `status: ok` | (poll) | `lanes.frontend.status == merged`; if all lanes merged → `gates.build == approved` and "run /pf-deploy". |
| 4 | reply `looks good` to the merge question | — | Asks again with yes/no; nothing merged. |
