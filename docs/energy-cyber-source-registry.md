# Energy-cyber source registry

Review date: 2026-11-04. Starting list, not a closed list and not proof of current status. Edit as you trust or reject sources.

## Access limits
- ISA/IEC 62443: paywalled standard. NIST SP 800-82r3 is the free substitute for OT security guidance.
- E-ISAC portal: members only. Public output comes via NERC alerts and CISA advisories.
- CISA RSS feeds return HTTP 403 to some automated clients; read the site directly or from GitHub Actions.

## Tier 0 — primary documents (fetch for any legal or regulatory claim)
- Federal Register (federalregister.gov), FERC eLibrary and orders, NERC Reliability Standards (CIP-002 through CIP-015), TSA pipeline security directives, statutes on congress.gov, CISA ICS advisories (cisa.gov/news-events/cybersecurity-advisories), NIST SP 800-82r3, DOE CESER publications.

## Tier 1 — primary / government
- **CISA Advisories** (US) — https://www.cisa.gov/cybersecurity-advisories/all.xml  
  Bias note: US government body; authoritative on US-facing threats, careful wording, rarely attributes publicly, slow on non-US incidents.
- **CISA News** (US) — https://www.cisa.gov/news.xml  
  Bias note: Agency press office; frames events around its own programs and successes.
- **DOE Newsroom** (US) — https://www.energy.gov/rss/newsroom.xml  
  Bias note: Department press releases; promotional about federal programs.
- **UK NCSC News** (UK) — https://www.ncsc.gov.uk/api/1/services/v1/all-rss-feed.xml  
  Bias note: UK government agency; aligned with Five Eyes attributions.

## Tier 2 — wire and established press
- **CyberScoop** (US) — https://cyberscoop.com/feed/  
  Bias note: Washington-focused trade outlet; strong on policy and federal sourcing, sponsor-funded events with vendors.
- **SecurityWeek** (US) — https://www.securityweek.com/feed/  
  Bias note: Vendor-advertising supported; dedicated ICS/OT coverage, sometimes echoes vendor research uncritically.
- **Dark Reading** (US) — https://www.darkreading.com/rss.xml  
  Bias note: Informa-owned, heavy vendor sponsorship; analysis-led, can amplify vendor threat reports.
- **Krebs on Security** (US) — https://krebsonsecurity.com/feed/  
  Bias note: Single investigative reporter; deep on cybercrime ecosystems, selective coverage, US-centric.
- **Utility Dive** (US) — https://www.utilitydive.com/feeds/news/  
  Bias note: Utility-industry trade outlet; frames security through regulation, cost and reliability; sympathetic to utilities.
- **Industrial Cyber** (international) — https://industrialcyber.co/feed/  
  Bias note: ICS/OT-only trade outlet; vendor-advertising supported, relays vendor reports and regulator notices with little pushback.

## Tier 3 — fast tech press (discovery, confirm elsewhere)
- **BleepingComputer** (US) — https://www.bleepingcomputer.com/feed/  
  Bias note: Fast, incident-driven, often first with ransomware claims; headlines can run ahead of confirmation.
- **The Hacker News** (international) — https://feeds.feedburner.com/TheHackersNews  
  Bias note: High volume, sponsored content mixed with news; good for the wide-angle view of what else is happening.
- **The Register Security** (UK) — https://www.theregister.com/security/headlines.atom  
  Bias note: Irreverent UK tech press; sceptical of vendors and governments alike, headline tone can trivialise.

## Tier 3 — vendor-adjacent (attribute by name)
- **The Record (Recorded Future News)** (US) — https://therecord.media/feed  
  Bias note: Editorially independent but owned by threat-intel vendor Recorded Future; strong on nation-state and ransomware actors.

## Vendor threat intelligence (usable, attribute by name, flag as a seller of security products)
- Dragos, Mandiant (Google), Claroty, Nozomi, Microsoft Threat Intelligence, VulnCheck, ESET. No working public RSS for Dragos as of the review date.

## Excluded
- Anonymous sites, newly created dashboard sites, content farms, social posts as sources, AI-generated summaries, ransomware leak sites as confirmation (claims only).

## Known dead or blocked feeds (review date)
- NERC news page is HTML, no RSS. Reuters agency cyber feed 404. ENISA rss 404. Dragos feed 404. CISA feeds 403 from this client.