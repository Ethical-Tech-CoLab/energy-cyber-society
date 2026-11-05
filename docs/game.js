/* Energy Cyber Society — a pixel town of five LLM agents.
   Data: data/briefing.json (daily agent run) + data/news.json (raw wire) + ../agents/personas.json (voices). */
(() => {
const S = 3;                           // pixel scale
const W = 960, H = 560;
const cv = document.getElementById('town');
const ctx = cv.getContext('2d');
ctx.imageSmoothingEnabled = false;

let personas, briefing, news, sources, lookmap, buildings;
let agents = [];
let selected = null;
let bubbles = [];                      // {agent, text, until}
let convo = null;                      // running overheard conversation
let t0 = performance.now();
let chatter = true, convoIdx = -1, nextConvoAt = 1500;
const MEETING_SPOTS = [{ x: 480, y: 330 }, { x: 300, y: 250 }, { x: 660, y: 250 }, { x: 200, y: 300 }, { x: 760, y: 300 }, { x: 480, y: 240 }];

// ---------------------------------------------------------------- buildings
const BUILDINGS = [
  { key: 'Newsroom',          x: 90,  y: 110, w: 150, h: 110, color: '#5a4a2c', roof: '#e8b04b' },
  { key: 'Threat Lab',        x: 400, y: 80,  w: 170, h: 120, color: '#2c4a5a', roof: '#4bb3e8' },
  { key: 'Press Review',      x: 720, y: 110, w: 150, h: 110, color: '#4a2c5a', roof: '#c94be8' },
  { key: 'Observatory',       x: 130, y: 340, w: 150, h: 120, color: '#2c5a3e', roof: '#4be89a' },
  { key: "Devil's Advocate",  x: 700, y: 340, w: 160, h: 115, color: '#5a2c2c', roof: '#e85a4b' },
  { key: 'Verification Office', x: 400, y: 440, w: 160, h: 80, color: '#3a3f4a', roof: '#e6e9ef' },
  { key: 'Library',            x: 40,  y: 470, w: 120, h: 70, color: '#4a4420', roof: '#e8d44b' },
];
const PLAZA = { x: 380, y: 300, w: 200, h: 120 };

function rect(x, y, w, h, c) { ctx.fillStyle = c; ctx.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h)); }

function drawGround() {
  rect(0, 0, W, H, '#1d2b1f');
  // grass noise, deterministic
  for (let i = 0; i < 400; i++) {
    const x = (i * 97) % W, y = (i * 193) % H;
    rect(x, y, S, S, i % 3 ? '#223325' : '#182419');
  }
  // paths
  ctx.fillStyle = '#6b5f4a';
  rect(0, 262, W, 26, '#6b5f4a');                 // main street
  rect(165, 220, 26, 50, '#6b5f4a'); rect(485, 200, 26, 70, '#6b5f4a'); rect(795, 220, 26, 50, '#6b5f4a');
  rect(205, 288, 26, 60, '#6b5f4a'); rect(775, 288, 26, 60, '#6b5f4a');
  rect(PLAZA.x, PLAZA.y, PLAZA.w, PLAZA.h, '#7a6c55'); rect(PLAZA.x + PLAZA.w/2 - 13, PLAZA.y + PLAZA.h, 26, 30, '#6b5f4a');
  for (let i = 0; i < 30; i++) rect(PLAZA.x + (i * 37) % PLAZA.w, PLAZA.y + (i * 53) % PLAZA.h, S, S, '#8a7b62');
  // the substation in the plaza: the town's reason to exist
  rect(455, 330, 50, 40, '#3a3f4a'); rect(460, 318, 6, 12, '#9aa3b5'); rect(494, 318, 6, 12, '#9aa3b5');
  rect(466, 312, 28, 6, '#9aa3b5');
  ctx.fillStyle = '#e8b04b'; ctx.font = '10px "Press Start 2P"'; ctx.textAlign = 'center';
  ctx.fillText('⚡', 480, 356);
  // power lines
  ctx.strokeStyle = '#9aa3b5'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(463, 318); ctx.lineTo(0, 240); ctx.moveTo(497, 318); ctx.lineTo(W, 240); ctx.stroke();
}

