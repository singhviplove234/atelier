"""Second-pass validator: cross-references, mirrored contracts, fixtures gate, feature wiring, and no personal data."""
import json, os, re, subprocess, sys, tempfile
C, B = "atelier", "atelier-builder"
n_ok = n_bad = 0
def ok(m):
    global n_ok; n_ok += 1; print("PASS", m)
def bad(m):
    global n_bad; n_bad += 1; print("FAIL", m)
def check(cond, m): (ok if cond else bad)(m)
def read(p): return open(p, encoding="utf-8").read()
def has(p, pat, flags=0):
    check(os.path.exists(p) and re.search(pat, read(p), flags) is not None, f"{p} contains /{pat}/")
def hasnt(p, pat):
    check(not re.search(pat, read(p)), f"{p} is free of /{pat}/")

# --- 1. manifests
ver = {}
for p in (C, B):
    f = f"{p}/.claude-plugin/plugin.json"
    try: d = json.load(open(f)); ver[p] = d["version"]; check(d["name"] == p, f"{f} name")
    except Exception as e: bad(f"{f}: {e}")
check(len(set(ver.values())) == 1, f"both plugins share one version {ver}")

# --- 2. every skill: frontmatter name == folder, description, size
skills = {}
for p in (C, B):
    for s in sorted(os.listdir(f"{p}/skills")):
        f = f"{p}/skills/{s}/SKILL.md"
        if not os.path.exists(f): bad(f"{f} missing"); continue
        t = read(f); skills[s] = p
        m = re.match(r"---\nname: (\S+)\ndescription: (.+?)\n(?:.*?\n)?---\n", t, re.S)
        check(bool(m) and m.group(1) == s, f"{f} frontmatter name matches folder")
        if s not in ("security-audit", "humanizer", "design-md", "find-skill"):
            check(bool(m) and len(m.group(2)) <= 1024 + 2, f"{f} description within 1024 chars")
            check(len(t.split()) < 3900, f"{f} under 3900 words ({len(t.split())})")

# --- 3. cross-references resolve
refs = {p: set(os.listdir(f"{p}/references")) for p in (C, B)}
targets = {p: {x[:-3] for x in os.listdir(f"{p}/references/targets")} for p in (C, B)}
for p in (C, B):
    for root, _, files in os.walk(p):
        if "security-audit" in root: continue
        for fn in files:
            if not fn.endswith(".md"): continue
            f = os.path.join(root, fn); t = read(f)
            for r in set(re.findall(r"references/([a-z0-9-]+\.md)", t)):
                # the builder may point at the Cowork plugin's references by name
                local = os.path.exists(os.path.join(os.path.dirname(f), "references", r))
                check(r in refs[p] or r in refs[C] or local, f"{f} -> references/{r} exists")
            for r in set(re.findall(r"`([a-z0-9-]+\.md)`", t)):
                if r in refs[C] | refs[B]: continue
                if r in ("verify.yml", "brief.md", "rules.md", "storyboard.md") or not re.match(r"[a-z]", r): continue
                if r[:-3] in targets[C]: continue
                bad(f"{f} names `{r}` which is not a reference file")
            for cmd in set(re.findall(r"(?<![\w/-])/(pf-[a-z-]+)", t)):
                check(cmd in skills, f"{f} -> /{cmd} is a skill")
            for tg in set(re.findall(r"targets/([a-z0-9-]+)\.md", t)):
                check(tg in targets[C], f"{f} -> target {tg} exists")

# --- 4. mirrored contracts are byte-identical
for r in sorted(refs[B]):
    if r == "targets": continue
    check(r in refs[C] and read(f"{C}/references/{r}") == read(f"{B}/references/{r}"), f"references/{r} identical in both plugins")
check(targets[C] == targets[B], "target registries list the same targets")
for tg in sorted(targets[C]):
    a, b = f"{C}/references/targets/{tg}.md", f"{B}/references/targets/{tg}.md"
    check(os.path.exists(b) and read(a) == read(b), f"targets/{tg}.md identical in both plugins")
    t = read(a)
    order = [h for h in re.findall(r"^## (.+)$", t, re.M)]
    check(order == ["Fits", "Env vars", "Preview", "Deploy steps", "Health check", "Custom domain"], f"targets/{tg}.md has the six sections in order")
rule = read(f"{C}/references/deploy-rule.md")
for tg in sorted(targets[C]): check(f"`{tg}`" in rule, f"deploy-rule.md lists target {tg}")

# --- 5. SPEC contract + fixtures (positive and negative)
sf = read(f"{C}/references/spec-format.md")
body = re.sub(r"```\n# <Project name>.*?```\n", "", sf, count=1, flags=re.S)
heads = re.findall(r"^## (.+)$", body, re.M)
skel = re.search(r"```\n# <Project name>\n\n(.*?)```", sf, re.S)
check(bool(skel) and [l[3:] for l in skel.group(1).strip().split("\n")] == ["Brief", "Stack", "Screens", "Tokens", "Components", "Data model", "Routes / API", "Diagrams", "Acceptance checks"], "spec-format.md skeleton lists the nine headings")
for h in ("Brief", "Stack", "Screens", "Tokens", "Components", "Data model", "Routes / API", "Diagrams", "Acceptance checks"):
    m = re.search(rf"^## {re.escape(h)}\n(.+)$", body, re.M)
    check(bool(m) and len(m.group(1)) > 40, f"spec-format.md defines what goes under ## {h}")
NINE = ["Brief", "Stack", "Screens", "Tokens", "Components", "Data model", "Routes / API", "Diagrams", "Acceptance checks"]
check(heads == NINE, "spec-format.md lists the nine headings in order")
for fx in ("landing", "app"):
    f = f"atelier-builder/tests/fixtures/{fx}/SPEC.md"
    r = subprocess.run([sys.executable, "-I", "tests/spec_gate.py", f], capture_output=True, text=True)
    check(r.returncode == 0, f"{f} passes the Diagrams gate ({r.stdout.strip()[:80]})")
    t = read(f); cut = re.sub(r"```mermaid\n%% id: page-[a-z]+\n.*?```\n", "", t, count=1, flags=re.S)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tmp: tmp.write(cut)
    r = subprocess.run([sys.executable, "-I", "tests/spec_gate.py", tmp.name], capture_output=True, text=True)
    check(r.returncode != 0, f"{f} with one page diagram removed FAILS the gate")
    os.unlink(tmp.name)

# --- 6. no secrets, no stale wording
blob = ""
for p in (C, B):
    for root, _, files in os.walk(p):
        for fn in files:
            if fn.endswith((".md", ".json")): blob += read(os.path.join(root, fn))
check(not re.search(r"(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36}|eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{10,})", blob), "no secret-looking values")
for p in (C, B):
    for root, _, files in os.walk(p):
        if "security-audit" in root: continue
        for fn in files:
            if fn.endswith(".md"):
                f = os.path.join(root, fn)
                if re.search(r"eight headings|all eight", read(f)): bad(f"{f} has stale wording")
ok("no stale 'eight headings' wording") if True else None

