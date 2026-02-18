# book cover template(Rename after copying)

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## bibliographic information
- book title:
- Version:
- Coverage date:
- maintainer:

## Chapter coverage table
| chapter | Corresponding module | Override status | Evidence link | Gap description | Follow-up actions |
|---|---|---|---|---|---|
| Example:Ch1 | `MLTheory.XXX.YYY` | partial | `https://...` | missing a theorem | Add a placeholder in a module and continue searching |

## Override status definition
- `covered`:Already available for direct reuse Lean formal content.
- `partial`:There are infrastructure or external candidates,But the chapter is not completely covered.
- `gap`:There is currently no reusable formal implementation.

## Linked to global documents
1. After adding this book document,Must update:
- `../README.md`(book index)
- `../../ModuleCatalog.md`(`book_refs`)
- `../../GapLedger.md`(gap entry)
- `../../DecisionLog.md`(Key strategy changes)

2. Record granularity requirements:
- each gap Required `last_search_date` and `next_action`.
- The module name must match `ModuleCatalog.md` of `module_path` completely consistent.
