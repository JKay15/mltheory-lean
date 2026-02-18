/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.OR.ConvexCore

/-!
# MLTheory.Methods.OR.GraphOptimization

Minimal graph-optimization interfaces aligned with `OR.ConvexCore`.
-/

namespace MLTheory.Methods.OR

/-- Weighted graph optimization problem over a finite edge universe. -/
structure GraphOptimizationProblem (Vertex : Type*) where
  edgeUniverse : Finset (Vertex × Vertex)
  edgeWeight : Vertex -> Vertex -> Real

/-- Cost of a selected edge set under graph edge weights. -/
def pathCost {Vertex : Type*} (problem : GraphOptimizationProblem Vertex)
    (selectedEdges : Finset (Vertex × Vertex)) : Real :=
  Finset.sum selectedEdges (fun e => problem.edgeWeight (Prod.fst e) (Prod.snd e))

/-- Path-cost objective gap reusing `ConvexCore.objectiveGap`. -/
def pathObjectiveGap {Vertex : Type*} (problem : GraphOptimizationProblem Vertex)
    (chosen reference : Finset (Vertex × Vertex)) : Real :=
  objectiveGap (pathCost problem) chosen reference

/-- Path objective gap at the same edge set is zero. -/
theorem pathObjectiveGap_self {Vertex : Type*}
    (problem : GraphOptimizationProblem Vertex)
    (selectedEdges : Finset (Vertex × Vertex)) :
    pathObjectiveGap problem selectedEdges selectedEdges = 0 := by
  simpa [pathObjectiveGap] using objectiveGap_self (pathCost problem) selectedEdges

/-- Path objective gap is nonnegative when reference cost is no larger than chosen cost. -/
theorem pathObjectiveGap_nonneg_of_le {Vertex : Type*}
    (problem : GraphOptimizationProblem Vertex)
    (chosen reference : Finset (Vertex × Vertex))
    (h : pathCost problem reference <= pathCost problem chosen) :
    0 <= pathObjectiveGap problem chosen reference := by
  simpa [pathObjectiveGap] using
    objectiveGap_nonneg_of_le (pathCost problem) chosen reference h

/-- Gap between best cut value and chosen cut value. -/
def cutObjectiveGap (bestCutValue chosenCutValue : Real) : Real :=
  bestCutValue - chosenCutValue

/-- Cut objective gap is nonnegative when chosen cut is bounded by the best cut value. -/
theorem cutObjectiveGap_nonneg_of_le {bestCutValue chosenCutValue : Real}
    (h : chosenCutValue <= bestCutValue) :
    0 <= cutObjectiveGap bestCutValue chosenCutValue := by
  exact sub_nonneg.mpr h

/-- Cumulative path objective gap across rounds/horizons. -/
def cumulativePathObjectiveGap {Vertex : Type*} (problem : GraphOptimizationProblem Vertex)
    (n : Nat)
    (chosen reference : Fin n -> Finset (Vertex × Vertex)) : Real :=
  Finset.sum Finset.univ (fun i => pathObjectiveGap problem (chosen i) (reference i))

/-- Cumulative path objective gap is nonnegative under round-wise dominance. -/
theorem cumulativePathObjectiveGap_nonneg {Vertex : Type*}
    (problem : GraphOptimizationProblem Vertex) {n : Nat}
    (chosen reference : Fin n -> Finset (Vertex × Vertex))
    (h : ∀ i : Fin n, pathCost problem (reference i) <= pathCost problem (chosen i)) :
    0 <= cumulativePathObjectiveGap problem n chosen reference := by
  refine Finset.sum_nonneg ?_
  intro i _
  exact pathObjectiveGap_nonneg_of_le problem (chosen i) (reference i) (h i)

end MLTheory.Methods.OR
