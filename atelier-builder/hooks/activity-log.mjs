#!/usr/bin/env node
// Activity logger. Read-only towards the product: it starts nothing, changes no code,
// blocks nothing and prints nothing. It writes only inside the linked project's folder:
//   activity/<lane>.jsonl   one line per event (what happened, never the content)
//   PROGRESS-<lane>.json    which step the current piece of work is at
// plus one tiny note per session in ~/.pf-activity (which checkout that session last touched),
// and, for `link`, the pointer file .pf-activity.json in the code checkout.
// It never records a command, a prompt, file contents or any value - only names.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const POINTER = '.pf-activity.json';
const NAME = /^[a-z0-9][a-z0-9-]{0,63}$/;
const MAX_LOG = 2 * 1024 * 1024;
export const STEPS = {
  build: ['Planned', 'Request written', 'Picked up', 'Coding', 'Tests and checks', 'Reviews', 'Pull request ready', 'Your approval', 'Merged'],
  deploy: ['Request written', 'Picked up', 'Preview deploy', 'Health check', 'Your approval', 'Live'],
  merge: ['Request written', 'Picked up', 'Merge and checks', 'Merged'],
  harden: ['Request written', 'Picked up', 'Checks and fixes', 'Pull request ready', 'Your approval'],
  pentest: ['Request written', 'Picked up', 'Scope check', 'Testing', 'Report ready'],
};
const STATES = ['running', 'waiting', 'blocked', 'done'];

const now = () => new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
const scrub = (s, n = 120) => String(s ?? '').replace(/[\r\n\t]+/g, ' ').replace(/[A-Za-z0-9_\-+/=]{24,}/g, '[hidden]').slice(0, n);

