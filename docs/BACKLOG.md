# Backlog

Everything asked for in the build conversation of 2026-11-04, with status. Nothing here is
forgotten; "blocked" means a person must act. Update this file when something ships.

## Done (in the repo and the private demo)
- Pixel town with click-to-talk residents, continuous chatter, transcript, live chat via key or proxy
- Fourteen residents: Reporter, Analyst, Media Critic, Wide-Angle, Contrarian, Verifier, Librarian, Counsel, Archivist, Ombudsman, Operator, Economist, Geopolitical Analyst, Technologist; buildings for each, clickable, with purpose, data flow and naming notes
- Credible-source allowlist with bias notes (`sources.json`); energy+cyber relevance filter; wide bucket
- Per-item intelligence schema (event core, subsector, value chain, IT/OT/PIT, actor, CVE/KEV, indicators, ATT&CK for ICS TTPs, impact, geopolitics, regulatory trigger, Admiralty A-F and 1-6, scoring rationales)
- Direct-source puller and outlet-versus-primary cross-check; Verifier verdicts; random spot-checks in the playbook
- Cyber Command: append-only flag log, verify-anything panel, history of unusual acts; session flags from live chat
- Tabs: Executive brief, Summary, Methodology, Where to look, Limitations, Rules, Agent Register, Dashboard (clickable drill-down to full analysis), Collections (TI-platform cut), Scenarios (action, impact, scenarios, correlations), Human touch, Briefing board, Today's wire, Settings
- Twelve energy facilities with sector dossiers (incl. data centre, LNG terminal and tanker, interconnector and subsea cable); energy scope widened to transport, compute and connectivity; continent tag and world desk by continent in Summary and Gazette (variables, IT/OT/PIT, vulnerabilities, attacks, how a breach happens, live and background cases)
- The Gazette: broadsheet printed from the data, with the ten-threat box
- Per-layer geopolitical analysis (theatres, IT/OT/PIT, subsectors, absent theatres)
- AI-market inputs checklist (`agents/ai_market.json`) and the Technologist's note
- Notifications bell and 'While you were away' inbox (breaking, behaviour, verification, discussions, editions; state per browser)
- The Bank (building + tab): per-run spend from history, running total, projected month, browser-stored budget with warning
- Cost & energy tab (interactive: model, runs/day, caching, energy assumption; per stage, per resident, per question ledger); feeds in 9 languages (34 feeds)
- Breach anatomy layer on every item and on key background cases (attribution hypotheses with reasoning, bypass, mechanics, full process, layers to add)
- Append-only archive of every run (docs/archive/, ARCHIVE.md, History tab, Gazette ?run=); clickable sources in every view and a Sources & references index; research feeds (arXiv cs.CR, eess.SY), magazine (WIRED), think tank (CSIS), independent (Schneier), vendor research (Kaspersky ICS CERT) added to the allowlist
- STIX 2.1 export; per-run history for trend charts; measured cost model (`COST.md`)
- INTELLIGENCE_ANALYSIS.md (ten-step procedure to IC standards), RULES.md (32 rules), REGISTER.md, source registry, Project instructions file, CURATION.md playbook, validator
- Twice-daily schedule: GitHub Actions workflow on disk; cloud-routine body in `scripts/routine.json`
- Repo pushed to github.com/carolina-moron/energy-cyber-society (private)

## From the peer review (REVIEW.md): status 2026-11-05
- DONE: dry-run replay; independent Verifier input; ground-truth check + eval tiles; human sample script; relevance classifier script; language-independent excerpting; NVD/KEV enrichment; computed severity + overrides; attribution restriction + validator rule; regional feeds/stories/items counts; CSP + prompt fencing + proxy-first note; STIX stable created; keyboard list view; schema_version; cross-language dedupe; actor aliases; Gazette AI line; Incident Desk rename; LICENSE (MIT, reversible); scripts/test_all.sh
- OPEN: first real API run; CI workflow (needs gh workflow scope); split game.js; native-speaker review of keyword lists; outage datasets (OE-417, E-ISAC); push notifications; in-page human feedback

