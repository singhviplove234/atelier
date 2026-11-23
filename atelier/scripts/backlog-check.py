#!/usr/bin/env python3
"""Checks BACKLOG.json (PF-BACKLOG v1). Read-only. python backlog-check.py <project folder>
Prints one line per problem and exits 1, or 'backlog ok: ...' and exits 0."""
import json, os, re, sys
SPRINT_STATUS = ("planned", "active", "done")
TASK_STATUS = ("todo", "doing", "waiting", "blocked", "done")
KINDS = ("plan", "design", "build", "merge", "deploy", "harden", "pentest", "other")
OWNERS = ("code", "cowork", "you")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def check(folder):
    errs = []; f = os.path.join(folder, "BACKLOG.json")
    try: b = json.load(open(f, encoding="utf-8"))
    except FileNotFoundError: return ["no BACKLOG.json in the folder"], None
    except ValueError as e: return [f"BACKLOG.json is not valid JSON: {e}"], None
    if b.get("format") != "PF-BACKLOG v1": errs.append('format must be "PF-BACKLOG v1"')
    if b.get("project") != os.path.basename(os.path.abspath(folder)): errs.append("project must be the folder name")
    lanes = None
    try: lanes = set((json.load(open(os.path.join(folder, "factory.json"), encoding="utf-8")).get("lanes") or {}).keys())
    except Exception: pass
    sprints = b.get("sprints"); tasks = b.get("tasks")
    if not isinstance(sprints, list): errs.append("sprints must be a list"); sprints = []
    if not isinstance(tasks, list): errs.append("tasks must be a list"); tasks = []
    sids = [s.get("id") for s in sprints if isinstance(s, dict)]
    for s in sprints:
        if not isinstance(s, dict): errs.append("a sprint is not an object"); continue
        i = s.get("id")
        if not (isinstance(i, str) and re.match(r"^S\d+$", i)): errs.append(f"sprint id {i!r} must look like S1")
        if not s.get("name"): errs.append(f"sprint {i}: name is missing")
        if s.get("status") not in SPRINT_STATUS: errs.append(f"sprint {i}: status must be one of {', '.join(SPRINT_STATUS)}")
        for k in ("start", "end"):
            if s.get(k) is not None and not (isinstance(s.get(k), str) and DATE.match(s[k])): errs.append(f"sprint {i}: {k} must be YYYY-MM-DD or null")
        if s.get("start") and s.get("end") and str(s["start"]) > str(s["end"]): errs.append(f"sprint {i}: start is after end")
    if len(sids) != len(set(sids)): errs.append("two sprints share an id")
    if sum(1 for s in sprints if isinstance(s, dict) and s.get("status") == "active") > 1: errs.append("more than one sprint is active")
    tids = [t.get("id") for t in tasks if isinstance(t, dict)]
    if len(tids) != len(set(tids)): errs.append("two tasks share an id")
    for t in tasks:
        if not isinstance(t, dict): errs.append("a task is not an object"); continue
        i = t.get("id")
        if not (isinstance(i, str) and re.match(r"^[A-Z]{1,3}-\d+$", i)): errs.append(f"task id {i!r} must look like T-12")
        if not t.get("title"): errs.append(f"task {i}: title is missing")
        if t.get("kind") not in KINDS: errs.append(f"task {i}: kind must be one of {', '.join(KINDS)}")
        if t.get("status") not in TASK_STATUS: errs.append(f"task {i}: status must be one of {', '.join(TASK_STATUS)}")
        if t.get("owner") not in OWNERS: errs.append(f"task {i}: owner must be one of {', '.join(OWNERS)}")
        if t.get("sprint") is not None and t.get("sprint") not in sids: errs.append(f"task {i}: sprint {t.get('sprint')!r} does not exist")
        if lanes is not None and t.get("lane") is not None and t.get("lane") not in lanes: errs.append(f"task {i}: lane {t.get('lane')!r} is not a lane of this project")
        for d in t.get("depends_on") or []:
            if d not in tids: errs.append(f"task {i}: depends on {d!r}, which does not exist")
            if d == i: errs.append(f"task {i}: depends on itself")
        if t.get("status") == "blocked" and not t.get("blocked_by"): errs.append(f"task {i}: a blocked task says what blocks it (blocked_by)")
        for k in ("request", "result"):
            v = t.get(k)
            if v is not None and (not isinstance(v, str) or "/" in v or "\\" in v or ".." in v): errs.append(f"task {i}: {k} must be a file name in the project folder, or null")
    return errs, (len(sprints), len(tasks))

if __name__ == "__main__":
    if len(sys.argv) != 2: print(__doc__); sys.exit(2)
    errs, n = check(sys.argv[1])
    if errs:
        for e in errs: print("backlog problem:", e)
        sys.exit(1)
    print(f"backlog ok: {n[0]} sprints, {n[1]} tasks")
