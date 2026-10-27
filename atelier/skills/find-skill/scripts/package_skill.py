"""Download a skill from GitHub and package it as an upload-ready zip.

Usage: python package_skill.py <github url or owner/repo> [--path SUBDIR] [--name NAME] [--out DIR]

Handles repo roots, /tree/<branch>/<path> links and mono-repos (picks the
folder whose SKILL.md matches --name, or lists the choices). The zip has the
skill folder at its root with SKILL.md inside, which is what Claude's
"Upload skill" (Settings > Capabilities > Skills) expects.
"""
import argparse
import io
import os
import re
import sys
import urllib.request
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def parse(src):
    src = src.strip().rstrip("/")
    # skills.sh/<owner>/<repo>/<skill> pages point at a skill inside a GitHub repo
    m = re.match(r"https?://(?:www\.)?(?:official)?skills\.sh/([\w.-]+)/([\w.-]+)/([\w.-]+)$", src)
    if m:
        return m.group(1), m.group(2), "HEAD", "", m.group(3)
    m = re.match(r"(?:https?://github\.com/)?([\w.-]+)/([\w.-]+?)(?:\.git)?(?:/(?:tree|blob)/([^/]+)(?:/(.*))?)?$", src)
    if not m:
        sys.exit(f"Not a GitHub repo reference: {src}")
    owner, repo, ref, path = m.groups()
    if path and path.endswith("SKILL.md"):
        path = os.path.dirname(path)
    return owner, repo, ref or "HEAD", path or "", None


def frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            if v:
                fm[k.strip()] = v.strip().strip("\"'")
    return fm


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source")
    p.add_argument("--path", default=None)
    p.add_argument("--name", default=None)
    p.add_argument("--out", default=".")
    a = p.parse_args()

    owner, repo, ref, path, sh_name = parse(a.source)
    path = (a.path or path).strip("/")
    a.name = a.name or sh_name
    url = f"https://codeload.github.com/{owner}/{repo}/zip/{ref}"
    print(f"Downloading {url}")
    try:
        blob = urllib.request.urlopen(url, timeout=60).read()
    except Exception as e:
        sys.exit(f"DOWNLOAD FAILED ({e}). Network may be unavailable here; "
                 f"give the user https://github.com/{owner}/{repo} to download themselves.")
    zin = zipfile.ZipFile(io.BytesIO(blob))
    root = zin.namelist()[0].split("/")[0]

    skill_mds = [n for n in zin.namelist() if n.endswith("/SKILL.md")]
    candidates = {}
    for n in skill_mds:
        d = n[len(root) + 1:-len("SKILL.md")].strip("/")
        candidates[d] = frontmatter(zin.read(n).decode("utf-8", "replace"))
    if not candidates:
        sys.exit("No SKILL.md in this repo, so it is not a Claude skill.")

    if path in candidates:
        chosen = path
    else:
        pool = {d: fm for d, fm in candidates.items() if d.startswith(path)} if path else candidates
        if a.name:
            pool = {d: fm for d, fm in pool.items()
                    if fm.get("name") == a.name or os.path.basename(d) == a.name}
        # Ignore test fixtures and examples unless nothing else is left
        noise = {"test", "tests", "__tests__", "fixtures", "fixture", "examples", "example"}
        real = {d: fm for d, fm in pool.items() if not noise & set(d.lower().split("/"))}
        pool = real or pool
        # Same skill copied per agent (.claude/, .agents/, ...): take the Claude copy
        if len(pool) > 1 and len({fm.get("name") for fm in pool.values()}) == 1:
            best = sorted(pool, key=lambda d: (".claude/" not in d + "/", len(d)))[0]
            pool = {best: pool[best]}
        if len(pool) != 1:
            print("MULTIPLE_OR_NO_MATCH. Skills in this repo:")
            for d, fm in sorted(candidates.items()):
                print(f"  --path '{d}'  name={fm.get('name')}  :: {fm.get('description', '')[:90]}")
            sys.exit(2)
        chosen = next(iter(pool))

    fm = candidates[chosen]
    name = fm.get("name") or os.path.basename(chosen) or repo
    name = re.sub(r"[^a-z0-9-]", "-", name.lower()).strip("-")[:64]
    if not fm.get("description"):
        print("WARNING: SKILL.md has no description; upload may be rejected.")

    prefix = f"{root}/{chosen}/" if chosen else f"{root}/"
    os.makedirs(a.out, exist_ok=True)
    out = os.path.join(a.out, f"{name}.zip")
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for n in zin.namelist():
            if n.startswith(prefix) and not n.endswith("/") and "/.git/" not in n:
                zout.writestr(f"{name}/{n[len(prefix):]}", zin.read(n))
                count += 1
    print(f"PACKAGED {out}  ({count} files, skill name '{name}')")
    print(f"description: {fm.get('description', '')[:300]}")


if __name__ == "__main__":
    main()
