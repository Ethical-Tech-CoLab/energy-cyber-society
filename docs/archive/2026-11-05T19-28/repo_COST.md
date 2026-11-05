# What one run costs

Measured from the real bundle on 2026-11-04 (16 energy-cyber + 140 wider stories, 7-day window).

| Stage | Tokens in | Tokens out | Time | Notes |
|---|---|---|---|---|
| fetch_news.py | 0 | 0 | ~10 s | plain HTTP, 14 feeds |
| pull_sources.py | 0 | 0 | ~20-30 s | fetches every source URL + primary links |
| run_agents.py (44 Claude calls) | ~234,000 (≈4,600 of bundle per call) | ~10,500 | 3-6 min | bundle sent as a cached system block |
| validate.py | 0 | 0 | <1 s | |

Per run at Anthropic first-party rates, with prompt caching (cache reads ≈10% of input price):

| Model | per run | 2 runs/day | per month |
|---|---|---|---|
| Haiku 5.5 ($0.10 / $0.50 per MTok) | ~$0.01 | ~$0.02 | <$1 |
| Sonnet 5.5 ($2 / $10) | ~$0.22 | ~$0.44 | ~$13 |
| Opus 5.5 ($4 / $20) | ~$0.40 | ~$0.79 | ~$24 |

Uncached, multiply by ~2.5. GitHub Actions minutes: ~5 per run, within the free tier for a
public repo. The claude.ai scheduled-routine path (agent session instead of API calls) is
billed through the subscription; expect several hundred thousand tokens per session.
The real counts are written to `usage` in `docs/data/briefing.json` on every API run.
