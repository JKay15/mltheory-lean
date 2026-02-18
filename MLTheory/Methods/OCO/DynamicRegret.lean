/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.OCO.OptimizationCore
import MLTheory.Methods.OR.ConvexCore

/-!
# MLTheory.Methods.OCO.DynamicRegret

Minimal dynamic-regret interfaces aligned with `OCO.OptimizationCore`.
-/

namespace MLTheory.Methods.OCO

/-- Dynamic comparator with round-indexed reference decisions. -/
structure DynamicComparator (Decision : Type*) where
  ref : Nat -> Decision

/-- Dynamic one-round regret against round-specific comparator decision. -/
def dynamicInstantRegret {Decision : Type*} (ℓ : Decision -> Real)
    (x xRef : Decision) : Real :=
  ℓ x - ℓ xRef

/-- Dynamic one-round regret is nonnegative when comparator loss is no larger. -/
theorem dynamicInstantRegret_nonneg_of_le {Decision : Type*} (ℓ : Decision -> Real)
    (x xRef : Decision) (h : ℓ xRef <= ℓ x) :
    0 <= dynamicInstantRegret ℓ x xRef := by
  exact sub_nonneg.mpr h

/-- Dynamic cumulative regret over `n` rounds. -/
def dynamicCumulativeRegret {Decision : Type*} (n : Nat)
    (losses : Fin n -> Decision -> Real) (choices : Fin n -> Decision)
    (u : DynamicComparator Decision) : Real :=
  ∑ t : Fin n, dynamicInstantRegret (losses t) (choices t) (u.ref t)

/-- Dynamic cumulative regret is nonnegative under round-wise comparator dominance. -/
theorem dynamicCumulativeRegret_nonneg_of_le {Decision : Type*} {n : Nat}
    (losses : Fin n -> Decision -> Real) (choices : Fin n -> Decision)
    (u : DynamicComparator Decision)
    (h : ∀ t : Fin n, losses t (u.ref t) <= losses t (choices t)) :
    0 <= dynamicCumulativeRegret n losses choices u := by
  unfold dynamicCumulativeRegret
  refine Finset.sum_nonneg ?_
  intro t _
  exact dynamicInstantRegret_nonneg_of_le (losses t) (choices t) (u.ref t) (h t)

/-- Embed a static comparator as a dynamic comparator. -/
def staticToDynamicComparator {Decision : Type*}
    (c : Comparator Decision) : DynamicComparator Decision where
  ref := fun _ => c.ref

/-- Dynamic regret reduces to static cumulative regret for constant comparators. -/
theorem dynamicCumulativeRegret_eq_static {Decision : Type*} (n : Nat)
    (losses : Fin n -> Decision -> Real) (choices : Fin n -> Decision)
    (c : Comparator Decision) :
    dynamicCumulativeRegret n losses choices (staticToDynamicComparator c) =
      cumulativeRegret n losses choices c := by
  unfold dynamicCumulativeRegret cumulativeRegret dynamicInstantRegret instantRegret
  simp [staticToDynamicComparator]

/-- Average dynamic regret over `n` rounds. -/
noncomputable def averageDynamicRegret {Decision : Type*} (n : Nat)
    (losses : Fin n -> Decision -> Real) (choices : Fin n -> Decision)
    (u : DynamicComparator Decision) : Real :=
  dynamicCumulativeRegret n losses choices u / n

/-- Average dynamic regret is nonnegative under round-wise comparator dominance. -/
theorem averageDynamicRegret_nonneg_of_le {Decision : Type*} {n : Nat}
    (losses : Fin n -> Decision -> Real) (choices : Fin n -> Decision)
    (u : DynamicComparator Decision)
    (h : ∀ t : Fin n, losses t (u.ref t) <= losses t (choices t)) :
    0 <= averageDynamicRegret n losses choices u := by
  unfold averageDynamicRegret
  exact div_nonneg (dynamicCumulativeRegret_nonneg_of_le losses choices u h)
    (Nat.cast_nonneg n)

/-- Dynamic one-round regret is exactly OR objective gap for that round loss. -/
theorem dynamicInstantRegret_eq_objectiveGap {Decision : Type*} (ℓ : Decision -> Real)
    (x xRef : Decision) :
    dynamicInstantRegret ℓ x xRef = MLTheory.Methods.OR.objectiveGap ℓ x xRef := by
  rfl

/-- Comparator-movement cost under a user-provided decision distance. -/
def comparatorMove {Decision : Type*} (dist : Decision -> Decision -> Real)
    (u : DynamicComparator Decision) (t : Nat) : Real :=
  dist (u.ref t) (u.ref (t + 1))

/-- Comparator-movement cost is nonnegative when the distance is nonnegative. -/
theorem comparatorMove_nonneg_of_dist_nonneg {Decision : Type*}
    (dist : Decision -> Decision -> Real)
    (hDist : ∀ a b : Decision, 0 <= dist a b)
    (u : DynamicComparator Decision) (t : Nat) :
    0 <= comparatorMove dist u t := by
  exact hDist (u.ref t) (u.ref (t + 1))

end MLTheory.Methods.OCO
