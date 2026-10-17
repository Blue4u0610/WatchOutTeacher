const HOST = 'com.courseassist.bridge';
let native, pending = new Map();
const clients = new Set();
async function prefs() { return {gesture:'alt',theme:'auto',...(await chrome.storage.local.get(['gesture','theme']))}; }
function nativePort() {
  if (native) return native;
  const p = chrome.runtime.connectNative(HOST); native = p;
  p.onMessage.addListener(msg => {
    const fn = pending.get(msg.id); if (fn) { pending.delete(msg.id); fn(msg); }
  });
  p.onDisconnect.addListener(() => {
    const technical = chrome.runtime.lastError?.message || 'connection closed';
    const message = `本地桥接已断开（${technical}）。请在设置中重连，然后重新划词。`;
    if (native === p) native = null;
    for (const [id, fn] of pending) fn({id,ok:false,error:{code:'disconnected',message}});
    pending.clear();
  });
  return p;
}
function rpc(op, payload, done) {
  const id = crypto.randomUUID();
  pending.set(id, done);
  try { nativePort().postMessage({id,op,payload}); }
  catch(e) { pending.delete(id); done({id,ok:false,error:{message:e.message}}); }
  return id;
}
function cancel(id) { if (!id) return; pending.delete(id); try { native?.postMessage({id:crypto.randomUUID(),op:'cancel',payload:{target:id}}); } catch {} }
chrome.runtime.onConnect.addListener(port => {
  if (port.name !== 'course-content' || port.sender?.id !== chrome.runtime.id || !port.sender.tab) return;
  let current, localId, closed = false;
  clients.add(port);
  prefs().then(data => { try { port.postMessage({kind:'prefs',data}); } catch {} });
  const send = msg => { if (!closed) try { port.postMessage(msg); } catch {} };
  port.onMessage.addListener(async msg => {
    if (msg.op === 'cancel') { if (msg.id === localId) { cancel(current); current = localId = null; } return; }
    if (msg.op !== 'ask' || typeof msg.id !== 'string') return;
    cancel(current); localId = msg.id; const expected = localId;
    let origin;
    try { origin = new URL(port.sender.url).origin; } catch { return; }
    if (!await chrome.permissions.contains({origins:[origin+'/*']})) { send({id:expected,ok:false,error:{message:'请先在设置中授权当前网站。'}}); return; }
    if (closed || localId !== expected) return;
    const {selection,context,context_complete,warnings} = msg.payload || {};
    if (typeof selection !== 'string' || selection.length > 8000 || typeof context !== 'string' || context.length > 16000) return;
    current = rpc('ask',{selection,context,context_complete:!!context_complete,warnings:Array.isArray(warnings)?warnings.slice(0,4).map(x=>String(x).slice(0,200)):[]}, result => {
      if (localId === expected) { current = null; send({...result,id:expected}); }
    });
  });
  port.onDisconnect.addListener(() => { closed = true; cancel(current); clients.delete(port); });
});
const management = new Set(['state','course_create','course_rename','course_delete','course_select','document_remove','upload_begin','upload_chunk','upload_finish','upload_abort','settings','providers','models','diagnostics']);
chrome.runtime.onMessage.addListener((msg,sender,respond) => {
  if (sender.id !== chrome.runtime.id || sender.url !== chrome.runtime.getURL('options.html')) return;
  if (msg.op === 'origins_sync') { syncScripts().then(()=>respond({ok:true}),e=>respond({ok:false,error:{message:e.message}})); return true; }
  if (!management.has(msg.op)) return;
  if (['course_create','course_select','course_delete','document_remove','settings'].includes(msg.op)) {
    for (const p of clients) try { p.postMessage({kind:'invalidate'}); } catch {}
  }
  rpc(msg.op,msg.payload || {},respond); return true;
});
let syncQueue = Promise.resolve();
function syncScripts() {
  syncQueue = syncQueue.catch(() => {}).then(async () => {
  const {origins=[]} = await chrome.permissions.getAll();
  const matches = origins.filter(x => /^https?:/.test(x));
  await chrome.scripting.unregisterContentScripts();
  if (matches.length) await chrome.scripting.registerContentScripts([{id:'course-assist',matches,js:['content.js'],runAt:'document_idle',allFrames:true,persistAcrossSessions:true}]);
  });
  return syncQueue;
}
chrome.permissions.onAdded.addListener(syncScripts);
chrome.permissions.onRemoved.addListener(syncScripts);
chrome.runtime.onInstalled.addListener(syncScripts);
chrome.runtime.onStartup.addListener(syncScripts);
chrome.action.onClicked.addListener(()=>chrome.runtime.openOptionsPage());
chrome.storage.onChanged.addListener(async () => { const data=await prefs(); for(const p of clients) try{p.postMessage({kind:'prefs',data});}catch{} });
