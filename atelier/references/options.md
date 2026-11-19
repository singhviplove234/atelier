# Options — what a project can add, and when the factory offers it

Added in 0.5.0. The contracts are not optional: every build meets them. Everything on this page **is** optional — an add-on that is offered only when the project needs it, clearly benefits from it, or the user asks for it, and that is otherwise left out so a project never carries machinery it does not use (`code-simplicity.md`). This page is the single index: one row per option, who offers it, where the choice is recorded, and the one file that defines it. An option is never defined in two places — if a row points to a contract, that contract is the only definition.

## How an option is offered (the same three triggers for every row)
1. **The project requires it** — the plan's facts make it necessary (the row's "Offered when" column). The factory says so and explains why in one line.
2. **The project or the user would benefit** — the factory mentions it once, in one line, with its cost and its downside (`recommendations.md`), and takes no for an answer. It is not raised again unless the facts change.
3. **The user asks** — at any time, in any words. `/pf-setup options <slug>` shows this table with the project's current choices.
An option is **off until chosen**. Choosing one never unlocks a paid tool by itself (`cost-posture.md`), never relaxes a contract, and can be turned off again; turning one off removes its code, if it has any, on the next build rather than leaving it dormant.

## The options
| Option | Offered when | Chosen at | Recorded in | Defined in |
|---|---|---|---|---|
| Team lanes | separable areas **and** more than one seat | `/pf-plan` | `lanes` | `planning.md` §2 |
| SaaS blocks (tenancy, billing, admin…) | paying customers or organizations as customers | `/pf-plan` | the brief | `saas-blueprint.md` |
| Mobile store release | the product is a mobile app | `/pf-plan` | `deploy.target` | `mobile-release.md` |
| More than one language/region | users in more than one locale | `/pf-plan` | `brief.locales` | `i18n.md` B |
| Infrastructure as code | several cloud resources, sensitive data, or a client delivery | `/pf-plan` | `infra` | `infrastructure.md` |
| Feature flags / kill switches | an unfinished or risky feature must ship, or the client flips it | `/pf-plan` or a build | the Brief's `Flags:` | `rollout.md` A |
| Canary rollout | real users **and** a host that splits traffic | each `/pf-deploy` | `deploy.rollout` | `rollout.md` B |
| CI workflow | team or sensitive project (self-hosted), or a public repo | `/pf-plan` or `/pf-setup ci` | `ci` | `verification.md` D |
| Pentest | `data_sensitivity: high` | `/pf-pentest` | `security_testing` | `security-testing.md` |
| Status page | client-facing or paid product | `/pf-monitor` | `monitoring.status_page` | `monitoring.md` F |
| Analytics | the owner wants traffic and behaviour data | `/pf-setup seo` | set up with the user, consent-gated | `seo-ai-visibility.md` (measurement foundation) |
| Delivery to a client | the product is for someone else | `/pf-plan` or `/pf-deliver` | `delivery` | `delivery.md` |
| **Advisor model** | the user asks about usage or cost, hits usage limits, or the project is large | `/pf-setup advisor` | `options.advisor` | `advisor.md` |
| **3D product scene** | a brand/product page where the product's form is the selling point | `/pf-plan` or `/pf-setup options` | `options.scene_3d` | `scene-3d.md` |
| **Launch video** | a launch that will be promoted (ads, social, a landing hero), after go-live | `/pf-promo` | `options.launch_video`, `promo` | `launch-video.md` |
| **Growth drafts** | a live site with Search Console data and pages stuck on page two | `/pf-grow --draft` | `options.grow_drafts` | `growth.md` "Drafts" |
The four rows in bold are recorded under `factory.json.options`; every other row keeps the field it already had — this page indexes them, it does not move them.

## Rules
- **One line, once.** An offer is a single sentence with the cost and the con. No option is pushed, bundled with another, or assumed from a similar project.
- **The plan is where most are settled** (`pf-plan` §3c), so nothing optional is discovered mid-build. The bold rows can also be chosen later, because they do not change what was built before them.
- **Not offered** is as deliberate as offered: a brochure site is not asked about tenancy, a solo internal tool is not asked about a status page.
- **Every option is complete inside Atelier.** None of them asks you to install another skill or plugin; the most an option needs is an ordinary program on the build machine (for example `ffmpeg` for the launch video), and `/pf-next doctor` says so.
