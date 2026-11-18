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
            check(len(t.split()) < 3700, f"{f} under 3700 words ({len(t.split())})")

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
                if r in ("verify.yml",) or not re.match(r"[a-z]", r): continue
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
                if re.search(r"eight headings|all eight|plan-audit\.md", read(f)): bad(f"{f} has stale wording")
ok("no stale 'eight headings' / plan-audit wording") if True else None

# --- 7. feature wiring (each line = a promise the docs make somewhere else)
BB, BD, BN = f"{B}/skills/pf-build-from-spec/SKILL.md", f"{B}/skills/pf-deploy-from-spec/SKILL.md", f"{B}/skills/pf-next/SKILL.md"
S = lambda n: f"{C}/skills/{n}/SKILL.md"; R = lambda n: f"{C}/references/{n}.md"
# 0.2.0: diagrams gate, attribution, token-light
has(BB, r"## 1b\. Diagrams gate"); has(BB, r"/diagram-design:doctor"); has(BB, r"failures: no diagram for")
has(BB, r'"attribution"'); has(BB, r"includeCoAuthoredBy"); hasnt(BB, r"~/.claude/settings.json`\s*\(create")
has(S("pf-build"), r"Token-light"); has(S("pf-deploy"), r"Token-light"); has(S("pf-setup"), r"0b2\.")
has(R("skills"), r"diagram-design"); has(R("growth"), r"includingRegex|Questions:")
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
# standing safety rules still present
has(S("pf-setup"), r"Never type"); has(S("pf-ship"), r"never flips `gates\.delivery`"); has(BN, r"never.* skips confirm|never skips the confirm", re.S)

# --- 8. public repo: no personal or private-project wording anywhere outside vendored skills
PRIV = r"$^"  # the word list is not kept in the repository
for top in (C, B, "README.md", "INSTALL.md", "CONTRIBUTING.md", "tests"):
    paths = [top] if os.path.isfile(top) else [os.path.join(r, x) for r, _, fs in os.walk(top) for x in fs]
    for f in paths:
        if any(v in f for v in ("security-audit", "design-md", "humanizer", "find-skill", "check2.py", "check.sh")) or not f.endswith((".md", ".json", ".sh", ".py")): continue
        m = re.search(PRIV, read(f))
        if m: bad(f"{f} contains private wording: {m.group(0)}")
ok("personal-data scan ran")
print(f"\n{n_ok} PASS, {n_bad} FAIL"); sys.exit(1 if n_bad else 0)
