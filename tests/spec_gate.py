#!/usr/bin/env python3
"""Mechanical half of the Diagrams gate (spec-format.md): nine headings in order,
every screen in exactly one page- block, every route group and user-scoped table in
exactly one feature- block. Usage: spec_gate.py SPEC.md  -> exit 0 / prints misses."""
import re, sys
NINE = ["Brief", "Stack", "Screens", "Tokens", "Components", "Data model",
        "Routes / API", "Diagrams", "Acceptance checks"]
s = open(sys.argv[1], encoding="utf-8").read()
miss = []
# headings: only those outside code fences
out, fence = [], False
for line in s.split("\n"):
    if line.startswith("```"): fence = not fence
    elif not fence: out.append(line)
h2 = [l[3:].strip() for l in out if l.startswith("## ")]
if [h for h in h2 if h != "Scope"] != NINE: miss.append(f"headings are {h2}, want {NINE}")
sec = lambda name: (re.search(rf"^## {re.escape(name)}\n(.*?)(?=^## |\Z)", s, re.S | re.M) or [None, ""])[1]
blocks = re.findall(r"```mermaid\n(.*?)```", sec("Diagrams"), re.S)
ids, covers = {}, {}
for b in blocks:
    m = re.match(r"%% id: (\S+)", b)
    if not m: miss.append("mermaid block without '%% id:' first line"); continue
    i = m.group(1)
    if i in ids: miss.append(f"duplicate diagram id {i}")
    ids[i] = b
    c = re.search(r"^%% covers: (.*)$", b, re.M)
    covers[i] = [x.strip().lower() for x in c.group(1).split(",")] if c else []
for req in ("app-architecture", "app-journey"):
    if req not in ids: miss.append(f"no diagram {req}")
slug = lambda t: re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
def hits(prefix, names):
    n = 0
    for i, cv in covers.items():
        if not i.startswith(prefix): continue
        if any(i == prefix + slug(x) for x in names) or any(x.lower() in c or c.endswith(x.lower()) for x in names for c in cv): n += 1
    return n
for scr in re.findall(r"^### (.+)$", sec("Screens"), re.M):
    k = hits("page-", [scr])
    if k != 1: miss.append(f"screen '{scr}' is in {k} page- diagrams (want 1)")
groups = sorted({m.group(1) for m in re.finditer(r"/api/([a-z0-9_-]+)", sec("Routes / API"))})
for g in groups:
    k = hits("feature-", [g, f"routes /api/{g}"])
    if k != 1: miss.append(f"route group '/api/{g}' is in {k} feature- diagrams (want 1)")
for t, rest in re.findall(r"^Table `([a-z_]+)`:(.*)$", sec("Data model"), re.M):
    if re.search(r"user-scoped|user_id|owner_id|RLS", rest):
        k = hits("feature-", [t, f"table {t}"])
        if k != 1: miss.append(f"user-scoped table '{t}' is in {k} feature- diagrams (want 1)")
for i, b in ids.items():
    if i.startswith("feature-") and not re.search(r"\belse\b|-->\|.*(invalid|fail|error|wrong|401|4\d\d)", b, re.I):
        miss.append(f"{i} draws no failure path")
print("\n".join(miss) or "ok"); sys.exit(1 if miss else 0)
