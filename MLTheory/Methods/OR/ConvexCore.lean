/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib

/-!
# MLTheory.Methods.OR.ConvexCore

Minimal OR/convex-optimization interfaces used by OCO and bandit methods.
-/

namespace MLTheory.Methods.OR

/-- Objective function wrapper for OR/convex pipelines. -/
structure ConvexObjective (α : Type*) where
  eval : α -> Real

/-- Feasible-set wrapper used by constrained optimization modules. -/
structure FeasibleSet (α : Type*) where
  carrier : Set α

/-- Objective gap relative to a reference point. -/
def objectiveGap {α : Type*} (f : α -> Real) (x xRef : α) : Real := f x - f xRef

/-- Objective gap at the same point is zero. -/
theorem objectiveGap_self {α : Type*} (f : α -> Real) (x : α) :
    objectiveGap f x x = 0 := by
  simp [objectiveGap]

/-- Objective gap is nonnegative when the reference is no larger than current value. -/
theorem objectiveGap_nonneg_of_le {α : Type*} (f : α -> Real) (x xRef : α)
    (h : f xRef <= f x) :
    0 <= objectiveGap f x xRef := by
  exact sub_nonneg.mpr h

/-- Scaling preserves objective-gap ordering under nonnegative multipliers. -/
theorem scaled_objectiveGap_nonneg {α : Type*} (f : α -> Real) (x xRef : α) (c : Real)
    (h : f xRef <= f x) (hc : 0 <= c) :
    0 <= c * objectiveGap f x xRef := by
  exact mul_nonneg hc (objectiveGap_nonneg_of_le f x xRef h)

end MLTheory.Methods.OR