## Original review list, for reference
- BLOCKER 1: run the pipeline end to end once with a key; add a dry-run replay mode for every parser
- BLOCKER 2: make the Verifier an independent call that never sees the author's rationale; held-out ground-truth set
- MAJOR: human-graded weekly sample with published agreement rate; model classification pass for relevance; language-aware excerpting + NVD/KEV enrichment; computed severity score; restrict attribution hypotheses to named attributors; regional feed-vs-item counts; proxy-first live chat, prompt fencing, CSP
- MINOR: stable STIX `created` (null-url fixed 2026-11-05); split game.js, CI smoke test, accessibility, mobile; schema_version + JSON Schema; cross-language dedupe and actor aliases; Gazette masthead 'written by AI residents'; rename Cyber Command

- Dependency stack on all 12 facilities (nine layers: supply chain, machinery, electricity, sensors, compute, storage, comms, software, people), each with exploitable point, signs and the cases that happened; global supply-chain map in the Research tab
- Research report integrated (2026-11-05): 20 report-sourced cases in the dossiers and timeline, rules 33-39, Research tab, related cases on items. OPEN: resolve the report's cited URLs (Archivist); obtain the 95-record spreadsheet from Carolina and import it

- US grid & weather tab: Leaflet map with live ISO load (ERCOT, CAISO, MISO, NYISO, ISONE), energy-relevant NWS alerts by state, 15 energy hubs with 3-day Open-Meteo stress flags, overlap with board items labelled inference; Grid Status plant map linked (cannot be embedded). OPEN: PJM needs PJM_API_KEY; SPP skipped; EIA-860 plant layer
- Regulations tab (Counsel's register of 16 regimes with primary URLs and honest 'unverified' status; this week's regulatory news with energy and cyber-intelligence impact lines); regimes mapped into the Risk check by facility and region
- Risk check (CIO) tab: profile of facilities, products, environment patterns, size and region → exposure score from this week's board, dependency stacks and the research record; ranked priorities with evidence; Markdown export; profile stays in the browser
- The Engineer (resident, Workshop, ENGINEERING.md, scripts/ux_audit.py, scripts/engineer_log.py, scripts/routine_engineer.json): autonomous bug-fix/refactor/UX agent that opens PRs daily, never merges

## Blocked: needs Carolina
- Review and merge the Engineer's PRs; first: https://github.com/carolina-moron/energy-cyber-society/pull/1
- Make the repo public and enable Pages from `main:/docs` (the assistant's permissions refuse public surfaces)
- `gh auth refresh -h github.com -s workflow`, then un-ignore and push `.github/workflows/daily.yml`
- Add the `ANTHROPIC_API_KEY` repository secret (for the Actions path)
- DONE 2026-11-05: claude.ai routines created: curation twice daily (trig_012X5bG37PWjSiAvMKUj71j6, 11:00 and 23:00 UTC) and Engineer daily (trig_01LtA6QZvXTLp7ukpepZmiC7, 14:00 UTC). Manage at https://claude.ai/code/routines. First runs: 2026-11-05 11:00 UTC and 14:00 UTC.
- Sign the executive brief (`executive_brief.evaluation`) after reading the sources
- Decide the Ombudsman's three proposals: CISA feed path, citation rule for reasoning sentences, background-case verification before sharing

## Pending: next runs will do these automatically once scheduled
- Fresh briefing twice a day by the thirteen analytic residents (today's is hand-curated in session)
- Verify two background cases per run; fill `trend` from history; grow the dashboard trend lines
- Counsel reads the CISA 2015 sunset clause, any NDAA extension, the grid-component instrument, the TSA directive versions
- Economist fills loss figures only where filings exist; Technologist records model releases and prices from makers' pages

## Pending: product ideas raised but not yet built
- Push notifications outside the page (email, browser push, Slack): needs a server or a GitHub Action step that sends on critical items; the in-page inbox is the current form
- 26-year backfill: an Archivist job that walks sources with archives (CISA ICS advisories 2010+, SEC 8-Ks, SANS/E-ISAC reports, DOJ indictments, court records) and adds one verified case per run; today the historical timeline holds ~25 background cases
- Random-interval verification (cloud cron minimum is 1 hour; spot-checks approximate it)
- Live monitoring (by design this is a snapshot; a push feed would need a server)
- Comments or annotations by the human evaluator inside the page (currently edits go in the JSON)
- Per-facility live case matching beyond keywords (needs the Archivist's links to be structured)
- Energy-per-token figures (no credible source exists; blank by rule)
- Replace or supplement Utility Dive and fix the CISA 403 for the puller
