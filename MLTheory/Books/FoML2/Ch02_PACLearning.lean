/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.Learning.PAC

/-!
# MLTheory.Books.FoML2.Ch02_PACLearning

Book-index compatibility adapters that re-export canonical MLTheory modules.
-/

namespace MLTheory.Books.FoML2

/-- Compatibility alias to concept-first PAC interface. -/
abbrev PACProblem := MLTheory.Core.Learning.PACProblem

/-- Compatibility alias for PAC sample-complexity placeholder. -/
abbrev pacSampleComplexityBound : Prop :=
  MLTheory.Core.Learning.pacSampleComplexityBound

end MLTheory.Books.FoML2
