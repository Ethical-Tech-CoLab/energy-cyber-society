#!/usr/bin/env python3
"""Enrich every CVE on the board from NVD (CVSS, description, published) and CISA's KEV catalog
(exploited: yes/no, date added). Free public APIs, no key. Writes cve fields into items and a
docs/data/cves.json cache. This settles 'is it exploited?' from a government source instead of press."""
import json, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; D = ROOT / "docs/data"
b = json.loads((D / "briefing.json").read_text())
cache_p = D / "cves.json"; cache = json.loads(cache_p.read_text()) if cache_p.exists() else {"cves": {}, "kev_fetched_at": None}
UA = {"User-Agent": "energy-cyber-society/1.0 (research)"}
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r: return json.loads(r.read())
try:
    kev = get("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
    kev_ids = {v["cveID"]: v for v in kev.get("vulnerabilities", [])}; cache["kev_fetched_at"] = datetime.now(timezone.utc).isoformat(); cache["kev_count"] = len(kev_ids)
    print(f"KEV: {len(kev_ids)} entries", file=sys.stderr)
except Exception as e:
    kev_ids = None; print(f"KEV unreachable: {e}", file=sys.stderr)
for it in b.get("items", []):
    it["cve_details"] = []
    for c in it.get("cves", []):
        rec = cache["cves"].get(c)
        if not rec:
            try:
                nvd = get(f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={c}")
                v = (nvd.get("vulnerabilities") or [{}])[0].get("cve", {})
                metrics = v.get("metrics", {}); cvss = None
                for k in ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30"):
                    if metrics.get(k): cvss = {"version": k.replace("cvssMetric", ""), "score": metrics[k][0]["cvssData"].get("baseScore"), "severity": metrics[k][0]["cvssData"].get("baseSeverity") or metrics[k][0].get("baseSeverity")}; break
                rec = {"id": c, "nvd_found": bool(v), "published": v.get("published"), "last_modified": v.get("lastModified"), "status": v.get("vulnStatus"), "cvss": cvss, "description": next((d["value"] for d in v.get("descriptions", []) if d.get("lang") == "en"), None), "references": [r["url"] for r in v.get("references", [])][:8], "fetched_at": datetime.now(timezone.utc).isoformat()}
                time.sleep(6)  # NVD public rate limit without a key
            except Exception as e:
                rec = {"id": c, "nvd_found": False, "error": str(e)[:120], "fetched_at": datetime.now(timezone.utc).isoformat()}
            cache["cves"][c] = rec
        if kev_ids is not None:
            k = kev_ids.get(c); rec["kev"] = {"listed": bool(k), "date_added": k.get("dateAdded") if k else None, "ransomware_use": k.get("knownRansomwareCampaignUse") if k else None, "required_action": k.get("requiredAction") if k else None}
        it["cve_details"].append(rec)
        if rec.get("kev"): it["kev_listed"] = "true" if rec["kev"]["listed"] else "false (not in KEV as of %s)" % cache["kev_fetched_at"][:10]
        print(f"  {c}: nvd={'yes' if rec.get('nvd_found') else 'no'} cvss={rec.get('cvss')} kev={rec.get('kev', {}).get('listed')}", file=sys.stderr)
cache_p.write_text(json.dumps(cache, indent=1, ensure_ascii=False)); (D / "briefing.json").write_text(json.dumps(b, indent=1, ensure_ascii=False))
print("cve enrichment done")
