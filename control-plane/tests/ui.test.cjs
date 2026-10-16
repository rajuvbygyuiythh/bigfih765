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
    server=spawn('python',['-B','app.py','--host','127.0.0.1','--port','0','--home','operations','--db',path.join(directory,'test.db')],{cwd:path.resolve(__dirname,'..'),env:{...process.env,CONTROL_PLANE_TOKEN:'ui-test-only-token',ORBIT_MINNIT_DIAGNOSTICS:'0',ORBIT_MINNIT_AUTHORIZED:'0'},stdio:['ignore','pipe','pipe']});
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
    d.querySelector('[data-view=research]').click();
    await waitFor(()=>$('research-view').classList.contains('hidden')===false&&d.querySelectorAll('.research-card').length===12,'research navigation');
    for(const card of d.querySelectorAll('.research-card')) {assert.equal(card.querySelectorAll('.gate-list li').length,12);assert.ok(card.textContent.includes('not a success probability'));assert.ok(card.querySelectorAll('.research-sources a').length>=1);}
    checks++;console.log('PASS UI: source-backed research cards and explicit progress meaning');
    await waitFor(()=>$('fixture-input').value.includes('chat_message'),'Minnit fixture load');
    $('inspect-fixture').click();await waitFor(()=>$('fixture-output').textContent.includes('offline_contract_check'),'Minnit fixture inspected');
    let inspected=JSON.parse($('fixture-output').textContent);assert.equal(inspected.messages_sent,0);assert.equal(inspected.events[0].kind,'message');
    checks++;console.log('PASS UI: Minnit offline contract inspection');
    $('fixture-platform').value='deadsimplechat';$('fixture-platform').dispatchEvent(new w.Event('change'));$('inspect-fixture').click();
    await waitFor(()=>$('fixture-output').textContent.includes('button_action'),'DSC fixture inspected');
    inspected=JSON.parse($('fixture-output').textContent);assert.equal(inspected.external_requests,0);assert.equal('text' in inspected.events[0],false);
    checks++;console.log('PASS UI: DSC action distinguished from bot-authored question');
    const invalid=JSON.parse($('fixture-input').value);invalid.expected_room_id='wrong-room';$('fixture-input').value=JSON.stringify(invalid);$('inspect-fixture').click();
    await waitFor(()=>$('fixture-output').textContent.includes('Unexpected room ID'),'scope rejection');
    $('fixture-input').value='{broken';$('inspect-fixture').click();await waitFor(()=>$('fixture-output').textContent.startsWith('Rejected:'),'invalid JSON rejected');
    checks++;console.log('PASS UI: contract workbench rejects wrong-room and malformed input');
    assert.equal($('adapter').options.length,13);
    for(const id of ['chatzy','chitchat','joingy','isexychat']) assert.equal(Array.from($('adapter').options).find(o=>o.value===id).disabled,true);
    assert.equal($('research-count').textContent,'12');
    checks++;console.log('PASS UI: shared registry with 12 tracked sites and blocked reference options');
    $('research-search').value='Chatiw';$('research-search').dispatchEvent(new w.Event('input'));
    assert.equal(d.querySelectorAll('.research-card').length,1);
    d.querySelector('.research-card[data-platform=chatiw] .secondary').click();
    await waitFor(()=>$('create-dialog').open,'site-specific config dialog');
    assert.equal($('adapter').value,'chatiw');
    const configCount=Number($('configured').textContent);submit('create-form');
    await waitFor(()=>Number($('configured').textContent)===configCount+1,'new Chatiw configuration');
    const inactive=cards().find(c=>c.querySelector('h3').textContent==='Chatiw workspace');
    assert.equal(inactive.querySelector('.start').disabled,true);
    checks++;console.log('PASS UI: research search -> add inactive site configuration');
    d.querySelector('[data-view=research]').click();$('research-search').value='';$('research-search').dispatchEvent(new w.Event('input'));
    $('research-filter').value='contract';$('research-filter').dispatchEvent(new w.Event('change'));assert.equal(d.querySelectorAll('.research-card').length,4);
    $('research-filter').value='needs_contract';$('research-filter').dispatchEvent(new w.Event('change'));assert.equal(d.querySelectorAll('.research-card').length,4);
    $('research-filter').value='restricted';$('research-filter').dispatchEvent(new w.Event('change'));assert.equal(d.querySelectorAll('.research-card').length,1);assert.equal(d.querySelector('.research-card .secondary').disabled,true);assert.equal(d.querySelector('.research-progress strong').textContent,'N/A');
    $('research-filter').value='reference';$('research-filter').dispatchEvent(new w.Event('change'));assert.equal(d.querySelectorAll('.research-card').length,3);
    for(const card of d.querySelectorAll('.research-card')) assert.equal(card.querySelector('.secondary').disabled,true);
    $('research-filter').value='all';$('research-filter').dispatchEvent(new w.Event('change'));
    checks++;console.log('PASS UI: phase filters and restricted/reference entries cannot activate');
    assert.equal($('fixture-platform').options.length,4);
    $('fixture-platform').value='rumbletalk';$('fixture-platform').dispatchEvent(new w.Event('change'));$('inspect-fixture').click();
    await waitFor(()=>$('fixture-output').textContent.includes('history_record'),'RumbleTalk snapshot');
    inspected=JSON.parse($('fixture-output').textContent);assert.equal(inspected.external_requests,0);assert.equal(inspected.events[0].room_scope_verified,false);
    checks++;console.log('PASS UI: RumbleTalk local history snapshot, not a live webhook');
    $('fixture-platform').value='chatwee';$('fixture-platform').dispatchEvent(new w.Event('change'));$('inspect-fixture').click();
    await waitFor(()=>$('fixture-output').textContent.includes('sso_session_shape'),'Chatwee SSO shape');
    inspected=JSON.parse($('fixture-output').textContent);assert.equal(inspected.events[0].session_value_redacted,true);assert.equal(inspected.events[0].is_chat_message,false);assert.ok(!$('fixture-output').textContent.includes('SYNTHETIC-SESSION-NOT-A-REAL-CREDENTIAL'));
    checks++;console.log('PASS UI: Chatwee session result is redacted and not a chat message');
    d.querySelector('[data-view=diagnostics]').click();
    await waitFor(()=>$('diagnostic-badge').textContent==='UNCONFIGURED','diagnostics fail-closed status');
    assert.equal($('diagnostics-view').classList.contains('hidden'),false);
    assert.equal($('diagnostic-controls').querySelector('button').disabled,true);
    assert.ok($('diagnostic-blockers').textContent.includes('CONTROL_PLANE_TOKEN'));
    assert.ok($('diagnostic-deliveries').textContent.includes('No messages sent'));
    checks++;console.log('PASS UI: diagnostic view exposes configuration blockers without enabling send');

    // UI-only injected responses; real local HTTP pipeline is covered in Python.
    const realFetch=w.fetch, approvals=[];
    let armed=false, deliveryStatus='pending';
    const deliveryId='synthetic-delivery', diagnosticRun='synthetic-run';
    w.fetch=async(url,options={})=>{
      if(url==='/api/diagnostics/minnit/arm'){armed=true;return {ok:true,json:async()=>({armed:true})};}
      if(url==='/api/diagnostics/minnit/disarm'){armed=false;deliveryStatus='cancelled';return {ok:true,json:async()=>({armed:false})};}
      if(url===`/api/diagnostics/minnit/deliveries/${deliveryId}/approve`){approvals.push(JSON.parse(options.body));deliveryStatus='api_accepted';return {ok:true,json:async()=>({status:'api_accepted'})};}
      if(url==='/api/diagnostics/minnit') return {ok:true,json:async()=>({configured:true,armed,run_id:diagnosticRun,expires_at:Date.now()/1000+900,blockers:[],reply:'[Orbit diagnostic bot] pong - requested test only.'})};
      if(url==='/api/diagnostics/minnit/deliveries') return {ok:true,json:async()=>({deliveries:[{id:deliveryId,status:deliveryStatus,run_id:diagnosticRun,event_at:Date.now()/1000,peer_delivery:'unverified',http_status:deliveryStatus==='api_accepted'?200:null}]})};
      return realFetch(url,options);
    };
    await w.refresh();
    assert.equal($('diagnostic-badge').textContent,'DISARMED');
    $('diagnostic-controls').querySelector('button').click();
    await waitFor(()=>$('diagnostic-badge').textContent.startsWith('ARMED'),'synthetic UI arm');
    const approvalButton=$('diagnostic-deliveries').querySelector('button');
    assert.equal(approvalButton.disabled,false);approvalButton.click();
    await waitFor(()=>$('diagnostic-deliveries').querySelector('strong').textContent==='api_accepted','synthetic UI approval');
    assert.equal(approvals.length,1);assert.deepEqual(approvals[0],{run_id:diagnosticRun});
    assert.equal($('diagnostic-deliveries').querySelector('button').disabled,true);
    assert.ok($('diagnostic-deliveries').textContent.includes('peer delivery: unverified'));
    checks++;console.log('PASS UI: synthetic-response arm -> one fixed approval -> no retry control');
    $('diagnostic-controls').querySelectorAll('button')[1].click();
    await waitFor(()=>$('diagnostic-badge').textContent==='DISARMED','synthetic UI disarm');
    assert.equal($('diagnostic-deliveries').querySelector('button').disabled,true);
    w.fetch=realFetch;
    checks++;console.log('PASS UI: disarm removes pending approval eligibility (injected responses)');
    d.querySelector('[data-view=queue]').click();
    await waitFor(()=>d.querySelectorAll('.queue-card').length===12,'locked queue cards');
    assert.equal($('queue-view').classList.contains('hidden'),false);
    const queueCards=Array.from(d.querySelectorAll('.queue-card'));
    assert.equal(queueCards.filter(c=>c.querySelector('.badge').textContent==='UNLOCKED · ACTIVE').length,1);
    assert.equal(queueCards.filter(c=>c.querySelector('.badge').textContent==='LOCKED').length,7);
    assert.ok($('queue-active').textContent.includes('DeadSimpleChat'));
    assert.ok(d.querySelector('.queue-card[data-site=deadsimplechat]').textContent.includes('25%'));
    checks++;console.log('PASS UI: one active target, seven locked targets and protected reference cards');
    const complete=Array.from(d.querySelectorAll('.queue-card[data-site=deadsimplechat] button')).find(b=>b.textContent==='Complete site & unlock next');
    assert.equal(complete.disabled,true);
    assert.ok($('queue-blockers').textContent.includes('eight'));
    assert.equal(d.querySelector('.queue-card[data-site=minnit] button'),null);
    checks++;console.log('PASS UI: incomplete completion blocked; locked sites have no unlock/skip control');
    const activeCard=d.querySelector('.queue-card[data-site=deadsimplechat]');
    assert.ok(activeCard.textContent.includes('Plan: approved'));
    const approvePlan=Array.from(activeCard.querySelectorAll('button')).find(b=>b.textContent==='Approve exact plan');
    assert.equal(approvePlan,undefined); // Owner already approved via chat; reading is not a new approval.
    const readPlanButton=Array.from(activeCard.querySelectorAll('button')).find(b=>b.textContent==='Read scope plan');
    readPlanButton.click();
    await waitFor(()=>$('queue-plan').textContent.includes('DS-DIAG-v1'),'proposed scope plan displayed');
    await waitFor(()=>readPlanButton.getAttribute('aria-busy')==='false','read-plan action including refresh settled');
    assert.ok($('queue-plan').textContent.includes('OWNER APPROVAL REQUIRED'));
    assert.ok(!d.querySelector('.queue-card[data-site=deadsimplechat]').textContent.includes('readiness: green'));
    checks++;console.log('PASS UI: read approved plan; still no provider GREEN or next unlock');
    assert.deepEqual(errors,[]);checks++;console.log('PASS UI: no JavaScript/DOM execution errors');
    console.log(`PASS: ${checks} DOM + local HTTP integration checks. No real browser or third-party chat test.`);
  } finally {
    if(dom) dom.window.close();
    if(server&&server.exitCode===null){const closed=new Promise(resolve=>server.once('close',resolve));server.kill('SIGTERM');await closed;}
    await rm(directory,{recursive:true,force:true});
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
