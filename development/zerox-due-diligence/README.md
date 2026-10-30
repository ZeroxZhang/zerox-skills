[中文](#中文) | [English](#english)

# Zerox Due Diligence — development

## 中文

这里维护公司与品牌研究技能的正式回归测试，与运行包分开。测试使用合成资料和自动清理的临时工作区，不联网、不调用模型、不需要密钥。

从仓库根目录执行（Python 3.10+，标准库）：

```bash
python3 -m unittest discover -s development/zerox-due-diligence/tests -q
```

覆盖报告与媒体、官网检索、品牌主体与自然人角色、关键问题和模块裁剪、估算独立性与声明关联，以及安装和完整示例。测试可以用 `zerox_dd_root` 指向另一份完整技能目录，默认读取仓库中的 `zerox-due-diligence/`。

运行包中的完整示例见 [examples](../../zerox-due-diligence/examples/README.md)。测试、缓存、覆盖率、截图和临时结果不复制到技能安装目录；正式测试源码纳入版本管理，过程材料不入库。单元测试通过不证明真实公司资料或研究结论正确。

## English

This directory holds the maintained regression suite for the company and brand research skill, separately from the runtime package. Tests use synthetic data and automatically cleaned temporary workspaces. They need no network, model calls, or API keys.

Run from the repository root with Python 3.10+ and the standard library:

```bash
python3 -m unittest discover -s development/zerox-due-diligence/tests -q
```

Coverage includes reports and media, website planning, brand entities and natural-person roles, key questions and module scope, estimate independence and claim links, installation, and the complete example. Set `zerox_dd_root` to test another complete skill directory; the default is the repository's `zerox-due-diligence/`.

See the shipped [example](../../zerox-due-diligence/examples/README.md). Tests, caches, coverage data, screenshots, and temporary results are excluded from skill installation. Maintained test source is versioned; process artifacts are not. Passing tests does not establish the truth of real company evidence or research conclusions.
