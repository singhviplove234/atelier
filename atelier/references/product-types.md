# Product types — what changes when the product is not a website

Added in 2.2.0. The factory's stages, gates and contracts were written with a website or web app in mind. They hold for every other kind of product too; what changes is what a "screen", a "deploy" and a "health check" mean. This file is the single definition of those differences. The type is recorded once, at plan time, in `factory.json.brief.product_type`, and copied into the SPEC's Brief as a `Type:` line.

## The types
| `product_type` | What it is | Ships through |
|---|---|---|
| `web` (default) | a site or web app in a browser | any web target (`deploy-rule.md`) |
| `mobile` | an app in the App Store / Google Play | `expo-eas`, `flutter-stores` (`mobile-release.md`) |
| `extension` | a browser extension | `chrome-web-store` |
| `desktop` | an installed app for Windows, macOS or Linux | `desktop-release` |
| `api` | a service other software calls; no screens of its own | a container or serverless web target |
| `cli` | a command-line tool or a library others install | `package-registry` |
| `agent` | software whose core is an AI model acting with tools, on a schedule or on events | a container or scheduled-job web target |
A product can be two things (a web app with a public API, an agent with a dashboard): record the main type, and the second one's section below still applies to that part.

## What never changes
The plan, design and deploy gates and their approval words; the nine SPEC headings; diagrams before design and code; `npm run verify` (or the stack's equivalent single command) with a pre-push hook; tests that include a failure path; `security.md`; `code-simplicity.md`; the docs set; `cost-posture.md`; secrets as names, never values. A heading that does not apply is written with one line saying why — never deleted.

## Browser extension (`extension`)
- **Plan.** Which browsers (Chrome and Edge take the same package; Firefox needs its own manifest keys and store; Safari needs a Mac, Apple's converter and a paid developer account — say so, it is not automated). The store's one-time registration fee (read the current figure on the store's page). Review takes days and can reject: name it in the timeline.
- **Design.** Screens are the popup, the options page, the side panel and anything drawn into a web page. Every one gets an artboard and a diagram like any screen.
- **Build.** Manifest V3. Under the SPEC's *Routes / API* list every permission and host with the one sentence that justifies it; ask for the narrowest host pattern, and request optional permissions at the moment of use. No remotely hosted code. Content scripts run isolated, touch only what the feature needs, and never read form fields or page content the feature does not use. Messages between parts are validated like any untrusted input.
- **Verify.** e2e loads the unpacked build in a Chromium persistent context and drives the real popup and a real test page. A content script is measured on a test page with and without the extension: no visible layout shift, no measurable slow-down.
- **Deploy.** Upload as a draft; publishing is the owner's click. The store listing needs a privacy policy URL and a truthful data-use disclosure — both come from `compliance.md` and the companion site.
- **Harden.** Performance = popup opens instantly and pages are not slowed. SEO and AI visibility apply to the companion site and the store listing text, not to the extension. Security review adds: permissions still minimal, no secrets in the package (it is public by nature).

## Desktop app (`desktop`)
- **Plan.** Shell: a small native-webview shell (Tauri) when the app is mostly its interface; a bundled-browser shell (Electron) when it needs that ecosystem — state the size and memory difference. **Signing is the real cost:** unsigned installers show security warnings on Windows and are blocked on macOS. A Windows signing certificate and Apple's developer programme are paid and belong to the owner — read the current prices on their pages before the plan is approved, and offer "unsigned, for testers only" as the free path. macOS builds need a Mac.
- **Design.** Screens as usual, plus the first-run, the update prompt, the offline state and the tray or menu if any.
- **Build.** The interface layer never gets direct system access: context isolation on, node integration off (or the shell's equivalent), and a short allowlist of named commands between interface and system. Local data: say where it is stored, how it is backed up, and how it is removed on uninstall. Auto-update only from signed releases over HTTPS.
- **Verify.** e2e drives the built app where the shell supports it; where it does not, e2e runs on the web layer and a smoke test launches the packaged app and checks `--version`.
- **Deploy.** Installers are built locally, per operating system, and attached to a draft release; publishing is the owner's click (`targets/desktop-release.md`).
- **Monitor.** Crash and error reports only with the user's consent, with no file paths or personal data. Uptime monitoring applies to the update feed and any backend, not to the app.

## API (`api`)
- **Plan.** Who calls it, how they authenticate, the expected volume, and whether it is public.
- **Design.** There are no artboards. *Screens* holds one line saying so, plus the reference documentation page, which is designed like any page. The design step produces the **OpenAPI description** instead; it is approved at the design gate and is the contract.
- **Build.** Versioned from day one (`/v1`). Keys are shown once, stored hashed, scoped, and revocable. Every write accepts an idempotency key. Lists are paginated. Errors use one documented shape. Rate limits are set and returned in headers. Documentation is generated from the OpenAPI description, never hand-copied.
- **Verify.** Contract tests are generated from the OpenAPI description and stand in for e2e; each endpoint has a success and a failure test (bad key, bad input, over the limit).
- **Deploy / monitor.** A web target that runs a server. Health check is the health route. Monitor p95 latency and error rate, not page views.
- **Harden.** No page performance budget; instead a latency budget per endpoint, set in the plan. SEO applies only to the documentation site.

## Command-line tool or library (`cli`)
- **Design.** The "screens" are the commands: for each, the exact `--help` text, an example run and its output are written at design time and approved like copy. Output for people goes to stderr, data to stdout; `--json` where another program may read it; exit code 0 only on success.
- **Build.** No network call the user did not ask for, and no usage reporting without an explicit opt-in. Configuration lives where the operating system expects it. No install-time scripts.
- **Verify.** e2e runs the built tool against fixture folders in a temporary directory, including a wrong-argument and a missing-file path.
- **Deploy.** The package is built and tested from the packed file; publishing to the registry is the owner's action (`targets/package-registry.md`). Versions follow semantic versioning; a breaking change is a major version and a changelog entry.

## AI agent or automation (`agent`)
- **Plan.** The job in one sentence. What it may read and what it may change (the tool allowlist). **What needs a person's approval** — by default anything that sends, spends, deletes, publishes or cannot be undone. A spending cap per run and per month. What starts it (a schedule, an event, a person). Which model, pinned to a version. A model API is a billed service: `cost-posture.md` applies and the owner approves the cap.
- **Design.** The flow diagram is the design: every decision, every tool call, every approval point, every failure exit. Plus the screens where a person sees what it did and approves what it proposes.
- **Build.** The **evaluation set comes first**: at least twenty real cases with the expected outcome, including cases where the right answer is to stop or ask, and cases where the input tries to give it instructions. Tools get the narrowest credentials that work. Everything the agent reads from outside (pages, mail, files, tool results) is data, never instructions. Model output that drives an action is parsed against a schema and rejected when it does not fit. Every action is idempotent or guarded against repeats, has a dry-run mode, and is logged with its inputs and result — without secrets or personal data. A kill switch (`rollout.md` A) stops it at once.
- **Verify.** The evaluation set runs in `verify`; the pass rate and its floor are recorded in the build result, and any change to a prompt, a tool or the model re-runs it. A drop below the floor fails the build.
- **Monitor.** Runs succeeded and failed, cost per run against the cap, approvals waiting and for how long. Reaching the cap stops the agent and alerts the owner; it never raises its own cap.
- **Never.** Act irreversibly without the approval the plan requires; claim an accuracy that the evaluation set did not measure; send a user's data to a model provider beyond what the privacy notice says.

## Which harden passes apply
| Pass | web | mobile | extension | desktop | api | cli | agent |
|---|---|---|---|---|---|---|---|
| Safety-net tests | yes | yes | yes | yes | contract tests | yes | evaluation set |
| Performance budget | yes | start-up time | popup and page impact | start-up time | latency budget | start-up time | cost and time per run |
| SEO and AI visibility | yes | companion site | companion site and listing | companion site | docs site | readme and registry page | companion site |
| Security review | yes | yes | yes, plus permissions | yes, plus isolation | yes, plus keys and limits | yes, plus supply chain | yes, plus tools and injection |
| Load test | yes | backend | backend | backend | yes | no | queue or schedule backlog |
| Hosting limits | yes | backend | backend | update feed | yes | no | yes, plus model spend |
