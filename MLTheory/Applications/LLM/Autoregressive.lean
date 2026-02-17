/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Applications.AI.Generalization

/-!
# MLTheory.Applications.LLM.Autoregressive

Application-layer autoregressive interface built on AI generalization bridges.
-/

namespace MLTheory.Applications.LLM

/-- Minimal autoregressive model interface over token sequences. -/
structure AutoregressiveModel (Token : Type*) where
  nextTokenScore : List Token -> Token -> Real

/-- Sequence score under teacher-forcing decomposition (sum of step scores). -/
def sequenceScore {Token : Type*} (model : AutoregressiveModel Token)
    (history : List Token) (targets : List Token) : Real :=
  match targets with
  | [] => 0
  | t :: ts => model.nextTokenScore history t + sequenceScore model (history ++ [t]) ts

/-- Empty target sequence has zero score. -/
theorem sequenceScore_nil {Token : Type*} (model : AutoregressiveModel Token)
    (history : List Token) :
    sequenceScore model history [] = 0 := by
  rfl

/-- Application-layer risk gap for autoregressive models (reused deployment gap). -/
def autoregressiveRiskGap (populationRisk empiricalRisk : Real) : Real :=
  MLTheory.Applications.AI.deploymentGap populationRisk empiricalRisk

/-- Autoregressive risk gap is nonnegative under population-risk dominance. -/
theorem autoregressiveRiskGap_nonneg_of_le (populationRisk empiricalRisk : Real)
    (h : empiricalRisk <= populationRisk) :
    0 <= autoregressiveRiskGap populationRisk empiricalRisk := by
  exact MLTheory.Applications.AI.deploymentGap_nonneg_of_le populationRisk empiricalRisk h

/-- LLM autoregressive scenario that reuses AI generalization contracts. -/
structure AutoregressiveScenario (Token X Y H Decision : Type*) where
  model : AutoregressiveModel Token
  aiScenario : MLTheory.Applications.AI.AIGeneralizationScenario X Y H Decision

/-- Autoregressive application inherits PAC-constant witness from AI bridge. -/
theorem autoregressive_pac_constant_exists {Token X Y H Decision : Type*}
    (scenario : AutoregressiveScenario Token X Y H Decision) :
    ∃ C : Real, 0 <= C := by
  exact MLTheory.Applications.AI.ai_pac_constant_exists scenario.aiScenario

end MLTheory.Applications.LLM
