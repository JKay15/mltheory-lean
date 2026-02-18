/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Core.Learning.Capacity
import MLTheory.Core.Probability.ProbIneq

/-!
# MLTheory.Methods.Learning.Capacity

Method-level capacity interfaces (VC/Rademacher/JL placeholders)
built on core capacity abstractions.
-/

namespace MLTheory.Methods.Learning

open MLTheory.Core.Learning

/-- Method-level wrapper that reuses core capacity bridge and tracks a complexity witness. -/
structure CapacityMethodBundle (X H : Type*) where
  bridge : CapacityBridge X H
  complexityUpper : Nat -> Real

/-- JL-style distortion gap between upper and lower bounds. -/
def jlDistortionGap (upper lower : Real) : Real :=
  upper - lower

/-- Distortion gap is nonnegative when lower bound does not exceed upper bound. -/
theorem jlDistortionGap_nonneg_of_le (upper lower : Real) (h : lower <= upper) :
    0 <= jlDistortionGap upper lower := by
  exact sub_nonneg.mpr h

/-- Nonnegative scaling helper for capacity upper bounds. -/
theorem scaled_complexity_nonneg (c bound : Real) (hc : 0 <= c) (hb : 0 <= bound) :
    0 <= c * bound := by
  exact mul_nonneg hc hb

/-- Method-level access to core VC bound hook. -/
theorem method_vcDimensionBound (n : Nat) : n <= n := by
  exact MLTheory.Core.Learning.vcDimensionBound n

/-- Method-level access to core Rademacher bound hook. -/
theorem method_rademacherBound (ε : Real) : 0 <= |ε| := by
  exact MLTheory.Core.Learning.rademacherBound ε

/-- Trivial tail-envelope witness used when wiring concentration-style capacity bounds. -/
theorem capacity_tailUpperEnvelope_refl (f : Real -> Real) :
    MLTheory.Core.Probability.tailUpperEnvelope f f := by
  exact MLTheory.Core.Probability.tailUpperEnvelope_refl f

end MLTheory.Methods.Learning
