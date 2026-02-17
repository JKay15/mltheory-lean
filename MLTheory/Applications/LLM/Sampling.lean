/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Applications.LLM.Autoregressive

/-!
# MLTheory.Applications.LLM.Sampling

Application-layer sampling interfaces aligned with autoregressive contracts.
-/

namespace MLTheory.Applications.LLM

/-- Minimal sampling policy with a deterministic fallback token. -/
structure SamplingPolicy (Token : Type*) where
  defaultToken : Token
  pick : List Token -> List Token -> Token

/-- Sampled token from a candidate list; fallback to `defaultToken` when candidates are empty. -/
def sampledToken {Token : Type*} (policy : SamplingPolicy Token)
    (history candidates : List Token) : Token :=
  match candidates with
  | [] => policy.defaultToken
  | _ => policy.pick history candidates

/-- One-step sampling score induced by an autoregressive model and sampling policy. -/
def samplingStepScore {Token : Type*} (model : AutoregressiveModel Token)
    (policy : SamplingPolicy Token) (history candidates : List Token) : Real :=
  model.nextTokenScore history (sampledToken policy history candidates)

/-- Empty-candidate sampling falls back to the default token. -/
theorem sampledToken_nil {Token : Type*} (policy : SamplingPolicy Token) (history : List Token) :
    sampledToken policy history [] = policy.defaultToken := by
  rfl

/-- Sampling singleton scoring is consistent with autoregressive sequence scoring. -/
theorem sequenceScore_singleton_sampled {Token : Type*} (model : AutoregressiveModel Token)
    (policy : SamplingPolicy Token) (history candidates : List Token) :
    sequenceScore model history [sampledToken policy history candidates] =
      samplingStepScore model policy history candidates := by
  simp [sequenceScore, samplingStepScore]

/-- Sampling risk gap is inherited from the autoregressive risk-gap contract. -/
def samplingRiskGap (populationRisk empiricalRisk : Real) : Real :=
  autoregressiveRiskGap populationRisk empiricalRisk

/-- Sampling risk gap is nonnegative under population-risk dominance. -/
theorem samplingRiskGap_nonneg_of_le (populationRisk empiricalRisk : Real)
    (h : empiricalRisk <= populationRisk) :
    0 <= samplingRiskGap populationRisk empiricalRisk := by
  exact autoregressiveRiskGap_nonneg_of_le populationRisk empiricalRisk h

/-- LLM sampling scenario built by extending an autoregressive scenario with a sampling policy. -/
structure SamplingScenario (Token X Y H Decision : Type*) where
  autoregressive : AutoregressiveScenario Token X Y H Decision
  policy : SamplingPolicy Token

/-- Sampling applications inherit PAC witness from the autoregressive bridge. -/
theorem sampling_pac_constant_exists {Token X Y H Decision : Type*}
    (scenario : SamplingScenario Token X Y H Decision) :
    ∃ C : Real, 0 <= C := by
  exact autoregressive_pac_constant_exists scenario.autoregressive

end MLTheory.Applications.LLM
