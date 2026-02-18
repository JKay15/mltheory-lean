/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.Compat.Mathlib

/-!
# MLTheory.Core.RL.MDP

Core abstractions and foundational statements for MLTheory.
-/

namespace MLTheory.Core.RL

/-- Concept-first skeleton for finite Markov decision processes. -/
structure FiniteMDP (State Action : Type*) where
  transition : State -> Action -> State -> Real
  reward : State -> Action -> State -> Real
  discount : Real

/-- Deterministic policy interface for RL core statements. -/
abbrev DeterministicPolicy (State Action : Type*) := State -> Action

/-- Specification-level statement for Bellman expectation equations. -/
def bellmanExpectationSpec {State Action : Type*}
    (mdp : FiniteMDP State Action) (π : DeterministicPolicy State Action) (V : State -> Real) :
    Prop :=
  ∀ s s' : State,
    0 ≤ mdp.transition s (π s) s' ->
      mdp.discount * V s ≤ mdp.reward s (π s) s' + mdp.discount * V s'

/-- Specification-level statement for Bellman optimality equations. -/
def bellmanOptimalitySpec {State Action : Type*}
    (mdp : FiniteMDP State Action) (V : State -> Real) : Prop :=
  ∀ s s' : State,
    ∃ a : Action,
      0 ≤ mdp.transition s a s' ∧
        mdp.discount * V s ≤ mdp.reward s a s' + mdp.discount * V s'

end MLTheory.Core.RL
