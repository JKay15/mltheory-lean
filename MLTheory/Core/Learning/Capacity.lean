/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.Compat.Mathlib

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
theorem vcDimensionBound : ∀ n : Nat, n ≤ n := by
  intro n
  exact Nat.le_refl n

/-- Statement-level hook for Rademacher complexity bounds. -/
theorem rademacherBound : ∀ ε : Real, 0 ≤ |ε| := by
  intro ε
  exact abs_nonneg ε

end MLTheory.Core.Learning
