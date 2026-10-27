# Manual test script — /pf-lanes

| # | Setup | Do | Expected |
|---|---|---|---|
| 1 | fresh solo project | `/pf-lanes list` | One row: `solo · main · code_url ✗ · idle`. |
| 2 | solo, no requests | `/pf-lanes add frontend backend` | Asks "Convert to a team project?"; on yes `solo` removed, two lanes added with `lane/<name>` branches; reminder to run `/pf-setup` per seat. |
| 3 | lane `frontend` has a newer `BUILD-RESULT-frontend.md` with `status: ok` but status `building` | `/pf-lanes status` | Row shows `ok`; "Ready to merge: frontend". |
| 4 | lane `backend` status `requested` | `/pf-lanes remove backend` | Refuses: not idle/merged. |
