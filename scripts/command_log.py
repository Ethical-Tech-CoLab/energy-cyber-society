#!/usr/bin/env python3
"""Cyber Command: append-only log of every flag raised by the residents or the checks.

Runs after run_agents.py and pull_sources.py. Deterministic rules scan the briefing and the
pulled sources and append events to docs/data/command_log.json. Nothing is ever deleted;
a resolved flag gets a later 'resolved' event. Event types:
  unsourced-claim      a briefing sentence with no (Source) citation
  single-source        an item resting on one outlet
  contradiction        cross-check verdict says the primary and the outlet differ
  downgrade            the Verifier downgraded an item
  unverifiable         a source page was blocked (403) or a claim is marked [unverified]
  fallback-run         the run had no model (headlines only)
  validator-fail       validate.py reported errors
  hand-curated         the briefing was written in a live session, not by the scheduled run
  invented-suspected   a claim names a story that is not in the fetched bundle
"""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "docs/data"
LOG = D / "command_log.json"
b = json.loads((D / "briefing.json").read_text())
news = json.loads((D / "news.json").read_text())
src = json.loads((D / "sources.json").read_text()) if (D / "sources.json").exists() else {"items": {}}
log = json.loads(LOG.read_text()) if LOG.exists() else {"events": []}
now = datetime.now(timezone.utc).isoformat()
run_id = b.get("generated_at", now)
seen = {(e["run"], e["type"], e.get("item", ""), e.get("agent", "")) for e in log["events"]}
events = []
def flag(type_, agent, item, detail, severity="warn"):
    key = (run_id, type_, item or "", agent or "")
    if key in seen: return
    seen.add(key); events.append({"at": now, "run": run_id, "type": type_, "agent": agent, "item": item, "detail": detail, "severity": severity, "status": "open"})

if b.get("model", "").startswith("fallback"): flag("fallback-run", "system", "", "No model ran; briefing is headlines only.", "info")
if "session" in b.get("model", ""): flag("hand-curated", "system", "", f"Briefing curated in a live session ({b['model']}), not by the scheduled run.", "info")
titles = " ".join((s["title"] + " " + s["summary"]).lower() for s in news["energy"] + news["wide"])
for aid, ag in b.get("agents", {}).items():
    for sent in re.split(r"(?<=[.!?])\s+", ag.get("briefing", "")):
        if len(sent) > 60 and not re.search(r"\([A-Z][^)]{2,}\)", sent) and not re.search(r"\b(I cannot verify|headlines|no (confirmed|story)|next run|audit|where to look|allowlisted)\b", sent, re.I):
            flag("unsourced-claim", aid, sent[:90], "Sentence in a briefing with no (Source) citation.", "warn")
for it in b.get("items", []):
    h = it["headline"]
    if len({s["name"].split(" (")[0] for s in it.get("sources", [])}) <= 1: flag("single-source", "reporter", h, "Item rests on a single outlet.", "warn")
    for l in it.get("labels", []):
        if "[unverified]" in l: flag("unverifiable", "verifier", h, l, "warn")
    # invented-suspected: headline words not present anywhere in the bundle
    words = [w for w in re.findall(r"[a-z]{5,}", h.lower()) if w not in {"attack", "cyber", "against", "critical", "energy", "sector"}]
    if words and sum(w in titles for w in words) / len(words) < 0.3:
        flag("invented-suspected", "reporter", h, "Fewer than 30% of the headline's key words appear in the fetched bundle. Check that this item exists in news.json.", "critical")
for h, rec in src.get("items", {}).items():
    for s in rec.get("sources", []):
        if s.get("status") != 200: flag("unverifiable", "librarian", h, f"Source page blocked or failed: {s['name']} ({s.get('status')}).", "warn")
xc = b.get("verification", {}).get("crosschecks", {})
for h, c in xc.items():
    if c.get("differ") and c["differ"] not in ("n/a", "") and not c["differ"].lower().startswith("single outlet"):
        flag("contradiction", "verifier", h, f"Cross-check: {c['differ'][:160]}", "warn")
for h, v in b.get("verification", {}).get("verdicts", {}).items():
    if v["verdict"].lower().startswith("downgrade"): flag("downgrade", "verifier", h, v["reason"], "warn")
    if v["verdict"].lower().startswith("retire"): flag("retire", "verifier", h, v["reason"], "critical")
log["events"].extend(events)
log["updated_at"] = now
LOG.write_text(json.dumps(log, indent=1, ensure_ascii=False))
# per-run history for the dashboard (append-only, one row per run)
H = D / "history.json"
hist = json.loads(H.read_text()) if H.exists() else {"runs": []}
if not any(r["run"] == run_id for r in hist["runs"]):
    from collections import Counter
    items = b.get("items", [])
    hist["runs"].append({"run": run_id, "model": b.get("model"), "energy": len(news["energy"]), "wide": len(news["wide"]), "items": len(items),
        "severity": dict(Counter(i.get("severity") for i in items)), "ot_impact": dict(Counter(i.get("ot_impact") for i in items)),
        "subsector": dict(Counter(i.get("subsector") for i in items)), "country": dict(Counter(i.get("country") for i in items)),
        "event_type": dict(Counter(i.get("event_type") for i in items)), "action": dict(Counter(i.get("recommended_action") for i in items)),
        "reliability": dict(Counter(i.get("source_reliability") for i in items)), "credibility": dict(Counter(str(i.get("info_credibility")) for i in items)),
        "single_source": sum(1 for i in items if len({s["name"].split(" (")[0] for s in i.get("sources", [])}) <= 1),
        "flags": dict(Counter(e["type"] for e in events)), "feeds_ok": sum(1 for s in news["sources"]) - len(news.get("errors", [])), "feeds_err": len(news.get("errors", [])),
        "usage": b.get("usage")})
    H.write_text(json.dumps(hist, indent=1, ensure_ascii=False))
print(f"command log: +{len(events)} events, {len(log['events'])} total")
