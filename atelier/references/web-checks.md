# Web platform checks — outdated or harmful web patterns, decided by code

Eleven rules, all checked by `scripts/web-check.mjs` in the Code plugin. Each was written from the page named beside it, opened and read on 23 November 2026, with the supporting words quoted. A rule whose page did not support it is not here. This is the factory's own check: it needs no outside tool, fetches nothing and reports nothing to anyone. It serves the "Modern platform first" rule in `code-simplicity.md`.

## How it runs
The Code session runs `node "${CLAUDE_PLUGIN_ROOT}/scripts/web-check.mjs" "<code checkout>"` on every web build, before the reviews step. It is read-only. A `FAIL` line is fixed before the result can say `status: ok`. The result carries its last line as `web-check:`. If it cannot be run, the result says `web-check: not run (<why>)` - never a pass. Test files and bundled or minified files are not judged; a skipped bundle is named.

| # | Rule | Source (MDN Web Docs, opened 23 Nov 2026) |
|---|---|---|
| W1 | No `document.write()`. | Document.write: "Use of the document.write() method is strongly discouraged." |
| W2 | No `unload` event. Use `pagehide` or `visibilitychange`. | Window unload event: "Developers should avoid using this event." |
| W3 | No `keyCode` on keyboard events. Use `key` or `code`. | KeyboardEvent.keyCode: "it's been deprecated for some time". |
| W4 | No `document.execCommand()`. | Document.execCommand: "Avoid using this feature in new projects." |
| W5 | No `substr()`. Use `slice()` or `substring()`. | String.prototype.substr: "advised to use the standard String.prototype.substring() and String.prototype.slice()". |
| W6 | No `escape()`. Use `encodeURIComponent()` or `encodeURI()`. | escape(): "Use encodeURIComponent() or encodeURI() if possible." |
| W7 | No mutation events (`DOMNodeInserted` and the rest). Use a `MutationObserver`. | MutationEvent: "deprecated in favor of mutation observers". |
| W8 | No `<center>`, `<font>` or `<marquee>`. Use CSS. | center: "has been deprecated"; font: "Avoid using this feature in new projects."; marquee: "deprecated and its use is strongly discouraged". |
| W9 | The page never stops people zooming in (`user-scalable=no`, or a maximum scale of 1 or less). | viewport meta: "Disabling zooming capabilities ... prevents people experiencing low vision". |
| W10 | The `<html>` element says which language the page is in (`lang`). | lang attribute: "WCAG Success Criterion 3.1.1 requires that a page language is specified". |
| W11 | A focus outline is never removed without something visible replacing it. | :focus: "Never just remove the focus outline (visible focus indicator) without replacing it". |

## Left out on purpose
One rule was considered and is not here: replacing `XMLHttpRequest` with `fetch`. The page read did not say so in its own words.

## What this check is not
It does not judge taste, layout or framework choice, and it does not replace the reviews. It finds eleven things that are wrong for certain.
