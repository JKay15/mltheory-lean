/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Learning.KernelMethods

/-!
# MLTheory.Books.FoML2.Ch06_KernelMethods

Book-index compatibility adapters that re-export canonical MLTheory modules.
-/

namespace MLTheory.Books.FoML2

/-- Compatibility alias to concept-first kernel interface. -/
abbrev KernelFunction := MLTheory.Methods.Learning.KernelFunction

/-- Compatibility alias for PSD-kernel predicate placeholder. -/
def isPSDKernel {X : Type*} (k : KernelFunction X) : Prop :=
  MLTheory.Methods.Learning.isPSDKernel k

/-- Compatibility alias to kernel learning problem interface. -/
abbrev KernelLearningProblem := MLTheory.Methods.Learning.KernelLearningProblem

/-- Compatibility alias for representer theorem placeholder. -/
abbrev representerTheoremPlaceholder : Prop :=
  MLTheory.Methods.Learning.representerTheoremPlaceholder

end MLTheory.Books.FoML2