# --- 7. feature wiring (each line = a promise the docs make somewhere else)
BB, BD, BN = f"{B}/skills/pf-build-from-spec/SKILL.md", f"{B}/skills/pf-deploy-from-spec/SKILL.md", f"{B}/skills/pf-next/SKILL.md"
S = lambda n: f"{C}/skills/{n}/SKILL.md"; R = lambda n: f"{C}/references/{n}.md"
# 0.2.0: diagrams gate, attribution, token-light
has(BB, r"## 1b\. Diagrams gate"); has(BB, r"references/diagram-render\.md"); has(BB, r"@mermaid-js/mermaid-cli --version"); has(BB, r"failures: no diagram for")
has(BB, r'"attribution"'); has(BB, r"includeCoAuthoredBy"); hasnt(BB, r"~/.claude/settings.json`\s*\(create")
has(S("pf-build"), r"Token-light"); has(S("pf-deploy"), r"Token-light"); has(S("pf-setup"), r"0b2\.")
has(R("skills"), r"never asks you to install another skill or plugin"); has(R("growth"), r"includingRegex|Questions:")
# 0.3.0: verify + e2e from diagrams
has(R("verification"), r"^## A\. One command", re.M); has(R("verification"), r"// diagram: <id>"); has(R("verification"), r"failure path")
has(BB, r"npm run verify"); has(BB, r"e2e/<id>\.spec"); has(BB, r"takes its failure path"); has(BB, r"\.githooks/pre-push"); has(BB, r"core\.hooksPath")
has(BB, r"runs-on: self-hosted"); has(BB, r"references/delivery\.md"); has(BB, r"Never choose `self-hosted` or `hosted` yourself"); has(BB, r"^verify: pass\|fail", re.M)
has(R("bridge"), r"^verify: pass\|fail", re.M); has(R("bridge"), r"^ci: hook \| self-hosted \| hosted", re.M); has(R("bridge"), r"^live: yes", re.M)
has(S("pf-build"), r"ci: <factory\.json\.ci>"); has(S("pf-build"), r"`live: yes` \*\*only\*\*"); has(S("pf-build"), r"npm run verify exits 0")
has(R("state-schema"), r'"ci": "hook"'); has(S("pf-setup"), r"/pf-setup ci <slug>")
# 0.3.0: docs gate + delivery
has(BB, r"## 6b\. Docs gate"); [has(BB, d) for d in (r"docs/ARCHITECTURE\.md", r"docs/RUNBOOK\.md", r"docs/ADMIN-GUIDE\.md", r"CHANGELOG\.md", r"When something breaks")]
has(S("pf-deliver"), r"gates\.delivery"); has(S("pf-deliver"), r"AskUserQuestion"); has(S("pf-deliver"), r"scoped token"); has(S("pf-deliver"), r"restore_tested")
has(S("pf-deliver"), r"Never click Transfer"); has(R("delivery"), r"rotate after transfer"); has(R("state-schema"), r'"delivery": "pending"')
has(S("pf-ship"), r"7\. \*\*Deliver\*\*"); has(R("control-panel"), r"Delivered"); has(f"{C}/README.md", r"/pf-deliver")
# 0.3.0: preview first + live tag
has(R("deploy-rule"), r"^## Preview first", re.M); has(BD, r"## Stage: preview"); has(BD, r"E2E_BASE_URL"); has(BD, r"X-Robots-Tag: noindex"); has(BD, r"live-<yyyymmdd-HHMM>")
has(R("bridge"), r"^stage: preview \| live", re.M); has(S("pf-deploy"), r"## 3b\. Preview first"); has(R("state-schema"), r'"preview_url"')
# 0.3.0: data safety
has(R("migrations"), r"Expand, then contract"); has(R("migrations"), r"PROD_"); has(BB, r"single database"); has(BB, r"-- destructive:")
has(BD, r"destructive_ok"); has(BD, r"no recent backup"); has(S("pf-deploy"), r"destructive_ok"); has(S("pf-setup"), r"/pf-setup database <slug>"); has(R("state-schema"), r'"database": "single"')
hasnt(R("deploy-rule"), r"prefer backward-compatible")
# 0.3.0: SaaS + mobile + doctor + stack-neutral backups
has(R("saas-blueprint"), r"across two organizations"); has(S("pf-plan"), r"saas-blueprint\.md"); has(S("pf-build"), r"saas-blueprint\.md")
has(R("mobile-release"), r"owner's click"); has(S("pf-plan"), r"mobile-release\.md"); has(f"{C}/references/targets/expo-eas.md", r"never run a command that releases to production")
has(BN, r"/pf-next doctor"); has(R("bridge"), r"PF-DOCTOR-RESULT v1"); has(S("pf-deploy"), r"ends at the store test track"); has(BN, r"PF-DOCTOR-RESULT v1"); has(S("pf-setup"), r"/pf-setup --check"); has(R("maintenance"), r"Another data store, same three rules")
has(R("monitoring"), r"When an alert fires")
# 0.4.0: locales, rollout, infrastructure, visual baseline + design check, Flutter stores, versions notice, status page
has(R("i18n"), r"Intl\.NumberFormat"); has(R("i18n"), r"needs-review"); has(BB, r"references/i18n\.md"); has(S("pf-plan"), r"brief\.locales"); has(R("state-schema"), r'"locales": \["en-US"\]'); has(S("pf-deploy"), r"needs-review")
has(R("rollout"), r"never the security boundary"); has(R("rollout"), r"Migrations do not canary"); has(BB, r"references/rollout\.md"); has(BD, r"rollout: canary"); has(R("bridge"), r"^rollout: full \| canary", re.M); has(R("state-schema"), r'"rollout": "full"')
has(R("infrastructure"), r"what-if"); has(R("infrastructure"), r"\*\*Never automated:\*\* `destroy`"); has(BB, r"never apply it here"); has(BD, r"Never run a destroy"); has(BD, r"infra_ok"); has(S("pf-deploy"), r"infra_ok"); has(R("bridge"), r"^infra: bicep \| opentofu \| compose", re.M); has(R("state-schema"), r'"infra": "none"'); has(S("pf-build"), r"infra: <factory\.json\.infra>")
has(R("verification"), r"^## F\. What the screens look like", re.M); has(R("verification"), r"toHaveScreenshot"); has(BB, r"e2e/__screenshots__/"); has(BB, r"never re-baseline an unexplained difference"); has(S("pf-build"), r"Design check before asking for approval"); has(R("bridge"), r"^screens: <n> checked", re.M)
has(f"{C}/references/targets/flutter-stores.md", r"never run a command that releases to production"); has(R("mobile-release"), r"flutter-stores\.md"); has(S("pf-setup"), r"flutter-stores")
has(R("control-panel"), r"Factory version line"); has(S("pf-board"), r"DOCTOR-RESULT\.md"); has(R("monitoring"), r"^## F\. Status page", re.M); has(S("pf-monitor"), r"## 3b\. Status page"); has(R("monitoring"), r"never posts an incident notice"); has(R("state-schema"), r'"status_page"')
hasnt(R("mobile-release"), r"not automated yet")
# 0.5.0: options index, advisor, 3D scene, launch video, growth drafts, numbered notes
has(R("options"), r"off until chosen"); has(R("options"), r"never defined in two places"); has(S("pf-plan"), r"references/options\.md"); has(S("pf-setup"), r"/pf-setup options <slug>"); has(R("state-schema"), r'"options": \{ "advisor": "none"')
for row, ref in (("Advisor model","advisor.md"),("3D product scene","scene-3d.md"),("Launch video","launch-video.md"),("Growth drafts","growth.md"),("Canary rollout","rollout.md"),("Status page","monitoring.md"),("Infrastructure as code","infrastructure.md")):
    has(R("options"), rf"{row}.*`{re.escape(ref)}`")
has(R("advisor"), r"machine"); has(R("advisor"), r"no percentage"); has(R("advisor"), r"experimental"); has(S("pf-setup"), r"/pf-setup advisor"); has(S("pf-setup"), r"Never claim a saving"); has(BB, r"^model: <this session", re.M); has(R("bridge"), r"^model: <main model>", re.M); has(BN, r"advisorModel")
has(R("scene-3d"), r"250 KB gzipped"); has(R("scene-3d"), r"1\.5 MB"); has(R("scene-3d"), r"failure path"); has(BB, r"references/scene-3d\.md"); has(S("pf-build"), r"`3D scene:` line"); has(R("performance-budget"), r"scene-3d\.md")
has(R("launch-video"), r"render-video\.mjs"); has(R("launch-video"), r"storyboard"); has(S("pf-promo"), r"deploy\.live_url"); has(S("pf-promo"), r"AskUserQuestion"); has(S("pf-promo"), r"never a gate|Treat this as a gate"); has(S("pf-ship"), r"Optional add-ons are not stages"); has(R("state-schema"), r'"promo": \{')
has(R("growth"), r"^## Drafts", re.M); has(R("growth"), r"28 days"); has(R("growth"), r"five pages per run"); has(S("pf-grow"), r"--draft"); has(S("pf-grow"), r"Publish a draft")
has(S("pf-build"), r"D1, D2"); has(R("growth"), r"G1, G2")
# an option is defined once: the four new contracts are not restated in other references
for other in ("verification","deploy-rule","design-standard","monitoring","planning","rollout","infrastructure","i18n"):
    hasnt(R(other), r"250 KB gzipped|advisorModel|brief pack")
# standing safety rules still present
has(S("pf-setup"), r"Never type"); has(S("pf-ship"), r"never flips `gates\.delivery`"); has(BN, r"never.* skips confirm|never skips the confirm", re.S)

# --- 7b. one bundle: nothing points outside Atelier for a skill or plugin
PF = f"{B}/skills/pf-promo-from-spec/SKILL.md"
for gone in (f"{C}/skills/pf-bootstrap", f"{C}/skills/find-skill", f"{C}/references/skill-catalog.md"):
    check(not os.path.exists(gone), f"{gone} is gone")
for need in (R("plan-audit"), R("design-craft"), R("diagram-render"), f"{B}/references/diagram-render.md", f"{B}/references/launch-video.md", f"{B}/scripts/render-video.mjs", PF):
    check(os.path.exists(need), f"{need} exists")
for shared in ("diagram-render.md", "launch-video.md"):
    check(read(f"{C}/references/{shared}") == read(f"{B}/references/{shared}"), f"{shared} identical in both plugins")
has(R("plan-audit"), r"^## A\b", re.M); has(R("plan-audit"), r"^## B\b", re.M); has(R("plan-audit"), r"^## C\b", re.M)
has(S("pf-plan"), r"plan-audit\.md` section A"); has(S("pf-plan"), r"plan-audit\.md` section B"); has(S("pf-plan"), r"section C"); has(S("pf-design"), r"design-craft\.md")
has(PF, r"^name: pf-promo-from-spec$", re.M); has(PF, r"PF-PROMO v1"); has(PF, r"PF-PROMO-RESULT v1"); has(PF, r"scripts/render-video\.mjs"); has(PF, r"Never merge `promo` into `main`")
has(BN, r"promo → `pf-promo-from-spec`"); has(BN, r"PROMO-REQUEST\.md"); has(BN, r"PF-PROMO v1"); has(BN, r"ffmpeg -version"); has(BN, r"@mermaid-js/mermaid-cli --version")
has(R("bridge"), r"^PF-PROMO v1$", re.M); has(R("bridge"), r"^PF-PROMO-RESULT v1$", re.M); has(S("pf-promo"), r"/pf-next <slug> promo")
has(BB, r"\*\*Review pass \(always\):\*\*"); has(BB, r"\*\*Plan-first \+ self-verify \(always\):\*\*")
has("THIRD-PARTY-NOTICES.md", r"Nothing else is installed or fetched")
OUTSIDE = (r"diagram[- ]design|superpowers|apple-look|blender|motion design|claude-mem|graphify|find-skill|pf-bootstrap|skill-catalog|"
           r"swot-analysis|tech-doc-audit|llmcouncil|impeccable|design-taste|gpt-taste|emil-design|brandkit|remove-ai-marks|context_tooling|"
           r"official sources?\b|/plugin (?:marketplace add|install) (?!singhviplove234/atelier|atelier@atelier|atelier-builder@atelier)|"
           r"skills\.sh|npx skills|cathrynlavery|obra/")
