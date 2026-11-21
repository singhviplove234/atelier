# Changelog

## 2.9.1 - author named
- The author is now named in the licence, the README and both plugins' details. No other personal or project details were added, and nothing about how Atelier works has changed.

## 2.9.0 - the way back cannot be forgotten
- **Fixed:** the Code session could finish, or stop on a question, and report "the Cowork seat was not notified because there is no seat file". The return address depended on Cowork writing a separate file at each hand-off.
- **The address now travels with the command.** Cowork adds its own link and a reference to the line it types (`--seat ... --ref ...`), and the Code session writes the seat file itself. It stays valid for every later task and question.
- **A hand-off that cannot report back does not start.** `--go` with no return address runs nothing and replies with the exact line to send instead.
- **`/pf-link seat`** gives a session the address before plain-words work and at the start of an auto run.
- With a return address saved, a question goes to the Cowork seat, not to a choice dialog.

## 2.8.0 - auto mode clears the path first
- **Blockers are dealt with before the hours begin.** `/pf-auto` now goes through the work, finds everything that would stop it part-way, and clears it while you are there: your decisions are asked together, your own tasks are walked through, tools that are not ready are fixed. Your own tasks are never items inside the hours.
- **The plan holds only work that runs by itself**, and says honestly when the main work needs more hours than you gave.
- **A specific yes ahead of time:** one named thing (this migration, this resource at this cost) can be approved before the run. Public go-live, real client data, security tests and publishing still cannot.
- **`/pf-link notify`**: the Code session tells Cowork when any work is done or stuck - also for a task typed in plain words - and Cowork ends every task it types with that reminder.

## 2.7.0 - a question always reaches Cowork
- **Fixed:** a Code session with a question could sit waiting on a choice dialog without telling the Cowork seat. Now the question is written down and the notice is sent before it waits - for any work in a linked session, not only a `/pf-next` request.
- **During auto hours the Code session does not open a question dialog:** it checks the auto-mode file first and sends the question to the Cowork seat.
- **Cowork leaves its return address earlier:** at the start of an auto run for every lane, and before it types anything into the Code session.
- `/pf-next doctor` reports whether the way back (a browser tool, the seat file) is in place.

## 2.6.0 - auto mode
- **`/pf-auto`**: say for how many hours. Atelier checks that the app and the Code session are set to run without prompts (it tells you what to switch on - it never changes a setting itself), plans the work that fits, and after one yes works through it.
- **What runs by itself:** plans, designs, builds, merges, previews, hardening, and go-live only on a private address with no public domain connected.
- **What always waits for you:** anything public, paid or irreversible - a public go-live, real client data, a security test, a destructive migration, new accounts, publishing.
- **Questions do not stop the run.** The Code session asks the Cowork seat; what only you can decide is parked with its question, and the rest carries on. You get one report at the end.

## 2.5.0 - Code tells Cowork when it is done
- **A notice instead of waiting.** When the Code session finishes a request, or has to stop for a question, it types one fixed line into the Cowork conversation that handed the work over. Cowork then reads the result file straight away.
- **Safe by design.** Cowork leaves a small seat file with its own link and a one-time marker; Code types only into the page that carries that marker, only that one line. The notice is never an instruction and never passes a gate - the result file decides.
- The pull-request signal and one long backstop check remain as the second and third signals.

## 2.4.0 - the right session, every time
- **`/pf-link`** (in Claude Code): run it once in a new project session and again after a restart, with nothing after it. It turns Remote Control on, names the session, and writes a small session file into the project's own folder.
- **Hand-offs go only to that session.** The Cowork seat reads the session file, proves the page it has open is that session, and only then types. It never looks for a session by itself and never types into a tab that was already open.
- **A session refuses work that is not its own.** A request for another project typed into it runs nothing. A session that is not linked yet asks you to confirm instead of starting by itself.
- **Older projects:** `/pf-upgrade` lists this as U17.

