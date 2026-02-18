/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib

/-!
# MLTheory.Methods.Learning.AutomataLanguage

Minimal automata-language learning interfaces: run semantics, 0-1 loss, and risk gap.
-/

namespace MLTheory.Methods.Learning

/-- Automata-language learning setup with hypothesis-indexed finite automata. -/
structure AutomataLanguageProblem (Alpha State H : Type*) where
  init : H -> State
  step : H -> State -> Alpha -> State
  accepting : H -> State -> Bool
  target : List Alpha -> Bool

/-- Run the automaton induced by `h` on a word `w`. -/
def runState {Alpha State H : Type*}
    (problem : AutomataLanguageProblem Alpha State H) (h : H) (w : List Alpha) : State :=
  w.foldl (fun q a => problem.step h q a) (problem.init h)

/-- Acceptance decision of hypothesis `h` on word `w`. -/
def accepts {Alpha State H : Type*}
    (problem : AutomataLanguageProblem Alpha State H) (h : H) (w : List Alpha) : Bool :=
  problem.accepting h (runState problem h w)

/-- Scalar 0-1 loss for binary decisions. -/
def zeroOneLoss (pred target : Bool) : Real :=
  if pred = target then 0 else 1

/-- 0-1 loss is always nonnegative. -/
theorem zeroOneLoss_nonneg (pred target : Bool) : 0 <= zeroOneLoss pred target := by
  unfold zeroOneLoss
  split_ifs <;> norm_num

/-- 0-1 loss is upper-bounded by one. -/
theorem zeroOneLoss_le_one (pred target : Bool) : zeroOneLoss pred target <= 1 := by
  unfold zeroOneLoss
  split_ifs <;> norm_num

/-- Pointwise automata-language loss of hypothesis `h` on word `w`. -/
def languagePointLoss {Alpha State H : Type*}
    (problem : AutomataLanguageProblem Alpha State H) (h : H) (w : List Alpha) : Real :=
  zeroOneLoss (accepts problem h w) (problem.target w)

/-- Pointwise loss is nonnegative. -/
theorem languagePointLoss_nonneg {Alpha State H : Type*}
    (problem : AutomataLanguageProblem Alpha State H) (h : H) (w : List Alpha) :
    0 <= languagePointLoss problem h w := by
  exact zeroOneLoss_nonneg (accepts problem h w) (problem.target w)

/-- Finite-sample empirical risk over a word sample. -/
def languageEmpiricalRisk {Alpha State H : Type*}
    (problem : AutomataLanguageProblem Alpha State H)
    (n : Nat) (samples : Fin n -> List Alpha) (h : H) : Real :=
  ∑ t : Fin n, languagePointLoss problem h (samples t)

/-- Empirical risk is nonnegative. -/
theorem languageEmpiricalRisk_nonneg {Alpha State H : Type*}
    (problem : AutomataLanguageProblem Alpha State H)
    (n : Nat) (samples : Fin n -> List Alpha) (h : H) :
    0 <= languageEmpiricalRisk problem n samples h := by
  unfold languageEmpiricalRisk
  refine Finset.sum_nonneg ?_
  intro t _
  exact languagePointLoss_nonneg problem h (samples t)

/-- Empirical risk gap between `h` and reference `hRef`. -/
def languageRiskGap {Alpha State H : Type*}
    (problem : AutomataLanguageProblem Alpha State H)
    (n : Nat) (samples : Fin n -> List Alpha) (h hRef : H) : Real :=
  languageEmpiricalRisk problem n samples h -
    languageEmpiricalRisk problem n samples hRef

/-- Risk gap is nonnegative when reference loss is pointwise no larger. -/
theorem languageRiskGap_nonneg_of_le {Alpha State H : Type*}
    (problem : AutomataLanguageProblem Alpha State H)
    (n : Nat) (samples : Fin n -> List Alpha) (h hRef : H)
    (hle : ∀ t : Fin n,
      languagePointLoss problem hRef (samples t) <= languagePointLoss problem h (samples t)) :
    0 <= languageRiskGap problem n samples h hRef := by
  unfold languageRiskGap languageEmpiricalRisk
  exact sub_nonneg.mpr <| Finset.sum_le_sum (fun t _ => hle t)

end MLTheory.Methods.Learning
