/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.RL.MDP

/-!
# MLTheory.Books.SuttonBartoRL2.Ch03_MDP

Book-index compatibility adapters that re-export canonical MLTheory modules.
-/

namespace MLTheory.Books.SuttonBartoRL2

/-- Compatibility alias to concept-first MDP interface. -/
abbrev FiniteMDP := MLTheory.Core.RL.FiniteMDP

/-- Compatibility alias for deterministic policy interface. -/
abbrev DeterministicPolicy := MLTheory.Core.RL.DeterministicPolicy

/-- Compatibility alias for Bellman expectation placeholder. -/
abbrev bellmanExpectationPlaceholder : Prop :=
  MLTheory.Core.RL.bellmanExpectationPlaceholder

/-- Compatibility alias for Bellman optimality placeholder. -/
abbrev bellmanOptimalityPlaceholder : Prop :=
  MLTheory.Core.RL.bellmanOptimalityPlaceholder

end MLTheory.Books.SuttonBartoRL2
