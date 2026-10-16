'use strict';
const $=id=>document.getElementById(id);
const names={deadsimplechat:'DeadSimpleChat',minnit:'Minnit',rumbletalk:'RumbleTalk',chatwee:'Chatwee',chatblink:'Chatblink',strangermeetup:'StrangerMeetup',chatango:'Chatango',chatiw:'Chatiw'};
const pages={home:'Home',sites:'Sites & delivery',messages:'Messages',sessions:'Sessions',chat:'Live chat',settings:'Settings',logs:'Logs & tests'};
const steps=['Recon','Contract','Intake','Outbound','Dashboard','Integration','Regression','Handoff'];
let token='', authenticated=false, disposed=false, busy=false, stopping=false, refreshing=false, localPolling=false, epoch=0;
let workflow=null, setup=null, configs=[], sessions=[], selected=null, receipt=null, pending=null;
let transcript=[], shown=new Set();
function text(id,value){$(id).textContent=String(value);}
function node(tag,value,cls){const el=document.createElement(tag);if(value!==undefined)el.textContent=String(value);if(cls)el.className=cls;return el;}
function notice(value,error=false){if(disposed)return;text('notice',value);$('notice').classList.toggle('error',error);}
function enabledScope(){return authenticated&&workflow?.active_site==='deadsimplechat'&&workflow?.sites?.deadsimplechat?.plan?.approved===true;}
function controls(){
 if(disposed)return;const active=enabledScope(), ready=!!selected, blocked=busy||stopping;
 $('stop-all').disabled=!authenticated||stopping;
 for(const id of ['script-file','sample','save-script','create-slot'])$(id).disabled=blocked||!active;
 $('local-start').disabled=blocked||!active||!ready||['waiting','complete'].includes(selected?.status);
 $('local-start').textContent=selected?.status==='stopped'?'▶ Resume test':'▶ Start test';
 $('local-stop').disabled=blocked||!ready||selected?.status!=='waiting';$('local-reset').disabled=blocked||!ready;
 $('user-message').disabled=blocked||!active||selected?.status!=='waiting'||!!pending;
 $('send-message').disabled=blocked||!active||(!pending&&selected?.status!=='waiting');text('send-message',pending?'Retry same event':'Send →');
 $('shadow-arm').disabled=blocked||!active||!setup?.configured||setup?.workflow_blocked||setup?.armed;
 $('shadow-disarm').disabled=blocked||!authenticated||!setup?.armed;
 $('register-intent').disabled=blocked||!active||!setup?.armed||setup?.workflow_blocked;
 $('read-plan').disabled=blocked||!workflow?.active_site;
 document.querySelectorAll('[data-session],[data-stop-session],[data-stop-slot]').forEach(el=>{el.disabled=blocked||!authenticated;});
}
async function api(path,method='GET',data){
 const response=await fetch(path,{method,headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},...(method==='GET'?{}:{body:JSON.stringify(data||{})})});
 const result=await response.json();
 if(!response.ok){
  if(response.status===401){authenticated=false;workflow=null;setup=null;configs=[];sessions=[];selected=null;pending=null;transcript=[];shown.clear();$('auth-banner').hidden=false;render();}
  const error=new Error(result.error||'Request failed');error.status=response.status;throw error;
 }
 return result;
}
function navigate(page,focus=false){
 if(!pages[page])page='home';
 for(const key of Object.keys(pages))$('page-'+key).hidden=key!==page;
 document.querySelectorAll('[data-page]').forEach(button=>{if(button.dataset.page===page)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');});
 text('breadcrumb',pages[page]);if(focus)$('main').focus();
}
document.querySelectorAll('[data-page],[data-goto]').forEach(button=>button.onclick=()=>{const page=button.dataset.page||button.dataset.goto;location.hash=page;navigate(page,true);});
window.addEventListener('hashchange',()=>navigate(location.hash.slice(1)));
navigate(location.hash.slice(1)||(location.pathname==='/test'?'messages':'home'));
window.addEventListener('pagehide',()=>{disposed=true;token='';pending=null;transcript=[];});
function badge(value,cls=''){return node('span',value,'badge '+cls);}
function emptyRow(body,columns,message){const row=node('tr'),cell=node('td',message);cell.colSpan=columns;row.append(cell);body.replaceChildren(row);}
function renderWorkflow(){
 const item=workflow?.sites?.[workflow.active_site], done=item?.completed_steps?.length||0;
 text('home-site',item?(names[workflow.active_site]||workflow.active_site):'—');text('active-name',item?(names[workflow.active_site]||workflow.active_site):'Workflow unavailable');
 text('home-progress',item?`${done} / 8`:'—');text('delivery-percent',item?`${item.percent}%`:'—');$('progress-bar').style.width=item?`${item.percent}%`:'0%';
 text('step-summary',item?`Step ${Math.min(done+1,8)} · ${steps[Math.min(done,7)]} ${done<8?'in progress':'evidence complete'}`:'No progress inferred');
 text('scope-status',item?.plan?.approved?'SCOPE APPROVED':'SCOPE BLOCKED');$('scope-status').className='badge '+(item?.plan?.approved?'green':'amber');
 const locked=workflow?.order?.filter(id=>workflow.sites[id].state==='locked').length;
 text('nav-locked',locked??'—');text('queue-count',workflow?`${workflow.order.length} SITES · ${locked} LOCKED`:'WORKFLOW UNAVAILABLE');
 text('next-site',workflow?.next_site?`${names[workflow.next_site]||workflow.next_site} is next. Still locked.`:'No successor inferred');
 $('home-steps').replaceChildren(...steps.map((label,index)=>{const li=node('li',undefined,index<done?'done':index===done&&item?'current':'');li.append(node('span',index<done?'✓':index+1,'step-dot'),node('span',label));return li;}));
 const rows=$('site-rows');
 if(!workflow){emptyRow(rows,5,'Saved queue unavailable. No unlock/progress is inferred.');}
 else rows.replaceChildren(...workflow.order.map((id,index)=>{
  const site=workflow.sites[id],row=node('tr');row.append(node('td',String(index+1).padStart(2,'0')),node('td',names[id]||id,'site-title'));
  const status=node('td');status.append(badge(site.state.toUpperCase(),site.state==='active'?'green':'muted'));row.append(status,node('td',`${site.completed_steps.length} / 8 · ${site.percent}%`),node('td',site.state==='locked'?`Complete ${names[workflow.order[index-1]]||workflow.order[index-1]} first`:site.state==='done'?'Evidence-backed handoff complete':`Step ${Math.min(site.completed_steps.length+1,8)} · ${steps[Math.min(site.completed_steps.length,7)]}`));return row;
 }));
 text('plan-hash',item?.plan?.sha256||'No verified current plan');text('approval-ref',item?.approval?.reference||'No approval recorded');
 text('scope-description',workflow?.active_site==='deadsimplechat'?'DS-DIAG-v1: one authorized room/bot, registered consenting question/user/action, at most one fixed disclosed diagnostic reply. No sender exists yet.':'Only the active site’s verified scoped plan may govern work.');
}
function renderSetup(){
 text('home-sends',setup?setup.external_messages_sent:'—');text('setup-status',setup?.armed?'SHADOW ARMED':setup?.configured&&!setup?.workflow_blocked?'SHADOW CONFIGURED':'SETUP BLOCKED');
 $('setup-blockers').replaceChildren(...(setup?[...setup.blockers,...(setup.workflow_blocked?['Active approved scope is blocked']:[])]:['Sanitized setup report unavailable']).map(value=>node('li',value)));
 if(setup&&!setup.blockers.length&&!setup.workflow_blocked)$('setup-blockers').append(node('li','Shadow configuration complete. Still no provider sender/authenticity proof.'));
 $('live-blockers').replaceChildren(...(setup?.live_blockers||['Sanitized live requirements unavailable. No connection is inferred.']).map(value=>node('li',value)));
 text('shadow-summary',setup?`${setup.armed?'Armed':'Disarmed'} · ${setup.counts.registered||0} registered · ${setup.counts.matched||0} matched · 0 DS sends`:'Status unavailable');
}
function renderLocal(){
 const row=selected;text('home-replies',row?row.cursor:'—');text('chat-generated',row?row.cursor:'—');text('observed-session',row?`${row.id.slice(0,8)} · ${row.status}`:'None selected');
 text('script-count',row?`${row.total_lines} LINES`:'NO SCRIPT');text('local-counter',row?`${row.cursor} / ${row.total_lines} lines`:'0 / 0 lines');
 text('local-status',row?(row.status==='waiting'?'WAITING FOR INPUT':row.status==='complete'?'LOCAL COMPLETE':row.status.toUpperCase()):'NO SESSION');
 if(row)$('script-preview').replaceChildren(...row.script_preview.map((line,index)=>node('li',line,index<row.cursor?'used':index===row.cursor?'next':'')));
 else $('script-preview').replaceChildren(node('li','Load a script to see its sequence.'));
 renderTranscript();
}
function renderTranscript(){
 for(const id of ['test-chat','observed-chat']){
  const root=$(id);if(!transcript.length){
   const empty=node('div',undefined,'empty-state');empty.append(node('span','◌'),node('h3',id==='test-chat'?'Test your next conversation.':'No observed chat yet.'),node('p',selected?'Historical user inputs are not stored. New test messages appear here in this tab.':'Load a script in Messages and start a local self-test. No provider chat is connected.'));root.replaceChildren(empty);
  }else root.replaceChildren(...transcript.map(item=>{const bubble=node('div',undefined,'chat-bubble '+item.kind);bubble.append(node('small',item.label),node('p',item.text));return bubble;}));
 }
}
function actionButton(label,attr,id){const button=node('button',label);button.dataset[attr]=id;return button;}
function renderSessions(){
 const root=$('session-rows');if(!sessions.length)emptyRow(root,5,'No local sessions saved. Create one in Messages.');
 else root.replaceChildren(...sessions.map(item=>{const row=node('tr');row.append(node('td',item.id.slice(0,8)),node('td',item.status),node('td',`${item.cursor} / ${item.total_lines}`),node('td',item.run_id?.slice(0,8)||'Stopped / no run'));const cell=node('td');cell.append(actionButton(selected?.id===item.id?'Selected':'Open','session',item.id));if(item.status==='waiting')cell.append(actionButton('Stop','stopSession',item.id));row.append(cell);return row;}));
 const slots=$('instance-rows');if(!configs.length)emptyRow(slots,4,'No saved DS configurations. Create a non-secret label in Settings.');
 else slots.replaceChildren(...configs.map(item=>{const row=node('tr');row.append(node('td',item.name));const id=node('td');id.append(node('code',item.id));row.append(id,node('td',`${item.status} · not live`));const cell=node('td');cell.append(actionButton('Stop slot','stopSlot',item.id));row.append(cell);return row;}));
 const previous=$('instance-select').value;
 $('instance-select').replaceChildren(...(configs.length?configs.map(item=>{const option=node('option',item.name);option.value=item.id;return option;}):[node('option','No DS configurations')]));
 if(configs.some(item=>item.id===previous))$('instance-select').value=previous;
 showSlot();
}
function showSlot(){const item=configs.find(item=>item.id===$('instance-select').value);text('instance-detail',item?`Slot ID: ${item.id} · ${item.status} · not connected. Private DS_INSTANCE_ID binding is set on the server, not by this selection.`:'A slot does not establish account authorization.');}
$('instance-select').onchange=showSlot;
function renderLogs(){
 text('receipt-status',receipt?.fresh_and_passed?'Current source · local regression PASS':'Regression proof missing, stale or failed');
 text('receipt-badge',receipt?.fresh_and_passed?'LOCAL PASS':'UNVERIFIED');$('receipt-badge').className='badge '+(receipt?.fresh_and_passed?'green':'amber');
 text('receipt-detail',receipt?.finished_at?`${new Date(receipt.finished_at).toLocaleString()} · no provider or peer-delivery proof`:'Run tools/run_checks.py --ui to bind actual test evidence to source.');
 const filter=$('log-filter').value, events=[];
 if(filter!=='shadow')for(const event of selected?.events||[])events.push({at:event.at,kind:'LOCAL',value:`Session ${selected.id.slice(0,8)} · line ${event.reply_index+1} generated · event ${event.event_id.slice(0,8)} · not externally delivered`});
 if(filter!=='local')for(const event of setup?.intents||[])events.push({at:event.matched_at||event.created_at,kind:'SHADOW',value:`Intent ${event.id.slice(0,8)} · ${event.status} · repeated callbacks suppressed ${event.duplicates} · no send`});
 events.sort((a,b)=>b.at-a.at);
 $('outcome-log').replaceChildren(...(events.length?events.slice(0,60).map(event=>{const row=node('div',undefined,'log-entry');row.append(node('time',new Date(event.at*1000).toLocaleTimeString()),node('b',event.kind),node('span',event.value));return row;}):[node('p','No observed local / shadow outcomes for this selection.','hint')]));
}
function render(){if(disposed)return;renderWorkflow();renderSetup();renderLocal();renderSessions();renderLogs();controls();}
async function refresh(force=false){
 if(disposed||!authenticated||refreshing||busy&&!force)return;refreshing=true;const version=epoch;
 try{
  const [wf,provider,state,index,research]=await Promise.all([api('/api/workflow'),api('/api/deadsimplechat/setup'),api('/api/state'),api('/api/reply-test/sessions'),api('/api/research')]);
  if(disposed||version!==epoch)return;
  workflow=wf;setup=provider;configs=state.instances.filter(item=>item.adapter==='deadsimplechat');sessions=index.sessions;receipt=research.local_test_receipt;
  if(!selected&&sessions.length){const restored=await api('/api/reply-test/sessions/'+sessions[0].id);if(disposed||version!==epoch)return;selected=restored;text('script-label','Saved local script');}
  text('connection','LOCAL API CONNECTED');text('updated','Updated '+new Date().toLocaleTimeString()+' · local API');render();
 }catch(error){if(!disposed&&version===epoch){workflow=null;setup=null;receipt=null;render();text('connection','STATUS UNAVAILABLE');text('updated','Status unavailable · no live state inferred');notice(error.message,true);}}
 finally{refreshing=false;}
}
async function task(callback){if(busy||stopping||disposed)return;busy=true;epoch++;controls();try{await callback();}catch(error){notice(error.message,true);}finally{busy=false;if(!disposed){render();await refresh();}}}
async function localPoll(){
 if(disposed||!authenticated||!selected||busy||stopping||localPolling)return;localPolling=true;const id=selected.id,version=epoch;
 try{const state=await api('/api/reply-test/sessions/'+id);if(!disposed&&epoch===version&&selected?.id===id){selected=state;if(pending&&pending.run_id!==state.run_id)pending=null;renderLocal();renderLogs();controls();}}
 catch(error){if(!disposed)notice(error.message,true);}finally{localPolling=false;}
}
async function chooseSession(id){const state=await api('/api/reply-test/sessions/'+id);if(disposed)return;selected=state;pending=null;transcript=[];shown.clear();text('script-label','Saved local script');$('user-message').value='';render();}
async function loadScript(value,label){const result=await api('/api/reply-test/sessions','POST',{script:value});if(disposed)return;selected=result;pending=null;transcript=[];shown.clear();text('script-label',label);$('user-message').value='';render();notice('Script validated. Start a local test, then send a test user message. No provider sends.');}
$('sample').onclick=()=>{if(busy||stopping)return;$('script-input').value='Hello! This is reply line 1.\nThanks for your message. This is reply line 2.\nThat was our final local test reply.';notice('Sample draft loaded. Click Load & validate script.');};
$('save-script').onclick=()=>task(()=>loadScript($('script-input').value,'Edited TXT sequence'));
function readFile(file){return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>{try{resolve(new TextDecoder('utf-8',{fatal:true}).decode(new Uint8Array(reader.result)));}catch{reject(new Error('Use a valid UTF-8 TXT file.'));}};reader.onerror=()=>reject(new Error('Could not read the TXT file.'));reader.readAsArrayBuffer(file);});}
$('script-file').onchange=()=>task(async()=>{const file=$('script-file').files[0];if(!file)return;try{if(!/\.txt$/i.test(file.name)||file.size>8192)throw new Error('Choose a .txt file up to 8 KiB.');const value=await readFile(file);await loadScript(value,file.name);$('script-input').value=value;}finally{$('script-file').value='';}});
$('local-start').onclick=()=>task(async()=>{selected=await api(`/api/reply-test/sessions/${selected.id}/start`,'POST');notice('Local test waiting for your input. No automatic message is sent.');});
$('local-stop').onclick=()=>task(async()=>{selected=await api(`/api/reply-test/sessions/${selected.id}/stop`,'POST');pending=null;notice('Selected local test stopped. Resume explicitly to continue.');});
$('local-reset').onclick=()=>task(async()=>{selected=await api(`/api/reply-test/sessions/${selected.id}/reset`,'POST');pending=null;transcript=[];shown.clear();$('user-message').value='';notice('Local sequence reset to line 1. No automatic start.');});
$('message-form').onsubmit=event=>{event.preventDefault();task(async()=>{
 if(!selected||!enabledScope())throw new Error('An approved active DS scope and local session are required.');
 if(!pending){const value=$('user-message').value;if(!value.trim())throw new Error('Enter a local test user message.');pending={text:value,run_id:selected.run_id,event_id:crypto.randomUUID()};}
 const outgoing=pending;
 try{
  const result=await api(`/api/reply-test/sessions/${selected.id}/message`,'POST',outgoing);
  if(disposed)return;
  if(!shown.has(result.event_id)){transcript.push({kind:'user',label:'YOU · LOCAL TEST',text:outgoing.text},{kind:'bot',label:`LOCAL SCRIPT · LINE ${result.reply_index+1}`,text:result.reply});transcript=transcript.slice(-60);shown.add(result.event_id);}
  selected=result.state;pending=null;$('user-message').value='';notice(selected.status==='complete'?'Local script complete. This is not provider acceptance or peer delivery.':'One local reply generated. Send another input for the next line.');
 }catch(error){if(error.status&&error.status<500)pending=null;else error.message='Response uncertain. Retry uses the same event ID; do not start a new event. '+error.message;throw error;}
 });};