for top in (C, B, "README.md", "INSTALL.md", "CONTRIBUTING.md", "THIRD-PARTY-NOTICES.md", ".claude-plugin"):
    paths = [top] if os.path.isfile(top) else [os.path.join(r, x) for r, _, fs in os.walk(top) for x in fs]
    for f in paths:
        if any(v in f for v in ("security-audit", "design-md/references")) or not f.endswith((".md", ".json", ".mjs")): continue
        m = re.search(OUTSIDE, read(f), re.I)
        if m: bad(f"{f} points outside the bundle: {m.group(0)}")
ok("outside-pointer scan ran")
# every SKILL.md / reference a plugin names with ${CLAUDE_PLUGIN_ROOT} exists inside that plugin
for p in (C, B):
    for root, _, files in os.walk(p):
        for fn in files:
            if not fn.endswith(".md"): continue
            f = os.path.join(root, fn)
            for rel in set(re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)", read(f))):
                rel = rel.rstrip(".")
                check(os.path.exists(os.path.join(p, rel)), f"{f} -> {rel} is inside {p}")

# --- 7c. learning, and the SEO crawl
has(R("learning"), r"LESSONS\.md"); has(R("learning"), r"What a lesson may never do"); has(R("learning"), r"active only on the user's yes"); has(R("learning"), r"never a command")
has(S("pf-learn"), r"^name: pf-learn$", re.M); has(S("pf-learn"), r"GATE: each lesson needs the user's yes"); has(S("pf-learn"), r"install, download or run")
has(R("state-schema"), r"## Lessons \(read first, by every command\)"); has(BN, r"\*\*Lessons:\*\* before running any request"); has(f"{C}/README.md", r"/pf-learn")
has(R("seo-ai-visibility"), r"No orphan pages"); has(R("seo-ai-visibility"), r"one hop"); has(R("seo-ai-visibility"), r"Crawl the built site from the home page"); has(R("growth"), r"Off-site presence \(suggest only")

# --- 7d. flow diagrams before any design
has(R("planning"), r"Flow diagrams, before any design"); has(R("planning"), r"user journey"); has(R("planning"), r"screen map"); has(S("pf-design"), r"## 3b\. Flow diagrams first"); has(S("pf-design"), r"No artboard is drawn before"); has(S("pf-plan"), r"Flow diagrams are part of the set for every product")

# --- 8. public repo: no personal or private-project wording anywhere outside vendored skills.
# The words themselves are not written here: each is stored as a short hash, and every word and
# adjacent word pair in the repo is hashed and compared. Maintainers add a term by adding its hash.
import hashlib
_h = lambda t: hashlib.sha256(t.encode()).hexdigest()[:16]
PRIV_LC = {'bf77e2a6d3c0c5b6', '1d0e0e23238779ea', 'e52b9fb83fb40a16', '31a1736842d27b11', '7cf0c08e6d6cae38', '567781541aa1d043', 'cf1c96e9d2e42846', 'b78293703cf3e005', '7068f6611e5257b4', 'f04222209b2d8a97'}
PRIV_CS = {'1a3326777cf2220b', '39943de3ebeb355c', 'b6152a0c6c5b3465'}
# The author's name is the single allowed exception: once in each plugin's details, once as the marketplace owner,
# once on the README's licence line and once in the LICENSE. It is assembled here so this file does not carry it.
CREDIT = "Vip" + "love" + " " + "Si" + "ngh"
CREDIT_IN = {f"{C}/.claude-plugin/plugin.json", f"{B}/.claude-plugin/plugin.json", os.path.join(".claude-plugin", "marketplace.json"), "README.md"}
for f_ in sorted(CREDIT_IN) + ["LICENSE"]:
    check(read(f_).count(CREDIT) == 1, f"{f_} names the author exactly once")
