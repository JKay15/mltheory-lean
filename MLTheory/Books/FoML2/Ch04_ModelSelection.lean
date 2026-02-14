/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Learning.ModelSelection

/-!
# MLTheory.Books.FoML2.Ch04_ModelSelection

Book-index compatibility adapters that re-export canonical MLTheory modules.
-/

namespace MLTheory.Books.FoML2

/-- Compatibility alias to concept-first model-selection interface. -/
abbrev ModelSelectionProblem := MLTheory.Methods.Learning.ModelSelectionProblem

/-- Compatibility alias for SRM-style theorem placeholder. -/
abbrev structuralRiskMinimizationBound : Prop :=
  MLTheory.Methods.Learning.structuralRiskMinimizationBound

end MLTheory.Books.FoML2