function drawBuilding(b, lit) {
  rect(b.x, b.y, b.w, b.h, b.color);
  rect(b.x - 6, b.y - 18, b.w + 12, 22, b.roof);
  rect(b.x - 6, b.y - 18, b.w + 12, 4, '#05070b');
  // windows
  for (let r = 0; r < 2; r++) for (let c = 0; c < Math.floor(b.w / 36); c++) {
    const on = lit || ((r * 7 + c * 13) % 5 !== 0);
    rect(b.x + 14 + c * 36, b.y + 16 + r * 36, 16, 16, on ? '#f6e7a1' : '#0b0e14');
  }
  // door
  rect(b.x + b.w / 2 - 10, b.y + b.h - 28, 20, 28, '#1a1410');
  // sign
  ctx.fillStyle = '#05070b'; ctx.fillRect(b.x + 4, b.y - 36, b.w - 8, 14);
  ctx.fillStyle = '#e6e9ef'; ctx.font = '8px "Press Start 2P"'; ctx.textAlign = 'center';
  ctx.fillText(b.key.toUpperCase(), b.x + b.w / 2, b.y - 26);
}

// ---------------------------------------------------------------- characters (16x24 pixel figure)
function drawFigure(g, x, y, frame, facing, p, scale = S) {
  const px = (cx, cy, c) => { g.fillStyle = c; g.fillRect(Math.round(x + cx * scale), Math.round(y + cy * scale), scale, scale); };
  const hair = p.hair, skin = p.skin, coat = p.color, dark = '#05070b', pants = '#2a2f3a';
  // hair
  for (let i = 4; i < 12; i++) px(i, 0, hair);
  for (let i = 3; i < 13; i++) px(i, 1, hair);
  px(3, 2, hair); px(12, 2, hair);
  // face
  for (let r = 2; r < 7; r++) for (let i = 4; i < 12; i++) px(i, r, skin);
  if (facing >= 0) { px(6, 4, dark); px(9, 4, dark); } else { px(5, 4, dark); px(8, 4, dark); }
  // neck + coat
  px(7, 7, skin); px(8, 7, skin);
  for (let r = 8; r < 16; r++) for (let i = 3; i < 13; i++) px(i, r, coat);
  px(7, 9, '#f6f6f6'); px(8, 9, '#f6f6f6'); px(7, 10, '#f6f6f6'); px(8, 10, '#f6f6f6');
  // arms
  for (let r = 9; r < 15; r++) { px(2, r, coat); px(13, r, coat); } px(2, 15, skin); px(13, 15, skin);
  // legs with 2-frame walk
  const step = frame % 2;
  for (let r = 16; r < 22; r++) { px(5 + (step ? 1 : 0), r, pants); px(6 + (step ? 1 : 0), r, pants); px(9 - (step ? 1 : 0), r, pants); px(10 - (step ? 1 : 0), r, pants); }
  px(5, 22, dark); px(6, 22, dark); px(9, 22, dark); px(10, 22, dark);
}

function makeAgents() {
  agents = personas.agents.map((p, i) => {
    const b = BUILDINGS.find(b => b.key === p.building);
    return {
      p, home: { x: b.x + b.w / 2 - 8 * S, y: b.y + b.h + 6 },
      x: b.x + b.w / 2 - 8 * S, y: b.y + b.h + 6,
      tx: null, ty: null, speed: 0.5 + Math.random() * 0.3, facing: 1, frame: 0,
      wait: Math.random() * 2000, state: 'idle',
    };
  });
}

function pickTarget(a) {
  const r = Math.random();
  if (r < 0.4) { return { x: PLAZA.x + 10 + Math.random() * (PLAZA.w - 60), y: PLAZA.y + 10 + Math.random() * (PLAZA.h - 80) }; }
  if (r < 0.7) { return { x: 40 + Math.random() * (W - 120), y: 262 - 30 + Math.random() * 10 }; }
  return { ...a.home };
}

