/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib
import MLTheory.Core.Probability.Conditioning

/-!
# MLTheory.Core.Probability.BasicMeasure

Minimal measure-theoretic interfaces for event mass and basic monotonicity bounds.
-/

namespace MLTheory.Core.Probability

/-- Measurable-event predicate exposed as a probability-core API surface. -/
def isMeasurableEvent {Ω : Type*} [MeasurableSpace Ω] (s : Set Ω) : Prop :=
  MeasurableSet s

/-- Event mass wrapper for reuse by upper layers. -/
def eventMass {Ω : Type*} [MeasurableSpace Ω]
    (μ : MeasureTheory.Measure Ω) (s : Set Ω) : ENNReal :=
  μ s

/-- Event mass is monotone with set inclusion. -/
theorem eventMass_mono {Ω : Type*} [MeasurableSpace Ω]
    (μ : MeasureTheory.Measure Ω)
    {s t : Set Ω} (hsub : s ⊆ t) :
    eventMass μ s <= eventMass μ t := by
  exact MeasureTheory.measure_mono hsub

/-- Event mass of union is bounded by sum of event masses. -/
theorem eventMass_union_le {Ω : Type*} [MeasurableSpace Ω]
    (μ : MeasureTheory.Measure Ω)
    (s t : Set Ω) :
    eventMass μ (s ∪ t) <= eventMass μ s + eventMass μ t := by
  exact MeasureTheory.measure_union_le s t

/-- Conditioned event mass is bounded by left-event mass. -/
theorem conditionedEvent_mass_le_left {Ω : Type*} [MeasurableSpace Ω]
    (μ : MeasureTheory.Measure Ω) (s t : Set Ω) :
    eventMass μ (conditionedEvent s t) <= eventMass μ s := by
  exact eventMass_mono μ (conditionedEvent_subset_left s t)

/-- Conditioned event mass is bounded by right-event mass. -/
theorem conditionedEvent_mass_le_right {Ω : Type*} [MeasurableSpace Ω]
    (μ : MeasureTheory.Measure Ω) (s t : Set Ω) :
    eventMass μ (conditionedEvent s t) <= eventMass μ t := by
  exact eventMass_mono μ (conditionedEvent_subset_right s t)

end MLTheory.Core.Probability
