/* Validation topology: how a story becomes a Gazette line. Same pattern as the neocloud-supply-os
   topology (clickable nodes, packets along edges, a step list), driven by a real board item. */
(() => {
const esc = t => String(t == null ? '' : t).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const NODES = {
  X: { x: 20, y: 30, w: 190, h: 46, t: 'External sources', s: '38 feeds · 9 languages', d: 'Feeds, primary documents, NVD and CISA KEV, NWS, ISOs. Untrusted until graded. Nothing outside sources.json enters.' },
  H: { x: 280, y: 20, w: 220, h: 52, t: 'Humans', s: 'owner · signer', d: 'Set intent; edit rules, sources, personas and dossiers; merge the Engineer\'s PRs; sign the executive brief. The only authority over policy (rule 31).', cls: 'human' },
  C: { x: 300, y: 110, w: 180, h: 46, t: 'Conductor', s: 'scheduled runtime', d: 'Follows CURATION.md twice a day. Never parses raw feeds; reasons over the Reader\'s structured records. A dry-run replay exercises every parser without a key.' },
  E: { x: 20, y: 200, w: 190, h: 46, t: 'Envoy: fetch_news.py', s: 'allowlist only', d: 'The only door. Reads the allowlisted feeds, applies the energy-and-cyber filter, collapses cross-language duplicates, writes news.json.' },
  D: { x: 280, y: 200, w: 220, h: 56, t: 'Desks ×14 + Engineer', s: 'typed records', d: 'Reporter, Analyst, Critic, Wide-Angle, Contrarian, Librarian, Counsel, Archivist, Operator, Economist, Geopolitics, Technologist, Ombudsman. They never fetch. Each story becomes a schema record with two separate grades: importance and trust.' },
  A: { x: 560, y: 200, w: 180, h: 46, t: 'Auditor: Verifier', s: 'independent input', d: 'Sees only the stripped facts and the pulled text, never the author\'s rationale. Issues hold / upgrade / downgrade / retire per item, writes the cross-check (agree, differ, verdict) and what changed since last run. A ground-truth file measures its agreement rate.' },
  R: { x: 20, y: 310, w: 190, h: 46, t: 'Reader (quarantined)', s: 'text fenced as data', d: 'news.json plus pull_sources.py, which fetches the direct source and any primary document behind every item, and enrich_cves.py (NVD, KEV). Fetched text is fenced as DATA in every prompt: a malicious headline is never an instruction.' },
  P: { x: 280, y: 300, w: 220, h: 50, t: 'Policy Engine (code)', s: 'RULES.md · validate.py', d: 'Deterministic. Rejects a briefing with an unsourced bullet, a severity that disagrees with the computed score without an override reason, or an attribution without a named attributor. command_log.py reports every breach to the Incident Desk, append-only.', cls: 'gate' },
  L: { x: 280, y: 400, w: 220, h: 50, t: 'Ledger', s: 'briefing.json · archive', d: 'The published record plus docs/archive/<run>/, history.json, STIX and the engineering log. Nothing overwritten. The Gazette and every tab only read the ledger.' },
  G: { x: 560, y: 400, w: 180, h: 50, t: 'Gazette + brief', s: 'views of the ledger', d: 'The broadsheet prints items, verdicts and sources straight from the ledger with a masthead that says AI residents wrote it. The executive brief stays UNSIGNED until a person evaluates it.' },
};
const EDGES = [
  ['M390,72 L390,110', 'intent, rules', 398, 95],
  ['M390,156 L390,200', 'tasks', 398, 182],
  ['M390,256 L390,300', 'proposed records', 398, 282],
  ['M390,350 L390,400', 'allowed only', 398, 379],
  ['M115,76 L115,200', 'RSS, HTTP', 123, 142],
  ['M115,246 L115,310', 'raw stories', 123, 282],
  ['M210,333 C250,333 242,242 280,242', 'schema data', 224, 365],
  ['M560,223 L500,223', 're-checks', 504, 216, 'dash'],
  ['M500,325 H520 Q528,325 528,317 V53 Q528,45 520,45 H500', 'out of mandate|→ a person', 536, 140, 'escalate'],
  ['M500,425 L560,425', 'reads', 512, 418],
  ['M650,246 C650,300 500,300 500,320', 'verdicts', 600, 300, 'dash'],
];
const svg = document.getElementById('vtopo'); if (!svg) return;
svg.innerHTML = EDGES.map(([d, label, lx, ly, kind], i) => { const lines = label.split('|').map((t, j) => `<tspan x="${lx}" dy="${j ? 12 : 0}">${esc(t)}</tspan>`).join(''); return `<path id="ve${i}" class="edge ${kind === 'dash' ? 'dash' : ''} ${kind === 'escalate' ? 'esc' : ''}" d="${d}"/><text class="elabel" x="${lx}" y="${ly}">${lines}</text>`; }).join('') + Object.entries(NODES).map(([k, n]) => `<g class="node ${n.cls || ''}" data-n="${k}" tabindex="0" role="button" aria-label="${esc(n.t)}"><rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="8"/><text x="${n.x + 12}" y="${n.y + 20}">${esc(n.t)}</text><text class="sub" x="${n.x + 12}" y="${n.y + 36}">${esc(n.s)}</text></g>`).join('') + '<g id="vpackets"></g>';
function showNode(k) { const n = NODES[k]; svg.querySelectorAll('.node').forEach(g => g.classList.toggle('on', g.dataset.n === k)); document.getElementById('vnode').innerHTML = `<span class="k">${esc(n.s)}</span><h4>${esc(n.t)}</h4><p>${esc(n.d)}</p>`; }
svg.addEventListener('click', e => { const g = e.target.closest('.node'); if (g) showNode(g.dataset.n); });
svg.addEventListener('keydown', e => { const g = e.target.closest('.node'); if (g && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); showNode(g.dataset.n); } });
showNode('C');
const packets = svg.querySelector('#vpackets');
function sendPacket(i, cls = '', dur = 900) { return new Promise(res => { const path = svg.querySelector('#ve' + i), L = path.getTotalLength(); const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle'); c.setAttribute('r', 4.5); c.setAttribute('class', 'packet ' + cls); packets.appendChild(c); const t0 = performance.now(); const step = now => { const k = Math.min(1, (now - t0) / dur), p = path.getPointAtLength(L * (1 - Math.pow(1 - k, 2))); c.setAttribute('cx', p.x); c.setAttribute('cy', p.y); if (k < 1) requestAnimationFrame(step); else { c.remove(); res(); } }; requestAnimationFrame(step); }); }
const sleep = ms => new Promise(r => setTimeout(r, ms));
let playing = false, briefing = null, sources = null;
function stepsFor(it) {
  const V = (briefing.verification || {}); const v = V.verdicts && V.verdicts[it.headline]; const c = V.crosschecks && V.crosschecks[it.headline]; const r = sources && sources.items && sources.items[it.headline];
  const flags = ((window.ECS_CMDLOG || {}).events || []).filter(e => e.item === it.headline);
  const sc = it.scoring || {};
  return [
    { n: 'E', edges: [4], text: `Envoy fetched ${(it.sources || []).length} allowlisted source${(it.sources || []).length > 1 ? 's' : ''} for this story: ${(it.sources || []).map(s => s.name).join('; ')}.` },
    { n: 'R', edges: [5], text: `Reader: energy signal + cyber signal passed the filter; text fenced as data. Direct-source pull: ${r ? (r.sources || []).filter(x => x.status === 200).length + ' outlet page(s) and ' + (r.primary || []).filter(x => x.status === 200).length + ' primary page(s) fetched' : 'no pull record'}${(it.cve_details || []).length ? '; NVD/KEV: ' + it.cve_details.map(d => d.id + (d.kev && d.kev.listed ? ' EXPLOITED (KEV)' : d.kev ? ' not in KEV' : '')).join(', ') : ''}.` },
    { n: 'D', edges: [6, 1], text: `Desks wrote the record: ${it.severity} severity (${sc.computed ? sc.computed.points + ' points computed → ' + sc.computed.level + (sc.override_reason ? '; override: ' + sc.override_reason.slice(0, 90) : '') : 'no computed score'}); trust ${it.source_reliability}${it.info_credibility} (${it.claim_vs_confirmed}); IT/OT: ${it.ot_impact}; case type: ${it.case_type || 'n/a'}; attribution: ${it.attribution_tier || 'n/a'}.` },
    { n: 'A', edges: [7, 10], text: v ? `Verifier (independent input): ${v.verdict}. ${v.reason}${c ? ' Cross-check ' + (c.compared || []).join(' vs ') + ': ' + c.verdict + '. Differ: ' + c.differ.slice(0, 120) : ''}` : 'Verifier: no verdict recorded for this item.' },
    { n: 'P', edges: [2], text: `Policy Engine: validate.py checks sources present, taxonomy values, scoring rationale, computed-vs-asserted severity, attribution rule. ${flags.length} flag${flags.length === 1 ? '' : 's'} on this item in the Incident Desk${flags.length ? ': ' + [...new Set(flags.map(f => f.type))].join(', ') : ''}. ${(it.labels || []).length ? 'Labels: ' + it.labels.map(l => l.slice(0, 60)).join(' · ') : ''}` },
    { n: 'L', edges: [3], text: `Ledger: written to briefing.json, archived under docs/archive/, exported to STIX. Nothing overwritten.` },
    { n: 'G', edges: [9], text: `Gazette prints it with its sources and the Verifier's verdict; the executive brief line stays unsigned until a person reviews it.` },
    { n: 'H', edges: [8], text: `Out of mandate → a person: ${(it.labels || []).some(l => l.includes('[unverified]')) ? 'this item carries [unverified] labels a person must resolve' : 'nothing escalated on this item'}; the brief awaits signature.` },
  ];
}
async function play() {
  if (playing || !briefing) return; playing = true; document.getElementById('vplay').disabled = true;
  const sel = document.getElementById('vitem'); const it = briefing.items.find(x => x.headline === sel.value) || briefing.items[0];
  const steps = stepsFor(it); const list = document.getElementById('vsteps'); list.innerHTML = steps.map((s, i) => `<li data-i="${i}"><b>${esc(NODES[s.n].t)}</b> ${esc(s.text)}</li>`).join('');
  for (let i = 0; i < steps.length; i++) { list.querySelectorAll('li').forEach((li, j) => li.classList.toggle('on', j === i)); showNode(steps[i].n); for (const e of steps[i].edges) await sendPacket(e, steps[i].n === 'A' ? 'risk' : '', 800); await sleep(500); }
  await sleep(600); list.querySelectorAll('li').forEach(li => li.classList.remove('on')); document.getElementById('vplay').disabled = false; playing = false;
}
window.ECS_PIPELINE = { init(b, s, cmd) { briefing = b; sources = s; window.ECS_CMDLOG = cmd; const sel = document.getElementById('vitem'); sel.innerHTML = (b.items || []).map(it => `<option>${esc(it.headline)}</option>`).join(''); }, play };
document.getElementById('vplay').addEventListener('click', play);
})();
