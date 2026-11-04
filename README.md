# Energy Cyber Society

A virtual town of five LLM agents who read the day's cybersecurity news about the
energy sector, worldwide with a focus on the United States, and argue about it.
Walk around, overhear them, click one to talk.

**Live demo:** https://ethical-tech-colab.github.io/energy-cyber-society/

## The residents

All five run in the same runtime over the same news bundle. Each has one job,
which is why they disagree.

| Resident | Role | Job |
|---|---|---|
| Dana Okafor | The Reporter | Gathers and summarizes the day's energy-cyber stories, US first. Separates confirmed from claimed. |
| Mateo Reyes | The Analyst | Actors, tradecraft, IT-versus-OT impact, attribution confidence. |
| Priya Venkataraman | The Media Critic | What is the bias or incentive of each source? Who owns it, what does it overplay? |
| Samir Haddad | The Wide-Angle | What else happened in cyberspace at the same time that could spill into energy? |
| Ingrid Solberg | The Contrarian | Who was *not* affected, and why? Where is the coverage overstating impact? |

## How it works

1. `scripts/fetch_news.py` reads only the feeds in `sources.json` (the credible-source
   allowlist, each with a bias note) and keeps stories that have both an energy and a
   cyber signal. Everything else from the same window goes in a "wide" bucket.
2. `scripts/run_agents.py` runs the five personas in `agents/personas.json` on the Claude
   API: a briefing each, canned answers to their suggested questions, a speech-bubble line,
   and five pairwise conversations. Output: `docs/data/briefing.json`.
   Without `ANTHROPIC_API_KEY` it writes an honest headlines-only fallback.
3. Unattended runs, twice a day (06:00 and 18:00 US East), either way:
   - `.github/workflows/daily.yml` runs both scripts on the Claude API (needs an
     `ANTHROPIC_API_KEY` secret), or
   - a claude.ai scheduled routine (`scripts/routine.json`) clones the repo and does the
     curation itself following `CURATION.md`; no API key needed, the agent is the model.
   The sixth resident, the Verifier, audits every item on each run: source tier,
   corroboration, claim-versus-confirmed, staleness, and what changed since last time.
4. `docs/` is the GitHub Pages site: a canvas pixel town, no framework, no build step.

### Live chat

By default residents answer their suggested questions from the day's briefing. To ask
anything, open **Settings** in the page and add either an Anthropic API key (sent straight
from the browser to Anthropic) or an OpenAI-compatible proxy URL such as
[pages-ai-proxy](https://github.com/Ethical-Tech-CoLab/pages-ai-proxy). Settings live in
your browser's localStorage only.

## Run locally

```bash
pip install feedparser anthropic
python scripts/fetch_news.py 48          # hours of news to read
ANTHROPIC_API_KEY=sk-ant-... python scripts/run_agents.py
cd docs && python -m http.server 8765    # open http://localhost:8765
```

## The intelligence schema and sourcing rules

Each story the agents keep becomes a structured record (`agents/schema.json`): event core,
energy subsector and value-chain segment, IT-versus-OT impact, actor and attribution
confidence, CVE/KEV, impact, geopolitical and regulatory context, Admiralty-style source
reliability and credibility, a so-what line and a recommended action. The **Briefing board**
in the page shows these ranked by severity. The residents' shared rules
(`agents/personas.json`) carry the sourcing discipline: primary documents for legal claims,
vendor intel attributed and flagged, `[inference]`/`[unverified]` labels, "I cannot verify
this" instead of guesses.

Two companion files for using the same rigor in a Claude Project:
`docs/claude-project-instructions.md` (paste as Project instructions) and
`docs/energy-cyber-source-registry.md` (tiered registry, upload to Project knowledge).

## Pull the direct source, then verify one against the other

`scripts/pull_sources.py` fetches every source URL behind every board item, keeps the
sentences that match the item, and follows links to primary documents (CISA, FERC, NERC,
TSA, vendor advisories, victim statements). The board shows the pulled excerpts under
"Direct source" and the Verifier's cross-check ("Agree / Differ / verdict") next to each
item. The board's rubric keeps **importance** (severity) and **correctness** (source tier,
corroboration, Verifier verdict) as separate columns, so a critical-but-single-source item
and a confirmed-but-minor one are never confused.

## Adding a source

Add it to `sources.json` with a `bias_note`. The Media Critic reads those notes; a source
without one is a source nobody is thinking critically about.

## Known limits

- CISA's feeds return 403 to some clients; the fetcher logs the error and moves on.
- NERC, Reuters, ENISA and Dragos have no working public RSS as of November 2026.
- The energy filter is keyword-based, so an occasional off-topic story slips in and the
  Contrarian is there to say so.
