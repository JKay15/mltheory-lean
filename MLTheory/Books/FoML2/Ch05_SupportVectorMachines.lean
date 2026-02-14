/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Learning.SVM

/-!
# MLTheory.Books.FoML2.Ch05_SupportVectorMachines

Book-index compatibility adapters that re-export canonical MLTheory modules.
-/

namespace MLTheory.Books.FoML2

/-- Compatibility alias to concept-first SVM dataset interface. -/
abbrev BinaryClassificationDataset := MLTheory.Methods.Learning.BinaryClassificationDataset

/-- Compatibility alias for label-sign conversion. -/
abbrev boolLabelToSign := MLTheory.Methods.Learning.boolLabelToSign

/-- Compatibility alias for hinge loss. -/
abbrev hingeLoss := MLTheory.Methods.Learning.hingeLoss

/-- Compatibility alias for primal SVM placeholder. -/
abbrev svmPrimalGuarantee : Prop :=
  MLTheory.Methods.Learning.svmPrimalGuarantee

/-- Compatibility alias for dual SVM placeholder. -/
abbrev svmDualGuarantee : Prop :=
  MLTheory.Methods.Learning.svmDualGuarantee

end MLTheory.Books.FoML2
