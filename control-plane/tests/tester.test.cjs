// Dedicated small tester: real local HTTP + jsdom; no provider or rendered browser.
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
const {mkdtemp,rm}=require('node:fs/promises');
const {tmpdir}=require('node:os');
const path=require('node:path');
const {randomUUID}=require('node:crypto');
const {TextDecoder}=require('node:util');
const {JSDOM,VirtualConsole}=require('jsdom');
async function waitFor(predicate,label){const end=Date.now()+8000;while(Date.now()<end){if(predicate())return;await new Promise(resolve=>setTimeout(resolve,25));}throw new Error('Timeout: '+label);}
(async()=>{
 const tmp=await mkdtemp(path.join(tmpdir(),'orbit-reply-lab-'));let server,dom,checks=0;
 try{
  const token='local-ui-test-token';
  server=spawn('python',['-B','app.py','--host','127.0.0.1','--port','0','--db',path.join(tmp,'local.db'),'--home','tester'],{cwd:path.resolve(__dirname,'..'),env:{...process.env,CONTROL_PLANE_TOKEN:token,ORBIT_MINNIT_DIAGNOSTICS:'0',ORBIT_MINNIT_AUTHORIZED:'0'},stdio:['ignore','pipe','pipe']});
  const base=await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(new Error('startup timeout')),8000);server.once('error',reject);server.stdout.on('data',chunk=>{const match=chunk.toString().match(/listening on 127\.0\.0\.1:(\d+)/);if(match){clearTimeout(timeout);resolve('http://127.0.0.1:'+match[1]);}});server.once('exit',()=>{clearTimeout(timeout);reject(new Error('server exited'));});});
  const errors=[],console=new VirtualConsole();console.on('jsdomError',error=>errors.push(error));
  dom=await JSDOM.fromURL(base,{runScripts:'dangerously',resources:'usable',pretendToBeVisual:true,virtualConsole:console,beforeParse(w){w.fetch=(url,options)=>fetch(new URL(url,base),options);w.TextDecoder=TextDecoder;Object.defineProperty(w.crypto,'randomUUID',{value:randomUUID});}});
  const w=dom.window,d=w.document,$=id=>d.getElementById(id);
  const settled=()=>!w.eval('busy')&&!w.eval('polling');
  const submit=id=>$(id).dispatchEvent(new w.SubmitEvent('submit',{bubbles:true,cancelable:true}));
  await waitFor(()=>!$('login').hidden,'operator login');$('token').value=token;submit('login');
  await waitFor(()=>$('login').hidden&&settled(),'login complete');
  assert.ok(d.body.textContent.includes('NO PROVIDER SEND'));assert.equal($('external').textContent,'0');
  checks++;global.console.log('PASS LAB: standalone small dashboard and operator authentication');
  const input=$('script-file');
  Object.defineProperty(input,'files',{value:[new w.File(['\ufeffFirst reply\r\n\r\nবাংলা দ্বিতীয় reply\n<img src=x onerror=alert(1)>'], 'my-replies.txt',{type:'text/plain'})],configurable:true});
  input.dispatchEvent(new w.Event('change'));
  await waitFor(()=>$('total').textContent==='3'&&settled(),'real TXT upload');
  assert.equal($('used').textContent,'0');assert.equal($('script-lines').children.length,3);assert.equal(d.querySelector('#script-lines img'),null);
  checks++;global.console.log('PASS LAB: UTF-8 file upload, blank-line handling, ordered text-safe preview');
  $('start').click();await waitFor(()=>$('test-status').textContent==='WAITING FOR YOUR MESSAGE'&&settled(),'start without auto reply');
  assert.equal($('used').textContent,'0');
  $('user-message').value='Hello from the test user';submit('message-form');
  await waitFor(()=>$('used').textContent==='1'&&settled(),'first local reply');
  assert.equal(d.querySelector('.bubble.bot p').textContent,'First reply');
  checks++;global.console.log('PASS LAB: first user message consumes only TXT line 1');
  $('user-message').value='My next reply';$('user-message').dispatchEvent(new w.KeyboardEvent('keydown',{key:'Enter',bubbles:true,cancelable:true}));
  await waitFor(()=>$('used').textContent==='2'&&settled(),'second local reply');
  assert.equal(d.querySelectorAll('.bubble.bot p')[1].textContent,'বাংলা দ্বিতীয় reply');
  checks++;global.console.log('PASS LAB: Enter sends, next user input advances exactly one line');
  $('stop').click();await waitFor(()=>$('test-status').textContent==='STOPPED'&&settled(),'stop');assert.equal($('send').disabled,true);
  $('start').click();await waitFor(()=>$('test-status').textContent==='WAITING FOR YOUR MESSAGE'&&settled(),'resume');
  $('user-message').value='Final input';submit('message-form');
  await waitFor(()=>$('test-status').textContent==='LOCAL SCRIPT COMPLETE'&&settled(),'end of script');
  assert.equal($('remaining').textContent,'0');assert.equal($('send').disabled,true);assert.equal(d.querySelector('#chat img'),null);
  assert.equal(d.querySelectorAll('.bubble.bot p')[2].textContent,'<img src=x onerror=alert(1)>');
  checks++;global.console.log('PASS LAB: stop/resume, last-line completion and no HTML execution');
  $('reset').click();await waitFor(()=>$('used').textContent==='0'&&settled(),'reset');assert.equal($('test-status').textContent,'READY');assert.equal(d.querySelectorAll('.bubble').length,0);
  $('start').click();await waitFor(()=>$('test-status').textContent==='WAITING FOR YOUR MESSAGE'&&settled(),'fresh run');
  checks++;global.console.log('PASS LAB: explicit reset restores cursor without auto-start');
  await waitFor(()=>$('provider-status').textContent.includes('SETUP BLOCKED'),'sanitized provider preflight');
  assert.ok($('provider-blockers').textContent.includes('DS_ROOM_ID'));
  assert.equal($('shadow-arm').disabled,true);assert.equal($('intent-register').disabled,true);
  checks++;global.console.log('PASS LAB: sanitized provider blockers, disabled shadow controls and no false connected status');
  const id=w.sessionStorage.getItem('orbit-reply-test-session');
  const request=async(route,data)=>{const response=await fetch(base+route,{method:data?'POST':'GET',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},...(data?{body:JSON.stringify(data)}:{})});assert.equal(response.ok,true);return response.json();};
  const state=await request('/api/reply-test/sessions/'+id);
  const body={text:'Out of band local user',event_id:'idempotent-ui-report',run_id:state.run_id};
  await request('/api/reply-test/sessions/'+id+'/message',body);
  await request('/api/reply-test/sessions/'+id+'/message',body);
  await waitFor(()=>$('used').textContent==='1'&&$('duplicates').textContent==='1'&&settled(),'live backend report polling');
  assert.ok($('events').textContent.includes('Local reply 1'));assert.equal($('external').textContent,'0');
  checks++;global.console.log('PASS LAB: real local report refresh and server-side duplicate suppression');
  Object.defineProperty(input,'files',{value:[new w.File(['hello'],'not-txt.csv')],configurable:true});input.dispatchEvent(new w.Event('change'));
  await waitFor(()=>$('notice').textContent.includes('Choose a .txt')&&settled(),'wrong file refused');assert.equal($('total').textContent,'3');
  checks++;global.console.log('PASS LAB: invalid file rejected without replacing current session');
  assert.deepEqual(errors,[]);checks++;global.console.log('PASS LAB: no DOM/JavaScript errors');
  global.console.log(`PASS: ${checks} DOM reply-lab + local HTTP checks. No provider connection or external delivery.`);
 }finally{
  if(dom){dom.window.dispatchEvent(new dom.window.Event('pagehide'));dom.window.close();}
  if(server&&server.exitCode===null){const closed=new Promise(resolve=>server.once('close',resolve));server.kill('SIGTERM');await closed;}
  await rm(tmp,{recursive:true,force:true});
 }
})().catch(error=>{global.console.error(error);process.exitCode=1;});
