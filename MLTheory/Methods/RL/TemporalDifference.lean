/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.RL.MDP

/-!
# MLTheory.Methods.RL.TemporalDifference

Minimal temporal-difference interfaces and error-recurrence statements.
-/

namespace MLTheory.Methods.RL

open MLTheory.Core.RL

/-- Temporal-difference method bundle over a finite MDP. -/
structure TemporalDifferenceProblem (State Action : Type*) where
  mdp : FiniteMDP State Action
  policy : DeterministicPolicy State Action
  stepSize : Real

/-- One-step TD target `r + γ V(s')`. -/
def tdTarget (reward discount nextValue : Real) : Real :=
  reward + discount * nextValue

/-- TD prediction error `target - prediction`. -/
def tdError (target prediction : Real) : Real :=
  target - prediction

/-- TD update for scalar prediction: `prediction + α * (target - prediction)`. -/
def tdUpdate (stepSize target prediction : Real) : Real :=
  prediction + stepSize * tdError target prediction

/-- TD error is zero when target equals prediction. -/
theorem tdError_self (x : Real) : tdError x x = 0 := by
  simp [tdError]

/-- TD update keeps prediction unchanged when step size is zero. -/
theorem tdUpdate_zero_stepSize (target prediction : Real) :
    tdUpdate 0 target prediction = prediction := by
  simp [tdUpdate, tdError]

/-- TD update keeps prediction unchanged when target already matches prediction. -/
theorem tdUpdate_self_target (stepSize x : Real) :
    tdUpdate stepSize x x = x := by
  simp [tdUpdate, tdError]

/-- TD error recurrence after one update step. -/
theorem tdError_after_update (stepSize target prediction : Real) :
    tdError target (tdUpdate stepSize target prediction) =
      (1 - stepSize) * tdError target prediction := by
  simp [tdError, tdUpdate]
  ring

/-- Squared TD error is always nonnegative. -/
theorem tdError_sq_nonneg (target prediction : Real) :
    0 <= (tdError target prediction) ^ (2 : Nat) := by
  exact sq_nonneg (tdError target prediction)

end MLTheory.Methods.RL