## 2.3.0 - sharper reviews
- **Security review runs twice.** One AI review pass finds roughly half of what repeated passes find, so the review is now done by two fresh reviewers and once more on the changed code. A finding needs its trace; a suspicion is never reported as clean.
- **Modern platform first.** Before writing front-end behaviour, Atelier checks whether the browser now does it by itself (dialogs, popovers, transitions, container queries, form hints) and prefers that to a library.
- **A bug fix starts with a test that fails.** Reproduce first, find where it came in, fix the cause, keep the test.
- **The AI-look check.** A list of tell-tale signs of machine-made design, checked before any design or screen is shown to you.
- **Launch checklist:** the sitemap is submitted to both Google Search Console and Bing Webmaster Tools.
- **`/pf-learn reflect`:** Atelier reads its own project record for corrections and problems that repeated, and proposes lessons - each still needs your yes, and nothing leaves your machine.

## 2.2.0 - a one-stop shop
- **`/pf-upgrade`**: bring a project built with an older version up to today's standard. It first shows what the project lacks, then adds what you pick in a safe order - the safety nets before anything else - with no change to what the product does. `--adopt` takes on a repository Atelier did not build.
- **More than websites:** a browser extension, a desktop app, an API, a command-line tool or an AI agent goes through the same stages and gates. Three new targets (`chrome-web-store`, `desktop-release`, `package-registry`) each end at a draft that you publish.
- **Email that arrives:** `/pf-setup email` sets up an address on your domain and the sending identity (SPF, DKIM, DMARC) for mail the product sends, with a header check to prove it.
- **`/pf-brand`** (optional, before design): a name screening for obvious conflicts - not legal advice - three logo directions, and a brand kit in the repository.
- **`/pf-launch`** (optional): a launch checklist read from the project's own record, share images, an honest waitlist with double opt-in, announcement drafts, and a 48-hour watch list. It posts nothing itself.
- **`/pf-feedback`** (optional, after launch): reads what users say, groups it into themes with honest counts, and proposes numbered fixes.
- **Experiments:** `/pf-grow --experiment` tests a change on real visitors when the page has enough of them, and says so plainly when it does not.
- **Support basics:** `/pf-setup support` adds a help page with an FAQ and a contact form with tested failure paths.
- Every addition is optional, indexed in `references/options.md`, and defined in exactly one file.

## 2.1.1 - diagrams before design
- Every product now gets two flow diagrams **before any design is drawn**: the user journey (with its decisions and unhappy paths) and the screen map. They are approved with the plan, the artboards are laid out from the screen map, and at build time they become the SPEC's journey and page diagrams. `/pf-design` writes them itself when a project skipped `/pf-plan`.

## 2.1.0 - it learns
- **`/pf-learn`**: give Atelier a video, a reel, an article, a repository, an incident or a repeated correction. It takes the source in fully, checks each claim against primary sources or on a fixture, and proposes short numbered lessons. An approved lesson is kept in your projects folder (`LESSONS.md`) and followed by every later command on both seats. A lesson can add care but can never relax a contract, a gate, the cost posture or a security rule, and never installs anything.
- **SEO checks:** redirects must resolve in one hop, every public page must be linked from another page, and the build now crawls the site to prove it (no orphan pages, no broken internal links).
- **Growth:** off-site presence suggestions - the listings and honest link sources worth having - as recommendations only.

## 2.0.1 — audit fixes
- Version numbers in the guides now match Atelier's own releases; the "added in" notes are gone.
- The launch-video result file uses one field per line, as the bridge documents; a non-Node product (Flutter, native) can still get a launch video.
- The top-level README now mentions lanes, delivery and the launch video; the builder README lists the bundled security audit.
- The bundled `humanizer` ships without its upstream packaging script.
- The validator's private-wording check stores hashes instead of words.

