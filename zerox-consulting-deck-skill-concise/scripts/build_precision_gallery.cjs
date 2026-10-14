#!/usr/bin/env node
/* 精度展品的浏览器验收样张：从 test_precision_exhibit 的同一批 samples 生成，
   内嵌交付字体子集。以前这份夹具放在已不随仓库发布的历史目录里，
   测试只能抛一句"先运行某个不存在的脚本"——现在它自己就能造出来。 */
'use strict';
const fs = require('node:fs'), path = require('node:path');
const { samples } = require('./test_precision_exhibit.cjs');
const R = require('./render_precision_exhibit.cjs');
const { pack } = require('./pack_fonts.cjs');

function build(outDir, options = {}) {
  const profile = options.profile || 'serif-report-bold';
  const sections = Object.entries(samples)
    .map(([name, spec]) => '<section data-sample="' + name + '">' + R.render(Object.assign({ theme: 'mckinsey' }, spec)) + '</section>')
    .join('\n');
  const html = '<!DOCTYPE html><html lang="zh-CN" data-frame="off"><head><meta charset="UTF-8">'
    + '<title>精度展品浏览器样张</title><style>body{margin:0;background:#fff}section{display:block}</style></head>'
    + '<body>' + sections + '<script>window.deckReady=Promise.resolve();</script></body></html>';
  fs.mkdirSync(outDir, { recursive: true });
  const file = path.join(outDir, 'gallery.html');
  fs.writeFileSync(file, pack(html, { profile }));
  return { file, samples: Object.keys(samples), profile };
}

if (require.main === module) {
  try {
    const out = path.resolve(process.argv[2] || path.join(__dirname, '..', 'assets', '.precision-gallery'));
    console.log(JSON.stringify(build(out), null, 2));
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
module.exports = { build };
