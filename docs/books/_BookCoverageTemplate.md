# 书籍覆盖模板（复制后重命名）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 书目信息
- 书名：
- 版本：
- 覆盖日期：
- 维护人：

## 章节覆盖表
| 章节 | 对应模块 | 覆盖状态 | 证据链接 | 缺口说明 | 后续动作 |
|---|---|---|---|---|---|
| 示例：Ch1 | `MLTheory.XXX.YYY` | partial | `https://...` | 缺少某定理 | 在某模块新增占位并继续检索 |

## 覆盖状态定义
- `covered`：已有可直接复用的 Lean 形式化内容。
- `partial`：有基础设施或外部候选，但未完整覆盖该章节。
- `gap`：当前无可复用形式化实现。

## 与全局文档联动
1. 新增本书文档后，必须更新：
- `../README.md`（书籍索引）
- `../../ModuleCatalog.md`（`book_refs`）
- `../../GapLedger.md`（缺口条目）
- `../../DecisionLog.md`（关键策略变更）

2. 记录粒度要求：
- 每条 gap 必填 `last_search_date` 与 `next_action`。
- 模块名必须与 `ModuleCatalog.md` 的 `module_path` 完全一致。
