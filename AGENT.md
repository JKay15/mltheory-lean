# AGENT.md

兼容文件名（主规范文件为 `AGENTS.md`）。

请优先阅读并遵循：`/Users/xiongjiangkai/xjk_papers/MLTheory/AGENTS.md`。

关键约束摘要：
1. 文档单一事实源是 `docs/ssot/registry.json`，其余文档为派生文件。
2. 文档维护流程固定：先改 SSOT，再运行 `validate_ssot.py` 与 `sync_docs.py --write`。
3. 新信息必须回写文档系统（决策/模块/缺口/书籍覆盖）。
4. 不允许随意删除；允许有理由删除，但必须在决策日志（由 SSOT 派生）留痕。
5. 三仓协同固定：模板仓为入口，`lean-proof-skills` 为 skillpack 父仓，`MLTheory` 通过 Lake `git + tag` 接入。
6. 占位门禁固定：`Core/Methods` 禁止占位回归，`Applications/Books/Legacy` 允许阶段性占位。
