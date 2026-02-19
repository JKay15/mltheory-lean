import Problems.RL.TDUpdateOneStep.Spec

namespace Problems.RL.TDUpdateOneStep

/-- Cache lemma used by final proof file. -/
theorem tdUpdateErrorIdentity (stepSize target prediction : ℝ) :
    tdUpdateErrorStatement stepSize target prediction := by
  exact tdErrorStatementWellTyped stepSize target prediction

/-- Auxiliary non-negativity fact reused in final report. -/
theorem tdErrorSquaredNonneg (target prediction : ℝ) :
    0 <= (MLTheory.Methods.RL.tdError target prediction) ^ 2 := by
  exact MLTheory.Methods.RL.tdError_sq_nonneg target prediction

end Problems.RL.TDUpdateOneStep