function update(dt) {
  for (const a of agents) {
    if (a === selected) continue;             // the one you're talking to stands still
    if (a.state === 'idle') { a.wait -= dt; if (a.wait <= 0) { const t = pickTarget(a); a.tx = t.x; a.ty = t.y; a.state = 'walk'; } continue; }
    const dx = a.tx - a.x, dy = a.ty - a.y, d = Math.hypot(dx, dy);
    if (d < 2) { a.state = 'idle'; a.wait = 1500 + Math.random() * 4000; continue; }
    const v = a.speed * dt / 16;
    a.x += dx / d * v; a.y += dy / d * v; a.facing = dx >= 0 ? 1 : -1;
    a.frame += dt / 180;
  }
  // overheard conversations: continuous. When one ends, the next pair meets somewhere else.
  const now = performance.now();
  bubbles = bubbles.filter(b => b.until > now);
  if (chatter && !convo && briefing && briefing.conversations.length && now >= nextConvoAt) {
    const pool = briefing.conversations;
    convoIdx = (convoIdx + 1) % pool.length;
    const c = pool[convoIdx];
    const A = agents.find(a => a.p.id === c.between[0]), B = agents.find(a => a.p.id === c.between[1]);
    if (A && B && A !== selected && B !== selected) {
      const spot = MEETING_SPOTS[Math.floor(Math.random() * MEETING_SPOTS.length)];
      A.tx = spot.x - 40; A.ty = spot.y; A.state = 'walk'; B.tx = spot.x + 20; B.ty = spot.y; B.state = 'walk';
      convo = { c, A, B, i: 0, next: now + 2500 };
    } else nextConvoAt = now + 1500;
  }
  if (convo) {
    if (now >= convo.next) {
      const line = convo.c.lines[convo.i];
      if (!line) { convo = null; nextConvoAt = now + 2500; maybeGenerateLive(); }
      else {
        const who = agents.find(a => a.p.id === line.who) || convo.A;
        who.facing = who === convo.A ? 1 : -1;
        bubbles = bubbles.filter(b => b.agent !== who);
        bubbles.push({ agent: who, text: line.line, until: now + 4600 });
        logLine(who.p, line.line);
        convo.i++; convo.next = now + 4800;
      }
    }
  } else if (Math.random() < 0.0015 && briefing) {
    // solitary mutterings from the daily briefing
    const a = agents[Math.floor(Math.random() * agents.length)];
    const b = briefing.agents[a.p.id];
    if (b && b.bubble && !bubbles.some(x => x.agent === a)) { bubbles.push({ agent: a, text: b.bubble, until: now + 3500 }); logLine(a.p, b.bubble); }
  }
}

function wrap(text, max) {
  const words = text.split(' '), lines = []; let cur = '';
  for (const w of words) { if ((cur + ' ' + w).trim().length > max) { lines.push(cur.trim()); cur = w; } else cur += ' ' + w; }
  if (cur.trim()) lines.push(cur.trim()); return lines;
}

function drawBubble(b) {
  const lines = wrap(b.text, 30);
  ctx.font = '11px "IBM Plex Mono"';
  const wdt = Math.min(300, Math.max(...lines.map(l => ctx.measureText(l).width)) + 24);
  const hgt = lines.length * 14 + 10;
  let x = b.agent.x + 8 * S - wdt / 2, y = b.agent.y - hgt - 12;
  x = Math.max(4, Math.min(W - wdt - 4, x)); if (y < 4) y = b.agent.y + 24 * S + 8;
  rect(x, y, wdt, hgt, '#f6f6f6'); rect(x + 2, y + 2, wdt - 4, hgt - 4, '#ffffff');
  rect(b.agent.x + 8 * S - 3, y + hgt, 6, 6, '#f6f6f6');
  ctx.fillStyle = '#0b0e14'; ctx.textAlign = 'left';
  lines.forEach((l, i) => ctx.fillText(l, x + 10, y + 15 + i * 14));
}

function render() {
  drawGround();
  // depth sort: buildings then agents by y
  for (const b of BUILDINGS) drawBuilding(b, selected && selected.p.building === b.key);
  const sorted = [...agents].sort((a, b) => a.y - b.y);
  for (const a of sorted) {
    if (a === selected) { ctx.fillStyle = 'rgba(75,232,154,.25)'; ctx.beginPath(); ctx.ellipse(a.x + 8 * S, a.y + 23 * S, 30, 10, 0, 0, Math.PI * 2); ctx.fill(); }
    drawFigure(ctx, a.x, a.y, a.state === 'walk' ? Math.floor(a.frame) : 0, a.facing, a.p);
    ctx.fillStyle = '#05070b'; ctx.fillRect(a.x - 8, a.y + 24 * S + 2, 16 * S + 16, 12);
    ctx.fillStyle = a.p.color; ctx.font = '7px "Press Start 2P"'; ctx.textAlign = 'center';
    ctx.fillText(a.p.name.split(' ')[0].toUpperCase(), a.x + 8 * S, a.y + 24 * S + 11);
  }
  for (const b of bubbles) drawBubble(b);
}

