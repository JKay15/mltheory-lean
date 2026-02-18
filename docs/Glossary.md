# Glossary of vernacular terms(Glossary)

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## Data structure basics
1. JSON:a data format,expressible objects(key value pair)and array(list).
2. root(outermost layer):JSON The outermost object of the file.
3. object(object):shaped like `{ "key": value }`.
4. array(array):shaped like `[value1, value2, ...]`.

## SSOT root field(`docs/ssot/registry.json`)
1. `meta`:Global project information(language,toolchain,Update time,Strategy,cleanup_release_epoch).
2. `decisions`:Decision log(date,decision making,state,Influence).
3. `taxonomy_nodes`:main tree node(master-father relationship + tier Label).
4. `taxonomy_relations`:Horizontal relationship edge(second father/association + strength 0~1).
5. `official_workflow_refs`:Lean Official workflow capabilities and warehouse location mapping.
6. `canonical_specs`:canonical Entrance contract(sign/forbidden words/Dependency closure).
7. `modules`:Real module list(Must have local `.lean` document).
8. `planned_modules`:Planning module list(Allow files that have not been implemented yet).
9. `execution_backlog`:Planning short list(`near/mid/far` + priority + complete definition).
10. `structure_cleanup_candidates`:Restructuring Candidates(Execution status,in batches,Compatibility window,window value,Migration starting point,alternative entrance,risk,Recommended action).
11. `gaps`:Gap ledger(Topics not covered or partially covered and follow-up actions).
12. `books`:book coverage mapping(chapter -> module -> Override status).
13. `aliases`:Compatible mapping(old module path -> new module path).

## Module related terms
1. module(module):one can be `import` of Lean code unit,Usually corresponds to a `.lean` document.
2. `module_path`:module path,like `MLTheory.Core.Learning.PAC`.
3. `status`:Override status,`planned/partial/covered/gap`.
3.1 In `planned_modules`, `partial` is only allowed for entries with traceable external evidence; otherwise use `planned` or `gap`.
4. `primary_node_id`:module in taxonomy Primary home node in the primary tree.
5. `source_track`:source axis(`native/books/legacy`).
5.1 exist `modules` Desirable `native/books/legacy`;exist `planned_modules` Only allowed in `native/books`.
5.2 `execution_backlog` used to give `planned_modules` Do short queue scheduling:`near`(Recently),`mid`(medium term),`far`(forward).
6. `layer`:Hierarchical ownership,`core/methods/applications/books/legacy`.
7. `proof_status`:Demonstrate progress,`placeholder/statement/proved`.
8. `placeholder_policy_scope`:placeholder strategy,`allowed/forbidden`.
9. `role`:module role(canonical/compat/bridge/tool/placeholder).
10. `user_surface`:Whether to be a public entrance to users(public/internal).
11. `formal_decl_refs`:List of key declaration names carried by this module.

## Documentation generation and consistency
1. SSOT(Single Source of Truth):single source of truth,here it is `docs/ssot/registry.json`.
2. Derived documents:from SSOT automatically generated Markdown(like `INDEX.md`,`ModuleCatalog.md`).
3. `sync_docs.py --write`:Generate documents according to fixed template.
4. `sync_docs.py --check`: regenerate expected text and compare it to the current file; any difference fails the check.
5. fixed template:`tools/docs/sync_docs.py` inside `render_*` function(title,Column order,The descriptions are all written down).
6. `NamespaceConvergence.md`:Namespace convergence view(Too SSOT derived,Manual modification is not allowed).

## Lean Build and check
1. `lake build`:build the entire Lean project(parse import,type checking,Generate products).
2. `import`:Import module.
3. `#check`:Check if a name exists,Is the type correct?.
4. smoke check(smoke):Quickly confirm that critical paths can still be compiled with a minimal example.

