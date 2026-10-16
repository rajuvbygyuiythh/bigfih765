'use strict';
const $ = (id) => document.getElementById(id);
let researchData = null, fixtures = null, platforms = null, reviewedPlanHash = null;
let token = '', state = {instances: [], audit: []}, selected = null, filter = 'all', refreshing = false, toastTimer;
const adapterNames = {};
async function loadRegistry() {
  if(platforms) return;
  const result=await api('/api/platforms'); platforms=result.platforms;
  const select=$('adapter');select.replaceChildren();
  for(const platform of platforms){adapterNames[platform.id]=platform.name+(platform.local_ready?'':' · not connected');const option=el('option','',platform.name+(platform.local_ready?' · ready':platform.configurable?' · configuration only':' · '+platform.phase));option.value=platform.id;option.disabled=!platform.configurable;select.append(option);}
}
function prepareFixtures() {const select=$('fixture-platform');select.replaceChildren();for(const platform of platforms||[]){if(fixtures[platform.id]){const option=el('option','',platform.fixture_label);option.value=platform.id;select.append(option);}}loadFixture();}
function toast(message) { $('toast').textContent = message; $('toast').classList.remove('hidden'); clearTimeout(toastTimer); toastTimer = setTimeout(() => $('toast').classList.add('hidden'), 4500); }
async function api(path, method = 'GET', data) {
  const response = await fetch(path, {method, headers: {'Content-Type': 'application/json', ...(token ? {Authorization: `Bearer ${token}`} : {})}, ...(method !== 'GET' ? {body: JSON.stringify(data || {})} : {})});
  const result = await response.json();
  if (!response.ok) { if (response.status === 401 && !$('auth-dialog').open) $('auth-dialog').showModal(); throw new Error(result.error || `Request failed (${response.status})`); }
  return result;
}
function el(tag, cls, text) {const node = document.createElement(tag); if(cls) node.className = cls; if(text !== undefined) node.textContent = text; return node;}
function button(text, cls, callback, disabled = false) {const b = el('button', cls, text); b.disabled = disabled; b.addEventListener('click', async (event) => { event.stopPropagation(); b.disabled = true; b.setAttribute('aria-busy','true'); try {await callback(); await refresh();} catch(error) {toast(error.message);} finally {b.setAttribute('aria-busy','false');if(b.isConnected) b.disabled = disabled;}}); return b;}
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
async function refresh() {if(refreshing) return; refreshing=true; try {state=await api('/api/state'); await loadRegistry(); render(); await refreshLogs(); await refreshDiagnostics(); await refreshWorkflow(); try { researchData=await api('/api/research'); renderResearch(); } catch(error) { $('research-cards').replaceChildren(el('p','error',error.message)); } $('connection-status').textContent='CONNECTED · LOCAL STATE';} catch(error) {$('connection-status').textContent='CONNECTION ERROR'; throw error;} finally {refreshing=false;}}
function openCreate() {$('form-error').textContent=''; $('create-dialog').showModal(); $('instance-name').focus();}
$('add').onclick=openCreate; $('empty-add').onclick=openCreate;
$('close-dialog').onclick=()=>$('create-dialog').close(); $('cancel-dialog').onclick=()=>$('create-dialog').close();
$('create-form').onsubmit=async(event)=>{event.preventDefault(); const submit=event.submitter; submit.disabled=true; try {const item=await api('/api/instances','POST',{name:$('instance-name').value,adapter:$('adapter').value}); selected=item.id; $('create-dialog').close(); $('create-form').reset(); await refresh(); document.querySelector('[data-view=fleet]').click(); toast('Instance configuration saved.');} catch(error){$('form-error').textContent=error.message;} finally{submit.disabled=false;}};
$('auth-form').onsubmit=async(event)=>{event.preventDefault(); token=$('operator-token').value; try{await api('/api/state'); $('auth-dialog').close(); $('operator-token').value=''; $('auth-error').textContent=''; await refresh();}catch(error){token=''; $('auth-error').textContent=error.message;}};
$('auth-dialog').addEventListener('cancel',event=>event.preventDefault());
$('search').oninput=render;
$('stop-all').onclick=async()=>{try {await api('/api/stop-all','POST'); await refresh(); toast('Synthetic workers stopped and Minnit diagnostics disarmed.');}catch(error){toast(error.message);}};
for(const tab of document.querySelectorAll('[data-filter]')) tab.onclick=()=>{filter=tab.dataset.filter; for(const b of document.querySelectorAll('[data-filter]')) b.classList.toggle('active',b===tab);render();};
for(const nav of document.querySelectorAll('[data-view]')) nav.onclick=async()=>{
  const view=nav.dataset.view;
  for(const b of document.querySelectorAll('[data-view]')) b.classList.toggle('active',b===nav);
  for(const id of ['fleet','activity','research','diagnostics','queue']) $(`${id}-view`).classList.toggle('hidden',id!==view);
  const titles={fleet:'Instance fleet',activity:'Workspace activity',research:'Site research',diagnostics:'Minnit diagnostics',queue:'Locked site queue'};
  const descriptions={fleet:'Configure your instances. Control every lifecycle.',activity:'A clear timeline of local lifecycle events.',research:'Source-backed analysis, local contract tests, and explicit delivery gates.',diagnostics:'One authorized room. Explicit test requests. Operator-approved sends.',queue:'Finish one site. Unlock exactly the next. No skipped acceptance gates.'};
  $('page-title').textContent=titles[view]; $('breadcrumb').textContent=titles[view]; $('page-description').textContent=descriptions[view];
  if(view==='research'&&!fixtures) {try{await loadRegistry();fixtures=(await api('/api/contracts')).fixtures;prepareFixtures();}catch(error){toast(error.message);}}
};
function renderResearch() {
  if(!researchData) return;
  const box=$('research-cards');box.replaceChildren();
  $('research-count').textContent=researchData.summary.tracked;
  $('research-summary').textContent=`${researchData.summary.tracked} tracked · ${researchData.summary.local_contracts} local contracts · 0 live`;
  const query=$('research-search').value.toLowerCase(), phase=$('research-filter').value;
  const visible=researchData.sites.filter(site=>site.name.toLowerCase().includes(query)&&(phase==='all'||(phase==='contract'?site.has_local_contract:site.phase===phase)));
  for(const site of visible) {
    const card=el('article','panel research-card');card.dataset.platform=site.id;
    const heading=el('div','research-card-heading');heading.append(el('h2','',site.name),el('span','badge',site.phase.replaceAll('_',' ')));card.append(heading);
    card.append(el('p','',site.scope));
    const progress=el('div','research-progress'); progress.append(el('strong','',site.progress.applicable?`${site.progress.percent}%`:'N/A'),el('span','',site.progress.applicable?`${site.progress.completed}/${site.progress.total} checklist gates complete`:'Research/reference only — not an implementation target'));card.append(progress);
    if(site.progress.applicable){const bar=el('progress','');bar.max=site.progress.total;bar.value=site.progress.completed;bar.setAttribute('aria-label',`${site.name} checklist completion`);card.append(bar);}
    card.append(el('p','muted',`Documentation/design review: ${site.progress.documentation_review_completed}/${site.progress.documentation_review_total}. This is not a success probability.`));
    card.append(el('p','muted',site.start_blocker));
    const addConfig=button(site.configurable?'Add configuration':'Tracking only','secondary',async()=>{openCreate();$('adapter').value=site.id;$('instance-name').value=site.name+' workspace';},!site.configurable);card.append(addConfig);
    const gates=el('ul','gate-list');for(const gate of site.gates) {const row=el('li',gate.status);row.append(el('span','',gate.status==='complete'?'✓':'○'),el('span','',gate.label));row.title=gate.evidence;gates.append(row);}card.append(gates);
    const sources=el('div','research-sources');sources.append(el('strong','','Primary sources: '));for(const [index,source] of site.sources.entries()){const link=el('a','',String(index+1));link.href=source.url;link.target='_blank';link.rel='noopener noreferrer';link.setAttribute('aria-label',source.id);sources.append(link);}card.append(sources);
    const details=el('details','');details.append(el('summary','','Technical findings / unresolved questions'));for(const [key,value] of Object.entries(site.findings)){details.append(el('h3','',key.replaceAll('_',' ')),el('p','',value));}card.append(details);
    box.append(card);
  }
  if(!visible.length) box.append(el('p','muted','No tracked sites match this filter.'));
}
$('research-search').oninput=renderResearch;
$('research-filter').onchange=renderResearch;
function loadFixture(){if(fixtures){$('fixture-input').value=JSON.stringify(fixtures[$('fixture-platform').value],null,2);$('fixture-output').textContent='Ready. This check never sends a message.';}}
$('fixture-platform').onchange=loadFixture;
$('inspect-fixture').onclick=async()=>{const control=$('inspect-fixture');control.disabled=true;try{const fixture=JSON.parse($('fixture-input').value);const output=await api(`/api/contracts/${$('fixture-platform').value}/inspect`,'POST',fixture);$('fixture-output').textContent=JSON.stringify(output,null,2);}catch(error){$('fixture-output').textContent='Rejected: '+error.message;}finally{control.disabled=false;}};
(async()=>{try{const info=await api('/api/info'); if(info.auth_required) $('auth-dialog').showModal();else await refresh();}catch(error){toast(error.message);}})();
setInterval(()=>{if(!$('auth-dialog').open) refresh().catch(()=>{});},2000);

