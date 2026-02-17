# 结构问题台账（Structure Issues）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 这份文档解决什么问题（人话）
1. 不靠主观印象，直接从当前 `registry.json` 统计结构问题。
2. 每个问题都给证据、影响范围、下一步动作、验收门禁、回滚点。
3. 目标是让“先修什么、怎么修、失败怎么退”一眼可见。

## 当前自动识别的问题
| issue_id | severity | title | evidence | scope | action | acceptance_gate | rollback_point |
|---|---|---|---|---|---|---|---|

## 分批重整顺序（可回滚）
| phase | status | focus_issues | goal | gates | rollback |
|---|---|---|---|---|---|
| Phase-1 | done | S1 + S2 | 先把空心节点和公开 placeholder 收敛到可用入口（不改 theorem 语义） | lake build + check_namespace_layout + check_placeholder_policy | 回滚新增骨架文件与 registry 字段改动 |
| Phase-2 | done | S3 | active alias 分批退役，保证用户入口单轨化 | check_no_new_deprecated_imports + ImportSmoke | 把受阻 alias 从 deprecated 切回 active |
| Phase-3 | done | S4 | 关键 canonical/tool 从 statement 推进到 proved | check_canonical_contract + lake build | 仅回滚当前批 theorem，不影响已收敛批次 |
| Phase-4 | done | S5 | 整理 planned 状态语义，降低路线图歧义 | validate_ssot + sync_docs --check | 仅回滚 planned_modules 的状态与 reason 文案 |

## 使用方式
1. 先看最高 severity 的问题（若存在 `P1`，优先修 `P1`）。
2. 每完成一批，都跑对应 gates；未过门禁不进入下一批。
3. 若某批卡住，按该批 rollback 先撤回，再拆小批次重试。
