# Decisions and answers: the questions asked while building, and where each answer lives

A log of the build conversation of 2026-11-04 to 2026-11-05. Each entry: the question or
instruction as asked, the answer or decision, and the place in the product that carries it.
Nothing here is lost in chat.

| # | Question or instruction | Answer or decision | Where it lives |
|---|---|---|---|
| 1 | Create a virtual society of LLM agents with specific skills, energy and cyber news, video-game style, click to talk | Pixel town, residents as analytic roles, click-to-talk panel | the page; `agents/personas.json` |
| 2 | They should tell me about cyber news, cybercrime, hackers, intelligence breaches in energy, daily, worldwide, US focus | Allowlist fetch, energy+cyber filter, US-first ordering, twice-daily schedule | `sources.json`, `scripts/fetch_news.py`, `CURATION.md` |
| 3 | Use only credible sources; summarize and analyze; bias of each source; what else is happening; who was NOT affected | Allowlist with bias notes; Reporter, Critic, Wide-Angle, Contrarian roles; rules 1–10, 22–24 | `RULES.md`, Media Critic, Contrarian |
| 4 | Create a Pages demo | Private Artifact now; GitHub Pages blocked until the repo is public | `BACKLOG.md` (blocked) |
| 5 | Search and curate for me | Pipeline curates; today's edition was hand-curated and labelled | `model` field in `briefing.json`; `REVIEW.md` finding 1 |
| 6 | Run it on demand without me asking; another agent keeps checking credibility; twice a day | Verifier role; GitHub Action and cloud-routine body, 06:00 and 18:00 Eastern | `.github/workflows/daily.yml`, `scripts/routine.json` |
| 7 | Keep them talking to each other | Continuous chatter, transcript, live generation when a key is set | Chatter toggle, "Overheard in town" |
| 8 | Methodology tab; where to look; how they fine-tune where to ask; limitations tab | Methodology, Where to look (Librarian, source performance), Limitations | those tabs; `agents/where_to_look.json` |
| 9 | Is it live? Does it need a button? Verify at random intervals? | Snapshot, not live; no button; schedule is fixed, random spot-checks approximate randomness | Limitations tab; `CURATION.md` 5b |
| 10 | Biggest gap: if it didn't affect something... ; don't make up | Absence of evidence stated; rule 25 | Limitations; `RULES.md` |
| 11 | Deploy on a new repo in my GitHub | Done privately; public visibility and Pages need you | `BACKLOG.md` |
| 12 | Facilitated bullet points; critical thought; responsible AI; is there a verifier; can it invent; live monitoring; tokens, input, output, cost per run | Summary tab; Verifier + cross-check; never fetches, only reads the bundle; not live; ~234k in / 10.5k out, ~$0.22 Sonnet cached | Summary, Methodology "Cost, inputs and outputs", `COST.md` |
| 13 | Click each residence; the specific names, why chosen | Clickable buildings; names invented for variety, no meaning, rename freely | building panel; `name_note` in personas |
| 14 | Click and see summarized bullet points | Summary tab | Summary |
| 15 | Click facilities: sectors, variables, IT/OT/PIT, vulnerabilities, real cases, attack types, how a breach happens | Twelve facility dossiers | map facilities; `agents/sectors.json` |
| 16 | What is the methodology; who is verifying; what are the limitations; guideline of rules | Dossier methodology note; Verifier for live cases, nobody yet for background cases; Rules tab | dossiers, Rules, `RULES.md`, `INTELLIGENCE_ANALYSIS.md` |
| 17 | A journal: old-school visualization | The Gazette, via the newsstand | `docs/gazette.html` |
| 18 | Flag anything not real to a cyber command; verify news, sources; history of unusual acts | Cyber Command: append-only log, verify panel, history | Cyber Command; `scripts/command_log.py` |
| 19 | Register of how each agent thinks, looks, verifies | Agent Register tab; `REGISTER.md` | Agent Register |
| 20 | A cyber analytics dashboard | Dashboard with tiles, charts, drill-down, timelines | Dashboard |
| 21 | Add the threat-intel platform variables (vulnerabilities, attacks, actors, malware, indicators, geopolitical risks, boards, STIX) | Collections tab; indicators and ATT&CK fields; STIX 2.1 export | Collections; `scripts/export_stix.py` |
| 22 | Who are we missing? | Counsel, Archivist, Ombudsman, Operator, Economist recommended; not a red team | this file; `REVIEW.md` "what is missing" |
| 23 | Click dashboard items; why scored; criteria; severity; cases | Drill-down and full analysis with scoring rationales and scales | Dashboard, full analysis |
| 24 | Add the five agents and a geopolitical analyst per layer | Six residents added; per-layer theatres | second row of buildings; `geopolitics` in briefing |
| 25 | Tab for what needs human touch | Human touch tab | Human touch |
| 26 | Ambiance correlated across domains, action, impact, scenarios | Correlations and Scenarios tab | Scenarios |
| 27 | Senior analyst evaluates an assembled picture; ten biggest threats for executives | Executive brief with unsigned evaluation block | Final output: Executive brief |
| 28 | Agent for market trends, AI models, energy use, prices, makers, valuations, all inputs | The Technologist; nine-layer inputs checklist | Compute Exchange; `agents/ai_market.json` |
| 29 | Backlog file; forget nothing | `BACKLOG.md` | `BACKLOG.md` |
| 30 | Step-by-step intelligence analysis to FBI standards | `INTELLIGENCE_ANALYSIS.md` (synthesis of public IC standards, not an official document) | linked from Rules |
| 31 | Reduce data to what matters; newspaper by continent; data centres, hardware, connectivity, machinery; how energy is transported | Scope widened; continent tag; world desk; three transport/compute facilities | Summary world desk, Gazette, facilities |
| 32 | A sources/references tab in everything; click sources from the executive summary | source_urls on brief, summary, scenarios, theatres; citation resolver; Sources & references index | every view; Sources & references |
| 33 | Verify all parts have it; what journals, magazines, forums, research? | Audit done, remaining views fixed; journals mapped not read, arXiv read, forums excluded by rule 7 | `energy-cyber-source-registry.md` |
| 34 | All history registered so nothing is lost | Append-only archive, History tab, archived Gazette editions | `docs/archive/`, `ARCHIVE.md` |
| 35 | Layer for how each was breached: attribution and why, bypass, phishing/malware mechanics, full process, next layers | Breach anatomy on items and key background cases | full analysis; dossiers; `REVIEW.md` finding 7 on attribution risk |
| 36 | Latin America missing; sample size too small | Five regional feeds and Spanish/Portuguese keywords; sample size shown everywhere; small by design | Summary "Sample", world desk |
| 37 | Can't read the conversation; minimize suggested questions | Collapsible description and suggestions | resident panel |
| 38 | Where is the final result? | The Executive brief, labelled "Final output", with the convergence line | Executive brief |
| 39 | Timeline of dates covered; last 26 years? | Three timelines; feeds reach days, history is unverified cases plus the archive; backfill is a job | Dashboard timelines; Limitations; `BACKLOG.md` |
| 40 | Other languages, local news | 38 feeds in nine languages; Arabic, Korean, Chinese, Hindi not found | `sources.json` note; world desk |
| 41 | Tab with cost, energy, agents cost, each question | Cost & energy tab, interactive, with question ledger and energy assumption | Cost & energy; `docs/data/cost_model.json` |
| 42 | A bank to see that information | The Bank: per-run spend, projection, budget | Bank building and tab |
| 43 | Notifications for what I missed: behaviour, breaking news | Bell, inbox, toast; push outside the page in backlog | Notifications |
| 44 | Tech crime, WIRED, Stanford, Berkeley, MIT Tech Review | TechCrunch Security, Berkeley CLTC, MIT Technology Review added; Stanford feeds malformed, mapped by hand | `sources.json`, Where to look |
| 45 | How many tokens per Claude plan? Build total? | Plans are time-window multiples, not token counts; API is per token; build ≈ $50–60 one-off | this file; Cost tab notes |
| 46 | What processing: GPU, CPU, internet? | Static page, Python scripts, no GPU; ~3 MB per fetch, ~1 MB API traffic per run; inference on the provider's servers | this file; Methodology cost section |
| 47 | Peer review, be critical; presentation in under ten minutes | `REVIEW.md` (2 blockers, 7 majors, 6 minors, missing list); `PRESENTATION.md` | both files |
| 48 | Are all answers documented? | This file | `DECISIONS.md` |

