'use strict';
const $=id=>document.getElementById(id);
let token='', session=null, pending=null, busy=false, polling=false, version=0, disposed=false;
window.addEventListener('pagehide',()=>{disposed=true;});
const shown=new Set();
function notice(text,error=false){if(disposed)return;$('notice').textContent=text;$('notice').classList.toggle('error',error);}
function node(tag,text,cls){const item=document.createElement(tag);if(text!==undefined)item.textContent=text;if(cls)item.className=cls;return item;}
async function api(path,method='GET',data){
  const response=await fetch(path,{method,headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},...(method==='GET'?{}:{body:JSON.stringify(data||{})})});
  const result=await response.json();
  if(!response.ok){if(response.status===401)$('login').hidden=false;const error=new Error(result.error||'Request failed');error.status=response.status;throw error;}
  return result;
}
function controls(){
  if(disposed)return;
  const ready=!!session;
  $('script-file').disabled=busy;$('sample').disabled=busy;
  $('start').disabled=busy||!ready||session?.status==='waiting'||session?.status==='complete';
  $('stop').disabled=busy||!ready||session?.status!=='waiting';$('reset').disabled=busy||!ready;
  $('user-message').disabled=busy||!ready||session?.status!=='waiting'||!!pending;
  $('send').disabled=busy||!ready||(!pending&&session?.status!=='waiting');
  $('send').textContent=pending?'Retry same event':'Send →';
}
function render(state){
  session=state;
  try{sessionStorage.setItem('orbit-reply-test-session',state.id);}catch{}
  $('total').textContent=state.total_lines;$('used').textContent=state.cursor;$('remaining').textContent=state.remaining;
  $('external').textContent=state.external_messages_sent;$('duplicates').textContent=state.duplicates;
  $('test-status').textContent=state.status==='waiting'?'WAITING FOR YOUR MESSAGE':state.status==='complete'?'LOCAL SCRIPT COMPLETE':state.status.toUpperCase();
  $('run').textContent=state.run_id?state.run_id.slice(0,8):'—';$('file-badge').textContent=state.total_lines+' LINES';
  $('script-lines').replaceChildren(...state.script_preview.map((line,index)=>node('li',line,index<state.cursor?'used':index===state.cursor?'next':'')));
  const events=state.events.map(item=>{const row=node('div',undefined,'event');row.append(node('time',new Date(item.at*1000).toLocaleTimeString()),node('span',`Local reply ${item.reply_index+1} generated · event ${item.event_id.slice(0,8)}`));return row;});
  $('events').replaceChildren(...(events.length?events:[node('p','No local message events yet.','muted')]));
  controls();
}
async function task(callback){if(busy)return;busy=true;version++;controls();try{await callback();}catch(error){notice(error.message,true);}finally{busy=false;controls();}}
async function loadScript(text,label){
  const state=await api('/api/reply-test/sessions','POST',{script:text});
  pending=null;shown.clear();$('chat').replaceChildren();$('user-message').value='';$('file-name').textContent=label;
  render(state);notice('Script loaded. Click Start test, then send your first test user message.');
}
function readFile(file){return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>{try{resolve(new TextDecoder('utf-8',{fatal:true}).decode(new Uint8Array(reader.result)));}catch{reject(new Error('Use a valid UTF-8 TXT file.'));}};reader.onerror=()=>reject(new Error('Could not read this TXT file.'));reader.readAsArrayBuffer(file);});}
$('script-file').addEventListener('change',()=>task(async()=>{const file=$('script-file').files[0];if(!file)return;if(!/\.txt$/i.test(file.name)||file.size>8192)throw new Error('Choose a .txt file up to 8 KiB.');await loadScript(await readFile(file),file.name);$('script-file').value='';}));
$('sample').onclick=()=>task(()=>loadScript('Hello! This is reply line 1.\nThanks for your message. This is reply line 2.\nThat was our final test reply.','3-line sample (local test)'));
$('start').onclick=()=>task(async()=>{render(await api(`/api/reply-test/sessions/${session.id}/start`,'POST'));notice('Running locally. Type a user message to receive the next TXT line.');});
$('stop').onclick=()=>task(async()=>{render(await api(`/api/reply-test/sessions/${session.id}/stop`,'POST'));pending=null;notice('Stopped. No new local reply can be generated until you resume.');});
$('reset').onclick=()=>task(async()=>{render(await api(`/api/reply-test/sessions/${session.id}/reset`,'POST'));pending=null;shown.clear();$('chat').replaceChildren();$('user-message').value='';notice('Reset to line 1. Click Start test for a fresh run.');});
function bubble(kind,text,label){const row=node('div',undefined,'bubble '+kind);row.append(node('small',label),node('p',text));$('chat').append(row);$('chat').scrollTop=$('chat').scrollHeight;}
$('message-form').onsubmit=event=>{event.preventDefault();task(async()=>{
  if(!session)throw new Error('Load a script first.');
  if(!pending){const text=$('user-message').value;if(!text.trim())throw new Error('Type a test user message first.');pending={text,event_id:crypto.randomUUID(),run_id:session.run_id};}
  const outgoing=pending;
  try{
    const result=await api(`/api/reply-test/sessions/${session.id}/message`,'POST',outgoing);
    if(!shown.has(result.event_id)){bubble('user',outgoing.text,'YOU · TEST USER');bubble('bot',result.reply,`LOCAL SCRIPT · LINE ${result.reply_index+1}`);shown.add(result.event_id);}
    pending=null;$('user-message').value='';render(result.state);
    notice(result.state.status==='complete'?'All TXT lines used. Local test complete — NOT a provider delivery pass.':`Local reply ${result.reply_index+1} shown. Send another user message for the next line.`);
  }catch(error){if(error.status&&error.status<500)pending=null;else error.message='Response uncertain. Retry uses the same event ID; no extra line consumed. '+error.message;throw error;}
});};
$('user-message').onkeydown=event=>{if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();$('message-form').requestSubmit();}};
$('login').onsubmit=event=>{event.preventDefault();task(async()=>{token=$('token').value;try{await api('/api/workflow');$('token').value='';$('login').hidden=true;if(!await restore())notice('Operator authenticated. Load a TXT file to begin.');}catch(error){token='';throw error;}});};
async function poll(){if(!session||busy||polling)return;polling=true;const current=version,id=session.id;try{const state=await api(`/api/reply-test/sessions/${id}`);if(!disposed&&current===version&&id===session?.id){render(state);$('poll-status').textContent='Updated '+new Date().toLocaleTimeString()+' · 1s local refresh';}}catch(error){if(!disposed){$('poll-status').textContent='Report unavailable';notice(error.message,true);}}finally{polling=false;}}
async function restore(){let id;try{id=sessionStorage.getItem('orbit-reply-test-session');}catch{}if(id&&/^[a-f0-9]{32}$/.test(id)){render(await api(`/api/reply-test/sessions/${id}`));notice('Restored script/report. Chat bubbles are tab-local; click Start to resume after server restart.');return true;}return false;}
(async()=>{try{const info=await api('/api/info');if(info.auth_required){$('login').hidden=false;return;}await restore();}catch(error){notice(error.message,true);}})();
setInterval(poll,1000);
