# MLTheory Document index

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## Purpose
This directory is used for precipitation MLTheory historical decisions,Module planning,Book coverage and gap search ledger.

## core navigation
<!-- AUTO:INDEX-CORE-NAV BEGIN -->
| document | illustrate |
|---|---|
| [../AGENTS.md](../AGENTS.md) | Agent execution specifications(Document system first,Delete legacy rules) |
| [DecisionLog.md](./DecisionLog.md) | Decision log(fixed fields:`date/decision/status/impact`) |
| [ModuleCatalog.md](./ModuleCatalog.md) | Module summary(fixed fields:`module_path/primary_node_id/source_track/status/...`) |
| [GapLedger.md](./GapLedger.md) | Global gap ledger(fixed fields:`book/chapter/topic/status/last_search_date/sources_checked/candidate_repo/next_action`) |
| [ToolForest.md](./ToolForest.md) | concept + Module forest diagram(Depend on SSOT Automatically generated) |
| [ToolForestInteractive.html](./ToolForestInteractive.html) | filterable/Searchable/Collapsible interactive structure view(Recommended for daily use) |
| [GraphExplorer.html](./GraphExplorer.html) | Graph view MVP(Backbone priority + One jump to expand,read subgraph) |
| [ReviewDashboard.md](./ReviewDashboard.md) | Acceptance Kanban(New in this round,current focus,One-click acceptance command) |
| [RefactorHandoffForGPT52Pro.md](./RefactorHandoffForGPT52Pro.md) | Give GPT5.2pro refactoring handover package(Achieve panorama + access control + risk) |
| [APICards.md](./APICards.md) | smallest API card(each public what module does,Which statements to look at first) |
| [ExecutionBacklog.md](./ExecutionBacklog.md) | Planning module short list(near/mid/far),Bundle 96 roadmap converges into executable queue |
| [NamespaceConvergence.md](./NamespaceConvergence.md) | Namespace convergence view(Level prefix,legacy Entrance,alias mapping) |
| [StructureIssues.md](./StructureIssues.md) | Structural Issues Ledger(Automatically identify problems + Rectification order in batches + rollback point) |
| [StructureCleanupCandidates.md](./StructureCleanupCandidates.md) | Restructuring candidate list(in batches/window/alternative entrance/risk) |
| [books/README.md](./books/README.md) | Books cover index page |
| [Glossary.md](./Glossary.md) | Glossary of vernacular terms(Reduce slang communication costs) |
| [meta/taxonomy.yaml](./meta/taxonomy.yaml) | vNext Concept tree and binding(Increment meta) |
| [meta/aliases.yaml](./meta/aliases.yaml) | vNext Retrieve alias table(Increment meta) |
| [meta/canon.yaml](./meta/canon.yaml) | vNext Stablize API Checklist(Increment meta) |
| [meta/backlog.yaml](./meta/backlog.yaml) | Optional blueprint-style Spec execution backlog states |
| [meta/ui.yaml](./meta/ui.yaml) | Optional graph viewer defaults(scope/spine/expand/visible nodes) |
| [_auto/README.md](./_auto/README.md) | AutoView Catalog Description(Generate entry) |
| [_auto/CodeIndex.md](./_auto/CodeIndex.md) | code first module/import automatic view |
| [_auto/GraphArtifacts.md](./_auto/GraphArtifacts.md) | subgraph with telemetry Statistics automatic view |
| [ssot/registry.json](./ssot/registry.json) | single source of truth(The only data file that can be modified manually) |
| [ssot/schema.json](./ssot/schema.json) | SSOT field contract |
<!-- AUTO:INDEX-CORE-NAV END -->

## Book coverage document
<!-- AUTO:INDEX-BOOKS BEGIN -->
| books | Overwrite document |
|---|---|
| Vershynin<High-Dimensional Probability> | [books/Vershynin_HDP_Coverage.md](./books/Vershynin_HDP_Coverage.md) |
| Durrett<Probability Theory and Examples> | [books/Durrett5_Coverage.md](./books/Durrett5_Coverage.md) |
| Lattimore & Szepesvari<Bandit Algorithms> | [books/BanditAlgorithms_Coverage.md](./books/BanditAlgorithms_Coverage.md) |
| Hazan<Introduction to Online Convex Optimization> | [books/HazanOCO2_Coverage.md](./books/HazanOCO2_Coverage.md) |
| Mohri-Rostamizadeh-Talwalkar<Foundations of Machine Learning> | [books/FoML2_Coverage.md](./books/FoML2_Coverage.md) |
| Sutton-Barto<Reinforcement Learning: An Introduction> | [books/SuttonBarto_RL2_Coverage.md](./books/SuttonBarto_RL2_Coverage.md) |
<!-- AUTO:INDEX-BOOKS END -->

## maintenance rules(When adding a new book)
1. Update first `ssot/registry.json`,Run the document generation script again.
2. implement `python3 tools/docs/validate_ssot.py` Check field contract.
3. implement `python3 tools/docs/sync_docs.py --write` Generate derived documents.
4. implement `tools/index/gen_mltheory_index.sh` renew `artifacts/index` and `docs/_auto`.
5. If deleted or replaced,must be in `DecisionLog.md` leave traces.

## ToolForest Get started quickly
1. Accept the current round of changes:Look first [ReviewDashboard.md](./ReviewDashboard.md).
2. To give complete context to the reconstructed model:look [RefactorHandoffForGPT52Pro.md](./RefactorHandoffForGPT52Pro.md).
3. See module usage and entry declaration:Look again [APICards.md](./APICards.md).
4. Look at the overall structure:Open [ToolForestInteractive.html](./ToolForestInteractive.html)(By default, only the real modules are viewed).
5. Look at the backbone+Expand map:Open [GraphExplorer.html](./GraphExplorer.html).
6. Look at index statistics and graph statistics:Check [_auto/CodeIndex.md](./_auto/CodeIndex.md) + [_auto/GraphArtifacts.md](./_auto/GraphArtifacts.md).
7. To overview the main tree:look [ToolForest.md](./ToolForest.md) of"surface 1:taxonomy Node overview".
8. Depends on the recent schedule:look [ExecutionBacklog.md](./ExecutionBacklog.md).
9. Depends on the namespace migration path:look [NamespaceConvergence.md](./NamespaceConvergence.md).
10. Depends on structural issues and cleanup candidates:look [StructureIssues.md](./StructureIssues.md) + [StructureCleanupCandidates.md](./StructureCleanupCandidates.md).
11. Any structural adjustment can only change `ssot/registry.json`,Execute again:
- `python3 tools/docs/validate_ssot.py`
- `python3 tools/docs/sync_docs.py --write`
- `tools/index/gen_mltheory_index.sh`
- `tools/index/gen_graph_artifacts.sh`
- `python3 tools/ci/check_taxonomy_contract.py`
- `python3 tools/ci/check_tool_forest_consistency.py`
- `python3 tools/ci/check_review_views_consistency.py`
- `python3 tools/ci/check_namespace_layout.py`
- `tools/ci/check_ssot_migration_idempotent.sh`
- `tools/ci/check_no_new_deprecated_imports.sh`
- `python3 tools/ci/check_ready_to_remove.py`
- `python3 tools/ci/check_registry_reference_hygiene.py`

## Current default constraints
1. Document language:Chinese.
2. Document organization:Multiple document indexing(Not merged into a single overall document).
3. Near term strategy:Stable first SSOT with layered module skeleton,Then add proof chapter by chapter.
4. delete rule:Random deletion is not allowed;When deletion is justified, the scope of impact must be recorded.
