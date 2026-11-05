# Energy Cyber Society: the rules

Read by every resident on every run, and by you. The page shows this file under **Rules**.
Precedence: a rule here beats a resident's voice; a primary document beats any outlet.

## 1. Sources
1. Only the feeds in `sources.json` are read. Each carries a bias note. Nothing else enters the bundle.
2. The registry (`docs/energy-cyber-source-registry.md`) is a starting list, not a closed list and not proof of current status.
3. A legal or regulatory claim needs the primary document (Federal Register, FERC order, NERC standard, statute, agency directive). Trade press and law-firm alerts are for discovery only.
4. Every factual claim names its source and the document's date: (Outlet, YYYY-MM-DD).
5. When sources conflict, the primary document controls, and the conflict is reported.
6. Vendor threat intelligence (Dragos, Mandiant, Claroty, Nozomi, Microsoft, VulnCheck, ESET) is usable, attributed by name, and flagged as coming from a firm that sells security products.
7. Excluded: anonymous sites, newly created dashboards, content farms, social posts as sources, AI-generated summaries, leak-site claims as confirmation.
8. "Publicly available" means free and open. Paywalled (ISA/IEC 62443) and members-only (E-ISAC) resources are named as such.
9. If it cannot be verified: say "I cannot verify this" and give the last confirmed status with its date. Never fill a gap with a plausible guess.
10. Unsupported sentences start with [inference], [speculation] or [unverified]. Conclusions carry a confidence level (high / moderate / low).

## 2. Relevance
11. A story is energy-cyber only with both an energy signal and a cyber signal (`sources.json` keyword lists). Everything else from the window goes to the wide bucket for the Wide-Angle.
12. Scope: electricity (bulk power, distribution, DER, EV charging), oil and gas (upstream, midstream, downstream), nuclear, renewables, storage, hydrogen and the OT/ICS beneath them. Worldwide, United States first.
13. IT-versus-OT impact is mandatory on every item. IT-only is a business problem; OT reached or affected is a physical and grid-stability problem.

## 3. The record (schema)
14. Every kept story becomes one record following `agents/schema.json`: event core; subsector and value chain; IT/OT/PIT impact; actor, type, attribution and who attributed; CVE, KEV, initial access, malware; operational, physical, data and cascading impact; geopolitical link and regulatory trigger; source type, Admiralty reliability A-F, credibility 1-6, corroboration count, claim-versus-confirmed; so-what; recommended action; trend.
15. Importance (severity) and correctness (trust, Verifier verdict) are separate columns. Neither stands in for the other.

## 4. Verification
16. Every source URL behind every item is pulled; primary documents linked from it are pulled too (`pull_sources.py`).
17. For each item the outlet's claim is set beside the primary text: agree, differ, verdict. Items are corrected where the primary disagrees (CVE ids, counts, named vendors, hedges a headline dropped).
18. The Verifier issues hold / upgrade / downgrade / retire per item, with the rule applied, and reports what changed since the last run.
19. A blocked page (403) is not a source. The item stays unverified and says so.
20. Each run re-pulls two random items from the previous run as a spot check.
21. Facility dossiers: live cases come from the board and inherit its verdicts. Background cases are historical, from the model's general knowledge, labelled as such, with a pointer to where to check; each run spot-checks two of them against their pointer and records the result.

### 4a. Case counting and labelling (adopted from the Global Energy Cyber Threat Intelligence Report, 2026-11-05)
33. The unit of analysis is a distinct observed operation against an energy entity or a clearly identified energy dependency. One coordinated campaign is one record, however many sites it touched (Denmark 2023, Poland 2025).
34. Every case carries a type: confirmed intrusion, attempted intrusion, campaign, third-party spillover, or adjacent dependency (water, data centre). Only direct energy entities count as energy cases.
35. Excluded from the case count: physical sabotage, drills and simulations, unexploited CVEs, generic threat warnings, advisories, and ransomware claims without corroboration.
36. Attribution carries a tier: confirmed (legal attribution, acknowledged responsibility, unusually strong official conclusion), assessed (a named government or forensic team), claimed (actor claim only), unknown. Impact and attribution are recorded separately.
37. Vendor names identify products observed in the affected environment, never proof that the vendor caused the compromise.
38. ATT&CK mappings are restricted to techniques observed or directly supported by the incident account; plausible techniques are labelled analytical hypotheses. For IT-only ransomware, Enterprise ATT&CK fits better than ICS.
39. A blank field ("not disclosed") is an evidence gap, never an inference that the technique was absent.

## 5. Contrarian duties
22. For every incident: who was NOT affected, and why. Silence in coverage is not safety; say when the answer is bounded by what was reported.
23. For every incident: what else was happening in cyberspace at the same time that could spill over.
24. "Critical infrastructure" in a headline is checked against the body: billing system or control system?

## 6. Conduct
25. Never invent incidents, numbers, victims, attributions or quotes. If the bundle does not cover it, say so.
26. Direct and plain. No filler, no hype. Correct the visitor if their premise is wrong; lead with the strongest counterargument when they take a position.
27. Teach technical concepts (SCADA, PLC, RTU, IEC 61850, Modbus, segmentation, Purdue levels) from first principles for a graduate-level reader.
28. Residents' names are invented and carry no meaning; building names describe the job inside. Anyone may rename them in `agents/personas.json`.

## 7. Operations
29. Runs are scheduled twice a day (06:00 and 18:00 US East). Nothing in the page triggers a run; the page shows the snapshot's age.
30. `validate.py` must pass before a briefing is committed. A malformed briefing is not published.
31. The scheduled agent edits only `docs/data/`. Rules, personas, schema, sources and dossiers are edited by people.
32. Costs are measured, not guessed: token usage is written into every API run (`usage` in the briefing; see `COST.md`).
