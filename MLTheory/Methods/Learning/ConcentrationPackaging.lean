/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.Learning.GeneralizationTools

/-!
# MLTheory.Methods.Learning.ConcentrationPackaging

Reusable finite-class concentration packaging tools:
- concentration bundle abstraction,
- union-bound endpoints,
- subgaussian-family constructor.
-/

open scoped BigOperators

namespace MLTheory.Methods.Learning

open MeasureTheory

/-- Generic finite-class concentration bundle. -/
structure FiniteClassConcentrationBundle
    {Ω H : Type*} [MeasurableSpace Ω] [Fintype H] where
  μ : Measure Ω
  bad : H -> Set Ω
  tail : H -> ENNReal
  δ : ENNReal
  hConc : ∀ h : H, μ (bad h) ≤ tail h
  hTailLe : ∀ h : H, tail h ≤ δ

/-- Concentration bundle implies finite-class PAC bad-event sum bound. -/
theorem FiniteClassConcentrationBundle.union_bound
    {Ω H : Type*} [MeasurableSpace Ω] [Fintype H]
    (C : FiniteClassConcentrationBundle (Ω := Ω) (H := H)) :
    C.μ (⋃ h : H, C.bad h) ≤ ∑ h : H, C.tail h :=
  pac_badEvent_from_concentration C.μ C.bad C.tail C.hConc

/-- Concentration bundle implies finite-class PAC bad-event uniform bound. -/
theorem FiniteClassConcentrationBundle.uniform_bound
    {Ω H : Type*} [MeasurableSpace Ω] [Fintype H]
    (C : FiniteClassConcentrationBundle (Ω := Ω) (H := H)) :
    C.μ (⋃ h : H, C.bad h) ≤ (Fintype.card H : ENNReal) * C.δ := by
  calc
    C.μ (⋃ h : H, C.bad h) ≤ ∑ h : H, C.tail h := C.union_bound
    _ ≤ ∑ h : H, C.δ := Finset.sum_le_sum (fun h _ => C.hTailLe h)
    _ = (Fintype.card H : ENNReal) * C.δ := by simp

/-- Convert a real-valued measure bound to an `ENNReal` bound. -/
private lemma measure_le_of_real_bound
    {Ω : Type*} [MeasurableSpace Ω]
    (μ : Measure Ω) [IsFiniteMeasure μ]
    (s : Set Ω) (r : Real)
    (hr0 : 0 ≤ r) (hr : μ.real s ≤ r) :
    μ s ≤ ENNReal.ofReal r := by
  have hne : μ s ≠ ⊤ := measure_ne_top μ s
  have htr : (μ s).toReal ≤ r := by
    simpa [Measure.real_def] using hr
  exact (ENNReal.le_ofReal_iff_toReal_le hne hr0).2 htr

/--
`ENNReal` tail expression used by subgaussian finite-class constructors.
-/
noncomputable def subgaussianTailENN (n : Nat) (c : NNReal) (ε : Real) : ENNReal :=
  ENNReal.ofReal (Real.exp (-(ε ^ 2) / (2 * (n : Real) * (c : Real))))

/--
Build a finite-class concentration bundle from per-hypothesis subgaussian sum tails.
-/
noncomputable def FiniteClassConcentrationBundle.ofSubgaussianFamily
    {Ω H : Type*} [MeasurableSpace Ω] [Fintype H]
    (μ : Measure Ω) [IsFiniteMeasure μ]
    (n : Nat)
    (X : H -> Nat -> Ω -> Real)
    (c : NNReal) (ε : Real) (hε : 0 ≤ ε)
    (hIndep : ∀ h : H, ProbabilityTheory.iIndepFun (X h) μ)
    (hSubG : ∀ h : H, ∀ i < n, ProbabilityTheory.HasSubgaussianMGF (X h i) c μ) :
    FiniteClassConcentrationBundle (Ω := Ω) (H := H) := by
  let tailReal : Real := Real.exp (-(ε ^ 2) / (2 * (n : Real) * (c : Real)))
  let tailENN : ENNReal := ENNReal.ofReal tailReal
  refine
    { μ := μ
      bad := fun h => {ω | ε ≤ ∑ i ∈ Finset.range n, X h i ω}
      tail := fun _ => tailENN
      δ := tailENN
      hConc := ?_
      hTailLe := ?_ }
  · intro h
    have hReal :
        μ.real {ω | ε ≤ ∑ i ∈ Finset.range n, X h i ω} ≤ tailReal := by
      simpa [tailReal] using
        (ProbabilityTheory.HasSubgaussianMGF.measure_sum_range_ge_le_of_iIndepFun
          (h_indep := hIndep h)
          (c := c) (n := n)
          (h_subG := by intro i hi; exact hSubG h i hi)
          (ε := ε) hε)
    have hNonneg : 0 ≤ tailReal := by
      dsimp [tailReal]
      positivity
    exact measure_le_of_real_bound μ _ tailReal hNonneg hReal
  · intro h
    rfl

end MLTheory.Methods.Learning
