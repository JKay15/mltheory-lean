/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory.Methods.Compat.Mathlib
import MLTheory.Methods.Learning.KernelMethods

/-!
# MLTheory.Methods.Learning.KernelBayes

Minimal kernel-Bayes interfaces: posterior update, predictive mean, and risk gap.
-/

namespace MLTheory.Methods.Learning

/-- Kernel-Bayes setup: kernel-learning problem + prior/likelihood + predictor family. -/
structure KernelBayesProblem (X Y H : Type*) where
  kernelProblem : KernelLearningProblem X Y
  prior : H -> Real
  likelihood : H -> X -> Y -> Real
  predictor : H -> X -> Real

/-- Unnormalized posterior weight at one observation pair `(xObs, yObs)`. -/
def posteriorWeightUnnormalized {X Y H : Type*}
    (problem : KernelBayesProblem X Y H) (xObs : X) (yObs : Y) (h : H) : Real :=
  problem.prior h * problem.likelihood h xObs yObs

/-- Posterior normalizer (partition function) over a finite hypothesis pool. -/
def posteriorNormalization {X Y H : Type*} [Fintype H]
    (problem : KernelBayesProblem X Y H) (xObs : X) (yObs : Y) : Real :=
  ∑ h : H, posteriorWeightUnnormalized problem xObs yObs h

/-- Posterior normalizer is nonnegative under nonnegative prior and likelihood. -/
theorem posteriorNormalization_nonneg_of_nonneg {X Y H : Type*} [Fintype H]
    (problem : KernelBayesProblem X Y H) (xObs : X) (yObs : Y)
    (hPrior : ∀ h : H, 0 <= problem.prior h)
    (hLike : ∀ h : H, 0 <= problem.likelihood h xObs yObs) :
    0 <= posteriorNormalization problem xObs yObs := by
  unfold posteriorNormalization
  refine Finset.sum_nonneg ?_
  intro h _
  exact mul_nonneg (hPrior h) (hLike h)

/-- Normalized posterior weight at one observation pair `(xObs, yObs)`. -/
noncomputable def posteriorWeight {X Y H : Type*} [Fintype H]
    (problem : KernelBayesProblem X Y H) (xObs : X) (yObs : Y) (h : H) : Real :=
  posteriorWeightUnnormalized problem xObs yObs h /
    posteriorNormalization problem xObs yObs

/-- Posterior weight is nonnegative when prior/likelihood are nonnegative
and the normalizer is nonnegative. -/
theorem posteriorWeight_nonneg_of_nonneg {X Y H : Type*} [Fintype H]
    (problem : KernelBayesProblem X Y H) (xObs : X) (yObs : Y) (h : H)
    (hPrior : ∀ h' : H, 0 <= problem.prior h')
    (hLike : ∀ h' : H, 0 <= problem.likelihood h' xObs yObs) :
    0 <= posteriorWeight problem xObs yObs h := by
  unfold posteriorWeight posteriorWeightUnnormalized
  exact div_nonneg
    (mul_nonneg (hPrior h) (hLike h))
    (posteriorNormalization_nonneg_of_nonneg problem xObs yObs hPrior hLike)

/-- Predictive mean under posterior averaging at `(xObs, yObs)` for query `xQuery`. -/
noncomputable def kernelBayesPredictiveMean {X Y H : Type*} [Fintype H]
    (problem : KernelBayesProblem X Y H)
    (xObs : X) (yObs : Y) (xQuery : X) : Real :=
  ∑ h : H, posteriorWeight problem xObs yObs h * problem.predictor h xQuery

/-- Pointwise loss of a single hypothesis under kernel-learning loss. -/
def kernelBayesPointLoss {X Y H : Type*}
    (problem : KernelBayesProblem X Y H) (h : H) (x : X) (y : Y) : Real :=
  problem.kernelProblem.loss (problem.predictor h) x y

/-- Finite-sample empirical risk of hypothesis `h`. -/
def kernelBayesRisk {X Y H : Type*}
    (problem : KernelBayesProblem X Y H)
    (n : Nat) (samples : Fin n -> X × Y) (h : H) : Real :=
  ∑ t : Fin n, kernelBayesPointLoss problem h (samples t).1 (samples t).2

/-- Empirical risk gap between `h` and reference `hRef`. -/
def kernelBayesRiskGap {X Y H : Type*}
    (problem : KernelBayesProblem X Y H)
    (n : Nat) (samples : Fin n -> X × Y) (h hRef : H) : Real :=
  kernelBayesRisk problem n samples h - kernelBayesRisk problem n samples hRef

/-- Risk gap is nonnegative if reference loss is pointwise no larger. -/
theorem kernelBayesRiskGap_nonneg_of_le {X Y H : Type*}
    (problem : KernelBayesProblem X Y H)
    (n : Nat) (samples : Fin n -> X × Y) (h hRef : H)
    (hle : ∀ t : Fin n,
      kernelBayesPointLoss problem hRef (samples t).1 (samples t).2 <=
        kernelBayesPointLoss problem h (samples t).1 (samples t).2) :
    0 <= kernelBayesRiskGap problem n samples h hRef := by
  unfold kernelBayesRiskGap kernelBayesRisk
  exact sub_nonneg.mpr <| Finset.sum_le_sum (fun t _ => hle t)

/-- Kernel-Bayes re-export: PSD diagonal nonnegativity from `KernelMethods`. -/
theorem kernelBayesDiagonal_nonneg_of_isPSD {X Y H : Type*}
    (problem : KernelBayesProblem X Y H)
    (hPSD : isPSDKernel problem.kernelProblem.kernel) (x : X) :
    0 <= problem.kernelProblem.kernel.eval x x := by
  exact hPSD x

end MLTheory.Methods.Learning
