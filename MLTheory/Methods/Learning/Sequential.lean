/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.OCO.OptimizationCore

/-!
# MLTheory.Methods.Learning.Sequential

Minimal sequential-learning interfaces with prefix regret and OCO bridge.
-/

namespace MLTheory.Methods.Learning

/-- Sequential-learning scenario with round-indexed loss and data stream. -/
structure SequentialLearningProblem (X Y H : Type*) where
  loss : Nat -> H -> X -> Y -> Real
  dataX : Nat -> X
  dataY : Nat -> Y

/-- One-round sequential loss for hypothesis `h` at round `t`. -/
def sequentialInstantLoss {X Y H : Type*}
    (problem : SequentialLearningProblem X Y H)
    (t : Nat) (h : H) : Real :=
  problem.loss t h (problem.dataX t) (problem.dataY t)

/-- Cumulative sequential loss of a fixed hypothesis. -/
def sequentialCumulativeLoss {X Y H : Type*}
    (problem : SequentialLearningProblem X Y H) (n : Nat) (h : H) : Real :=
  ∑ t : Fin n, sequentialInstantLoss problem t h

/-- Sequential regret of `h` relative to reference hypothesis `hRef`. -/
def sequentialRegret {X Y H : Type*}
    (problem : SequentialLearningProblem X Y H) (n : Nat) (h hRef : H) : Real :=
  sequentialCumulativeLoss problem n h - sequentialCumulativeLoss problem n hRef

/-- Sequential regret is nonnegative under round-wise reference dominance. -/
theorem sequentialRegret_nonneg_of_le {X Y H : Type*}
    (problem : SequentialLearningProblem X Y H) {n : Nat} (h hRef : H)
    (hle : ∀ t : Fin n,
      sequentialInstantLoss problem t hRef <= sequentialInstantLoss problem t h) :
    0 <= sequentialRegret problem n h hRef := by
  unfold sequentialRegret sequentialCumulativeLoss
  exact sub_nonneg.mpr <| Finset.sum_le_sum (fun t _ => hle t)

/-- Prefix regret for a round-wise chosen hypothesis sequence. -/
def sequentialPrefixRegret {X Y H : Type*}
    (problem : SequentialLearningProblem X Y H) (n : Nat)
    (choices : Fin n -> H) (hRef : H) : Real :=
  Finset.sum Finset.univ
    (fun t : Fin n =>
      sequentialInstantLoss problem t (choices t) -
        sequentialInstantLoss problem t hRef)

/-- Prefix regret is nonnegative under round-wise reference dominance. -/
theorem sequentialPrefixRegret_nonneg_of_le {X Y H : Type*}
    (problem : SequentialLearningProblem X Y H) {n : Nat}
    (choices : Fin n -> H) (hRef : H)
    (hle : ∀ t : Fin n,
      sequentialInstantLoss problem t hRef <= sequentialInstantLoss problem t (choices t)) :
    0 <= sequentialPrefixRegret problem n choices hRef := by
  simpa [sequentialPrefixRegret] using
    (Finset.sum_nonneg (fun t _ => sub_nonneg.mpr (hle t)))

/-- Average prefix regret used for online-to-batch style statements. -/
noncomputable def averagePrefixRegret {X Y H : Type*}
    (problem : SequentialLearningProblem X Y H) (n : Nat)
    (choices : Fin n -> H) (hRef : H) : Real :=
  sequentialPrefixRegret problem n choices hRef / n

/-- Average prefix regret is nonnegative under round-wise reference dominance. -/
theorem averagePrefixRegret_nonneg_of_le {X Y H : Type*}
    (problem : SequentialLearningProblem X Y H) {n : Nat}
    (choices : Fin n -> H) (hRef : H)
    (hle : ∀ t : Fin n,
      sequentialInstantLoss problem t hRef <= sequentialInstantLoss problem t (choices t)) :
    0 <= averagePrefixRegret problem n choices hRef := by
  unfold averagePrefixRegret
  exact div_nonneg
    (sequentialPrefixRegret_nonneg_of_le problem choices hRef hle)
    (Nat.cast_nonneg n)

/-- OCO-style view of sequential prefix regret. -/
def sequentialRegretFromOCO {X Y H : Type*}
    (problem : SequentialLearningProblem X Y H) (n : Nat)
    (choices : Fin n -> H) (hRef : H) : Real :=
  MLTheory.Methods.OCO.cumulativeRegret n
    (fun t h => sequentialInstantLoss problem t h)
    choices
    ⟨hRef⟩

/-- OCO view matches sequential prefix regret by definition unfolding. -/
theorem sequentialRegretFromOCO_eq_prefix {X Y H : Type*}
    (problem : SequentialLearningProblem X Y H) (n : Nat)
    (choices : Fin n -> H) (hRef : H) :
    sequentialRegretFromOCO problem n choices hRef =
      sequentialPrefixRegret problem n choices hRef := by
  unfold sequentialRegretFromOCO
  unfold MLTheory.Methods.OCO.cumulativeRegret
  unfold MLTheory.Methods.OCO.instantRegret
  simp [sequentialPrefixRegret]

/-- OCO view is nonnegative under round-wise reference dominance. -/
theorem sequentialRegretFromOCO_nonneg_of_le {X Y H : Type*}
    (problem : SequentialLearningProblem X Y H) {n : Nat}
    (choices : Fin n -> H) (hRef : H)
    (hle : ∀ t : Fin n,
      sequentialInstantLoss problem t hRef <= sequentialInstantLoss problem t (choices t)) :
    0 <= sequentialRegretFromOCO problem n choices hRef := by
  unfold sequentialRegretFromOCO
  exact MLTheory.Methods.OCO.cumulativeRegret_nonneg_of_le
    (losses := fun t h => sequentialInstantLoss problem t h)
    (choices := choices)
    ⟨hRef⟩
    hle

end MLTheory.Methods.Learning
