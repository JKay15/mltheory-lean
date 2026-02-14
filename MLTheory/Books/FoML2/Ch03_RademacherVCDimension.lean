/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.Learning.Capacity
import MLTheory.Core.Learning.FunctionClass
import MLTheory.Methods.Learning.Rademacher
import MLTheory.Methods.Learning.Contraction

/-!
# MLTheory.Books.FoML2.Ch03_RademacherVCDimension

Book-index compatibility adapters that re-export canonical MLTheory modules.
-/

namespace MLTheory.Books.FoML2

noncomputable section

/-- Compatibility alias to concept-first capacity interface. -/
abbrev CapacityBridge := MLTheory.Core.Learning.CapacityBridge

/-- Compatibility alias for VC-dimension placeholder. -/
abbrev vcDimensionBound : Prop :=
  MLTheory.Core.Learning.vcDimensionBound

/-- Compatibility alias for hypothesis-class representation. -/
abbrev HypothesisClass (H X : Type*) := MLTheory.Core.Learning.HypothesisClass H X

/-- Compatibility alias for finite-sample representation. -/
abbrev Sample (X : Type*) (n : Nat) := MLTheory.Core.Learning.Sample X n

/-- Compatibility alias for finite sign vectors. -/
abbrev SignVector (n : Nat) := MLTheory.Core.Learning.SignVector n

/-- Compatibility alias for symmetric-class condition. -/
abbrev NegClosed {H X : Type*} (F : HypothesisClass H X) : Prop :=
  MLTheory.Core.Learning.NegClosed F

/-- Compatibility alias for standard empirical Rademacher complexity. -/
abbrev empiricalRadStd {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (σ : SignVector n) : Real :=
  MLTheory.Methods.Learning.empiricalRadStd n F x σ

/-- Compatibility alias for absolute empirical Rademacher complexity. -/
abbrev empiricalRadAbs {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (σ : SignVector n) : Real :=
  MLTheory.Methods.Learning.empiricalRadAbs n F x σ

/-- Compatibility alias for standard Rademacher complexity. -/
abbrev radStd {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) : Real :=
  MLTheory.Methods.Learning.radStd n F x

/-- Compatibility alias for absolute Rademacher complexity. -/
abbrev radAbs {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) : Real :=
  MLTheory.Methods.Learning.radAbs n F x

/-- Compatibility alias for the baseline inequality `radStd ≤ radAbs`. -/
abbrev radStd_le_radAbs {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) :
    radStd n F x ≤ radAbs n F x :=
  MLTheory.Methods.Learning.radStd_le_radAbs n F x

/-- Compatibility alias for symmetric-class equality `radAbs = radStd`. -/
abbrev radAbs_eq_radStd_of_symmetric {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (hSymm : NegClosed F) :
    radAbs n F x = radStd n F x :=
  MLTheory.Methods.Learning.radAbs_eq_radStd_of_symmetric n F x hSymm

/-- Compatibility alias for standard contraction bridge. -/
abbrev lip_contraction_std {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (φ : Real -> Real) (L : Real)
    (hContract :
      ∀ σ : SignVector n,
        empiricalRadStd n (fun h t => φ (F h t)) x σ ≤ L * empiricalRadStd n F x σ) :
    radStd n (fun h t => φ (F h t)) x ≤ L * radStd n F x :=
  MLTheory.Methods.Learning.lip_contraction_std n F x φ L hContract

/-- Compatibility alias for absolute contraction bridge. -/
abbrev lip_contraction_abs {H X : Type*} [Fintype H] [Nonempty H]
    (n : Nat) (F : HypothesisClass H X) (x : Sample X n) (φ : Real -> Real) (L : Real)
    (hContract :
      ∀ σ : SignVector n,
        empiricalRadAbs n (fun h t => φ (F h t)) x σ ≤ L * empiricalRadAbs n F x σ) :
    radAbs n (fun h t => φ (F h t)) x ≤ L * radAbs n F x :=
  MLTheory.Methods.Learning.lip_contraction_abs n F x φ L hContract

end

end MLTheory.Books.FoML2
