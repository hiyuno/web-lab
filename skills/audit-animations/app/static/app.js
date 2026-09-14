const COLORS = {critical:'var(--critical)',high:'var(--high)',medium:'var(--medium)',
  low:'var(--low)',info:'var(--info)'};
const CAT_LABEL = {composited:'Composited', runtime:'Runtime', 'safari-risk':'Safari-risk'};
const CATS = ['composited', 'runtime', 'safari-risk'];
const SEVERITY_ORDER = ['critical','high','medium','low','info'];
const SEVERITY_WEIGHT = {critical:100, high:40, medium:15, low:5, info:1};
const CONFIDENCE_WEIGHT = {measured:1, documented:0.7, heuristic:0.5};

let data = null;

async function load() {
  const r = await fetch('/api/findings');
  data = await r.json();
  document.getElementById('site').textContent = data.site;

  // Populate page filter with unique pages, sorted: home first, then alphabetical,
  // with .mobile variants immediately after their desktop version.
  const uniquePages = [...new Set(data.findings.map(f => f.page))];
  const pageOrder = buildPageOrder(uniquePages);
  const pageSelect = document.getElementById('page');
  for (const page of pageOrder) {
    const opt = document.createElement('option');
    opt.value = page;
    opt.textContent = page;
    pageSelect.appendChild(opt);
  }

  render();
}

