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
        return r.read(limit).decode("utf-8", "replace"), r.status

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

def relevant(sents, terms, n=5):
    scored = sorted(((len(terms & keyterms(s)), s) for s in sents), key=lambda x: -x[0])
    return [s for sc, s in scored[:n] if sc >= 2]

def main():
    b = json.loads(B.read_text())
    out = {"pulled_at": datetime.now(timezone.utc).isoformat(), "items": {}}
    for it in b.get("items", []):
        terms = keyterms(it["headline"], it.get("so_what", ""), " ".join(it.get("cves", [])))
        rec = {"sources": [], "primary": []}
        seen = set()
        for s in it.get("sources", []):
            url = s.get("url")
            if not url or url in seen: continue
            seen.add(url)
            try:
                page, status = fetch(url); txt, links = text_of(page)
                ex = relevant(sentences(txt), terms)
                rec["sources"].append({"name": s["name"], "url": url, "status": status, "chars": len(txt), "excerpts": ex})
                print(f"  ok  {status} {len(txt):>7} {len(ex)} excerpts  {url[:80]}", file=sys.stderr)
                for l in links:
                    host = urllib.parse.urlparse(l).netloc.lower()
                    if any(h in host or h in l.lower() for h in PRIMARY_HOSTS) and l not in seen and not l.endswith((".png", ".jpg", ".svg", ".pdf")) and not re.search(r"facebook|twitter|linkedin|/styles/|share", l):
                        seen.add(l)
                        try:
                            p2, st2 = fetch(l); t2, _ = text_of(p2); ex2 = relevant(sentences(t2), terms)
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
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
