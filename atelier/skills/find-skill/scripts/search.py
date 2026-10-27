"""Search the bundled skill catalogue.

Usage:
  python search.py <query words> [--limit N] [--page N] [--all] [--source NAME]
  python search.py --top N
  python search.py --stats

Finds data/catalogue.json relative to this file, so it works wherever the skill
is installed (Claude Code, Cowork, claude.ai chats).
"""
import argparse
import collections
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOGUE = os.path.join(HERE, "..", "data", "catalogue.json")

# Trust ranking by source (roughly GitHub stars of the source list)
SOURCE_PRIORITY = {
    "Anthropic": 60, "skills.sh": 30, "hesreallyhim": 28, "ComposioHQ": 25,
    "vercel-labs": 12, "VoltAgent-subagents": 8, "VoltAgent": 7, "travisvn": 5,
    "BehiSecc": 4, "alirezarezvani": 4, "heilcheng": 3, "daymade": 3, "mxyhi": 3,
    "SkillsMP": 3,
}
TRUST = {
    "Anthropic": "Official", "skills.sh": "Official catalogue", "hesreallyhim": "Top list",
    "ComposioHQ": "Top list", "vercel-labs": "Curated", "VoltAgent-subagents": "Curated",
    "VoltAgent": "Curated", "travisvn": "Curated", "BehiSecc": "Curated",
    "alirezarezvani": "Community", "heilcheng": "Community", "daymade": "Community",
    "mxyhi": "Community", "SkillsMP": "Marketplace - verify",
}


def score(s, terms):
    name, desc = s["n"].lower(), s["d"].lower()
    tags = " ".join(s.get("t", [])).lower()
    total = 0
    for t in terms:
        if t == name:
            total += 100
        elif t in name:
            total += 50
        elif t in desc:
            total += 20
        elif t in tags:
            total += 10
        else:
            return 0  # every term must match somewhere
    return total + SOURCE_PRIORITY.get(s["s"], 0) + min(s.get("st", 0) / 1000, 20)


def fmt(s):
    return {"name": s["n"], "source": s["s"], "trust": TRUST.get(s["s"], "Unknown - verify"),
            "stars": s.get("st") or None, "url": s["u"], "description": s["d"]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("query", nargs="*")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--all", action="store_true")
    p.add_argument("--source")
    p.add_argument("--top", type=int)
    p.add_argument("--stats", action="store_true")
    a = p.parse_args()

    with open(CATALOGUE, encoding="utf-8") as f:
        data = json.load(f)
    skills = data["skills"]
    if a.source:
        skills = [s for s in skills if s["s"].lower() == a.source.lower()]

    if a.stats:
        c = collections.Counter(s["s"] for s in skills)
        print(json.dumps({"updated_at": data["updated_at"], "total": len(skills),
                          "by_source": dict(c.most_common())}, indent=2))
        return

    if a.top:
        ranked = sorted(skills, key=lambda s: (-s.get("st", 0), -SOURCE_PRIORITY.get(s["s"], 0)))
        print(json.dumps({"updated_at": data["updated_at"],
                          "results": [fmt(s) for s in ranked[:a.top]]}, indent=2, ensure_ascii=False))
        return

    terms = [t.lower() for t in a.query if t.strip()]
    if not terms:
        p.error("give a search query, --top N, or --stats")
    hits = [(score(s, terms), s) for s in skills]
    hits = [h for h in hits if h[0] > 0]
    hits.sort(key=lambda h: (-h[0], -h[1].get("st", 0)))

    total = len(hits)
    page = hits if a.all else hits[(a.page - 1) * a.limit: a.page * a.limit]
    print(json.dumps({
        "query": " ".join(terms), "total": total,
        "page": 1 if a.all else a.page,
        "total_pages": 1 if a.all else max(1, -(-total // a.limit)),
        "catalogue_updated_at": data["updated_at"],
        "results": [fmt(s) for _, s in page],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
