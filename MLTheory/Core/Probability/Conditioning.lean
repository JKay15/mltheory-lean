/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib

/-!
# MLTheory.Core.Probability.Conditioning

Minimal conditioning interfaces intended for reuse by learning and concentration modules.
-/

namespace MLTheory.Core.Probability

/-- Conditioning event wrapper used by higher-level probability interfaces. -/
def conditionedEvent {Ω : Type*} (s t : Set Ω) : Set Ω := s ∩ t

/-- Conditioned event is always a subset of the left event. -/
theorem conditionedEvent_subset_left {Ω : Type*} (s t : Set Ω) :
    conditionedEvent s t ⊆ s := by
  intro x hx
  exact hx.1

/-- Conditioned event is always a subset of the right event. -/
theorem conditionedEvent_subset_right {Ω : Type*} (s t : Set Ω) :
    conditionedEvent s t ⊆ t := by
  intro x hx
  exact hx.2

/-- Scalar helper for conditioning-style mass decompositions. -/
def condWeight (mass witness : Real) : Real := mass * witness

/-- Nonnegativity hook used by later probability inequalities. -/
theorem condWeight_nonneg {mass witness : Real} (hmass : 0 <= mass) (hwitness : 0 <= witness) :
    0 <= condWeight mass witness := by
  exact mul_nonneg hmass hwitness

end MLTheory.Core.Probability
