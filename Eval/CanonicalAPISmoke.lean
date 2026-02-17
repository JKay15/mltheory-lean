/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Core.Learning
import MLTheory.Methods.Learning

/-!
# Canonical API Smoke

Compile-time smoke checks for the minimal canonical API surface used by downstream repos.
-/

#check MLTheory.Core.Learning.PACProblem
#check MLTheory.Core.Learning.HypothesisClass

#check MLTheory.Methods.Learning.stone_exists_uniform_near
#check MLTheory.Methods.Learning.stone_closure_eq_top
#check MLTheory.Methods.Learning.FiniteClassConcentrationBundle
#check MLTheory.Methods.Learning.FiniteClassConcentrationBundle.ofSubgaussianFamily
#check MLTheory.Methods.Learning.subgaussianTailENN
#check MLTheory.Methods.Learning.radStd
#check MLTheory.Methods.Learning.radAbs
#check MLTheory.Methods.Learning.pac_badEvent_uniform_bound
