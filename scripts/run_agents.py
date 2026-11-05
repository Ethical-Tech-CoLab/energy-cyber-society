#!/usr/bin/env python3
"""Run the five residents over today's news and write docs/data/briefing.json.

All five agents run in the same process against the same news bundle. Each
produces its own briefing and canned answers to its suggested questions; then
pairs of agents hold short conversations, which the town plays as overheard
dialogue. If ANTHROPIC_API_KEY is missing, a deterministic fallback briefing is
written from the raw headlines so the Pages demo always has something to show.
"""
import json, os, sys, random, re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEWS = ROOT / "docs" / "data" / "news.json"
OUT = ROOT / "docs" / "data" / "briefing.json"
PERSONAS_COPY = ROOT / "docs" / "data" / "personas.json"
MODEL = os.environ.get("ECS_MODEL", "claude-sonnet-5-5")

personas = json.loads((ROOT / "agents" / "personas.json").read_text())
news = json.loads(NEWS.read_text())
AGENTS = personas["agents"]
BY_ID = {a["id"]: a for a in AGENTS}

def news_context(limit_energy=25, limit_wide=30):
    lines = ["# ENERGY-SECTOR STORIES (last %sh)" % news["window_hours"]]
    for i, s in enumerate(news["energy"][:limit_energy], 1):
        lines.append(f"E{i}. [{s['source_name']} | {s['source_type']} | {s['source_country']}] {s['title']} :: {s['summary'][:300]} :: {s['link']}")
    lines.append("\n# OTHER CYBER STORIES SAME PERIOD")
    for i, s in enumerate(news["wide"][:limit_wide], 1):
        lines.append(f"W{i}. [{s['source_name']}] {s['title']} :: {s['summary'][:200]}")
    lines.append("\n# SOURCE BIAS NOTES")
    for src in news["sources"]:
        lines.append(f"- {src['name']} ({src['type']}, {src['country']}): {src['bias_note']}")
    return "\n".join(lines)

def system_for(a):
    return (f"You are {a['name']}, {a['role']} of the town. {a['job']} Voice: {a['voice']}\n"
            f"{personas['shared_rules']}")

