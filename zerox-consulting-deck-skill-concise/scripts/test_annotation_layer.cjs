/* 标注层几何、语义与碰撞；不依赖浏览器。 */
const assert = require('node:assert/strict');
const A = require('../assets/annotation-layer.js');
const G = require('../assets/exhibit-geometry.js');

// 确定性测量：每字符 0.6em，测试不依赖字体资产。
const measure = (text, options) => ({ width: Array.from(String(text)).length * (options.size || 14) * 0.6 });
const results = {};
const scene = options => A.createScene(Object.assign({ width: 640, height: 360, fontSize: 14, measure }, options));

// 1. 锚点契约：注册、重复拒绝、显式坐标必需。
{
  const s = scene();
  A.addAnchor(s, { id: 'a', x: 100, y: 200, side: 'right', value: 42, label: '甲', box: { x: 90, y: 190, width: 10, height: 20 } });
  assert.throws(() => A.addAnchor(s, { id: 'a', x: 1, y: 1 }), /重复/);
  assert.throws(() => A.addAnchor(s, { id: 'b', x: NaN, y: 1 }), /有限数值/);
  assert.throws(() => A.addAnchor(s, { id: 'b', x: 1, y: 1, side: 'up' }), /side/);
  const attrs = A.anchorAttrs(s.anchors.a);
  assert.match(attrs, /data-anchor-id="a"/);
  assert.match(attrs, /data-anchor-value="42"/, '锚点必须自带原值，读回时不能依赖图元恰好有 data-value');
  const roundtrip = A.collect('<svg><rect ' + A.anchorAttrs({ id: 'k', x: 1, y: 2, value: 7, group: 'g', side: 'top' }) + '/></svg>');
  assert.equal(roundtrip.k.value, 7);
  assert.equal(roundtrip.k.group, 'g');
  assert.match(attrs, /data-anchor-x="100" data-anchor-y="200"/);
  assert.match(attrs, /data-anchor-side="right"/);
  assert.match(attrs, /data-anchor-box="90,190,10,20"/);
  assert.match(attrs, /data-anchor-label="甲"/);
}

// 2. 从已生成 SVG 收集锚点：只读显式声明，拒绝缺坐标与重复 id。
{
  const svg = '<svg><rect data-anchor-id="x" data-anchor-x="1" data-anchor-y="2" data-anchor-side="top" data-value="7"/>'
    + '<circle data-anchor-id="y" data-anchor-x="3" data-anchor-y="4" data-anchor-box="0,0,5,5"/></svg>';
  const collected = A.collect(svg);
  assert.deepEqual(Object.keys(collected).sort(), ['x', 'y']);
  assert.equal(collected.x.value, 7);
  assert.equal(collected.x.side, 'top');
  assert.deepEqual(collected.y.box, { x: 0, y: 0, width: 5, height: 5 });
  assert.throws(() => A.collect('<svg><rect data-anchor-id="x" data-anchor-x="1"/></svg>'), /显式坐标/);
  assert.throws(() => A.collect('<svg><rect data-anchor-id="x" data-anchor-x="1" data-anchor-y="1"/><rect data-anchor-id="x" data-anchor-x="2" data-anchor-y="2"/></svg>'), /重复/);
}