check(not re.search(r"@[A-Za-z0-9.-]+\.[a-z]{2,}", read("LICENSE")) and "http" not in read("LICENSE"), "LICENSE carries a name only: no email, no address")
for top in (C, B, "README.md", "INSTALL.md", "CONTRIBUTING.md", "CHANGELOG.md", "THIRD-PARTY-NOTICES.md", "tests", ".claude-plugin"):
    paths = [top] if os.path.isfile(top) else [os.path.join(r, x) for r, _, fs in os.walk(top) for x in fs]
    for f in paths:
        if any(v in f for v in ("security-audit", "design-md", "humanizer")) or not f.endswith((".md", ".json", ".sh", ".py", ".mjs")): continue
        txt_ = read(f)
        if f in CREDIT_IN: txt_ = txt_.replace(CREDIT, "", 1)      # the one author credit; any second mention is still caught
        toks = re.findall(r"[A-Za-z0-9]+", txt_); low = [t.lower() for t in toks]
        comp = {t.lower() for t in re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+", txt_)}
        hit = (any(_h(t) in PRIV_CS for t in set(toks)) or any(_h(a + " " + b) in PRIV_CS for a, b in set(zip(toks, toks[1:])))
               or any(_h(t) in PRIV_LC for t in set(low) | comp) or any(_h(a + " " + b) in PRIV_LC for a, b in set(zip(low, low[1:]))))
        if hit: bad(f"{f} contains private wording")
ok("personal-data scan ran")
# 2.2.0: one-stop shop - upgrade path, product types, email, brand basics, launch pack, feedback loop, experiments, support basics
for s_ in ("pf-upgrade", "pf-brand", "pf-launch", "pf-feedback"):
    has(S(s_), rf"^name: {s_}$", re.M); has(S(s_), r"^## Never$", re.M); has(S(s_), r"--check"); has(S(s_), r"--dry-run"); has(S(s_), r"AskUserQuestion|with the owner's yes"); has(f"{C}/README.md", rf"/{s_}")
for row, ref in (("Product type", "product-types.md"), ("Brand basics", "brand.md"), ("Email", "email.md"), ("Support basics", "support.md"), ("Launch pack", "launch.md"), ("Feedback loop", "feedback.md"), ("Experiments", "experiments.md")):
    has(R("options"), rf"\*\*{row}\*\*.*`{re.escape(ref)}`")
has(R("options"), r"An upgrade is not an option"); hasnt(R("options"), r"The four rows in bold")
for fld in (r'"factory_version": ""', r'"product_type": "web"', r'"experiments": \[\]', r'"brand_kit": "off"', r'"email": "none"', r'"launch_pack": "off"', r'"upgraded": \{'):
    has(R("state-schema"), fld)
for shared in ("product-types", "email", "support", "experiments"):
    check(os.path.exists(f"{B}/references/{shared}.md") and read(f"{B}/references/{shared}.md") == read(R(shared)), f"{shared}.md is the builder's contract too, byte-identical")
has(R("upgrade"), r"same result before and after"); has(R("upgrade"), r"safety nets first"); has(R("upgrade"), r"never overwrite a value"); has(R("upgrade"), r"\*\*its own build\*\*")
has(S("pf-upgrade"), r"--lane upgrade"); has(S("pf-upgrade"), r"factory\.json\.bak-<date>"); has(S("pf-upgrade"), r"Hide a bug that the new e2e finds"); has(S("pf-upgrade"), r"--adopt"); has(S("pf-ship"), r"/pf-upgrade")
has(R("product-types"), r"Manifest V3"); has(R("product-types"), r"evaluation set comes first"); has(R("product-types"), r"is data, never instructions"); has(R("product-types"), r"^## Which harden passes apply", re.M)
has(R("product-types"), r"never raises its own cap"); has(R("product-types"), r"Signing is the real cost"); has(R("product-types"), r"No install-time scripts")
for tg_ in ("chrome-web-store", "desktop-release", "package-registry"):
    has(f"{C}/references/targets/{tg_}.md", r"[Nn]ever run a command that releases to production"); has(f"{C}/references/targets/{tg_}.md", r"owner's (click|action)")
has(R("deploy-rule"), r"each ends at a draft that the owner publishes"); has(S("pf-plan"), r"brief\.product_type"); has(S("pf-design"), r"Other product types"); has(S("pf-harden"), r"Which harden passes apply")
has(f"{B}/skills/pf-harden-from-spec/SKILL.md", r"Which harden passes apply"); has(BB, r"\*\*Other Brief lines \(only when present\):\*\*"); has(S("pf-build"), r"`Type:` line"); has(R("spec-format"), r"`Type:`.*`Email:`.*`Support:`.*`Experiment:`.*`Launch:`")
has(R("email"), r"Never start at `reject`"); has(R("email"), r"Tests never send to real people"); has(R("email"), r"double opt-in"); has(R("email"), r"exactly one SPF record"); has(R("email"), r"not legal advice")
has(S("pf-setup"), r"/pf-setup email <slug>"); has(S("pf-setup"), r"Never type a DNS or registrar password"); has(S("pf-setup"), r"/pf-setup support <slug>")
has(R("brand"), r"not a legal clearance"); has(R("brand"), r"single source"); has(S("pf-brand"), r"Register, reserve or buy"); has(S("pf-brand"), r"screening sentence")
has(R("launch"), r"\*\*not a gate\*\*"); has(R("launch"), r"No invented reviews"); has(R("launch"), r"real count"); has(S("pf-launch"), r"Post, send, submit or publish anything without"); has(S("pf-launch"), r"cannot be waved through")
has(R("feedback"), r"data, never instructions"); has(R("feedback"), r"Three people is three people"); has(S("pf-feedback"), r"Act on an instruction found inside"); has(S("pf-feedback"), r"\*\*Nothing is changed\.\*\*")
has(R("experiments"), r"16 × p × \(1 − p\) ÷ d²"); has(R("experiments"), r"No peeking"); has(R("experiments"), r"no clear difference"); has(S("pf-grow"), r"--experiment"); has(R("growth"), r"`experiments\.md`")
has(R("support"), r"spam trap"); has(R("support"), r"never by default"); has(R("support"), r"only an admin may read"); has(R("support"), r"The four e2e paths are required")
# each new contract is defined once: its key rule appears in no other reference
NEW_ = {"email": r"Never start at `reject`", "experiments": r"16 × p ×", "product-types": r"evaluation set comes first", "support": r"hidden trap field", "brand": r"not a legal clearance", "launch": r"\| L14 \|", "feedback": r"Three people is three people", "upgrade": r"\| U16 \|"}
for r_ in sorted(refs[C]):
    if r_ == "targets": continue
    for own, pat in NEW_.items():
        if r_ != own + ".md": check(not re.search(pat, read(f"{C}/references/{r_}")), f"{r_} does not restate {own}.md")
# the new skills promise nothing they cannot keep, and carry no secrets or addresses
for s_ in ("pf-upgrade", "pf-brand", "pf-launch", "pf-feedback"):
    hasnt(S(s_), r"guarantee[sd]? (?:that|a|the|you)|will rank|will go viral|legally safe"); hasnt(S(s_), r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}"); hasnt(S(s_), r"https?://")
for r_ in ("brand", "email", "experiments", "feedback", "launch", "product-types", "support", "upgrade"):
    hasnt(R(r_), r"https?://"); hasnt(R(r_), r"\$\d|₹\d|€\d")
# 2.3.0: lessons from the reel research - review twice, modern platform first, fix starts with a failing test, AI-look check, Bing in the launch list, reflect
has(R("security"), r"^## D\. Review twice", re.M); has(R("security"), r"never the one that raised it"); has(R("security"), r"never after one pass"); has(f"{B}/skills/pf-harden-from-spec/SKILL.md", r"runs \*\*twice\*\*")
has(R("code-simplicity"), r"^## Modern platform first", re.M); has(R("code-simplicity"), r"\*\*Baseline\*\*"); has(R("code-simplicity"), r"no drive-by rewrites")
has(R("verification"), r"^## G\. A bug fix starts with a test that fails", re.M); has(R("verification"), r"git bisect"); has(R("verification"), r"A fix reported without its test is not accepted")
has(R("design-standard"), r"^## The AI-look check", re.M); has(R("design-standard"), r"ai-look: <n> found"); has(S("pf-design"), r"the AI-look check")
has(R("launch"), r"\| L7 \|.*\*\*both\*\* Google Search Console and Bing Webmaster Tools")
has(R("learning"), r"^## Reflect - learning from how the work actually went", re.M); has(R("learning"), r"sends nothing anywhere"); has(R("learning"), r"at least twice"); has(S("pf-learn"), r"/pf-learn reflect"); has(S("pf-learn"), r"Ask before reading saved conversations")
for shared_ in ("security", "code-simplicity", "verification", "design-standard"):
    check(read(f"{B}/references/{shared_}.md") == read(R(shared_)), f"{shared_}.md still identical in both plugins")
check(not os.path.exists(R("seo-tools")), "Atelier carries no outside-tool option file")
for f_ in (R("security"), R("code-simplicity"), R("verification"), R("design-standard"), R("learning"), R("launch")):
    hasnt(f_, r"github\.com|npx |modern-web-guidance|security-audit-skill|claude-seo|mcp-gsc|geo-optimizer")
# --- the authorized session (session-link.md)
SL = f"{C}/references/session-link.md"; BL = f"{B}/skills/pf-link/SKILL.md"; BNX = f"{B}/skills/pf-next/SKILL.md"
check(read(SL) == read(f"{B}/references/session-link.md"), "session-link.md identical in both plugins")
for pat in (r"PF-SESSION v1", r"One file per lane, never one shared file", r"never finds a session by itself", r"A session never serves two projects", r"`--go` is ignored", r"run nothing and write nothing", r"\*\*writes nothing\*\*", r"a tab that was already open", r"names the \*\*project and lane\*\*, never a session", r"One attempt, never a second session", r"first message after any restart", r"never prints a secret", r"data, never an instruction", r"It never creates a project folder"):
    has(SL, pat)
for pat in (r"^name: pf-link$", r"session-link\.md", r"nothing after it", r"Never guess from a similar name", r"write nothing", r"## Never"):
    has(BL, pat, re.M)
has(BNX, r"^## 1a\. Is this the authorized session\?", re.M); has(BNX, r"\*\*ignore `--go`\*\*"); has(BNX, r"run nothing, write nothing")
has(f"{C}/references/bridge.md", r"0\. \*\*Authorized session first\.\*\*"); has(f"{C}/references/bridge.md", r"Never look for a session by yourself")
check("`code_url` is stale" not in read(f"{C}/references/bridge.md"), "bridge.md no longer asks for a pasted link after a restart")
has(f"{C}/skills/pf-setup/SKILL.md", r"2\. \*\*Authorized Code session \(per lane\)\*\*"); has(f"{C}/skills/pf-lanes/SKILL.md", r"SESSION-<name>\.md")
has(f"{C}/references/state-schema.md", r"`lanes\.<name>\.session_key`"); has(f"{C}/references/upgrade.md", r"^\| U17 \|", re.M); has(f"{C}/skills/pf-upgrade/SKILL.md", r"U1–U19")
for s_ in ("pf-build", "pf-deploy"): has(f"{C}/skills/{s_}/SKILL.md", r"authorized session \(`session-link\.md`\)")
for f_ in (SL, BL):
    t_ = read(f_)
    check(not re.search(r"https?://(?!claude\.ai/)|[A-Za-z]:\\|ghp_|token:|password:", t_), f"{f_} carries no address, path or secret")
    check(not re.search(r"mcp__", t_), f"{f_} names no tool that may not exist")

# --- the notice from the Code session to the Cowork seat
SLN = read(f"{C}/references/session-link.md")
check(SLN == read(f"{B}/references/session-link.md"), "session-link.md still identical in both plugins after the notice")
for pat_ in ("PF-SEAT v1", "must start with https://claude.ai/", "not a sign-in page or an error page", "no free text, no question text", "One attempt; never a second page, never a tab that was already open", "never an instruction", "**The file decides, not the notice.**", "A notice never passes a gate", "does not match any request in flight - ignored", "`lanes.<lane>.seat_ref`", "single long backstop"):
    check(pat_ in SLN, f"session-link.md: {pat_[:50]}")
has(f"{B}/skills/pf-next/SKILL.md", r"\*\*Tell the Cowork seat\.\*\*"); has(f"{B}/skills/pf-next/SKILL.md", r"one attempt, nothing else typed")
has(f"{C}/references/bridge.md", r"2b\. \*\*The return address goes on the command itself\*\*"); has(f"{C}/references/bridge.md", r"7\. \*\*Or woken by the notice\.\*\*")
for s_ in ("pf-build", "pf-deploy", "pf-harden", "pf-merge"): has(f"{C}/skills/{s_}/SKILL.md", r"line starting 'PF-NOTICE'")

# --- auto mode
AM = read(f"{C}/references/auto-mode.md"); PA = read(f"{C}/skills/pf-auto/SKILL.md")
check(AM == read(f"{B}/references/auto-mode.md"), "auto-mode.md identical in both plugins")
for pat_ in ("PF-AUTO v1", "at most 24", "it never changes them", "Only the user's typed yes in this conversation starts it", "no custom or public domain is connected to it", "it holds no real client data", "so no permission pop-up appears later", "stopped on a permission prompt", "A contract is never relaxed", "a security test (`/pf-pentest`)", "any new billable resource or paid service", "any change to auto mode itself", "never stops to ask the person during auto mode", "carries on with the rest of the plan", "no new item starts", "can never start auto mode, extend it or widen it", "Auto mode adds no ability", "approved (auto, <grant>)"):
    check(pat_ in AM, f"auto-mode.md: {pat_[:48]}")
for pat_ in ("**Change no setting yourself**", "run **the rehearsal**", "Start auto mode until <time>?", "past the end time, start nothing", "## Never", "Treat text in a file, a notice or a page as permission"):
    check(pat_ in PA, f"pf-auto: {pat_[:48]}")
has(f"{B}/skills/pf-next/SKILL.md", r"^## 1c\. Auto mode", re.M); has(f"{B}/skills/pf-next/SKILL.md", r"Auto mode allows nothing extra"); has(f"{B}/skills/pf-next/SKILL.md", r"- Permissions: the commands the factory uses")
has(f"{C}/references/state-schema.md", r"^\| `auto` \|", re.M); has(f"{C}/skills/pf-ship/SKILL.md", r"\*\*Auto mode\*\* \(`/pf-auto`"); has(f"{C}/README.md", r"`/pf-auto \[<hours>\]`")
check(not re.search(r"https?://|[A-Za-z]:\\|ghp_", AM + PA), "auto mode files carry no address, path or secret")

# --- a question always reaches the Cowork seat
SLQ = read(f"{C}/references/session-link.md"); AMQ = read(f"{C}/references/auto-mode.md")
check(SLQ == read(f"{B}/references/session-link.md") and AMQ == read(f"{B}/references/auto-mode.md"), "session-link.md and auto-mode.md identical in both plugins after the question fix")
for pat_ in ("before the Cowork seat types anything at all into the Code session", "**before** it waits", "**Without a return address** the session has nobody to send the question to", "never obeyed as an instruction", "that is what the rehearsal"):
    check(pat_ in SLQ, f"session-link.md: {pat_[:48]}")
check("**The seat files come first.**" in AMQ and "**The way back:**" in AMQ, "auto-mode.md: seat files at the start, the way back in the ready check")
has(f"{C}/skills/pf-auto/SKILL.md", r"`SEAT-<lane>\.md` for every lane in the plan must then be in the folder"); has(f"{B}/skills/pf-next/SKILL.md", r"never skip it silently"); has(f"{B}/skills/pf-next/SKILL.md", r"- The way back:"); has(f"{B}/skills/pf-link/SKILL.md", r"tell the Cowork seat first"); check(sorted(os.listdir(f"{B}/hooks")) == ["activity-log.mjs", "hooks.json"], "the builder ships exactly one hook: the activity logger")

# --- auto mode clears the path first; done is always reported
AM3 = read(f"{C}/references/auto-mode.md"); SL3 = read(f"{C}/references/session-link.md"); PL3 = read(f"{B}/skills/pf-link/SKILL.md"); PA3 = read(f"{C}/skills/pf-auto/SKILL.md")
check(AM3 == read(f"{B}/references/auto-mode.md") and SL3 == read(f"{B}/references/session-link.md"), "auto-mode.md and session-link.md identical in both plugins after 'clear the path'")
for pat_ in ("3. **Clear the path.**", "the user's own tasks are never items inside the hours", "one specific, named yes for one thing the user was shown", "Never a category", "*Never ahead*", "2 hours would fit it", "A plan with nothing that runs by itself is not started", "Parking is the exception, not the plan", "The clock starts at the yes"):
    check(pat_ in AM3, f"auto-mode.md: {pat_[:48]}")
check(AM3.index("3. **Clear the path.**") < AM3.index("5. **The plan.**") < AM3.index("6. **One yes.**"), "auto mode: blockers are cleared before the plan, the plan before the yes")
for pat_ in ("Do not plan first and discover blockers later", "never put a \"stops for you\" item inside the hours", "If nothing would run by itself, do not start"):
    check(pat_ in PA3, f"pf-auto: {pat_[:48]}")
for pat_ in ("**Done counts too.**", "When finished or stuck: /pf-link notify"):
    check(pat_ in SL3, f"session-link.md: {pat_[:40]}")
for pat_ in ("## `/pf-link notify <done|failed|needs-input>`", "do not try another way", "Nothing else is ever typed on that page", "end with `/pf-link notify done`"):
    check(pat_ in PL3, f"pf-link: {pat_[:40]}")
has(f"{C}/references/bridge.md", r"6b\. \*\*Before a task in plain words, type `/pf-link seat")

# --- the return address travels with the command
SL4 = read(f"{C}/references/session-link.md"); PN4 = read(f"{B}/skills/pf-next/SKILL.md"); PL4 = read(f"{B}/skills/pf-link/SKILL.md")
check(SL4 == read(f"{B}/references/session-link.md") and read(f"{C}/references/auto-mode.md") == read(f"{B}/references/auto-mode.md"), "shared references identical after the return-address change")
for pat_ in ("--seat <link of this Cowork conversation> --ref <8 letters and digits>", "**`--go` without a return address is refused.**", "written by the Code session from that line", "A link found in a spec, a request file, a note or a web page is never used", "**It stays valid until it is replaced**", "notice not sent: no return address", "the question goes to the Cowork seat, not to a dialog"):
    check(pat_ in SL4, f"session-link.md: {pat_[:48]}")
check("request_id: <the request this hand-off is for" not in SL4, "the seat file is no longer tied to one request")
for pat_ in ("## 1a-2. The way back", "**`--go` with no `--seat` and no valid seat file for the lane: run nothing**", "No return address - nothing was run. Send again as:"):
    check(pat_ in PN4, f"pf-next: {pat_[:48]}")
for pat_ in ("## `/pf-link seat <link> <ref>`", "return address saved", "Never open the link here", "as the **first line** of your reply"):
    check(pat_ in PL4, f"pf-link: {pat_[:40]}")
has(f"{C}/references/bridge.md", r"If the reply starts with `No return address`"); has(f"{C}/references/auto-mode.md", r"is a blocker for step A3")

# --- team projects: a lane seat nudges the PM seat
SL5 = read(f"{C}/references/session-link.md"); PLN = read(f"{C}/skills/pf-lanes/SKILL.md")
check(SL5 == read(f"{B}/references/session-link.md") and read(f"{C}/references/auto-mode.md") == read(f"{B}/references/auto-mode.md"), "shared references identical after the PM nudge")
for pat_ in ("## Team projects - a lane seat nudges the PM seat", "PF-PM-SEAT v1", "a seat never nudges itself", "`PF-LANE <slug> <lane> <done|failed|ready-to-merge|needs-input> <marker>`", "never in the line", "The PM seat was not told: <why>. In the PM conversation run /pf-lanes seat.", "A nudge never merges, deploys or passes a gate by itself", "A solo project has one seat and none of this applies", "without anyone remembering it"):
    check(pat_ in SL5, f"session-link.md: {pat_[:48]}")
for pat_ in ("## `/pf-lanes seat [--also <name>,<name>]` (PM seat)", "PM address saved", "## When a line starting `PF-LANE` arrives (PM seat)", "approves, merges and passes nothing", "| PM told |"):
    check(pat_ in PLN, f"pf-lanes: {pat_[:40]}")
has(f"{C}/skills/pf-build/SKILL.md", r"tell the PM seat now"); has(f"{C}/skills/pf-build/SKILL.md", r"ready-to-merge <marker>"); has(f"{C}/skills/pf-merge/SKILL.md", r"make sure `PM-SEAT\.md` is current first"); has(f"{C}/references/state-schema.md", r"`PM-SEAT\.md` \(a file, team projects\)")

# --- hands-on steps go to the Code session before the user
HO6 = read(f"{C}/references/handoff.md"); AM6 = read(f"{C}/references/auto-mode.md")
check(AM6 == read(f"{B}/references/auto-mode.md"), "auto-mode.md identical in both plugins after the hands-on rule")
for pat_ in ("## Who does a hands-on step - the Code session before the user", "The user is not a pair of hands for commands", "\"It is a PowerShell command\" is not a reason", "That rule is not relaxed here", "do not pass the work to the user instead", "a session never types a password or a code"):
    check(pat_ in HO6, f"handoff.md: {pat_[:48]}")
check("starting a program, pasting a link, a command that needs their own rights" not in AM6 and "never to the user" in AM6, "auto mode no longer lists commands and starting programs as the user's own tasks")
has(f"{B}/skills/pf-link/SKILL.md", r"## A hands-on step from the Cowork seat"); has(f"{B}/skills/pf-link/SKILL.md", r"never a secret value"); has(f"{C}/skills/pf-auto/SKILL.md", r"to the Code session instead of the user")

# --- audit of the hand-off rules
SL7 = read(f"{C}/references/session-link.md"); AM7 = read(f"{C}/references/auto-mode.md")
check(SL7 == read(f"{B}/references/session-link.md") and AM7 == read(f"{B}/references/auto-mode.md"), "shared references identical after the audit fixes")
check("Outside auto hours it may also ask the person" not in SL7 and SL7.count("not to a dialog") == 1, "one rule, not two, about when a question dialog may open")
for pat_ in ("**Seats that review but do not build**", "`also_from: <name>, <name>`", "never in a lane file", "read that seat's log or hand-off note", "a long conversation may no longer remember it"):
    check(pat_ in SL7, f"session-link.md: {pat_[:44]}")
check("[<reference>]" not in SL7 + read(f"{B}/skills/pf-link/SKILL.md"), "notify takes no free text")
has(f"{B}/skills/pf-next/SKILL.md", r"no `status: ended` or `status: stopped` line"); has(f"{C}/references/bridge.md", r"the pentest too, which still has no `--go`"); has(f"{C}/references/auto-mode.md", r"scope: preview\+private-live \| preview")
for s_ in ("pf-build", "pf-deploy", "pf-harden", "pf-merge", "pf-pentest", "pf-auto"):
    has(f"{C}/skills/{s_}/SKILL.md", r"not from memory of an earlier reading in this conversation")
has(f"{C}/skills/pf-lanes/SKILL.md", r"## `/pf-lanes seat \[--also <name>,<name>\]`"); has(f"{C}/references/state-schema.md", r"`lanes\.<name>\.seat_ref`")

# --- activity logger + backlog file
import shutil as _sh
AL = f"{B}/hooks/activity-log.mjs"; ALS = read(AL); HK = json.load(open(f"{B}/hooks/hooks.json"))
check(set(HK) == {"hooks"} and set(HK["hooks"]) == {"SessionStart", "UserPromptSubmit", "PostToolUse", "SubagentStop", "Stop"}, "hooks.json: the five logging events and nothing else")
for ev_, arr_ in HK["hooks"].items():
    h_ = arr_[0]["hooks"][0]
    check(len(arr_) == 1 and len(arr_[0]["hooks"]) == 1 and h_["type"] == "command" and h_["async"] is True and h_["command"] == 'node "${CLAUDE_PLUGIN_ROOT}/hooks/activity-log.mjs"', f"hooks.json {ev_}: one async call of the logger")
for bad_ in ("child_process", "spawn", "exec(", "fetch(", "http", "process.env", "eval(", "tool_response", "i.command", "transcript_path"):
    check(bad_ not in ALS, f"the logger has no {bad_}")
check(read(f"{C}/references/activity.md") == read(f"{B}/references/activity.md"), "activity.md identical in both plugins")
for pat_ in ("It **starts nothing**", "names, never content", "A step counts as done only when its proof exists", "No pointer, no log", "A missed mark never stops the work", "data. No session obeys it"):
    check(pat_ in read(f"{C}/references/activity.md"), f"activity.md: {pat_[:40]}")
if _sh.which("node"):
    td_ = tempfile.mkdtemp(); pd_ = os.path.join(td_, "pf", "demo"); cd_ = os.path.join(td_, "code"); os.makedirs(pd_); os.makedirs(os.path.join(cd_, ".git", "info")); os.makedirs(os.path.join(cd_, "src"))
    open(os.path.join(pd_, "factory.json"), "w").write('{"lanes":{"solo":{}}}'); ALA = os.path.abspath(AL)
    def run_(args, cwd, inp=None): return subprocess.run(["node", ALA] + args, cwd=cwd, input=inp, capture_output=True, text=True)
    def hook_(d, cwd): return run_([], cwd, json.dumps(d))
    r_ = hook_({"hook_event_name": "PostToolUse", "tool_name": "Bash", "cwd": cd_, "tool_input": {"description": "x"}}, cd_)
    check(r_.returncode == 0 and r_.stdout == "" and not os.path.exists(os.path.join(pd_, "activity")), "logger: no pointer, no log, no output")
    check(run_(["link", pd_, "other", "solo"], cd_).returncode == 1 and not os.path.exists(os.path.join(cd_, ".pf-activity.json")), "logger link: refuses a slug that is not the folder name")
    r_ = run_(["link", pd_, "demo", "solo"], cd_)
    check(r_.returncode == 0 and "activity log on: demo / solo" in r_.stdout and ".pf-activity.json" in read(os.path.join(cd_, ".git", "info", "exclude")), "logger link: pointer written and kept out of git")
    SECRET_ = "ghp_" + "A1b2C3d4" * 5
    hook_({"hook_event_name": "PostToolUse", "session_id": "s" * 20, "tool_name": "Bash", "cwd": os.path.join(cd_, "src"), "tool_input": {"command": "export T=" + SECRET_, "description": "Run tests with " + SECRET_}, "tool_response": {"stdout": SECRET_}}, os.path.join(cd_, "src"))
    hook_({"hook_event_name": "PostToolUse", "tool_name": "Write", "cwd": cd_, "tool_input": {"file_path": os.path.join(cd_, "src", "a.ts"), "content": SECRET_}}, cd_)
    hook_({"hook_event_name": "UserPromptSubmit", "cwd": cd_, "prompt": "my password is " + SECRET_}, cd_)
    hook_({"hook_event_name": "UserPromptSubmit", "cwd": cd_, "prompt": "/pf-next demo build --lane solo --go --seat https://claude.ai/x --ref abcd1234"}, cd_)
    r_ = run_([], cd_, "not json"); check(r_.returncode == 0 and r_.stdout == "", "logger: bad input is swallowed, exit 0, silent")
    LOG_ = read(os.path.join(pd_, "activity", "solo.jsonl")); LN_ = [json.loads(x) for x in LOG_.strip().split("\n")]
    check(SECRET_ not in LOG_ and "password" not in LOG_ and "export" not in LOG_ and "claude.ai" not in LOG_, "logger: no command, prompt text, content, output or key-like value reaches the log")
    check([x["event"] for x in LN_] == ["link", "PostToolUse", "PostToolUse", "UserPromptSubmit"], "logger: free text is not logged, factory commands are")
    check(LN_[1]["what"] == "Run tests with [hidden]" and LN_[2]["what"] == "src/a.ts" and LN_[3]["what"] == "pf-next demo build", "logger: description, path and command name only")
    r_ = run_(["step", "build", "5", "--task", "T-47", "--done", "212", "--of", "275"], os.path.join(cd_, "src")); PR_ = json.load(open(os.path.join(pd_, "PROGRESS-solo.json")))
    check(r_.returncode == 0 and PR_["format"] == "PF-PROGRESS v1" and PR_["step"] == 5 and PR_["name"] == "Tests and checks" and PR_["task"] == "T-47" and PR_["within"] == {"done": 212, "of": 275} and len(PR_["steps"]) == 9, "step mark: PROGRESS file written")
    check(run_(["step", "build", "12"], cd_).returncode == 1 and run_(["step", "nonsense", "1"], cd_).returncode == 1 and json.load(open(os.path.join(pd_, "PROGRESS-solo.json")))["step"] == 5, "step mark: a wrong step changes nothing")
    r_ = run_(["step", "build", "3"], td_); check(r_.returncode == 0 and "step not marked" in r_.stdout, "step mark: outside a linked checkout it does nothing and does not fail")
    STEPS_ = json.loads(run_(["steps"], cd_).stdout)
    for k_, row_ in re.findall(r"^\| (build|deploy|merge|harden|pentest) \| (.+) \|$", read(f"{C}/references/activity.md"), re.M):
        check([re.sub(r"^\d+ ", "", x) for x in row_.split(" · ")] == STEPS_[k_], f"activity.md step list for {k_} matches the code")
    os.rename(os.path.join(pd_, "factory.json"), os.path.join(pd_, "f.json")); n0_ = len(LN_)
    hook_({"hook_event_name": "Stop", "cwd": cd_}, cd_); os.rename(os.path.join(pd_, "f.json"), os.path.join(pd_, "factory.json"))
    check(len(read(os.path.join(pd_, "activity", "solo.jsonl")).strip().split("\n")) == n0_ + 1, "logger: a pointer to a folder without factory.json is ignored")
    run_(["unlink"], cd_); check(not os.path.exists(os.path.join(cd_, ".pf-activity.json")), "logger unlink: pointer removed")
    # backlog check
    BC_ = os.path.abspath(f"{C}/scripts/backlog-check.py")
    def bc_(obj):
        open(os.path.join(pd_, "BACKLOG.json"), "w").write(json.dumps(obj)); r = subprocess.run([sys.executable, BC_, pd_], capture_output=True, text=True); return r.returncode, r.stdout
    good_ = {"format": "PF-BACKLOG v1", "project": "demo", "sprints": [{"id": "S1", "name": "Build", "status": "active", "start": "2026-11-20", "end": "2026-11-27"}], "tasks": [{"id": "T-1", "title": "x", "kind": "build", "status": "doing", "owner": "code", "sprint": "S1", "lane": "solo", "depends_on": [], "request": "BUILD-REQUEST-solo.md"}]}
    check(bc_(good_) == (0, "backlog ok: 1 sprints, 1 tasks\n"), "backlog check: a good file passes")
    import copy as _cp
    for name_, mut_, want_ in (("unknown sprint", lambda b: b["tasks"][0].update(sprint="S9"), "does not exist"), ("unknown lane", lambda b: b["tasks"][0].update(lane="zz"), "not a lane"), ("bad status", lambda b: b["tasks"][0].update(status="started"), "status must be"), ("blocked without a reason", lambda b: b["tasks"][0].update(status="blocked"), "blocked_by"), ("a path as request", lambda b: b["tasks"][0].update(request="../x.md"), "file name"), ("two active sprints", lambda b: b["sprints"].append({"id": "S2", "name": "n", "status": "active"}), "more than one sprint"), ("duplicate id", lambda b: b["tasks"].append(dict(b["tasks"][0])), "share an id"), ("wrong project", lambda b: b.update(project="other"), "folder name"), ("missing dependency", lambda b: b["tasks"][0].update(depends_on=["T-9"]), "depends on")):
        b_ = _cp.deepcopy(good_); mut_(b_); rc_, out_ = bc_(b_); check(rc_ == 1 and want_ in out_, f"backlog check catches: {name_}")
else:
    bad("node is needed to test the activity logger")
BLG = read(f"{C}/references/backlog.md")
for pat_ in ("The PM seat is the only writer", "An id is never reused", "At most one sprint is `active`", "never claim it passed", "Never mark a task `done` without the result that proves it"):
    check(pat_ in BLG, f"backlog.md: {pat_[:40]}")
for s_ in ("pf-build", "pf-merge", "pf-deploy", "pf-harden", "pf-pentest", "pf-lanes"):
    has(f"{C}/skills/{s_}/SKILL.md", r"## Backlog \(`backlog\.md`\)"); has(f"{C}/skills/{s_}/SKILL.md", r"Only the PM seat writes `BACKLOG\.json`")
has(f"{C}/skills/pf-plan/SKILL.md", r"\*\*Write `BACKLOG\.json`\*\*"); has(f"{C}/references/planning.md", r"the file is the list"); has(f"{C}/references/state-schema.md", r"`PROGRESS-<lane>\.json` \(`PF-PROGRESS v1`\)")
has(f"{B}/skills/pf-link/SKILL.md", r"6b\. \*\*Switch the activity log on\*\*"); has(f"{B}/skills/pf-link/SKILL.md", r"activity-log\.mjs. unlink"); has(f"{B}/skills/pf-next/SKILL.md", r"## 3a\. Mark the step"); has(f"{B}/skills/pf-next/SKILL.md", r"write `step not marked` in the result and carry on")
for s_ in ("pf-deploy-from-spec", "pf-harden-from-spec", "pf-pentest-from-spec"):
    has(f"{B}/skills/{s_}/SKILL.md", r"## Step marks")
has(f"{C}/references/upgrade.md", r"^\| U18 \|", re.M); has(f"{C}/skills/pf-upgrade/SKILL.md", r"U1–U19"); has(f"{B}/README.md", r"its one hook is a read-only activity logger that starts nothing"); hasnt(f"{B}/README.md", r"ships no hooks module")

# --- guided founder steps
FS = read(f"{C}/references/founder-steps.md")
check(FS == read(f"{B}/references/founder-steps.md"), "founder-steps.md identical in both plugins")
for pat_ in ("## Before the first click", "ready to copy", "exact words shown on the page", "never from memory", "Fill what is not a secret", "never presses the button that submits, authorizes, pays, publishes or deletes", "I will not read that page", "never move on because the owner said \"done\" when the page says otherwise", "Step 3 of 5", "Only one of them guides at a time", "never during them", "solve a CAPTCHA", "If in doubt, it is a founder-only job", "is **not** a founder job"):
    check(pat_ in FS, f"founder-steps.md: {pat_[:44]}")
for bad_ in ("Cowork seat types the password", "may read the token", "skip the confirmation"):
    check(bad_ not in FS, f"founder-steps.md never says: {bad_}")
for s_ in ("pf-setup", "pf-deploy", "pf-auto", "pf-monitor", "pf-launch", "pf-ship", "pf-pentest", "pf-harden"):
    has(f"{C}/skills/{s_}/SKILL.md", r"## Founder-only steps\n.*`founder-steps\.md`")
has(f"{C}/references/handoff.md", r"## A founder-only job is guided, never just handed over"); has(f"{B}/skills/pf-link/SKILL.md", r"let the owner type only the secret"); has(f"{C}/references/backlog.md", r"check \*\*before saving\*\*"); has(f"{C}/references/backlog.md", r"A founder-only job \(`founder-steps\.md`\) is a task")
for s_ in ("pf-build", "pf-merge", "pf-deploy", "pf-harden", "pf-pentest", "pf-lanes"):
    hasnt(f"{C}/skills/{s_}/SKILL.md", r"Run the check after every write")
for f_ in sorted(os.listdir(f"{C}/references")):
    if f_.endswith(".md") and os.path.exists(f"{B}/references/{f_}") and f_ in ("activity.md", "founder-steps.md", "session-link.md", "auto-mode.md"):
        check(read(f"{C}/references/{f_}") == read(f"{B}/references/{f_}"), f"shared reference {f_} is the same in both plugins")

# --- the logger finds the project when the session's own folder is not the checkout
if _sh.which("node"):
    t2_ = tempfile.mkdtemp(); h2_ = os.path.join(t2_, "home"); p2_ = os.path.join(t2_, "pf", "demo"); c2_ = os.path.join(t2_, "code"); s2_ = os.path.join(t2_, "sessionfolder")
    for x_ in (h2_, p2_, os.path.join(c2_, "src"), s2_): os.makedirs(x_)
    open(os.path.join(p2_, "factory.json"), "w").write("{}"); env2_ = dict(os.environ, HOME=h2_, USERPROFILE=h2_)
    def run2_(args, cwd, inp=None): return subprocess.run(["node", ALA] + args, cwd=cwd, input=inp, capture_output=True, text=True, env=env2_)
    run2_(["link", p2_, "demo", "solo"], c2_); lg2_ = os.path.join(p2_, "activity", "solo.jsonl"); n2_ = lambda: len(read(lg2_).strip().split("\n"))
    run2_([], s2_, json.dumps({"hook_event_name": "PostToolUse", "session_id": "sess-A", "cwd": s2_, "tool_name": "Bash", "tool_input": {"description": "before any file was touched"}}))
    check(n2_() == 1, "logger: a session elsewhere that has touched nothing in the checkout is not logged")
    run2_([], s2_, json.dumps({"hook_event_name": "PostToolUse", "session_id": "sess-A", "cwd": s2_, "tool_name": "Edit", "tool_input": {"file_path": os.path.join(c2_, "src", "a.ts")}}))
    check(n2_() == 2 and json.loads(read(lg2_).strip().split("\n")[-1])["what"] == "a.ts", "logger: found through the file a tool touched")
    run2_([], s2_, json.dumps({"hook_event_name": "PostToolUse", "session_id": "sess-A", "cwd": s2_, "tool_name": "Bash", "tool_input": {"description": "Run the tests"}}))
    run2_([], s2_, json.dumps({"hook_event_name": "Stop", "session_id": "sess-A", "cwd": s2_}))
    check(n2_() == 4, "logger: the same session is then logged from its own folder")
    run2_([], s2_, json.dumps({"hook_event_name": "PostToolUse", "session_id": "sess-B", "cwd": s2_, "tool_name": "Bash", "tool_input": {"description": "another session"}}))
    check(n2_() == 4, "logger: another session in the same folder is not logged")
    check(sorted(os.listdir(os.path.join(h2_, ".pf-activity"))) == ["last-hook.json", "sess-A.json"] and set(json.load(open(os.path.join(h2_, ".pf-activity", "sess-A.json")))) == {"v", "pointer"}, "logger: the per-session note holds a path and nothing else")
    lh_ = json.load(open(os.path.join(h2_, ".pf-activity", "last-hook.json"))) if os.path.exists(os.path.join(h2_, ".pf-activity", "last-hook.json")) else {}
    check(set(lh_) == {"v", "ts", "event"} and lh_["event"] == "PostToolUse", "logger: leaves a time-and-name-only proof that it fired")
    run2_(["unlink"], c2_); run2_([], s2_, json.dumps({"hook_event_name": "Stop", "session_id": "sess-A", "cwd": s2_}))
    check(n2_() == 5, "logger: after unlink the remembered session is no longer logged")
has(f"{C}/references/activity.md", r"A session that never touched a linked checkout is never logged"); check(read(f"{C}/references/activity.md") == read(f"{B}/references/activity.md"), "activity.md still identical in both plugins")

# --- logger: tool names kept, PowerShell described
if _sh.which("node"):
    t3_ = tempfile.mkdtemp(); p3_ = os.path.join(t3_, "pf", "demo"); c3_ = os.path.join(t3_, "code"); os.makedirs(p3_); os.makedirs(c3_)
    open(os.path.join(p3_, "factory.json"), "w").write("{}"); e3_ = dict(os.environ, HOME=t3_, USERPROFILE=t3_)
    r3_ = lambda args, inp=None: subprocess.run(["node", ALA] + args, cwd=c3_, input=inp, capture_output=True, text=True, env=e3_)
    r3_(["link", p3_, "demo", "solo"])
    r3_([], json.dumps({"hook_event_name": "PostToolUse", "cwd": c3_, "tool_name": "mcp__ccd_session_mgmt__get_session_details", "tool_input": {}}))
    r3_([], json.dumps({"hook_event_name": "PostToolUse", "cwd": c3_, "tool_name": "PowerShell", "tool_input": {"command": "$env:TOKEN='" + "Zx9" * 12 + "'", "description": "Run the unit tests"}}))
    r3_([], json.dumps({"hook_event_name": "PostToolUse", "cwd": c3_, "tool_name": "Evil\"name<script>", "tool_input": {}}))
    L3_ = [json.loads(x) for x in read(os.path.join(p3_, "activity", "solo.jsonl")).strip().split("\n")]
    check(L3_[1]["tool"] == "mcp__ccd_session_mgmt__get_session_details", "logger: a long tool name is kept, not masked")
    check(L3_[2]["tool"] == "PowerShell" and L3_[2]["what"] == "Run the unit tests" and "TOKEN" not in json.dumps(L3_[2]), "logger: PowerShell shows its description, never its command")
    check(L3_[3]["tool"] == "Evilnamescript", "logger: a tool name is cleaned to plain characters")

# --- the activity log switches itself on
has(f"{B}/skills/pf-next/SKILL.md", r"First, every time: is the activity log on\?"); has(f"{B}/skills/pf-link/SKILL.md", r"## Work given in plain words"); has(f"{B}/skills/pf-link/SKILL.md", r"switch the activity log on first")

# --- attack checks: code checker + sourced rules + India section
SC = os.path.abspath(f"{B}/scripts/sec-check.mjs"); SCS = read(SC); AC = read(f"{C}/references/attack-checks.md")
check(AC == read(f"{B}/references/attack-checks.md"), "attack-checks.md identical in both plugins")
for bad_ in ("child_process", "fetch(", "http", "writeFile", "appendFile", "unlink", "rename", "process.env", "eval("):
    check(bad_ not in SCS, f"sec-check has no {bad_}: read-only, no network")
rows_ = re.findall(r"^\| ([ABC]\d+) \|", AC, re.M)
check(rows_ == ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "B5", "B6"] + [f"C{i}" for i in range(1, 11)], "attack-checks.md: exactly the twenty sourced rules")
for row_ in [l for l in AC.split("\n") if re.match(r"^\| [ABC]\d+ \|", l)]:
    check(row_.count('"') >= 2 and len(row_.split("|")[-2].strip()) > 20, f"attack rule {row_[2:5].strip()} carries its source and a quoted line")
