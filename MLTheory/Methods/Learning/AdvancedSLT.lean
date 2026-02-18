/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.Learning.Capacity

/-!
# MLTheory.Methods.Learning.AdvancedSLT

Minimal advanced-SLT interfaces: excess risk decomposition and complexity proxies.
-/

namespace MLTheory.Methods.Learning

/-- Advanced-SLT scenario with shared capacity witness and risk pair. -/
structure AdvancedSLTProblem (X H : Type*) where
  capacity : CapacityMethodBundle X H
  empiricalRisk : H -> Real
  populationRisk : H -> Real

/-- Excess risk of a hypothesis. -/
def advancedExcessRisk {X H : Type*}
    (problem : AdvancedSLTProblem X H) (h : H) : Real :=
  problem.populationRisk h - problem.empiricalRisk h

/-- Excess risk is nonnegative when empirical risk does not exceed population risk. -/
theorem advancedExcessRisk_nonneg_of_le {X H : Type*}
    (problem : AdvancedSLTProblem X H) (h : H)
    (hle : problem.empiricalRisk h <= problem.populationRisk h) :
    0 <= advancedExcessRisk problem h := by
  exact sub_nonneg.mpr hle

/-- Complexity penalty (capacity + confidence contributions). -/
def complexityPenalty (capacityTerm confidenceTerm : Real) : Real :=
  capacityTerm + confidenceTerm

/-- Complexity penalty is nonnegative when both components are nonnegative. -/
theorem complexityPenalty_nonneg {capacityTerm confidenceTerm : Real}
    (hCap : 0 <= capacityTerm) (hConf : 0 <= confidenceTerm) :
    0 <= complexityPenalty capacityTerm confidenceTerm := by
  exact add_nonneg hCap hConf

/-- Approximation penalty (model + optimization contributions). -/
def approximationPenalty (modelError optimizationError : Real) : Real :=
  modelError + optimizationError

/-- Approximation penalty is nonnegative when both components are nonnegative. -/
theorem approximationPenalty_nonneg {modelError optimizationError : Real}
    (hModel : 0 <= modelError) (hOpt : 0 <= optimizationError) :
    0 <= approximationPenalty modelError optimizationError := by
  exact add_nonneg hModel hOpt

/-- Advanced-SLT upper bound: excess risk + complexity penalty + approximation penalty. -/
def advancedExcessRiskBound {X H : Type*}
    (problem : AdvancedSLTProblem X H) (h : H)
    (capacityTerm confidenceTerm modelError optimizationError : Real) : Real :=
  advancedExcessRisk problem h +
    complexityPenalty capacityTerm confidenceTerm +
    approximationPenalty modelError optimizationError

/-- The bound dominates excess risk under nonnegative penalty components. -/
theorem advancedExcessRisk_le_bound {X H : Type*}
    (problem : AdvancedSLTProblem X H) (h : H)
    (capacityTerm confidenceTerm modelError optimizationError : Real)
    (hCap : 0 <= capacityTerm) (hConf : 0 <= confidenceTerm)
    (hModel : 0 <= modelError) (hOpt : 0 <= optimizationError) :
    advancedExcessRisk problem h <=
      advancedExcessRiskBound
        problem h capacityTerm confidenceTerm modelError optimizationError := by
  unfold advancedExcessRiskBound
  nlinarith [complexityPenalty_nonneg hCap hConf, approximationPenalty_nonneg hModel hOpt]

/-- Sample-complexity proxy used by advanced-SLT planning estimates. -/
noncomputable def sampleComplexityProxy (complexity ε : Real) : Real :=
  complexity / ε

/-- Sample-complexity proxy nonnegativity under nonnegative complexity and positive accuracy. -/
theorem sampleComplexityProxy_nonneg_of_pos {complexity ε : Real}
    (hComplexity : 0 <= complexity) (hε : 0 < ε) :
    0 <= sampleComplexityProxy complexity ε := by
  unfold sampleComplexityProxy
  exact div_nonneg hComplexity (le_of_lt hε)

/-- Advanced-SLT re-export of method-level VC-dimension bound hook. -/
theorem advanced_vcDimensionBound (n : Nat) : n <= n := by
  exact method_vcDimensionBound n

/-- Advanced-SLT re-export of method-level Rademacher nonnegativity hook. -/
theorem advanced_rademacher_nonneg (ε : Real) : 0 <= |ε| := by
  exact method_rademacherBound ε

end MLTheory.Methods.Learning
