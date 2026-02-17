/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib
import MLTheory.Methods.OR.ConvexCore

/-!
# MLTheory.Methods.OR.DiscreteOptimization

Minimal discrete-optimization interfaces aligned with `OR.ConvexCore`.
-/

namespace MLTheory.Methods.OR

/-- Discrete optimization problem with candidate set, objective, and feasibility predicate. -/
structure DiscreteOptimizationProblem (Decision : Type*) where
  candidateSet : Finset Decision
  objective : Decision -> Real
  feasible : Decision -> Prop

/-- Candidate points that satisfy the feasibility predicate. -/
noncomputable def feasibleCandidates {Decision : Type*}
    (problem : DiscreteOptimizationProblem Decision) : Finset Decision :=
  by
    classical
    exact problem.candidateSet.filter problem.feasible

/-- Any element of `feasibleCandidates` is in the original candidate set. -/
theorem mem_candidateSet_of_mem_feasibleCandidates {Decision : Type*}
    (problem : DiscreteOptimizationProblem Decision) (x : Decision)
    (hx : x ∈ feasibleCandidates problem) :
    x ∈ problem.candidateSet := by
  classical
  exact (Finset.mem_filter.mp hx).1

/-- Any element of `feasibleCandidates` satisfies feasibility. -/
theorem feasible_of_mem_feasibleCandidates {Decision : Type*}
    (problem : DiscreteOptimizationProblem Decision) (x : Decision)
    (hx : x ∈ feasibleCandidates problem) :
    problem.feasible x := by
  classical
  exact (Finset.mem_filter.mp hx).2

/-- Discrete objective gap reusing `ConvexCore.objectiveGap`. -/
def discreteObjectiveGap {Decision : Type*}
    (problem : DiscreteOptimizationProblem Decision)
    (chosen reference : Decision) : Real :=
  objectiveGap problem.objective chosen reference

/-- Objective gap at the same point is zero. -/
theorem discreteObjectiveGap_self {Decision : Type*}
    (problem : DiscreteOptimizationProblem Decision) (x : Decision) :
    discreteObjectiveGap problem x x = 0 := by
  simpa [discreteObjectiveGap] using objectiveGap_self problem.objective x

/-- Objective gap is nonnegative when reference is no larger than chosen value. -/
theorem discreteObjectiveGap_nonneg_of_le {Decision : Type*}
    (problem : DiscreteOptimizationProblem Decision)
    (chosen reference : Decision)
    (h : problem.objective reference <= problem.objective chosen) :
    0 <= discreteObjectiveGap problem chosen reference := by
  simpa [discreteObjectiveGap] using
    objectiveGap_nonneg_of_le problem.objective chosen reference h

/-- Cumulative discrete objective gap over a finite horizon. -/
def cumulativeDiscreteObjectiveGap {Decision : Type*}
    (problem : DiscreteOptimizationProblem Decision) (n : Nat)
    (chosen reference : Fin n -> Decision) : Real :=
  ∑ i, discreteObjectiveGap problem (chosen i) (reference i)

/-- Cumulative discrete objective gap is nonnegative under pointwise dominance. -/
theorem cumulativeDiscreteObjectiveGap_nonneg {Decision : Type*}
    (problem : DiscreteOptimizationProblem Decision) {n : Nat}
    (chosen reference : Fin n -> Decision)
    (h : ∀ i : Fin n, problem.objective (reference i) <= problem.objective (chosen i)) :
    0 <= cumulativeDiscreteObjectiveGap problem n chosen reference := by
  refine Finset.sum_nonneg ?_
  intro i _
  exact discreteObjectiveGap_nonneg_of_le problem (chosen i) (reference i) (h i)

end MLTheory.Methods.OR
