/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib
import MLTheory.Methods.Learning.AutomataLanguage

/-!
# MLTheory.Methods.Learning.DiscreteModeling

Minimal discrete-modeling interfaces: prediction loss, empirical risk, and comparator gap.
-/

namespace MLTheory.Methods.Learning

/-- Discrete supervised-learning setup with hypothesis-indexed predictor family. -/
structure DiscreteModelingProblem (X Y H : Type*) where
  predict : H -> X -> Y
  target : X -> Y
  loss : Y -> Y -> Real

/-- Pointwise loss of hypothesis `h` on one sample `x`. -/
def discretePointLoss {X Y H : Type*}
    (problem : DiscreteModelingProblem X Y H) (h : H) (x : X) : Real :=
  problem.loss (problem.predict h x) (problem.target x)

/-- Pointwise loss is nonnegative when `loss` is pointwise nonnegative. -/
theorem discretePointLoss_nonneg_of_nonneg {X Y H : Type*}
    (problem : DiscreteModelingProblem X Y H) (h : H) (x : X)
    (hLoss : ∀ y y' : Y, 0 <= problem.loss y y') :
    0 <= discretePointLoss problem h x := by
  exact hLoss (problem.predict h x) (problem.target x)

/-- Finite-sample empirical risk. -/
def discreteEmpiricalRisk {X Y H : Type*}
    (problem : DiscreteModelingProblem X Y H)
    (n : Nat) (samples : Fin n -> X) (h : H) : Real :=
  ∑ t : Fin n, discretePointLoss problem h (samples t)

/-- Empirical risk is nonnegative under pointwise nonnegative loss. -/
theorem discreteEmpiricalRisk_nonneg_of_nonneg {X Y H : Type*}
    (problem : DiscreteModelingProblem X Y H)
    (n : Nat) (samples : Fin n -> X) (h : H)
    (hLoss : ∀ y y' : Y, 0 <= problem.loss y y') :
    0 <= discreteEmpiricalRisk problem n samples h := by
  unfold discreteEmpiricalRisk
  refine Finset.sum_nonneg ?_
  intro t _
  exact discretePointLoss_nonneg_of_nonneg problem h (samples t) hLoss

/-- Reference comparator for risk-gap style discrete guarantees. -/
structure DiscreteComparator (H : Type*) where
  ref : H

/-- Empirical risk gap to a reference comparator. -/
def discreteRiskGap {X Y H : Type*}
    (problem : DiscreteModelingProblem X Y H)
    (n : Nat) (samples : Fin n -> X) (h : H) (c : DiscreteComparator H) : Real :=
  discreteEmpiricalRisk problem n samples h -
    discreteEmpiricalRisk problem n samples c.ref

/-- Risk gap is nonnegative when reference pointwise loss is no larger. -/
theorem discreteRiskGap_nonneg_of_le {X Y H : Type*}
    (problem : DiscreteModelingProblem X Y H)
    (n : Nat) (samples : Fin n -> X) (h : H) (c : DiscreteComparator H)
    (hle : ∀ t : Fin n,
      discretePointLoss problem c.ref (samples t) <=
        discretePointLoss problem h (samples t)) :
    0 <= discreteRiskGap problem n samples h c := by
  unfold discreteRiskGap discreteEmpiricalRisk
  exact sub_nonneg.mpr <| Finset.sum_le_sum (fun t _ => hle t)

/-- Average empirical risk gap. -/
noncomputable def averageDiscreteRiskGap {X Y H : Type*}
    (problem : DiscreteModelingProblem X Y H)
    (n : Nat) (samples : Fin n -> X) (h : H) (c : DiscreteComparator H) : Real :=
  discreteRiskGap problem n samples h c / n

/-- Average risk gap is nonnegative under pointwise reference dominance. -/
theorem averageDiscreteRiskGap_nonneg_of_le {X Y H : Type*}
    (problem : DiscreteModelingProblem X Y H)
    (n : Nat) (samples : Fin n -> X) (h : H) (c : DiscreteComparator H)
    (hle : ∀ t : Fin n,
      discretePointLoss problem c.ref (samples t) <=
        discretePointLoss problem h (samples t)) :
    0 <= averageDiscreteRiskGap problem n samples h c := by
  unfold averageDiscreteRiskGap
  exact div_nonneg
    (discreteRiskGap_nonneg_of_le problem n samples h c hle)
    (Nat.cast_nonneg n)

/-- 0-1-loss specialization bridge to `AutomataLanguage.zeroOneLoss`. -/
theorem discretePointLoss_eq_zeroOneLoss {X H : Type*}
    (problem : DiscreteModelingProblem X Bool H) (h : H) (x : X)
    (hLoss : problem.loss = zeroOneLoss) :
    discretePointLoss problem h x = zeroOneLoss (problem.predict h x) (problem.target x) := by
  simpa [discretePointLoss] using
    congrArg (fun f => f (problem.predict h x) (problem.target x)) hLoss

end MLTheory.Methods.Learning
