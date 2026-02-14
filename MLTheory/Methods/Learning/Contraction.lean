/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Learning.Rademacher

/-!
# MLTheory.Methods.Learning.Contraction

Contraction-style transfer lemmas on top of Rademacher interfaces.
-/

open scoped BigOperators

namespace MLTheory.Methods.Learning

open MLTheory.Core.Learning

/-- One-Lipschitz-at-zero interface for scalar activations. -/
def OneLipschitzAtZero (φ : Real -> Real) : Prop :=
  φ 0 = 0 ∧ ∀ a b : Real, |φ a - φ b| ≤ |a - b|

theorem lip_contraction_abs {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (φ : Real -> Real) (L : Real)
    (hContract :
      ∀ σ : SignVector n,
        empiricalRadAbs n (fun h t => φ (F h t)) x σ ≤ L * empiricalRadAbs n F x σ) :
    radAbs n (fun h t => φ (F h t)) x ≤ L * radAbs n F x := by
  classical
  unfold radAbs
  have hcoef_nonneg : 0 ≤ (1 / (Fintype.card (SignVector n) : Real)) := by positivity
  calc
    (1 / (Fintype.card (SignVector n) : Real)) *
        ∑ σ : SignVector n, empiricalRadAbs n (fun h t => φ (F h t)) x σ
      ≤ (1 / (Fintype.card (SignVector n) : Real)) *
        ∑ σ : SignVector n, L * empiricalRadAbs n F x σ := by
          refine mul_le_mul_of_nonneg_left ?_ hcoef_nonneg
          exact Finset.sum_le_sum (fun σ _ => hContract σ)
    _ = L * ((1 / (Fintype.card (SignVector n) : Real)) *
        ∑ σ : SignVector n, empiricalRadAbs n F x σ) := by
          simp [Finset.mul_sum, mul_left_comm]
    _ = L * radAbs n F x := by rfl

theorem lip_contraction_std {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (φ : Real -> Real) (L : Real)
    (hContract :
      ∀ σ : SignVector n,
        empiricalRadStd n (fun h t => φ (F h t)) x σ ≤ L * empiricalRadStd n F x σ) :
    radStd n (fun h t => φ (F h t)) x ≤ L * radStd n F x := by
  classical
  unfold radStd
  have hcoef_nonneg : 0 ≤ (1 / (Fintype.card (SignVector n) : Real)) := by positivity
  calc
    (1 / (Fintype.card (SignVector n) : Real)) *
        ∑ σ : SignVector n, empiricalRadStd n (fun h t => φ (F h t)) x σ
      ≤ (1 / (Fintype.card (SignVector n) : Real)) *
        ∑ σ : SignVector n, L * empiricalRadStd n F x σ := by
          refine mul_le_mul_of_nonneg_left ?_ hcoef_nonneg
          exact Finset.sum_le_sum (fun σ _ => hContract σ)
    _ = L * ((1 / (Fintype.card (SignVector n) : Real)) *
        ∑ σ : SignVector n, empiricalRadStd n F x σ) := by
          simp [Finset.mul_sum, mul_left_comm]
    _ = L * radStd n F x := by rfl

end MLTheory.Methods.Learning
