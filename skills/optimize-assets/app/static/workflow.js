// Cross-feature UI state: persisted draft settings, provenance and inspection.
const draftNames = new Map();
let overviewData = null;
const storageKey = id => 'walo-settings-v1-' + id;
function storedSelection(a) { try {return JSON.parse(localStorage.getItem(storageKey(a.id)));} catch {return null;} }
function storeSelection(id) { try {localStorage.setItem(storageKey(id),JSON.stringify(selections.get(id)));} catch {} }
function captureDraftNames() { for(const [id,el] of rows) {const input=el.querySelector('.export-name');if(input) draftNames.set(id,input.value);} }
function pendingReasons(a) {
  const r=a.result,s=selection(a),reasons=[];
  const saved=a.export_name || a.file.split('/').pop().replace(/\.[^.]+$/,'');
  const draft=rows.get(a.id)?.querySelector('.export-name')?.value ?? draftNames.get(a.id) ?? saved;
  if(draft.trim()!==saved) reasons.push('nombre sin guardar');
  if(!r) return [...reasons,'sin optimizar'];
  if(s.preset!==r.preset) reasons.push('tamaño');
  if(a.type==='video') {
    if(a.info?.audio && Boolean(s.strip_audio)!==Boolean(r.options?.strip_audio)) reasons.push('audio');
    if((s.trim || null)!==(r.options?.trim || null)) reasons.push('recorte');
    if(!a.cover || a.cover.w!==r.w || a.cover.h!==r.h || (a.cover.at && r.at && a.cover.at<r.at)) reasons.push('cover pendiente');
  }
  if(s.preset==='retina' && (a.retina?.w!==r.options?._retina?.w || a.retina?.h!==r.options?._retina?.h)) reasons.push('medidas Retina actualizadas');
  return reasons;
}
function pendingHtml(a) {
  if(a.job && ['queued','running'].includes(a.job.status)) return '<span>Procesando los ajustes enviados…</span>';
  const reasons=pendingReasons(a);
  return reasons.length ? `<span class="dirty">Falta optimizar · ${esc(reasons.join(', '))}</span>` : '<span class="ready">Archivos actualizados</span>';
}
function updatePending(id) {const el=rows.get(id)?.querySelector('.pending-state');if(el)el.innerHTML=pendingHtml(assets.find(a=>a.id===id));}
function updateOverview(data) {overviewData=data;drawSummary();drawAudit();}
function drawSummary() {
  if(!overviewData) return;
  const slug=$('#fPage').value;
  const s=overviewData.pages?.find(p=>p.page===slug);
  if(!s)return;
  $('#pageSummary').innerHTML=`<div class="summary-panel"><div class="eyebrow">${esc(slug ? pageName(slug) : 'Todo el sitio · assets únicos')}</div><div class="summary-numbers"><div><strong>${fmt(s.original_bytes)}</strong><span>Originales</span></div><div><strong>${fmt(s.current_bytes)}</strong><span>Con optimizaciones actuales</span></div><div><strong>${s.saved_bytes===0?'':s.saved_bytes<0?'+':'−'}${fmt(Math.abs(s.saved_bytes))}</strong><span>${s.saved_bytes<0?'Incremento':'Ahorro real'}</span></div></div><progress max="${s.count||1}" value="${s.optimized}"></progress><div class="hint">${s.optimized}/${s.count} optimizados · Covers adicionales: ${fmt(s.cover_bytes)}.<br>Inventario de archivos, no carga inicial. Incluye los compartidos usados en esta página.</div></div>`;
}
function drawAudit() {
  const a=overviewData?.audit;if(!a)return;
  const running=a.status==='running';
  const state={idle:'Sin auditoría responsive',running:`Midiendo ${a.completed}/${a.total||60}`,done:'Auditoría completada',partial:'Auditoría parcial',error:'No se pudo completar',interrupted:'Auditoría interrumpida'}[a.status] || a.status;
  $('#auditPanel').innerHTML=`<div class="audit-panel"><div class="eyebrow">Retina · Responsive</div><b>${esc(state)}</b><div class="hint">390 · 768 · 1024 · 1440 · 1920 · 2560 px<br>${a.measured_assets||0}/${assets.length} assets medidos${a.at?' · '+new Date(a.at*1000).toLocaleString():''}</div><button onclick="runAudit()" ${running?'disabled':''}>${running?'Midiendo…':'Medir la web'}</button><div class="hint">Máximo observado en estos anchos. Las medidas nuevas pueden dejar exportaciones Retina pendientes.</div>${a.error?`<details><summary>Ver error</summary>${esc(a.error)}</details>`:''}${a.failures?.length?`<details><summary>${a.failures.length} mediciones incompletas</summary>${a.failures.map(f=>`${esc(f.page)} · ${f.width}px: ${esc(f.error)}`).join('<br>')}</details>`:''}</div>`;
}
async function runAudit() {
  const d=dialog('Medir la web'),content=d.querySelector('.dialog-content');
  content.innerHTML='<p>Se medirán las 10 páginas entre 390 y 2560 px para calcular Retina.</p><label>Contraseña del sitio (si está protegido)<input class="audit-password" type="password" autocomplete="off" style="display:block;margin:12px 0;padding:10px;background:var(--bg);border:1px solid var(--line);border-radius:6px;color:var(--fg)"></label><p class="hint">Se usa solo durante esta auditoría. No se guarda en archivos ni historial.</p><button class="begin-audit">Iniciar medición</button><p class="audit-error" role="status"></p>';
  content.querySelector('.begin-audit').onclick=async()=>{
    const button=content.querySelector('.begin-audit');button.disabled=true;
    try{const input=content.querySelector('input');const password=input.value;input.value='';const r=await api('/api/audit',{password});if(r.error && r.status!=='error')throw Error(r.error);overviewData.audit=r;drawAudit();startPolling();d.close();}catch(e){content.querySelector('.audit-error').textContent=e.message;button.disabled=false;}
  };
}

