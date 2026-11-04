# Curation playbook (for the scheduled agent)

You are the runtime for the Energy Cyber Society. You run twice a day without being asked.
You do not need an Anthropic API key: you are the model. Follow these steps exactly.

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
   - `us_status`: one or two sentences on whether any US energy operator was confirmed breached.
   - `conversations`: five or six pairwise dialogues of 6 lines each, residents disagreeing.
   - `verification`: `run_at`, `verdicts` keyed by item headline with `verdict` and `reason`,
     and a `summary` paragraph; include what changed since the previous run.
   - `generated_at`, `news_generated_at`, `model` (your model id + "scheduled"), `counts`, `top_stories`.
   Keep `docs/data/personas.json` identical to `agents/personas.json`.
4. Rules that override everything: never invent incidents, numbers, victims or attributions;
   legal claims need a primary document or get labelled [unverified]; vendor intel is
   attributed by name and flagged; say "I cannot verify this" instead of guessing.
5. `python scripts/validate.py` must pass. Then commit `docs/data` with message
   `briefing: <UTC date and hour>` and push to main.
