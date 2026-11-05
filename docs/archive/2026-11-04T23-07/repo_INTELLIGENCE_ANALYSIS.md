# Intelligence analysis: the step-by-step procedure for an investigative agent

How a resident of this society, or a person, performs intelligence analysis to the standard
used by the FBI and the wider US Intelligence Community. This is a synthesis of public
standards, not an official document: the Intelligence Cycle as taught by the FBI and ODNI,
Intelligence Community Directive (ICD) 203 *Analytic Standards*, ICD 206 *Sourcing
Requirements for Disseminated Analytic Products*, the FBI/CISA joint advisory format, the
NATO/Admiralty source-grading system, and the structured analytic techniques in the CIA's
*Tradecraft Primer*. Each step names the resident who owns it here. Read RULES.md first;
where this file and RULES.md differ, RULES.md controls.

## The intelligence cycle (the loop every run follows)

| Phase | What it means | Who, here |
|---|---|---|
| 1. Planning and direction | Decide the question, the audience, the deadline, the collection plan | the human owner; the Ombudsman checks the plan against the rules |
| 2. Collection | Gather raw reporting from approved sources | `fetch_news.py` over the allowlist; the Librarian keeps the map |
| 3. Processing and exploitation | Turn raw reporting into usable records; translate, extract, tag | the Reporter fills the schema; `pull_sources.py` gets the direct text |
| 4. Analysis and production | Evaluate sources, correlate, judge, write with confidence and alternatives | Analyst, Critic, Wide-Angle, Contrarian, Counsel, Archivist, Operator, Economist, Geopolitical Analyst, Technologist |
| 5. Dissemination | Deliver in the form the consumer uses | the Briefing board, the Executive brief, the Gazette, STIX |
| 6. Evaluation and feedback | Measure what was wrong, what was late, what was missed; adjust | the Verifier, Cyber Command, the Ombudsman's conduct note, the human owner |

## Step by step

### Step 1. Define the requirement
1. Write the question in one sentence, with the consumer named (an energy-sector executive, a
   control-room engineer, a student) and the decision it supports.
2. Set scope: sector, geography (worldwide, US first), time window, and what is out of scope.
3. State the deadline and the form of the product (bullet brief, record, dossier, executive brief).
4. List the collection sources permitted (the allowlist) and the ones excluded (RULES.md §1.7).
5. Write down your key assumptions before you collect anything. You will check them in step 7.

### Step 2. Collect
1. Collect only from approved sources; log every source read, including the ones that returned
   nothing or were blocked (HTTP 403 is a collection fact, recorded in Cyber Command).
2. Capture each item with: title, date of event, date of reporting, outlet, outlet type and bias
   note, URL, and the raw text or a verbatim excerpt. Never a paraphrase at this stage.
3. Collect the primary document behind every secondary report where one exists: victim
   statement, vendor advisory, government advisory, statute, filing (`pull_sources.py`).
4. Note gaps explicitly: which sources could not be reached, which theatres or sectors produced
   nothing. Absence of reporting is a collection result, not an analytic conclusion.

### Step 3. Evaluate every source and every piece of information (ICD 206, Admiralty)
For each item record two independent grades:
- **Source reliability (A–F):** A completely reliable (primary document, victim, government
  advisory); B usually reliable (wire, established press with named sources); C fairly reliable
  (vendor research, a firm that sells the fix); D not usually reliable; E unreliable; F cannot be
  judged.
- **Information credibility (1–6):** 1 confirmed by independent sources; 2 probably true;
  3 possibly true; 4 doubtful; 5 improbable; 6 cannot be judged.
Then record: corroboration count (independent sources, not outlets repeating one press
release), claim-versus-confirmed, whether the direct source was pulled and whether it agrees
with the outlet (agree / differ / verdict). A vendor's exploitation claim is C at best until a
government or vendor-PSIRT notice exists. A leak-site claim is a claim.

### Step 4. Process into the record
1. Fill the intelligence record (`agents/schema.json`): event core; energy subsector and
   value-chain segment; IT / OT / PIT impact (mandatory); actor, type, attribution confidence and
   who attributed; CVE, KEV, initial access, malware, indicators, ATT&CK for ICS techniques;
   operational, physical, data and cascading impact; geopolitical link, regulatory trigger,
   government response; the two source grades; so-what; recommended action; trend.
2. Use only taxonomy values; the validator rejects anything else.
3. Keep the rationale with the score: why this severity and not the adjacent ones; why this
   letter; why this number.

### Step 5. Analyse: correlate, then judge
1. **Correlate across domains**: same actor, same technique, same vendor, same sector, same
   window, same policy. Record each link with its strength (strong / thematic / inferred /
   weak) and its evidence; mark inferred links as [inference].
2. **Reconstruct the behaviour**: initial access → foothold → crossing to OT → learning the
   process → effect → persistence, mapped to Purdue levels and ATT&CK for ICS. Say which steps
   are evidenced and which are inferred.
3. **Assess impact** on the consumer: operational, safety, financial (only with a source),
   regulatory, cascading. Separate what happened from what could happen.
4. **Ask who was NOT affected and why**, and what else was happening at the same time
   (RULES.md §5). Say when the answer is bounded by what was reported.
5. **Check the law** for any regulatory trigger against the primary instrument (the Counsel);
   trade press is discovery only.