// Build page order: home first, then alphabetical by base name (without .mobile),
// with .mobile variants immediately after their desktop counterpart.
function buildPageOrder(pages) {
  const bases = new Map(); // base name -> [desktop, mobile]
  for (const page of pages) {
    const isMobile = page.endsWith('.mobile');
    const baseName = isMobile ? page.slice(0, -7) : page;
    if (!bases.has(baseName)) bases.set(baseName, [null, null]);
    if (isMobile) bases.get(baseName)[1] = page;
    else bases.get(baseName)[0] = page;
  }

  // Sort base names: 'home' first, then alphabetical
  const sorted = [...bases.keys()].sort((a, b) => {
    if (a === 'home') return -1;
    if (b === 'home') return 1;
    return a.localeCompare(b);
  });

  const ordered = [];
  for (const baseName of sorted) {
    const [desktop, mobile] = bases.get(baseName);
    if (desktop) ordered.push(desktop);
    if (mobile) ordered.push(mobile);
  }
  return ordered;
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

// Group findings by (page, where): every finding sharing that pair describes the same real
// animated element, whatever category or property it was flagged under.
function groupFindings() {
  const groups = new Map();
  for (const f of data.findings) {
    const key = f.page + ' ' + f.where;
    if (!groups.has(key)) {
      groups.set(key, {page: f.page, where: f.where, findings: []});
    }
    groups.get(key).findings.push(f);
  }
  return [...groups.values()];
}

function order(sev) { return SEVERITY_ORDER.indexOf(sev); }

function score(findings) {
  let s = 0;
  for (const f of findings) {
    if (f.status === 'resolved') continue;
    s += (SEVERITY_WEIGHT[f.severity] || 0) * (CONFIDENCE_WEIGHT[f.confidence] || 0.5);
  }
  return s;
}

// The worst severity among a group's unresolved findings, or null if every finding is resolved.
function worstSeverity(findings) {
  const open = findings.filter(f => f.status !== 'resolved');
  if (!open.length) return null;
  return open.reduce((worst, f) => order(f.severity) < order(worst) ? f.severity : worst,
    open[0].severity);
}

function render() {
  counts();
  const cats = [...document.querySelectorAll('#filters input[type=checkbox][value]')]
    .filter(c => c.checked).map(c => c.value);
  const severity = document.getElementById('severity').value;
  const hideResolved = document.getElementById('hide-resolved').checked;
  const pageFilter = document.getElementById('page').value;
  const sortMode = document.getElementById('sort').value;

  const matches = f => {
    if (!cats.includes(f.category)) return false;
    if (severity && f.severity !== severity) return false;
    if (hideResolved && f.status === 'resolved') return false;
    if (pageFilter && f.page !== pageFilter) return false;
    return true;
  };

  let groups = groupFindings();
  // A group is shown if at least one of its findings matches the active filters.
  groups = groups.filter(g => g.findings.some(matches));
  for (const g of groups) {
    g.score = score(g.findings);
    g.worst = worstSeverity(g.findings);
    g.shown = g.findings.filter(matches).sort((a, b) => order(a.severity) - order(b.severity));
  }

  const list = document.getElementById('list');
  list.innerHTML = '';
  list.appendChild(topOffenders(groups));

  const byPage = new Map();
  for (const g of groups) {
    if (!byPage.has(g.page)) byPage.set(g.page, []);
    byPage.get(g.page).push(g);
  }

  // Order pages according to sort mode
  let orderedPages = [...byPage.entries()];
  if (sortMode === 'page') {
    // Use page selector order (populated in load())
    const pageOptions = [...document.getElementById('page').options].map(o => o.value).slice(1); // skip "Todas"
    orderedPages.sort((a, b) => pageOptions.indexOf(a[0]) - pageOptions.indexOf(b[0]));
  } else {
    // sortMode === 'severity': sort by highest score descending
    orderedPages.sort((a, b) => {
      const maxA = Math.max(...a[1].map(g => g.score), 0);
      const maxB = Math.max(...b[1].map(g => g.score), 0);
      return maxB - maxA;
    });
  }

  for (const [page, pageGroups] of orderedPages) {
    pageGroups.sort((a, b) => b.score - a.score);
    const worstOfPage = pageGroups.reduce((w, g) =>
      (g.worst && (!w || order(g.worst) < order(w))) ? g.worst : w, null);
    const section = document.createElement('div');
    section.className = 'group';
    section.innerHTML = `<h2>${escapeHtml(page)} <small>${pageGroups.length} animation` +
      `${pageGroups.length === 1 ? '' : 's'}${worstOfPage ? ' · worst: ' + worstOfPage : ''}` +
      `</small></h2>`;
    for (const g of pageGroups) section.appendChild(renderCard(g));
    list.appendChild(section);
  }
}

function groupDomId(g) {
  // Stable, DOM-safe id derived from the group key so the top-offenders strip can scroll to it.
  return 'card-' + btoa(unescape(encodeURIComponent(g.page + ' ' + g.where)))
    .replace(/[^a-zA-Z0-9]/g, '');
}

function topOffenders(groups) {
  const wrap = document.createElement('div');
  wrap.id = 'top-offenders';
  if (groups.length < 3) return wrap; // not worth it on a tiny site

  const top = [...groups].sort((a, b) => b.score - a.score).slice(0, 5).filter(g => g.score > 0);
  if (!top.length) return wrap;

  wrap.innerHTML = `<h2>Top offenders</h2><div class="chips"></div>`;
  const chipsEl = wrap.querySelector('.chips');
  for (const g of top) {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'offender-chip';
    const dot = document.createElement('span');
    dot.className = 'dot';
    dot.style.background = g.worst ? COLORS[g.worst] : 'var(--muted)';
    chip.appendChild(dot);
    const label = document.createElement('span');
    label.className = 'offender-label';
    label.textContent = `${g.page} · ${g.where}`;
    label.title = `${g.page} · ${g.where}`;
    chip.appendChild(label);
    const sc = document.createElement('span');
    sc.className = 'offender-score';
    sc.textContent = Math.round(g.score);
    chip.appendChild(sc);
    chip.onclick = () => scrollToCard(groupDomId(g));
    chipsEl.appendChild(chip);
  }
  return wrap;
}

function scrollToCard(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.scrollIntoView({
    behavior: prefersReducedMotion() ? 'auto' : 'smooth',
    block: 'center',
  });
  if (prefersReducedMotion()) return;
  el.classList.remove('pulse');
  // restart the animation even if it was just triggered
  void el.offsetWidth;
  el.classList.add('pulse');
  setTimeout(() => el.classList.remove('pulse'), 1600);
}

function prefersReducedMotion() {
  return matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function renderCard(g) {
  const div = document.createElement('div');
  div.className = 'item card';
  div.id = groupDomId(g);
  if (!g.worst) div.classList.add('resolved');

  const dot = document.createElement('span');
  dot.className = 'severity-dot';
  dot.style.background = g.worst ? COLORS[g.worst] : 'var(--muted)';
  dot.title = g.worst ? `Worst open severity: ${g.worst}` : 'All findings resolved';
  div.appendChild(dot);

  const body = document.createElement('div');
  body.className = 'body';

  const title = document.createElement('div');
  title.className = 'where card-title';
  title.textContent = g.where;
  title.title = g.where;
  body.appendChild(title);

  const meta = document.createElement('div');
  meta.className = 'card-meta';
  const scoreEl = document.createElement('span');
  scoreEl.className = 'score';
  scoreEl.title = 'Higher = more/worse issues on this animation. Not a real performance unit.';
  scoreEl.textContent = `Cost score: ${Math.round(g.score)}`;
  meta.appendChild(scoreEl);
  const cats = [...new Set(g.findings.map(f => f.category))];
  for (const cat of cats) {
    const chip = document.createElement('span');
    chip.className = 'cat-chip';
    chip.textContent = CAT_LABEL[cat];
    meta.appendChild(chip);
  }
  body.appendChild(meta);

  const ul = document.createElement('ul');
  ul.className = 'issues';
  for (const f of g.shown) ul.appendChild(renderIssue(f));
  body.appendChild(ul);

  const unresolvedShown = g.shown.filter(f => f.status !== 'resolved');
  if (unresolvedShown.length) {
    const needsRuntime = unresolvedShown.some(f => f.category === 'runtime');
    const needsPhase3 = unresolvedShown.some(f => f.category !== 'runtime');
    const parts = [];
    if (needsPhase3) parts.push('phase 3 (composited/safari-risk)');
    if (needsRuntime) parts.push('phase 4 (runtime)');
    const hint = document.createElement('div');
    hint.className = 'hint';
    hint.textContent = `Re-run ${parts.join(' and ')} for this page to verify a fix`;
    body.appendChild(hint);
  }

  div.appendChild(body);
  return div;
}

function renderIssue(f) {
  const li = document.createElement('li');
  li.className = f.status === 'resolved' ? 'resolved' : '';

  const check = document.createElement('input');
  check.type = 'checkbox';
  check.checked = f.status === 'resolved';
  check.onchange = () => setStatus(f.id, check.checked ? 'resolved' : 'open');
  li.appendChild(check);

  const badge = document.createElement('span');
  badge.className = 'badge';
  badge.style.background = COLORS[f.severity];
  badge.textContent = f.severity;
  li.appendChild(badge);

  const conf = document.createElement('span');
  conf.className = `confidence ${f.confidence}`;
  conf.textContent = f.confidence;
  li.appendChild(conf);

  if (f.status === 'not_verified') {
    const nv = document.createElement('span');
    nv.className = 'badge';
    nv.style.background = '#555';
    nv.textContent = 'not verified';
    li.appendChild(nv);
  }

  const text = document.createElement('span');
  text.className = 'issue-text';
  text.textContent = f.before;
  li.appendChild(text);

  return li;
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