$('user-message').onkeydown=event=>{if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();$('message-form').requestSubmit();}};
$('session-rows').onclick=event=>{const button=event.target.closest('button');if(!button)return;if(button.dataset.session)task(()=>chooseSession(button.dataset.session));if(button.dataset.stopSession)task(async()=>{const state=await api(`/api/reply-test/sessions/${button.dataset.stopSession}/stop`,'POST');if(selected?.id===state.id){selected=state;pending=null;}notice('Local session stop acknowledged.');});};
$('instance-rows').onclick=event=>{const button=event.target.closest('[data-stop-slot]');if(button)task(async()=>{await api(`/api/instances/${button.dataset.stopSlot}/stop`,'POST');notice('DS slot stop acknowledged. It was not provider-connected.');});};
$('slot-form').onsubmit=event=>{event.preventDefault();task(async()=>{if(!enabledScope())throw new Error('Only active approved DS setup is available.');await api('/api/instances','POST',{name:$('slot-name').value,adapter:'deadsimplechat'});$('slot-name').value='';notice('Non-secret DS slot saved. No account connection or private env changed.');});};
$('shadow-arm').onclick=()=>task(async()=>{setup=await api('/api/deadsimplechat/shadow/arm','POST');notice('Shadow observation armed. No sender exists.');});
$('shadow-disarm').onclick=()=>task(async()=>{await api('/api/deadsimplechat/shadow/disarm','POST');notice('Shadow disarmed; unused intents cancelled.');});
$('intent-form').onsubmit=event=>{event.preventDefault();task(async()=>{await api('/api/deadsimplechat/shadow/register','POST',{question_id:$('question-id').value,test_user_id:$('test-user-id').value,run_id:setup?.run_id});$('question-id').value='';$('test-user-id').value='';notice('Registered one shadow intent; still no provider send.');});};
$('read-plan').onclick=()=>task(async()=>{const report=await api('/api/workflow/plan');text('plan-content',report.markdown);$('plan-content').hidden=false;notice('Read-only provider scope. No approval or unlock action performed.');});
$('log-filter').onchange=renderLogs;
$('refresh').onclick=()=>refresh();
$('stop-all').onclick=async()=>{
 if(!authenticated||stopping)return;stopping=true;epoch++;pending=null;controls();
 try{await api('/api/stop-all','POST');await localPoll();notice('Global Stop acknowledged. Local tests and shadow intake disarmed; inspect current status below.');}
 catch(error){notice('Stop could not be confirmed. '+error.message,true);}
 finally{stopping=false;controls();await refresh();await localPoll();}
};
$('auth-form').onsubmit=event=>{event.preventDefault();task(async()=>{token=$('operator-token').value;$('operator-token').value='';try{await api('/api/state');authenticated=true;$('auth-banner').hidden=true;notice('Operator authenticated. No automatic start.');}catch(error){token='';throw error;}});};
controls();
(async()=>{try{const info=await api('/api/info');if(disposed)return;if(info.auth_required){$('auth-banner').hidden=false;text('connection','AUTH REQUIRED');notice('Authenticate to read the actual workspace. Nothing starts on login.');}else{authenticated=true;notice('Sample-only local workspace. Provider disabled. Do not enter private data in this public demo.');await refresh();}controls();}catch(error){notice(error.message,true);}})();
setInterval(()=>refresh(),5000);setInterval(localPoll,1000);
