# check_package.py 埋错样例测试

目的：确认脚本能报出每类证据链错误，而不是只会绿灯通过。

样例包在 `broken/`（故意埋错）与 `clean/`（应通过），可重复运行：

```bash
CK=../../zerox-deep-research/scripts/check_package.py
python3 $CK broken   # 应 FAIL，退出码 1
python3 $CK clean    # 应 PASS，退出码 0
```

## 埋入的错误与检出结果

| # | 埋的错 | 期望 | 实测输出 | 判定 |
|---|---|---|---|---|
| 1 | `report.md` 引用 `[9]`，参考列表无该条目 | 错误 | `正文引用 [9]（行 11）在参考列表中无对应条目` | ✓ |
| 2 | 参考条目 `[2]` 的存档路径指向不存在的文件 | 错误 | `[2] 存档路径不存在: raw/sources/A001-DOES-NOT-EXIST.md` | ✓ |
| 3 | `notes/M-facts.md` E-002 的逐字摘录被改成「50 亿元」，快照原文是「48 亿元」 | 错误 | `notes/M-facts.md:19 摘录在快照 A001 中找不到` | ✓ |
| 4 | `A001` 快照元数据里的 `sha256` 改成全 0，与实际文件不符 | 错误 | `A001-white-paper.md 记录的哈希与 … 不一致（记录 000000000000，实际 0af1c8ed47ff）` | ✓ |
| 5 | 参考条目 `[3]` 未被正文引用 | 警告 | `[3] 参考条目未被正文引用` | ✓ |
| 6 | `sources.md` 登记 `U999`，但没有对应快照 | 警告 | `sources.md 登记的 U999 没有对应快照` | ✓ |
| 7 | `raw/files/orphan-stray.pdf` 无任何快照/元数据引用 | 警告 | `孤立文件（无快照/元数据引用）: raw/files/orphan-stray.pdf` | ✓ |
| 8 | `raw/search-logs/M.md` 是检索日志 | **不应报** | （修前误报为孤立文件；修后不再报） | ✓ 已修 |

**结果：4 错误 + 3 警告，退出码 1。8/8 项符合预期。**

## 测试中发现并修复的问题

| 问题 | 根因 | 修复 |
|---|---|---|
| 检索日志被误报为孤立文件 | 孤立文件判定只豁免了 `notes/`、`analysis/`、`tasks/`，漏了 `raw/search-logs/` 与 `raw/user-provided/`——这两类是过程记录，按包结构自登记 | 豁免列表加上这两条前缀 |
| 错误信息里出现绝对路径 | `parse_notes` 直接存 `str(path)` | 改存相对研究包根的路径 |
| `capture_source.py` 把列表字段写成 Python repr（`original_files: "['raw/…']"`） | `yaml_scalar` 未处理 list | 补 list 分支，输出 YAML 流式列表 `[a, b]` |
| 无 report.md 时崩溃 | 缺文件分支把 `refs` 初始化成 `[]` 而非 `{}` | 改成 `{}` |

## 干净包通过验证

`clean/` 含 2 个一手来源、2 条笔记摘录、3 条参考条目、2 份检索日志、用户材料与计算脚本：

```
-- 错误 (0) --  无
-- 警告 (0) --  无
-- 统计 --
  来源总数: 2
  完整度: {'full': 2}
  层级: {'primary': 2}
  检索次数: 2 段日志 / 2 条查询
  研究线: A,M
结果: PASS
```

## manifest 完整性校验

```bash
python3 $CK clean --write-manifest
cd clean && shasum -a 256 -c manifest-sha256.txt   # 全部 OK
echo tamper >> brief.md && shasum -a 256 -c manifest-sha256.txt   # brief.md: FAILED
```

清单格式为 `SHA-256 值 + 两个空格 + 相对路径`，与 BagIt/RFC 8493 的清单同形，`sha256sum -c` / `shasum -a 256 -c` 可直接校验。篡改可被检出。