# ---------------------------------------------------------------- Claude path
def run_with_claude():
    import anthropic
    client = anthropic.Anthropic()
    ctx = news_context()

    # The news bundle is identical across all ~44 calls of a run, so it goes first in a
    # cached system block (prompt caching: ~90% off the input cost of every call after the first).
    def sys_blocks(agent):
        return [{"type": "text", "text": "TODAY'S NEWS BUNDLE (shared by every resident):\n" + ctx, "cache_control": {"type": "ephemeral"}},
                {"type": "text", "text": system_for(agent)}]
    usage = {"input": 0, "cached": 0, "output": 0, "calls": 0}
    def tally(r):
        u = r.usage; usage["calls"] += 1; usage["input"] += u.input_tokens; usage["output"] += u.output_tokens
        usage["cached"] += getattr(u, "cache_read_input_tokens", 0) or 0
    def ask(agent, prompt, max_tokens=700):
        r = client.messages.create(model=MODEL, max_tokens=max_tokens, system=sys_blocks(agent),
            messages=[{"role": "user", "content": prompt}])
        tally(r)
        return "".join(b.text for b in r.content if b.type == "text").strip()

    result = {"agents": {}, "conversations": []}
    for a in AGENTS:
        print("briefing:", a["id"], file=sys.stderr)
        briefing = ask(a, "Write your briefing for today in your own voice, 4 to 7 sentences, with the source named after each claim. If the energy bucket is thin, say so honestly.")
        answers = {}
        for q in a["questions"]:
            answers[q] = ask(a, f"A visitor to the town asks you: \"{q}\" Answer in 3 to 6 sentences, naming sources.", 500)
        headline = ask(a, "Give one speech-bubble line of at most 12 words you might say today while walking around town. Output only the line.", 60)
        result["agents"][a["id"]] = {"briefing": briefing, "answers": answers, "bubble": headline.strip('"')}

    # structured intelligence ledger: the Reporter fills the schema, the Contrarian audits it
    schema = json.loads((ROOT / "agents" / "schema.json").read_text())
    print("ledger", file=sys.stderr)
    r = client.messages.create(model=MODEL, max_tokens=6000, system=system_for(BY_ID["reporter"]),
        messages=[{"role": "user", "content": f"TODAY'S NEWS BUNDLE:\n{ctx}\n\nFill this intelligence record for each energy-relevant story (max 12), using only the allowed values in the taxonomy. Output ONLY a JSON array of items.\nSCHEMA:\n{json.dumps(schema)}"}])
    tally(r)
    txt = "".join(b.text for b in r.content if b.type == "text"); m = re.search(r"\[.*\]", txt, re.S)
    try: result["items"] = json.loads(m.group(0)) if m else []
    except json.JSONDecodeError: result["items"] = []
    sm = client.messages.create(model=MODEL, max_tokens=2500, system=sys_blocks(BY_ID["reporter"]),
        messages=[{"role": "user", "content": "Write the week's summary as JSON only: {\"headline\": one sentence, \"bullets\": [{\"text\": one-sentence bullet, \"sources\": [\"Outlet, YYYY-MM-DD\"], \"tag\": \"region · kind\"}] (6 to 10, US first), \"considerations\": [5 critical-thought sentences: absence of evidence, corroboration vs severity, vendor framing, what could not be verified, what spills over from the wider bucket]}"}])
    tally(sm); smt = "".join(b.text for b in sm.content if b.type == "text"); smm = re.search(r"\{.*\}", smt, re.S)
    try: result["summary"] = json.loads(smm.group(0)) if smm else None
    except json.JSONDecodeError: result["summary"] = None
    result["us_status"] = ask(BY_ID["contrarian"], "In one or two sentences: was any US energy operator (utility, pipeline, refinery, LNG, nuclear) confirmed breached in this bundle? If not, say so plainly and say what the US items are instead.", 200)

    # verifier pass over the ledger
    print("verifier", file=sys.stderr)
    vr = client.messages.create(model=MODEL, max_tokens=3000, system=sys_blocks(BY_ID["verifier"]),
        messages=[{"role": "user", "content": f"BOARD ITEMS:\n{json.dumps(result['items'])}\n\nPROCEDURE:\n{json.dumps(personas['verification_procedure'])}\n\nAudit every item. Output ONLY JSON: {{\"verdicts\": {{\"<headline>\": {{\"verdict\": \"hold|upgrade|downgrade|retire + grade\", \"reason\": \"rule applied\"}}}}, \"summary\": \"one paragraph\"}}"}])
    tally(vr)
    vt = "".join(b.text for b in vr.content if b.type == "text"); vm = re.search(r"\{.*\}", vt, re.S)
    try: result["verification"] = json.loads(vm.group(0)) if vm else {}
    except json.JSONDecodeError: result["verification"] = {}
    result["verification"]["run_at"] = datetime.now(timezone.utc).isoformat()

    # correlations + scenarios + geopolitics (Analyst, Operator and Geopolitical Analyst)
    for key, who, prompt, mt in [("correlations", "analyst", "Output ONLY a JSON array of correlations between board items across domains: [{\"between\": [headline, headline], \"domains\": [..], \"link\": \"...\", \"strength\": \"strong|thematic|inferred|weak\", \"evidence\": \"(Outlet, date) or [inference]\"}]", 2000),
                                 ("scenarios", "operator", "For the three most important board items output ONLY a JSON array: [{\"story\": headline, \"title\": \"...\", \"action_now\": \"...\", \"impact_chain\": \"a → b → c\", \"scenarios\": [{\"name\", \"likelihood\": \"likely|possible|unlikely|cannot assess\", \"what\", \"confirms\"} x3]}]", 3000),
                                 ("geopolitics", "geopolitics", "Output ONLY JSON: {\"theatres\": [{\"conflict\", \"parties\", \"evidence_this_week\": [..], \"layers\": {\"IT\", \"OT\", \"PIT\"}, \"subsectors\": [..], \"us_relevance\", \"confidence\"}], \"absent_this_week\": [..], \"note\": \"...\"}", 3000)]:
        if who not in BY_ID: continue
        rr = client.messages.create(model=MODEL, max_tokens=mt, system=sys_blocks(BY_ID[who]), messages=[{"role": "user", "content": f"BOARD ITEMS:\n{json.dumps(result.get('items', []))}\n\n{prompt}"}])
        tally(rr); tt = "".join(bb.text for bb in rr.content if bb.type == "text"); mm = re.search(r"[\[{].*[\]}]", tt, re.S)
        try: result[key] = json.loads(mm.group(0)) if mm else None
        except json.JSONDecodeError: result[key] = None
    prev = json.loads(OUT.read_text()) if OUT.exists() else {}
    result["human_touch"] = prev.get("human_touch")

    pairs = [("reporter", "analyst"), ("critic", "reporter"), ("contrarian", "analyst"), ("wideangle", "contrarian"), ("critic", "wideangle"), ("verifier", "contrarian"), ("counsel", "contrarian"), ("operator", "analyst"), ("geopolitics", "wideangle"), ("economist", "archivist"), ("ombudsman", "verifier"), ("librarian", "verifier"), ("technologist", "economist")]
    for x, y in pairs:
        ax, ay = BY_ID[x], BY_ID[y]
        print("conversation:", x, y, file=sys.stderr)
        r = client.messages.create(
            model=MODEL, max_tokens=900,
            system=(f"You write a short dialogue between two residents of a town about today's energy-cyber news. "
                    f"Resident A: {ax['name']}, {ax['role']}. {ax['job']} Voice: {ax['voice']}\n"
                    f"Resident B: {ay['name']}, {ay['role']}. {ay['job']} Voice: {ay['voice']}\n"
                    f"{personas['shared_rules']} They should disagree or sharpen each other, not agree politely. "
                    f"Output ONLY a JSON array of 6 objects {{\"who\": \"{x}\" or \"{y}\", \"line\": \"...\"}}, each line under 30 words, alternating speakers starting with {x}."),
            messages=[{"role": "user", "content": f"TODAY'S NEWS BUNDLE:\n{ctx}"}])
        tally(r)
        txt = "".join(b.text for b in r.content if b.type == "text")
        m = re.search(r"\[.*\]", txt, re.S)
        try:
            lines = json.loads(m.group(0)) if m else []
        except json.JSONDecodeError:
            lines = []
        if lines:
            result["conversations"].append({"between": [x, y], "lines": lines})
    result["usage"] = usage
    print(f"usage: {usage}", file=sys.stderr)
    return result, MODEL

