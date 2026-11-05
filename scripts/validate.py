#!/usr/bin/env python3
"""Fail if the briefing is malformed: every resident present, every item on-taxonomy, every item sourced."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
b = json.loads((ROOT / "docs/data/briefing.json").read_text())
p = json.loads((ROOT / "agents/personas.json").read_text())
sch = json.loads((ROOT / "agents/schema.json").read_text())["taxonomy"]
errs = []
for a in p["agents"]:
    ag = b.get("agents", {}).get(a["id"])
    if not ag: errs.append(f"missing agent {a['id']}"); continue
    for k in ("briefing", "answers", "bubble"):
        if not ag.get(k): errs.append(f"{a['id']} missing {k}")
    for q in a["questions"]:
        if q not in ag.get("answers", {}): errs.append(f"{a['id']} missing answer: {q[:40]}")
for it in b.get("items", []):
    h = it.get("headline", "?")[:50]
    for f in ("subsector", "value_chain", "event_type", "ot_impact", "actor_type", "attribution_confidence", "severity", "recommended_action"):
        if it.get(f) not in sch[f]: errs.append(f"item '{h}': {f}={it.get(f)!r} not in taxonomy")
    if not it.get("sources"): errs.append(f"item '{h}': no sources")
    if not it.get("so_what"): errs.append(f"item '{h}': no so_what")
    scg = it.get("scoring", {})
    if not (scg.get("severity", {}).get("rationale") and scg.get("reliability_rationale")): errs.append(f"item '{h}': missing scoring rationale")
if "us_status" not in b: errs.append("missing us_status")
sm = b.get("summary")
if sm:
    if not sm.get("bullets"): errs.append("summary has no bullets")
    for x in sm.get("bullets", []):
        if not x.get("sources"): errs.append(f"summary bullet without sources: {x.get('text','')[:40]}")
if (ROOT / "docs/data/buildings.json").read_text() != (ROOT / "agents/buildings.json").read_text(): errs.append("docs/data/buildings.json differs from agents/buildings.json (cp it)")
bl = json.loads((ROOT / "agents/buildings.json").read_text())["buildings"]
for a in p["agents"]:
    if a["building"] not in bl: errs.append(f"{a['id']}'s building '{a['building']}' has no entry in buildings.json")
if (ROOT / "docs/data/where_to_look.json").read_text() != (ROOT / "agents/where_to_look.json").read_text(): errs.append("docs/data/where_to_look.json differs from agents/where_to_look.json (cp it)")
if (ROOT / "docs/data/personas.json").read_text() != json.dumps(p, indent=1, ensure_ascii=False):
    errs.append("docs/data/personas.json differs from agents/personas.json (run: python3 -c \"import json;json.dump(json.load(open('agents/personas.json')),open('docs/data/personas.json','w'),indent=1,ensure_ascii=False)\")")
if errs:
    print("\n".join("FAIL " + e for e in errs)); sys.exit(1)
print(f"ok: {len(b['agents'])} agents, {len(b.get('items', []))} items, {len(b.get('conversations', []))} conversations")
