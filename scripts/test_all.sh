#!/usr/bin/env bash
# Runs every check that needs no API key. Exit non-zero on any failure. Wire into CI once the
# workflow can be pushed (gh token needs the workflow scope).
set -euo pipefail
cd "$(dirname "$0")/.."
echo "== python syntax"; python3 -m py_compile scripts/*.py
echo "== js syntax"; node -e "new Function(require('fs').readFileSync('docs/game.js','utf8'))"
echo "== dry-run pipeline"; python3 scripts/run_agents.py --dry-run --out /tmp/ecs-dry.json >/dev/null 2>&1 && python3 -c "import json;d=json.load(open('/tmp/ecs-dry.json'));assert len(d['agents'])==14 and d['items'] and d['conversations'] and d['verification'],'dry-run incomplete'"
echo "== validate published briefing"; python3 scripts/validate.py
echo "== ground truth"; python3 scripts/check_ground_truth.py
echo "== stix"; python3 scripts/export_stix.py >/dev/null && python3 -c "import json;d=json.load(open('docs/data/stix.json'));assert not [1 for o in d['objects'] for r in o.get('external_references',[]) if 'url' in r and r['url'] is None]"
echo "== page smoke (playwright, optional)"; python3 - <<'PY' || echo "playwright smoke skipped"
import subprocess,sys,time
try:
    from playwright.sync_api import sync_playwright
except ImportError: sys.exit(0)
srv=subprocess.Popen([sys.executable,'-m','http.server','8766'],cwd='docs',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
try:
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        pg.goto('http://localhost:8766/'); pg.wait_for_timeout(3000)
        assert pg.evaluate("ECS.agents.length")==14, 'agents'
        for btn in ['#btn-exec','#btn-summary','#btn-board','#btn-dash','#btn-command','#btn-refs']:
            pg.click(btn); pg.wait_for_timeout(200); pg.keyboard.press('Escape')
        assert not errs, errs
        b.close()
finally: srv.terminate()
print("page smoke ok")
PY
echo "ALL CHECKS PASSED"
