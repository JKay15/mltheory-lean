# AGENTS.md

This document defines the agent execution specification of this warehouse.All subsequent tasks must follow the rules here by default..

## 0. Standard entry
1. This warehouse only uses `AGENTS.md` As an agent specification entry.
2. No longer maintained `AGENT.md` Compatible with entry files.

## 1. Document system first(SSOT)
1. Before starting any new task,Look first `docs/INDEX.md`.
2. The single source of truth for document data is fixed at:`docs/ssot/registry.json`.
3. `docs/*.md` and `docs/books/*.md`(With index,cover,Ledger)All are derived files,Direct manual correction of text data is prohibited.
4. The document modification process is fixed as:
- Change first `docs/ssot/registry.json`
- implement `python3 tools/docs/validate_ssot.py`
- implement `python3 tools/docs/sync_docs.py --write`
5. new information generated(new decision,new module,new gap,new external candidate)Must write back to `registry.json`,and regenerate the document.

## 1.1 Three warehouse collaborative constraints(fixed)
1. Paper template warehouse(outermost layer)It is the running entrance.
2. `lean-proof-skills` yes skillpack father's warehouse,Contains within `lean4` and `ml-paper-workflow`.
3. `MLTheory` Passed by the template warehouse Lake `git + rev(tag)` rely,Not used submodule.
4. skills Use priority:repo-scope(Template warehouse `.agents/skills/*`)Prioritize the global `~/.codex/skills/*`.

## 2. Structure and naming
1. Document language defaults to Chinese.
2. Dates are used uniformly `YYYY-MM-DD`.
3. The module name must match `docs/ModuleCatalog.md`(Depend on SSOT generate)of `module_path` completely consistent.
4. When adding books, they must be based on `docs/books/_BookCoverageTemplate.md`.
5. Code organization follows concept priority layering:
- `MLTheory/Core/*`
- `MLTheory/Methods/*`
- `MLTheory/Applications/*`
- `MLTheory/Books/*`(Compatible adaptation and re-export)

## 3. Delete policy(important)
1. Default policy:Do not delete at will(append-first).
2. Allow deletion,But the following conditions must be met:
- There is a clear reason for deletion(mistake,repeat,Obsolete and superseded).
- exist `registry.json` Add corresponding decision records,and regenerate `docs/DecisionLog.md`.
- priority"Mark obsolete/Migrate archive",Consider physical deletion again.
3. Deletion without recording reasons is considered a violation.

## 4. Implement minimum requirements
1. Before each submission, execute at least:
- `python3 tools/docs/validate_ssot.py`
- `python3 tools/docs/sync_docs.py --check`
- `lake build`
2. Perform at least one document retrieval self-check before each submission(For example `rg`)Make sure key fields exist.
3. Keep `docs/INDEX.md` Can be used as the only navigation entrance,New core documents must be linked.

## 4.1 Occupancy access control strategy(fixed)
1. Phase 1:allow `Applications/Books/Legacy` layer occupancy.
2. Phase 1 Also required:`Core/Methods` The layer occupancy must be 0.
3. Phase 2:CI right `Core/Methods` Placeholder regression fails directly(Hard access control).

## 5. Conflict handling
1. If this document conflicts with the user's latest explicit instructions,Subject to user instructions.
2. If there is any ambiguity,Press first"retain information,minimal deletion,Record first and change later"direction processing.
