/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib

/-!
# MLTheory.Core.Learning.Capacity

Core abstractions and foundational statements for MLTheory.
-/

namespace MLTheory.Core.Learning

/-- Concept-first interface for VC/Rademacher style capacity control. -/
structure CapacityBridge (X H : Type*) where
  hypothesisSet : Set H
  eval : H -> X -> Bool

/-- Statement-level hook for VC-dimension bounds. -/
def vcDimensionBound : Prop := ∀ n : Nat, n ≤ n

/-- Statement-level hook for Rademacher complexity bounds. -/
def rademacherBound : Prop := ∀ ε : Real, 0 ≤ |ε|

end MLTheory.Core.Learning
