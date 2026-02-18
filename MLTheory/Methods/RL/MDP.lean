/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.RL.MDP
import MLTheory.Methods.RL.DynamicProgramming

/-!
# MLTheory.Methods.RL.MDP

Methods-layer MDP bridge definitions aligned with `Core.RL.MDP`.
-/

namespace MLTheory.Methods.RL

open MLTheory.Core.RL

/-- Methods-layer MDP bundle with a value-function seed. -/
structure MDPMethodProblem (State Action : Type*) where
  mdp : FiniteMDP State Action
  initValue : State -> Real

/-- Bellman-operator placeholder at methods layer. -/
def bellmanOperator {State Action : Type*}
    (_mdp : FiniteMDP State Action) (v : State -> Real) : State -> Real :=
  v

/-- Methods-layer Bellman operator is identity in the current placeholder model. -/
theorem bellmanOperator_apply {State Action : Type*}
    (mdp : FiniteMDP State Action) (v : State -> Real) (s : State) :
    bellmanOperator mdp v s = v s := by
  rfl

/-- Dynamic-programming update currently matches methods-layer Bellman placeholder. -/
theorem valueIterationUpdate_eq_bellmanOperator {State Action : Type*}
    (mdp : FiniteMDP State Action) (v : State -> Real) :
    valueIterationUpdate mdp v = bellmanOperator mdp v := by
  rfl

/-- Bridge spec from methods-layer MDP bundles to the core Bellman expectation spec. -/
def bellmanBridgeSpec {State Action : Type*}
    (problem : MDPMethodProblem State Action) (π : DeterministicPolicy State Action) : Prop :=
  bellmanExpectationSpec problem.mdp π problem.initValue

end MLTheory.Methods.RL