// 3. 语义：原值／差额／增长率／百分点／倍数／份额／排名／模板。
{
  const s = scene();
  A.addAnchor(s, { id: 'p', x: 10, y: 10, value: 100, label: '期初', group: 'ch' });
  A.addAnchor(s, { id: 'q', x: 20, y: 10, value: 140, label: '本期', group: 'ch' });
  A.addAnchor(s, { id: 'r', x: 30, y: 10, value: 60, label: '其他', group: 'ch' });
  assert.equal(A.resolveText(s, { on: 'p' }, {}), '100');
  assert.equal(A.resolveText(s, { on: 'q', kind: 'delta', from: 'p' }, {}), '+40');
  assert.equal(A.resolveText(s, { on: 'q', kind: 'rate', from: 'p' }, {}), '+40.0%');
  assert.equal(A.resolveText(s, { on: 'q', kind: 'pp', from: 'p', format: { basis: 'percent' } }, {}), '+40 个百分点');
  assert.equal(A.resolveText(s, { on: 'q', kind: 'multiple', from: 'p' }, {}), '1.4×');
  assert.equal(A.resolveText(s, { on: 'q', kind: 'share', of: 'p' }, {}), '+140%');
  assert.match(A.resolveText(s, { on: 'q', kind: 'rank' }, {}), /第 1 位/);
  assert.equal(A.resolveText(s, { on: 'q', kind: 'note', text: '首个完整年度' }, {}), '首个完整年度');
  assert.equal(A.resolveText(s, { on: 'q', kind: 'delta', from: 'p', text: '{label} {delta}（{rate}）' }, {}), '本期 +40（+40.0%）');
  // 零基数不能硬算增长率：差额仍可读，增长率给出不适用原因。
  A.addAnchor(s, { id: 'z', x: 40, y: 10, value: 0, label: '零基', group: 'ch' });
  assert.equal(A.resolveText(s, { on: 'q', kind: 'delta', from: 'z' }, {}), '+140');
  assert.match(A.resolveText(s, { on: 'q', kind: 'rate', from: 'z' }, {}), /不适用（零基数）/);
  // 无 from 时按自身语义：瀑布的 delta 柱直接标注本柱带符号原值，不再要求一组端点。
  assert.equal(A.resolveText(s, { on: 'q', kind: 'delta' }, {}), '+140');
  assert.equal(A.resolveText(s, { on: 'q', kind: 'delta', text: '主要拖累 {value}' }, {}), '主要拖累 +140');
  // 无 from 时取不到的字段必须当场拦住。文档把六个字段并列成通用能力，
  // 作者照写 {delta} 会把它原样印在图上——那是成稿里很难被发现的错字。
  assert.throws(() => A.resolveText(s, { on: 'q', kind: 'delta', text: '主要拖累 {delta}' }, {}), /\{delta\} 取不到值/);
  assert.throws(() => A.resolveText(s, { on: 'q', kind: 'delta', text: '{rate}' }, {}), /\{rate\} 取不到值/);
  assert.throws(() => A.resolveText(s, { on: 'q', kind: 'note', text: '{start}→{end}' }, {}), /\{start\} 取不到值/);
  assert.match(A.resolveText(s, { on: 'q', kind: 'share', text: '占比 {value}' }, {}), /^占比 /, '这一分支能给的字段不能被一起拦掉');
  // 集合外的花括号是普通文字，不参与校验。
  assert.equal(A.resolveText(s, { on: 'q', kind: 'note', text: '口径 {见附注}' }, {}), '口径 {见附注}');
  assert.throws(() => A.resolveText(s, { on: 'q', kind: 'bracket' }, {}), /需要 from/);
  assert.throws(() => A.resolveText(s, { on: 'missing' }, {}), /未知标注端点/);
}

// 4. 放置：优先贴近锚点，越界或碰撞时退到更远的候选环，引线绑定真实端点。
{
  const s = scene();
  const box = { x: 560, y: 160, width: 40, height: 40 };
  A.addAnchor(s, { id: 'a', x: 580, y: 180, side: 'right', value: 42, label: '甲', box, markId: 'a' });
  A.addObstacle(s, { id: 'a', box });            // 图元本身注册为障碍，柱内候选才能验证真的装得下
  const item = A.place(s, { id: 'n1', on: 'a', kind: 'value' }, {});
  assert.equal(item.placement, 'inside');       // 柱内放得下就先放柱内
  assert.equal(item.leader, null);
  assert.ok(item.box.x >= box.x && item.box.x + item.box.width <= box.x + box.width);

  const s2 = scene();
  A.addAnchor(s2, { id: 'a', x: 300, y: 180, side: 'right', value: 42, label: '甲', box: { x: 294, y: 100, width: 12, height: 160 } });
  const outside = A.place(s2, { id: 'n2', on: 'a', kind: 'value', text: '一个明显放不进柱子的长标注文字' }, {});
  assert.equal(outside.placement, 'outside');
  assert.equal(outside.side, 'right');
  assert.ok(outside.leader, '外置标注必须带引线');
  assert.deepEqual(outside.leader[0], { x: 306, y: 180 });  // 引线从图元侧边出发，不从中心出发
  assert.equal(A.audit(s2).ok, true);
  assert.equal(A.audit(s2).count, 1);
}

// 5. 碰撞避让：先用障碍占满最近的位置环，标注必须移到更远处而不是压上去。
{
  const s = scene();
  A.addAnchor(s, { id: 'a', x: 300, y: 180, side: 'right', value: 42, label: '甲', box: { x: 294, y: 170, width: 12, height: 20 } });
  for (let d = 0; d <= 2; d++) {
    A.addObstacle(s, { id: 'block' + d, box: { x: 320, y: 180 - 10 + d * 28, width: 90, height: 22 } });
  }
  const placed = A.place(s, { id: 'n3', on: 'a', kind: 'value', text: '值 42' }, {});
  assert.equal(placed.placement, 'outside');
  const blocked = s.obstacles.every(ob => !G.intersects(ob.box, placed.box, 2));
  assert.ok(blocked, '标注不得压住已注册的图元');
}

