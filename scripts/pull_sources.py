#!/usr/bin/env python3
"""Pull the direct source for every board item and every allowlisted story behind it.

For each item in docs/data/briefing.json, fetch each source URL, extract the article text,
keep the sentences that overlap the item's headline and so-what, and look inside the page
for links to PRIMARY documents (government, regulator, vendor advisory, victim statement).
Those primary links are fetched too. Output: docs/data/sources.json, which the Verifier's
cross-check reads and the page shows under each item as 'Direct source'.
"""
import json, re, sys, html, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
B = ROOT / "docs/data/briefing.json"
OUT = ROOT / "docs/data/sources.json"
PRIMARY_HOSTS = ("cisa.gov", "cert.siemens.com", "siemens.com/cert", "federalregister.gov", "congress.gov", "ferc.gov", "nerc.com", "tsa.gov", "energy.gov",
                 "ncsc.gov.uk", "nist.gov", "zyxel.com", "efs.sante.fr", "dondedesang.efs.sante.fr", "gov.uk", "europa.eu", "nvd.nist.gov", "vulncheck.com", "whitehouse.gov")
UA = {"User-Agent": "Mozilla/5.0 (energy-cyber-society source puller)"}

def fetch(url, limit=400_000):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read(limit); ctype = r.headers.get("Content-Type", "")
        m = re.search(r"charset=([\w\-]+)", ctype, re.I); enc = m.group(1) if m else None
        if not enc:
            m2 = re.search(rb'charset=["\']?([\w\-]+)', raw[:4000], re.I); enc = m2.group(1).decode() if m2 else "utf-8"
        try: txt = raw.decode(enc, "strict")
        except (UnicodeDecodeError, LookupError):
            try: txt = raw.decode("utf-8", "strict")
            except UnicodeDecodeError: txt = raw.decode("latin-1")
        return txt.replace("\ufffd", ""), r.status

def text_of(page):
    page = re.sub(r"<(script|style|nav|footer|header|aside)[^>]*>.*?</\1>", " ", page, flags=re.S | re.I)
    links = re.findall(r'href="(https?://[^"]+)"', page)
    t = re.sub(r"<[^>]+>", " ", page); t = html.unescape(re.sub(r"\s+", " ", t))
    return t.strip(), links

def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if 40 < len(s) < 400]

def keyterms(*parts):
    words = re.findall(r"[a-z0-9][a-z0-9\-]{3,}", " ".join(parts).lower())
    stop = {"that","with","from","this","have","were","been","their","which","into","after","about","than","what","when","will","over","more","also","they"}
    return {w for w in words if w not in stop}

def anchors(*parts):
    """Language-independent tokens: CVE ids, numbers with units, capitalised proper nouns, vendor
    names. These survive translation, so a French or Japanese primary can still be matched
    (REVIEW.md finding 5)."""
    t = " ".join(parts)
    a = set(re.findall(r"CVE-\d{4}-\d+", t, re.I)) | set(re.findall(r"\b\d{2,}(?:[.,]\d+)?\s?(?:%|°C|MW|GW|million|billion|M|B)?\b", t))
    a |= {w for w in re.findall(r"\b[A-Z][A-Za-z]{2,}\b", t) if w.lower() not in {"the","this","that","attackers","critical","multiple","cyberattack"}}
    return {x.lower() for x in a if len(x) > 2}

def relevant(sents, terms, n=5, anch=None):
    anch = anch or set()
    def score(s):
        sl = s.lower(); return len(terms & keyterms(s)) + 2 * sum(1 for x in anch if x in sl)
    scored = sorted(((score(s), s) for s in sents), key=lambda x: -x[0])
    out = [s for sc, s in scored[:n] if sc >= 2]
    return out if out else [s for s in sents[:3]]  # never return nothing: the first sentences are better than silence

def main():
    b = json.loads(B.read_text())
    out = {"pulled_at": datetime.now(timezone.utc).isoformat(), "items": {}}
    for it in b.get("items", []):
        terms = keyterms(it["headline"], it.get("so_what", ""), " ".join(it.get("cves", [])))
        anch = anchors(it["headline"], it.get("ics_vendor") or "", it.get("victim") or "", " ".join(it.get("cves", [])))
        rec = {"sources": [], "primary": []}
        seen = set()
        for s in it.get("sources", []):
            url = s.get("url")
            if not url or url in seen: continue
            seen.add(url)
            try:
                page, status = fetch(url); txt, links = text_of(page)
                ex = relevant(sentences(txt), terms, anch=anch)
                rec["sources"].append({"name": s["name"], "url": url, "status": status, "chars": len(txt), "excerpts": ex})
                print(f"  ok  {status} {len(txt):>7} {len(ex)} excerpts  {url[:80]}", file=sys.stderr)
                for l in links:
                    host = urllib.parse.urlparse(l).netloc.lower()
                    if any(h in host or h in l.lower() for h in PRIMARY_HOSTS) and l not in seen and not l.endswith((".png", ".jpg", ".svg", ".pdf")) and not re.search(r"facebook|twitter|linkedin|/styles/|share", l):
                        seen.add(l)
                        try:
                            p2, st2 = fetch(l); t2, _ = text_of(p2); ex2 = relevant(sentences(t2), terms, anch=anch)
                            if ex2 or st2 == 200:
                                rec["primary"].append({"url": l, "status": st2, "chars": len(t2), "excerpts": ex2, "found_in": s["name"]})
                                print(f"    primary {st2} {len(ex2)} excerpts {l[:80]}", file=sys.stderr)
                        except Exception as e:
                            rec["primary"].append({"url": l, "status": "error", "error": str(e)[:120], "found_in": s["name"]})
                        if len(rec["primary"]) >= 4: break
            except Exception as e:
                rec["sources"].append({"name": s["name"], "url": url, "status": "error", "error": str(e)[:160], "excerpts": []})
                print(f"  ERR {url[:80]} {e}", file=sys.stderr)
        out["items"][it["headline"]] = rec
        print(f"[{len(rec['sources'])} sources, {len(rec['primary'])} primary] {it['headline'][:70]}", file=sys.stderr)
    # what the Librarian learns: which sources delivered, which were blocked, which supplied items
    news = json.loads((ROOT / "docs/data/news.json").read_text())
    perf = {src["name"]: {"energy_items": 0, "wide_items": 0, "feed": "ok", "pulls_ok": 0, "pulls_blocked": 0} for src in news["sources"]}
    for e in news.get("errors", []):
        nm = next((x["name"] for x in news["sources"] if x["id"] == e["source"]), e["source"]); perf.setdefault(nm, {})["feed"] = "error: " + e["error"][:60]
    for st in news["energy"]: perf.setdefault(st["source_name"], {}).setdefault("energy_items", 0); perf[st["source_name"]]["energy_items"] += 1
    for st in news["wide"]: perf.setdefault(st["source_name"], {}).setdefault("wide_items", 0); perf[st["source_name"]]["wide_items"] += 1
    for rec in out["items"].values():
        for x in rec["sources"]:
            nm = x["name"].split(" (")[0]; perf.setdefault(nm, {"energy_items": 0, "wide_items": 0, "feed": "n/a", "pulls_ok": 0, "pulls_blocked": 0})
            perf[nm]["pulls_ok" if x.get("status") == 200 else "pulls_blocked"] = perf[nm].get("pulls_ok" if x.get("status") == 200 else "pulls_blocked", 0) + 1
    out["source_performance"] = perf
    out["primary_hosts_reached"] = sorted({urllib.parse.urlparse(p["url"]).netloc for rec in out["items"].values() for p in rec["primary"] if p.get("status") == 200})
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
