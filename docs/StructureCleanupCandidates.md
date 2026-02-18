# Structural Cleanup Candidates(Just make a list)

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## illustrate
1. current `structure_cleanup_candidates=0`,Batch deletion of compatible portals has been completed.
2. If a new compatible entry is added in the future,,Candidate evidence must be registered first,re-enter `deprecated -> ready_to_remove -> physical remove` process.
3. The delete action still requires writing first `DecisionLog`,And run full access control.

| module_path | definition_file | imported_by | role | execution_state | priority | batch | compatibility_window | remove_after_releases | migration_started_epoch | replacement_imports | risk | suggested_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
