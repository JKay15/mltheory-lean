/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib
import MLTheory.Methods.Bandits.Foundations

/-!
# MLTheory.Methods.Bandits.Adversarial

Minimal adversarial-bandit interfaces aligned with existing regret foundations.
-/

namespace MLTheory.Methods.Bandits

/-- Adversarial bandit model with round-indexed reward values. -/
structure AdversarialBanditModel (Arm : Type*) where
  reward : Nat -> Arm -> Real

/-- Round-wise adversarial regret against a fixed reference arm. -/
def adversarialRoundRegret {Arm : Type*} (model : AdversarialBanditModel Arm)
    (t : Nat) (bestArm chosenArm : Arm) : Real :=
  regret (model.reward t bestArm) (model.reward t chosenArm)

/-- Round-wise adversarial regret is nonnegative when chosen reward is below reference reward. -/
theorem adversarialRoundRegret_nonneg_of_le {Arm : Type*} (model : AdversarialBanditModel Arm)
    (t : Nat) (bestArm chosenArm : Arm)
    (h : model.reward t chosenArm <= model.reward t bestArm) :
    0 <= adversarialRoundRegret model t bestArm chosenArm := by
  exact regret_nonneg_of_le h

/-- Cumulative adversarial regret over `n` rounds. -/
def adversarialCumulativeRegret {Arm : Type*} (model : AdversarialBanditModel Arm)
    (n : Nat) (bestArm : Arm) (chosen : Fin n -> Arm) : Real :=
  ∑ t : Fin n, adversarialRoundRegret model t bestArm (chosen t)

/-- Cumulative adversarial regret is nonnegative under round-wise dominance. -/
  theorem adversarialCumulativeRegret_nonneg {Arm : Type*} (model : AdversarialBanditModel Arm)
    {n : Nat} (bestArm : Arm) (chosen : Fin n -> Arm)
    (h : ∀ t : Fin n, model.reward t (chosen t) <= model.reward t bestArm) :
    0 <= adversarialCumulativeRegret model n bestArm chosen := by
  unfold adversarialCumulativeRegret
  exact Finset.sum_nonneg (fun t _ =>
    adversarialRoundRegret_nonneg_of_le model t bestArm (chosen t) (h t))

/-- EXP3-style learning-rate template. -/
noncomputable def exp3LearningRate (numArms horizon : Nat) : Real :=
  Real.sqrt (Real.log (numArms + 1) / (horizon + 1))

/-- EXP3 learning rate is nonnegative. -/
theorem exp3LearningRate_nonneg (numArms horizon : Nat) :
    0 <= exp3LearningRate numArms horizon := by
  exact Real.sqrt_nonneg _

/-- Scalar adversarial pseudo-regret hook that reuses the shared cumulative-regret API. -/
def adversarialScalarCumulativeRegret (bestValue : Real) (n : Nat)
    (chosenValues : Fin n -> Real) : Real :=
  cumulativeRegret bestValue n chosenValues

/-- Scalar adversarial pseudo-regret is definitionally the shared cumulative regret. -/
theorem adversarialScalarCumulativeRegret_eq_foundation (bestValue : Real) (n : Nat)
    (chosenValues : Fin n -> Real) :
    adversarialScalarCumulativeRegret bestValue n chosenValues =
      cumulativeRegret bestValue n chosenValues := by
  rfl

end MLTheory.Methods.Bandits