let last = performance.now();
function loop(now) { const dt = Math.min(50, now - last); last = now; update(dt); render(); requestAnimationFrame(loop); }

// ---------------------------------------------------------------- transcript + live chatter
const logEl = document.getElementById('log');
function logLine(p, text) {
  const d = document.createElement('div'); d.className = 'logline';
  const n = document.createElement('b'); n.style.color = p.color; n.textContent = p.name.split(' ')[0] + ' ';
  d.appendChild(n); d.appendChild(document.createTextNode(text)); logEl.appendChild(d);
  while (logEl.children.length > 300) logEl.removeChild(logEl.firstChild);
  logEl.scrollTop = logEl.scrollHeight;
}
let generating = false;
async function maybeGenerateLive() {
  if (!isLive() || generating || !personas) return;
  generating = true;
  try {
    const ids = personas.agents.map(a => a.id);
    const x = ids[Math.floor(Math.random() * ids.length)]; let y = ids[Math.floor(Math.random() * ids.length)]; if (y === x) y = ids[(ids.indexOf(x) + 1) % ids.length];
    const ax = personas.agents.find(a => a.id === x), ay = personas.agents.find(a => a.id === y);
    const recent = [...logEl.children].slice(-12).map(e => e.textContent).join('\n');
    const sys = `You write a short dialogue between two residents of a town about today's energy-cyber news. Resident A: ${ax.name}, ${ax.role}. ${ax.job} Voice: ${ax.voice}\nResident B: ${ay.name}, ${ay.role}. ${ay.job} Voice: ${ay.voice}\n${personas.shared_rules} They should disagree or sharpen each other and NOT repeat what was already said. Output ONLY a JSON array of 6 objects {"who": "${x}" or "${y}", "line": "..."}, each line under 30 words, alternating speakers starting with ${x}.`;
    const user = `TODAY'S NEWS BUNDLE:\n${newsContext()}\n\nRECENTLY SAID IN TOWN:\n${recent}`;
    const txt = await callRaw(sys, user, 900);
    const m = txt.match(/\[[\s\S]*\]/); const lines = m ? JSON.parse(m[0]) : [];
    if (lines.length) { briefing.conversations.push({ between: [x, y], lines, live: true }); if (briefing.conversations.length > 24) briefing.conversations.splice(0, 1); }
  } catch (e) { console.warn('live chatter failed', e.message); }
  finally { generating = false; }
}
document.getElementById('btn-chatter').onclick = ev => { chatter = !chatter; ev.target.textContent = chatter ? 'Chatter: on' : 'Chatter: off'; };

// ---------------------------------------------------------------- interaction
cv.addEventListener('mousemove', ev => {
  const r = cv.getBoundingClientRect(); const x = (ev.clientX - r.left) * (W / r.width), y = (ev.clientY - r.top) * (H / r.height);
  const over = agents.some(a => x >= a.x - 6 && x <= a.x + 16 * S + 6 && y >= a.y - 6 && y <= a.y + 24 * S + 14) || BUILDINGS.some(b => x >= b.x - 6 && x <= b.x + b.w + 6 && y >= b.y - 36 && y <= b.y + b.h);
  cv.style.cursor = over ? 'pointer' : 'default';
});
cv.addEventListener('click', ev => {
  const r = cv.getBoundingClientRect();
  const x = (ev.clientX - r.left) * (W / r.width), y = (ev.clientY - r.top) * (H / r.height);
  const hit = [...agents].reverse().find(a => x >= a.x - 6 && x <= a.x + 16 * S + 6 && y >= a.y - 6 && y <= a.y + 24 * S + 14);
  if (hit) { select(hit); return; }
  const bld = BUILDINGS.find(b => x >= b.x - 6 && x <= b.x + b.w + 6 && y >= b.y - 36 && y <= b.y + b.h);
  if (bld) selectBuilding(bld);
});

const $ = id => document.getElementById(id);
const panel = $('panel'), chat = $('chat');
function addMsg(text, cls) { const d = document.createElement('div'); d.className = 'msg ' + cls; d.textContent = text; chat.appendChild(d); chat.scrollTop = chat.scrollHeight; return d; }

