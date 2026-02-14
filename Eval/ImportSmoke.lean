/-
Copyright (c) 2026 Xiong Jiangkai. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xiong Jiangkai, Codex
-/
import MLTheory
import MLTheory.Core.Learning.PAC
import MLTheory.Methods.Learning.SVM
import MLTheory.Applications.Learning
import MLTheory.Books.FoML2.Ch05_SupportVectorMachines
import MLTheory.Probability
import MLTheory.Concentration
import MLTheory.Optimization
import MLTheory.InfoTheory

/-!
# Import Smoke

Compile-time smoke checks for both layered and legacy compatibility imports.
-/

#check MLTheory.Core.Learning.PACProblem
#check MLTheory.Methods.Learning.hingeLoss
#check MLTheory.Applications.Learning.learningApplicationsReady
#check MLTheory.Books.FoML2.hingeLoss