function findPointer(start) {
  let dir = path.resolve(start || process.cwd());
  for (let i = 0; i < 10; i++) {
    const f = path.join(dir, POINTER);
    if (fs.existsSync(f)) return readPointer(f);
    const up = path.dirname(dir);
    if (up === dir) break;
    dir = up;
  }
  return null;
}
// A desktop Code session often runs in its own folder and works in the checkout by full path.
// So the project is found three ways: the session's folder, the file a tool touched, and then
// a small note per session (in the home folder) of the checkout that session last touched.
const CACHE_DIR = path.join(os.homedir(), '.pf-activity');
const sessKey = (id) => (typeof id === 'string' ? id.replace(/[^A-Za-z0-9_-]/g, '').slice(-40) : '');
function pointerFile(start) {
  let dir = path.resolve(start);
  for (let i = 0; i < 10; i++) {
    const f = path.join(dir, POINTER);
    if (fs.existsSync(f)) return f;
    const up = path.dirname(dir);
    if (up === dir) break;
    dir = up;
  }
  return null;
}
function resolve(d) {
  const key = sessKey(d.session_id);
  const i = d.tool_input || {};
  const touched = [i.file_path, i.notebook_path].find((x) => typeof x === 'string' && path.isAbsolute(x));
  for (const start of [d.cwd, touched && path.dirname(touched)]) {
    if (typeof start !== 'string' || !start) continue;
    const f = pointerFile(start);
    const p = f && readPointer(f);
    if (p) {
      if (key) { try { fs.mkdirSync(CACHE_DIR, { recursive: true }); fs.writeFileSync(path.join(CACHE_DIR, key + '.json'), JSON.stringify({ v: 1, pointer: f })); } catch {} }
      return p;
    }
  }
  if (!key) return null;
  try {
    const c = JSON.parse(fs.readFileSync(path.join(CACHE_DIR, key + '.json'), 'utf8'));
    return c.v === 1 && typeof c.pointer === 'string' && path.basename(c.pointer) === POINTER && fs.existsSync(c.pointer) ? readPointer(c.pointer) : null;
  } catch { return null; }
}
function readPointer(f) {
  try {
    const p = JSON.parse(fs.readFileSync(f, 'utf8'));
    if (p.v !== 1 || !NAME.test(p.slug) || !NAME.test(p.lane) || typeof p.project_dir !== 'string') return null;
    if (path.basename(p.project_dir) !== p.slug) return null;
    if (!fs.existsSync(path.join(p.project_dir, 'factory.json'))) return null;
    return p;
  } catch { return null; }
}
function append(p, ev) {
  const dir = path.join(p.project_dir, 'activity');
  fs.mkdirSync(dir, { recursive: true });
  const f = path.join(dir, `${p.lane}.jsonl`);
  try { if (fs.statSync(f).size > MAX_LOG) fs.renameSync(f, path.join(dir, `${p.lane}.1.jsonl`)); } catch {}
  fs.appendFileSync(f, JSON.stringify({ v: 1, ts: now(), slug: p.slug, lane: p.lane, ...ev }) + '\n');
}
function rel(file, cwd) {
  if (typeof file !== 'string' || !file) return undefined;
  const r = path.relative(cwd || process.cwd(), file);
  return scrub(r.startsWith('..') ? path.basename(file) : r.split(path.sep).join('/'));
}
function fromHook(d, p) {
  const ev = { event: String(d.hook_event_name || 'unknown') };
  if (typeof d.session_id === 'string') ev.session = d.session_id.slice(-8);
  if (ev.event === 'PostToolUse') {
    const t = String(d.tool_name || ''), i = d.tool_input || {};
    ev.tool = t.replace(/[^A-Za-z0-9_.:-]/g, '').slice(0, 80);          // a tool's name is a name, not a value: never masked, only cleaned
    if (t === 'Bash' || t === 'PowerShell') ev.what = scrub(i.description) || undefined;        // the description, never the command
    else if (['Edit', 'Write', 'Read', 'NotebookEdit'].includes(t)) ev.what = rel(i.file_path || i.notebook_path, d.cwd);
    else if (t === 'Skill') ev.what = scrub(i.skill, 80) || undefined;
  } else if (ev.event === 'UserPromptSubmit') {
    const m = typeof d.prompt === 'string' ? d.prompt.trim().match(/^\/(pf-[a-z-]+)(?:\s+([a-z0-9-]+))?(?:\s+(build|merge|deploy|harden|pentest|doctor|seat|notify|confirm|show|release))?/) : null;
    if (!m) return null;                                                   // only factory commands, never free text
    const VERBS = ['seat', 'notify', 'confirm', 'show', 'release', 'doctor'];
    ev.what = [m[1], m[2] === p.slug || VERBS.includes(m[2]) ? m[2] : null, m[3]].filter(Boolean).join(' ');   // a word that is not this project's name is not logged
  } else if (ev.event === 'SessionStart') {
    ev.what = scrub(d.source, 20) || undefined;
  }
  return ev;
}
function cmdLink(projectDir, slug, lane) {
  if (!NAME.test(slug || '') || !NAME.test(lane || '')) throw new Error('slug and lane must be lower-case letters, digits and dashes');
  const dir = path.resolve(projectDir || '');
  if (path.basename(dir) !== slug) throw new Error('the folder name must be the project slug');
  if (!fs.existsSync(path.join(dir, 'factory.json'))) throw new Error('no factory.json in that folder');
  const here = process.cwd();
  fs.writeFileSync(path.join(here, POINTER), JSON.stringify({ v: 1, project_dir: dir, slug, lane }, null, 2) + '\n');
  try {                                                                    // keep the pointer out of git, without touching .gitignore
    const ex = path.join(here, '.git', 'info', 'exclude');
    if (fs.existsSync(path.dirname(ex))) {
      const cur = fs.existsSync(ex) ? fs.readFileSync(ex, 'utf8') : '';
      if (!cur.split(/\r?\n/).includes(POINTER)) fs.appendFileSync(ex, (cur && !cur.endsWith('\n') ? '\n' : '') + POINTER + '\n');
    }
  } catch {}
  append({ project_dir: dir, slug, lane }, { event: 'link' });
  console.log(`activity log on: ${slug} / ${lane}`);
}
function cmdUnlink() {
  const f = path.join(process.cwd(), POINTER);
  const p = fs.existsSync(f) ? readPointer(f) : null;
  if (p) append(p, { event: 'unlink' });
  if (fs.existsSync(f)) fs.unlinkSync(f);
  console.log('activity log off');
}
function cmdStep(kind, n, rest) {
  const p = findPointer();
  if (!p) { console.log('no activity pointer here: step not marked'); return; }
  const steps = STEPS[kind];
  const step = Number(n);
  if (!steps || !Number.isInteger(step) || step < 1 || step > steps.length) throw new Error(`usage: step <${Object.keys(STEPS).join('|')}> <number> [${STATES.join('|')}] [--task <id>] [--done <n> --of <n>]`);
  let state = 'running', task = null, done = null, of = null;
  for (let i = 0; i < rest.length; i++) {
    if (STATES.includes(rest[i])) state = rest[i];
    else if (rest[i] === '--task') task = scrub(rest[++i], 24);
    else if (rest[i] === '--done') done = Number(rest[++i]);
    else if (rest[i] === '--of') of = Number(rest[++i]);
  }
  const f = path.join(p.project_dir, `PROGRESS-${p.lane}.json`);
  let prev = null; try { prev = JSON.parse(fs.readFileSync(f, 'utf8')); } catch {}
  const same = prev && prev.kind === kind && prev.step === step && prev.state === state;
  const out = { format: 'PF-PROGRESS v1', project: p.slug, lane: p.lane, kind, task: task ?? (prev && prev.kind === kind ? prev.task ?? null : null), steps, step, name: steps[step - 1], state, since: same ? prev.since : now(), updated: now() };
  if (Number.isFinite(done) && Number.isFinite(of) && of > 0) out.within = { done, of };
  const tmp = f + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(out, null, 2) + '\n'); fs.renameSync(tmp, f);
  if (!same) append(p, { event: 'step', kind, step, of: steps.length, name: out.name, state, ...(out.task ? { task: out.task } : {}) });
  console.log(`step ${step} of ${steps.length}: ${out.name} (${state})`);
}
async function hook() {
  let raw = ''; for await (const c of process.stdin) raw += c;
  const d = JSON.parse(raw || '{}');
  try { fs.mkdirSync(CACHE_DIR, { recursive: true }); fs.writeFileSync(path.join(CACHE_DIR, 'last-hook.json'), JSON.stringify({ v: 1, ts: now(), event: String(d.hook_event_name || 'unknown').slice(0, 40) })); } catch {}   // proof that the hook fires at all
  const p = resolve(d);
  if (!p) return;
  const ev = fromHook(d, p);
  if (ev) append(p, ev);
}

const [cmd, ...a] = process.argv.slice(2);
if (cmd === 'link' || cmd === 'unlink' || cmd === 'step') {
  try { cmd === 'link' ? cmdLink(a[0], a[1], a[2]) : cmd === 'unlink' ? cmdUnlink() : cmdStep(a[0], a[1], a.slice(2)); }
  catch (e) { console.log(`not done: ${e.message}`); process.exitCode = 1; }
} else if (cmd === 'steps') {
  console.log(JSON.stringify(STEPS));
} else {
  hook().catch(() => {}).finally(() => { process.exitCode = 0; });       // a logger never fails the work
}
