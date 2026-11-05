#!/usr/bin/env python3
"""Compact worldwide power-plant layer from the WRI Global Power Plant Database (CC BY 4.0).
Keeps plants >= MIN_MW (default 300) plus all nuclear, as [lat, lon, mw, fuel, country, name].
Source CSV is passed as argv[1] (download from the WRI GitHub repository); output docs/data/plants.json."""
import csv, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
src = Path(sys.argv[1]); MIN_MW = float(sys.argv[2]) if len(sys.argv) > 2 else 300
rows = list(csv.DictReader(open(src, encoding="utf-8")))
FUEL = {"Coal": "C", "Gas": "G", "Oil": "O", "Nuclear": "N", "Hydro": "H", "Wind": "W", "Solar": "S", "Biomass": "B", "Geothermal": "T", "Storage": "E", "Waste": "B", "Petcoke": "O", "Cogeneration": "G", "Wave and Tidal": "H", "Other": "X"}
out = []
for r in rows:
    try: mw = float(r["capacity_mw"] or 0); lat = float(r["latitude"]); lon = float(r["longitude"])
    except ValueError: continue
    if mw >= MIN_MW or r["primary_fuel"] == "Nuclear":
        out.append([round(lat, 3), round(lon, 3), int(mw), FUEL.get(r["primary_fuel"], "X"), r["country"], r["name"][:40]])
data = {"source": "WRI Global Power Plant Database v1.3.0 (CC BY 4.0), https://datasets.wri.org/dataset/globalpowerplantdatabase", "filter": f"capacity >= {MIN_MW:g} MW plus all nuclear", "total_in_source": len(rows), "kept": len(out), "fuel_codes": {v: k for k, v in FUEL.items() if k not in ("Waste", "Petcoke", "Cogeneration", "Wave and Tidal")}, "plants": out}
(ROOT / "docs/data/plants.json").write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False))
print(f"plants.json: {len(out)} of {len(rows)} plants, {(ROOT / 'docs/data/plants.json').stat().st_size // 1024} KB")
