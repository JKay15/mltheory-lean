/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.Compat.Mathlib

/-!
# MLTheory.Core.Statistics.Risk

Minimal risk abstractions used by learning/generalization modules.
-/

namespace MLTheory.Core.Statistics

/-- Minimal container for empirical/population risk values. -/
structure RiskPair where
  empirical : Real
  population : Real

/-- Excess risk defined as population minus empirical risk. -/
def excessRisk (r : RiskPair) : Real := r.population - r.empirical

/-- Zero excess risk when empirical and population risks match. -/
theorem excessRisk_self (x : Real) : excessRisk { empirical := x, population := x } = 0 := by
  simp [excessRisk]

/-- Excess risk is nonnegative when population risk upper-bounds empirical risk. -/
theorem excessRisk_nonneg_of_le (r : RiskPair) (h : r.empirical <= r.population) :
    0 <= excessRisk r := by
  exact sub_nonneg.mpr h

/-- Excess risk identity used when rearranging bounds. -/
theorem excessRisk_add_empirical (r : RiskPair) :
    excessRisk r + r.empirical = r.population := by
  simp [excessRisk]

end MLTheory.Core.Statistics
