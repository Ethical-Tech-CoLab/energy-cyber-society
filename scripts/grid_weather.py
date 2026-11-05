#!/usr/bin/env python3
"""Grid and weather context for the energy-cyber picture. Writes docs/data/grid_weather.json:
- US ISO load (gridstatus library; ERCOT, CAISO, MISO, NYISO, ISONE; PJM needs PJM_API_KEY, SPP skipped: slow)
- NWS active alerts filtered to events that stress energy assets, grouped by state
- 3-day Open-Meteo forecast for energy hubs (heat/cold/wind/rain extremes)
Free public sources, no keys. Weather is context for 'who is stressed today', never a cyber claim."""
import json, sys, signal, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / "docs/data/grid_weather.json"
UA = {"User-Agent": "energy-cyber-society/1.0 (research tool)"}
out = {"generated_at": datetime.now(timezone.utc).isoformat(), "isos": [], "alerts": {}, "hubs": [], "errors": [],
       "links": {"gridstatus_map": "https://www.gridstatus.io/power-plant-map", "gridstatus": "https://www.gridstatus.io/", "nws": "https://www.weather.gov/", "eia_outages": "https://www.eia.gov/electricity/gridmonitor/"},
       "note": "Grid Status's map cannot be embedded (X-Frame-Options); it opens in a new tab. Load and weather are context for which assets are stressed, not evidence of any cyber event. Correlation with the board is keyword-based and labelled."}
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r: return json.loads(r.read())
class TO(Exception): pass
def alarm(s, f): raise TO()
signal.signal(signal.SIGALRM, alarm)
# ISO load
try:
    import gridstatus, logging; logging.disable(logging.CRITICAL)
    for name, cls in [("ERCOT", gridstatus.Ercot), ("CAISO", gridstatus.CAISO), ("MISO", gridstatus.MISO), ("NYISO", gridstatus.NYISO), ("ISONE", gridstatus.ISONE)]:
        try:
            signal.alarm(40); df = cls().get_load("today"); signal.alarm(0); row = df.tail(1).iloc[0]
            out["isos"].append({"iso": name, "time": str(row.get("Time"))[:19], "load_mw": int(float(row.get("Load"))), "peak_today_mw": int(float(df["Load"].max()))})
        except Exception as e: signal.alarm(0); out["errors"].append(f"{name}: {type(e).__name__}")
    try:
        signal.alarm(40); fm = gridstatus.Ercot().get_fuel_mix("today"); signal.alarm(0); r = fm.tail(1).iloc[0].to_dict()
        out["ercot_fuel_mix_mw"] = {k: int(float(v)) for k, v in r.items() if k != "Time"}
    except Exception as e: signal.alarm(0); out["errors"].append(f"ERCOT fuel mix: {type(e).__name__}")
except ImportError: out["errors"].append("gridstatus not installed (pip install gridstatus)")
# NWS alerts relevant to energy assets
ENERGY_EVENTS = {"High Wind Warning", "Extreme Wind Warning", "Hurricane Warning", "Hurricane Watch", "Tropical Storm Warning", "Ice Storm Warning", "Winter Storm Warning", "Blizzard Warning", "Extreme Cold Warning", "Wind Chill Warning", "Excessive Heat Warning", "Extreme Heat Warning", "Heat Advisory", "Red Flag Warning", "Fire Weather Watch", "Flood Warning", "Flash Flood Warning", "Storm Surge Warning", "Tornado Warning", "Severe Thunderstorm Warning", "Freezing Rain Advisory", "Winter Weather Advisory", "Gale Warning", "Storm Warning"}
WHY = {"wind": "transmission lines, wind-farm curtailment, substation damage", "ice": "line loading, icing, telecom and cellular backhaul", "cold": "gas-well freeze-offs, demand peaks (Uri 2021 class)", "heat": "demand peaks, derating of plants and lines, data-centre cooling", "fire": "preventive de-energisation, line faults", "flood": "substations, pump stations, pipeline crossings", "storm": "outages that mask or coincide with cyber effects; recovery crews stretched", "marine": "LNG and tanker movements, offshore wind"}
def why(ev):
    e = ev.lower()
    for k, w in (("wind", "wind"), ("ice", "ice"), ("freez", "ice"), ("cold", "cold"), ("chill", "cold"), ("heat", "heat"), ("fire", "fire"), ("flag", "fire"), ("flood", "flood"), ("surge", "flood"), ("hurricane", "storm"), ("tropical", "storm"), ("tornado", "storm"), ("thunder", "storm"), ("blizzard", "ice"), ("winter", "ice"), ("gale", "marine"), ("storm", "marine")):
        if k in e: return WHY[w]
    return "general"
