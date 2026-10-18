const $ = id => document.getElementById(id);
let state, deleting;
let uploading=false, dragDepth=0;
let modifierLabel='Alt / Option';
async function platformLabels() {
  const {os}=await chrome.runtime.getPlatformInfo();
  modifierLabel=os==='mac' ? 'Option ⌥' : 'Alt';
  document.querySelectorAll('[data-modifier]').forEach(el=>{el.textContent=modifierLabel;});
  $('gesture').options[0].textContent=modifierLabel;
  $('gesture').options[1].textContent=modifierLabel+' + Shift';
}
const catalogs = {codex:[],claude:[]};
const effortLabels={none:'无额外推理（none）',minimal:'最低（minimal）',low:'低（low）',medium:'中等（medium）',high:'高（high）',xhigh:'很高（xhigh）',max:'最高（max）'};
function effortPicker(value=$('codex-effort').value) {
  const model=catalogs.codex.find(m=>m.id===modelValue('codex'));
  const levels=model ? model.efforts : ['low','medium','high','xhigh','max'];
  const select=$('codex-effort');
  const defaultLabel=model?.default_effort ? `自动（目录默认：${effortLabels[model.default_effort]}）` : '自动（CLI / 服务默认）';
  select.replaceChildren(new Option(defaultLabel,''));
  for(const effort of levels || []) select.add(new Option(effortLabels[effort],effort));
  const invalid=value && !(levels || []).includes(value);
  if(invalid) select.add(new Option(`原设置 ${value} 当前不受支持，请重新选择`,value));
  select.value=value;
  select.setCustomValidity(invalid?'请选择当前模型支持的推理强度，或选择自动。':'');
  $('effort-note').textContent=invalid ? '模型已变化：请重新选择推理强度后保存。' : model ? '手动选择会明确传给 CLI；自动不指定强度。' : '自动模型、自定义模型或列表未加载：显示通用档位，具体支持情况由 CLI 校验。';
}
function modelValue(provider) {
  const value=$(provider+'-model').value;
  return value==='__custom__' ? $(provider+'-model-custom').value.trim() : value;
}
function customVisibility(provider) {
  const custom=$(provider+'-model').value==='__custom__';
  $(provider+'-custom-label').hidden=!custom;
  $(provider+'-model-custom').required=custom;
}
function modelPicker(provider,value,custom=false) {
  const select=$(provider+'-model');
  select.replaceChildren(new Option('自动（CLI 默认）',''));
  for(const model of catalogs[provider]) select.add(new Option(model.name,model.id));
  select.add(new Option('自定义模型…','__custom__'));
  const known=catalogs[provider].some(model=>model.id===value);
  select.value=custom || (value && !known) ? '__custom__' : value;
  $(provider+'-model-custom').value=value;
  customVisibility(provider);
  if(provider==='codex') effortPicker();
}
async function refreshModels() {
  $('refresh-models').disabled=true;
  try {
    await Promise.all(['codex','claude'].map(async provider=>{
      const note=$(provider+'-model-status'); note.textContent='正在读取模型列表…';
      try {
        const result=await rpc('models',{provider});
        // Read the current input after the request: don't overwrite edits made while loading.
        const value=modelValue(provider);
        const custom=$(provider+'-model').value==='__custom__' && !value;
        catalogs[provider]=result.models;
        modelPicker(provider,value,custom);
        note.textContent=result.message;
      } catch(e) { note.textContent='读取失败：'+e.message+' 已保留当前选择。'; }
    }));
  } finally { $('refresh-models').disabled=false; }
}
const ALL_SITES = ['https://*/*','http://*/*'];
function status(text,error=false) { $('status').textContent=text; $('status').className=error?'error':''; }
async function rpc(op,payload={}) {
  const r=await chrome.runtime.sendMessage({op,payload});
  if (!r?.ok) throw new Error(r?.error?.message || '无法连接本地桥接。请运行 python3 scripts/install.py，随后刷新此页。');
  return r.data;
}
function text(tag,value,parent,cls) { const e=document.createElement(tag); e.textContent=value; if(cls)e.className=cls; parent.append(e); return e; }
function render(next) {
  state=next;
  const select=$('courses'); select.replaceChildren(new Option('不使用课程资料',''));
  for(const c of state.courses) select.add(new Option(c.name,c.id));
  select.value=state.settings.active_course || '';
  $('rename').disabled=$('delete-course').disabled=!select.value;
  uploadControls();
  $('documents').replaceChildren();
  for(const d of state.documents.filter(d=>d.course===select.value)) {
    const row=document.createElement('div'); row.className='document'; $('documents').append(row);
    const content=document.createElement('div'); row.append(content);
    text('strong',d.name,content);
    text('p',d.status==='ready'?`已导入 · ${d.chunks} 个本地索引片段`:'导入失败',content,'small');
    for(const warning of d.warnings) text('p',warning,content,'small');
    const remove=text('button','移除',row); remove.onclick=()=>act(async()=>{render(await rpc('document_remove',{id:d.id})); status('资料及索引已移除。');});
  }
  if(!state.documents.some(d=>d.course===select.value)) text('p',select.value?'尚未导入资料。也可以直接使用通用知识问答。':'选择或创建课程后导入资料。',$('documents'),'small');
}
async function act(fn) { try { await fn(); } catch(e) { status(e.message,true); } }
async function refresh() {
  render(await rpc('state'));
  $('primary').value=state.settings.primary; $('fallback').checked=state.settings.fallback;
  $('timeout').value=state.settings.timeout;
  $('answer-instructions').value=state.settings.answer_instructions || '';
  $('reset-instructions').disabled=!state.defaults?.answer_instructions;
  for(const provider of ['codex','claude']) modelPicker(provider,state.settings[provider+'_model']);
  effortPicker(state.settings.codex_effort || '');
  const p=await chrome.storage.local.get(['gesture','theme']); $('gesture').value=p.gesture || 'alt'; $('theme').value=p.theme || 'auto';
  status('本地桥接已连接。');
  if(!$('refresh-models').disabled) void refreshModels();
}
async function sites() {
  const {origins=[]}=await chrome.permissions.getAll(); $('sites').replaceChildren();
  const allGranted=ALL_SITES.every(origin=>origins.includes(origin));
  $('all-sites').disabled=allGranted;
  $('all-sites').textContent=allGranted?'已授权所有网站':'授权所有网站';
  for(const origin of origins) {
    const label=origin==='https://*/*'?'所有 HTTPS 网站':origin==='http://*/*'?'所有 HTTP 网站':origin;
    const item=text('li',label,$('sites')); const remove=text('button','撤销',item);
    remove.onclick=()=>act(async()=>{await chrome.permissions.remove({origins:[origin]}); await sites(); status('权限已撤销；请刷新已打开的题目页。');});
  }
}
$('site-form').onsubmit=e=>{
  e.preventDefault();
  let origin;
  try {
    const u=new URL($('site').value);
    if(!['https:','http:'].includes(u.protocol)) throw new Error('请输入 HTTP 或 HTTPS 网站。');
    origin=u.origin+'/*';
  } catch(error) { status(error.message,true); return; }
  // Request exactly the chosen origin, directly in the user gesture.
  const request=chrome.permissions.request({origins:[origin]});
  act(async()=>{
    if(!await request) throw new Error('网站授权未授予。');
    await rpc('origins_sync'); await sites(); status(`网站已授权，请刷新题目页后按住 ${modifierLabel} 拖选文字。`);
  });
};
$('all-sites').onclick=()=>{
  // Broad access is optional and requested only by this explicit button click.
  const request=chrome.permissions.request({origins:ALL_SITES});
  act(async()=>{
    if(!await request) throw new Error('全部网站授权未授予；已有网站授权保持有效。');
    await rpc('origins_sync'); await sites();
    status(`已授权所有 HTTP / HTTPS 网站。请刷新要使用的网页，再按住 ${modifierLabel} 拖选；可在下方撤销授权。`);
  });
};
$('course-form').onsubmit=e=>{e.preventDefault(); act(async()=>{render(await rpc('course_create',{name:$('course-name').value})); $('course-name').value=''; status('课程已创建并设为当前课程。');});};
$('courses').onchange=()=>act(async()=>{render(await rpc('course_select',{id:$('courses').value || null})); status('已切换课程，请重新划词；旧请求已取消。');});
$('rename').onclick=()=>{
  const c=state?.courses.find(c=>c.id===state.settings.active_course); if(!c)return;
  const name=prompt('新的课程名称',c.name); if(name)act(async()=>{render(await rpc('course_rename',{id:c.id,name})); status('已重命名。');});
};
$('delete-course').onclick=()=>{deleting=state.settings.active_course; $('confirm-delete').hidden=false;};
$('keep-course').onclick=()=>{$('confirm-delete').hidden=true;};
$('confirm-delete-course').onclick=()=>act(async()=>{render(await rpc('course_delete',{id:deleting})); $('confirm-delete').hidden=true; status('课程及资料索引已删除。');});
$('reset-instructions').onclick=()=>{
  $('answer-instructions').value=state.defaults.answer_instructions;
  status('已填入默认回答要求，点击“保存设置”后生效。');
};
$('settings-form').onsubmit=e=>{e.preventDefault();act(async()=>{
  await rpc('settings',{primary:$('primary').value,fallback:$('fallback').checked,timeout:Number($('timeout').value),answer_instructions:$('answer-instructions').value,codex_model:modelValue('codex'),claude_model:modelValue('claude'),codex_effort:$('codex-effort').value});
  await chrome.storage.local.set({gesture:$('gesture').value,theme:$('theme').value}); status('设置已保存。');
});};
function uploadControls() {
  const disabled=uploading || !state?.settings.active_course;
  $('files').disabled=disabled;
  $('drop-zone').setAttribute('aria-disabled',String(disabled));
  $('drop-zone').setAttribute('aria-busy',String(uploading));
  $('drop-hint').textContent=uploading?'正在导入，请稍候…':disabled?'请先选择或创建课程。':'支持一次拖入多个文件；PDF、PPTX、TXT、MD，每个最多 30 MB。';
}
async function importFiles(files) {
  if(uploading)throw new Error('正在导入资料，请完成后再添加。');
  const course=state?.settings.active_course; if(!course)throw new Error('请先选择课程。');
  if(!files.length)throw new Error('请拖入文件，暂不支持文件夹或网页链接。');
  uploading=true; uploadControls(); $('progress').hidden=false;
  const errors=[];
  try {
    for(const file of files) {
      let token;
      try {
        if(!/\.(pdf|pptx|txt|md)$/i.test(file.name))throw new Error('不支持此格式。支持 PDF、PPTX、TXT、MD。');
        if(!file.size || file.size>30*1024*1024)throw new Error('文件为空或超过 30 MB。');
        status(`正在上传 ${file.name}…`); $('progress').value=0;
        token=(await rpc('upload_begin',{course,name:file.name,size:file.size})).token;
        for(let offset=0;offset<file.size;offset+=192*1024) {
          const bytes=new Uint8Array(await file.slice(offset,offset+192*1024).arrayBuffer());
          let binary=''; for(const byte of bytes)binary+=String.fromCharCode(byte);
          await rpc('upload_chunk',{token,offset,data:btoa(binary)});
          $('progress').value=Math.round((offset+bytes.length)/file.size*100);
        }
        status(`正在解析 ${file.name}…`); render(await rpc('upload_finish',{token})); token=null;
      } catch(e) {
        errors.push(`${file.name}：${e.message}`);
        if(token)try{await rpc('upload_abort',{token});}catch{}
      }
    }
    render(await rpc('state'));
    status(errors.length?errors.join('\n'):'资料已导入。重新划词即可使用当前课程资料。',!!errors.length);
  } finally { uploading=false; $('files').value=''; uploadControls(); $('progress').hidden=true; }
}
$('files').onchange=()=>{const files=[...$('files').files]; if(files.length)void act(()=>importFiles(files));};
const dropZone=$('drop-zone');
const hasFiles=e=>Array.from(e.dataTransfer?.types || []).includes('Files');
function clearDrag(){dragDepth=0;dropZone.classList.remove('drag-over');}
dropZone.addEventListener('dragenter',e=>{
  if(!hasFiles(e))return;
  e.preventDefault(); dragDepth++;
  if(!uploading && state?.settings.active_course)dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragover',e=>{
  if(!hasFiles(e))return;
  e.preventDefault(); e.dataTransfer.dropEffect=uploading || !state?.settings.active_course?'none':'copy';
});
dropZone.addEventListener('dragleave',e=>{if(hasFiles(e) && --dragDepth<=0)clearDrag();});
dropZone.addEventListener('drop',e=>{
  e.preventDefault(); clearDrag();
  const items=Array.from(e.dataTransfer?.items || []);
  if(items.some(item=>item.webkitGetAsEntry?.()?.isDirectory)){
    status('暂不支持拖入文件夹，请打开文件夹后选择其中的资料。',true); return;
  }
  const files=Array.from(e.dataTransfer?.files || []);
  void act(()=>importFiles(files));
});
// Prevent dropped files outside the import area from replacing the settings page.
document.addEventListener('dragover',e=>{if(hasFiles(e)){e.preventDefault();if(!dropZone.contains(e.target))e.dataTransfer.dropEffect='none';}});
document.addEventListener('drop',e=>{if(hasFiles(e)){e.preventDefault();clearDrag();if(!dropZone.contains(e.target))status('请把文件拖到“课程资料”的导入区域。',true);}});
window.addEventListener('blur',clearDrag);
$('check').onclick=()=>act(async()=>{
  $('check').disabled=true; status('正在检测 CLI 的安装、参数能力与登录状态…');
  try {
    const providers=await rpc('providers'); $('providers').replaceChildren();
    for(const p of providers)text('p',`${p.provider} · ${p.message} · ${p.version || '无版本'}\n${p.path || ''}\n认证：${p.authentication}`,$('providers'),'small');
    status('检测完成。真实调用状态请在题目浮层或最近诊断中查看。');
  } finally { $('check').disabled=false; }
});
for(const provider of ['codex','claude']) $(provider+'-model').onchange=()=>{customVisibility(provider);if(provider==='codex')effortPicker();};
$('codex-model-custom').oninput=()=>effortPicker();
$('codex-effort').onchange=()=>effortPicker();
$('refresh-models').onclick=()=>void refreshModels();
$('refresh').onclick=()=>act(refresh);
$('diagnostics').onclick=()=>act(async()=>{ $('diagnostic-output').hidden=false; $('diagnostic-output').textContent=JSON.stringify(await rpc('diagnostics'),null,2); });
$('extension-id').textContent=`扩展 ID：${chrome.runtime.id}`;
act(async()=>{await platformLabels();await sites();await refresh();});