| 49 | Add this research (Global Energy Cyber Threat Intelligence Report PDF) | Transcribed to structured data; 20 cases into dossiers and timeline as 'report-sourced'; its counting and attribution rules adopted as rules 33-39; Research tab; items linked to related cases; spreadsheet not attached, URLs pending | Research tab; `agents/research/`; `RULES.md` §4a |

| 50 | More complexity per industry: supply chain, products, machinery, electricity dependence, sensors, compute, storage, everything exploitable; and the cases that happened | Nine-layer dependency stack per facility with cases linked to the report, the history and this week's items; global supply-chain map | facility dossiers; Research tab; `agents/sectors.json` |

| 51 | Add an autonomous agent that fixes bugs, refactors, opens PRs, improves UX, and actually does it | The Engineer resident with ENGINEERING.md, a UX audit script, an Incident Desk log, a daily routine body; first PR opened by hand following the playbook | Workshop; `ENGINEERING.md`; `scripts/ux_audit.py`; open PRs |

| 52 | A CIO should be able to determine if their organization is at risk and prioritize security efforts across all parts of the energy sector | Risk check (CIO) tab: tick facilities, products and environment patterns; scored 45/35/20 from patterns, live items and historical cases; ranked actions with evidence; export | Risk check (CIO); `agents/risk_model.json` |

| 53 | Add regulations: newest regulations and proposals in the news, and how they impact the energy sector and cyber intelligence | Regulations tab with the register and the week's regulatory news, each with energy-impact and intel-impact lines labelled [inference] where inferred; applicable regimes in the Risk check | Regulations tab; `agents/regulations.json` |

| 54 | Connect the Grid Status power-plant map and weather that might affect facilities and providers; connect the US grid map | Grid Status blocks embedding (X-Frame-Options), so it is linked; built an in-page US map with live ISO load, NWS alerts, hub forecasts and weather-to-item overlap labelled as inference | US grid & weather tab; `scripts/grid_weather.py` |

## Standing decisions made by the assistant without being asked (so you can reverse them)

- Resident names and the town metaphor; the building names; PIT as the third layer (DoD term).
- The Admiralty A–F / 1–6 grading and the five severity factors with weights 3/2/1/1/1.
- The allowlist's bias notes and the keyword lists in nine languages, unreviewed by native speakers.
- Twice daily at 06:00 and 18:00 US Eastern; Sonnet 5.5 as the default model in the routine body.
- Prompt caching of the bundle; the wide bucket capped at 150 stories.
- The ICD 203 probability words as the only likelihood vocabulary; no numeric probabilities.
- "Cyber Command" as the name of the flag log (review recommends renaming).
