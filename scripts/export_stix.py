#!/usr/bin/env python3
"""Export the board as a STIX 2.1 bundle (docs/data/stix.json): one report per item, plus
vulnerability, indicator, threat-actor, malware and attack-pattern objects where the record
names them. Deterministic ids (uuid5) so repeated runs update rather than duplicate."""
import json, uuid
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
b = json.loads((ROOT / "docs/data/briefing.json").read_text())
NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
def sid(kind, key): return f"{kind}--{uuid.uuid5(NS, kind + ':' + key)}"
objs = {}
ident = {"type": "identity", "spec_version": "2.1", "id": sid("identity", "energy-cyber-society"), "created": now, "modified": now, "name": "Energy Cyber Society", "identity_class": "system", "description": "Seven LLM residents curating energy-sector cyber news from an allowlist of credible sources. Confidence per object follows the item's Admiralty grading."}
objs[ident["id"]] = ident
CONF = {"1": 90, "2": 70, "3": 50, "4": 30, "5": 10, "6": 0}
for it in b.get("items", []):
    refs = []
    for c in it.get("cves", []):
        v = {"type": "vulnerability", "spec_version": "2.1", "id": sid("vulnerability", c), "created": now, "modified": now, "name": c, "external_references": [{"source_name": "cve", "external_id": c}]}
        objs[v["id"]] = v; refs.append(v["id"])
        ind = {"type": "indicator", "spec_version": "2.1", "id": sid("indicator", c), "created": now, "modified": now, "name": f"Exploitation of {c}", "pattern": f"[vulnerability:name = '{c}']", "pattern_type": "stix", "valid_from": now, "indicator_types": ["malicious-activity"]}
        objs[ind["id"]] = ind; refs.append(ind["id"])
    for i in it.get("indicators", []):
        if i.get("type") == "cve": continue
        pat = {"ipv4": f"[ipv4-addr:value = '{i['value']}']", "domain": f"[domain-name:value = '{i['value']}']", "sha256": f"[file:hashes.'SHA-256' = '{i['value']}']", "url": f"[url:value = '{i['value']}']"}.get(i["type"])
        if pat:
            ind = {"type": "indicator", "spec_version": "2.1", "id": sid("indicator", i["value"]), "created": now, "modified": now, "name": i["value"], "pattern": pat, "pattern_type": "stix", "valid_from": now, "indicator_types": ["malicious-activity"], "description": f"Source: {i.get('source','')}"}
            objs[ind["id"]] = ind; refs.append(ind["id"])
    if it.get("actor"):
        a = {"type": "threat-actor", "spec_version": "2.1", "id": sid("threat-actor", it["actor"]), "created": now, "modified": now, "name": it["actor"], "threat_actor_types": [it.get("actor_type", "unknown").replace(" ", "-")], "description": f"Attribution {it.get('attribution_confidence')} by {it.get('attributed_by') or 'nobody named'}."}
        objs[a["id"]] = a; refs.append(a["id"])
    if it.get("malware"):
        m = {"type": "malware", "spec_version": "2.1", "id": sid("malware", it["malware"]), "created": now, "modified": now, "name": it["malware"], "is_family": False}
        objs[m["id"]] = m; refs.append(m["id"])
    for t in it.get("ttps", []):
        ap = {"type": "attack-pattern", "spec_version": "2.1", "id": sid("attack-pattern", t["id"]), "created": now, "modified": now, "name": t["name"], "external_references": [{"source_name": "mitre-attack-ics" if t["id"].startswith("T0") else "mitre-attack", "external_id": t["id"]}]}
        objs[ap["id"]] = ap; refs.append(ap["id"])
    r = {"type": "report", "spec_version": "2.1", "id": sid("report", it["headline"]), "created": now, "modified": now, "created_by_ref": ident["id"], "name": it["headline"], "report_types": ["threat-report"], "published": now,
         "description": it.get("so_what", ""), "confidence": CONF.get(str(it.get("info_credibility")), 0), "labels": [it.get("severity", ""), it.get("subsector", ""), it.get("ot_impact", ""), it.get("event_type", "")],
         "external_references": [({"source_name": s["name"], "url": s["url"]} if s.get("url") else {"source_name": s["name"]}) for s in it.get("sources", [])],
         "object_refs": refs or [ident["id"]], "x_ecs": {"source_reliability": it.get("source_reliability"), "info_credibility": it.get("info_credibility"), "claim_vs_confirmed": it.get("claim_vs_confirmed"), "labels": it.get("labels", []), "value_chain": it.get("value_chain"), "recommended_action": it.get("recommended_action")}}
    objs[r["id"]] = r
bundle = {"type": "bundle", "id": sid("bundle", b.get("generated_at", now)), "objects": list(objs.values())}
(ROOT / "docs/data/stix.json").write_text(json.dumps(bundle, indent=1, ensure_ascii=False))
print(f"stix: {len(bundle['objects'])} objects")
