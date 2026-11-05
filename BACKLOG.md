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
- Append-only archive of every run (docs/archive/, ARCHIVE.md, History tab, Gazette ?run=); clickable sources in every view and a Sources & references index; research feeds (arXiv cs.CR, eess.SY), magazine (WIRED), think tank (CSIS), independent (Schneier), vendor research (Kaspersky ICS CERT) added to the allowlist
- STIX 2.1 export; per-run history for trend charts; measured cost model (`COST.md`)
- INTELLIGENCE_ANALYSIS.md (ten-step procedure to IC standards), RULES.md (32 rules), REGISTER.md, source registry, Project instructions file, CURATION.md playbook, validator
- Twice-daily schedule: GitHub Actions workflow on disk; cloud-routine body in `scripts/routine.json`
- Repo pushed to github.com/carolina-moron/energy-cyber-society (private)

## Blocked: needs Carolina
- Make the repo public and enable Pages from `main:/docs` (the assistant's permissions refuse public surfaces)
- `gh auth refresh -h github.com -s workflow`, then un-ignore and push `.github/workflows/daily.yml`
- Add the `ANTHROPIC_API_KEY` repository secret (for the Actions path)
- Create the claude.ai scheduled routine from `scripts/routine.json` (fails with repo_access_denied until the repo is reachable)
- Sign the executive brief (`executive_brief.evaluation`) after reading the sources
- Decide the Ombudsman's three proposals: CISA feed path, citation rule for reasoning sentences, background-case verification before sharing

## Pending: next runs will do these automatically once scheduled
- Fresh briefing twice a day by the thirteen analytic residents (today's is hand-curated in session)
- Verify two background cases per run; fill `trend` from history; grow the dashboard trend lines
- Counsel reads the CISA 2015 sunset clause, any NDAA extension, the grid-component instrument, the TSA directive versions
- Economist fills loss figures only where filings exist; Technologist records model releases and prices from makers' pages

## Pending: product ideas raised but not yet built
- Random-interval verification (cloud cron minimum is 1 hour; spot-checks approximate it)
- Live monitoring (by design this is a snapshot; a push feed would need a server)
- Comments or annotations by the human evaluator inside the page (currently edits go in the JSON)
- Per-facility live case matching beyond keywords (needs the Archivist's links to be structured)
- Energy-per-token figures (no credible source exists; blank by rule)
- Replace or supplement Utility Dive and fix the CISA 403 for the puller