try:
    d = get("https://api.weather.gov/alerts/active")
    feats = [f["properties"] for f in d.get("features", []) if f["properties"].get("event") in ENERGY_EVENTS]
    by = {}
    for p in feats:
        for st in (p.get("geocode", {}).get("UGC") or []):
            by.setdefault(st[:2], {}).setdefault(p["event"], 0); by[st[:2]][p["event"]] += 1
    out["alerts"] = {"total_active": len(d.get("features", [])), "energy_relevant": len(feats), "by_state": by,
                     "events": sorted({p["event"] for p in feats}), "why": {ev: why(ev) for ev in sorted({p["event"] for p in feats})},
                     "top": [{"event": p["event"], "area": (p.get("areaDesc") or "")[:120], "severity": p.get("severity"), "ends": (p.get("ends") or "")[:16], "why": why(p["event"])} for p in sorted(feats, key=lambda p: ({"Extreme": 0, "Severe": 1, "Moderate": 2}.get(p.get("severity"), 3)))[:15]]}
except Exception as e: out["errors"].append(f"NWS: {type(e).__name__}")
# hubs
HUBS = [("Houston TX (Gulf Coast refining, LNG, ERCOT)", 29.76, -95.37, ["refinery", "lngport", "pipeline"]), ("Midland TX (Permian upstream)", 31.99, -102.08, ["wellhead"]), ("Chicago IL (PJM/MISO seam, pipelines)", 41.88, -87.63, ["pipeline", "substation"]), ("Phoenix AZ (data centres, solar, nuclear)", 33.45, -112.07, ["datacentre", "renewables", "nuclear"]), ("Northern Virginia (data-centre capital)", 38.95, -77.45, ["datacentre", "substation"]), ("Los Angeles CA (CAISO, ports)", 34.05, -118.24, ["lngport", "evcharging"]), ("New York NY (NYISO, interconnectors)", 40.71, -74.01, ["interconnector", "substation"]), ("Minneapolis MN (MISO north, cold)", 44.98, -93.27, ["thermal", "substation"]), ("Hamburg DE (offshore wind, interconnectors)", 53.55, 9.99, ["renewables", "interconnector"]), ("Rotterdam NL (refining, LNG)", 51.92, 4.48, ["refinery", "lngport"]), ("Warsaw PL (CHP, distributed energy)", 52.23, 21.01, ["thermal", "renewables"]), ("Kyiv UA (grid under attack)", 50.45, 30.52, ["substation", "thermal"]), ("Tokyo JP (nuclear restart, LNG)", 35.68, 139.69, ["nuclear", "lngport"]), ("São Paulo BR (hydro, distribution)", -23.55, -46.63, ["substation"]), ("Mexico City MX (CFE)", 19.43, -99.13, ["substation", "pipeline"])]
for name, lat, lon, fac in HUBS:
    try:
        f = get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,wind_speed_10m_max,precipitation_sum&forecast_days=3&timezone=UTC")["daily"]
        tmax, tmin, wind, rain = max(f["temperature_2m_max"]), min(f["temperature_2m_min"]), max(f["wind_speed_10m_max"]), sum(f["precipitation_sum"])
        flags = [x for x, c in (("heat", tmax >= 35), ("cold", tmin <= -10), ("wind", wind >= 60), ("rain", rain >= 50)) if c]
        out["hubs"].append({"hub": name, "lat": lat, "lon": lon, "facilities": fac, "tmax_c": tmax, "tmin_c": tmin, "wind_max_kmh": wind, "rain_3d_mm": round(rain, 1), "stress": flags})
    except Exception as e: out["errors"].append(f"open-meteo {name}: {type(e).__name__}")
# GDACS: global disaster alerts (floods, cyclones, earthquakes, wildfires, volcanoes), orange/red only
try:
    import re, urllib.request as ur
    xml = ur.urlopen(ur.Request("https://www.gdacs.org/xml/rss.xml", headers=UA), timeout=30).read().decode("utf-8", "replace")
    items = re.findall(r"<item>(.*?)</item>", xml, re.S); gd = []
    for it in items:
        g = lambda tag: (re.search(rf"<{tag}>(.*?)</{tag}>", it, re.S) or [None, ""])[1].strip()
        lvl = g("gdacs:alertlevel"); ev = g("gdacs:eventtype"); cty = g("gdacs:country"); title = re.sub(r"<.*?>", "", g("title"))
        lat = g("geo:lat") or g("geo:Point>\s*<geo:lat"); lon = g("geo:long")
        if lvl in ("Orange", "Red"):
            try: gd.append({"level": lvl, "type": {"FL": "flood", "TC": "tropical cyclone", "EQ": "earthquake", "WF": "wildfire", "VO": "volcano", "DR": "drought"}.get(ev, ev), "country": cty.replace("&amp;", "&"), "title": title[:120], "lat": float(lat), "lon": float(lon), "link": g("link"), "why": {"FL": "substations, pump stations, hydro spillways", "TC": "transmission, offshore wind, ports and LNG", "EQ": "pipelines, refineries, nuclear safety shutdowns", "WF": "transmission corridors, de-energisation", "VO": "ash on insulators and turbines, aviation fuel", "DR": "hydro and thermal cooling water"}.get(ev, "")})
            except ValueError: pass
    out["gdacs"] = {"orange_red": gd, "total_items": len(items), "source": "https://www.gdacs.org/"}
except Exception as e: out["errors"].append(f"GDACS: {type(e).__name__}")
OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(f"grid_weather: {len(out['isos'])} ISOs, {out['alerts'].get('energy_relevant', 0)} energy-relevant alerts, {len(out['hubs'])} hubs, errors={out['errors']}")