6. **Place it in history** (the Archivist): has this happened before, to whom, what did it cost,
   is it new / campaign / rising / recurring, with the case cited.

### Step 6. Apply structured analytic techniques before you write a judgment
Use at least two of these on any judgment that will reach an executive:
- **Key Assumptions Check**: list the assumptions behind the judgment; for each, how confident,
  what evidence, what if it is wrong.
- **Analysis of Competing Hypotheses (ACH)**: list the plausible explanations (including
  "coincidence" and "reporting artefact"); score each piece of evidence as consistent,
  inconsistent or neutral with each hypothesis; prefer the hypothesis with the least
  inconsistent evidence, not the most consistent.
- **Devil's Advocacy** (the Contrarian): argue the opposite of the emerging judgment from the
  same evidence.
- **Indicators**: for each scenario, list what would confirm or refute it, so the next run can
  check rather than re-argue.
- **Red-team the attribution**: who else could it be, what evidence would distinguish them,
  and who benefits from the attribution being believed.

### Step 7. Write to ICD 203 analytic standards
Every product must:
1. **Be objective**: evidence first, judgment second; no advocacy.
2. **Be independent of political considerations**: the US-first scope is a relevance rule, not
   a conclusion.
3. **Be timely**: state the data's age; a snapshot's date is part of the product.
4. **Be based on all available sources** within the permitted set; say what was unavailable.
5. **Exhibit tradecraft**, meaning the product:
   - describes the quality and credibility of its sources (step 3);
   - expresses uncertainty with the standard words: *almost no chance / remote* (1–5%),
     *very unlikely / highly improbable* (5–20%), *unlikely / improbable* (20–45%),
     *roughly even chance* (45–55%), *likely / probable* (55–80%), *very likely / highly
     probable* (80–95%), *almost certain / nearly certain* (95–99%); never mix a probability
     word with a confidence word in one sentence;
   - states **confidence** (high / moderate / low) separately, based on source quality,
     corroboration and the strength of the reasoning;
   - distinguishes underlying reporting from assumptions and from judgments; labels
     [inference], [speculation], [unverified];
   - analyses alternatives (step 6) and says why they were set aside;
   - is relevant to the consumer: leads with the so-what and the action;
   - uses clear, logical argumentation; one claim per sentence, each with its source and date;
   - is consistent with prior products or explains the change (the Verifier's "what changed");
   - makes accurate judgments, meaning it does not overstate: a forecast is called a
     forecast, a claim a claim;
   - uses visuals where they clarify (the dashboard, the facility layers), never to decorate.
6. **Keep importance and correctness as separate columns.** Severity ranks what matters;
   reliability, credibility and the Verifier's verdict rank how much to trust it.

### Step 8. Produce in the consumer's format
- **Record** for analysts (the Briefing board, STIX for machines).
- **Bullets** for readers (the Summary, Cyber Bytes).
- **Executive brief** for decision-makers: ten threats, each with threat, why it matters,
  exposure, action, confidence, source; a "not on the list" line; a signature block.
- **Joint-advisory style** for defenders, following the FBI/CISA format: overview; technical
  details (TTPs mapped to ATT&CK, indicators); detection; mitigations; references; contact.
  The Operator writes the mitigations in shifts and windows, not in slogans.
- **Dossier** for learners (the facility pages): variables, layers, how a breach happens,
  cases, with the verification status of every case.

### Step 9. Verify before dissemination (the Verifier)
1. Pull the direct source for every claim that will be disseminated; set the outlet's text
   beside the primary's; record agree / differ / verdict; correct the record.
2. Issue a verdict per item: hold / upgrade / downgrade / retire, with the rule applied.
3. Report what changed since the last product.
4. Run the validator; a malformed product is not released.
5. Report every flag to Cyber Command the moment it is raised: unsourced sentence,
   single-source item, contradiction, downgrade, blocked page, suspected invention.

### Step 10. Disseminate, then evaluate (the Ombudsman and the human owner)
1. Release in the forms above; the page shows the data's age and the model used.
2. The human evaluator assesses the assembled picture rather than building it: opens the
   sources, checks the confidence lines, strikes what does not hold, signs or does not sign.
3. The Ombudsman reviews the run against RULES.md and the flag history for patterns, and
   writes the conduct note with proposals; the owner decides.
4. Record feedback as new requirements (step 1 of the next cycle).

## What this procedure forbids
- Inventing an incident, victim, number, quote or attribution. If it is not in the collected
  material, it is not in the product.
- Attributing an attack yourself. Quote the attributor and their confidence.
- Filling a gap with a plausible guess. "I cannot verify this" plus the last confirmed status
  with its date is the required form.
- Treating three outlets repeating one press release as three sources.
- Letting severity stand in for credibility, or the reverse.
- Changing the rules, the sources or the personas from inside a run. People do that.

## Where it lives in the code
Collection: `scripts/fetch_news.py`, `sources.json`. Processing: `agents/schema.json`,
`scripts/run_agents.py`. Verification: `scripts/pull_sources.py`, `scripts/validate.py`,
`scripts/command_log.py`. Production: `docs/` (board, brief, Gazette), `scripts/export_stix.py`.
Playbook for the unattended agent: `CURATION.md`. Rules: `RULES.md`. Register: `docs/REGISTER.md`.
