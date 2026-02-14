/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.Learning.PAC
import MLTheory.Methods.Learning.Rademacher

/-!
# MLTheory.Methods.Learning.GeneralizationTools

Generic PAC + concentration bridge lemmas used across books and case studies.
-/

open scoped BigOperators

namespace MLTheory.Methods.Learning

open MeasureTheory

theorem pac_badEvent_union_bound {Ω H : Type*} [MeasurableSpace Ω] [Fintype H]
    (μ : Measure Ω) (bad : H -> Set Ω) :
    μ (⋃ h : H, bad h) ≤ ∑ h : H, μ (bad h) := by
  simpa using measure_iUnion_fintype_le μ bad

theorem pac_badEvent_from_concentration {Ω H : Type*} [MeasurableSpace Ω] [Fintype H]
    (μ : Measure Ω) (bad : H -> Set Ω) (tail : H -> ENNReal)
    (hTail : ∀ h : H, μ (bad h) ≤ tail h) :
    μ (⋃ h : H, bad h) ≤ ∑ h : H, tail h := by
  calc
    μ (⋃ h : H, bad h) ≤ ∑ h : H, μ (bad h) := pac_badEvent_union_bound μ bad
    _ ≤ ∑ h : H, tail h := Finset.sum_le_sum (fun h _ => hTail h)

theorem pac_badEvent_uniform_bound {Ω H : Type*} [MeasurableSpace Ω] [Fintype H]
    (μ : Measure Ω) (bad : H -> Set Ω) (δ : ENNReal)
    (hδ : ∀ h : H, μ (bad h) ≤ δ) :
    μ (⋃ h : H, bad h) ≤ (Fintype.card H : ENNReal) * δ := by
  calc
    μ (⋃ h : H, bad h) ≤ ∑ h : H, μ (bad h) := pac_badEvent_union_bound μ bad
    _ ≤ ∑ h : H, δ := Finset.sum_le_sum (fun h _ => hδ h)
    _ = (Fintype.card H : ENNReal) * δ := by simp

end MLTheory.Methods.Learning
