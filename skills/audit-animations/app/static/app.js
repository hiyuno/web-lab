const COLORS = {critical:'var(--critical)',high:'var(--high)',medium:'var(--medium)',
  low:'var(--low)',info:'var(--info)'};
const CAT_LABEL = {composited:'Composited', runtime:'Runtime', 'safari-risk':'Safari-risk'};
const CATS = ['composited', 'runtime', 'safari-risk'];

let data = null;

async function load() {
  const r = await fetch('/api/findings');
  data = await r.json();
  document.getElementById('site').textContent = data.site;
  render();
}

function counts() {
  const c = {};
  for (const f of data.findings) {
    if (f.status === 'resolved') continue;
    c[f.severity] = (c[f.severity] || 0) + 1;
  }
  const el = document.getElementById('counts');
  el.innerHTML = '';
  for (const [sev, n] of Object.entries(c)) {
    const span = document.createElement('span');
    span.className = 'count';
    span.style.background = COLORS[sev];
    span.style.color = '#fff';
    span.textContent = `${n} ${sev}`;
    el.appendChild(span);
  }
}

function render() {
  counts();
  const cats = [...document.querySelectorAll('#filters input[type=checkbox][value]')]
    .filter(c => c.checked).map(c => c.value);
  const severity = document.getElementById('severity').value;
  const hideResolved = document.getElementById('hide-resolved').checked;

  const list = document.getElementById('list');
  list.innerHTML = '';
  for (const cat of CATS) {
    if (!cats.includes(cat)) continue;
    let items = data.findings.filter(f => f.category === cat);
    if (severity) items = items.filter(f => f.severity === severity);
    if (hideResolved) items = items.filter(f => f.status !== 'resolved');
    items.sort((a, b) => order(a.severity) - order(b.severity));
    if (!items.length) continue;

    const group = document.createElement('div');
    group.className = 'group';
    group.innerHTML = `<h2>${CAT_LABEL[cat]} (${items.length})</h2>`;
    for (const f of items) group.appendChild(renderItem(f));
    list.appendChild(group);
  }
}

function order(sev) { return ['critical','high','medium','low','info'].indexOf(sev); }

function renderItem(f) {
  const div = document.createElement('div');
  div.className = 'item' + (f.status === 'resolved' ? ' resolved' : '');

  const check = document.createElement('input');
  check.type = 'checkbox';
  check.checked = f.status === 'resolved';
  check.onchange = () => setStatus(f.id, check.checked ? 'resolved' : 'open');
  div.appendChild(check);

  const body = document.createElement('div');
  body.className = 'body';
  const notVerified = f.status === 'not_verified';
  body.innerHTML = `
    <span class="badge" style="background:${COLORS[f.severity]}">${f.severity}</span>
    <span class="confidence ${f.confidence}">${f.confidence}</span>
    ${notVerified ? '<span class="badge" style="background:#555">not verified</span>' : ''}
    <div class="where">${f.page} · ${escapeHtml(f.where)}</div>
    <div class="before"><strong>Antes:</strong> ${escapeHtml(f.before)}</div>
    <div class="after"><strong>Después:</strong> ${escapeHtml(f.after)}</div>
    ${f.why ? `<div class="why">${escapeHtml(f.why)}</div>` : ''}
  `;
  const actions = document.createElement('div');
  actions.className = 'actions';
  const hint = document.createElement('span');
  hint.className = 'hint';
  hint.textContent = f.category === 'runtime'
    ? 'Re-run phase 4 (runtime) for this page to verify a fix'
    : 'Re-run phase 3 (composited/safari-risk) for this page to verify a fix';
  actions.appendChild(hint);
  body.appendChild(actions);
  div.appendChild(body);
  return div;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',
    "'":'&#39;'}[c]));
}

async function setStatus(id, status) {
  await fetch('/api/status', {method:'POST', body: JSON.stringify({id, status})});
  const f = data.findings.find(f => f.id === id);
  if (f) f.status = status;
  render();
}

document.querySelectorAll('#filters input, #filters select').forEach(el =>
  el.addEventListener('change', render));

load();