async function refreshDiagnostics() {
  try {
    const [diagnostic, ledger] = await Promise.all([api('/api/diagnostics/minnit'), api('/api/diagnostics/minnit/deliveries')]);
    $('diagnostic-badge').textContent=diagnostic.armed?'ARMED · TEST ONLY':diagnostic.configured?'DISARMED':'UNCONFIGURED';
    $('diagnostic-status').textContent=diagnostic.armed?`Intake armed until ${new Date(diagnostic.expires_at*1000).toLocaleTimeString()}. Each fresh ping needs separate approval. Live validation: not verified.`:'Intake disarmed. Configure the server environment using README instructions, then arm a 15-minute test window.';
    $('diagnostic-blockers').replaceChildren(...diagnostic.blockers.map(message=>el('li','',message)));
    $('diagnostic-controls').replaceChildren(
      button('Arm test intake','start',async()=>{if(confirm('Confirm this is your authorized test room with consenting participants. Arm intake for 15 minutes?')) await api('/api/diagnostics/minnit/arm','POST');},!diagnostic.configured||diagnostic.armed||diagnostic.workflow_locked),
      button('Disarm intake','danger-ghost',async()=>{await api('/api/diagnostics/minnit/disarm','POST');},!diagnostic.armed));
    const box=$('diagnostic-deliveries');box.replaceChildren();
    for(const delivery of ledger.deliveries) {
      const row=el('article','diagnostic-delivery');
      row.append(el('strong','',delivery.status),el('span','muted',` ${delivery.id.slice(0,8)} · peer delivery: ${delivery.peer_delivery} · HTTP ${delivery.http_status??'—'}`));
      const age=Date.now()/1000-delivery.event_at;
      row.append(button('Approve fixed pong','secondary',async()=>{if(confirm(`Send exactly this reply to the configured test room?\n\n${diagnostic.reply}`)) {const result=await api(`/api/diagnostics/minnit/deliveries/${delivery.id}/approve`,'POST',{run_id:diagnostic.run_id});toast(`${result.status} · peer delivery unverified`);}},diagnostic.workflow_locked||!diagnostic.armed||delivery.status!=='pending'||delivery.run_id!==diagnostic.run_id||age>300||age< -30));
      box.append(row);
    }
    if(!ledger.deliveries.length) box.append(el('p','log-empty','No diagnostic events recorded. No messages sent.'));
  } catch(error) {
    $('diagnostic-status').textContent='Diagnostic status unavailable: '+error.message;
    $('diagnostic-controls').replaceChildren();
    $('diagnostic-deliveries').replaceChildren();
  }
}

