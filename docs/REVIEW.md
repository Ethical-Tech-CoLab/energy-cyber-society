# Peer review of the Energy Cyber Society

> **Status 2026-11-05 (same day):** addressed in commit series 'review fixes'. Per finding:
> 1 dry-run replay mode built and passing (91 call sites); the real API run still needs a key.
> 2 Verifier now receives stripped records + pulled text only; ground-truth check added (10 facts, 100% today, trivially, because the facts were set from the same data; it becomes meaningful when facts are added by a person). 3 human-grading sample drawn each run; agreement tiles on the dashboard. 4 second-stage classifier script (runs with a key). 5 language-independent anchors in excerpting; NVD/KEV enrichment live (found one KEV-listed CVE the board had under-rated). 6 computed severity with arithmetic and mandatory override reasons. 7 attribution restricted to quoted attributors; validator enforces. 8 feeds/stories/items per continent beside every regional line; timeline marked illustrative. 9 CSP meta, prompt fencing, proxy-first settings text. 10 STIX stable `created`, nulls removed. 11 keyboard list view added; split and CI still pending. 12 schema_version + fuller validator. 13 cross-language dedupe in fetch; actor alias table. 14 Gazette masthead line. 15 renamed Incident Desk.
> Still open: a real API run; CI (needs workflow scope); game.js split; native-speaker review; outage datasets; push notifications; human feedback inside the page.

Reviewer: the assistant that built it, asked to be critical. Date: 2026-11-05. Severity:
**blocker** (the product's claim does not hold), **major** (a user could be misled or the system
could fail silently), **minor** (quality). Each finding has a fix.

## 1. The pipeline has never run

**Blocker.** Every briefing published so far was written by the authoring assistant in a live
session, then labelled "curated-by-claude-fable-5.1 (session run)". `run_agents.py`, the part
that is supposed to produce the briefing from the Claude API, has never executed end to end:
no API key was available. Its JSON-parsing paths (ledger, anatomy, verifier, summary,
correlations, scenarios, geopolitics) are untested against real model output and will fail on
the first malformed response. The scheduled workflow and the cloud-routine body are likewise
untested. The claim "the agents run twice a day without you" is a design, not an observation.
*Fix:* run the pipeline once with a key, fix what breaks, archive that run as the first real
edition; add a dry-run mode that replays a saved model output through every parser.

## 2. The curator audited its own work

**Blocker.** The Verifier's verdicts, the cross-checks, the scoring rationales, the breach
anatomies and the Ombudsman's conduct note for this run were all written by the same assistant
that wrote the items. The verification layer therefore verified nothing independently; it
restated the author's judgement in the Verifier's voice. The same is true of the conversations:
they are scripted disagreement, not emergent disagreement. *Fix:* the Verifier must run as a
separate model call with only the item and the pulled text, never the author's rationale; keep
a held-out set of items with known ground truth (CVE ids, dates, counts) and measure the
Verifier's catch rate each run.

## 3. No ground truth, no evaluation

**Major.** The system reports confidence and credibility on every line, but nothing measures
whether those grades are right. There is no eval set, no sampling of items for human review,
no record of how often a "confirmed" item was later contradicted. The Ombudsman counts
flags, which is activity, not accuracy. *Fix:* a weekly sample of ten items graded by a person
against the pulled primaries; publish the agreement rate on the dashboard; treat a falling rate
as a blocker.

## 4. Relevance is a keyword list

**Major.** Energy-cyber membership is decided by two keyword lists in nine languages. It
admitted a Rails bug (via "rail") and "politics" (via "ics") until whole-word matching was
added, and it still cannot see a story that names only a company or a place. The multilingual
lists are translations by the author, unreviewed by a native speaker. Recall is unknown.
*Fix:* a cheap model classification pass (Haiku) on every fetched story with the taxonomy as
the label set, measured against a hand-labelled sample; keep the keyword list as a pre-filter.

## 5. The direct-source puller is English-only and shallow

**Major.** Excerpts are chosen by English keyword overlap; the French victim statement that
matters most this week produced zero excerpts and was "read by hand", which means by the
author, which returns to finding 2. Primary-document discovery follows links from the outlet
page, so a primary the outlet did not link is never found. *Fix:* language-aware sentence
scoring (or the classification pass from finding 4), plus a per-vendor PSIRT lookup and a
NVD/KEV query for every CVE on the board, which is an API call, not a scrape.

## 6. Scoring is prose, not computation

**Major.** The rubric lists five severity factors with weights (3, 2, 1, 1, 1); nothing
computes them. The severity level is asserted and the rationale is written after it. Two
items with the same factor values could carry different levels. *Fix:* compute a score from
the factor values, show the arithmetic, and let the rationale explain only overrides.

## 7. Attribution hypotheses are speculation in a product

