> 来源：`.trae/skills/onepager/guideline.md` 第 146-1058 行（2026-04-26 版独有内容）
> 该版本 guideline.md 主体为旧代际提示词体系，已被现版重写；此段美学规范为独立内容，故单独保留。
> 抢救时间：2026-09-19


---

# 美学设计规范参考

>  用户想要我基于之前的 One-Page 设计提示词，创建几套不同风格的视觉规范方案，每套都要有完整的设计语言定义，并用 HTML、CSS 和 JS 实现出来，让他们能直接看到效果。我需要确保这些方案都体现出极致美学的水准。
> 
> 我列出了六套有代表性的风格方向——从瑞士国际主义的严谨克制，到日式极简的留白优雅，再到编辑设计的杂志感、暗黑科技风、新粗野主义的大胆对比，以及高端奢华的精致感。考虑到用户的实际需求，我应该从中选出 3-4 套最有代表性的方案，为每一套都制作一个可视化的演示页面。
> 
> 我决定做 4 套方案：瑞士极简风格用于咨询和方案类、编辑杂志风格用于信息图和深度内容、暗黑科技风格用于 SaaS 和产品、日式禅意风格用于高端品质。我会用一个交互式的 HTML 页面来展示这些规范，每套都包含设计理念、色彩系统、字体系统、间距系统、组件示例和实际应用案例，用标签切换让用户能在不同风格间浏览对比。
> 
> 现在我需要规划 HTML 的整体结构——顶部导航用来切换四个风格，内容区根据选择展示对应的完整规范，每个规范都包含色彩、字体、组件和应用案例。接下来我要详细设计每套规范的具体参数。
> 
> 瑞士极简主义强调少即是多和网格至上，用深黑、纯白和瑞士红的配色，Inter 或 Helvetica Neue 字体，8 倍数的间距系统，特点是粗细对比和大量留白。编辑杂志风格则以阅读体验为中心，用炭黑和米色背景，配合金色或深红强调色，采用衬线字体做标题，支持多栏布局和装饰元素。暗黑科技风格追求未来感和专业精确，用深空蓝背景和次级深色卡片...
> 

# 极致美学 One-Page 视觉规范集

基于不同的品牌调性与使用场景，我为你设计了**四套**经过精心打磨的视觉规范系统。每套都有完整的色彩、字体、间距与组件定义，并附带可直接观察的实战应用案例。

**四套风格概览：**

| 系统 | 美学源流 | 核心场景 | 情绪关键词 |
|---|---|---|---|
| **Swiss Minimalism** | 瑞士国际主义 | 咨询方案 / 白皮书 | 理性 · 权威 · 客观 |
| **Editorial Magazine** | 高端杂志编辑设计 | 品牌故事 / 信息图 | 优雅 · 沉静 · 底蕴 |
| **Dark Tech** | 现代科技美学 | SaaS / AI 产品 | 前沿 · 精确 · 未来 |
| **Japanese Zen** | 日式侘寂美学 | 高端品牌 / 生活方式 | 宁静 · 内敛 · 禅意 |

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>One-Page 极致美学视觉规范集</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500;600&family=Noto+Serif+JP:wght@300;400;500;600;700&family=Noto+Sans+JP:wght@300;400;500&family=Shippori+Mincho:wght@400;500;600;700;800&family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  font-family: 'Inter', -apple-system, sans-serif;
  background: #050505; color: #fff;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}
