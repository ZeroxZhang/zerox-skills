# zerox-deep-research 评测

`zerox-deep-research/` 的验证材料。**不是 skill**，不参与 `bridge-skill.sh` 的集合识别（无 `SKILL.md`）。

## 目录

| 路径 | 是什么 |
|---|---|
| `scenarios/` | 6 个测试场景的推演记录（以「刚加载 skill 的新会话」视角逐个走查） |
| `fixture-package/` | `check_package.py` 的埋错样例包 + 测试结果 |
| `live-run/` | 真实运行记录（场景 2 到闸门、完整 L2） |

## 6 个场景

| # | 场景 | 考什么 | 结果 |
|---|---|---|---|
| 1 | 简单事实题 | description 不误触发；显式点名时走 L1 轻路径、不建包 | 静态推演通过 |
| 2 | 模糊大题 | 先摸底再提问；澄清附默认选项；产出简报并停在计划确认闸门 | 推演 + **实跑到闸门** |
| 3 | 对比选型 | 拆评估维度、并行研究、对比矩阵；来源 ID 不冲突、重复合并 | 静态推演通过（ID 机制经 L2 实跑验证） |
| 4 | 「直接开始别问我」 | 跳过提问但不跳过假设；假设进简报与报告 | 静态推演通过 |
| 5 | 需要最新信息的中文题 | 中英双语检索；时效事实标日期 | 静态推演 + L2 实跑验证日期标注 |
| 6 | 存档韧性 | 付费墙/403 → metadata-only；长 PDF → 页码标记；动态页 → 截图或 partial；无凭空补写 | 推演 + **L2 实跑踩到 403** |

## 怎么复现

```bash
CK=../zerox-deep-research/scripts/check_package.py
python3 $CK fixture-package/broken   # 应 FAIL（4 错误）
python3 $CK fixture-package/clean    # 应 PASS
python3 $CK live-run/l2-llm-api-pricing/research/*/   # 真实研究包
```

## 测试中发现并修复的问题

见 `fixture-package/RESULTS.md`。摘要：

1. `capture_source.py` 把列表元数据写成 Python repr 而非 YAML 列表
2. `check_package.py` 无 report.md 时崩溃（`refs` 初始化成 `[]`）
3. 检索日志被误报为孤立文件
4. `sha256: null`（无原始文件时的合法值）被当成缺字段
5. 错误信息里的绝对路径

另有两处**内容层**错误由质检/复算抓出（非脚本问题）：`notes/A-pricing.md` 的缓存倍率算错（0.1 → 0.025）；`analysis/normalize_cache_cost.py` 初版把不同档位型号的绝对价并排比较。均已修正，正是本 skill「数字要核对口径」要防的失败。