**Major.** The breach-anatomy layer offers attribution hypotheses with "low" confidence and a
[speculation] label. Labelled or not, naming a state next to an incident in a product that
executives read is the thing the rules say not to do (rule 26). A reader will remember the
state, not the label. *Fix:* restrict hypotheses to actors named by a government or a named
firm for that incident; for everything else say "unattributed" and list what evidence would
distinguish candidates, without naming them.

## 8. Coverage claims outrun the data

**Major.** 38 feeds in nine languages sounds broad; in this window the new feeds produced one
Latin American item (a relay of a UK press release), one Japanese item and one German item.
"No reporting from Africa / the Middle East" is stated honestly, but the dashboards still
present continent counts as if they were coverage. The history timeline shows 27 years with
~25 unverified cases. *Fix:* show feed count and item count per region side by side wherever a
regional claim appears; mark the history timeline "illustrative" until the Archivist verifies.

## 9. Security of the page

**Major.** The live-chat path stores an API key in localStorage and calls the provider from the
browser; any script injection on the page would read it. Fetched story text goes into the live
prompt verbatim, so a malicious headline in an allowlisted feed is a prompt injection into the
residents. `linkify` and the panels use innerHTML with escaping, which is correct today and one
careless edit from an XSS. *Fix:* prefer the proxy path and say so; strip or fence fetched text
in prompts and tell the model it is data; add a CSP header via the Pages host or a meta tag; a
lint rule that forbids unescaped template insertion.

## 10. The STIX export is invalid

**Minor, but it is an export.** Two report objects carry `external_references` entries with
`url: null`, which STIX 2.1 does not allow (omit the property instead). Objects use `uuid5` ids,
good, but `created` is regenerated every run so consumers see every object as modified. *Fix:*
drop null fields; keep `created` stable per id and bump only `modified`.

## 11. The front end is a 1,300-line monolith

**Minor.** One file, no tests beyond a Playwright smoke script run by hand, twenty-one top-bar
buttons, a canvas with no keyboard access and no screen-reader path, no mobile layout check
since the buildings went to three rows. *Fix:* split by view, add a smoke test to CI, add a
"views" menu, give every canvas object a list equivalent for accessibility.

## 12. Data model sprawl

**Minor.** `briefing.json` is 260 KB with eighteen top-level sections added one request at a
time; there is no schema version, and `validate.py` checks some sections and not others
(anatomy, scenarios, geopolitics, world_desk, executive_brief source_urls partly). The archive
copies the whole set every run. *Fix:* a `schema_version` field; a JSON Schema for the briefing
validated in CI; archive deltas or compress.

## 13. Duplicates and entity resolution

**Minor.** The Canadian centre's EN and FR feeds carry the same advisories; the Latin American
relay of the NCSC release is the same story as three others; nothing merges them, so
"corroboration" can count a translation as an independent source. Actors have aliases across
vendors; nothing maps them. *Fix:* near-duplicate detection on title+date across languages;
an actor alias table (Sandworm = APT44 = Seashell Blizzard).

## 14. The Gazette can be mistaken for journalism

**Minor, ethical.** A broadsheet with bylines by named people reads as reporting. The footer
says it is printed from data; the masthead does not say the residents are AI and the names are
invented. *Fix:* a standing masthead line: "Written by fourteen AI residents from an allowlist
of sources; names are fictional; see Methodology."

## 15. "Cyber Command" is a real agency's name

**Minor.** US Cyber Command exists. Naming the flag log that way invites confusion in exactly
the audience this is for. *Fix:* rename to "Incident Desk" or "Flag Log".

## What is missing entirely

- A human feedback loop inside the page (comments, strike-throughs, the signature), not a JSON edit.
- Change detection between runs at item level (what was added, dropped, re-graded), beyond verdicts.
- CVE enrichment from NVD and the KEV catalog (free APIs), which would settle "exploited?" for most items.
- Outage and incident datasets (DOE OE-417, E-ISAC public alerts, ENTSO-E) to answer "who was affected" with data instead of press.
- Push notifications outside the page; the inbox only works when you open it.
- Tests and CI for the scripts and the page; a LICENSE file; a CONTRIBUTING note.
- A native-speaker review of the nine keyword lists and bias notes.
- Any measurement of whether fourteen residents produce better analysis than three; the cast grew by request, not by evidence.

## What is sound

The sourcing discipline (allowlist with bias notes, primary over trade press, vendor intel
flagged, "I cannot verify this" as a required answer); the separation of importance from
correctness; the append-only flag log and archive; clickable sources on every claim; the
explicit statements of sample size and of what is not covered; the Human touch and
Limitations tabs; and a cost model that is measured where it can be and labelled where it
cannot. Those are the parts to keep while the rest is made true.