function select(a) {
  selected = a; a.state = 'idle'; a.wait = 99999;
  if (convo && (convo.A === a || convo.B === a)) { convo = null; nextConvoAt = performance.now() + 2000; }
  panel.hidden = false;
  $('p-name').textContent = a.p.name; $('p-role').textContent = a.p.role + ' · ' + a.p.building;
  $('p-job').textContent = a.p.job + (a.p.name_note ? ' · Name: ' + a.p.name_note : '');
  const pc = $('portrait').getContext('2d'); pc.imageSmoothingEnabled = false; pc.fillStyle = '#1d2b1f'; pc.fillRect(0, 0, 64, 64);
  drawFigure(pc, 8, 4, 0, 1, a.p, 3);
  chat.innerHTML = '';
  const b = briefing && briefing.agents[a.p.id];
  addMsg(b ? b.briefing : 'No briefing yet today.', 'them');
  if (briefing && briefing.us_status && a.p.id === 'contrarian') addMsg('US status: ' + briefing.us_status, 'sys');
  if (briefing && briefing.verification && a.p.id === 'verifier') addMsg('Audit ' + (briefing.verification.run_at || '').slice(0, 16).replace('T', ' ') + ' UTC: ' + briefing.verification.summary, 'sys');
  if (briefing && briefing.model === 'fallback-headlines') addMsg('Headlines-only mode: the daily agent run has not happened yet, so this is the wire, not analysis. Add your key in Settings for a live answer.', 'sys');
  const sg = $('suggest'); sg.innerHTML = '';
  a.p.questions.forEach(q => { const btn = document.createElement('button'); btn.textContent = q; btn.onclick = () => ask(q); sg.appendChild(btn); });
  updateLiveNote();
}
function selectBuilding(b) {
  if (selected) { selected.wait = 500; selected = null; }
  panel.hidden = false;
  const info = buildings && buildings.buildings[b.key]; const res = info && personas.agents.find(a => a.id === info.resident);
  $('p-name').textContent = b.key; $('p-role').textContent = res ? `home of ${res.name}, ${res.role}` : 'building';
  $('p-job').textContent = info ? info.what : '';
  const pc = $('portrait').getContext('2d'); pc.imageSmoothingEnabled = false; pc.fillStyle = '#1d2b1f'; pc.fillRect(0, 0, 64, 64);
  pc.fillStyle = b.color; pc.fillRect(8, 22, 48, 36); pc.fillStyle = b.roof; pc.fillRect(4, 16, 56, 8); pc.fillStyle = '#f6e7a1'; [14, 28, 42].forEach(x => pc.fillRect(x, 30, 8, 8)); pc.fillStyle = '#1a1410'; pc.fillRect(28, 44, 8, 14);
  chat.innerHTML = '';
  if (info) addMsg('Data flow: ' + info.data, 'sys');
  if (res) { addMsg(`${res.name} works here. ${res.job}`, 'them'); if (res.name_note) addMsg('About the name: ' + res.name_note, 'sys'); }
  if (buildings && buildings.naming_note) addMsg('How all the names were chosen: ' + buildings.naming_note, 'sys');
  const sg = $('suggest'); sg.innerHTML = '';
  if (res) { const btn = document.createElement('button'); btn.textContent = `Talk to ${res.name.split(' ')[0]}`; btn.onclick = () => select(agents.find(a => a.p.id === res.id)); sg.appendChild(btn); }
  $('live-note').textContent = 'Click a resident to talk, or a building to read what happens inside it.';
}
$('p-close').onclick = () => { if (selected) { selected.wait = 500; } selected = null; panel.hidden = true; };

// ---------------------------------------------------------------- live chat
const cfg = { get: () => { try { return JSON.parse(localStorage.getItem('ecs-cfg') || '{}'); } catch { return {}; } },
              set: v => { try { localStorage.setItem('ecs-cfg', JSON.stringify(v)); } catch {} } };
function isLive() { const c = cfg.get(); return !!(c.key || c.proxy); }
function updateLiveNote() { $('live-note').textContent = isLive() ? 'Live: free-text questions go to the model with today\'s wire as context.' : 'Suggested questions are answered from today\'s briefing. Free-text needs a key or proxy in Settings.'; }

function newsContext() {
  if (!news) return '';
  const L = ['# ENERGY-SECTOR STORIES'];
  news.energy.slice(0, 25).forEach((s, i) => L.push(`E${i + 1}. [${s.source_name} | ${s.source_type} | ${s.source_country}] ${s.title} :: ${s.summary.slice(0, 300)} :: ${s.link}`));
  L.push('\n# OTHER CYBER STORIES SAME PERIOD');
  news.wide.slice(0, 30).forEach((s, i) => L.push(`W${i + 1}. [${s.source_name}] ${s.title} :: ${s.summary.slice(0, 200)}`));
  L.push('\n# SOURCE BIAS NOTES');
  news.sources.forEach(s => L.push(`- ${s.name} (${s.type}, ${s.country}): ${s.bias_note}`));
  return L.join('\n');
}
function systemFor(p) { return `You are ${p.name}, ${p.role} of the town. ${p.job} Voice: ${p.voice}\n${personas.shared_rules}`; }