::selection { background: #fff; color: #000; }

/* === 顶部导航 === */
.nav {
  position: sticky; top: 0; z-index: 100;
  background: rgba(5, 5, 5, 0.85);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.nav-inner {
  max-width: 1400px; margin: 0 auto;
  padding: 18px 32px;
  display: flex; justify-content: space-between;
  align-items: center; gap: 24px; flex-wrap: wrap;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-mark {
  width: 28px; height: 28px;
  background: linear-gradient(135deg, #fff, #888);
  border-radius: 6px;
}
.brand-name {
  font-size: 13px; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase;
}
.tabs {
  display: flex; gap: 4px;
  background: rgba(255, 255, 255, 0.04);
  padding: 4px; border-radius: 100px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}
.tab {
  background: transparent; border: none;
  color: rgba(255, 255, 255, 0.6);
  padding: 8px 16px; font-size: 13px; font-weight: 500;
  border-radius: 100px; cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap; font-family: inherit;
}
.tab:hover { color: #fff; }
.tab.active { background: #fff; color: #000; }

/* === Hero === */
.hero {
  padding: 100px 32px 60px;
  text-align: center;
  max-width: 900px; margin: 0 auto;
}
.hero-eyebrow {
  display: inline-block; padding: 6px 14px;
  font-size: 12px; font-weight: 500;
  letter-spacing: 0.08em; text-transform: uppercase;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 100px; color: #ccc;
  margin-bottom: 24px;
}
.hero-title {
  font-size: clamp(40px, 6vw, 68px);
  font-weight: 800; line-height: 1.05;
  letter-spacing: -0.03em; margin-bottom: 20px;
  background: linear-gradient(180deg, #fff 0%, #888 100%);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-subtitle {
  font-size: 17px; line-height: 1.6;
  color: rgba(255, 255, 255, 0.6);
}

/* === 风格容器 === */
.style-block { display: none; animation: fadeIn 0.6s ease; }
.style-block.active { display: block; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.style-bar { height: 4px; }

/* === 风格头部 === */
.style-header {
  max-width: 1400px; margin: 0 auto;
  padding: 60px 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.style-number {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px; color: #666; margin-bottom: 16px;
}
.style-name {
  font-size: clamp(36px, 5vw, 56px);
  font-weight: 700; letter-spacing: -0.02em;
  margin-bottom: 16px; line-height: 1.1;
}
.style-desc {
  font-size: 16px; line-height: 1.7;
  color: rgba(255, 255, 255, 0.6); max-width: 720px;
}
.style-meta {
  display: flex; gap: 32px; flex-wrap: wrap;
  margin-top: 32px; padding-top: 32px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.meta-item { flex: 1; min-width: 200px; }
.meta-label {
  font-size: 11px; font-weight: 500;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: #666; margin-bottom: 8px;
}
.meta-value { font-size: 14px; font-weight: 500; line-height: 1.5; }

/* === 区块 === */
.section {
  max-width: 1400px; margin: 0 auto;
  padding: 72px 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.section-head { margin-bottom: 40px; }
.section-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px; color: #666; margin-bottom: 12px;
}
.section-title {
  font-size: 30px; font-weight: 700;
  letter-spacing: -0.01em; margin-bottom: 12px;
}
.section-desc {
  font-size: 15px; line-height: 1.6;
  color: rgba(255, 255, 255, 0.55); max-width: 640px;
}

/* === 色板 === */
.palette {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
.swatch {
  background: #0d0d0d;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px; overflow: hidden;
  transition: all 0.3s ease;
}
.swatch:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.15);
}
.swatch-color { height: 100px; }
.swatch-info { padding: 14px 16px; }
.swatch-name { font-size: 13px; font-weight: 600; margin-bottom: 4px; }
.swatch-hex {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px; color: #888; text-transform: uppercase;
}
.swatch-usage { font-size: 11px; color: #666; margin-top: 4px; }

/* === 字体展示 === */
.type-grid { display: grid; gap: 0; }
.type-row {
  display: grid; grid-template-columns: 200px 1fr;
  gap: 32px; padding: 24px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  align-items: center;
}
.type-row:last-child { border-bottom: none; }
.type-spec {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px; color: #888; line-height: 1.6;
}
.type-spec strong { display: block; color: #fff; margin-bottom: 4px; }

/* === 预览容器 === */
.preview-wrap {
  margin-top: 32px; border-radius: 24px; overflow: hidden;
  box-shadow: 0 40px 80px rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* ============ 1. SWISS ============ */
.swiss-block .style-bar { background: #E63946; }
.swiss-display { font-size: 64px; font-weight: 800; letter-spacing: -0.03em; line-height: 0.95; color: #fff; }
.swiss-h1 { font-size: 40px; font-weight: 700; letter-spacing: -0.02em; color: #fff; }
.swiss-h2 { font-size: 24px; font-weight: 600; letter-spacing: -0.01em; color: #fff; }
.swiss-body { font-size: 16px; font-weight: 400; line-height: 1.6; color: rgba(255,255,255,0.85); }
.swiss-caption { font-size: 12px; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; color: #E63946; }

.swiss-app {
  background: #fff; color: #0A0A0A;
  font-family: 'Inter', sans-serif; padding: 56px;
}
.swiss-app-head {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 48px;
  padding-bottom: 16px; border-bottom: 2px solid #0A0A0A;
}
.swiss-app-cap {
  font-size: 11px; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase;
}
.swiss-app-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 48px; align-items: start;
}
.swiss-app-eyebrow {
  display: inline-block; padding: 4px 10px;
  background: #E63946; color: #fff;
  font-size: 11px; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase;
  margin-bottom: 24px;
}
.swiss-app-title {
  font-size: 52px; font-weight: 800;
  letter-spacing: -0.03em; line-height: 1;
  margin-bottom: 24px;
}
.swiss-app-sub {
  font-size: 17px; line-height: 1.6;
  color: #525252; margin-bottom: 32px;
}
.swiss-stat { border-top: 2px solid #0A0A0A; padding-top: 16px; }
.swiss-stat-num {
  font-size: 48px; font-weight: 800;
  letter-spacing: -0.02em; line-height: 1; margin-bottom: 8px;
}
.swiss-stat-num span { color: #E63946; }
.swiss-stat-label {
  font-size: 11px; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase; color: #525252;
}
.swiss-modules { display: grid; gap: 16px; }
.swiss-module { border-top: 1px solid #0A0A0A; padding-top: 12px; }
.swiss-module-num {
  font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
  font-family: 'JetBrains Mono', monospace;
  color: #525252; margin-bottom: 6px;
}
.swiss-module-title { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
.swiss-module-desc { font-size: 13px; color: #737373; line-height: 1.5; }

/* ============ 2. EDITORIAL ============ */
.editorial-block .style-bar { background: #C9A961; }
.editorial-display {
  font-family: 'Playfair Display', serif;
  font-size: 76px; font-weight: 800;
  letter-spacing: -0.02em; line-height: 0.95; color: #fff;
}
.editorial-h1 {
  font-family: 'Playfair Display', serif;
  font-size: 48px; font-weight: 700;
  font-style: italic; color: #fff;
}
.editorial-h2 {
  font-family: 'Cormorant Garamond', serif;
  font-size: 32px; font-weight: 500;
  color: rgba(255,255,255,0.85);
}
.editorial-body {
  font-family: 'Inter', sans-serif;
  font-size: 17px; line-height: 1.7;
  color: rgba(255, 255, 255, 0.85);
}
.editorial-caption {
  font-family: 'Inter', sans-serif;
  font-size: 11px; font-weight: 600;
  letter-spacing: 0.15em; text-transform: uppercase; color: #C9A961;
}

.editorial-app {
  background: #F8F4ED; color: #1A1A1A;
  padding: 56px; font-family: 'Inter', sans-serif;
}
.editorial-issue {
  font-size: 11px; font-weight: 600;
  letter-spacing: 0.2em; text-transform: uppercase;
  color: #525252; display: flex; justify-content: space-between;
  border-bottom: 1px solid #1A1A1A;
  padding-bottom: 16px; margin-bottom: 40px;
}
.editorial-app-title {
  font-family: 'Playfair Display', serif;
  font-size: 88px; font-weight: 800;
  letter-spacing: -0.03em; line-height: 0.9;
  margin-bottom: 24px;
}
.editorial-app-title em {
  color: #C9A961; font-style: italic; font-weight: 400;
}
.editorial-cols {
  column-count: 2; column-gap: 32px; margin-top: 32px;
}
.editorial-lead {
  font-family: 'Cormorant Garamond', serif;
  font-size: 22px; font-style: italic;
  line-height: 1.5; color: #1A1A1A;
  margin-bottom: 16px; break-after: column;
}
.editorial-lead::first-letter {
  font-family: 'Playfair Display', serif;
  font-size: 64px; font-weight: 700;
  float: left; line-height: 1;
  margin: 4px 12px 0 0; color: #C9A961;
}
.editorial-text {
  font-size: 14px; line-height: 1.7;
  color: #525252; margin-bottom: 12px;
}
.editorial-byline {
  margin-top: 32px; padding-top: 16px;
  border-top: 1px solid rgba(26, 26, 26, 0.2);
  display: flex; justify-content: space-between;
  font-size: 11px; letter-spacing: 0.1em;
  text-transform: uppercase; color: #525252;
}

/* ============ 3. DARK TECH ============ */
.dark-block .style-bar { background: linear-gradient(90deg, #00D9FF, #6366F1); }
.dark-display {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 64px; font-weight: 700;
  letter-spacing: -0.03em; line-height: 1;
  background: linear-gradient(180deg, #fff 0%, #888 100%);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}
.dark-h1 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 40px; font-weight: 600;
  letter-spacing: -0.02em; color: #fff;
}
.dark-mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px; font-weight: 500; color: #00D9FF;
}
.dark-body {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 16px; line-height: 1.6; color: rgba(255,255,255,0.7);
}

.dark-app {
  background: #0A0E1A; color: #E2E8F0;
  padding: 56px; font-family: 'Space Grotesk', sans-serif;
  position: relative; overflow: hidden;
}
.dark-app::before {
  content: ''; position: absolute;
  top: -50%; left: -20%;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(0, 217, 255, 0.18) 0%, transparent 70%);
  pointer-events: none;
}
.dark-app::after {
  content: ''; position: absolute;
  bottom: -30%; right: -10%;
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.18) 0%, transparent 70%);
  pointer-events: none;
}
.dark-app-content { position: relative; z-index: 1; }
.dark-app-tag {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 12px;
  background: rgba(0, 217, 255, 0.1);
  border: 1px solid rgba(0, 217, 255, 0.3);
  border-radius: 100px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px; color: #00D9FF;
  margin-bottom: 24px;
}
.dark-app-tag::before {
  content: ''; width: 6px; height: 6px;
  background: #00D9FF; border-radius: 50%;
  box-shadow: 0 0 10px #00D9FF;
}
.dark-app-title {
  font-size: 60px; font-weight: 700;
  letter-spacing: -0.03em; line-height: 1.05;
  margin-bottom: 20px;
}
.dark-app-title span {
  background: linear-gradient(135deg, #00D9FF, #6366F1);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}
.dark-app-sub {
  font-size: 17px; color: rgba(226, 232, 240, 0.6);
  line-height: 1.6; margin-bottom: 36px; max-width: 540px;
}
.dark-stats {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 16px; margin-bottom: 32px;
}
.dark-stat {
  background: rgba(19, 24, 37, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px; padding: 20px;
  backdrop-filter: blur(20px);
}
.dark-stat-num {
  font-size: 30px; font-weight: 700;
  background: linear-gradient(135deg, #00D9FF, #6366F1);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 4px;
}
.dark-stat-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px; color: rgba(226, 232, 240, 0.5);
  text-transform: uppercase; letter-spacing: 0.05em;
}
.dark-cta {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 14px 24px;
  background: linear-gradient(135deg, #00D9FF, #6366F1);
  color: #0A0E1A; font-weight: 600; font-size: 14px;
  border-radius: 8px; text-decoration: none;
  box-shadow: 0 10px 30px rgba(0, 217, 255, 0.3);
  transition: transform 0.2s;
}
.dark-cta:hover { transform: translateY(-2px); }

/* ============ 4. JAPANESE ZEN ============ */
.zen-block .style-bar { background: #C53030; }
.zen-display {
  font-family: 'Shippori Mincho', serif;
  font-size: 56px; font-weight: 600;
  letter-spacing: 0.02em; line-height: 1.2; color: #fff;
}
.zen-h1 {
  font-family: 'Noto Serif JP', serif;
  font-size: 36px; font-weight: 500; color: #fff;
}
.zen-body {
  font-family: 'Noto Sans JP', sans-serif;
  font-size: 15px; line-height: 1.9;
  color: rgba(255, 255, 255, 0.8);
}

.zen-app {
  background: #FAF7F2; color: #1C1917;
  padding: 72px 56px;
  font-family: 'Noto Sans JP', sans-serif;
  position: relative; min-height: 540px;
}
.zen-circle {
  position: absolute; top: 56px; right: 56px;
  width: 72px; height: 72px;
  border: 1.5px solid #1C1917;
  border-radius: 50%;
}
.zen-vertical {
  position: absolute; top: 72px; left: 56px;
  writing-mode: vertical-rl;
  font-family: 'Shippori Mincho', serif;
  font-size: 13px; letter-spacing: 0.3em; color: #8B7355;
}
.zen-content { max-width: 600px; margin-left: 100px; }
.zen-mark {
  font-family: 'Shippori Mincho', serif;
  font-size: 14px; letter-spacing: 0.2em;
  color: #C53030; margin-bottom: 28px;
}
.zen-title {
  font-family: 'Shippori Mincho', serif;
  font-size: 52px; font-weight: 600;
  letter-spacing: 0.02em; line-height: 1.3;
  margin-bottom: 28px; color: #1C1917;
}
.zen-divider { width: 60px; height: 1px; background: #1C1917; margin: 24px 0; }
.zen-text {
  font-size: 15px; line-height: 2; color: #525252;
  margin-bottom: 20px; letter-spacing: 0.05em;
}
.zen-quote {
  font-family: 'Shippori Mincho', serif;
  font-style: italic; color: #8B7355;
  font-size: 17px;
}
.zen-meta {
  display: flex; gap: 48px;
  margin-top: 40px; padding-top: 24px;
  border-top: 1px solid rgba(28, 25, 23, 0.15);
  flex-wrap: wrap;
}
.zen-meta-item { font-family: 'Shippori Mincho', serif; }
.zen-meta-label {
  font-size: 11px; letter-spacing: 0.2em;
  color: #8B7355; margin-bottom: 8px; text-transform: uppercase;
}
.zen-meta-val { font-size: 18px; color: #1C1917; }

/* === 响应式 === */
@media (max-width: 768px) {
  .nav-inner { padding: 14px 20px; }
  .tab { padding: 7px 12px; font-size: 12px; }
  .section, .style-header { padding: 50px 20px; }
  .type-row { grid-template-columns: 1fr; gap: 16px; padding: 20px 0; }
  .swiss-app, .editorial-app, .dark-app { padding: 32px 24px; }
  .zen-app { padding: 48px 24px; }
  .swiss-app-grid { grid-template-columns: 1fr; gap: 32px; }
  .editorial-cols { column-count: 1; }
  .editorial-app-title { font-size: 52px; }
  .swiss-app-title { font-size: 36px; }
  .dark-app-title { font-size: 38px; }
  .zen-title { font-size: 36px; }
  .zen-vertical { display: none; }
  .zen-circle { width: 50px; height: 50px; top: 32px; right: 24px; }
  .zen-content { margin-left: 0; padding-top: 60px; }
  .dark-stats { grid-template-columns: 1fr; }
  .swiss-display, .editorial-display, .dark-display, .zen-display { font-size: 44px; }
}

footer {
  padding: 60px 32px; text-align: center;
  border-top: 1px solid rgba(255,255,255,0.06);
}
footer p { font-size: 13px; color: #666; }
</style>
</head>
<body>

<nav class="nav">
  <div class="nav-inner">
    <div class="brand">
      <div class="brand-mark"></div>
      <div class="brand-name">Visual Systems</div>
    </div>
    <div class="tabs">
      <button class="tab active" data-style="swiss">瑞士极简</button>
      <button class="tab" data-style="editorial">编辑杂志</button>
      <button class="tab" data-style="dark">暗黑科技</button>
      <button class="tab" data-style="zen">日式禅意</button>
    </div>
  </div>
</nav>

<header class="hero">
  <div class="hero-eyebrow">Design System · 2026</div>
  <h1 class="hero-title">极致美学视觉规范集</h1>
  <p class="hero-subtitle">四套精心打磨的设计系统，覆盖咨询方案、产品介绍、信息图与品牌叙事等典型 One-Page 场景</p>
</header>

<!-- ========== 1. SWISS ========== -->
<div class="style-block swiss-block active" id="swiss-block">
  <div class="style-bar"></div>
  <header class="style-header">
    <div class="style-number">VISUAL SYSTEM / 01</div>
    <h2 class="style-name">Swiss Minimalism</h2>
    <p class="style-desc">起源于二十世纪中叶的瑞士国际主义平面设计风格。以严谨的网格、克制的字体、大量的留白为核心，传递专业、理性、可信的品牌印象。最适合咨询报告、方案书、专业服务介绍。</p>
    <div class="style-meta">
      <div class="meta-item"><div class="meta-label">关键词</div><div class="meta-value">网格 · 留白 · 无衬线 · 客观</div></div>
      <div class="meta-item"><div class="meta-label">适用场景</div><div class="meta-value">咨询方案 / 产品白皮书 / 专业服务</div></div>
      <div class="meta-item"><div class="meta-label">情绪基调</div><div class="meta-value">理性 · 权威 · 现代</div></div>
    </div>
  </header>

  <section class="section">
    <div class="section-head">
      <div class="section-label">01 / COLOR SYSTEM</div>
      <h3 class="section-title">色彩系统</h3>
      <p class="section-desc">高对比度的黑白基调，搭配一抹瑞士红作为视觉锚点。色彩比例严格遵循 60-30-10 法则。</p>
    </div>
    <div class="palette">
      <div class="swatch"><div class="swatch-color" style="background:#0A0A0A"></div><div class="swatch-info"><div class="swatch-name">Ink Black</div><div class="swatch-hex">#0A0A0A</div><div class="swatch-usage">主文字 · 60%</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#FFFFFF;border-bottom:1px solid #eee"></div><div class="swatch-info"><div class="swatch-name">Pure White</div><div class="swatch-hex">#FFFFFF</div><div class="swatch-usage">背景 · 30%</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#E63946"></div><div class="swatch-info"><div class="swatch-name">Swiss Red</div><div class="swatch-hex">#E63946</div><div class="swatch-usage">强调 · 10%</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#737373"></div><div class="swatch-info"><div class="swatch-name">Neutral 600</div><div class="swatch-hex">#737373</div><div class="swatch-usage">辅助文字</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#F5F5F5"></div><div class="swatch-info"><div class="swatch-name">Neutral 100</div><div class="swatch-hex">#F5F5F5</div><div class="swatch-usage">分隔背景</div></div></div>
    </div>
  </section>

  <section class="section">
    <div class="section-head">
      <div class="section-label">02 / TYPOGRAPHY</div>
      <h3 class="section-title">字体系统 — Inter</h3>
      <p class="section-desc">单一无衬线字体家族，通过字重和字号建立清晰的信息层级。</p>
    </div>
    <div class="type-grid">
      <div class="type-row"><div class="type-spec"><strong>Display</strong>Inter 800<br>64px / -3% / 0.95</div><div class="swiss-display">极致设计</div></div>
      <div class="type-row"><div class="type-spec"><strong>Heading 01</strong>Inter 700<br>40px / -2% / 1.1</div><div class="swiss-h1">主标题样式</div></div>
      <div class="type-row"><div class="type-spec"><strong>Heading 02</strong>Inter 600<br>24px / -1% / 1.3</div><div class="swiss-h2">次级标题样式</div></div>
      <div class="type-row"><div class="type-spec"><strong>Body</strong>Inter 400<br>16px / 0% / 1.6</div><div class="swiss-body">网格、留白、客观，是瑞士国际主义平面设计的三大支柱。它强调形式追随功能。</div></div>
      <div class="type-row"><div class="type-spec"><strong>Caption</strong>Inter 500<br>12px / 5% / 1.4</div><div class="swiss-caption">FIGURE 01 / METHODOLOGY</div></div>
    </div>
  </section>

  <section class="section">
    <div class="section-head">
      <div class="section-label">03 / IN PRACTICE</div>
      <h3 class="section-title">实战应用 — 咨询方案介绍</h3>
      <p class="section-desc">网格为骨架，文字为血肉，红色为心跳。极致克制的视觉表达。</p>
    </div>
    <div class="preview-wrap">
      <div class="swiss-app">
        <div class="swiss-app-head">
          <div class="swiss-app-cap">STRATEGY · 2026</div>
          <div class="swiss-app-cap">CONFIDENTIAL</div>
        </div>
        <div class="swiss-app-grid">
          <div>
            <div class="swiss-app-eyebrow">Digital Transformation</div>
            <h1 class="swiss-app-title">重构企业<br>数字化路径</h1>
            <p class="swiss-app-sub">基于 12 个月深度调研与 47 家头部企业实践，构建可落地的数字化转型方法论。</p>
            <div class="swiss-stat">
              <div class="swiss-stat-num">+<span>247</span>%</div>
              <div class="swiss-stat-label">平均运营效率提升</div>
            </div>
          </div>
          <div class="swiss-modules">
            <div class="swiss-module"><div class="swiss-module-num">01 / DIAGNOSIS</div><div class="swiss-module-title">现状诊断</div><div class="swiss-module-desc">六维评估模型，量化数字化成熟度</div></div>
            <div class="swiss-module"><div class="swiss-module-num">02 / STRATEGY</div><div class="swiss-module-title">战略规划</div><div class="swiss-module-desc">三阶段路线图，明确投入产出比</div></div>
            <div class="swiss-module"><div class="swiss-module-num">03 / EXECUTION</div><div class="swiss-module-title">执行落地</div><div class="swiss-module-desc">敏捷迭代机制，持续优化交付</div></div>
            <div class="swiss-module"><div class="swiss-module-num">04 / SCALE</div><div class="swiss-module-title">规模化复制</div><div class="swiss-module-desc">建立企业能力中心，沉淀方法论</div></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</div>

<!-- ========== 2. EDITORIAL ========== -->
<div class="style-block editorial-block" id="editorial-block">
  <div class="style-bar"></div>
  <header class="style-header">
    <div class="style-number">VISUAL SYSTEM / 02</div>
    <h2 class="style-name">Editorial Magazine</h2>
    <p class="style-desc">以高端杂志的视觉语言为蓝本。大尺寸衬线标题、多栏排版、首字母下沉、装饰性元素，营造沉浸式阅读体验。最适合品牌故事、深度内容、信息图。</p>
    <div class="style-meta">
      <div class="meta-item"><div class="meta-label">关键词</div><div class="meta-value">衬线 · 多栏 · 故事感 · 优雅</div></div>
      <div class="meta-item"><div class="meta-label">适用场景</div><div class="meta-value">品牌故事 / 深度信息图 / 文化内容</div></div>
      <div class="meta-item"><div class="meta-label">情绪基调</div><div class="meta-value">优雅 · 沉静 · 富有底蕴</div></div>
    </div>
  </header>

  <section class="section">
    <div class="section-head">
      <div class="section-label">01 / COLOR SYSTEM</div>
      <h3 class="section-title">色彩系统</h3>
      <p class="section-desc">米色暖底替代纯白，降低阅读疲劳。金色或深红作为强调色，营造高级感。</p>
    </div>
    <div class="palette">
      <div class="swatch"><div class="swatch-color" style="background:#1A1A1A"></div><div class="swatch-info"><div class="swatch-name">Charcoal</div><div class="swatch-hex">#1A1A1A</div><div class="swatch-usage">主文字</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#F8F4ED"></div><div class="swatch-info"><div class="swatch-name">Cream</div><div class="swatch-hex">#F8F4ED</div><div class="swatch-usage">背景</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#C9A961"></div><div class="swatch-info"><div class="swatch-name">Gold</div><div class="swatch-hex">#C9A961</div><div class="swatch-usage">强调</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#B91C1C"></div><div class="swatch-info"><div class="swatch-name">Crimson</div><div class="swatch-hex">#B91C1C</div><div class="swatch-usage">辅助强调</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#525252"></div><div class="swatch-info"><div class="swatch-name">Slate</div><div class="swatch-hex">#525252</div><div class="swatch-usage">辅助文字</div></div></div>
    </div>
  </section>

  <section class="section">
    <div class="section-head">
      <div class="section-label">02 / TYPOGRAPHY</div>
      <h3 class="section-title">字体系统 — Playfair × Cormorant</h3>
      <p class="section-desc">两款经典衬线字体的组合，配合 Inter 作正文，构建优雅的阅读节奏。</p>
    </div>
    <div class="type-grid">
      <div class="type-row"><div class="type-spec"><strong>Display</strong>Playfair Display 800<br>76px / -2% / 0.95</div><div class="editorial-display">封面大字</div></div>
      <div class="type-row"><div class="type-spec"><strong>Heading Italic</strong>Playfair Display 700 italic<br>48px / 0% / 1.1</div><div class="editorial-h1">优雅的标题</div></div>
      <div class="type-row"><div class="type-spec"><strong>Subtitle</strong>Cormorant 500<br>32px / 0% / 1.3</div><div class="editorial-h2">余韵悠长的副标题</div></div>
      <div class="type-row"><div class="type-spec"><strong>Body</strong>Inter 400<br>17px / 0% / 1.7</div><div class="editorial-body">编辑设计的精髓在于让阅读本身成为一种美学体验。每一行字、每一处留白都经过精心编排。</div></div>
      <div class="type-row"><div class="type-spec"><strong>Caption</strong>Inter 600<br>11px / 15% / 1.4</div><div class="editorial-caption">ISSUE NO.07 — VOLUME II</div></div>
    </div>
  </section>

  <section class="section">
    <div class="section-head">
      <div class="section-label">03 / IN PRACTICE</div>
      <h3 class="section-title">实战应用 — 品牌故事</h3>
      <p class="section-desc">以杂志封面为灵感，融合大字标题、多栏正文与装饰性元素。</p>
    </div>
    <div class="preview-wrap">
      <div class="editorial-app">
        <div class="editorial-issue">
          <span>ATELIER · ISSUE 07</span>
          <span>春季特刊 · MMXXVI</span>
        </div>
        <h1 class="editorial-app-title">器物之间，<br><em>见微知著</em></h1>
        <div class="editorial-cols">
          <div class="editorial-lead">一件好的器物，从不喧哗。它静静伫立在角落，等待被理解。我们花了七年时间，从瓷土到釉面，重新追问什么是"好"。</div>
          <p class="editorial-text">创立于 2019 年的 Atelier，至今已与 23 位独立匠人合作，共出品 147 件器物。每一件都经历不少于 90 天的反复打磨。</p>
          <p class="editorial-text">"美应当是日用之物，而非奢侈之物。"我们相信，真正好的设计应当融入生活的褶皱里，与时间共老。</p>
        </div>
        <div class="editorial-byline">
          <span>BY EDITORIAL TEAM</span>
          <span>P. 24</span>
        </div>
      </div>
    </div>
  </section>
</div>

<!-- ========== 3. DARK TECH ========== -->
<div class="style-block dark-block" id="dark-block">
  <div class="style-bar"></div>
  <header class="style-header">
    <div class="style-number">VISUAL SYSTEM / 03</div>
    <h2 class="style-name">Dark Tech</h2>
    <p class="style-desc">以暗色为底，霓虹为光的现代科技美学。结合渐变、玻璃态、辉光效果与等宽字体，传递专业、精确、未来的品牌印象。最适合 SaaS 产品、AI 工具、技术文档。</p>
    <div class="style-meta">
      <div class="meta-item"><div class="meta-label">关键词</div><div class="meta-value">暗色 · 渐变 · 辉光 · 数据感</div></div>
      <div class="meta-item"><div class="meta-label">适用场景</div><div class="meta-value">SaaS 产品 / AI 工具 / 技术介绍</div></div>
      <div class="meta-item"><div class="meta-label">情绪基调</div><div class="meta-value">前沿 · 精确 · 未来感</div></div>
    </div>
  </header>

  <section class="section">
    <div class="section-head">
      <div class="section-label">01 / COLOR SYSTEM</div>
      <h3 class="section-title">色彩系统</h3>
      <p class="section-desc">深空蓝替代纯黑减轻视觉压力，青色与紫色构成核心强调，营造深度与未来感。</p>
    </div>
    <div class="palette">
      <div class="swatch"><div class="swatch-color" style="background:#0A0E1A"></div><div class="swatch-info"><div class="swatch-name">Deep Space</div><div class="swatch-hex">#0A0E1A</div><div class="swatch-usage">主背景</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#131825"></div><div class="swatch-info"><div class="swatch-name">Card</div><div class="swatch-hex">#131825</div><div class="swatch-usage">卡片背景</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:linear-gradient(135deg,#00D9FF,#6366F1)"></div><div class="swatch-info"><div class="swatch-name">Gradient</div><div class="swatch-hex">#00D9FF→#6366F1</div><div class="swatch-usage">核心强调</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#00D9FF"></div><div class="swatch-info"><div class="swatch-name">Cyan</div><div class="swatch-hex">#00D9FF</div><div class="swatch-usage">数据 / 链接</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#E2E8F0"></div><div class="swatch-info"><div class="swatch-name">Soft White</div><div class="swatch-hex">#E2E8F0</div><div class="swatch-usage">主文字</div></div></div>
    </div>
  </section>

  <section class="section">
    <div class="section-head">
      <div class="section-label">02 / TYPOGRAPHY</div>
      <h3 class="section-title">字体系统 — Space Grotesk × JetBrains Mono</h3>
      <p class="section-desc">几何无衬线传达现代感，等宽字体强化技术属性。</p>
    </div>
    <div class="type-grid">
      <div class="type-row"><div class="type-spec"><strong>Display</strong>Space Grotesk 700<br>64px / -3% / 1</div><div class="dark-display">Build the future</div></div>
      <div class="type-row"><div class="type-spec"><strong>Heading</strong>Space Grotesk 600<br>40px / -2% / 1.1</div><div class="dark-h1">现代科技标题</div></div>
      <div class="type-row"><div class="type-spec"><strong>Body</strong>Space Grotesk 400<br>16px / 0% / 1.6</div><div class="dark-body">深色背景下的正文，需要更柔和的白色与适当的行高。</div></div>
      <div class="type-row"><div class="type-spec"><strong>Mono</strong>JetBrains Mono 500<br>14px / 0% / 1.5</div><div class="dark-mono">$ build --production --optimize</div></div>
    </div>
  </section>

  <section class="section">
    <div class="section-head">
      <div class="section-label">03 / IN PRACTICE</div>
      <h3 class="section-title">实战应用 — SaaS 产品介绍</h3>
      <p class="section-desc">深色背景搭配辉光渐变，玻璃态卡片承载关键数据。</p>
    </div>
    <div class="preview-wrap">
      <div class="dark-app">
        <div class="dark-app-content">
          <div class="dark-app-tag">v2.0 · LIVE NOW</div>
          <h1 class="dark-app-title">为 AI 时代而生的<br><span>下一代工作流</span></h1>
          <p class="dark-app-sub">从研究到决策，我们将团队效率提升 10 倍。无需复杂配置，5 分钟即可上手。</p>
          <div class="dark-stats">
            <div class="dark-stat"><div class="dark-stat-num">12.7M</div><div class="dark-stat-label">ACTIVE USERS</div></div>
            <div class="dark-stat"><div class="dark-stat-num">99.99%</div><div class="dark-stat-label">UPTIME SLA</div></div>
            <div class="dark-stat"><div class="dark-stat-num">~50ms</div><div class="dark-stat-label">AVG LATENCY</div></div>
          </div>
          <a href="#" class="dark-cta">免费开始 · 无需信用卡 →</a>
        </div>
      </div>
    </div>
  </section>
</div>

<!-- ========== 4. ZEN ========== -->
<div class="style-block zen-block" id="zen-block">
  <div class="style-bar"></div>
  <header class="style-header">
    <div class="style-number">VISUAL SYSTEM / 04</div>
    <h2 class="style-name">Japanese Zen</h2>
    <p class="style-desc">源自日式美学的"侘寂"与"间"。以极致的留白、克制的元素、自然的材质感传递宁静、内敛、有底蕴的品牌印象。最适合高端品牌、文化产品、生活方式。</p>
    <div class="style-meta">
      <div class="meta-item"><div class="meta-label">关键词</div><div class="meta-value">留白 · 明朝体 · 朱红 · 余白之美</div></div>
      <div class="meta-item"><div class="meta-label">适用场景</div><div class="meta-value">高端品牌 / 文化产品 / 生活方式</div></div>
      <div class="meta-item"><div class="meta-label">情绪基调</div><div class="meta-value">宁静 · 内敛 · 富有禅意</div></div>
    </div>
  </header>

  <section class="section">
    <div class="section-head">
      <div class="section-label">01 / COLOR SYSTEM</div>
      <h3 class="section-title">色彩系统</h3>
      <p class="section-desc">和纸般的米白底色，墨色为主，茶褐为辅，朱红点睛。整体色彩饱和度极低。</p>
    </div>
    <div class="palette">
      <div class="swatch"><div class="swatch-color" style="background:#1C1917"></div><div class="swatch-info"><div class="swatch-name">墨 Sumi</div><div class="swatch-hex">#1C1917</div><div class="swatch-usage">主文字</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#FAF7F2"></div><div class="swatch-info"><div class="swatch-name">和纸 Washi</div><div class="swatch-hex">#FAF7F2</div><div class="swatch-usage">背景</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#C53030"></div><div class="swatch-info"><div class="swatch-name">朱 Shu</div><div class="swatch-hex">#C53030</div><div class="swatch-usage">点睛</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#8B7355"></div><div class="swatch-info"><div class="swatch-name">茶 Cha</div><div class="swatch-hex">#8B7355</div><div class="swatch-usage">辅助</div></div></div>
      <div class="swatch"><div class="swatch-color" style="background:#A8A29E"></div><div class="swatch-info"><div class="swatch-name">灰 Hai</div><div class="swatch-hex">#A8A29E</div><div class="swatch-usage">弱化</div></div></div>
    </div>
  </section>

  <section class="section">
    <div class="section-head">
      <div class="section-label">02 / TYPOGRAPHY</div>
      <h3 class="section-title">字体系统 — Shippori Mincho × Noto</h3>
      <p class="section-desc">明朝体作主标题，呼应日式书道之美；现代无衬线作正文，平衡阅读性。</p>
    </div>
    <div class="type-grid">
      <div class="type-row"><div class="type-spec"><strong>Display</strong>Shippori Mincho 600<br>56px / 2% / 1.2</div><div class="zen-display">静水流深</div></div>
      <div class="type-row"><div class="type-spec"><strong>Heading</strong>Noto Serif JP 500<br>36px / 0% / 1.4</div><div class="zen-h1">器物之美</div></div>
      <div class="type-row"><div class="type-spec"><strong>Body</strong>Noto Sans JP 300<br>15px / 5% / 1.9</div><div class="zen-body">真正的美，存在于不完美之中。<br>这是日本美学传承千年的核心思想。</div></div>
    </div>
  </section>

  <section class="section">
    <div class="section-head">
      <div class="section-label">03 / IN PRACTICE</div>
      <h3 class="section-title">实战应用 — 高端品牌介绍</h3>
      <p class="section-desc">大量留白与纵向元素构成视觉骨架，朱红点缀提供呼吸节奏。</p>
    </div>
    <div class="preview-wrap">
      <div class="zen-app">
        <div class="zen-circle"></div>
        <div class="zen-vertical">令和八年 · 春</div>
        <div class="zen-content">
          <div class="zen-mark">— 静</div>
          <h1 class="zen-title">器之间，<br>余白之美</h1>
          <div class="zen-divider"></div>
          <p class="zen-text">一器一物，皆有其声。<br>我们追求的不是完美的器物，<br>而是与时间共老的陪伴。</p>
          <p class="zen-text zen-quote">「真正的美，在于克制」</p>
          <div class="zen-meta">
            <div class="zen-meta-item"><div class="zen-meta-label">CRAFT</div><div class="zen-meta-val">90 日</div></div>
            <div class="zen-meta-item"><div class="zen-meta-label">EDITION</div><div class="zen-meta-val">23 件</div></div>
            <div class="zen-meta-item"><div class="zen-meta-label">SINCE</div><div class="zen-meta-val">2019</div></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</div>

<footer>
  <p>每套规范均可独立用于 One-Page 设计 · 建议根据品牌调性、目标受众与内容类型综合选择</p>
</footer>

<script>
  const tabs = document.querySelectorAll('.tab');
  const blocks = document.querySelectorAll('.style-block');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.style;
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      blocks.forEach(b => {
        b.classList.toggle('active', b.id === target + '-block');
      });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });
</script>

</body>
</html>
```

---

## 如何使用这套规范

每套系统都包含**可直接复用的三大资产**：

**色板**：直接复制 HEX 色值到你的设计文件（Figma / Sketch / PPT）。
**字体**：所有字体均来自 Google Fonts，可免费商用。
**应用案例**：观察实战应用中"色彩比例、字号阶梯、留白节奏"的具体落地方式，照此移植到你自己的内容。

**选型建议**：

如果你做的是 B 端咨询方案、白皮书、企业介绍，选**瑞士极简**最稳妥；如果是品牌故事、深度长文、信息图，**编辑杂志**风格能让内容自带溢价感；做 SaaS、AI 产品、技术文档，**暗黑科技**几乎是当前的行业标配；做高端消费品、文化品牌、生活方式品类，**日式禅意**能在一片喧闹中脱颖而出。