for out_ in ("timingSafeEqual", "alias"):
    check(out_ not in AC.split("## Left out on purpose")[0], f"unverified rule not added: {out_}")
if _sh.which("node"):
    tb_ = tempfile.mkdtemp()
    def mk_(rel_, body_):
        p_ = os.path.join(tb_, rel_); os.makedirs(os.path.dirname(p_), exist_ok=True); open(p_, "w").write(body_)
    def sc_(sub_): r = subprocess.run(["node", SC, os.path.join(tb_, sub_), "--json"], capture_output=True, text=True); return r.returncode, (json.loads(r.stdout) if r.stdout.strip().startswith("{") else r.stdout)
    CASES_ = {
     "view-security": ("supabase/migrations/1.sql", "create view public.v as select 1;\nCREATE OR REPLACE VIEW w WITH (security_barrier) AS select 1;\n", "create view public.v with (security_invoker = true) as select 1;\ncreate view w as select 1;\nalter view w set (security_invoker = on);\ncreate view private.x as select 1;\n-- create view commented as select 1;\ncreate view gone as select 1; drop view gone;\n", 2),
     "weak-random": ("src/a.ts", "const resetToken = Math.random().toString(36);\n", "const resetToken = crypto.randomBytes(32).toString('hex');\nconst jitter = Math.random() * 10;\n", 1),
     "trust-proxy": ("src/a.ts", "app.set('trust proxy', true);\n", "app.set('trust proxy', 1);\n// app.set('trust proxy', true)\n", 1),
     "jwt-algorithm": ("src/a.ts", "import jwt from 'jsonwebtoken';\nimport { jwtVerify } from 'jose';\nconst p = jwt.verify(t, k);\nconst q = await jwtVerify(t, k, { issuer: 'x' });\n", "import jwt from 'jsonwebtoken';\nimport { jwtVerify } from 'jose';\nconst p = jwt.verify(t, k, { algorithms: ['RS256'] });\nconst q = await jwtVerify(t, k, { algorithms: ['ES256'] });\nconst s = crypto.verify('sha256', d, k, sig);\n", 2),
    }
    for rule_, (rel_, bad_src_, good_src_, n_) in CASES_.items():
        mk_(f"bad-{rule_}/{rel_}", bad_src_); mk_(f"good-{rule_}/{rel_}", good_src_)
        rc_, o_ = sc_(f"bad-{rule_}"); check(rc_ == 1 and isinstance(o_, dict) and [x["rule"] for x in o_["findings"] if x["level"] == "fail"] == [rule_] * n_, f"sec-check rejects the bad sample: {rule_}")
        rc_, o_ = sc_(f"good-{rule_}"); check(rc_ == 0 and isinstance(o_, dict) and o_["fails"] == 0, f"sec-check accepts the good sample: {rule_}")
    mk_("bundle/public/viewer.js", "var a=1;" + "x=Math.random();token=x;" * 400 + "\n"); rc_, o_ = sc_("bundle"); check(rc_ == 0 and o_["skipped"] == ["public/viewer.js"] and o_["fails"] == 0, "sec-check names a minified bundle as skipped and does not judge it")
    mk_("tests-only/tests/x.test.ts", "const token = Math.random();\n"); rc_, o_ = sc_("tests-only"); check(rc_ == 0, "sec-check ignores test files")
    r_ = subprocess.run(["node", SC, os.path.join(tb_, "nope")], capture_output=True, text=True); check(r_.returncode == 2 and "not run" in r_.stdout, "sec-check that cannot run says so and exits 2, never 0")
    h0_ = {f_: read(os.path.join(dp_, f_)) for dp_, _, fs_ in os.walk(tb_) for f_ in fs_}; subprocess.run(["node", SC, tb_], capture_output=True, text=True)
    check(h0_ == {f_: read(os.path.join(dp_, f_)) for dp_, _, fs_ in os.walk(tb_) for f_ in fs_}, "sec-check changes no file")