## Quality Gate Control Script
1. `check_no_sorry_axiom.sh`:Does the scan appear? `sorry` or `axiom`.
2. `sorry`:Temporary placeholder,Indicates that the proof is not completed but the compilation must pass first.
3. `axiom`:Direct introduction of unproven premises,Will reduce formal reliability.
4. `check_placeholder_policy.sh`:examine `Core/Methods` not allowed `Prop := True` Placeholder,and check SSOT placeholder policy field.
5. Allowable range of space occupied:Current policy allows `applications/books/legacy` Keep staged placeholders,not allowed `core/methods` placeholder return.
6. `check_canonical_contract.sh`:examine canonical contract declares existence,Forbidden words and dependent citations.
7. `check_official_workflow_alignment.sh`:Check official capability mapping(Loogle/LeanSearch/InfoView/LoogleView/REPL).
8. `check_tool_forest_consistency.py`:Check concept tree and module ownership consistency.
9. `check_review_views_consistency.py`:examine ReviewDashboard/APICards/Is the default behavior of interactive pages consistent with SSOT consistent.
10. `check_namespace_layout.py`:Check that module paths respect hierarchical prefixes with alias Convergence constraints.
11. `check_no_new_deprecated_imports.sh`:Prohibit new additions to deprecated compatible entries import(Backflow prevention).
12. `check_ready_to_remove.py`:according to release The window automatically determines whether to enter `ready_to_remove`.
13. `check_registry_reference_hygiene.py`:examine books/gaps Whether to quote deprecated alias,and check coverage Whether there are repeated modules in the row.
14. `check_ssot_migration_idempotent.sh`:Check migration script idempotence(current registry MUST NOT produce after running migration diff).
15. `advance_cleanup_release_epoch.py`:advance cleanup_release_epoch And automatically switch to the expiration candidate status.
16. `StructureCleanupCandidates.md`:Restructuring candidate list(This round only list,Don't delete files).

## Compatibility layer and import regression
1. Compatibility layer:Thin wrapper files for old module paths,for keeping history `import` constantly.
2. thin package:The file itself does not host the core implementation,Mainly forwarded to the new hierarchical module.
3. Import regression:`Eval/ImportSmoke.lean` Import new path and old path at the same time,Verify that the interface is not broken after reconstruction.

## Development environment terminology
1. symlink(symbolic link):Similar shortcut,Point to another directory or file.
2. submodule(Git submodule):Fixed reference to a commit in another repository in one repository.
3. MCP:Codex Tool service access layer used;For this project `lean-lsp-mcp` supply Lean Interactive capabilities.

## Common commands(Main warehouse)
1. `python3 tools/docs/validate_ssot.py`
2. `python3 tools/docs/sync_docs.py --check`
3. `python3 tools/docs/sync_docs.py --write`
4. `tools/ci/check_no_sorry_axiom.sh`
5. `tools/ci/check_placeholder_policy.sh`
6. `tools/ci/check_canonical_contract.sh`
7. `tools/ci/check_official_workflow_alignment.sh`
8. `python3 tools/ci/check_tool_forest_consistency.py`
9. `python3 tools/ci/check_review_views_consistency.py`
10. `python3 tools/ci/check_namespace_layout.py`
11. `tools/ci/check_no_new_deprecated_imports.sh`
12. `python3 tools/ci/check_ready_to_remove.py`
13. `python3 tools/ci/check_registry_reference_hygiene.py`
14. `tools/ci/check_ssot_migration_idempotent.sh`
15. `python3 tools/ci/advance_cleanup_release_epoch.py --to <N> --write`
16. `~/.elan/bin/lake env lean Eval/ImportSmoke.lean`
17. `~/.elan/bin/lake build`

## Common errors(meaning -> Suggested command)
| Error report fragment | meaning(vernacular) | Which command to run first? |
|---|---|---|
| `Derived docs are out of sync` | The generated document is inconsistent with the existing document in the warehouse | `python3 tools/docs/sync_docs.py --write` Then `--check` |
| `missing keys` / `extra keys` | `registry.json` Field does not conform to contract | `python3 tools/docs/validate_ssot.py` Repair after positioning JSON Field |
| `bad import` | The import path is invalid or the dependencies are not pulled locally. | First `~/.elan/bin/lake build`,Check the correspondence again `import` Does the path exist? |
| `found forbidden token` | Prohibited `sorry/axiom` | `tools/ci/check_no_sorry_axiom.sh` Locate and delete |
| `Prop := True placeholders` | `Core/Methods` An illegal placeholder appears | `tools/ci/check_placeholder_policy.sh` locate and change to true statement |
| `no such file or directory`(mathlib) | Dependency directory or path does not match | `~/.elan/bin/lake build` Re-parse dependencies and look at the first failure point |

## Terminology back-checking(How to find the definition when you see a new word)
1. first `docs/Glossary.md` Look at the vernacular definition.
2. again `docs/ssot/registry.json` Check the field or module path corresponding to the word.
3. If it is the module name(like `MLTheory.X.Y`),use `rg "MLTheory\.X\.Y" docs /Users/xiongjiangkai/xjk_papers/MLTheory/MLTheory` Find sources and citations.
4. If it is a script term(like `placeholder_policy_scope`),use `rg "placeholder_policy_scope" /Users/xiongjiangkai/xjk_papers/MLTheory/tools` Find verification logic.
5. if CI the term(like `ImportSmoke`),look `/Users/xiongjiangkai/xjk_papers/MLTheory/.github/workflows/lean_action_ci.yml` Corresponding steps.
6. If still unclear, ask: 'In which file and line does this term take effect?' to avoid semantic ambiguity.
