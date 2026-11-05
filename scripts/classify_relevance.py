#!/usr/bin/env python3
"""Second-stage relevance pass (REVIEW.md finding 4): a cheap model labels every fetched story
with the taxonomy after the keyword pre-filter. With no key it is a no-op and says so. Moves
stories between the energy and wide buckets and records the label on each story."""
import json, os, sys, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; NP = ROOT / "docs/data/news.json"
news = json.loads(NP.read_text()); sch = json.loads((ROOT / "agents/schema.json").read_text())["taxonomy"]
if not os.environ.get("ANTHROPIC_API_KEY"):
    news["relevance_pass"] = "skipped: no ANTHROPIC_API_KEY; keyword pre-filter only"; NP.write_text(json.dumps(news, indent=1, ensure_ascii=False)); print(news["relevance_pass"]); sys.exit(0)
import anthropic
client = anthropic.Anthropic(); model = os.environ.get("ECS_CLASSIFIER_MODEL", "claude-haiku-5-5")
stories = [dict(s, _b="energy") for s in news["energy"]] + [dict(s, _b="wide") for s in news["wide"]]
labels = {}
for i in range(0, len(stories), 25):
    chunk = stories[i:i + 25]
    prompt = ("Label each story. Output ONLY a JSON array of {\"i\": index, \"energy_cyber\": true|false, \"subsector\": one of %s or null, \"reason\": short}. "
              "energy_cyber is true only if the story is about a cyber incident, vulnerability, threat actor, or cyber policy AND it concerns energy as defined: generation, grids, oil and gas, nuclear, renewables, storage, EV charging, pipelines, LNG and tanker shipping, interconnectors, data centres as load, industrial control systems, or connectivity gear used by operators.\n<<<DATA>>>\n%s\n<<<END>>>"
              % (json.dumps(sch["subsector"]), "\n".join(f"{j}. [{s['source_name']}] {s['title']} :: {s['summary'][:200]}" for j, s in enumerate(chunk))))
    r = client.messages.create(model=model, max_tokens=2000, messages=[{"role": "user", "content": prompt}])
    txt = "".join(bk.text for bk in r.content if bk.type == "text"); m = re.search(r"\[.*\]", txt, re.S)
    try:
        for row in json.loads(m.group(0)): labels[i + row["i"]] = row
    except Exception as e: print("chunk parse failed:", e, file=sys.stderr)
energy, wide, moved = [], [], 0
for j, s in enumerate(stories):
    lab = labels.get(j); b0 = s.pop("_b")
    if lab: s["classified"] = {"energy_cyber": lab.get("energy_cyber"), "subsector": lab.get("subsector"), "reason": lab.get("reason"), "model": model}
    target = "energy" if (lab and lab.get("energy_cyber")) else ("wide" if lab else b0)
    if target != b0: moved += 1
    (energy if target == "energy" else wide).append(s)
news["energy"], news["wide"] = energy, wide; news["relevance_pass"] = f"{model}: {len(labels)} labelled, {moved} moved"
NP.write_text(json.dumps(news, indent=1, ensure_ascii=False)); print(news["relevance_pass"])
