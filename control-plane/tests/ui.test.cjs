// DOM + real local HTTP integration. Not a rendering/real-browser test.
const assert = require('node:assert/strict');
const {spawn} = require('node:child_process');
const {mkdtemp, rm} = require('node:fs/promises');
const {tmpdir} = require('node:os');
const path = require('node:path');
const {randomUUID} = require('node:crypto');
const {JSDOM, VirtualConsole} = require('jsdom');

async function waitFor(predicate, message) {
  const end = Date.now() + 8000;
  while(Date.now() < end) {if(predicate()) return; await new Promise(r=>setTimeout(r,25));}
  throw new Error('Timed out: '+message);
}

(async()=>{
  const directory = await mkdtemp(path.join(tmpdir(),'orbit-ui-'));
  let dom, server;
  let checks = 0;
  try {
    server=spawn('python',['-B','app.py','--host','127.0.0.1','--port','0','--db',path.join(directory,'test.db')],{cwd:path.resolve(__dirname,'..'),env:{...process.env,CONTROL_PLANE_TOKEN:'ui-test-only-token'},stdio:['ignore','pipe','pipe']});
    const base=await new Promise((resolve,reject)=>{
      const timeout=setTimeout(()=>reject(new Error('Local test server startup timeout')),8000);
      server.once('error',reject);
      server.stdout.on('data',chunk=>{const match=chunk.toString().match(/listening on 127\.0\.0\.1:(\d+)/); if(match){clearTimeout(timeout);resolve('http://127.0.0.1:'+match[1]);}});
      server.once('exit',()=>{clearTimeout(timeout);reject(new Error('Test server exited before startup'));});
    });
    const errors=[]; const virtualConsole=new VirtualConsole(); virtualConsole.on('jsdomError',e=>errors.push(e));
    dom=await JSDOM.fromURL(base,{resources:'usable',runScripts:'dangerously',pretendToBeVisual:true,virtualConsole,beforeParse(window){
      window.fetch=(url,options)=>fetch(new URL(url,base),options);
      window.confirm=()=>true;
      Object.defineProperty(window.crypto,'randomUUID',{value:randomUUID});
      window.HTMLDialogElement.prototype.showModal=function(){this.open=true;};
      window.HTMLDialogElement.prototype.close=function(){this.open=false;};
    }});
    const w=dom.window,d=w.document,$=id=>d.getElementById(id);
    function submit(id){const form=$(id);form.dispatchEvent(new w.SubmitEvent('submit',{bubbles:true,cancelable:true,submitter:form.querySelector('[type=submit]')}));}
    await waitFor(()=>$('auth-dialog').open,'auth challenge');
    $('operator-token').value='wrong';submit('auth-form');
    await waitFor(()=>$('auth-error').textContent.includes('required'),'wrong token rejected');
    $('operator-token').value='ui-test-only-token';submit('auth-form');
    await waitFor(()=>!$('auth-dialog').open&&$('connection-status').textContent.includes('CONNECTED'),'authenticated UI');
    assert.equal($('configured').textContent,'0');checks++;console.log('PASS UI: operator token authentication');
    async function create(name,adapter='simulator'){
      const before=Number($('configured').textContent);$('add').click();await waitFor(()=>$('create-dialog').open,'create modal');
      $('instance-name').value=name;$('adapter').value=adapter;submit('create-form');
      await waitFor(()=>Number($('configured').textContent)===before+1,'created instance');
    }
    const hostileName='<img src=x onerror=alert(1)>';
    await create(hostileName);
    assert.equal(d.querySelector('.instance-card h3').textContent,hostileName);
    assert.equal(d.querySelector('.instance-card img'),null);checks++;console.log('PASS UI: configuration create and text-only rendering');
    const cards=()=>Array.from(d.querySelectorAll('.instance-card'));
    cards()[0].querySelector('.start').click();
    await waitFor(()=>$('running').textContent==='1'&&cards()[0].querySelector('.badge').textContent==='running','start worker');
    cards()[0].querySelectorAll('.card-controls button')[1].click();
    await waitFor(()=>$('checks').textContent==='1'&&$('logs').textContent.includes('Synthetic event accepted'),'synthetic check and log');checks++;console.log('PASS UI: start, synthetic check and instance log');
    await create('Isolated sandbox');cards()[1].querySelector('.start').click();
    await waitFor(()=>$('running').textContent==='2','second worker');
    assert.equal(cards()[1].querySelector('.delete').disabled,true);
    cards()[0].querySelector('.card-controls button').click();
    await waitFor(()=>$('running').textContent==='1'&&cards()[0].querySelector('.badge').textContent==='stopped','isolated stop');
    assert.equal(cards()[1].querySelector('.badge').textContent,'running');checks++;console.log('PASS UI: two-instance lifecycle isolation');
    $('stop-all').click();await waitFor(()=>$('running').textContent==='0','global stop');
    d.querySelector('[data-filter=running]').click();assert.equal(cards().length,0);assert.equal($('empty').querySelector('h2').textContent,'No matching instances');
    d.querySelector('[data-filter=stopped]').click();assert.equal(cards().length,2);
    $('search').value='Isolated';$('search').dispatchEvent(new w.Event('input'));assert.equal(cards().length,1);
    $('search').value='';$('search').dispatchEvent(new w.Event('input'));checks++;console.log('PASS UI: global stop, filters and search');
    d.querySelector('[data-view=activity]').click();assert.equal($('activity-view').classList.contains('hidden'),false);assert.ok($('audit').textContent.includes('Worker stopped'));
    d.querySelector('[data-view=fleet]').click();cards()[0].querySelector('.delete').click();await waitFor(()=>$('configured').textContent==='1','delete instance');checks++;console.log('PASS UI: activity navigation and stopped-instance deletion');
    await create('Minnit configuration','minnit');const platform=cards().find(c=>c.querySelector('h3').textContent==='Minnit configuration');
    assert.equal(platform.querySelector('.start').disabled,true);assert.ok(platform.textContent.includes('Not connected'));checks++;console.log('PASS UI: unimplemented live adapter cannot start');
    assert.deepEqual(errors,[]);checks++;console.log('PASS UI: no JavaScript/DOM execution errors');
    console.log(`PASS: ${checks} DOM + local HTTP integration checks. No real browser or third-party chat test.`);
  } finally {
    if(dom) dom.window.close();
    if(server&&server.exitCode===null){const closed=new Promise(resolve=>server.once('close',resolve));server.kill('SIGTERM');await closed;}
    await rm(directory,{recursive:true,force:true});
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
