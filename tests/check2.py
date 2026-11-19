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

# --- 8. public repo: no personal or private-project wording anywhere outside vendored skills.
# The words themselves are not written here: each is stored as a short hash, and every word and
# adjacent word pair in the repo is hashed and compared. Maintainers add a term by adding its hash.
import hashlib
_h = lambda t: hashlib.sha256(t.encode()).hexdigest()[:16]
PRIV_LC = {'bf77e2a6d3c0c5b6', '1d0e0e23238779ea', 'e52b9fb83fb40a16', '31a1736842d27b11', '7cf0c08e6d6cae38', '567781541aa1d043', 'cf1c96e9d2e42846', 'b78293703cf3e005', '7068f6611e5257b4', 'f04222209b2d8a97'}
PRIV_CS = {'1a3326777cf2220b', '39943de3ebeb355c', 'b6152a0c6c5b3465'}
for top in (C, B, "README.md", "INSTALL.md", "CONTRIBUTING.md", "CHANGELOG.md", "THIRD-PARTY-NOTICES.md", "tests", ".claude-plugin"):
    paths = [top] if os.path.isfile(top) else [os.path.join(r, x) for r, _, fs in os.walk(top) for x in fs]
    for f in paths:
        if any(v in f for v in ("security-audit", "design-md", "humanizer")) or not f.endswith((".md", ".json", ".sh", ".py", ".mjs")): continue
        toks = re.findall(r"[A-Za-z0-9]+", read(f)); low = [t.lower() for t in toks]
        comp = {t.lower() for t in re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+", read(f))}
        hit = (any(_h(t) in PRIV_CS for t in set(toks)) or any(_h(a + " " + b) in PRIV_CS for a, b in set(zip(toks, toks[1:])))
               or any(_h(t) in PRIV_LC for t in set(low) | comp) or any(_h(a + " " + b) in PRIV_LC for a, b in set(zip(low, low[1:]))))
        if hit: bad(f"{f} contains private wording")
ok("personal-data scan ran")
print(f"\n{n_ok} PASS, {n_bad} FAIL"); sys.exit(1 if n_bad else 0)
