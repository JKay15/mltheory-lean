<!-- AUTO:DOC-DOCS_STRUCTUREISSUES_MD BEGIN -->
# Structural Issues Ledger(Structure Issues)

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## What problem does this document solve?(human language)
1. Not relying on subjective impression,directly from the current `registry.json` Statistical structure issues.
2. Give evidence for every question,Scope of influence,Next action,Acceptance of access control,rollback point.
3. The goal is to make 'what to fix first, how to fix it, and how to roll back' visible at a glance.

## Current automatically identified issues
| issue_id | severity | title | evidence | scope | action | acceptance_gate | rollback_point |
|---|---|---|---|---|---|---|---|
| S4 | P2 | The key entry statement is already in,But the proof status is still statement | 4 modules;Example:MLTheory.Basic, MLTheory.Core.RL.MDP, MLTheory.Methods.Learning.KernelMethods, MLTheory.Methods.RL.DynamicProgramming | canonical/tool Credibility | according to canonical_specs Prioritize statement The entrance is advanced in batches to proved;First complement dependency closure shortest link. | canonical/tool of proved Ratio increases by batch,and canonical_contract keep passing. | When the proof of a single batch fails, only the batch will be rolled back. theorem change,Do not roll back passed batches. |

## batch reordering(Can be rolled back)
| phase | status | focus_issues | goal | gates | rollback |
|---|---|---|---|---|---|
| Phase-1 | done | S1 + S2 | First make the hollow nodes public placeholder Convergence to available entry(Don't change theorem semantics) | lake build + check_namespace_layout + check_placeholder_policy | Roll back newly added skeleton files and registry Field changes |
| Phase-2 | done | S3 | active alias Decommissioning in batches,Ensure single-track user entrance | check_no_new_deprecated_imports + ImportSmoke | block alias from deprecated switch back active |
| Phase-3 | pending | S4 | key canonical/tool from statement advance to proved | check_canonical_contract + lake build | Rollback only the current batch theorem,Does not affect converged batches |
| Phase-4 | done | S5 | tidy planned state semantics,Reduce roadmap ambiguity | validate_ssot + sync_docs --check | Rollback only planned_modules status and reason copywriting |

## Usage
1. Look at the highest first severity question(if exists `P1`,Prioritize repair `P1`).
2. Each batch is completed,All running correspondence gates;Those who fail to pass the gate will not be admitted to the next batch..
3. If a batch is stuck,According to the batch rollback Withdraw first,Split into smaller batches and try again.
<!-- AUTO:DOC-DOCS_STRUCTUREISSUES_MD END -->
