import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import http from 'node:http';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
const root=path.resolve(import.meta.dirname,'..');
const live=process.argv.includes('--live');
const profile=await fs.mkdtemp(path.join(os.tmpdir(),'course-browser-'));
const resultDir=path.join(root,'test-results'); await fs.mkdir(resultDir,{recursive:true});
const manifest=JSON.parse(await fs.readFile(path.join(root,'extension/manifest.json'),'utf8'));
const eid=[...crypto.createHash('sha256').update(Buffer.from(manifest.key,'base64')).digest('hex').slice(0,32)].map(x=>String.fromCharCode(97+parseInt(x,16))).join('');
const runtime=path.join(profile,'runtime');
await fs.cp(path.join(root,'bridge'),path.join(runtime,'bridge'),{recursive:true});
await fs.mkdir(path.join(runtime,'extension'));await fs.copyFile(path.join(root,'extension/manifest.json'),path.join(runtime,'extension/manifest.json'));
await fs.mkdir(path.join(runtime,'tests'));await fs.copyFile(path.join(root,'tests/mock_host.py'),path.join(runtime,'tests/mock_host.py'));
const testExtension=path.join(profile,'extension');
await fs.cp(path.join(root,'extension'),testExtension,{recursive:true});
// Headless Chromium cannot accept native optional-permission prompts. Only fixture origins
// are pre-granted in this disposable test copy; shipped manifest has zero host permissions.
await fs.writeFile(path.join(testExtension,'manifest.json'),JSON.stringify({...manifest,host_permissions:['http://localhost/*','http://127.0.0.1/*']}));
const win=process.platform==='win32';
// Use a unique test host name: Windows registration is per-user, not per-profile.
const hostName='com.courseassist.test.h'+crypto.randomBytes(8).toString('hex');
const background=path.join(testExtension,'background.js');
await fs.writeFile(background,(await fs.readFile(background,'utf8')).replaceAll('com.courseassist.bridge',hostName));
const installedPython=path.join(os.homedir(),'Library/Application Support/CourseAssist/runtime/.venv/bin/python');
const hasInstalledPython=!win && await fs.access(installedPython).then(()=>true,()=>false);
const python=process.env.COURSE_ASSIST_TEST_PYTHON || (hasInstalledPython ? installedPython : path.join(root,'.venv',win?'Scripts/python.exe':'bin/python'));
execFileSync(python,[path.join(root,'tests/make_fixtures.py'),resultDir],{env:{...process.env,PYTHONUTF8:'1'}});
const hostManifest=path.join(profile,'NativeMessagingHosts',hostName+'.json');
const setupScript=path.join(root,'tests/native_fixture.py');
execFileSync(python,[setupScript,'install',profile,hostName,eid,live?'live':'mock'],{env:{...process.env,PYTHONUTF8:'1'}});
const server=http.createServer(async(req,res)=>{try{const file=path.basename(new URL(req.url,'http://localhost').pathname)||'fixture.html';if(!['fixture.html','frame.html'].includes(file))throw Error();res.setHeader('Content-Type','text/html; charset=utf-8');res.end((await fs.readFile(path.join(root,'tests',file),'utf8')).replaceAll(':8765',':'+server.address().port));}catch{res.writeHead(404).end();}});
await new Promise(resolve=>server.listen(0,resolve));
const port=server.address().port;
const results=[];
let context;
function pass(name){results.push(name);console.log('PASS',name);}
async function waitFor(fn,timeout=7000) {const start=Date.now();let last;while(Date.now()-start<timeout){try{last=await fn();if(last)return last;}catch(e){last=e;}await new Promise(r=>setTimeout(r,100));}throw Error('Timed out: '+String(last));}
try {
 context=await chromium.launchPersistentContext(profile,{channel:'chromium',headless:true,viewport:{width:1100,height:900},args:[`--disable-extensions-except=${testExtension}`,`--load-extension=${testExtension}`]});
 const worker=context.serviceWorkers()[0]||await context.waitForEvent('serviceworker');
 const opts=await context.newPage();
 await opts.goto(`chrome-extension://${eid}/options.html`);
 await waitFor(async()=> (await opts.locator('#status').textContent()).includes('已连接'));
 pass('real extension → Native Messaging → isolated host connection');
 assert.equal(await opts.locator('#gesture option[value=alt]').textContent(),process.platform==='darwin'?'Option ⌥':'Alt');
 pass('platform-specific modifier labels');
 const rpc=(op,payload={})=>opts.evaluate(async ({op,payload})=>await chrome.runtime.sendMessage({op,payload}),{op,payload});
 if(!live){
   await waitFor(async()=> !(await opts.locator('#refresh-models').isDisabled()));
   await opts.locator('#codex-model').selectOption('test-model');
   await opts.locator('#settings-form button:not([type="button"])').click();
   await waitFor(async()=> (await rpc('state')).data.settings.codex_model==='test-model');
   await opts.reload();
   await waitFor(async()=> !(await opts.locator('#refresh-models').isDisabled()) && await opts.locator('#codex-model').inputValue()==='test-model');
   pass('CLI catalog dropdown persists selected model across reload');
   assert.deepEqual(await opts.locator('#codex-effort option').evaluateAll(nodes=>nodes.map(n=>n.value)),['','low','medium','high']);
   await opts.locator('#codex-effort').selectOption('high');
   await opts.locator('#settings-form button:not([type="button"])').click();
   await waitFor(async()=> (await rpc('state')).data.settings.codex_effort==='high');
   await opts.reload();
   await waitFor(async()=> !(await opts.locator('#refresh-models').isDisabled()) && await opts.locator('#codex-effort').inputValue()==='high');
   pass('model-supported effort choices persist across reload');
   await opts.locator('#codex-model').selectOption('');
   await opts.locator('#codex-effort').selectOption('max');
   await opts.locator('#codex-model').selectOption('test-model');
   assert.equal(await opts.locator('#codex-effort').evaluate(el=>el.checkValidity()),false);
   assert.equal(await opts.locator('#codex-effort').inputValue(),'max');
   await opts.locator('#codex-effort').selectOption('high');
   assert.equal(await opts.locator('#codex-effort').evaluate(el=>el.checkValidity()),true);
   pass('model switch blocks unsupported effort without silently changing it');
   await opts.locator('#codex-model').selectOption('__custom__');
   await opts.locator('#codex-model-custom').fill('future-custom-model');
   await opts.locator('#settings-form button:not([type="button"])').click();
   await waitFor(async()=> (await rpc('state')).data.settings.codex_model==='future-custom-model');
   await opts.reload();
   await waitFor(async()=> !(await opts.locator('#refresh-models').isDisabled()) && await opts.locator('#codex-model-custom').inputValue()==='future-custom-model');
   assert.equal(await opts.locator('#codex-model').inputValue(),'__custom__');
   assert(await opts.locator('#codex-model-custom').isVisible());
   await opts.locator('#refresh-models').click();
   await waitFor(async()=> !(await opts.locator('#refresh-models').isDisabled()));
   assert.equal(await opts.locator('#codex-model-custom').inputValue(),'future-custom-model');
   pass('custom model retained across reload and catalog refresh');
   await opts.locator('#codex-model').selectOption('');
   await opts.locator('#settings-form button:not([type="button"])').click();
   await waitFor(async()=> (await rpc('state')).data.settings.codex_model==='');
 }
 await opts.screenshot({path:path.join(resultDir,'model-settings.png'),fullPage:true});
 await opts.setViewportSize({width:375,height:812});
 await opts.screenshot({path:path.join(resultDir,'settings-mobile.png'),fullPage:true});
 await opts.setViewportSize({width:1100,height:900});
 // Exercise settings UI with fixture origins pre-granted in this test copy.
 await opts.locator('#site').fill(`http://localhost:${port}`); await opts.locator('#site-form button').click();
 await waitFor(async()=> (await opts.locator('#status').textContent()).includes('网站已授权'));
 await opts.locator('#site').fill(`http://127.0.0.1:${port}`); await opts.locator('#site-form button').click();
 await waitFor(async()=> (await opts.locator('#sites').textContent()).includes('127.0.0.1'));
 pass('site settings + dynamic injection (fixture origins pre-granted for headless test)');
 await opts.locator('#course-name').fill('Lumen test course');await opts.locator('#course-form button').click();
 await waitFor(async()=> (await opts.locator('#status').textContent()).includes('课程已创建'));
 await opts.locator('#files').setInputFiles(live ? [path.join(resultDir,'material.pdf'),path.join(resultDir,'material.pptx')] : path.join(root,'tests/material.md'));
 await waitFor(async()=> (await opts.locator('#status').textContent()).includes('资料已导入'));
 pass('settings UI course creation + chunked document import');
 const page=await context.newPage();await page.goto(`http://localhost:${port}/fixture.html`);
 const session=await context.newCDPSession(page);
 async function cardText() {
   const {root:dom}=await session.send('DOM.getDocument',{depth:-1,pierce:true});
   function find(n){if(n.nodeName==='COURSE-ASSIST-CARD')return n;for(const ch of [...(n.children||[]),...(n.shadowRoots||[])]){const r=find(ch);if(r)return r;}}
   function text(n){return (n.nodeName==='STYLE'?'':(n.nodeValue||'')+(n.children||[]).map(text).join('')+(n.shadowRoots||[]).map(text).join(''));}
   const card=find(dom);return card?text(card):'';
 }
 async function shadowBox(cls) {
   const {root:dom}=await session.send('DOM.getDocument',{depth:-1,pierce:true});
   function find(n,inCard=false){
     inCard ||= n.nodeName==='COURSE-ASSIST-CARD';
     const attrs=n.attributes||[];const i=attrs.indexOf('class');
     if(inCard && i>=0 && attrs[i+1].split(' ').includes(cls))return n;
     for(const child of [...(n.children||[]),...(n.shadowRoots||[])]){const found=find(child,inCard);if(found)return found;}
   }
   const n=find(dom);assert(n,cls);
   const {model}=await session.send('DOM.getBoxModel',{nodeId:n.nodeId});
   const q=model.border;return {x:q[0],y:q[1],width:q[2]-q[0],height:q[7]-q[1]};
 }
 async function toggleDetails(){const b=await shadowBox('expand');await page.mouse.click(b.x+b.width/2,b.y+b.height/2);}
 async function dismiss(){await page.mouse.click(5,5);await waitFor(async()=>await page.locator('course-assist-card').count()===0);}
 async function chromeSetting(gesture){await opts.evaluate(async gesture=>chrome.storage.local.set({gesture}),gesture);await page.waitForTimeout(100);}
 async function select(selector,alt=true,releaseEarly=false,target=page) {
   const loc=target.locator(selector);await loc.scrollIntoViewIfNeeded();
   const r=await loc.evaluate(e=>{const range=document.createRange();range.selectNodeContents(e);const rects=[...range.getClientRects()];const a=rects[0],b=rects.at(-1);return {x:a.x,y:a.y+a.height/2,endX:b.right,endY:b.y+b.height/2};});
   // Frame local coordinates converted through the iframe element for mouse input.
   let ox=0,oy=0;
   if(target!==page){const frameEl=await target.frameElement();const b=await frameEl.boundingBox();ox=b.x+1;oy=b.y+1;}
   if(alt)await page.keyboard.down('Alt');
   await page.mouse.move(ox+r.x+1,oy+r.y);await page.mouse.down();
   await page.mouse.move(ox+r.endX-1,oy+r.endY,{steps:14});
   if(releaseEarly && alt)await page.keyboard.up('Alt');
   await page.mouse.up();if(alt&&!releaseEarly)await page.keyboard.up('Alt');
 }
 await select('#q1',false);await page.waitForTimeout(300);assert.equal(await page.locator('course-assist-card').count(),0);pass('normal selection sends no request');
 await select('#editable');await page.waitForTimeout(200);assert.equal(await page.locator('course-assist-card').count(),0);pass('editable region excluded');
 const before=(await rpc('diagnostics')).data.length;
 await select('#q1',true,true);
 await waitFor(async()=> (await cardText()).includes('B — 4'),live?100000:8000);
 const text1=await cardText();
 const rect=await page.locator('course-assist-card').boundingBox();const qr=await page.locator('#q1').boundingBox();
 assert(Math.abs(rect.y-qr.y)<150);assert(rect.x>=0 && rect.x+rect.width<=1100);
 const diag=(await rpc('diagnostics')).data; assert.equal(diag.length,before+1);assert.equal(diag[0].code,'ok');
 if(!live){assert.equal(JSON.parse(diag[0].details).requested_effort,'high');pass('saved effort reaches answer provider and diagnostics');}
 pass(`${live?'LIVE CODEX':'MOCK'} Alt/Option drag → actual native host → answer B — 4 near selection; exactly one request; modifier released before mouseup`);
 const ab=await shadowBox('answer');
 await page.mouse.click(ab.x+5,ab.y+ab.height/2);
 assert.equal((await page.locator('course-assist-card').boundingBox()).height,rect.height);
 await page.mouse.move(ab.x+1,ab.y+ab.height/2);await page.mouse.down();await page.mouse.move(ab.x+ab.width-1,ab.y+ab.height/2,{steps:10});await page.mouse.up();
 assert.equal(await page.evaluate(()=>getSelection().toString().trim()),'B — 4');
 assert.equal((await page.locator('course-assist-card').boundingBox()).height,rect.height);
 pass('answer click does not expand; native drag selects answer text for copying');
 await page.keyboard.press('Escape');assert.equal(await page.locator('course-assist-card').count(),1);pass('Esc preserves answer');
 await toggleDetails();
 await page.screenshot({path:path.join(resultDir,live?'live-answer.png':'mock-answer.png')});
 const expanded=await cardText();assert(expanded.includes('Explanation'));
 const expandedRect=await page.locator('course-assist-card').boundingBox();assert(expandedRect.height>rect.height+60);
 pass('bottom-right chevron expands English explanation');
 await toggleDetails();assert.equal((await page.locator('course-assist-card').boundingBox()).height,rect.height);pass('chevron collapses without dismissing answer');
 await dismiss();
 await select('#q2');await waitFor(async()=> (await cardText()).includes('Violet'),live?100000:8000);
 const text2=await cardText();if(live){assert(/material\.(pdf|pptx)/.test(text2));assert(/(PDF 文件页|幻灯片) 2/.test(text2));}else{assert(text2.includes('material.md'));assert(text2.includes('文本分段'));}pass(`${live?'LIVE CODEX':'MOCK'} imported material changes answer; source points to supplied document/chunk`);
 const rb=await page.locator('course-assist-card').boundingBox();await toggleDetails();assert((await page.locator('course-assist-card').boundingBox()).height>rb.height+60);
 await page.screenshot({path:path.join(resultDir,live?'live-source.png':'mock-source.png')});
 await dismiss();pass('outside left click clearing selection closes');
 assert.equal(await page.locator('input:checked').count(),0);pass('no option selected or submitted');
 if(!live){
   await select('#q1');await select('#q2');await waitFor(async()=> (await cardText()).includes('Violet'));await page.waitForTimeout(900);assert(!(await cardText()).includes('B — 4'));pass('rapid replacement never shows old result');
   await dismiss();await select('#q1');await dismiss();await page.waitForTimeout(1100);assert.equal(await page.locator('course-assist-card').count(),0);pass('late result after cancellation never reopens');
   await select('#q1');await page.evaluate(()=>history.pushState({},'', '#changed'));await page.waitForTimeout(1100);assert.equal(await page.locator('course-assist-card').count(),0);pass('SPA route change cancels and suppresses late result');
   await select('#q1');await page.mouse.move(10,400);await page.mouse.wheel(0,100);await waitFor(async()=> (await cardText()).includes('B — 4'));assert.equal(await page.locator('course-assist-card').count(),1);pass('scroll during loading preserves request and answer');
   await page.mouse.wheel(0,200);await page.waitForTimeout(150);assert.equal(await page.locator('course-assist-card').count(),1);
   const scrolled=await page.locator('course-assist-card').boundingBox();assert(scrolled.y>=0&&scrolled.y+scrolled.height<=900);pass('scroll after answer preserves visible overlay');
   await page.mouse.click(10,400,{button:'right'});await page.keyboard.press('Escape');assert.equal(await page.locator('course-assist-card').count(),1);
   await page.mouse.click(10,400,{button:'middle'});assert.equal(await page.locator('course-assist-card').count(),1);pass('outside right and middle clicks preserve answer');
   await page.setViewportSize({width:900,height:700});await page.waitForTimeout(150);assert.equal(await page.locator('course-assist-card').count(),1);await page.setViewportSize({width:1100,height:900});pass('resize keeps answer');
   await dismiss();
   await select('#edge');await waitFor(async()=> (await cardText()).includes('B — 4'));const edge=await page.locator('course-assist-card').boundingBox();assert(edge.x>=0&&edge.y>=0&&edge.x+edge.width<=1100&&edge.y+edge.height<=900);pass('viewport-edge positioning');await dismiss();
   await page.evaluate(()=>{document.body.style.zoom='1.25';document.body.classList.add('dark');});await page.emulateMedia({colorScheme:'dark'});
   await select('#q1');await waitFor(async()=> (await cardText()).includes('B — 4'));const zoom=await page.locator('course-assist-card').boundingBox();assert(zoom.x>=0 && zoom.y>=0 && zoom.x+zoom.width<=1100);await page.screenshot({path:path.join(resultDir,'dark-zoom.png')});pass('125% page CSS zoom and dark system theme');await dismiss();
   await page.evaluate(()=>{document.body.style.zoom='1';document.body.classList.remove('dark');});
   for(const frame of page.frames().filter(f=>f.url().includes('frame.html'))){
     const fe=await frame.frameElement();await fe.scrollIntoViewIfNeeded();await select('#frame-question',true,false,frame);
     await waitFor(async()=>await frame.locator('course-assist-card').count());await page.waitForTimeout(600);
     const b=await frame.locator('course-assist-card').boundingBox();const fb=await fe.boundingBox();assert(b.x>=fb.x&&b.x+b.width<=fb.x+fb.width);pass(`frame-local overlay: ${new URL(frame.url()).hostname}`);await page.mouse.click(fb.x+5,fb.y+5);await waitFor(async()=>await frame.locator('course-assist-card').count()===0);
   }
   await page.reload();
   await page.evaluate(()=>{const p=document.createElement('p');p.id='long';p.textContent='Long question text. '.repeat(450);p.style.cssText='position:fixed;top:60px;left:40px;width:950px;font:8px/10px monospace;z-index:10;background:white';document.body.append(p);});
   const nBefore=(await rpc('diagnostics')).data.length;await select('#long');await waitFor(async()=>(await cardText()).includes('8,000'));assert.equal((await rpc('diagnostics')).data.length,nBefore);pass('oversized multiline selection is rejected without calling provider');await dismiss();await page.evaluate(()=>document.querySelector('#long').remove());
   await chromeSetting('alt-shift');await select('#q1');await page.waitForTimeout(200);assert.equal(await page.locator('course-assist-card').count(),0);
   await page.keyboard.down('Shift');await select('#q1');await page.keyboard.up('Shift');await waitFor(async()=>(await cardText()).includes('B — 4'));pass('configurable Alt/Option + Shift gesture');await dismiss();await chromeSetting('alt');
   await select('#q1');await rpc('course_create',{name:'Empty course'});await page.waitForTimeout(900);assert.equal(await page.locator('course-assist-card').count(),0);pass('course change cancels pending answer and closes overlay');
   await select('#q1');await page.waitForTimeout(80);const pid=Number(await fs.readFile(path.join(profile,'host.pid'),'utf8'));process.kill(pid,'SIGKILL');await waitFor(async()=>(await cardText()).includes('本地桥接已断开'));pass('native host disconnect shows an actionable error');await dismiss();assert((await rpc('state')).ok);pass('native reconnect succeeds');
   await page.reload();await select('#q1');await page.waitForTimeout(80);await page.reload();await page.waitForTimeout(900);assert.equal(await page.locator('course-assist-card').count(),0);pass('reload disconnects old request');
 }
 const finalDiag=(await rpc('diagnostics')).data;
 await fs.writeFile(path.join(resultDir,live?'live-results.json':'browser-results.json'),JSON.stringify({mode:live?'LIVE CODEX':'MOCK PROVIDER',date:new Date().toISOString(),browser:context.browser()?.version(),passed:results,diagnostics:finalDiag},null,2));
 console.log(`Completed ${results.length} checks (${live?'LIVE':'MOCK'}).`);
} catch(e){if(context){for(const p of context.pages().slice(-1))await p.screenshot({path:path.join(resultDir,'failure.png')}).catch(()=>{});}throw e;}
finally{
 if(context)await context.close();
 server.close();
 execFileSync(python,[setupScript,'uninstall',profile,hostName,eid,live?'live':'mock']);
 await fs.rm(profile,{recursive:true,force:true,maxRetries:10,retryDelay:200});
}