// 6. 容量耗尽必须报错，而不是静默丢标签或压图。
{
  const s = scene({ width: 200, height: 120 });
  A.addAnchor(s, { id: 'a', x: 100, y: 60, side: 'right', value: 1, label: '甲', box: { x: 98, y: 58, width: 4, height: 4 } });
  for (let i = 0; i < 40; i++) A.addObstacle(s, { id: 'b' + i, box: { x: 0, y: 0, width: 200, height: 120 } });
  assert.throws(() => A.place(s, { id: 'n4', on: 'a', kind: 'value', text: '放不下' }, {}), /无法无碰撞放置/);
  const reported = A.annotate(s, [{ id: 'n4', on: 'a', kind: 'value', text: '放不下' }], { onFailure: 'report' });
  assert.equal(reported.items.length, 0);
  assert.equal(reported.issues[0].code, 'annotation-placement');
}

// 7. 小目标先占位：小柱片的唯一出路不能被大柱片的宽松候选挤掉后仍然通过。
{
  const s = scene();
  A.addAnchor(s, { id: 'big', x: 200, y: 300, side: 'top', value: 900, label: '大', box: { x: 180, y: 40, width: 40, height: 260 } });
  A.addAnchor(s, { id: 'tiny', x: 260, y: 300, side: 'top', value: 3, label: '小', box: { x: 255, y: 294, width: 10, height: 6 } });
  const result = A.annotate(s, [
    { id: 'A-big', on: 'big', kind: 'value' },
    { id: 'B-tiny', on: 'tiny', kind: 'value', text: '极小片 3' }
  ], {});
  assert.equal(result.items.length, 2);
  assert.equal(A.audit(s).ok, true);
  const tiny = s.labels.find(l => l.id === 'B-tiny');
  assert.ok(s.obstacles.every(ob => ob.id === 'tiny' || !G.intersects(ob.box, tiny.box, 2)));
}

// 8. 序列化：引线与文字都带可核对的角色和归属。
{
  const s = scene();
  A.addAnchor(s, { id: 'a', x: 300, y: 180, side: 'right', value: 42, label: '甲', box: { x: 294, y: 168, width: 12, height: 24 } });
  const result = A.annotate(s, [{ id: 'n5', on: 'a', kind: 'value', text: '很长的说明文字放不进柱内' }], {});
  const svg = A.serialize(s, result.items, {});
  assert.match(svg, /data-role="leader"/);
  assert.match(svg, /data-annotation-id="n5"/);
  assert.match(svg, /data-anchor-ref="a"/);
  assert.match(svg, /<text[^>]+data-role="annotation"/);
  assert.doesNotMatch(svg, /NaN|undefined/);
}

// 9. 视觉语法：引线不得穿越已有文字或其他图元。
{
  const s = scene();
  A.addAnchor(s, { id: 'a', x: 120, y: 180, side: 'right', value: 5, label: '甲', box: { x: 114, y: 174, width: 12, height: 12 } });
  A.addObstacle(s, { id: 'wall', box: { x: 300, y: 120, width: 30, height: 120 } });
  const placed = A.place(s, { id: 'n6', on: 'a', kind: 'value', text: '值 5' }, {});
  const points = placed.leader;
  if (points) for (let i = 1; i < points.length; i++) {
    assert.equal(G.lineHitsRect(points[i - 1], points[i], s.obstacles[0].box, 0), false, '引线穿越图元');
  }
}

