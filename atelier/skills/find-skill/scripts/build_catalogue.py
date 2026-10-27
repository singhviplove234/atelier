"""Build the bundled catalogue for the portable find-skill from the full upstream one.

Usage: python build_catalogue.py <upstream catalogue.json> [output path]

The upstream catalogue (produced by update-skills-catalogue.sh from
github.com/fockus/claude-skill-find-skill) mixes real skills with awesome-list
headings and relative links. This cleans it and writes a compact version:
  n = name, d = description, s = source, u = url, st = stars, t = tags, c = category
"""
import json
import os
import re
import sys

LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
JUNK_NAMES = {"skill.md", ".github", "readme", "readme.md", "contributing", "license"}


def clean_name(raw):
    link_url = None
    m = LINK.search(raw)
    if m:
        raw, link_url = m.group(1), m.group(2)
    name = re.sub(r"[*_`]", "", raw)
    name = re.sub(r"^[^\w@./-]+", "", name).strip()  # leading emoji / bullets
    return name, link_url


def resolve_url(s, link_url):
    for u in (link_url, s.get("install_url"), s.get("repo_url")):
        if u and u.startswith("http"):
            return u
    rel = s.get("install_url") or s.get("repo_url") or ""
    repo = s.get("repo") or ""
    if rel and not rel.startswith("#") and re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        return f"https://github.com/{repo}/blob/main/{rel.lstrip('./')}"
    return None  # anchor-only or missing: a list heading, not a skill


def to_int(v):
    try:
        return int(str(v or 0).replace(",", "").replace("+", ""))
    except ValueError:
        return 0


def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data", "catalogue.json")
    with open(src, encoding="utf-8") as f:
        data = json.load(f)

    skills, seen, dropped = [], set(), 0
    for s in data["skills"]:
        name, link_url = clean_name(s.get("name", ""))
        url = resolve_url(s, link_url)
        if not name or not url or name.lower() in JUNK_NAMES:
            dropped += 1
            continue
        key = (name.lower(), url)
        if key in seen:
            continue
        seen.add(key)
        desc = re.sub(r"\s+", " ", s.get("description", "")).strip()
        skills.append({
            "n": name,
            "d": desc[:240],
            "s": s.get("source", ""),
            "u": url,
            "st": to_int(s.get("stars")),
            "t": s.get("tags", [])[:6],
            "c": s.get("category", ""),
        })

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"updated_at": data.get("updated_at"), "total": len(skills), "skills": skills},
                  f, ensure_ascii=False, separators=(",", ":"))
    print(f"Kept {len(skills)} skills, dropped {dropped}. Wrote {out}")


if __name__ == "__main__":
    main()
