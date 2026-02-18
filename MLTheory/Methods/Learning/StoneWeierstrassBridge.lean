/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib

/-!
# MLTheory.Methods.Learning.StoneWeierstrassBridge

Reusable epsilon-style bridge lemmas extracted from Stone-Weierstrass in mathlib.
-/

namespace MLTheory.Methods.Learning

open scoped Topology

/--
Stone-Weierstrass epsilon bridge on compact spaces:
if a real subalgebra separates points, every continuous target is uniformly approximable.
-/
theorem stone_exists_uniform_near
    {X : Type*} [TopologicalSpace X] [CompactSpace X]
    (A : Subalgebra ℝ C(X, ℝ))
    (hSep : A.SeparatesPoints)
    (f : C(X, ℝ)) (ε : ℝ) (hε : 0 < ε) :
    ∃ g : A, ‖(g : C(X, ℝ)) - f‖ < ε :=
  ContinuousMap.exists_mem_subalgebra_near_continuousMap_of_separatesPoints A hSep f ε hε

/--
Stone-Weierstrass closure bridge:
if a real subalgebra separates points on a compact space, it is dense in `C(X, ℝ)`.
-/
theorem stone_closure_eq_top
    {X : Type*} [TopologicalSpace X] [CompactSpace X]
    (A : Subalgebra ℝ C(X, ℝ))
    (hSep : A.SeparatesPoints) :
    A.topologicalClosure = ⊤ :=
  ContinuousMap.subalgebra_topologicalClosure_eq_top_of_separatesPoints A hSep

end MLTheory.Methods.Learning
