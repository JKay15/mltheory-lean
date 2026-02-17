/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib
import MLTheory.Methods.Bandits.Foundations

/-!
# MLTheory.Methods.Bandits.Dueling

Minimal dueling-bandit interfaces aligned with shared regret foundations.
-/

namespace MLTheory.Methods.Bandits

/-- Dueling bandit preference model with round-indexed pairwise feedback. -/
structure DuelingBanditProblem (Arm : Type*) where
  preference : Nat -> Arm -> Arm -> Real

/-- Pairwise duel advantage `a` over `b` at round `t`. -/
def duelAdvantage {Arm : Type*} (problem : DuelingBanditProblem Arm)
    (t : Nat) (a b : Arm) : Real :=
  problem.preference t a b - problem.preference t b a

/-- Duel advantage is skew-symmetric. -/
theorem duelAdvantage_swap_neg {Arm : Type*} (problem : DuelingBanditProblem Arm)
    (t : Nat) (a b : Arm) :
    duelAdvantage problem t a b = -duelAdvantage problem t b a := by
  unfold duelAdvantage
  ring

/-- Dueling regret against a round-wise best preference value. -/
def duelingRegret (bestValue chosenValue : Real) : Real :=
  regret bestValue chosenValue

/-- Dueling regret is nonnegative under best-value dominance. -/
theorem duelingRegret_nonneg_of_le {bestValue chosenValue : Real}
    (h : chosenValue <= bestValue) :
    0 <= duelingRegret bestValue chosenValue := by
  exact regret_nonneg_of_le h

/-- Cumulative dueling regret hook that reuses shared cumulative regret. -/
def cumulativeDuelingRegret (bestValue : Real) (n : Nat) (chosenValues : Fin n -> Real) : Real :=
  cumulativeRegret bestValue n chosenValues

/-- Cumulative dueling regret is nonnegative under round-wise dominance. -/
theorem cumulativeDuelingRegret_nonneg {bestValue : Real} {n : Nat}
    (chosenValues : Fin n -> Real) (h : ∀ i : Fin n, chosenValues i <= bestValue) :
    0 <= cumulativeDuelingRegret bestValue n chosenValues := by
  simpa [cumulativeDuelingRegret] using cumulativeRegret_nonneg chosenValues h

/-- Preference margin helper between winner and loser scores. -/
def preferenceMargin (winnerScore loserScore : Real) : Real :=
  winnerScore - loserScore

/-- Preference margin is nonnegative when winner score dominates loser score. -/
theorem preferenceMargin_nonneg_of_le {winnerScore loserScore : Real}
    (h : loserScore <= winnerScore) :
    0 <= preferenceMargin winnerScore loserScore := by
  exact sub_nonneg.mpr h

end MLTheory.Methods.Bandits
