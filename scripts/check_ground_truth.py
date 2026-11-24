#!/usr/bin/env python3
"""Compare board items to tests/ground_truth.json; write agreement rate to docs/data/eval.json
and print mismatches. A falling rate is a blocker (REVIEW.md finding 3)."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
b = json.loads((ROOT / "docs/data/briefing.json").read_text()); gt = json.loads((ROOT / "tests/ground_truth.json").read_text())
res = []
for f in gt["facts"]:
    it = next((i for i in b.get("items", []) if f["match"].lower() in (i["headline"] + " " + " ".join(i.get("cves", []))).lower()), None)
    if not it: res.append({**f, "found": False, "ok": None, "actual": None}); continue  # retired from the board: not a miss
    if f["field"] == "cvss":
        actual = next((d.get("cvss", {}) or {}).get("score") for d in it.get("cve_details", []) if d.get("id") == f["match"])
    else: actual = it.get(f["field"])
    ok = (str(actual).lower().startswith(str(f["expect"]).lower()) if "expect" in f else f["expect_contains"].lower() in str(actual).lower())
    res.append({**f, "found": True, "ok": bool(ok), "actual": actual})
live = [r for r in res if r["found"]]
rate = sum(r["ok"] for r in live) / max(1, len(live))
ev_p = ROOT / "docs/data/eval.json"; ev = json.loads(ev_p.read_text()) if ev_p.exists() else {"runs": [], "human_samples": []}
ev["runs"].append({"at": datetime.now(timezone.utc).isoformat(), "run": b.get("generated_at"), "facts": len(live), "retired": len(res) - len(live), "agree": sum(r["ok"] for r in live), "rate": round(rate, 3), "mismatches": [{"match": r["match"], "field": r["field"], "expect": r.get("expect", r.get("expect_contains")), "actual": r["actual"]} for r in res if not r["ok"]]})
ev_p.write_text(json.dumps(ev, indent=1, ensure_ascii=False))
print(f"ground truth: {sum(r['ok'] for r in live)}/{len(live)} agree ({rate:.0%}); {len(res)-len(live)} facts belong to items retired from the board")
for r in live:
    if not r["ok"]: print(f"  MISMATCH {r['match']} {r['field']}: expected {r.get('expect', r.get('expect_contains'))!r}, got {r['actual']!r}")
if not live: print("  no ground-truth fact matches a live item: add facts for this run"); sys.exit(1)
sys.exit(0 if rate >= 0.8 else 1)
