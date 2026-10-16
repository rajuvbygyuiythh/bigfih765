// Plan-first page, default CLI, real local HTTP. No rendered-browser/provider claim.
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
const {mkdtemp,rm}=require('node:fs/promises');
const {tmpdir}=require('node:os');
const path=require('node:path');
const {JSDOM,VirtualConsole}=require('jsdom');
async function waitFor(predicate,label){const end=Date.now()+8000;while(Date.now()<end){if(predicate())return;await new Promise(r=>setTimeout(r,25));}throw new Error('Timeout: '+label);}
(async()=>{
 const tmp=await mkdtemp(path.join(tmpdir(),'orbit-plan-'));let server,dom,checks=0;
 try{
  const token='planning-test-token';
  server=spawn('python',['-B','app.py','--host','127.0.0.1','--port','0','--db',path.join(tmp,'test.db')],{cwd:path.resolve(__dirname,'..'),env:{...process.env,CONTROL_PLANE_TOKEN:token,ORBIT_MINNIT_DIAGNOSTICS:'0',ORBIT_MINNIT_AUTHORIZED:'0',DS_SHADOW_ENABLED:'0'},stdio:['ignore','pipe','pipe']});
  const base=await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(new Error('startup timeout')),8000);server.once('error',reject);server.stdout.on('data',chunk=>{const match=chunk.toString().match(/listening on 127\.0\.0\.1:(\d+)/);if(match){clearTimeout(timeout);resolve('http://127.0.0.1:'+match[1]);}});server.once('exit',()=>{clearTimeout(timeout);reject(new Error('server exited'));});});
  const errors=[],requests=[],vc=new VirtualConsole();vc.on('jsdomError',error=>errors.push(error));
  dom=await JSDOM.fromURL(base,{runScripts:'dangerously',resources:'usable',virtualConsole:vc,beforeParse(w){w.fetch=(url,options)=>{requests.push({url,method:options?.method||'GET'});return fetch(new URL(url,base),options);};}});
  const w=dom.window,d=w.document,$=id=>d.getElementById(id);
  await waitFor(()=>$('plan-status').textContent.includes('Authenticate'),'auth required');
  assert.equal(d.querySelector('h1').textContent,'One site. One finished delivery.');assert.equal($('script-file'),null);assert.equal($('stop-all'),null);
  checks++;console.log('PASS PLAN: CLI default retires previous dashboards and explains plan-only scope');
  function login(value){$('plan-token').value=value;$('plan-auth').dispatchEvent(new w.SubmitEvent('submit',{bubbles:true,cancelable:true}));}
  login('wrong');await waitFor(()=>$('plan-status').textContent.includes('required'),'wrong token rejected');assert.equal($('plan-queue').children.length,0);
  checks++;console.log('PASS PLAN: auth fails closed without exposing saved workflow');
  login(token);await waitFor(()=>$('plan-queue').children.length===8,'actual saved queue');
  const rows=Array.from($('plan-queue').children);assert.equal(rows[0].children[1].textContent,'deadsimplechat');assert.equal(rows[0].children[2].textContent,'ACTIVE');assert.equal(rows[0].children[4].textContent,'25%');assert.equal(rows.filter(row=>row.children[2].textContent==='LOCKED').length,7);
  checks++;console.log('PASS PLAN: actual queue shows active DS 25% and exactly seven locked successors');
  assert.ok(requests.every(request=>request.method==='GET'));assert.equal($('plan-token').value,'');assert.equal(w.localStorage.length,0);assert.equal(w.sessionStorage.length,0);
  checks++;console.log('PASS PLAN: read-only requests, cleared password field and no credential storage');
  for(const route of ['/test','/operations']){const html=await (await fetch(base+route)).text();assert.ok(html.includes('One site. One finished delivery.'));}
  assert.ok((await (await fetch(base+'/legacy/test')).text()).includes('TXT Reply Lab'));
  assert.ok((await (await fetch(base+'/legacy/operations')).text()).includes('id="stop-all"'));
  checks++;console.log('PASS PLAN: old aliases retired; prior implementations preserved in explicit legacy routes');
  assert.equal(errors.length,0);checks++;console.log('PASS PLAN: no JavaScript/DOM errors');
  console.log(`PASS: ${checks} DOM planning + local HTTP checks. No provider connection or UI-design acceptance claimed.`);
 }finally{if(dom){dom.window.dispatchEvent(new dom.window.Event('pagehide'));dom.window.close();}if(server){server.kill('SIGTERM');await new Promise(resolve=>server.once('exit',resolve));}await rm(tmp,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