# -------------------------------------------------------------- fallback path
def run_fallback():
    """No API key: build a sober briefing from the headlines themselves."""
    en, wd = news["energy"], news["wide"]
    def cite(s): return f"{s['title']} ({s['source_name']})"
    top = en[:5]
    us = [s for s in en if s["source_country"] == "US"]
    intl = [s for s in en if s["source_country"] != "US"]
    srcs_used = {s["source"] for s in en}
    bias = [f"{src['name']}: {src['bias_note']}" for src in news["sources"] if src["id"] in srcs_used]
    r = {"agents": {}, "conversations": [], "items": [], "us_status": "Headlines-only mode: nobody has checked."}
    r["agents"]["reporter"] = {
        "briefing": ("Here is what the allowlisted feeds carried on energy-sector cyber in the last %d hours. " % news["window_hours"]
                     + (" ".join(cite(s) + "." for s in top) if top else "The energy bucket is thin today; no story matched the energy filter, so I will not invent one.")
                     + " I have not yet had a model run over these, so this is headlines only, not analysis."),
        "answers": {
            AGENTS[0]["questions"][0]: " ".join(cite(s) + "." for s in top) or "Nothing matched the energy filter today.",
            AGENTS[0]["questions"][1]: " ".join(cite(s) + "." for s in us[:4]) or "No US-sourced energy story in the window.",
            AGENTS[0]["questions"][2]: "In headlines-only mode I cannot separate confirmed from claimed. Treat every line above as a claim by the outlet until the full agent run happens."},
        "bubble": top[0]["title"][:60] if top else "Quiet day on the energy wire."}
    r["agents"]["analyst"] = {
        "briefing": "I only have headlines until the model run, so no attribution from me today. " + (" ".join(f"Worth a deeper look: {cite(s)}." for s in en[:3]) if en else "Nothing in the energy bucket to analyze."),
        "answers": {q: "I will not attribute from a headline. Ask again after the daily agent run, or paste a key in Settings for a live answer." for q in AGENTS[1]["questions"]},
        "bubble": "Headlines are not evidence."}
    r["agents"]["critic"] = {
        "briefing": "Sources in play today and what to keep in mind about each: " + " ".join(bias[:6]) if bias else "No sources in the energy bucket today.",
        "answers": {AGENTS[2]["questions"][0]: " ".join(bias) or "No energy stories, so no sources to critique.",
                    AGENTS[2]["questions"][1]: "Check whether any headline names a vendor report; vendor research sells the solution to the problem it describes.",
                    AGENTS[2]["questions"][2]: f"{len(us)} US-sourced versus {len(intl)} internationally sourced energy stories in this window."},
        "bubble": "Who owns the outlet that wrote that?"}
    r["agents"]["wideangle"] = {
        "briefing": "Elsewhere in cyberspace at the same time: " + " ".join(cite(s) + "." for s in wd[:5]),
        "answers": {q: " ".join(cite(s) + "." for s in wd[:6]) for q in AGENTS[3]["questions"]},
        "bubble": wd[0]["title"][:60] if wd else "Watching the wider sky."}
    r["agents"]["contrarian"] = {
        "briefing": "Before anyone says 'the grid was attacked': the headlines above do not tell us who was spared, and silence in coverage is not evidence of impact. Ask who is missing from each story.",
        "answers": {q: "Headlines-only mode. The honest answer is that nobody has checked who was not affected yet." for q in AGENTS[4]["questions"]},
        "bubble": "And who was NOT affected?"}
    for aid, a in BY_ID.items():
        if aid not in r["agents"]:
            r["agents"][aid] = {"briefing": "Headlines-only mode; nothing for me to work on until an agent run produces board items.",
                "answers": {q: "Nothing to work on until an agent run produces board items." for q in a["questions"]}, "bubble": "Waiting for the run."}
    if top:
        r["conversations"].append({"between": ["reporter", "contrarian"], "lines": [
            {"who": "reporter", "line": f"Top of the wire: {top[0]['title'][:70]} ({top[0]['source_name']})."},
            {"who": "contrarian", "line": "Headline says affected. Does the body say who wasn't?"},
            {"who": "reporter", "line": "Not yet. That's the agent run's job, not mine."},
            {"who": "contrarian", "line": "Then it's a claim, not a finding."}]})
    return r, "fallback-headlines"

def main():
    if os.environ.get("ANTHROPIC_API_KEY"):
        result, model = run_with_claude()
    else:
        print("ANTHROPIC_API_KEY not set; writing headline-only fallback briefing", file=sys.stderr)
        result, model = run_fallback()
    result.update({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "news_generated_at": news["generated_at"],
        "model": model,
        "counts": {"energy": len(news["energy"]), "wide": len(news["wide"])},
        "top_stories": news["energy"][:8],
    })
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False))
    PERSONAS_COPY.write_text(json.dumps(personas, indent=1, ensure_ascii=False))  # Pages serves docs/ only
    print(f"wrote {OUT} using {model}")

if __name__ == "__main__":
    main()
