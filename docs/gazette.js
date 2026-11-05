const esc = t => String(t == null ? '' : t).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
(async () => {
  const run = new URLSearchParams(location.search).get('run'); const base = run ? `archive/${run}/` : 'data/';
  const [b, n] = await Promise.all([fetch(base + 'briefing.json').then(r => r.json()), fetch(base + 'news.json').then(r => r.json()).catch(() => null)]);

  const d = new Date(b.news_generated_at || b.generated_at);
  document.getElementById('date').textContent = d.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  document.getElementById('edition').textContent = run ? 'Archived edition ' + run : (b.model || '').includes('session') ? 'Hand-set edition' : 'Morning edition';
  document.getElementById('stamp').textContent = b.us_status && /no confirmed/i.test(b.us_status) ? 'NO US OPERATOR BREACHED' : 'SEE BOARD';
  const sm = b.summary || { headline: 'No summary yet', bullets: [], considerations: [] };
  document.getElementById('lead').textContent = sm.headline;
  document.getElementById('deck').textContent = b.us_status || '';
  if (b.sample) document.getElementById('price').textContent = `Sample: ${b.sample.feeds} feeds · ${b.sample.window_hours}h · ${b.sample.stories_fetched} stories · ${b.sample.board_items} items`;
  const A = b.agents || {}, names = { reporter: 'Dana Okafor', analyst: 'Mateo Reyes', critic: 'Priya Venkataraman', wideangle: 'Samir Haddad', contrarian: 'Ingrid Solberg', verifier: 'Tomasz Nowak', librarian: 'Aisha Bello' };
  const items = (b.items || []).slice().sort((x, y) => ({ critical: 0, high: 1, medium: 2, low: 3, info: 4 }[x.severity] ?? 9) - ({ critical: 0, high: 1, medium: 2, low: 3, info: 4 }[y.severity] ?? 9));
  const V = (b.verification && b.verification.verdicts) || {};
  let html = '';
  items.forEach((it, i) => { html += `<div class="story"><div class="kicker">${esc(it.country)} · ${esc(it.subsector)} · ${esc(it.ot_impact)}</div><h3>${esc(it.headline)}</h3><p>${esc(it.so_what)}${it.operational_impact ? ' ' + esc(it.operational_impact) + '.' : ''}</p><div class="byline">${(it.sources || []).map(s => (s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name)}</a>` : esc(s.name)) + (s.date ? ', ' + esc(s.date) : '')).join('; ')}${V[it.headline] ? ' · Verifier: ' + esc(V[it.headline].verdict) : ''}${(it.labels || []).length ? ' · (unverified: ' + esc(it.labels[0].slice(0, 70)) + ')' : ''}</div></div>`;
    if (i === 1) html += `<div class="box"><h4>In brief</h4><ul>${sm.bullets.slice(0, 6).map(x => `<li>${esc(x.text)} <i>(${(x.source_urls || []).length ? x.source_urls.map(u => `<a href="${esc(u.url)}" target="_blank" rel="noopener">${esc(u.name)}</a>`).join('; ') : esc((x.sources || []).join('; '))})</i></li>`).join('')}</ul></div>`;
    if (i === 3) html += `<div class="box"><h4>Opinion · The Contrarian</h4><p style="font-size:12.5px">${esc((A.contrarian || {}).briefing || '')}</p><div class="byline">— ${names.contrarian}</div></div>`;
    if (i === 5) html += `<div class="box"><h4>Press review</h4><p style="font-size:12.5px">${esc((A.critic || {}).briefing || '')}</p><div class="byline">— ${names.critic}</div></div>`; });
  if (b.executive_brief) html += `<div class="box"><h4>Ten threats for the boardroom${b.executive_brief.evaluation.signed ? '' : ' · unsigned'}</h4><ol style="font-size:12px;padding-left:18px;margin:0">${b.executive_brief.threats.map(t => `<li><b>${esc(t.threat.split(' (')[0])}</b>: ${esc(t.action)} <i>(${esc(t.confidence)})</i> ${(t.source_urls || []).map(u => `<a href="${esc(u.url)}" target="_blank" rel="noopener">[${esc(u.name.split(' ')[0])}]</a>`).join(' ')}</li>`).join('')}</ol></div>`;
  html += `<div class="box"><h4>Editor's considerations</h4><ul>${sm.considerations.map(t => `<li>${esc(t)}</li>`).join('')}</ul></div>`;
  html += `<div class="box"><h4>Elsewhere in cyberspace</h4><p style="font-size:12.5px">${esc((A.wideangle || {}).briefing || '')}</p><div class="byline">— ${names.wideangle}</div></div>`;
  html += `<div class="box"><h4>From the Verification Office</h4><p style="font-size:12.5px">${esc((b.verification || {}).summary || '')}</p><div class="byline">— ${names.verifier}</div></div>`;
  if (b.world_desk) html += `<div class="box"><h4>World desk</h4>${Object.entries(b.world_desk.continents).map(([c, t]) => `<p style="font-size:12px;margin:0 0 4px"><b>${esc(c)}.</b> ${esc(t)}</p>`).join('')}<p class="byline">${esc(b.world_desk.note)}</p></div>`;
  if (n) html += `<div class="box"><h4>The wire · classifieds</h4><div class="classified">${n.energy.map(s => `<div><b>${esc(s.source_name)}</b>: <a href="${esc(s.link)}" target="_blank" rel="noopener">${esc(s.title)}</a></div>`).join('')}</div></div>`;
  document.getElementById('cols').innerHTML = html;
})();
