# Curation playbook (for the scheduled agent)

You are the runtime for the Energy Cyber Society. You run twice a day without being asked.
You do not need an Anthropic API key: you are the model. Follow these steps exactly, and
follow INTELLIGENCE_ANALYSIS.md for how to evaluate sources, write judgments and state confidence.

1. `pip install feedparser` then `python scripts/fetch_news.py 48`. Read `docs/data/news.json`.
   Only the feeds in `sources.json` are allowed. Do not search the open web for stories;
   you may fetch a primary document (statute, FERC/NERC/CISA/TSA page, vendor advisory) to
   confirm a claim that is already in the bundle.
2. Read `agents/personas.json` (six residents, shared rules, verification procedure) and
   `agents/schema.json` (per-item record and taxonomy). Read the previous
   `docs/data/briefing.json` so you can report what changed.
3. Write a new `docs/data/briefing.json` with:
   - `agents`: for each of the six residents, `briefing` (4-7 sentences, every claim with
     (Source Name, date)), `answers` (one per question in personas.json), `bubble` (≤12 words).
   - `items`: one schema record per energy-relevant story, max 12, only taxonomy values.
     IT-versus-OT impact is mandatory on every item.
   - `summary`: `headline`, 6-10 `bullets` ({text, sources, tag}, US first, each with outlet
     and date), and 5 `considerations` (critical-thought sentences).
   - each item carries `scoring`: severity level with the five factors and a rationale that
     says why this level and not the adjacent ones, plus reliability and credibility rationales.
     Keep `rubric` (severity_scale, severity_factors, reliability_scale, credibility_scale, rule).
   - `correlations` (links between items across domains with strength and evidence),
     `scenarios` (per main story: action_now, impact_chain, three scenarios with likelihood
     words and what confirms each), `geopolitics` (theatres with layers IT/OT/PIT, subsectors,
     US relevance, confidence; and absent_this_week), and keep `human_touch` as is.
   - `executive_brief`: ten ranked threats for energy executives (threat, why, exposure, action,
     confidence, source, sev), `not_on_the_list`, and `evaluation` with signed=false; never set
     signed=true yourself. Carry forward evaluator_notes from the previous run.
   - every item carries `continent`; write `world_desk` with one line per continent, saying
     'No energy-cyber reporting in the allowlisted feeds this window' where that is true.
     Energy scope includes data centres, connectivity hardware, industrial machinery and energy
     transport (pipelines, LNG and tanker shipping, rail and road fuel, interconnectors, subsea cables).
   - `source_urls` ([{name,url,date}]) on every executive_brief threat, summary bullet, scenario
     and geopolitics theatre; and `references` (every URL read or cited this run, categorised).
     A claim without a clickable source is a validator failure.
   - `us_status`: one or two sentences on whether any US energy operator was confirmed breached.
   - `conversations`: five or six pairwise dialogues of 6 lines each, residents disagreeing.
   - `verification`: `run_at`, `verdicts` keyed by item headline with `verdict` and `reason`,
     and a `summary` paragraph; include what changed since the previous run.
   - `generated_at`, `news_generated_at`, `model` (your model id + "scheduled"), `counts`, `top_stories`.
   Keep `docs/data/personas.json` identical to `agents/personas.json`.
4. Rules that override everything: never invent incidents, numbers, victims or attributions;
   legal claims need a primary document or get labelled [unverified]; vendor intel is
   attributed by name and flagged; say "I cannot verify this" instead of guessing.
5. `python scripts/pull_sources.py` pulls the direct source behind every item plus any
   primary document (government, regulator, vendor advisory, victim statement) linked from
   it, into `docs/data/sources.json`. Read the excerpts. Then do the second verification:
   for each item, copy what the outlet says next to what the primary says and record
   `verification.crosschecks[<headline>] = {compared, agree, differ, verdict}`. Correct the
   item where the primary disagrees with the outlet (CVE ids, counts, named vendors,
   hedged language such as "highly likely" that a headline dropped). If a page is blocked
   (HTTP 403) say "I cannot verify this" in the cross-check.
5b. Random spot-check: pick two items from the previous briefing at random, re-pull their
   sources, and note in `verification.summary` whether the pages changed.
5c. The Librarian: from `docs/data/sources.json` (`source_performance`,
   `primary_hosts_reached`) write her briefing on which sources delivered, which were
   blocked, and where to ask next run. Copy `agents/where_to_look.json` to
   `docs/data/where_to_look.json`; add any primary host you reached that is missing.
6. Keep `rubric` in the briefing: importance (severity) and correctness (trust +
   Verifier) are separate columns; never let one stand in for the other.
7. Fill `indicators` (IOCs with source) and `ttps` (MITRE ATT&CK for ICS ids) on each item
   where the bundle supports them; never invent an IOC. Then `python scripts/export_stix.py`.
7b. `python scripts/validate.py` must pass. Then `python scripts/command_log.py` appends this
   run's flags to docs/data/command_log.json (append-only; never edit or delete events).
   Then `python scripts/archive.py` to file the run in docs/archive/ (append-only).
   Spot-check two background cases from agents/sectors.json against their 'check' pointer
   with WebFetch and log the result as a `background-check` event (ok / differs / unreachable). Then commit `docs/data` with message
   `briefing: <UTC date and hour>` and push to main.
