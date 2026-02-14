/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.Learning.Capacity

/-!
# MLTheory.Books.FoML2.Ch03_RademacherVCDimension

Book-index compatibility adapters that re-export canonical MLTheory modules.
-/

namespace MLTheory.Books.FoML2

/-- Compatibility alias to concept-first capacity interface. -/
abbrev CapacityBridge := MLTheory.Core.Learning.CapacityBridge

/-- Compatibility alias for VC-dimension placeholder. -/
abbrev vcDimensionBound : Prop :=
  MLTheory.Core.Learning.vcDimensionBound

/-- Compatibility alias for Rademacher placeholder. -/
abbrev rademacherBound : Prop :=
  MLTheory.Core.Learning.rademacherBound

end MLTheory.Books.FoML2
