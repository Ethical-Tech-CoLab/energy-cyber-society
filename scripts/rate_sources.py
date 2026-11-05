#!/usr/bin/env python3
"""Rate every source the society can read (feeds + Where-to-look entries) on five criteria and
write docs/data/source_catalogue.json for the Library. Criteria (0-3 each, 15 max):
  primacy     3 primary/victim/government, 2 wire or established press with named sources, 1 vendor research or trade press, 0 commentary/preprint
  independence 3 no product to sell and no party to the story, 2 editorially independent but vendor-funded, 1 vendor-owned or vendor-funded, 0 party to the story
  energy_focus 3 energy/OT specialist, 2 regular energy coverage, 1 occasional, 0 general
  timeliness  3 same-day, 2 daily, 1 weekly, 0 slow/irregular
  verifiability 3 primary docs linked and reachable, 2 names sources, 1 sometimes, 0 anonymous/unsourced
Delivery evidence is measured from this run: items contributed, pulls blocked, feed errors.
Scores are a person's judgement encoded as data; edit the overrides in agents/source_ratings.json."""
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; D = ROOT / "docs/data"
src = json.loads((ROOT / "sources.json").read_text()); news = json.loads((D / "news.json").read_text())
look = json.loads((ROOT / "agents/where_to_look.json").read_text())
over_p = ROOT / "agents/source_ratings.json"; over = json.loads(over_p.read_text()) if over_p.exists() else {"ratings": {}}
perf = {}
try: perf = json.loads((D / "sources.json").read_text()).get("source_performance", {})
except Exception: pass
BY_TYPE = {"government": (3, 3, 2, 2, 3), "regulator": (3, 3, 3, 1, 3), "wire": (2, 3, 1, 3, 2), "trade press": (1, 2, 2, 3, 2), "industry press": (1, 2, 3, 2, 2), "tech press": (1, 2, 1, 3, 2), "independent": (2, 3, 1, 2, 2), "vendor-owned press": (2, 1, 1, 3, 2), "vendor research": (1, 1, 3, 2, 2), "research preprints": (0, 3, 1, 3, 1), "think tank": (1, 2, 1, 1, 2), "magazine": (1, 2, 1, 1, 2), "academic": (1, 3, 1, 0, 2)}
CRIT = ["primacy", "independence", "energy_focus", "timeliness", "verifiability"]
def tier(score): return "A: check first" if score >= 12 else "B: check daily" if score >= 9 else "C: discovery only" if score >= 6 else "D: context"
out = []
for s in src["sources"]:
    base = list(BY_TYPE.get(s["type"], (1, 2, 1, 2, 2))); o = over["ratings"].get(s["id"], {})
    for i, c in enumerate(CRIT):
        if c in o: base[i] = o[c]
    p = perf.get(s["name"], {}); score = sum(base)
    out.append({"id": s["id"], "name": s["name"], "kind": "feed (read automatically)", "type": s["type"], "country": s["country"], "url": s["url"], "bias_note": s["bias_note"], "scores": dict(zip(CRIT, base)), "score": score, "tier": tier(score), "best_for": o.get("best_for", ""), "delivery": {"energy_items": p.get("energy_items", 0), "wide_items": p.get("wide_items", 0), "feed": p.get("feed", "n/a"), "pulls_blocked": p.get("pulls_blocked", 0)}, "verified": o.get("verified", "automatic rating from type; not yet reviewed by a person")})
for sec in look["sections"]:
    for e in sec["entries"]:
        if not e.get("url"): continue
        o = over["ratings"].get(e["name"], {}); base = [o.get(c, d) for c, d in zip(CRIT, (3, 3, 2, 0, 3) if "primary" in sec["tier"] else (1, 2, 2, 0, 2))]
        score = sum(base)
        out.append({"id": e["name"], "name": e["name"], "kind": "manual (Where to look)", "type": sec["tier"], "country": "", "url": e["url"], "bias_note": e["why"] + " [" + e.get("access", "") + "]", "scores": dict(zip(CRIT, base)), "score": score, "tier": tier(score), "best_for": o.get("best_for", sec["question"]), "delivery": {"energy_items": 0, "wide_items": 0, "feed": "not a feed", "pulls_blocked": 0}, "verified": o.get("verified", "listed for manual reading; rating from section tier")})
out.sort(key=lambda x: (-x["score"], x["name"]))
(D / "source_catalogue.json").write_text(json.dumps({"rated_at": datetime.now(timezone.utc).isoformat(), "criteria": {"primacy": "primary document > wire > vendor/trade > commentary", "independence": "no product to sell, no party to the story", "energy_focus": "energy/OT specialist > regular > occasional > general", "timeliness": "same-day > daily > weekly > slow", "verifiability": "links primary documents and names sources"}, "tiers": {"A: check first": ">=12 of 15", "B: check daily": "9-11", "C: discovery only": "6-8", "D: context": "<6"}, "sources": out}, indent=1, ensure_ascii=False))
print(f"catalogue: {len(out)} sources; A={sum(1 for x in out if x['tier'].startswith('A'))} B={sum(1 for x in out if x['tier'].startswith('B'))} C={sum(1 for x in out if x['tier'].startswith('C'))} D={sum(1 for x in out if x['tier'].startswith('D'))}")
