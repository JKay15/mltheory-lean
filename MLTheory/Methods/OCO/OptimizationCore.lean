/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib
import MLTheory.Methods.OR.ConvexCore

/-!
# MLTheory.Methods.OCO.OptimizationCore

Minimal OCO abstractions: problem definition, comparator baseline, and online update rule.
-/

namespace MLTheory.Methods.OCO

/-- OCO problem wrapper with round-indexed loss functions. -/
structure OCOProblem (Decision : Type*) where
  loss : Nat -> Decision -> Real

/-- Static comparator abstraction used for regret baselines. -/
structure Comparator (Decision : Type*) where
  ref : Decision

/-- Generic online update rule abstraction for iterative algorithms. -/
structure OnlineUpdate (State Decision : Type*) where
  init : State
  step : Nat -> State -> Decision -> State

/-- One-round regret against a comparator decision. -/
def instantRegret {Decision : Type*} (ℓ : Decision -> Real) (x : Decision)
    (c : Comparator Decision) : Real :=
  ℓ x - ℓ c.ref

/-- Cumulative regret over `n` rounds with fixed comparator baseline. -/
def cumulativeRegret {Decision : Type*} (n : Nat) (losses : Fin n -> Decision -> Real)
    (choices : Fin n -> Decision) (c : Comparator Decision) : Real :=
  ∑ t : Fin n, instantRegret (losses t) (choices t) c

/-- Choosing the comparator itself yields zero instant regret. -/
theorem instantRegret_self {Decision : Type*} (ℓ : Decision -> Real) (c : Comparator Decision) :
    instantRegret ℓ c.ref c = 0 := by
  simp [instantRegret]

/-- Instant regret is nonnegative when comparator loss is no larger than chosen loss. -/
theorem instantRegret_nonneg_of_le {Decision : Type*} (ℓ : Decision -> Real) (x : Decision)
    (c : Comparator Decision) (h : ℓ c.ref <= ℓ x) :
    0 <= instantRegret ℓ x c := by
  exact sub_nonneg.mpr h

/-- Cumulative regret is nonnegative under round-wise comparator dominance. -/
theorem cumulativeRegret_nonneg_of_le {Decision : Type*} {n : Nat}
    (losses : Fin n -> Decision -> Real) (choices : Fin n -> Decision)
    (c : Comparator Decision) (h : ∀ t : Fin n, losses t c.ref <= losses t (choices t)) :
    0 <= cumulativeRegret n losses choices c := by
  unfold cumulativeRegret
  exact Finset.sum_nonneg (fun t _ => instantRegret_nonneg_of_le (losses t) (choices t) c (h t))

/-- OCO instant regret is exactly OR objective gap under fixed comparator. -/
theorem instantRegret_eq_objectiveGap {Decision : Type*} (ℓ : Decision -> Real) (x : Decision)
    (c : Comparator Decision) :
    instantRegret ℓ x c = MLTheory.Methods.OR.objectiveGap ℓ x c.ref := by
  rfl

end MLTheory.Methods.OCO
