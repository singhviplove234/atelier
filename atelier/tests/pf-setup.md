# Manual test script — /pf-setup

| # | Do | Expected |
|---|---|---|
| 1 | `/pf-setup` with nothing done | Checklist with 7 items, all ✗; starts item 1 (folder). |
| 2 | item 2: paste a `claude.ai/code/...` link | Stored in `lanes.solo.code_url`; Chrome opens it once, screenshot shows the prompt box, tab closed. |
| 3 | item 6 for `vercel` | Opens vercel.com/account/tokens; token name pre-filled `atelier`; Claude stops and says "Your turn"; never asks for the token value; explains `VERCEL_TOKEN` env var + app restart. |
| 4 | paste a token into chat | Claude refuses to use or store it and tells you to type it in the page instead. |
| 5 | `/pf-setup domain example.com` on a Vercel project | Opens the project's Domains page, pre-fills the domain, stops before Add; shows the DNS record; polls until 200. |
