// Actual local HTTP + jsdom for the operator workspace. Provider disabled.
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
const {mkdtemp,rm}=require('node:fs/promises');
const {tmpdir}=require('node:os');
const path=require('node:path');
const {randomUUID}=require('node:crypto');
const {TextDecoder}=require('node:util');
const {JSDOM,VirtualConsole}=require('jsdom');
async function waitFor(predicate,label){const end=Date.now()+10000;while(Date.now()<end){if(predicate())return;await new Promise(resolve=>setTimeout(resolve,25));}throw new Error('Timeout: '+label);}
(async()=>{
 const tmp=await mkdtemp(path.join(tmpdir(),'orbit-workspace-'));let server,dom,checks=0;
 try{
  const token='workspace-test-token';
  server=spawn('python',['-B','app.py','--host','127.0.0.1','--port','0','--db',path.join(tmp,'test.db')],{cwd:path.resolve(__dirname,'..'),env:{...process.env,CONTROL_PLANE_TOKEN:token,ORBIT_MINNIT_DIAGNOSTICS:'0',ORBIT_MINNIT_AUTHORIZED:'0',DS_SHADOW_ENABLED:'0'},stdio:['ignore','pipe','pipe']});
  const base=await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(new Error('startup timeout')),8000);server.once('error',reject);server.stdout.on('data',chunk=>{const match=chunk.toString().match(/listening on 127\.0\.0\.1:(\d+)/);if(match){clearTimeout(timeout);resolve('http://127.0.0.1:'+match[1]);}});server.once('exit',()=>{clearTimeout(timeout);reject(new Error('server exited'));});});
  const errors=[],requests=[],vc=new VirtualConsole();vc.on('jsdomError',error=>errors.push(error));let discardNextMessage=false,failWorkflow=false;
  dom=await JSDOM.fromURL(base,{runScripts:'dangerously',resources:'usable',pretendToBeVisual:true,virtualConsole:vc,beforeParse(w){w.TextDecoder=TextDecoder;Object.defineProperty(w.crypto,'randomUUID',{value:randomUUID});w.fetch=async(url,options)=>{requests.push({url,options});if(failWorkflow&&url==='/api/workflow')throw new Error('Injected local status outage');const response=await fetch(new URL(url,base),options);if(discardNextMessage&&url.endsWith('/message')){discardNextMessage=false;await response.text();throw new Error('Discarded real local HTTP response for retry regression');}return response;};}});
  const w=dom.window,d=w.document,$=id=>d.getElementById(id),settled=()=>!w.eval('busy')&&!w.eval('refreshing')&&!w.eval('stopping');
  function submit(id){$(id).dispatchEvent(new w.SubmitEvent('submit',{bubbles:true,cancelable:true}));}
  function nav(page){d.querySelector(`[data-page="${page}"]`).click();assert.equal($('page-'+page).hidden,false);}
  function pass(message){checks++;console.log('PASS WORKSPACE: '+message);}
  await waitFor(()=>!$('auth-banner').hidden,'auth challenge');
  $('operator-token').value='wrong';submit('auth-form');await waitFor(()=>$('notice').textContent.includes('required')&&settled(),'wrong auth');assert.equal($('stop-all').disabled,true);
  $('operator-token').value=token;submit('auth-form');await waitFor(()=>$('connection').textContent==='LOCAL API CONNECTED'&&settled(),'authenticated workspace');
  assert.equal($('operator-token').value,'');assert.equal(w.localStorage.length,0);assert.equal(w.sessionStorage.length,0);pass('default shell authenticates; token memory-only, login never starts work');
  assert.equal(d.querySelectorAll('[data-page]').length,7);for(const page of ['home','sites','messages','sessions','chat','settings','logs'])nav(page);
  assert.equal(d.querySelectorAll('nav [aria-current=page]').length,1);pass('all seven pages navigate with one current marker');
  nav('sites');assert.equal($('site-rows').children.length,8);assert.equal($('site-rows').children[0].children[1].textContent,'DeadSimpleChat');assert.equal($('site-rows').textContent.match(/LOCKED/g).length,7);assert.equal($('home-progress').textContent,'2 / 8');
  $('read-plan').click();await waitFor(()=>!$('plan-content').hidden&&settled(),'read exact plan');assert.ok($('plan-content').textContent.includes('DS-DIAG-v1'));pass('saved order, seven locks and exact provider plan shown without unlock action');
  nav('messages');const script='First reply\nবাংলা দ্বিতীয় reply\n<img src=x onerror=alert(1)>';
  const file=new w.File([script],'sequence.txt',{type:'text/plain'});Object.defineProperty($('script-file'),'files',{value:[file],configurable:true});$('script-file').dispatchEvent(new w.Event('change',{bubbles:true}));
  await waitFor(()=>$('script-count').textContent==='3 LINES'&&settled(),'UTF8 upload');assert.equal($('script-preview').querySelectorAll('li').length,3);assert.equal($('script-preview').querySelector('img'),null);pass('one UTF-8 TXT upload validates, ordered lines are text-safe');
  $('local-start').click();await waitFor(()=>$('local-status').textContent==='WAITING FOR INPUT'&&settled(),'start local test');assert.equal($('local-counter').textContent,'0 / 3 lines');
  $('user-message').value='My first local input';submit('message-form');await waitFor(()=>$('local-counter').textContent==='1 / 3 lines'&&settled(),'first line');assert.equal(d.querySelector('#test-chat .bot p').textContent,'First reply');pass('explicit Start waits; first input consumes only line one');
  $('user-message').value='My second input';$('user-message').dispatchEvent(new w.KeyboardEvent('keydown',{key:'Enter',bubbles:true,cancelable:true}));await waitFor(()=>$('local-counter').textContent==='2 / 3 lines'&&settled(),'Enter sends next line');
  assert.equal(d.querySelectorAll('#test-chat .bot p')[1].textContent,'বাংলা দ্বিতীয় reply');pass('Enter progresses exactly one next line with Unicode preserved');
  $('local-stop').click();await waitFor(()=>$('local-status').textContent==='STOPPED'&&settled(),'Stop');assert.equal($('send-message').disabled,true);
  $('local-start').click();await waitFor(()=>$('local-status').textContent==='WAITING FOR INPUT'&&settled(),'Resume');
  $('user-message').value='Third input';submit('message-form');await waitFor(()=>$('local-status').textContent==='LOCAL COMPLETE'&&settled(),'EOF');assert.equal($('send-message').disabled,true);assert.equal($('test-chat').querySelector('img'),null);pass('Stop/Resume and EOF retain cursor without HTML execution');
  nav('chat');assert.equal(d.querySelectorAll('#observed-chat .bot').length,3);assert.equal($('chat-generated').textContent,'3');assert.ok($('page-chat').textContent.includes('NOT TESTED'));pass('read-only observer mirrors local transcript, never claims API/peer delivery');
  nav('messages');$('local-reset').click();await waitFor(()=>$('local-status').textContent==='READY'&&settled(),'Reset');assert.equal($('local-counter').textContent,'0 / 3 lines');assert.equal($('test-chat').querySelectorAll('.bot').length,0);pass('Reset restores line one without auto-start');
  $('local-start').click();await waitFor(()=>$('local-status').textContent==='WAITING FOR INPUT'&&settled(),'restart');discardNextMessage=true;
  $('user-message').value='Retry synthetic input';submit('message-form');await waitFor(()=>$('send-message').textContent==='Retry same event'&&settled(),'uncertain response');$('send-message').click();await waitFor(()=>$('send-message').textContent==='Send →'&&$('local-counter').textContent==='1 / 3 lines'&&settled(),'retry once');
  assert.equal(w.eval('selected.duplicates'),1);assert.equal(d.querySelectorAll('#test-chat .bot').length,1);pass('discarded real local response retries same event; no extra TXT line consumed');
  nav('sessions');await waitFor(()=>$('session-rows').textContent.includes('waiting')&&settled(),'session index');const index=await (await fetch(base+'/api/reply-test/sessions',{headers:{Authorization:'Bearer '+token}})).json();assert.equal(index.sessions.length,1);assert.equal('script_preview' in index.sessions[0],false);pass('saved local sessions use metadata-only index with isolated run IDs');
  nav('settings');$('slot-name').value='<img src=x onerror=alert(1)>';submit('slot-form');await waitFor(()=>$('instance-rows').textContent.includes('<img src=')&&settled(),'DS slot create');assert.equal($('instance-rows').querySelector('img'),null);assert.equal($('instance-select').options.length,1);pass('active DS non-secret slot creation is text-safe; no locked-site setup selector');
  assert.equal($('shadow-arm').disabled,true);assert.equal($('register-intent').disabled,true);assert.ok($('setup-blockers').textContent.includes('DS_SHADOW_ENABLED'));pass('missing server setup blocks shadow controls, no browser secret fields');
  $('slot-name').value='UNSAVED DRAFT';$('script-input').value='UNSAVED SCRIPT';$('refresh').click();await waitFor(()=>settled(),'refresh');assert.equal($('slot-name').value,'UNSAVED DRAFT');assert.equal($('script-input').value,'UNSAVED SCRIPT');pass('status polling preserves unsaved form drafts');
  failWorkflow=true;$('refresh').click();await waitFor(()=>$('connection').textContent==='STATUS UNAVAILABLE'&&settled(),'status outage');assert.equal($('local-start').disabled,true);assert.equal($('stop-all').disabled,false);
  $('stop-all').click();await waitFor(()=>!w.eval('stopping')&&settled(),'Stop despite failed status');failWorkflow=false;$('refresh').click();await waitFor(()=>$('connection').textContent==='LOCAL API CONNECTED'&&settled(),'recover status');await waitFor(()=>$('local-status').textContent==='STOPPED','stopped server session');
  assert.equal($('local-counter').textContent,'1 / 3 lines');pass('workflow read outage fails closed but global Stop remains available and stops server session');
  nav('logs');assert.ok($('outcome-log').textContent.includes('not externally delivered'));assert.ok($('receipt-detail').textContent.includes('provider'));assert.ok(!requests.some(item=>item.url.includes('complete-and-next')||item.url.includes('approve-plan')));assert.equal(errors.length,0);pass('bounded outcome logs, honest receipt scope, no queue mutations or DOM errors');
  console.log(`PASS: ${checks} DOM operator workspace + local HTTP checks. Includes one discarded-response and one injected local workflow-outage case; no provider connection.`);
 }finally{if(dom){dom.window.dispatchEvent(new dom.window.Event('pagehide'));await new Promise(r=>setTimeout(r,100));dom.window.close();}if(server){server.kill('SIGTERM');await new Promise(resolve=>server.once('exit',resolve));}await rm(tmp,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
