/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.Compat.Mathlib

/-!
# MLTheory.Core.Probability.ProbIneq

Minimal probability-inequality interfaces used by upper-layer learning/RL estimates.
-/

namespace MLTheory.Core.Probability

/-- Generic pointwise upper-envelope relation for tails/moments. -/
def tailUpperEnvelope (f g : Real -> Real) : Prop := ∀ x : Real, f x <= g x

/-- Reflexivity of pointwise upper-envelope relation. -/
theorem tailUpperEnvelope_refl (f : Real -> Real) : tailUpperEnvelope f f := by
  intro x
  exact le_rfl

/-- Transitivity of pointwise upper-envelope relation. -/
theorem tailUpperEnvelope_trans {f g h : Real -> Real}
    (hfg : tailUpperEnvelope f g) (hgh : tailUpperEnvelope g h) :
    tailUpperEnvelope f h := by
  intro x
  exact le_trans (hfg x) (hgh x)

/-- Envelope relation is stable under adding the same offset function. -/
theorem tailUpperEnvelope_add {f g h : Real -> Real} (hfg : tailUpperEnvelope f g) :
    tailUpperEnvelope (fun x => f x + h x) (fun x => g x + h x) := by
  intro x
  exact add_le_add (hfg x) le_rfl

/-- Nonnegativity helper for scaled bounds. -/
theorem scale_nonneg {x c : Real} (hx : 0 <= x) (hc : 0 <= c) : 0 <= c * x := by
  exact mul_nonneg hc hx

end MLTheory.Core.Probability
