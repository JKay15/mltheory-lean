/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.Compat.Mathlib

/-!
# MLTheory.Core.Learning.FunctionClass

Core function-class interfaces used by reusable learning-theory tools.
-/

namespace MLTheory.Core.Learning

/-- Finite sample represented as an index-to-point map. -/
abbrev Sample (X : Type*) (n : Nat) := Fin n -> X

/-- Hypothesis class represented as indexed real-valued functions. -/
abbrev HypothesisClass (H X : Type*) := H -> X -> Real

/-- Rademacher signs represented as finite vectors over `{+1, -1}`. -/
abbrev SignVector (n : Nat) := Fin n -> Bool

/-- Convert a Boolean sign into `+1` or `-1`. -/
def rademacherSign (b : Bool) : Real :=
  if b then (1 : Real) else (-1 : Real)

@[simp] theorem abs_rademacherSign (b : Bool) : |rademacherSign b| = 1 := by
  by_cases hb : b <;> simp [rademacherSign, hb]

/-- A hypothesis class is symmetric if it is closed under pointwise negation. -/
structure NegClosed {H X : Type*} (F : HypothesisClass H X) : Prop where
  neg_mem : ∀ h : H, ∃ hneg : H, ∀ x : X, F hneg x = -F h x

end MLTheory.Core.Learning
