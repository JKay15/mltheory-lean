import Problems.RL.TDUpdateOneStep.Cache

namespace Problems.RL.TDUpdateOneStep

/-- Final readable proof delegates to cache lemmas only. -/
theorem tdUpdateReadableProof (stepSize target prediction : ℝ) :
    tdUpdateErrorStatement stepSize target prediction := by
  simpa using tdUpdateErrorIdentity stepSize target prediction

/-- Combined summary theorem for quick inspection in ProofMap/Inspector. -/
theorem tdUpdateWithNonneg (stepSize target prediction : ℝ) :
    tdUpdateErrorStatement stepSize target prediction ∧
      0 <= (MLTheory.Methods.RL.tdError target prediction) ^ 2 := by
  constructor
  · exact tdUpdateErrorIdentity stepSize target prediction
  · exact tdErrorSquaredNonneg target prediction

end Problems.RL.TDUpdateOneStep
