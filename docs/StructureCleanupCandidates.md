# 结构清理候选（只做清单）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 说明
1. 当前 `structure_cleanup_candidates=0`，兼容入口分批删除已完成。
2. 若后续新增兼容入口，必须先登记候选证据，再进入 `deprecated -> ready_to_remove -> physical remove` 流程。
3. 删除动作仍要求先写 `DecisionLog`，并跑全量门禁。

| module_path | definition_file | imported_by | role | execution_state | priority | batch | compatibility_window | remove_after_releases | migration_started_epoch | replacement_imports | risk | suggested_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