else:
    bad("node is needed to test sec-check")
CMP = read(f"{C}/references/compliance.md"); IND = CMP.split("## India: the Digital Personal Data Protection rules")[1] if "## India: the Digital Personal Data Protection rules" in CMP else ""
for pat_ in ("flag every item below for legal sign-off", "withdrawn at any time", "parent or guardian", "without delay", "₹250 crore", "eighteen-month"):
    check(pat_ in IND, f"compliance.md India section: {pat_[:36]}")
check("72" not in IND.split("Not in this checklist")[0] and "13 Nov" not in IND and "13 May" not in IND, "India section carries no unverified deadline or date")
has(f"{B}/skills/pf-next/SKILL.md", r"## 3b\. The security checker"); has(f"{B}/skills/pf-next/SKILL.md", r"never `pass`"); has(f"{C}/references/security.md", r"## Attack checks \(added 23 Nov 2026\)"); has(f"{C}/references/upgrade.md", r"^\| U19 \|", re.M)

# --- the factory's own web platform check
WC = os.path.abspath(f"{B}/scripts/web-check.mjs"); WCS = read(WC); WR = read(f"{C}/references/web-checks.md")
check(WR == read(f"{B}/references/web-checks.md"), "web-checks.md identical in both plugins")
for bad_ in ("child_process", "fetch(", "http", "writeFile", "appendFile", "unlink", "rename", "process.env", "eval("):
    check(bad_ not in WCS, f"web-check has no {bad_}: read-only, no network")