async function callModel(p, question) {
  return callRaw(systemFor(p), `TODAY'S NEWS BUNDLE:\n${newsContext()}\n\nA visitor asks you: "${question}" Answer in your voice, 3 to 7 sentences, naming sources.`, 600);
}
async function callRaw(system, user, max_tokens) {
  const c = cfg.get(), model = c.model || 'claude-sonnet-5-5';
  if (c.proxy) {
    const r = await fetch(c.proxy, { method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ model, messages: [{ role: 'system', content: system }, { role: 'user', content: user }], max_tokens }) });
    if (!r.ok) throw new Error('proxy ' + r.status + ': ' + (await r.text()).slice(0, 200));
    const j = await r.json(); return j.choices[0].message.content;
  }
  const r = await fetch('https://api.anthropic.com/v1/messages', { method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': c.key, 'anthropic-version': '2023-06-01', 'anthropic-dangerous-direct-browser-access': 'true' },
    body: JSON.stringify({ model, max_tokens, system, messages: [{ role: 'user', content: user }] }) });
  if (!r.ok) throw new Error('anthropic ' + r.status + ': ' + (await r.text()).slice(0, 200));
  const j = await r.json(); return j.content.filter(b => b.type === 'text').map(b => b.text).join('');
}

async function ask(q) {
  if (!selected) return;
  const p = selected.p; addMsg(q, 'me');
  const canned = briefing && briefing.agents[p.id] && briefing.agents[p.id].answers[q];
  if (canned && !isLive()) { setTimeout(() => addMsg(canned, 'them'), 350); return; }
  if (!isLive()) { addMsg('I can only answer the suggested questions until you give the page a model. Open Settings and add an API key or a proxy URL.', 'sys'); return; }
  const wait = addMsg('…', 'them');
  try { wait.textContent = await callModel(p, q); }
  catch (e) { wait.className = 'msg sys'; wait.textContent = 'Could not reach the model: ' + e.message; if (canned) addMsg(canned, 'them'); }
}
$('ask').addEventListener('submit', ev => { ev.preventDefault(); const v = $('ask-input').value.trim(); if (!v) return; $('ask-input').value = ''; ask(v); });

// settings dialog
const dlgS = $('dlg-settings');
$('btn-settings').onclick = () => { const c = cfg.get(); $('s-key').value = c.key || ''; $('s-proxy').value = c.proxy || ''; $('s-model').value = c.model || ''; dlgS.showModal(); };
dlgS.addEventListener('close', () => {
  if (dlgS.returnValue === 'save') cfg.set({ key: $('s-key').value.trim(), proxy: $('s-proxy').value.trim(), model: $('s-model').value.trim() });
  if (dlgS.returnValue === 'clear') cfg.set({});
  updateLiveNote();
});

// wire dialog
$('btn-stories').onclick = () => {
  const w = $('wire'); w.innerHTML = '';
  (news ? news.energy : []).forEach(s => { const li = document.createElement('li'); const a = document.createElement('a'); a.href = s.link; a.target = '_blank'; a.rel = 'noopener'; a.textContent = s.title; li.appendChild(a); const sp = document.createElement('div'); sp.className = 'src'; sp.textContent = `${s.source_name} · ${s.source_type} · ${s.source_country}` + (s.published ? ' · ' + s.published.slice(0, 16).replace('T', ' ') : ''); li.appendChild(sp); w.appendChild(li); });
  if (!w.children.length) w.innerHTML = '<li>No energy-sector cyber story matched today.</li>';
  const so = $('sources'); so.innerHTML = '';
  (news ? news.sources : []).forEach(s => { const li = document.createElement('li'); li.innerHTML = `<b>${s.name}</b> (${s.type}, ${s.country}) — ${s.bias_note}`; so.appendChild(li); });
  $('wire-meta').textContent = news ? `${news.energy.length} energy-cyber stories, ${news.wide.length} other cyber stories, last ${news.window_hours}h, fetched ${news.generated_at.slice(0, 16).replace('T', ' ')} UTC` : '';
  $('dlg-stories').showModal();
};

