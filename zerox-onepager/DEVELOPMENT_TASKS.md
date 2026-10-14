# Onepager 产品开发任务清单

## 产品决策

`A/B/C/T/E/F` 是 Onepager 的核心渐进式交互协议，不是需要隐藏的专业参数。

系统必须：

1. 基于内容为每个维度给出推荐及理由。
2. 完整展示所有选项，让用户确认或覆盖。
3. 支持组合回复，如 `A4 B2 C2 T1 E1 F默认`。
4. 将用户最终选择写入 IR 和 manifest。
5. 迭代时允许只修改一个维度，不要求重新回答全部选项。

系统不得：

- 跳过配置交互并静默替用户决定。
- 把 `A/B/C/T/E/F` 藏到高级设置。
- 因引入自动推荐而削弱用户选择权。

## P0：可复现项目

### EPIC-01 内容蓝图

- [x] 定义内容蓝图 Schema。
- [x] Phase 1 生成用户可见的简洁蓝图。
- [x] 蓝图包含目标、受众、核心论点、模块、来源和缺失信息。
- [x] 用户确认蓝图后进入 `A/B/C/T/E/F` 配置。
- [x] 缺少事实时只标记，不自动补造。

验收：

- 蓝图能在生成 HTML 前暴露内容理解偏差。
- 每个事实模块有来源引用或 `missing` 标记。
- 用户可修改核心论点和模块重点。

### EPIC-02 渐进式配置协议

- [x] 保留 `A/B/C/T/E/F` 完整菜单。
- [x] 为每个推荐项补充一句与当前内容相关的理由。
- [x] 解析组合回复和单维度修改。
- [x] 校验非法组合并给出可执行修正。
- [x] 将最终选择写入 IR。

验收：

- 用户可一次确认全部推荐。
- 用户可覆盖任意一个或多个维度。
- 迭代时输入 `改成 B6` 只更新 B。

### EPIC-03 Onepager IR v1

- [x] 定义 IR JSON Schema。
- [x] IR 包含蓝图、最终配置、模块稳定 ID、来源、设计意图和锁定状态。
- [x] 提供 IR 示例。
- [x] 提供 Schema 校验命令。
- [x] 明确向后兼容和 `schema_version` 策略。

验收：

- IR 可脱离聊天上下文描述一次完整生成。
- 每个内容模块具有稳定 ID。
- 用户选择的 `A/B/C/T/E/F` 可无损还原。

### EPIC-04 项目目录与 Manifest

- [x] 定义 manifest JSON Schema。
- [x] 实现项目初始化命令。
- [x] 实现版本号递增与构建记录。
- [x] 保存 source、blueprint、IR、HTML、PNG 和质检结果。
- [x] 记录文件 SHA-256、生成时间和工具版本。
- [x] 实现 manifest 校验。

建议目录：

```text
.onepager/projects/{slug}/
├── source/
├── blueprint.json
├── onepager.ir.json
├── manifest.json
└── builds/
    └── v001/
        ├── output.html
        ├── output.png
        ├── static-check.json
        └── render-check.json
```

验收：

- 同一项目的版本不会互相覆盖。
- manifest 能定位全部输入、配置、产物和检查报告。
- 缺失或被修改的产物能被校验命令发现。

### EPIC-05 项目 CLI

- [x] `project init`：初始化项目和基础文件。
- [x] `project validate`：校验 Blueprint、IR、Manifest 和文件哈希。
- [x] `project record-build`：记录一次通过质检的构建。
- [x] `project next-version`：返回下一版本号。
- [x] 所有命令支持 JSON 输出和明确退出码。

验收：

- CLI 无需模型即可完成项目资产管理。
- 错误不会静默修复或覆盖已有文件。
- 路径包含空格和中文时正常工作。

## P1：局部迭代

### EPIC-06 模块锁定与 Patch

- [ ] 定义 IR Patch 格式。
- [ ] 支持按模块 ID 修改文案、角色、密度和图表类型。
- [ ] 支持锁定内容、布局或全部。
- [ ] Patch 不得修改未指定模块。
- [ ] 保存 Patch 历史和版本差异。

### EPIC-07 品牌系统

- [ ] 定义 Brand Schema。
- [ ] 支持颜色、字体、Logo、安全区、禁用色、圆角和语气。
- [ ] 提供品牌初始化向导。
- [ ] 品牌规则接入静态质检。
- [ ] `B` 仍用于选择视觉方向，Brand 负责长期一致性。

### EPIC-08 候选方案与预览

- [ ] 同一蓝图与配置生成两个差异明显的设计候选。
- [ ] 提供并排缩略图和质检状态。
- [ ] 支持选定一个候选继续迭代。
- [ ] 建立本地轻量预览器。

## P2：输出与生态

### EPIC-09 SVG / AntV Infographic

- [ ] 评估将流程图、层级图、矩阵图委托给 AntV。
- [ ] 保留整页 HTML 构图，增加 SVG 组件输出。
- [ ] IR 中记录渲染器类型。
- [ ] SVG 输出进入质检和 manifest。

### EPIC-10 Recipe 生态

- [ ] 定义 Recipe Schema。
- [ ] 每个 Recipe 包含适用场景、容量边界、反例和金标准截图。
- [ ] 建立 Gallery。
- [ ] Recipe PR 自动执行 Schema、截图和视觉回归。

### EPIC-11 安装与触发评测

- [ ] 支持通用 Agent Skill 安装工具。
- [ ] 建立中英文 should-trigger / near-miss 样本。
- [ ] 发布兼容矩阵与触发率报告。
- [ ] 提供轻量 HTML 模式和完整 Playwright 模式。

## 暂不开发

- 完整自由拖拽白板。
- 多人实时协作。
- 大型在线 SaaS。
- 完整 PPT 编辑器。
- 无边界增加视觉风格。