async function refreshWorkflow() {
  try {
    const queue=await api('/api/workflow');
    $('queue-active').textContent=queue.active_site?`Active: ${adapterNames[queue.active_site]?.split(' · ')[0]||queue.active_site} · next locked: ${queue.next_site||'none'}`:'All target sites completed.';
    const box=$('queue-cards');box.replaceChildren();
    for(const id of [...queue.order,...Object.keys(queue.sites).filter(id=>!queue.order.includes(id))]) {
      const item=queue.sites[id], card=el('article','panel queue-card');card.dataset.site=id;
      card.append(el('h3','',adapterNames[id]?.split(' · ')[0]||id),el('span',`badge ${item.state}`,item.state==='active'?'UNLOCKED · ACTIVE':item.state.toUpperCase()));
      card.append(el('p','muted',item.percent===null?'Not an unlock target':`${item.completed_steps.length}/8 delivery steps · ${item.percent}%`));
      if(item.state==='locked') card.append(el('p','muted','Locked until the current site is fully complete.'));
      if(item.state==='active') {
        card.append(el('p','muted',`Plan: ${item.plan?.status||'plan_required'} · readiness: ${queue.readiness||'not_verified'}`));
        if(item.plan?.sha256) {
          card.append(el('p','muted',`Plan SHA-256: ${item.plan.sha256}`));
          card.append(button('Read scope plan','secondary',async()=>{const plan=await api('/api/workflow/plan');$('queue-plan').textContent=plan.markdown;reviewedPlanHash=plan.plan_sha256;}));
          if(!item.plan.approved) card.append(button('Approve exact plan','secondary',async()=>{if(confirm(`Approve ONLY this plan for setup? This does not mark GREEN or unlock the next site.\nSHA-256: ${item.plan.sha256}`)) await api('/api/workflow/approve-plan','POST',{site:id,revision:queue.revision,plan_sha256:item.plan.sha256,approval_reference:'operator-dashboard'});},!queue.operator_mutations_enabled||reviewedPlanHash!==item.plan.sha256||item.completed_steps.length<2));
        }
        card.append(button('Complete site & unlock next','primary',async()=>{if(confirm('Complete this site and unlock exactly the next? All eight steps, live evidence and ZIP checksum must pass.')) await api('/api/workflow/complete-and-next','POST',{site:id,revision:queue.revision});},!queue.can_complete||!queue.operator_mutations_enabled));
      }
      box.append(card);
    }
    $('queue-blockers').replaceChildren(...queue.completion_blockers.map(reason=>el('li','',reason)));
  } catch(error) {
    $('queue-active').textContent='Queue unavailable — no unlock permitted.';
    $('queue-cards').replaceChildren();$('queue-blockers').replaceChildren(el('li','',error.message));
  }
}
