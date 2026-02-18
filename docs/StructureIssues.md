# 结构问题台账（Structure Issues）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 这份文档解决什么问题（人话）
1. 不靠主观印象，直接从当前 `registry.json` 统计结构问题。
2. 每个问题都给证据、影响范围、下一步动作、验收门禁、回滚点。
3. 目标是让“先修什么、怎么修、失败怎么退”一眼可见。

## 当前自动识别的问题
| issue_id | severity | title | evidence | scope | action | acceptance_gate | rollback_point |
|---|---|---|---|---|---|---|---|
| S4 | P2 | 关键入口声明已在，但证明状态仍是 statement | 3 个模块；示例：MLTheory.Core.RL.MDP, MLTheory.Methods.Learning.KernelMethods, MLTheory.Methods.RL.DynamicProgramming | canonical/tool 可信度 | 按 canonical_specs 优先级把 statement 入口逐批推进到 proved；先补依赖闭包最短链路。 | canonical/tool 的 proved 比例按批次上升，且 canonical_contract 持续通过。 | 单批证明失败时只回滚该批 theorem 变更，不回滚已通过批次。 |

## 分批重整顺序（可回滚）
| phase | status | focus_issues | goal | gates | rollback |
|---|---|---|---|---|---|
| Phase-1 | done | S1 + S2 | 先把空心节点和公开 placeholder 收敛到可用入口（不改 theorem 语义） | lake build + check_namespace_layout + check_placeholder_policy | 回滚新增骨架文件与 registry 字段改动 |
| Phase-2 | done | S3 | active alias 分批退役，保证用户入口单轨化 | check_no_new_deprecated_imports + ImportSmoke | 把受阻 alias 从 deprecated 切回 active |
| Phase-3 | pending | S4 | 关键 canonical/tool 从 statement 推进到 proved | check_canonical_contract + lake build | 仅回滚当前批 theorem，不影响已收敛批次 |
| Phase-4 | done | S5 | 整理 planned 状态语义，降低路线图歧义 | validate_ssot + sync_docs --check | 仅回滚 planned_modules 的状态与 reason 文案 |

## 使用方式
1. 先看最高 severity 的问题（若存在 `P1`，优先修 `P1`）。
2. 每完成一批，都跑对应 gates；未过门禁不进入下一批。
3. 若某批卡住，按该批 rollback 先撤回，再拆小批次重试。
