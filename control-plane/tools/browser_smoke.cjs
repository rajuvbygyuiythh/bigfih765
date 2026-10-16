// Optional real Chromium verification. Install playwright-core outside source;
// set NODE_PATH and CHROMIUM_EXECUTABLE. Synthetic isolated DB, no provider calls.
const assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
const {mkdtemp,mkdir,rm}=require('node:fs/promises');
const {tmpdir}=require('node:os');
const path=require('node:path');
const {chromium}=require('playwright-core');
(async()=>{
 if(!process.env.CHROMIUM_EXECUTABLE)throw new Error('Set CHROMIUM_EXECUTABLE for optional browser smoke');
 const root=path.resolve(__dirname,'..'),repo=path.resolve(root,'..'),tmp=await mkdtemp(path.join(tmpdir(),'orbit-browser-'));
 let server,browser,checks=0;const token='synthetic-browser-operator-token-only';
 const pass=message=>{checks++;console.log('PASS BROWSER: '+message);};
 try{
  server=spawn('python',['-B','app.py','--host','127.0.0.1','--port','0','--db',path.join(tmp,'test.db')],{cwd:root,env:{...process.env,CONTROL_PLANE_TOKEN:token,DS_SHADOW_ENABLED:'0',DS_AUTHORIZED_ROOM:'0',ORBIT_MINNIT_DIAGNOSTICS:'0',ORBIT_MINNIT_AUTHORIZED:'0'},stdio:['ignore','pipe','pipe']});
  const base=await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(new Error('Server startup timeout')),8000);server.once('error',reject);server.stdout.on('data',chunk=>{const match=String(chunk).match(/listening on 127\.0\.0\.1:(\d+)/);if(match){clearTimeout(timeout);resolve('http://127.0.0.1:'+match[1]);}});server.once('exit',()=>{clearTimeout(timeout);reject(new Error('Server exited'));});});
  browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE,headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--no-zygote','--single-process','--disable-gpu']});
  const context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage(),errors=[],external=[];
  page.on('pageerror',error=>errors.push(String(error)));
  await context.route('**/*',route=>{if(new URL(route.request().url()).origin===base)return route.continue();external.push(route.request().url());return route.abort();});
  await page.goto(base);await page.locator('#auth-banner').waitFor({state:'visible'});
  await page.locator('#operator-token').fill('wrong');await page.locator('#auth-form button').click();await page.waitForFunction(()=>document.querySelector('#notice').textContent.includes('required'));
  await page.locator('#operator-token').fill(token);await page.locator('#auth-form button').click();await page.waitForFunction(()=>document.querySelector('#connection').textContent==='LOCAL API CONNECTED');
  assert.equal(await page.locator('#operator-token').inputValue(),'');pass('actual Chromium authentication; default workspace, token field cleared');
  await page.locator('[data-page="sites"]').click();assert.equal(await page.locator('#site-rows tr').count(),8);assert.equal(await page.locator('#site-rows .badge').filter({hasText:'LOCKED'}).count(),7);assert.equal(await page.locator('#home-progress').textContent(),'2 / 8');
  await page.locator('[data-page="messages"]').focus();await page.keyboard.press('Enter');await page.locator('#page-messages').waitFor({state:'visible'});pass('real queue/locks and keyboard Enter navigation');
  await page.locator('#script-file').setInputFiles({name:'synthetic.txt',mimeType:'text/plain',buffer:Buffer.from('প্রথম local reply\nSecond reply')});
  await page.waitForFunction(()=>document.querySelector('#script-count').textContent==='2 LINES');await page.locator('#local-start').click();await page.waitForFunction(()=>document.querySelector('#local-status').textContent==='WAITING FOR INPUT');
  await page.locator('#user-message').fill('Synthetic local input');await page.locator('#user-message').press('Enter');await page.waitForFunction(()=>document.querySelector('#local-counter').textContent==='1 / 2 lines');assert.equal(await page.locator('#test-chat .bot p').textContent(),'প্রথম local reply');await page.evaluate(()=>document.fonts.ready);assert.equal(await page.evaluate(()=>Array.from(document.fonts).some(face=>face.family==='Orbit Bengali'&&face.status==='loaded')),true);pass('native file upload, Unicode TXT progression and keyboard send');
  await page.locator('#stop-all').click();await page.waitForFunction(()=>document.querySelector('#local-status').textContent==='STOPPED');assert.equal(await page.locator('#send-message').isDisabled(),true);pass('visible global Stop stops real local session without consuming another line');
  await mkdir(path.join(repo,'.runtime'),{recursive:true});await page.screenshot({path:path.join(repo,'.runtime/operator-messages-desktop.png'),fullPage:true});
  for(const width of [1440,390,320]){
   await page.setViewportSize({width,height:1000});
   for(const tab of ['home','sites','messages','sessions','chat','settings','logs']){
    await page.locator(`[data-page="${tab}"]`).click();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`${width}px ${tab} viewport overflow`);
   }
  }
  pass('seven pages at 1440/390/320px without document-level horizontal overflow');
  await page.setViewportSize({width:390,height:844});await page.locator('[data-page="home"]').click();await page.screenshot({path:path.join(repo,'.runtime/operator-home-mobile.png'),fullPage:true});
  await page.locator('[data-page="settings"]').click();assert.equal(await page.locator('#shadow-arm').isDisabled(),true);assert.equal(await page.locator('#register-intent').isDisabled(),true);assert.equal(await page.locator('#page-settings input[type=password]').count(),0);pass('unconfigured shadow remains disabled; no provider credential form');
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);pass('no page exceptions or outbound page requests; Chromium used normal web security/CSP');
  console.log(`PASS: ${checks} BROWSER smoke checks. Synthetic/local only; not full accessibility/security/peer-delivery audit.`);
 }finally{if(browser)await browser.close();if(server){server.kill('SIGTERM');await new Promise(resolve=>server.once('exit',resolve));}await rm(tmp,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
