#!/usr/bin/env python3
"""Draw a weekly sample of items for a human to grade against the pulled primaries
(REVIEW.md finding 3). Writes docs/data/eval_sample.json with a checklist per item; the grader
fills 'human' fields and the agreement rate appears on the dashboard."""
import json, random
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
b = json.loads((ROOT / "docs/data/briefing.json").read_text())
items = b.get("items", []); random.seed(b.get("generated_at", "")); sample = random.sample(items, min(10, len(items)))
out = {"drawn_at": datetime.now(timezone.utc).isoformat(), "run": b.get("generated_at"), "instructions": "For each item open the sources, then answer each check with true/false and a note. Leave null if you cannot tell. Save the file; the dashboard reads it.",
       "items": [{"headline": it["headline"], "sources": it.get("sources", []), "system": {"severity": it["severity"], "ot_impact": it["ot_impact"], "reliability": it["source_reliability"], "credibility": it["info_credibility"], "claim_vs_confirmed": it["claim_vs_confirmed"]},
                  "human": {"facts_match_sources": None, "ot_impact_correct": None, "severity_reasonable": None, "trust_grades_reasonable": None, "nothing_invented": None, "note": ""}} for it in sample]}
(ROOT / "docs/data/eval_sample.json").write_text(json.dumps(out, indent=1, ensure_ascii=False)); print(f"sample of {len(sample)} items written for human grading")
