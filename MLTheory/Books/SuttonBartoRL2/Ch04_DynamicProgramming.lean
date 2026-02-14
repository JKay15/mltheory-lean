/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.RL.DynamicProgramming

/-!
# MLTheory.Books.SuttonBartoRL2.Ch04_DynamicProgramming

Book-index compatibility adapters that re-export canonical MLTheory modules.
-/

namespace MLTheory.Books.SuttonBartoRL2

/-- Compatibility alias to concept-first value-iteration update. -/
def valueIterationUpdate {State Action : Type*}
    (mdp : MLTheory.Core.RL.FiniteMDP State Action) (v : State -> Real) : State -> Real :=
  MLTheory.Methods.RL.valueIterationUpdate mdp v

/-- Compatibility alias for policy-evaluation placeholder. -/
abbrev policyEvaluationPlaceholder : Prop :=
  MLTheory.Methods.RL.policyEvaluationPlaceholder

/-- Compatibility alias for policy-improvement placeholder. -/
abbrev policyImprovementPlaceholder : Prop :=
  MLTheory.Methods.RL.policyImprovementPlaceholder

/-- Compatibility alias for policy-iteration convergence placeholder. -/
abbrev policyIterationConvergencePlaceholder : Prop :=
  MLTheory.Methods.RL.policyIterationConvergencePlaceholder

end MLTheory.Books.SuttonBartoRL2
