/* deck-frame.css 是唯一样式来源；源引擎内联副本支持直接打开及比例测试。 */
const fs=require('node:fs'),path=require('node:path'),frame=require('./apply_frame.cjs');
const file=path.resolve(__dirname,'../assets/deck_engine.html');
fs.writeFileSync(file,frame.apply(fs.readFileSync(file,'utf8')));
console.log('母版 CSS 已同步到引擎；成稿与构建器使用同一 apply_frame 入口。');