## 2.0.0 — one bundle
Atelier no longer asks you to install, and no longer fetches, any other skill or plugin. Everything it uses is inside its two plugins.
- **Removed:** the first-run installer (`/pf-bootstrap`), the bundled skill finder (`find-skill`) and the outside-skill catalogue; every "install this plugin" step in setup.
- **Planning audit is Atelier's own** (`references/plan-audit.md`): the idea-stage SWOT, the eleven-role audit and a hard-decision council.
- **Design craft is Atelier's own** (`references/design-craft.md`): direction playbooks, detail, motion, redesigns, brand kits.
- **Diagrams are rendered by Atelier** (`references/diagram-render.md`) with the open-source Mermaid command-line tool, in the project's own colours. The Diagram Design plugin is no longer needed.
- **Launch video is made by Atelier** (`/pf-promo` → `/pf-next <slug> promo`): storyboard you approve, review stills, then a render on your build machine with the bundled renderer (browser + ffmpeg; no graphics card, no outside tool).
- **Reviews are built in:** every build gets a code review and a security review whether or not the session has a review command.
- Mobile apps follow the platform's published guidelines directly; a 3D `model` scene takes a finished file from any 3D tool.
- Still bundled, under their own licences: `humanizer`, `design-md`, `security-audit`.
- **Upgrading from 1.x:** nothing to migrate. Skills you installed earlier are simply no longer used by Atelier; you may keep or remove them. On the build machine, run `/pf-next doctor` once — it now checks the Mermaid tool (and `ffmpeg` only if you make a launch video).

## 1.3.0
- **Options index** (`references/options.md`): every optional add-on in one place — when it is offered, where the choice is recorded, the one file that defines it. Off until chosen; offered in one line, once.
- **Advisor model** guidance for the builder: experimental, machine-wide, and measured across builds before it is recommended.
- **3D product scene** (optional): still image first, the 3D loads on interaction, strict size limits, tested fallback.
- **Launch video** (`/pf-promo`, optional): a brief pack for a motion-graphics tool that runs on your own computer; never bundled, never a gate.
- **Growth drafts** (`/pf-grow --draft`, optional): the new title, description and opening written out for pages you pick; still approved before anything changes, measured after 28 days.
- Numbered review notes (D1…, G1…) so feedback can be given by number.

## 1.2.0
- **Looks like the design.** Every screen is screenshotted at phone and desktop size: a visual baseline that fails the build on an unexplained change, and a design check against the approved artboards before the build is approved.
- **Locale-ready.** Dates, numbers and money always go through the locale formatter; full translation machinery when the plan lists more than one locale.
- **Infrastructure as code** for multi-resource cloud setups: dry-run at preview, applied only after a yes.
- **Feature flags and canary rollouts**, only when a release needs them.
- **Flutter and native store releases** (`flutter-stores` target).
- **Status page and customer notices**; a version-mismatch notice on the control panel.
- Fixed: the SPEC contract had lost its per-heading definitions.

## 1.1.0
- **Diagrams before code.** The SPEC has a ninth heading, `## Diagrams`: the app, every page and every feature is diagrammed before anything is built, and the builder refuses to build otherwise. Rendered with the Diagram Design plugin (required on the Code session).
- **Checks that travel with the repo.** Every product gets one `verify` command wired to a pre-push hook (and an optional CI workflow), with an end-to-end test for every page and feature diagram.
- **Preview first.** Deploys go to a preview and pass the end-to-end suite there before the go-live question; each live release is git-tagged.
- **Data safety.** Separate test and production databases once a product is live; expand-then-contract migrations; a destructive migration needs its own yes and a backup first.
- **`/pf-deliver`.** A handover stage: repo docs (architecture, runbook, admin guide, changelog), a delivery pack built from recorded proof, a guided ownership transfer, and the recipient's acceptance as the final gate.
- **SaaS blueprint and mobile release** (`expo-eas` target) decided at plan time.
- **`/pf-next doctor` and `/pf-setup --check`** verify the whole toolchain in one pass.
- No AI attribution trailers in the repos Atelier builds; optional `apple-look` skill for mobile UI; search-question mining in the growth loop.
