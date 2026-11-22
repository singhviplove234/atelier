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
has(f"{C}/references/state-schema.md", r"`lanes\.<name>\.session_key`"); has(f"{C}/references/upgrade.md", r"^\| U17 \|", re.M); has(f"{C}/skills/pf-upgrade/SKILL.md", r"U1–U17")
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
has(f"{C}/skills/pf-auto/SKILL.md", r"`SEAT-<lane>\.md` for every lane in the plan must then be in the folder"); has(f"{B}/skills/pf-next/SKILL.md", r"never skip it silently"); has(f"{B}/skills/pf-next/SKILL.md", r"- The way back:"); has(f"{B}/skills/pf-link/SKILL.md", r"tell the Cowork seat first"); check(not os.path.isdir(f"{B}/hooks"), "the builder still ships no hooks module")

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

print(f"\n{n_ok} PASS, {n_bad} FAIL"); sys.exit(1 if n_bad else 0)