// briefing board: the structured intelligence ledger
function esc(t) { return String(t == null ? '' : t).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
$('btn-board').onclick = () => {
  const items = (briefing && briefing.items) || [];
  $('us-status').textContent = (briefing && briefing.us_status) || '';
  const rb = $('rubric'); if (rb) rb.innerHTML = briefing && briefing.rubric ? `<b>How to read the board:</b> ${esc(briefing.rubric.rule)}<br><b>Importance</b> (severity badge): ${esc(briefing.rubric.importance)}<br><b>Correctness</b> (trust line + Verifier): ${esc(briefing.rubric.correctness)}` : '';
  $('board-meta').textContent = items.length ? `${items.length} items, ranked by severity · schema: what happened / why it matters to energy / how much to trust it` : 'No structured items yet (headlines-only mode).';
  const order = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
  const bd = $('board'); bd.innerHTML = '';
  [...items].sort((a, b) => (order[a.severity] ?? 9) - (order[b.severity] ?? 9)).forEach(it => {
    const otHit = /process|physical|reached/i.test(it.ot_impact || '');
    const d = document.createElement('div'); d.className = 'item';
    const rows = [['Energy', `${it.subsector || '?'} · ${it.value_chain || 'n/a'}`], ['IT vs OT', it.ot_impact], ['Actor', `${it.actor || 'none named'} · ${it.actor_type || ''} · ${it.attribution_confidence || ''}${it.attributed_by ? ' (by ' + it.attributed_by + ')' : ''}`],
      ['Technical', [(it.cves || []).join(', '), it.ics_vendor, it.initial_access, it.malware].filter(Boolean).join(' · ') || 'n/a'],
      ['Impact', [it.operational_impact, it.physical_safety_impact, it.data_exposed].filter(Boolean).join(' · ')], ['Context', [it.geopolitical_link, it.regulatory_trigger, it.government_response].filter(Boolean).join(' · ') || 'none'],
      ['Trust', `source ${it.source_type || '?'} · reliability ${it.source_reliability || '?'} · credibility ${it.info_credibility || '?'} · ${it.corroboration || 0} independent · ${it.claim_vs_confirmed || ''} · confidence ${it.confidence || '?'}`]];
    d.innerHTML = `<h4>${esc(it.headline)}</h4>
      <div class="badges"><span class="badge sev-${esc(it.severity)}">${esc(it.severity)}</span><span class="badge ${otHit ? 'ot-hit' : ''}">${esc(it.ot_impact)}</span><span class="badge">${esc(it.event_type)}</span><span class="badge">${esc(it.country)}</span><span class="badge">${esc(it.recommended_action)}</span><span class="badge">${esc(it.trend)}</span></div>
      <dl>${rows.map(([k, v]) => `<dt>${k}</dt><dd>${esc(v)}</dd>`).join('')}</dl>
      <div class="sowhat"><b>So what:</b> ${esc(it.so_what)}</div>
      ${(it.labels || []).length ? `<div class="lbl">${it.labels.map(esc).join(' · ')}</div>` : ''}
      ${(() => { const v = briefing.verification && briefing.verification.verdicts && briefing.verification.verdicts[it.headline]; return v ? `<div class="verdict"><b>Verifier:</b> ${esc(v.verdict)} — ${esc(v.reason)}</div>` : ''; })()}
      ${(() => { const c = briefing.verification && briefing.verification.crosschecks && briefing.verification.crosschecks[it.headline]; return c ? `<details class="xcheck"><summary>Cross-check: ${esc((c.compared || []).join(' vs '))} — ${esc(c.verdict)}</summary><div><b>Agree:</b> ${esc(c.agree)}</div><div><b>Differ:</b> ${esc(c.differ)}</div></details>` : ''; })()}
      ${(() => { const r = sources && sources.items && sources.items[it.headline]; if (!r) return ''; const blocks = [...(r.sources || []).map(x => ({ ...x, kind: 'outlet' })), ...(r.primary || []).filter(x => x.excerpts && x.excerpts.length).map(x => ({ ...x, kind: 'primary', name: x.url.replace(/^https?:\/\//, '').slice(0, 60) }))]; if (!blocks.length) return ''; return `<details class="direct"><summary>Direct source: ${blocks.length} page${blocks.length > 1 ? 's' : ''} pulled ${esc((sources.pulled_at || '').slice(0, 10))}</summary>${blocks.map(x => `<div class="pulled ${x.kind}"><a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.name)}</a> <span class="k">${x.kind}${x.status !== 200 ? ' · ' + esc(x.status) : ''}</span>${(x.excerpts || []).slice(0, 3).map(e => `<blockquote>${esc(e)}</blockquote>`).join('')}${x.error ? `<div class="k">${esc(x.error)}</div>` : ''}</div>`).join('')}</details>`; })()}
      <div class="src">${(it.sources || []).map(s => s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name)}</a> ${esc(s.date || '')}` : `${esc(s.name)} ${esc(s.date || '')}`).join(' · ')}</div>`;
    bd.appendChild(d);
  });
  $('dlg-board').showModal();
};

// methodology / where to look / limitations
$('btn-method').onclick = () => $('dlg-method').showModal();
$('btn-limits').onclick = () => $('dlg-limits').showModal();
$('btn-look').onclick = () => {
  const el = $('look'); el.innerHTML = '';
  if (lookmap) {
    $('look-meta').textContent = `the Librarian's map · reviewed ${lookmap.reviewed} · edit agents/where_to_look.json`;
    lookmap.sections.forEach(sec => {
      const d = document.createElement('div'); d.className = 'look-sec';
      d.innerHTML = `<h4>${esc(sec.question)}</h4><div class="tier">${esc(sec.tier)}</div><ul>${sec.entries.map(e => `<li>${e.url ? `<a href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.name)}</a>` : `<b>${esc(e.name)}</b>`} — ${esc(e.why)} <span class="acc">[${esc(e.access)}]</span></li>`).join('')}</ul>`;
      el.appendChild(d);
    });
  }
  const pf = $('perf'); pf.innerHTML = '';
  if (sources && sources.source_performance) {
    const rows = Object.entries(sources.source_performance).sort((a, b) => (b[1].energy_items || 0) - (a[1].energy_items || 0));
    pf.innerHTML = `<table class="perf-table"><tr><th>Source</th><th>Energy items</th><th>Wide</th><th>Feed</th><th>Pulls ok</th><th>Blocked</th></tr>${rows.map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v.energy_items || 0}</td><td>${v.wide_items || 0}</td><td class="${String(v.feed || '').startsWith('error') ? 'bad' : ''}">${esc(v.feed || 'n/a')}</td><td>${v.pulls_ok || 0}</td><td class="${v.pulls_blocked ? 'bad' : ''}">${v.pulls_blocked || 0}</td></tr>`).join('')}</table>
      <p>Primary hosts reached: ${esc((sources.primary_hosts_reached || []).join(', ') || 'none')} · pulled ${esc((sources.pulled_at || '').slice(0, 16).replace('T', ' '))} UTC</p>`;
  }
  $('dlg-look').showModal();
};

// ---------------------------------------------------------------- boot
async function boot() {
  const [p, b, n, src, lk, bl] = await Promise.all([
    fetch('data/personas.json').then(r => r.json()),
    fetch('data/briefing.json').then(r => r.json()).catch(() => null),
    fetch('data/news.json').then(r => r.json()).catch(() => null),
    fetch('data/sources.json').then(r => r.json()).catch(() => null),
    fetch('data/where_to_look.json').then(r => r.json()).catch(() => null),
    fetch('data/buildings.json').then(r => r.json()).catch(() => null),
  ]);
  personas = p; briefing = b; news = n; sources = src; lookmap = lk; buildings = bl;
  if (briefing) {
    const ageH = (Date.now() - Date.parse(briefing.news_generated_at || briefing.generated_at)) / 36e5;
    const age = ageH < 1 ? 'under an hour' : ageH < 48 ? `${Math.round(ageH)}h` : `${Math.round(ageH / 24)} days`;
    $('hud-meta').textContent = `snapshot ${age} old (fetched ${(briefing.news_generated_at || briefing.generated_at).slice(0, 16).replace('T', ' ')} UTC) · ${briefing.counts.energy} energy-cyber · ${briefing.counts.wide} wider cyber · ${briefing.model}`;
    if (ageH > 24) $('hud-meta').classList.add('stale');
  } else $('hud-meta').textContent = 'no briefing yet';
  makeAgents();
  window.ECS = { agents, select };       // small debug hook, also handy for tests
  await document.fonts.ready;
  requestAnimationFrame(loop);
}
boot();
})();
