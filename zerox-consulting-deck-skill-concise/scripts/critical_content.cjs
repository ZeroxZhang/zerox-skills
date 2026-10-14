/* 检查作者声明的少量关键语义；不推断全部业务事实已经覆盖。 */
function inspectSlide(slide) {
  const box = slide.getBoundingClientRect(), sx = box.width / slide.offsetWidth, sy = box.height / slide.offsetHeight;
  const shown = el => {
    if (!el) return false;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) return false;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const s = getComputedStyle(n); if (s.display === 'none' || s.visibility !== 'visible' || Number(s.opacity) === 0 || s.contentVisibility === 'hidden') return false;
    }
    return true;
  };
  const rect = el => { const r = el.getBoundingClientRect(); return {x: (r.left - box.left) / sx, y: (r.top - box.top) / sy, width: r.width / sx, height: r.height / sy}; };
  /* 可见文字：ECharts 的 SSR SVG 会内嵌 <style>，它的 CSS 文本不是图上看得见的内容。
     直接取 textContent 会把这些选择器也算进去（实测 357 字符里大半是 .zr…-cls-0:hover{…}），
     于是"关联对象不完整"这类核对把一份正常页面判成失败。只剥 <style>/<script>，
     其余拼接方式与 textContent 一致。 */
  const visibleText = el => {
    if (!el) return '';
    const parts = [];
    (function walk(node) {
      for (const child of node.childNodes) {
        if (child.nodeType === 3) { if (child.nodeValue.trim()) parts.push(child.nodeValue); continue; }
        if (child.nodeType !== 1) continue;
        const tag = child.tagName.toLowerCase();
        if (tag === 'style' || tag === 'script') continue;
        walk(child);
      }
    })(el);
    return parts.join('');
  };
  return [...slide.querySelectorAll('[data-critical-id]')].map(el => {
    const target = el.getAttribute('data-critical-for'), object = target ? [...slide.querySelectorAll('[id]')].find(e => e.id === target) : null;
    return {id: el.getAttribute('data-critical-id'), text: visibleText(el), visible: shown(el), rect: rect(el), target,
      targetText: visibleText(object), targetVisible: target ? shown(object) : true, targetRect: object ? rect(object) : null};
  });
}
const normalize = text => String(text || '').replace(/\s+/g, '');
function verifyDeclared(contract, rows) {
  const errors = [], objects = rows.flatMap(r => (r.critical || []).map(c => ({...c, page: r.page})));
  const ids = objects.map(c => c.id);
  if (new Set(ids).size !== ids.length) errors.push('关键语义id重复');
  for (const required of contract?.critical || []) {
    const actual = objects.find(c => c.id === required.id);
    if (!actual || !actual.visible || !actual.targetVisible || normalize(actual.text) !== normalize(required.text) || (required.target && actual.target !== required.target)) errors.push('关键语义未完整落实：' + required.id);
  }
  for (const c of objects) if (!c.visible || !normalize(c.text) || !c.targetVisible) errors.push('关键语义不可见或关联对象缺失：' + c.id);
  return errors;
}
/* 只核对本次真正检查到的页：范围外的关键语义不算失败，单独列出来。
   逐页迭代时成稿只装到当前页，其余页的关键语义本来就不在 DOM 里——把它们报成阻塞，
   会让"阻塞"这个词在制作期失去意义，真阻塞也就没人看了。整册验收仍走 verifyDeclared。 */
function verifyScoped(contract, rows) {
  const found = new Set(rows.flatMap(r => (r.critical || []).map(c => c.id)));
  const errors = verifyDeclared({critical: (contract?.critical || []).filter(c => found.has(c.id))}, rows);
  const uncovered = (contract?.critical || []).filter(c => !found.has(c.id)).map(c => c.id);
  return {errors, uncovered};
}
function verifyPrint(screen, printed) {
  const errors = [];
  for (const c of screen) {
    const p = printed.find(v => v.id === c.id);
    if (!p || !p.visible || !p.targetVisible || normalize(p.text) !== normalize(c.text) || p.target !== c.target || normalize(p.targetText) !== normalize(c.targetText)) errors.push('打印丢失关键语义/关联：' + c.id);
  }
  return errors;
}
function verifyPdf(critical, words) {
  const inBox = r => words.filter(w => w.x + w.width / 2 >= r.x - 4 && w.x + w.width / 2 <= r.x + r.width + 4 && w.y + w.height / 2 >= r.y - 4 && w.y + w.height / 2 <= r.y + r.height + 4).map(w => w.text).join('');
  const errors = [];
  for (const c of critical) {
    if (!normalize(inBox(c.rect)).includes(normalize(c.text))) errors.push('实际PDF关键文字不在对应位置：' + c.id);
    if (c.targetRect && !normalize(inBox(c.targetRect)).includes(normalize(c.targetText))) errors.push('实际PDF关键语义关联对象不完整：' + c.id);
  }
  return errors;
}
module.exports = {inspectSlide, verifyDeclared, verifyScoped, verifyPrint, verifyPdf};