function dialog(title) {
  document.querySelector('#workDialog')?.close();document.querySelector('#workDialog')?.remove();
  const d=document.createElement('dialog');d.id='workDialog';d.className='work-dialog';
  d.innerHTML=`<div class="dialog-bar"><div class="dialog-title">${esc(title)}</div><button class="close-dialog">Cerrar ✕</button></div><div class="dialog-content"></div>`;
  document.body.append(d);d.querySelector('.close-dialog').onclick=()=>d.close();d.addEventListener('click',e=>{if(e.target===d)d.close();});
  d.addEventListener('close',()=>{d.querySelectorAll('video').forEach(v=>v.pause());});d.showModal();return d;
}
function openLb(id) {openCompare(id);}
function openCompare(id) {
  const a=assets.find(a=>a.id===id);if(!a)return;
  const d=dialog('Comparar · '+a.export_name);
  const output=a.result;
  const p=d.querySelector('.dialog-content');
  const files=[{label:'Original',file:a.file,url:'/files/'+encodeURI(a.file),w:a.info?.w,h:a.info?.h,bytes:a.bytes}];
  if(output)files.push({label:'Optimizado',file:output.file,url:'/result/'+id+'?v='+output.at,w:output.w,h:output.h,bytes:output.bytes});
  p.innerHTML=`<div class="compare-controls"><button data-zoom="fit" aria-pressed="true">Ajustar</button><button data-zoom="pixel" aria-pressed="false">100%</button><span class="hint">100% = 1 píxel del archivo por píxel CSS. Las resoluciones pueden diferir.</span></div><div class="compare-panes">${files.map(f=>`<figure><figcaption>${f.label} · ${fmt(f.bytes)} · ${f.w||'?'}×${f.h||'?'}</figcaption><div class="compare-scroll">${media(f.file,f.url)}</div></figure>`).join('')}</div>${!output?'<p class="hint">Optimiza este archivo para comparar ambas versiones.</p>':''}<div class="playback compare-controls"></div>`;
  const panes=p.querySelector('.compare-panes');
  p.querySelectorAll('[data-zoom]').forEach(b=>b.onclick=()=>{panes.classList.toggle('pixel',b.dataset.zoom==='pixel');p.querySelectorAll('[data-zoom]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));});
  const scrolls=[...p.querySelectorAll('.compare-scroll')];let syncing=false;
  scrolls.forEach(el=>el.addEventListener('scroll',()=>{if(syncing)return;syncing=true;scrolls.filter(x=>x!==el).forEach(x=>{x.scrollLeft=el.scrollLeft/Math.max(1,el.scrollWidth-el.clientWidth)*Math.max(0,x.scrollWidth-x.clientWidth);x.scrollTop=el.scrollTop/Math.max(1,el.scrollHeight-el.clientHeight)*Math.max(0,x.scrollHeight-x.clientHeight);});requestAnimationFrame(()=>syncing=false);}));
  const videos=[...p.querySelectorAll('video')];
  videos.forEach(v=>{v.autoplay=false;v.pause();v.controls=false;v.loop=false;});
  if(videos.length) {
    const controls=p.querySelector('.playback');controls.innerHTML='<button class="play-pair">Reproducir ambos</button><input class="seek-pair" type="range" min="0" max="1" step="0.01" value="0" aria-label="Posición de ambos videos"><span class="hint">Sincronizados al mismo segundo; se usa la duración común.</span>';
    const slider=controls.querySelector('input'),button=controls.querySelector('button');
    const duration=()=>Math.min(...videos.map(v=>Number.isFinite(v.duration)?v.duration:Infinity));
    videos.forEach(v=>v.addEventListener('loadedmetadata',()=>{if(Number.isFinite(duration()))slider.max=duration();}));
    button.onclick=async()=>{if(videos.some(v=>!v.paused)){videos.forEach(v=>v.pause());button.textContent='Reproducir ambos';}else{videos.forEach(v=>{v.currentTime=Number(slider.value);});await Promise.all(videos.map(v=>v.play().catch(()=>{})));button.textContent='Pausar';}};
    slider.oninput=()=>videos.forEach(v=>{v.currentTime=Number(slider.value);});
    videos[0].addEventListener('timeupdate',()=>{slider.value=videos[0].currentTime;for(const v of videos.slice(1))if(Math.abs(v.currentTime-videos[0].currentTime)>.2)v.currentTime=videos[0].currentTime;if(videos[0].currentTime>=duration()-.05){videos.forEach(v=>v.pause());button.textContent='Reproducir ambos';}});
  }
}
async function openHistory(id) {
  const a=assets.find(a=>a.id===id),d=dialog('Historial · '+a.export_name),content=d.querySelector('.dialog-content');content.textContent='Cargando versiones…';
  try {
    const data=await api('/api/history/'+id);if(data.error)throw Error(data.error);
    const total=data.versions.reduce((sum,v)=>sum+(v.result?.bytes||0)+(v.cover?.bytes||0),0);
    content.innerHTML=`<p class="hint">Original: ${esc(a.file)}<br>Copias recuperables: ${fmt(total)}. Se conservan los archivos y ajustes de cada versión.</p>${data.versions.map(v=>`<div class="history-row"><div><b>${esc(v.export_name)}</b><div class="hint">${new Date(v.at*1000).toLocaleString()} · ${esc(v.result?.preset||'original')} · ${v.result?.w||'?'}×${v.result?.h||'?'} · ${fmt(v.result?.bytes||0)}${v.cover?' + cover '+fmt(v.cover.bytes):''}<br>${v.result?.options?.strip_audio?'Sin audio':'Audio original'}${v.result?.options?.trim?' · Recorte '+v.result.options.trim+' s':''} · ${esc({imported:'Versión previa importada',optimized:'Optimizada',before_change:'Antes de optimizar',before_rename:'Antes de renombrar',before_restore:'Antes de restaurar'}[v.reason]||v.reason)}</div></div><button data-restore="${v.id}">Restaurar</button></div>`).join('') || '<p>Todavía no hay exportaciones.</p>'}`;
    content.querySelectorAll('[data-restore]').forEach(b=>b.onclick=async()=>{
      b.disabled=true;b.textContent='Restaurando…';
      try{const r=await api('/api/restore',{id,version:b.dataset.restore});if(r.error)throw Error(r.error);selections.delete(id);draftNames.delete(id);try{localStorage.removeItem(storageKey(id));}catch{}rows.delete(id);await load();d.close();}catch(e){b.disabled=false;b.textContent='Restaurar';alert(e.message);}
    });
  } catch(e){content.textContent=e.message;}
}
