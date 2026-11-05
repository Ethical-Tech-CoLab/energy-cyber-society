# Energy-cyber source registry

Review date: 2026-11-04. Starting list, not a closed list and not proof of current status. Edit as you trust or reject sources.

## What is actually read (automatically, every run)
The feeds below, and nothing else. Journals, forums and paywalled outlets are not read; they are mapped under 'Where to look' for a person.

## Access limits
- ISA/IEC 62443: paywalled standard. NIST SP 800-82r3 is the free substitute for OT security guidance.
- E-ISAC portal: members only. Public output comes via NERC alerts and CISA advisories.
- CISA RSS feeds return HTTP 403 to automated clients; read the site directly or from GitHub Actions.
- Journals (International Journal of Critical Infrastructure Protection, IEEE Transactions on Smart Grid, Computers & Security): paywalled, no usable RSS; Journal of Cybersecurity (Oxford) is open access; arXiv preprints are read automatically.
- Forums, social posts, Telegram channels and leak sites: excluded as sources by rule 7; they may be the subject of a story, never its evidence.

## Tier 0 — primary documents (fetch for any legal or regulatory claim)
- Federal Register (federalregister.gov), FERC eLibrary and orders, NERC Reliability Standards (CIP-002 through CIP-015), TSA pipeline security directives, statutes on congress.gov, CISA ICS advisories (cisa.gov/news-events/cybersecurity-advisories), NIST SP 800-82r3, DOE CESER publications, vendor PSIRT advisories, victim statements, SEC filings.

## Tier 1 — primary / government
- **CISA Advisories** (government, US) — https://www.cisa.gov/cybersecurity-advisories/all.xml  
  Bias note: US government body; authoritative on US-facing threats, careful wording, rarely attributes publicly, slow on non-US incidents.
- **CISA News** (government, US) — https://www.cisa.gov/news.xml  
  Bias note: Agency press office; frames events around its own programs and successes.
- **DOE Newsroom** (government, US) — https://www.energy.gov/rss/newsroom.xml  
  Bias note: Department press releases; promotional about federal programs.
- **UK NCSC News** (government, UK) — https://www.ncsc.gov.uk/api/1/services/v1/all-rss-feed.xml  
  Bias note: UK government agency; aligned with Five Eyes attributions.

## Tier 2 — wire and established press
- **CyberScoop** (trade press, US) — https://cyberscoop.com/feed/  
  Bias note: Washington-focused trade outlet; strong on policy and federal sourcing, sponsor-funded events with vendors.
- **SecurityWeek** (trade press, US) — https://www.securityweek.com/feed/  
  Bias note: Vendor-advertising supported; dedicated ICS/OT coverage, sometimes echoes vendor research uncritically.
- **Dark Reading** (trade press, US) — https://www.darkreading.com/rss.xml  
  Bias note: Informa-owned, heavy vendor sponsorship; analysis-led, can amplify vendor threat reports.
- **Krebs on Security** (independent, US) — https://krebsonsecurity.com/feed/  
  Bias note: Single investigative reporter; deep on cybercrime ecosystems, selective coverage, US-centric.
- **Utility Dive** (industry press, US) — https://www.utilitydive.com/feeds/news/  
  Bias note: Utility-industry trade outlet; frames security through regulation, cost and reliability; sympathetic to utilities.
- **Industrial Cyber** (trade press, international) — https://industrialcyber.co/feed/  
  Bias note: ICS/OT-only trade outlet; vendor-advertising supported, relays vendor reports and regulator notices with little pushback.
- **Schneier on Security** (independent, US) — https://www.schneier.com/feed/atom/  
  Bias note: One academic's commentary and links; strong on policy and crypto, selective, opinionated.
- **CSIS** (think tank, US) — https://www.csis.org/rss.xml  
  Bias note: Washington think tank; policy analysis with funders across defence and industry; frames through US strategic interest.

## Tier 3 — fast tech press (discovery, confirm elsewhere)
- **BleepingComputer** (tech press, US) — https://www.bleepingcomputer.com/feed/  
  Bias note: Fast, incident-driven, often first with ransomware claims; headlines can run ahead of confirmation.
- **The Hacker News** (tech press, international) — https://feeds.feedburner.com/TheHackersNews  
  Bias note: High volume, sponsored content mixed with news; good for the wide-angle view of what else is happening.
- **The Register Security** (tech press, UK) — https://www.theregister.com/security/headlines.atom  
  Bias note: Irreverent UK tech press; sceptical of vendors and governments alike, headline tone can trivialise.
- **WIRED Security** (magazine, US) — https://www.wired.com/feed/category/security/latest/rss  
  Bias note: Narrative long-form; strong investigative pieces on Sandworm and grid attacks; prioritises story over timeliness; Condé Nast.

## Tier 3 — vendor-adjacent (attribute by name)
- **The Record (Recorded Future News)** (vendor-owned press, US) — https://therecord.media/feed  
  Bias note: Editorially independent but owned by threat-intel vendor Recorded Future; strong on nation-state and ransomware actors.
- **Kaspersky ICS CERT** (vendor research, Russia) — https://ics-cert.kaspersky.com/feed/  
  Bias note: Deep ICS vulnerability and threat research from a Russian vendor banned from US federal use (2017) and US sales (2024); technical content is strong, attribution of Russian activity is absent or soft.

## Tier 4 — research preprints (unreviewed; author claims)
- **arXiv cs.CR (preprints)** (research preprints, international) — http://export.arxiv.org/rss/cs.CR  
  Bias note: Unreviewed preprints; author claims, not findings; good for what researchers are probing (ICS intrusion detection, grid attacks) before journals publish.
- **arXiv eess.SY (systems and control preprints)** (research preprints, international) — http://export.arxiv.org/rss/eess.SY  
  Bias note: Control-systems research, including grid and cyber-physical security; unreviewed.

## Vendor threat intelligence (usable, attribute by name, flag as a seller of security products)
- Dragos, Mandiant (Google), Claroty, Nozomi, Microsoft Threat Intelligence, VulnCheck, ESET, Kaspersky ICS CERT. Only Kaspersky ICS CERT has a working feed; the rest are reached by following links from stories or by hand.

## Excluded
- Anonymous sites, newly created dashboard sites, content farms, social posts as sources, AI-generated summaries, ransomware leak sites as confirmation (claims only).

## Known dead or blocked feeds (review date)
- CISA feeds return 403 to some clients (Akamai); they may work from GitHub Actions. NERC, Reuters, ENISA and Dragos have no working public RSS as of 2026-11-04. Probed 2026-11-04 and NOT available as feeds: SANS blog (500), Lawfare (403), Claroty Team82 (404), Nozomi (404), Microsoft Security blog (no response), Ars Technica security (404), E&E News (403), S&P Global (403). Journals (IJCIP, IEEE TSG, Computers & Security, Journal of Cybersecurity) have no usable public RSS and are mapped in where_to_look.json for manual reading. Forums and social posts are excluded by rule 7.