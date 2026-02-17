/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import Mathlib

/-!
# MLTheory.Core.Statistics.Information

Minimal information-theoretic interfaces for entropy/cross-entropy style gaps.
-/

namespace MLTheory.Core.Statistics

/-- Minimal entropy/cross-entropy container. -/
structure InformationPair where
  entropy : Real
  crossEntropy : Real

/-- KL-like surrogate gap: cross-entropy minus entropy. -/
def klSurrogate (i : InformationPair) : Real :=
  i.crossEntropy - i.entropy

/-- KL surrogate is zero when entropy equals cross-entropy. -/
theorem klSurrogate_self (x : Real) :
    klSurrogate { entropy := x, crossEntropy := x } = 0 := by
  simp [klSurrogate]

/-- KL surrogate is nonnegative when cross-entropy upper-bounds entropy. -/
theorem klSurrogate_nonneg_of_le (i : InformationPair) (h : i.entropy <= i.crossEntropy) :
    0 <= klSurrogate i := by
  exact sub_nonneg.mpr h

/-- Max-entropy template with candidate entropy and upper bound witness. -/
structure MaxEntropyTemplate where
  candidateEntropy : Real
  upperBound : Real

/-- Gap to the max-entropy upper bound. -/
def maxEntGap (m : MaxEntropyTemplate) : Real :=
  m.upperBound - m.candidateEntropy

/-- Max-entropy gap is nonnegative under upper-bound condition. -/
theorem maxEntGap_nonneg_of_le (m : MaxEntropyTemplate)
    (h : m.candidateEntropy <= m.upperBound) :
    0 <= maxEntGap m := by
  exact sub_nonneg.mpr h

/-- Conditional max-entropy style gap between joint and conditional terms. -/
def conditionalMaxEntGap (jointEntropy conditionalEntropy : Real) : Real :=
  jointEntropy - conditionalEntropy

/-- Conditional max-entropy gap is nonnegative when conditional term is bounded above. -/
theorem conditionalMaxEntGap_nonneg_of_le (jointEntropy conditionalEntropy : Real)
    (h : conditionalEntropy <= jointEntropy) :
    0 <= conditionalMaxEntGap jointEntropy conditionalEntropy := by
  exact sub_nonneg.mpr h

end MLTheory.Core.Statistics
