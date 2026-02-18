/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.Bandits.Stochastic

/-!
# MLTheory.Methods.Bandits.InformationTheory

Minimal information-theoretic bandit interfaces built on top of existing regret APIs.
-/

namespace MLTheory.Methods.Bandits

/-- Information-theoretic wrapper over a stochastic bandit model. -/
structure InformationBanditModel (Arm : Type*) where
  stochastic : StochasticBanditModel Arm
  infoGain : Arm -> Real

/-- KL-style exploration bonus with square-root information gain. -/
noncomputable def klStyleBonus (scale infoGain : Real) : Real :=
  scale * Real.sqrt infoGain

/-- KL-style exploration bonus is nonnegative under nonnegative assumptions. -/
theorem klStyleBonus_nonneg (scale infoGain : Real) (hScale : 0 <= scale) :
    0 <= klStyleBonus scale infoGain := by
  unfold klStyleBonus
  exact mul_nonneg hScale (Real.sqrt_nonneg infoGain)

/-- Information-theoretic one-step regret reuses the bandit foundation regret definition. -/
def informationRegret (bestValue posteriorValue : Real) : Real :=
  regret bestValue posteriorValue

/-- Information-theoretic regret is nonnegative when posterior value stays below best value. -/
theorem informationRegret_nonneg_of_le {bestValue posteriorValue : Real}
    (h : posteriorValue <= bestValue) :
    0 <= informationRegret bestValue posteriorValue := by
  exact regret_nonneg_of_le h

/-- Information-theoretic cumulative regret reuses existing cumulative regret API. -/
def informationCumulativeRegret (bestValue : Real) (n : Nat) (chosen : Fin n -> Real) : Real :=
  cumulativeRegret bestValue n chosen

/-- Information-theoretic cumulative regret inherits nonnegativity from foundations. -/
theorem informationCumulativeRegret_nonneg {bestValue : Real} {n : Nat} (chosen : Fin n -> Real)
    (h : ∀ i : Fin n, chosen i <= bestValue) :
    0 <= informationCumulativeRegret bestValue n chosen := by
  simpa [informationCumulativeRegret] using cumulativeRegret_nonneg chosen h

/-- Information-theoretic cumulative regret matches stochastic pseudo-regret by definition. -/
theorem informationRegret_eq_stochasticPseudoRegret (bestValue : Real) (n : Nat)
    (chosen : Fin n -> Real) :
    informationCumulativeRegret bestValue n chosen = stochasticPseudoRegret bestValue n chosen := by
  rfl

end MLTheory.Methods.Bandits
