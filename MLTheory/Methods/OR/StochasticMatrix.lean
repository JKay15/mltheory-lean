/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib
import MLTheory.Methods.OR.ConvexCore

/-!
# MLTheory.Methods.OR.StochasticMatrix

Minimal stochastic-matrix interfaces aligned with `OR.ConvexCore`.
-/

namespace MLTheory.Methods.OR

/-- Stochastic-matrix optimization problem over finite state space `Fin n`. -/
structure StochasticMatrixProblem (n : Nat) where
  transition : Matrix (Fin n) (Fin n) Real

/-- Row mass of transition row `i`. -/
def rowMass {n : Nat} (problem : StochasticMatrixProblem n) (i : Fin n) : Real :=
  Finset.sum Finset.univ (fun j => problem.transition i j)

/-- Row mass is nonnegative when all entries in that row are nonnegative. -/
theorem rowMass_nonneg_of_nonneg_entries {n : Nat} (problem : StochasticMatrixProblem n)
    (i : Fin n)
    (h : ∀ j : Fin n, 0 <= problem.transition i j) :
    0 <= rowMass problem i := by
  exact Finset.sum_nonneg (fun j _ => h j)

/-- Row-mass gap reusing `ConvexCore.objectiveGap`. -/
def rowMassGap {n : Nat} (problem : StochasticMatrixProblem n)
    (i iRef : Fin n) : Real :=
  objectiveGap (rowMass problem) i iRef

/-- Row-mass gap at the same row is zero. -/
theorem rowMassGap_self {n : Nat} (problem : StochasticMatrixProblem n) (i : Fin n) :
    rowMassGap problem i i = 0 := by
  simpa [rowMassGap] using objectiveGap_self (rowMass problem) i

/-- Row-mass gap is nonnegative when reference row mass is no larger. -/
theorem rowMassGap_nonneg_of_le {n : Nat} (problem : StochasticMatrixProblem n)
    (i iRef : Fin n) (h : rowMass problem iRef <= rowMass problem i) :
    0 <= rowMassGap problem i iRef := by
  simpa [rowMassGap] using objectiveGap_nonneg_of_le (rowMass problem) i iRef h

/-- Entrywise absolute deviation from a target matrix. -/
def entrywiseDeviation {n : Nat} (problem : StochasticMatrixProblem n)
    (target : Matrix (Fin n) (Fin n) Real) : Real :=
  Finset.sum Finset.univ (fun i =>
    Finset.sum Finset.univ (fun j => |problem.transition i j - target i j|))

/-- Entrywise absolute deviation is always nonnegative. -/
theorem entrywiseDeviation_nonneg {n : Nat} (problem : StochasticMatrixProblem n)
    (target : Matrix (Fin n) (Fin n) Real) :
    0 <= entrywiseDeviation problem target := by
  refine Finset.sum_nonneg ?_
  intro i _
  refine Finset.sum_nonneg ?_
  intro j _
  exact abs_nonneg (problem.transition i j - target i j)

/-- Cumulative row-mass gap over a finite horizon. -/
def cumulativeRowMassGap {n horizon : Nat}
    (problem : StochasticMatrixProblem n)
    (rows refRows : Fin horizon -> Fin n) : Real :=
  Finset.sum Finset.univ (fun t => rowMassGap problem (rows t) (refRows t))

/-- Cumulative row-mass gap is nonnegative under round-wise row-mass dominance. -/
theorem cumulativeRowMassGap_nonneg {n horizon : Nat}
    (problem : StochasticMatrixProblem n)
    (rows refRows : Fin horizon -> Fin n)
    (h : ∀ t : Fin horizon, rowMass problem (refRows t) <= rowMass problem (rows t)) :
    0 <= cumulativeRowMassGap problem rows refRows := by
  refine Finset.sum_nonneg ?_
  intro t _
  exact rowMassGap_nonneg_of_le problem (rows t) (refRows t) (h t)

end MLTheory.Methods.OR
