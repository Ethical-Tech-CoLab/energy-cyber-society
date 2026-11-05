#!/usr/bin/env python3
"""Append an 'engineering' event (PR opened, or blocked) to the Incident Desk log."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; LOG = ROOT / "docs/data/engineering_log.json"  # separate from the pipeline log: the Engineer may edit this file only
log = json.loads(LOG.read_text()) if LOG.exists() else {"events": []}
url, summary = (sys.argv + ["", ""])[1:3]
now = datetime.now(timezone.utc).isoformat()
log["events"].append({"at": now, "run": "engineer", "type": "engineering" if url.startswith("http") else "engineering-blocked", "agent": "engineer", "item": url or summary[:80], "detail": summary, "severity": "info", "status": "open"})
log["updated_at"] = now; LOG.write_text(json.dumps(log, indent=1, ensure_ascii=False)); print("logged")
