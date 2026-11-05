#!/usr/bin/env python3
"""Append-only archive of every run. Copies the run's data files into
docs/archive/<run-id>/ and updates docs/archive/index.json and ARCHIVE.md. Nothing is ever
overwritten or deleted; re-running for the same run id is a no-op."""
import json, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "docs/data"; A = ROOT / "docs/archive"
b = json.loads((D / "briefing.json").read_text())
run_id = (b.get("generated_at") or "unknown")[:16].replace(":", "-")
dest = A / run_id
idx_p = A / "index.json"
idx = json.loads(idx_p.read_text()) if idx_p.exists() else {"runs": []}
if dest.exists():
    print(f"archive: {run_id} already archived"); raise SystemExit(0)
dest.mkdir(parents=True)
files = ["briefing.json", "news.json", "sources.json", "command_log.json", "stix.json", "history.json", "personas.json", "sectors.json", "where_to_look.json", "buildings.json", "ai_market.json", "grid_weather.json", "plants.json", "regulations.json", "risk_model.json"]
copied = []
for f in files:
    if (D / f).exists(): shutil.copy2(D / f, dest / f); copied.append(f)
for f in ["RULES.md", "INTELLIGENCE_ANALYSIS.md", "CURATION.md", "COST.md", "sources.json"]:
    src = ROOT / f
    if src.exists(): shutil.copy2(src, dest / ("repo_" + f)); copied.append("repo_" + f)
entry = {"run": run_id, "generated_at": b.get("generated_at"), "news_generated_at": b.get("news_generated_at"), "model": b.get("model"),
         "items": len(b.get("items", [])), "energy": b.get("counts", {}).get("energy"), "wide": b.get("counts", {}).get("wide"),
         "headline": (b.get("summary") or {}).get("headline", ""), "us_status": b.get("us_status", ""), "files": copied,
         "flags": len([e for e in json.loads((D / "command_log.json").read_text()).get("events", []) if e.get("run") == b.get("generated_at")]) if (D / "command_log.json").exists() else 0}
idx["runs"].append(entry); idx["runs"].sort(key=lambda r: r["run"])
idx_p.write_text(json.dumps(idx, indent=1, ensure_ascii=False))
md = ["# Archive of every run", "", "Append-only. One folder per run with the complete data set as it was published, plus the rules, procedure and playbook in force at the time. Nothing here is edited after the fact.", ""]
for r in idx["runs"]:
    md.append(f"- **{r['run']}** · {r['model']} · {r['items']} items, {r['energy']} energy / {r['wide']} wide stories, {r['flags']} flags · [{r['headline'][:90]}](archive/{r['run']}/briefing.json) · [Gazette](gazette.html?run={r['run']})")
(ROOT / "docs/ARCHIVE.md").write_text("\n".join(md) + "\n")
print(f"archive: {run_id} saved ({len(copied)} files); {len(idx['runs'])} runs indexed")
