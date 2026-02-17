/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib
import MLTheory.Methods.OCO.OptimizationCore
import MLTheory.Methods.OR.ConvexCore

/-!
# MLTheory.Methods.OCO.GamesAndDuality

Minimal games/duality interfaces aligned with OCO core regret definitions.
-/

namespace MLTheory.Methods.OCO

/-- Online game problem with player loss and round-indexed opponent play. -/
structure GameProblem (Decision Opponent : Type*) where
  loss : Nat -> Decision -> Opponent -> Real
  opponentPlay : Nat -> Opponent

/-- Saddle comparator for primal/dual or player/opponent baselines. -/
structure SaddleComparator (Decision Opponent : Type*) where
  playerRef : Decision
  opponentRef : Opponent

/-- One-round game regret against a static player comparator. -/
def gameInstantRegret {Decision Opponent : Type*}
    (problem : GameProblem Decision Opponent) (t : Nat) (x : Decision)
    (c : Comparator Decision) : Real :=
  instantRegret (fun z => problem.loss t z (problem.opponentPlay t)) x c

/-- One-round game regret is nonnegative under comparator dominance. -/
theorem gameInstantRegret_nonneg_of_le {Decision Opponent : Type*}
    (problem : GameProblem Decision Opponent) (t : Nat) (x : Decision)
    (c : Comparator Decision)
    (h : problem.loss t c.ref (problem.opponentPlay t) <=
      problem.loss t x (problem.opponentPlay t)) :
    0 <= gameInstantRegret problem t x c := by
  exact instantRegret_nonneg_of_le (fun z => problem.loss t z (problem.opponentPlay t)) x c h

/-- Cumulative game regret under round-indexed opponent play. -/
def gameCumulativeRegret {Decision Opponent : Type*}
    (problem : GameProblem Decision Opponent) (n : Nat)
    (choices : Fin n -> Decision) (c : Comparator Decision) : Real :=
  cumulativeRegret n (fun t z => problem.loss t z (problem.opponentPlay t)) choices c

/-- Cumulative game regret is nonnegative under round-wise comparator dominance. -/
theorem gameCumulativeRegret_nonneg_of_le {Decision Opponent : Type*}
    (problem : GameProblem Decision Opponent) {n : Nat}
    (choices : Fin n -> Decision) (c : Comparator Decision)
    (h : ∀ t : Fin n,
      problem.loss t c.ref (problem.opponentPlay t) <=
        problem.loss t (choices t) (problem.opponentPlay t)) :
    0 <= gameCumulativeRegret problem n choices c := by
  simpa [gameCumulativeRegret] using
    cumulativeRegret_nonneg_of_le
      (losses := fun t z => problem.loss t z (problem.opponentPlay t))
      (choices := choices) c h

/-- Saddle gap at round `t` between current play and comparator references. -/
def saddleGap {Decision Opponent : Type*}
    (problem : GameProblem Decision Opponent) (t : Nat)
    (x : Decision) (y : Opponent)
    (s : SaddleComparator Decision Opponent) : Real :=
  problem.loss t x s.opponentRef - problem.loss t s.playerRef y

/-- Saddle gap is nonnegative under one-step saddle dominance. -/
theorem saddleGap_nonneg_of_le {Decision Opponent : Type*}
    (problem : GameProblem Decision Opponent) (t : Nat)
    (x : Decision) (y : Opponent)
    (s : SaddleComparator Decision Opponent)
    (h : problem.loss t s.playerRef y <= problem.loss t x s.opponentRef) :
    0 <= saddleGap problem t x y s := by
  exact sub_nonneg.mpr h

/-- Primal-dual gap helper. -/
def dualityGap (primalValue dualValue : Real) : Real :=
  primalValue - dualValue

/-- Duality gap is nonnegative when dual value is below primal value. -/
theorem dualityGap_nonneg_of_le {primalValue dualValue : Real}
    (h : dualValue <= primalValue) :
    0 <= dualityGap primalValue dualValue := by
  exact sub_nonneg.mpr h

/-- Game instant regret is exactly OR objective gap under fixed opponent play. -/
theorem gameInstantRegret_eq_objectiveGap {Decision Opponent : Type*}
    (problem : GameProblem Decision Opponent) (t : Nat) (x : Decision)
    (c : Comparator Decision) :
    gameInstantRegret problem t x c =
      MLTheory.Methods.OR.objectiveGap
        (fun z => problem.loss t z (problem.opponentPlay t)) x c.ref := by
  rfl

/-- Average game regret over `n` rounds. -/
noncomputable def averageGameRegret {Decision Opponent : Type*}
    (problem : GameProblem Decision Opponent) (n : Nat)
    (choices : Fin n -> Decision) (c : Comparator Decision) : Real :=
  gameCumulativeRegret problem n choices c / n

/-- Average game regret is nonnegative under round-wise comparator dominance. -/
theorem averageGameRegret_nonneg_of_le {Decision Opponent : Type*}
    (problem : GameProblem Decision Opponent) {n : Nat}
    (choices : Fin n -> Decision) (c : Comparator Decision)
    (h : ∀ t : Fin n,
      problem.loss t c.ref (problem.opponentPlay t) <=
        problem.loss t (choices t) (problem.opponentPlay t)) :
    0 <= averageGameRegret problem n choices c := by
  unfold averageGameRegret
  exact div_nonneg
    (gameCumulativeRegret_nonneg_of_le problem choices c h)
    (Nat.cast_nonneg n)

end MLTheory.Methods.OCO
