/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib
import MLTheory.Methods.OCO.OptimizationCore
import MLTheory.Methods.OR.ConvexCore

/-!
# MLTheory.Methods.OCO.BanditConvex

Minimal bandit-convex interfaces: estimated loss gap and regret gap.
-/

namespace MLTheory.Methods.OCO

/-- Bandit-convex problem with true loss and bandit-estimated loss. -/
structure BanditConvexProblem (Decision : Type*) where
  loss : Nat -> Decision -> Real
  lossEstimate : Nat -> Decision -> Real

/-- Absolute estimation gap between bandit-estimated and true loss. -/
def estimationGap {Decision : Type*} (problem : BanditConvexProblem Decision)
    (t : Nat) (x : Decision) : Real :=
  |problem.lossEstimate t x - problem.loss t x|

/-- Estimation gap is always nonnegative. -/
theorem estimationGap_nonneg {Decision : Type*} (problem : BanditConvexProblem Decision)
    (t : Nat) (x : Decision) :
    0 <= estimationGap problem t x := by
  exact abs_nonneg (problem.lossEstimate t x - problem.loss t x)

/-- One-round true regret under comparator baseline. -/
def trueInstantRegret {Decision : Type*} (problem : BanditConvexProblem Decision)
    (t : Nat) (x : Decision) (c : Comparator Decision) : Real :=
  instantRegret (problem.loss t) x c

/-- One-round estimated regret under comparator baseline. -/
def estimatedInstantRegret {Decision : Type*} (problem : BanditConvexProblem Decision)
    (t : Nat) (x : Decision) (c : Comparator Decision) : Real :=
  instantRegret (problem.lossEstimate t) x c

/-- One-round regret gap between estimated and true bandit regret. -/
def instantRegretGap {Decision : Type*} (problem : BanditConvexProblem Decision)
    (t : Nat) (x : Decision) (c : Comparator Decision) : Real :=
  |estimatedInstantRegret problem t x c - trueInstantRegret problem t x c|

/-- One-round regret gap is always nonnegative. -/
theorem instantRegretGap_nonneg {Decision : Type*} (problem : BanditConvexProblem Decision)
    (t : Nat) (x : Decision) (c : Comparator Decision) :
    0 <= instantRegretGap problem t x c := by
  exact abs_nonneg (estimatedInstantRegret problem t x c - trueInstantRegret problem t x c)

/-- Cumulative true bandit-convex regret over `n` rounds. -/
def banditCumulativeRegret {Decision : Type*} (problem : BanditConvexProblem Decision)
    (n : Nat) (choices : Fin n -> Decision) (c : Comparator Decision) : Real :=
  cumulativeRegret n (fun t => problem.loss t) choices c

/-- Cumulative estimated regret over `n` rounds. -/
def estimatedCumulativeRegret {Decision : Type*} (problem : BanditConvexProblem Decision)
    (n : Nat) (choices : Fin n -> Decision) (c : Comparator Decision) : Real :=
  cumulativeRegret n (fun t => problem.lossEstimate t) choices c

/-- Cumulative regret gap between estimated and true bandit regret. -/
def cumulativeRegretGap {Decision : Type*} (problem : BanditConvexProblem Decision)
    (n : Nat) (choices : Fin n -> Decision) (c : Comparator Decision) : Real :=
  |estimatedCumulativeRegret problem n choices c - banditCumulativeRegret problem n choices c|

/-- Cumulative regret gap is always nonnegative. -/
theorem cumulativeRegretGap_nonneg {Decision : Type*} (problem : BanditConvexProblem Decision)
    (n : Nat) (choices : Fin n -> Decision) (c : Comparator Decision) :
    0 <= cumulativeRegretGap problem n choices c := by
  exact abs_nonneg
    (estimatedCumulativeRegret problem n choices c - banditCumulativeRegret problem n choices c)

/-- True instant regret is exactly OR objective gap at round `t`. -/
theorem trueInstantRegret_eq_objectiveGap {Decision : Type*}
    (problem : BanditConvexProblem Decision)
    (t : Nat) (x : Decision) (c : Comparator Decision) :
    trueInstantRegret problem t x c =
      MLTheory.Methods.OR.objectiveGap (problem.loss t) x c.ref := by
  rfl

/-- Cumulative true regret is nonnegative under round-wise comparator dominance. -/
theorem banditCumulativeRegret_nonneg_of_le {Decision : Type*}
    (problem : BanditConvexProblem Decision) {n : Nat}
    (choices : Fin n -> Decision) (c : Comparator Decision)
    (h : ∀ t : Fin n, problem.loss t c.ref <= problem.loss t (choices t)) :
    0 <= banditCumulativeRegret problem n choices c := by
  simpa [banditCumulativeRegret] using
    cumulativeRegret_nonneg_of_le (losses := fun t => problem.loss t) (choices := choices) c h

end MLTheory.Methods.OCO
