#!/usr/bin/env python3
"""Automated UX and accessibility audit of docs/. Writes docs/data/ux_audit.json: findings with
severity and a suggested fix. The Engineer reads this to pick work; the Workshop panel shows it."""
import json, re
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; D = ROOT / "docs"
html = (D / "index.html").read_text(); js = (D / "game.js").read_text(); css = (D / "style.css").read_text()
F = []
def f(sev, what, fix, where): F.append({"severity": sev, "finding": what, "fix": fix, "where": where})
buttons = re.findall(r'<button id="btn-[^"]+" class="pix[^"]*">', html)
if len(buttons) > 10: f("high", f"{len(buttons)} top-level buttons in the control bar", "group into menus: Read (brief, summary, gazette), Analyse (board, dashboard, collections, scenarios, research), Verify (incident desk, references, history), About (methodology, rules, limitations, register, human touch, cost, bank), Settings", "docs/index.html .hud-actions")
dialogs = re.findall(r'<dialog id="([^"]+)"', html)
for d in dialogs:
    if f'id="{d}"' in html and 'aria-label' not in html.split(f'id="{d}"')[1][:200] and '<h2' not in html.split(f'id="{d}"')[1][:400]: f("low", f"dialog {d} has no heading in its first 400 chars", "add an <h2>", "docs/index.html")
if 'innerHTML' in js and js.count('innerHTML') > 40: f("medium", f"{js.count('innerHTML')} innerHTML assignments in one file", "render helpers; keep esc() on every interpolation", "docs/game.js")
lines = js.count('\n')
if lines > 1000: f("medium", f"game.js is {lines} lines in one file", "split by view: town.js, panels.js, dialogs.js, data.js; keep window.ECS", "docs/game.js")
if "prefers-color-scheme" not in css: f("low", "no light-mode support; page is dark only", "acceptable by design; document it, or add tokens for light mode", "docs/style.css")
if "@media(max-width" not in css and "@media (max-width" not in css: f("medium", "no narrow-screen media query beyond the grid breakpoint", "test at 390px; collapse the control bar into a menu button", "docs/style.css")
if "catch(() => null)" in js and "fetch error" not in js and "could not load" not in js.lower(): f("medium", "data loads fail silently (catch(() => null)); the page shows empty panels with no message", "show a visible 'could not load X' line in the HUD when a fetch fails", "docs/game.js boot()")
if "font-family:var(--font-pix)" in css and css.count("font-family:var(--font-pix)") > 6: f("low", "pixel font used in many places", "keep it to the title, button labels and tags; paragraphs in the mono font", "docs/style.css")
if "aria-live" not in html: f("low", "no live region for chat updates", "aria-live=polite on #chat", "docs/index.html")
if "<title>" in html and "tabindex" not in html: f("low", "canvas objects are not focusable; the list view exists but is hidden in a <details>", "open the list view by default on narrow screens", "docs/index.html #listview")
out = {"audited_at": datetime.now(timezone.utc).isoformat(), "findings": F, "counts": {s: sum(1 for x in F if x["severity"] == s) for s in ("high", "medium", "low")}}
(D / "data/ux_audit.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(f"ux audit: {len(F)} findings ({out['counts']})")
for x in F: print(f"  [{x['severity']}] {x['finding']}")