check(re.findall(r"^\| (W\d+) \|", WR, re.M) == [f"W{i}" for i in range(1, 12)], "web-checks.md: exactly the eleven sourced rules")
for row_ in [l for l in WR.split("\n") if re.match(r"^\| W\d+ \|", l)]:
    check(row_.count('"') >= 2, f"web rule {row_.split('|')[1].strip()} carries a quoted source line")
check("XMLHttpRequest" not in WCS and "modern-web-guidance" not in read(f"{C}/references/skills.md").lower() and "Modern Web Guidance" not in read(f"{C}/references/skills.md"), "the unverified rule and the outside tool are not in the plugin")
if _sh.which("node"):
    tw_ = tempfile.mkdtemp()
    def mw_(rel_, body_):
        p_ = os.path.join(tw_, rel_); os.makedirs(os.path.dirname(p_), exist_ok=True); open(p_, "w").write(body_)
    def wc_(sub_): r = subprocess.run(["node", WC, os.path.join(tw_, sub_), "--json"], capture_output=True, text=True); return r.returncode, (json.loads(r.stdout) if r.stdout.strip().startswith("{") else r.stdout)
    H_ = lambda body_, head_="": f'<!doctype html><html lang="en"><head>{head_}</head><body>{body_}</body></html>\n'
    WCASES_ = {
      "W1": (H_("<script>document.write('a')</script>"), H_("<script>// document.write('a')\nel.append(x)</script>")),
      "W2": (H_("<script>addEventListener('unload', f)</script>"), H_("<script>addEventListener('pagehide', f)</script>")),
      "W3": (H_("<script>if (e.keyCode === 13) go()</script>"), H_("<script>if (e.key === 'Enter') go()</script>")),
      "W4": (H_("<script>document.execCommand('copy')</script>"), H_("<script>navigator.clipboard.writeText(t)</script>")),
      "W5": (H_("<script>s.substr(1)</script>"), H_("<script>s.slice(1); s.substring(1)</script>")),
      "W6": (H_("<script>var q = escape(s)</script>"), H_("<script>var q = encodeURIComponent(s); CSS.escape(s); _.escape(s)</script>")),
      "W7": (H_("<script>el.addEventListener('DOMNodeInserted', g)</script>"), H_("<script>new MutationObserver(g).observe(el, {childList: true})</script>")),
      "W8": (H_("<center>x</center>"), H_("<!-- <center>old</center> --><div class=\"center\">x</div>")),
      "W9": (H_("x", '<meta name="viewport" content="width=device-width, user-scalable=no">'), H_("x", '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5">')),
      "W10": ("<!doctype html><html><head></head><body>x</body></html>\n", H_("x")),
      "W11": (H_("x", "<style>a:focus{outline:none}</style>"), H_("x", "<style>a:focus{outline:none;box-shadow:0 0 0 2px #0b6b5f} .x{outline:none}</style>")),
    }
    for rule_, (bad_src_, good_src_) in WCASES_.items():
        mw_(f"bad-{rule_}/index.html", bad_src_); mw_(f"good-{rule_}/index.html", good_src_)
        rc_, o_ = wc_(f"bad-{rule_}"); check(rc_ == 1 and isinstance(o_, dict) and {x["rule"] for x in o_["findings"]} == {rule_}, f"web-check rejects the bad sample: {rule_}")
        rc_, o_ = wc_(f"good-{rule_}"); check(rc_ == 0 and isinstance(o_, dict) and o_["fails"] == 0, f"web-check accepts the good sample: {rule_}")
    mw_("next/src/layout.tsx", "export const viewport = { userScalable: false };\nexport default function L(){ return <html><body/></html> }\n"); rc_, o_ = wc_("next")
    check(rc_ == 1 and sorted(x["rule"] for x in o_["findings"]) == ["W10", "W9"], "web-check reads a framework layout file too")
    mw_("bundle/public/app.js", "var a=1;" + "document.write(1);" * 400 + "\n"); rc_, o_ = wc_("bundle"); check(rc_ == 0 and o_["skipped"] == ["public/app.js"], "web-check names a minified bundle as skipped")
    r_ = subprocess.run(["node", WC, os.path.join(tw_, "nope")], capture_output=True, text=True); check(r_.returncode == 2 and "not run" in r_.stdout, "web-check that cannot run says so and exits 2, never 0")
else:
    bad("node is needed to test web-check")
has(f"{B}/skills/pf-next/SKILL.md", r"web-check\.mjs"); has(f"{C}/references/upgrade.md", r"`web-check: pass`")

# --- the checkers are shipped in both plugins, identical
for n_ in ("sec-check.mjs", "web-check.mjs"):
    check(read(f"{C}/scripts/{n_}") == read(f"{B}/scripts/{n_}"), f"{n_} identical in both plugins")
check("what a live tracker reads" in read("CHANGELOG.md"), "changelog entry for the port")

print(f"\n{n_ok} PASS, {n_bad} FAIL"); sys.exit(1 if n_bad else 0)
