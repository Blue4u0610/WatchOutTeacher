(() => {
  if (globalThis.__courseAssist) return;
  globalThis.__courseAssist = true;
  let port, gesture, card, shadow, range, requestId, sequence = 0, dismissGesture, positionFrame;
  let prefs = {gesture: 'alt', theme: 'auto'};
  let pageURL = location.href;
  const selector = '.question, [data-testid="question"], [data-testid="question-container"], [data-question-id], .assessment-question, fieldset';
  function connect() {
    if (port) return port;
    port = chrome.runtime.connect({name: 'course-content'});
    port.onMessage.addListener(msg => {
      if (msg.kind === 'prefs') { prefs = msg.data; return; }
      if (msg.kind === 'invalidate') { close(); return; }
      if (msg.id !== requestId || !card || location.href !== pageURL || !range?.startContainer.isConnected) return;
      if (!msg.ok) showError(msg.error?.message || '本地程序连接失败，请打开设置检查。');
      else showResult(msg.data);
    });
    port.onDisconnect.addListener(() => {
      void chrome.runtime.lastError;
      port = null;
      if (card) showError('本地连接已断开。请在设置中检查连接，然后重新划词。');
    });
    return port;
  }
  function inside(e) { return card && e.composedPath().includes(card); }
  function editable(e) {
    return e.composedPath().some(n => n instanceof Element && (n.matches('input, textarea, select, [role="textbox"]') || n.isContentEditable));
  }
  function close() {
    sequence++; dismissGesture = null;
    cancelAnimationFrame(positionFrame); positionFrame = null;
    if (requestId && port) { try { port.postMessage({op: 'cancel', id: requestId}); } catch {} }
    requestId = null; range = null; card?.remove(); card = shadow = null;
  }
  function el(tag, text, parent, cls) {
    const e = document.createElement(tag); if (text !== undefined) e.textContent = text;
    if (cls) e.className = cls; parent?.append(e); return e;
  }
  function position() {
    if (!card || !range) return;
    const r = range.getBoundingClientRect();
    const v = window.visualViewport;
    const left = v?.offsetLeft || 0, top = v?.offsetTop || 0;
    const w = v?.width || innerWidth, h = v?.height || innerHeight;
    card.style.setProperty('max-width', `${Math.max(80, w - 16)}px`, 'important');
    card.style.setProperty('max-height', `${Math.max(40, h - 16)}px`, 'important');
    const b = card.getBoundingClientRect();
    const node = range.commonAncestorContainer;
    const container = (node.nodeType === 1 ? node : node.parentElement)?.closest(selector);
    const bounds = container?.getBoundingClientRect();
    const controls = container ? [...container.querySelectorAll('input,textarea,select,button')].map(e => (e.closest('label') || e).getBoundingClientRect()) : [];
    const safeX = Math.max(left + 8, Math.min(r.left, left + w - b.width - 8));
    const candidates = [
      {x:safeX,y:r.bottom+7}, {x:safeX,y:r.top-b.height-7},
      {x:r.right+8,y:r.top}, {x:r.left-b.width-8,y:r.top},
      ...(bounds ? [{x:safeX,y:bounds.bottom+8},{x:safeX,y:bounds.top-b.height-8}] : [])
    ];
    const overlaps = (p,q) => p.x < q.right && p.x+b.width > q.left && p.y < q.bottom && p.y+b.height > q.top;
    const chosen = candidates.find(p => p.x>=left+8 && p.y>=top+8 && p.x+b.width<=left+w-8 && p.y+b.height<=top+h-8 && ![r,...controls].some(q=>overlaps(p,q)));
    const x = chosen?.x ?? safeX;
    const y = chosen?.y ?? Math.max(top+8,Math.min(r.bottom+7,top+h-b.height-8));
    card.style.setProperty('left', `${x}px`, 'important');
    card.style.setProperty('top', `${y}px`, 'important');
  }
  function schedulePosition(e) {
    if (!card || (e && inside(e)) || positionFrame) return;
    positionFrame = requestAnimationFrame(() => { positionFrame = null; position(); });
  }
  function createCard(r) {
    range = r;
    card = document.createElement('course-assist-card');
    card.style.cssText = 'all:initial!important;position:fixed!important;z-index:2147483647!important;display:block!important;width:max-content!important;overflow:auto!important;color-scheme:light dark!important;';
    shadow = card.attachShadow({mode: 'closed'});
    const style = el('style', undefined, shadow);
    style.textContent = `:host{font:13px/1.5 -apple-system,BlinkMacSystemFont,system-ui,sans-serif!important;--bg:#fbfbf9;--fg:#242824;--muted:#596259;--border:#cdd2cc} @media(prefers-color-scheme:dark){:host{--bg:#252925;--fg:#f0f2ec;--muted:#bac3b7;--border:#566052}} :host([data-theme=light]){--bg:#fbfbf9;--fg:#242824;--muted:#596259;--border:#cdd2cc}:host([data-theme=dark]){--bg:#252925;--fg:#f0f2ec;--muted:#bac3b7;--border:#566052} *{box-sizing:border-box} .box{position:relative;min-width:94px;background:var(--bg);color:var(--fg);border:1px solid var(--border);border-radius:7px;box-shadow:0 2px 8px #0002;max-width:360px;padding:9px 12px;overflow-wrap:anywhere;white-space:pre-wrap} button{font:inherit;color:inherit;background:transparent;border:0;padding:0;text-align:left;cursor:pointer} .answer{display:block;width:100%;user-select:text;-webkit-user-select:text;cursor:text}.toggle-row{display:flex;justify-content:flex-end;margin-top:3px}.expand{display:flex;align-items:center;justify-content:center;width:24px;height:20px;border-radius:4px;user-select:none}.expand:hover{background:var(--border)}.expand:focus-visible{outline:2px solid var(--muted);outline-offset:1px}.chevron{display:block;width:7px;height:7px;border-right:1.7px solid currentColor;border-bottom:1.7px solid currentColor;transform:rotate(45deg);margin-top:-4px}.expand[aria-expanded=true] .chevron{transform:rotate(225deg);margin-top:4px} .details{border-top:1px solid var(--border);margin-top:9px;padding-top:8px;max-width:340px} h4{font-size:12px;margin:8px 0 3px} p{margin:3px 0} .muted{color:var(--muted);font-size:11px} .copy{margin-top:9px;text-decoration:underline} [hidden]{display:none!important}`;
    card.dataset.theme = prefs.theme || 'auto';
    document.documentElement.append(card);
    const box = el('div', undefined, shadow, 'box');
    box.setAttribute('aria-live', 'polite');
    el('div', '正在查阅…', box, 'body');
    position();
  }
  function body() { const b = shadow?.querySelector('.body'); if (b) b.replaceChildren(); return b; }
  function showError(message) { if (!card) return; el('p', message, body()); position(); }
  function showResult(result) {
    const b = body(); if (!b) return;
    el('div', result.answer, b, 'answer');
    const detail = el('div', undefined, b, 'details'); detail.hidden = true; detail.id = 'answer-details';
    el('h4', 'Answer', detail); el('p', result.answer, detail);
    el('h4', 'Explanation', detail); el('p', result.explanation_en, detail);
    el('h4', 'Sources', detail);
    if (!result.sources?.length) el('p', '未引用课程资料。', detail, 'muted');
    for (const s of result.sources || []) el('p', `${s.document} · ${s.kind === 'slide' ? '幻灯片' : s.kind === 'page' ? 'PDF 文件页' : '文本分段'} ${s.page_or_slide}`, detail, 'muted');
    const labels = {course_material:'依据课程资料',general_knowledge:'依据通用知识',mixed:'课程资料 + 通用知识',insufficient:'信息不足'};
    el('p', labels[result.basis] || result.basis, detail, 'muted');
    if (result.needs_more_context) el('p', '上下文可能不完整，请补选题干与所有选项。', detail, 'muted');
    for (const warning of result.warnings || []) el('p', warning, detail, 'muted');
    const d = result.diagnostics || {};
    el('p', `${d.provider || ''}${d.fallback_reason ? ` · 回退：${d.fallback_reason}` : ''}`, detail, 'muted');
    if (d.retrieval) el('p', `资料片段：${d.retrieval.selected}/${d.retrieval.total}；本题仅使用所选片段。`, detail, 'muted');
    const copy = el('button', '复制', detail, 'copy');
    copy.onclick = async () => { try { await navigator.clipboard.writeText(`${result.answer}\n\n${result.explanation_en}\n${(result.sources || []).map(s => `${s.document} (${s.page_or_slide})`).join('\n')}`); copy.textContent = '已复制'; } catch { copy.textContent = '请选中文字复制'; } };
    const row = el('div', undefined, b, 'toggle-row');
    const toggle = el('button', undefined, row, 'expand'); toggle.type = 'button';
    toggle.setAttribute('aria-label', '展开解释'); toggle.setAttribute('aria-expanded', 'false'); toggle.setAttribute('aria-controls', detail.id);
    const chevron = el('span', undefined, toggle, 'chevron'); chevron.setAttribute('aria-hidden', 'true');
    toggle.onclick = () => {
      detail.hidden = !detail.hidden; toggle.setAttribute('aria-expanded', String(!detail.hidden));
      toggle.setAttribute('aria-label', detail.hidden ? '展开解释' : '收起解释'); position();
    };
    position();
  }
  function extract(selection) {
    const node = range.commonAncestorContainer;
    const ancestor = node.nodeType === 1 ? node : node.parentElement;
    const container = ancestor?.closest(selector);
    let context = selection, complete = false, warnings = [];
    if (container && container.contains(range.startContainer) && container.contains(range.endContainer)) {
      const clone = container.cloneNode(true);
      clone.querySelectorAll('script, style, input, textarea, select, button, [contenteditable], [hidden], [aria-hidden="true"]').forEach(n => n.remove());
      clone.querySelectorAll('p, div, li, label, pre, tr, h1, h2, h3, h4, br').forEach(n => n.append(document.createTextNode('\n')));
      const text = clone.textContent || '';
      if (text.trim() && text.length <= 16000) { context = text.trim(); complete = true; }
      else warnings.push('题目容器过长，仅发送选区。');
      if (container.querySelector('img, canvas, svg, math, .MathJax')) warnings.push('题目含图片或公式；仅提取可读文本，可能缺失视觉信息。');
    }
    if (!complete) warnings.push('未可靠识别整题；选项可能不完整。');
    return {selection, context, context_complete: complete, warnings};
  }
  document.addEventListener('pointerdown', e => {
    if (!e.isTrusted || e.button !== 0) return;
    dismissGesture = null;
    if (inside(e)) return;
    gesture = null;
    const modifier = prefs.gesture === 'alt-shift' ? e.altKey && e.shiftKey : e.altKey;
    if (modifier && !editable(e)) {
      close();
      // Start fresh even when dragging the same text again; avoid native text dragging
      // and Shift extending the previous question's selection.
      getSelection()?.removeAllRanges();
      gesture = {x:e.clientX,y:e.clientY,pointer:e.pointerId,url:location.href};
    } else if (card) dismissGesture = {pointer:e.pointerId,generation:sequence};
  }, true);
  document.addEventListener('pointerup', e => {
    if (e.button !== 0) return;
    const dismiss = dismissGesture; dismissGesture = null;
    if (dismiss && dismiss.pointer === e.pointerId && !inside(e)) {
      setTimeout(() => {
        if (!card || dismiss.generation !== sequence) return;
        const s = getSelection();
        const selected = s?.rangeCount ? s.getRangeAt(0) : null;
        const same = selected && range && selected.startContainer === range.startContainer && selected.startOffset === range.startOffset && selected.endContainer === range.endContainer && selected.endOffset === range.endOffset;
        if (!selected || s.isCollapsed || !same) close();
      }, 0);
    }
    const g = gesture; gesture = null;
    if (!g || e.button !== 0 || e.pointerId !== g.pointer || inside(e) || editable(e) || Math.hypot(e.clientX-g.x,e.clientY-g.y) < 3) return;
    const generation = sequence;
    setTimeout(() => {
      if (generation !== sequence || location.href !== g.url) return;
      const s = getSelection(); const text = s?.toString().trim();
      if (!text || !s.rangeCount || s.isCollapsed) return;
      const r = s.getRangeAt(0).cloneRange(); createCard(r);
      if (text.length > 8000) { showError('选区超过 8,000 字符，请只选当前题目。'); return; }
      pageURL = location.href; requestId = crypto.randomUUID();
      try { connect().postMessage({id:requestId,op:'ask',payload:extract(text)}); }
      catch { showError('扩展连接失效，请刷新页面后重试。'); }
    }, 0);
  }, true);
  document.addEventListener('pointercancel', () => { gesture = null; dismissGesture = null; }, true);
  // Keep the answer anchored and visible during page scroll, nested scroll and zoom.
  window.addEventListener('scroll', schedulePosition, true);
  window.addEventListener('resize', schedulePosition);
  window.visualViewport?.addEventListener('resize', schedulePosition);
  window.visualViewport?.addEventListener('scroll', schedulePosition);
  window.addEventListener('pagehide', () => { close(); port?.disconnect(); });
  setInterval(() => {
    if (location.href !== pageURL) { close(); pageURL = location.href; }
    if (range && (!range.startContainer.isConnected || !range.endContainer.isConnected)) close();
  }, 250);
  try { connect(); } catch {}
})();
