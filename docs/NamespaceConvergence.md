# Namespace convergence view(Namespace Convergence)

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## Target(human language)
1. New modules must fall under the hierarchical prefix(`Core/Methods/Applications/Books`).
2. `legacy` Layers retain only top-level compatible entries(`MLTheory.X`),No more new depths legacy path.
3. Map old entry paths to new entry paths via `aliases` to avoid 'imports still work, but migration targets are unclear'.

## Current convergence status
- current `structure_cleanup_candidates = 0`,Batch deletion of compatible portals has been completed.
- Total number of real modules:69
- alias total:22(deprecated=22 / active=0)

## Hierarchical prefix constraints(real module)
| layer | required_prefix | module_count | examples |
|---|---|---|---|
| core | MLTheory.Core | 14 | MLTheory.Core<br>MLTheory.Core.Learning<br>MLTheory.Core.Learning.Capacity |
| methods | MLTheory.Methods | 43 | MLTheory.Methods<br>MLTheory.Methods.Bandits<br>MLTheory.Methods.Bandits.Adversarial |
| applications | MLTheory.Applications | 9 | MLTheory.Applications.AI<br>MLTheory.Applications.AI.DecisionLearning<br>MLTheory.Applications.AI.Generalization |
| books | MLTheory.Books | 2 | MLTheory.Books.FoML2<br>MLTheory.Books.SuttonBartoRL2 |

## Remaining top layer legacy Entrance(Keep compatible)
| module_path | source_track | role | status | proof_status |
|---|---|---|---|---|

## Deprecated Alias(old entrance -> new entrance)
| legacy_module | canonical_module | status |
|---|---|---|
| MLTheory.AI | MLTheory.Applications.AI | deprecated |
| MLTheory.Applications | MLTheory.Applications.Learning | deprecated |
| MLTheory.Bandits | MLTheory.Methods.Bandits | deprecated |
| MLTheory.Books | MLTheory.Core | deprecated |
| MLTheory.Books.FoML2.Ch02_PACLearning | MLTheory.Core.Learning.PAC | deprecated |
| MLTheory.Books.FoML2.Ch03_RademacherVCDimension | MLTheory.Core.Learning.Capacity | deprecated |
| MLTheory.Books.FoML2.Ch04_ModelSelection | MLTheory.Methods.Learning.ModelSelection | deprecated |
| MLTheory.Books.FoML2.Ch05_SupportVectorMachines | MLTheory.Methods.Learning.SVM | deprecated |
| MLTheory.Books.FoML2.Ch06_KernelMethods | MLTheory.Methods.Learning.KernelMethods | deprecated |
| MLTheory.Books.SuttonBartoRL2.Ch03_MDP | MLTheory.Core.RL.MDP | deprecated |
| MLTheory.Books.SuttonBartoRL2.Ch04_DynamicProgramming | MLTheory.Methods.RL.DynamicProgramming | deprecated |
| MLTheory.Concentration | MLTheory.Methods.Learning.ConcentrationPackaging | deprecated |
| MLTheory.HDP | MLTheory.Core | deprecated |
| MLTheory.InfoTheory | MLTheory.Core.Statistics | deprecated |
| MLTheory.LLM | MLTheory.Applications.LLM | deprecated |
| MLTheory.Learning | MLTheory.Methods.Learning | deprecated |
| MLTheory.OCO | MLTheory.Methods.OCO | deprecated |
| MLTheory.OR | MLTheory.Methods.OR | deprecated |
| MLTheory.Optimization | MLTheory.Methods.OR | deprecated |
| MLTheory.Probability | MLTheory.Core.Probability | deprecated |
| MLTheory.RL | MLTheory.Core.RL | deprecated |
| MLTheory.Statistics | MLTheory.Core.Statistics | deprecated |

## Active Alias(Still in compatibility mapping)
| legacy_module | canonical_module | status |
|---|---|---|
