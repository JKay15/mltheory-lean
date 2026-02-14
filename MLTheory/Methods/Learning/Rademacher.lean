/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.Learning.FunctionClass

/-!
# MLTheory.Methods.Learning.Rademacher

Reusable Rademacher-complexity definitions and baseline inequalities.
-/

open scoped BigOperators

namespace MLTheory.Methods.Learning

open MLTheory.Core.Learning

noncomputable section

/-- Signed sample average induced by a sign vector. -/
def signedAverage {X : Type*} (n : Nat) (x : Sample X n) (f : X -> Real) (σ : SignVector n) :
    Real :=
  (1 / (n : Real)) * ∑ i : Fin n, rademacherSign (σ i) * f (x i)

lemma signedAverage_neg_of_pointwise {X : Type*} {n : Nat} {x : Sample X n}
    {f g : X -> Real} {σ : SignVector n} (hneg : ∀ t, g t = -f t) :
    signedAverage n x g σ = -signedAverage n x f σ := by
  simp [signedAverage, hneg]

/-- Empirical Rademacher complexity with the standard (non-absolute) supremum. -/
def empiricalRadStd {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (σ : SignVector n) : Real :=
  Finset.sup' Finset.univ Finset.univ_nonempty (fun h => signedAverage n x (F h) σ)

/-- Empirical Rademacher complexity with absolute values inside the class supremum. -/
def empiricalRadAbs {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (σ : SignVector n) : Real :=
  Finset.sup' Finset.univ Finset.univ_nonempty (fun h => |signedAverage n x (F h) σ|)

theorem empiricalRadStd_le_empiricalRadAbs {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (σ : SignVector n) :
    empiricalRadStd n F x σ ≤ empiricalRadAbs n F x σ := by
  classical
  unfold empiricalRadStd empiricalRadAbs
  exact Finset.sup'_le
    (s := Finset.univ)
    (f := fun h : H => signedAverage n x (F h) σ)
    Finset.univ_nonempty
    (by
      intro h hh
      exact (le_abs_self _).trans
        (Finset.le_sup'
          (s := Finset.univ)
          (f := fun h0 : H => |signedAverage n x (F h0) σ|)
          (by exact Finset.mem_univ h)))

theorem empiricalRadAbs_le_empiricalRadStd_of_symmetric {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (σ : SignVector n)
    (hSymm : NegClosed F) :
    empiricalRadAbs n F x σ ≤ empiricalRadStd n F x σ := by
  classical
  unfold empiricalRadAbs empiricalRadStd
  exact Finset.sup'_le
    (s := Finset.univ)
    (f := fun h : H => |signedAverage n x (F h) σ|)
    Finset.univ_nonempty
    (by
      intro h hh
      by_cases hnonneg : 0 ≤ signedAverage n x (F h) σ
      · simpa [abs_of_nonneg hnonneg] using
          (Finset.le_sup'
            (s := Finset.univ)
            (f := fun h0 : H => signedAverage n x (F h0) σ)
            (by exact Finset.mem_univ h) :
            signedAverage n x (F h) σ ≤
              Finset.sup' Finset.univ Finset.univ_nonempty (fun h0 => signedAverage n x (F h0) σ))
      · obtain ⟨hneg, hneg_spec⟩ := hSymm.neg_mem h
        have havg_neg :
            signedAverage n x (F hneg) σ = -signedAverage n x (F h) σ := by
          exact signedAverage_neg_of_pointwise (n := n) (x := x) (σ := σ) (hneg := hneg_spec)
        have hle_neg :
            signedAverage n x (F hneg) σ ≤
              Finset.sup' Finset.univ Finset.univ_nonempty (fun h0 => signedAverage n x (F h0) σ) :=
          Finset.le_sup'
            (s := Finset.univ)
            (f := fun h0 : H => signedAverage n x (F h0) σ)
            (by exact Finset.mem_univ hneg)
        have hsigned_neg : signedAverage n x (F h) σ < 0 := lt_of_not_ge hnonneg
        have habs :
            |signedAverage n x (F h) σ| = -signedAverage n x (F h) σ := abs_of_neg hsigned_neg
        calc
          |signedAverage n x (F h) σ| = -signedAverage n x (F h) σ := habs
          _ = signedAverage n x (F hneg) σ := havg_neg.symm
          _ ≤ Finset.sup' Finset.univ Finset.univ_nonempty (fun h0 => signedAverage n x (F h0) σ) :=
            hle_neg)

/-- Symmetric classes have identical standard and absolute empirical complexities. -/
theorem empiricalRadAbs_eq_empiricalRadStd_of_symmetric
    {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (σ : SignVector n)
    (hSymm : NegClosed F) :
    empiricalRadAbs n F x σ = empiricalRadStd n F x σ := by
  exact le_antisymm
    (empiricalRadAbs_le_empiricalRadStd_of_symmetric n F x σ hSymm)
    (empiricalRadStd_le_empiricalRadAbs n F x σ)

/-- Rademacher complexity averaged over all finite sign vectors (standard version). -/
def radStd {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) : Real :=
  (1 / (Fintype.card (SignVector n) : Real)) *
    ∑ σ : SignVector n, empiricalRadStd n F x σ

/-- Rademacher complexity averaged over all finite sign vectors (absolute version). -/
def radAbs {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) : Real :=
  (1 / (Fintype.card (SignVector n) : Real)) *
    ∑ σ : SignVector n, empiricalRadAbs n F x σ

theorem radStd_le_radAbs {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) :
    radStd n F x ≤ radAbs n F x := by
  classical
  unfold radStd radAbs
  have hcoef_nonneg : 0 ≤ (1 / (Fintype.card (SignVector n) : Real)) := by positivity
  refine mul_le_mul_of_nonneg_left ?_ hcoef_nonneg
  exact Finset.sum_le_sum (fun σ _ => empiricalRadStd_le_empiricalRadAbs n F x σ)

theorem radAbs_eq_radStd_of_symmetric {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (hSymm : NegClosed F) :
    radAbs n F x = radStd n F x := by
  unfold radAbs radStd
  simp [empiricalRadAbs_eq_empiricalRadStd_of_symmetric (n := n) (F := F) (x := x), hSymm]

end

end MLTheory.Methods.Learning