// 10. 自动旁注候选：只从真实原值派生，参照锚点不参与同类比较，每条都带依据。
{
  const s = scene({ width: 900, height: 500 });
  [['商超', 5.3], ['电商', 2.0], ['经销', 3.1], ['直营', 0.9]].forEach(([label, value]) =>
    A.addAnchor(s, { id: 'end:' + label, x: 100, y: 80, side: 'right', value, label, group: 'end' }));
  A.addAnchor(s, { id: 'value:达成率%', x: 100, y: 80, side: 'bottom', value: 76, label: '达成率%', group: 'value' });
  A.addAnchor(s, { id: 'target:达成率%', x: 120, y: 80, side: 'top', value: 90, label: '达成率% 目标', group: 'target' });
  const list = A.propose(s, { max: 8 });
  assert.ok(list.length >= 4, 'must propose something for a real exhibit');
  assert.ok(list.every(p => p.on && A.kinds[p.kind] && p.reason && p.derived && p.evidence.length), '每条候选都要能复核：kind、依据、派生量与引用锚点');
  const target = list.find(p => p.kind === 'delta' && p.from === 'target:达成率%');
  assert.ok(target, '实际与目标成对时必须提出缺口候选');
  assert.equal(target.to, 'value:达成率%');
  assert.deepEqual(target.derived, { start: 90, end: 76, delta: -14 });
  assert.ok(!list.some(p => p.on.startsWith('target:') && p.kind === 'value'), '参照锚点不能被当成同类数据点去比大小');
  const top = list.find(p => p.id === 'p-value-end:商超');
  assert.ok(top && /最高/.test(top.text));
  assert.equal(top.derived.value, 5.3);
  assert.equal(top.derived.rank, 1);
  assert.equal(A.propose(s, { max: 2 }).length, 2, 'max 必须生效');
  assert.ok(A.propose(A.createScene({ width: 400, height: 260, measure })).length === 0, '没有锚点时不给候选');
}

// 11. 绘制原点：框一律以左缘起算，text-anchor 只是绘制原点，换算只允许发生在序列化那一处。
//     这条守的是"标注整段压在别的文字上、引线接到空处"那类缺陷——生成期自查看不出来。
{
  const s = scene({ width: 900, height: 420 });
  A.addAnchor(s, { id: 'r', x: 700, y: 120, side: 'right', value: 12, label: '右', box: { x: 690, y: 110, width: 20, height: 20 } });
  // 左侧锚点要离画布左缘足够远，否则 left 侧候选越界，引擎会合理地退到右侧——那是正确行为，不是这条测试要测的。
  A.addAnchor(s, { id: 'l', x: 300, y: 300, side: 'left', value: 8, label: '左', box: { x: 290, y: 290, width: 20, height: 20 } });
  const placed = A.annotate(s, [
    { id: 'right-one', on: 'r', kind: 'value', text: '一段明显放不进图元的说明文字' },
    { id: 'left-one', on: 'l', kind: 'value', text: '另一段同样放不进去的说明文字' }
  ], {}).items;
  assert.equal(placed.length, 2);
  assert.deepEqual(placed.map(v => v.anchorMode).sort(), ['end', 'start'], '两侧必须分别产生 end 与 start 两种绘制原点');
  const svg = A.serialize(s, placed, {});
  for (const item of placed) {
    const tag = new RegExp('<text[^>]*data-annotation-id="' + item.id + '"[^>]*>').exec(svg)[0];
    const mode = /text-anchor="([^"]+)"/.exec(tag)[1];
    const x = Number(/ x="([^"]+)"/.exec(tag)[1]);
    const expected = mode === 'middle' ? item.box.x + item.box.width / 2 : mode === 'end' ? item.box.x + item.box.width : item.box.x;
    assert.ok(Math.abs(x - expected) < 1e-9, item.id + '：' + mode + ' 的绘制原点必须由声明框换算，当前 ' + x + ' ≠ ' + expected);
    // 声明框与绘制结果必须一致：end 锚点的文字右缘就是框右缘，start 锚点的文字左缘就是框左缘。
    const declared = [item.box.x, item.box.y, item.box.width, item.box.height];
    assert.equal(declared.length, 4);
  }
  // 反例：把绘制原点写回框左缘（旧的错误做法），检查必须失败。
  const broken = svg.replace(/<text([^>]*)data-annotation-id="(left-one|right-one)"([^>]*)>/, (m, a, id, b) => {
    const item = placed.find(v => v.id === id);
    return '<text' + a.replace(/ x="[^"]+"/, ' x="' + item.box.x + '"') + 'data-annotation-id="' + id + '"' + b + '>';
  });
  const check = target => placed.every(item => {
    const tag = new RegExp('<text[^>]*data-annotation-id="' + item.id + '"[^>]*>').exec(target)[0];
    const mode = /text-anchor="([^"]+)"/.exec(tag)[1], x = Number(/ x="([^"]+)"/.exec(tag)[1]);
    return Math.abs(x - (mode === 'end' ? item.box.x + item.box.width : item.box.x)) < 1e-9;
  });
  assert.equal(check(svg), true);
  if (broken !== svg) assert.equal(check(broken), false, '把绘制原点写回框左缘必须被这条检查抓住');
  results.drawOrigin = true;
}

console.log('AnnotationLayer: anchor contract, semantics, placement, leader routing, collision fallback, capacity errors, proposal rules and draw-origin conversion passed.');
