#!/usr/bin/env python3
"""Fetch the day's stories from the allowlisted feeds in sources.json.

Writes docs/data/news.json with two buckets:
  energy  - stories that match the energy keyword list (the town's main subject)
  wide    - everything else from the last 48h (what else is happening in cyberspace)
Nothing outside sources.json is ever read.
"""
import json, re, sys, time, html
from datetime import datetime, timedelta, timezone
from pathlib import Path
import feedparser

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "data" / "news.json"
WINDOW_HOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 48

def kw_match(k: str, blob: str) -> bool:
    """Whole-word match so 'rail' does not hit 'derail' and 'ics' does not hit 'politics'.
    Keywords ending in a space are prefix matches on a word; accented stems match any suffix."""
    k = k.lower()
    if any(ord(ch) > 0x2E7F for ch in k) or any(ord(ch) in range(0x0400, 0x0500) for ch in k):
        return k.strip() in blob  # CJK and Cyrillic: no word boundaries, plain substring
    if k.endswith(" "): return re.search(r"\b" + re.escape(k.strip()) + r"\b", blob) is not None
    if any(ch in k for ch in "áéíóúãçñ") or k.endswith(("ic", "ric", "ól", "ión", "ão")): return re.search(r"\b" + re.escape(k), blob) is not None
    return re.search(r"\b" + re.escape(k) + r"(s|es)?\b", blob) is not None

def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

def entry_time(e):
    for k in ("published_parsed", "updated_parsed"):
        if e.get(k):
            return datetime.fromtimestamp(time.mktime(e[k]), tz=timezone.utc)
    return None

def main():
    cfg = json.loads((ROOT / "sources.json").read_text())
    kws = [k.lower() for k in cfg["energy_keywords"]]
    cyber = [k.lower() for k in cfg["cyber_keywords"]]
    cutoff = datetime.now(timezone.utc) - timedelta(hours=WINDOW_HOURS)
    energy, wide, errors = [], [], []
    for src in cfg["sources"]:
        try:
            feed = feedparser.parse(src["url"], request_headers={"User-Agent": "energy-cyber-society/1.0"})
            if feed.bozo and not feed.entries:
                raise RuntimeError(str(feed.bozo_exception)[:120])
        except Exception as ex:  # one dead feed must not kill the day
            errors.append({"source": src["id"], "error": str(ex)[:200]})
            continue
        for e in feed.entries[:40]:
            t = entry_time(e)
            if t and t < cutoff:
                continue
            title = clean(e.get("title", ""))
            summary = clean(e.get("summary", "") or e.get("description", ""))[:600]
            if not title:
                continue
            item = {
                "title": title, "summary": summary, "link": e.get("link", ""),
                "published": t.isoformat() if t else None,
                "source": src["id"], "source_name": src["name"],
                "source_type": src["type"], "source_country": src["country"],
            }
            blob = f"{title} {summary}".lower()
            hits = [k for k in kws if kw_match(k, blob)]
            cyber_hits = [k for k in cyber if kw_match(k, blob)]
            # the energy bucket needs BOTH an energy and a cyber signal;
            # a coal-plant business story or a generic Linux CVE is not energy-cyber
            if hits and cyber_hits:
                item["matched"] = hits[:6]
                energy.append(item)
            else:
                wide.append(item)
    energy.sort(key=lambda x: x["published"] or "", reverse=True)
    wide.sort(key=lambda x: x["published"] or "", reverse=True)
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_hours": WINDOW_HOURS,
        "sources": [{k: s[k] for k in ("id", "name", "type", "country", "bias_note", "url")} for s in cfg["sources"]],
        "errors": errors,
        "energy": energy[:40],
        "wide": wide[:150],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"energy={len(energy)} wide={len(wide)} errors={len(errors)} -> {OUT}")
    for er in errors:
        print("  feed error:", er["source"], er["error"][:80])

if __name__ == "__main__":
    main()
