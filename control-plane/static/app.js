'use strict';
const $ = (id) => document.getElementById(id);
let researchData = null, fixtures = null;
let token = '', state = {instances: [], audit: []}, selected = null, filter = 'all', refreshing = false, toastTimer;
const adapterNames = {simulator: 'Synthetic sandbox', minnit: 'Minnit · not connected', deadsimplechat: 'DeadSimpleChat · not connected'};
function toast(message) { $('toast').textContent = message; $('toast').classList.remove('hidden'); clearTimeout(toastTimer); toastTimer = setTimeout(() => $('toast').classList.add('hidden'), 4500); }
async function api(path, method = 'GET', data) {
  const response = await fetch(path, {method, headers: {'Content-Type': 'application/json', ...(token ? {Authorization: `Bearer ${token}`} : {})}, ...(method !== 'GET' ? {body: JSON.stringify(data || {})} : {})});
  const result = await response.json();
  if (!response.ok) { if (response.status === 401 && !$('auth-dialog').open) $('auth-dialog').showModal(); throw new Error(result.error || `Request failed (${response.status})`); }
  return result;
}
function el(tag, cls, text) {const node = document.createElement(tag); if(cls) node.className = cls; if(text !== undefined) node.textContent = text; return node;}
function button(text, cls, callback, disabled = false) {const b = el('button', cls, text); b.disabled = disabled; b.addEventListener('click', async (event) => { event.stopPropagation(); b.disabled = true; try {await callback(); await refresh();} catch(error) {toast(error.message);} finally {if(b.isConnected) b.disabled = disabled;}}); return b;}
function render() {
  const summary = state.summary;
  $('configured').textContent = summary.configured; $('nav-count').textContent = summary.configured; $('all-count').textContent = summary.configured;
  $('running').textContent = summary.running; $('checks').textContent = summary.checks_passed;
  $('duplicate-count').textContent = `${summary.duplicates} duplicates filtered`;
  const search = $('search').value.toLowerCase();
  const visible = state.instances.filter(i => (filter === 'all' || i.status === filter) && i.name.toLowerCase().includes(search));
  const grid = $('instances'); grid.replaceChildren();
  for(const item of visible) {
    const card = el('article', `instance-card${selected === item.id ? ' selected' : ''}`);
    const top = el('div','card-top'); top.append(el('span','adapter-icon', item.adapter === 'simulator' ? '◇' : '↗'), el('span',`badge ${item.status}`, item.status));
    card.append(top, el('h3','',item.name), el('div','card-subtitle',adapterNames[item.adapter]));
    const stats = el('div','card-stats');
    for(const [label,value] of [['Mode',item.ready ? 'Synthetic only' : 'Not connected'],['Checks',String(item.checks_passed)],['Run',item.run_id ? item.run_id.slice(0,6) : '—']]) {const valueNode=el('span','',label); valueNode.append(el('b','',value)); stats.append(valueNode);}
    card.append(stats);
    const controls = el('div','card-controls');
    controls.append(button(item.status === 'running' ? '■ Stop' : '▶ Start',item.status === 'running' ? '' : 'start',async()=>{await api(`/api/instances/${item.id}/${item.status === 'running' ? 'stop' : 'start'}`,'POST');},!item.ready));
    controls.append(button('Run check','', async()=>{await api(`/api/instances/${item.id}/check`,'POST',{event_id: crypto.randomUUID(),run_id:item.run_id}); selected=item.id; toast('Synthetic check passed. No message sent.');}, item.status !== 'running'));
    controls.append(button('×','delete',async()=>{if(confirm(`Delete “${item.name}”?`)) {await api(`/api/instances/${item.id}`,'DELETE'); if(selected===item.id) selected=null;}},item.status==='running'));
    controls.lastChild.setAttribute('aria-label',`Delete ${item.name}`);
    card.append(controls); card.addEventListener('click',()=>{selected=item.id; render(); refreshLogs().catch(e=>toast(e.message));}); grid.append(card);
  }
  $('empty').classList.toggle('hidden', visible.length !== 0);
  if(state.instances.length && !visible.length) { $('empty').querySelector('h2').textContent='No matching instances'; $('empty').querySelector('p').textContent='Try another search or status filter.'; $('empty-add').classList.add('hidden'); }
  else { $('empty').querySelector('h2').textContent='Your workspace starts here'; $('empty').querySelector('p').textContent='Add a synthetic instance to test lifecycle controls, event deduplication, and isolated activity logs.'; $('empty-add').classList.remove('hidden'); }
  const audit=$('audit'); audit.replaceChildren();
  for(const event of [...state.audit].reverse()) {const row=el('div','audit-row'); const name=state.instances.find(i=>i.id===event.instance_id)?.name || 'Deleted instance'; row.append(el('time','',new Date(event.at*1000).toLocaleTimeString()),el('strong','',name),el('span','',event.message)); audit.append(row);}
  if(!state.audit.length) audit.append(el('p','log-empty','No activity yet. Create an instance to begin.'));
}
async function refreshLogs() {
  const instance = state.instances.find(i=>i.id===selected); const box=$('logs');
  if(!instance) {selected=null; $('log-title').textContent='Instance activity'; $('log-subtitle').textContent='Select an instance to inspect its lifecycle.'; box.replaceChildren(el('p','log-empty','No instance selected.')); return;}
  const requestedId=selected;
  const result=await api(`/api/instances/${requestedId}/logs`);
  if(selected!==requestedId) return;
  $('log-title').textContent=instance.name; $('log-subtitle').textContent='Recent 100 events · runtime only'; box.replaceChildren();
  for(const event of [...result.logs].reverse()) {const row=el('div','log-row'); row.append(el('time','',new Date(event.at*1000).toLocaleTimeString()),el('span','action',event.action),el('span','message',event.message)); box.append(row);}
}
async function refresh() {if(refreshing) return; refreshing=true; try {state=await api('/api/state'); render(); await refreshLogs(); try { researchData=await api('/api/research'); renderResearch(); } catch(error) { $('research-cards').replaceChildren(el('p','error',error.message)); } $('connection-status').textContent='CONNECTED · LOCAL STATE';} catch(error) {$('connection-status').textContent='CONNECTION ERROR'; throw error;} finally {refreshing=false;}}
function openCreate() {$('form-error').textContent=''; $('create-dialog').showModal(); $('instance-name').focus();}
$('add').onclick=openCreate; $('empty-add').onclick=openCreate;
$('close-dialog').onclick=()=>$('create-dialog').close(); $('cancel-dialog').onclick=()=>$('create-dialog').close();
$('create-form').onsubmit=async(event)=>{event.preventDefault(); const submit=event.submitter; submit.disabled=true; try {const item=await api('/api/instances','POST',{name:$('instance-name').value,adapter:$('adapter').value}); selected=item.id; $('create-dialog').close(); $('create-form').reset(); await refresh(); toast('Instance configuration saved.');} catch(error){$('form-error').textContent=error.message;} finally{submit.disabled=false;}};
$('auth-form').onsubmit=async(event)=>{event.preventDefault(); token=$('operator-token').value; try{await api('/api/state'); $('auth-dialog').close(); $('operator-token').value=''; $('auth-error').textContent=''; await refresh();}catch(error){token=''; $('auth-error').textContent=error.message;}};
$('auth-dialog').addEventListener('cancel',event=>event.preventDefault());
$('search').oninput=render;
$('stop-all').onclick=async()=>{try {await api('/api/stop-all','POST'); await refresh(); toast('All synthetic workers stopped.');}catch(error){toast(error.message);}};
for(const tab of document.querySelectorAll('[data-filter]')) tab.onclick=()=>{filter=tab.dataset.filter; for(const b of document.querySelectorAll('[data-filter]')) b.classList.toggle('active',b===tab);render();};
for(const nav of document.querySelectorAll('[data-view]')) nav.onclick=async()=>{
  const view=nav.dataset.view;
  for(const b of document.querySelectorAll('[data-view]')) b.classList.toggle('active',b===nav);
  for(const id of ['fleet','activity','research']) $(`${id}-view`).classList.toggle('hidden',id!==view);
  const titles={fleet:'Instance fleet',activity:'Workspace activity',research:'Site research'};
  const descriptions={fleet:'Configure your instances. Control every lifecycle.',activity:'A clear timeline of local lifecycle events.',research:'Source-backed analysis, local contract tests, and explicit delivery gates.'};
  $('page-title').textContent=titles[view]; $('breadcrumb').textContent=titles[view]; $('page-description').textContent=descriptions[view];
  if(view==='research'&&!fixtures) {try{fixtures=(await api('/api/contracts')).fixtures;loadFixture();}catch(error){toast(error.message);}}
};
function renderResearch() {
  const box=$('research-cards');box.replaceChildren();
  for(const site of researchData.sites) {
    const card=el('article','panel research-card');
    const heading=el('div','research-card-heading');heading.append(el('h2','',site.name),el('span','badge','Live: not connected'));card.append(heading);
    card.append(el('p','',site.scope));
    const progress=el('div','research-progress'); progress.append(el('strong','',`${site.progress.percent}%`),el('span','',`${site.progress.completed}/${site.progress.total} checklist gates complete`));card.append(progress);
    const bar=el('progress','');bar.max=site.progress.total;bar.value=site.progress.completed;bar.setAttribute('aria-label',`${site.name} checklist completion`);card.append(bar);
    card.append(el('p','muted',`Documentation/design review: ${site.progress.documentation_review_completed}/${site.progress.documentation_review_total}. This is not a success probability.`));
    const gates=el('ul','gate-list');for(const gate of site.gates) {const row=el('li',gate.status);row.append(el('span','',gate.status==='complete'?'✓':'○'),el('span','',gate.label));row.title=gate.evidence;gates.append(row);}card.append(gates);
    const sources=el('div','research-sources');sources.append(el('strong','','Primary sources: '));for(const [index,source] of site.sources.entries()){const link=el('a','',String(index+1));link.href=source.url;link.target='_blank';link.rel='noopener noreferrer';link.setAttribute('aria-label',source.id);sources.append(link);}card.append(sources);
    const details=el('details','');details.append(el('summary','','Technical findings / unresolved questions'));for(const [key,value] of Object.entries(site.findings)){details.append(el('h3','',key.replaceAll('_',' ')),el('p','',value));}card.append(details);
    box.append(card);
  }
}
function loadFixture(){if(fixtures){$('fixture-input').value=JSON.stringify(fixtures[$('fixture-platform').value],null,2);$('fixture-output').textContent='Ready. This check never sends a message.';}}
$('fixture-platform').onchange=loadFixture;
$('inspect-fixture').onclick=async()=>{const control=$('inspect-fixture');control.disabled=true;try{const fixture=JSON.parse($('fixture-input').value);const output=await api(`/api/contracts/${$('fixture-platform').value}/inspect`,'POST',fixture);$('fixture-output').textContent=JSON.stringify(output,null,2);}catch(error){$('fixture-output').textContent='Rejected: '+error.message;}finally{control.disabled=false;}};
(async()=>{try{const info=await api('/api/info'); if(info.auth_required) $('auth-dialog').showModal();else await refresh();}catch(error){toast(error.message);}})();
setInterval(()=>{if(!$('auth-dialog').open) refresh().catch(()=>{});},2000);
