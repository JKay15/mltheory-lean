import MLTheory.Methods.RL

namespace Problems.RL.TDUpdateOneStep

/-- Problem-level statement for one-step TD error update identity. -/
def tdUpdateErrorStatement (stepSize target prediction : ℝ) : Prop :=
  MLTheory.Methods.RL.tdError target (MLTheory.Methods.RL.tdUpdate stepSize target prediction) =
    (1 - stepSize) * MLTheory.Methods.RL.tdError target prediction

/-- Spec file keeps the statement executable and checkable. -/
theorem tdErrorStatementWellTyped (stepSize target prediction : ℝ) :
    tdUpdateErrorStatement stepSize target prediction := by
  simpa [tdUpdateErrorStatement] using
    (MLTheory.Methods.RL.tdError_after_update stepSize target prediction)

end Problems.RL.TDUpdateOneStep
