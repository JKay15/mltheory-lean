# 模块总表（Module Catalog）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

字段约束：
- `module_path`
- `domain`
- `status(planned/partial/covered/gap)`
- `source(mathlib/slt/external)`
- `book_refs`
- `layer(core/methods/applications/books/legacy)`
- `proof_status(placeholder/statement/proved)`
- `placeholder_policy_scope(allowed/forbidden)`

| module_path | domain | status(planned/partial/covered/gap) | source(mathlib/slt/external) | book_refs | layer(core/methods/applications/books/legacy) | proof_status(placeholder/statement/proved) | placeholder_policy_scope(allowed/forbidden) |
|---|---|---|---|---|---|---|---|
| MLTheory | Root | planned | mathlib | Vershynin Ch1-9; Durrett I-XI; BanditAlgorithms Part I-VII; HazanOCO2 Ch1-13; FoML2 Ch1-17; SuttonBartoRL2 Ch1-17 | legacy | statement | allowed |
| MLTheory.AI | AI Theory | planned | mathlib | Vershynin Ch8.4; HazanOCO2 Ch9-12; FoML2 Ch7/Ch9/Ch14/Ch17; SuttonBartoRL2 Ch13-17 | legacy | statement | allowed |
| MLTheory.AI.DecisionLearning | AI | planned | mathlib | Vershynin Ch8.4; HazanOCO2 Ch8/Ch11; FoML2 Ch7/Ch9/Ch17; SuttonBartoRL2 Ch13/Ch16-17 | legacy | placeholder | allowed |
| MLTheory.AI.Generalization | AI | planned | mathlib | Vershynin Ch8.4; HazanOCO2 Ch9; FoML2 Ch14 | legacy | placeholder | allowed |
| MLTheory.Applications | Architecture | partial | mathlib | FoML2 Ch17; SuttonBartoRL2 Ch16-17 | applications | statement | allowed |
| MLTheory.Applications.Learning | Applications | partial | mathlib | FoML2 Ch7-17 | applications | placeholder | allowed |
| MLTheory.Applications.RL | Applications | partial | mathlib | SuttonBartoRL2 Ch13-17 | applications | placeholder | allowed |
| MLTheory.Bandits | Bandits | planned | mathlib | BanditAlgorithms Part I-VII | legacy | statement | allowed |
| MLTheory.Bandits.Adversarial | Bandits | gap | external | BanditAlgorithms Part III | legacy | placeholder | allowed |
| MLTheory.Bandits.BestArmIdentification | Bandits | gap | external | BanditAlgorithms Ch25-27 | legacy | placeholder | allowed |
| MLTheory.Bandits.ContextualLinear | Bandits | gap | external | BanditAlgorithms Part IV | legacy | placeholder | allowed |
| MLTheory.Bandits.Dueling | Bandits | gap | external | BanditAlgorithms Ch28 | legacy | placeholder | allowed |
| MLTheory.Bandits.Foundations | Bandits | planned | mathlib | BanditAlgorithms Part I; SuttonBartoRL2 Ch2 | legacy | placeholder | allowed |
| MLTheory.Bandits.InformationTheory | Bandits | planned | mathlib | BanditAlgorithms Ch20-21 | legacy | placeholder | allowed |
| MLTheory.Bandits.LargeActionSpaces | Bandits | gap | external | BanditAlgorithms Part V | legacy | placeholder | allowed |
| MLTheory.Bandits.PureExplorationLinear | Bandits | gap | external | BanditAlgorithms Ch29 | legacy | placeholder | allowed |
| MLTheory.Bandits.RLBridge | Bandits | gap | external | BanditAlgorithms Part VII; FoML2 Ch17; SuttonBartoRL2 Ch3/Ch8/Ch17 | legacy | placeholder | allowed |
| MLTheory.Bandits.Stochastic | Bandits | planned | mathlib | BanditAlgorithms Part II; SuttonBartoRL2 Ch2 | legacy | placeholder | allowed |
| MLTheory.Books | Book Index | partial | mathlib | Durrett I-XI; BanditAlgorithms Part I-VII; HazanOCO2 Ch1-13; FoML2 Ch1-17; SuttonBartoRL2 Ch1-17 | books | statement | allowed |
| MLTheory.Books.BanditAlgorithms | Bandit Index | planned | mathlib | BanditAlgorithms Part I-VII | books | placeholder | allowed |
| MLTheory.Books.BanditAlgorithms.PartIII_AdversarialBandits | Bandit Index | gap | external | BanditAlgorithms Part III | books | placeholder | allowed |
| MLTheory.Books.BanditAlgorithms.PartII_StochasticBandits | Bandit Index | planned | mathlib | BanditAlgorithms Part II | books | placeholder | allowed |
| MLTheory.Books.BanditAlgorithms.PartIV_ContextualLinearBandits | Bandit Index | gap | external | BanditAlgorithms Part IV | books | placeholder | allowed |
| MLTheory.Books.BanditAlgorithms.PartI_Foundations | Bandit Index | planned | mathlib | BanditAlgorithms Part I | books | placeholder | allowed |
| MLTheory.Books.BanditAlgorithms.PartVII_ReinforcementLearning | Bandit Index | gap | external | BanditAlgorithms Part VII | books | placeholder | allowed |
| MLTheory.Books.BanditAlgorithms.PartVI_PureExploration | Bandit Index | gap | external | BanditAlgorithms Part VI | books | placeholder | allowed |
| MLTheory.Books.BanditAlgorithms.PartV_LargeActionSpaces | Bandit Index | gap | external | BanditAlgorithms Part V | books | placeholder | allowed |
| MLTheory.Books.Durrett5 | Durrett Index | planned | mathlib | Durrett I-XI | books | placeholder | allowed |
| MLTheory.Books.Durrett5.Ch01_MeasureTheory | Durrett Index | planned | mathlib | Durrett I | books | placeholder | allowed |
| MLTheory.Books.Durrett5.Ch02_ProbabilityTheory | Durrett Index | planned | mathlib | Durrett II | books | placeholder | allowed |
| MLTheory.Books.Durrett5.Ch03_IndependenceExpectations | Durrett Index | planned | mathlib | Durrett III | books | placeholder | allowed |
| MLTheory.Books.Durrett5.Ch04_LimitTheorems | Durrett Index | planned | external | Durrett IV | books | placeholder | allowed |
| MLTheory.Books.Durrett5.Ch05_PoissonApproximation | Durrett Index | gap | external | Durrett V | books | placeholder | allowed |
| MLTheory.Books.Durrett5.Ch06_MarkovChains | Durrett Index | planned | mathlib | Durrett VI | books | placeholder | allowed |
| MLTheory.Books.Durrett5.Ch07_Martingales | Durrett Index | planned | mathlib | Durrett VII | books | placeholder | allowed |
| MLTheory.Books.Durrett5.Ch08_BrownianMotion | Durrett Index | gap | external | Durrett VIII | books | placeholder | allowed |
| MLTheory.Books.Durrett5.Ch09_StationaryProcesses | Durrett Index | gap | external | Durrett IX | books | placeholder | allowed |
| MLTheory.Books.Durrett5.Ch10_CTMC | Durrett Index | gap | external | Durrett X | books | placeholder | allowed |
| MLTheory.Books.Durrett5.Ch11_ErgodicTheorems | Durrett Index | planned | mathlib | Durrett XI | books | placeholder | allowed |
| MLTheory.Books.FoML2 | FoML2 Index | partial | mathlib | FoML2 Ch1-17 | books | statement | allowed |
| MLTheory.Books.FoML2.Ch02_PACLearning | FoML2 Index | partial | mathlib | FoML2 Ch2 | books | statement | allowed |
| MLTheory.Books.FoML2.Ch03_RademacherVCDimension | FoML2 Index | partial | mathlib | FoML2 Ch3 | books | statement | allowed |
| MLTheory.Books.FoML2.Ch04_ModelSelection | FoML2 Index | partial | mathlib | FoML2 Ch4 | books | statement | allowed |
| MLTheory.Books.FoML2.Ch05_SupportVectorMachines | FoML2 Index | partial | mathlib | FoML2 Ch5 | books | statement | allowed |
| MLTheory.Books.FoML2.Ch06_KernelMethods | FoML2 Index | partial | mathlib | FoML2 Ch6 | books | statement | allowed |
| MLTheory.Books.HazanOCO2 | OCO Index | planned | mathlib | HazanOCO2 Ch1-13 | books | placeholder | allowed |
| MLTheory.Books.HazanOCO2.PartIII_GeneralizationAndAdaptivity | OCO Index | gap | external | HazanOCO2 Ch9-10 | books | placeholder | allowed |
| MLTheory.Books.HazanOCO2.PartII_BanditAndGames | OCO Index | gap | external | HazanOCO2 Ch6/Ch8 | books | placeholder | allowed |
| MLTheory.Books.HazanOCO2.PartIV_BoostingAndApproachability | OCO Index | gap | external | HazanOCO2 Ch11-13 | books | placeholder | allowed |
| MLTheory.Books.HazanOCO2.PartI_Core | OCO Index | planned | mathlib | HazanOCO2 Ch1-5/Ch7 | books | placeholder | allowed |
| MLTheory.Books.SuttonBartoRL2 | RL2 Index | partial | mathlib | SuttonBartoRL2 Ch1-17 | books | statement | allowed |
| MLTheory.Books.SuttonBartoRL2.Ch03_MDP | RL2 Index | partial | mathlib | SuttonBartoRL2 Ch3 | books | statement | allowed |
| MLTheory.Books.SuttonBartoRL2.Ch04_DynamicProgramming | RL2 Index | partial | mathlib | SuttonBartoRL2 Ch4 | books | statement | allowed |
| MLTheory.Books.SuttonBartoRL2.PartIII_LookingDeeper | RL2 Index | gap | external | SuttonBartoRL2 Ch14-17 | books | placeholder | allowed |
| MLTheory.Books.SuttonBartoRL2.PartII_ApproximateMethods | RL2 Index | gap | external | SuttonBartoRL2 Ch9-13 | books | placeholder | allowed |
| MLTheory.Books.SuttonBartoRL2.PartI_TabularMethods | RL2 Index | gap | external | SuttonBartoRL2 Ch2-8 | books | placeholder | allowed |
| MLTheory.Concentration | Probability | partial | mathlib | Vershynin Ch2; Durrett II-IV; BanditAlgorithms Ch4/Ch16/Ch38 | legacy | statement | allowed |
| MLTheory.Core | Architecture | partial | mathlib | FoML2 Ch2-6; SuttonBartoRL2 Ch3-4 | core | statement | forbidden |
| MLTheory.Core.Learning | Architecture | partial | mathlib | FoML2 Ch2-3 | core | statement | forbidden |
| MLTheory.Core.Learning.Capacity | Learning | partial | mathlib | FoML2 Ch3; Vershynin Ch8 | core | statement | forbidden |
| MLTheory.Core.Learning.FunctionClass | Learning | partial | mathlib | FoML2 Ch3; Vershynin Ch6 | core | proved | forbidden |
| MLTheory.Core.Learning.PAC | Learning | partial | mathlib | FoML2 Ch2 | core | statement | forbidden |
| MLTheory.Core.RL | Architecture | partial | mathlib | SuttonBartoRL2 Ch3-4 | core | statement | forbidden |
| MLTheory.Core.RL.MDP | RL | partial | mathlib | SuttonBartoRL2 Ch3 | core | statement | forbidden |
| MLTheory.HDP | Book Index | planned | mathlib | Vershynin Ch1-9 | legacy | statement | allowed |
| MLTheory.HDP.Ch01_Refresher | HDP Index | planned | mathlib | Vershynin Ch1 | legacy | placeholder | allowed |
| MLTheory.HDP.Ch02_IndependentSums | HDP Index | planned | mathlib | Vershynin Ch2 | legacy | placeholder | allowed |
| MLTheory.HDP.Ch03_RandomVectors | HDP Index | planned | mathlib | Vershynin Ch3 | legacy | placeholder | allowed |
| MLTheory.HDP.Ch04_RandomMatrices | HDP Index | planned | mathlib | Vershynin Ch4 | legacy | placeholder | allowed |
| MLTheory.HDP.Ch05_WithoutIndependence | HDP Index | planned | mathlib | Vershynin Ch5 | legacy | placeholder | allowed |
| MLTheory.HDP.Ch06_QuadraticSymmContraction | HDP Index | planned | mathlib | Vershynin Ch6 | legacy | placeholder | allowed |
| MLTheory.HDP.Ch07_RandomProcesses | HDP Index | planned | mathlib | Vershynin Ch7 | legacy | placeholder | allowed |
| MLTheory.HDP.Ch08_Chaining | HDP Index | planned | slt | Vershynin Ch8 | legacy | placeholder | allowed |
| MLTheory.HDP.Ch09_MatrixDeviations | HDP Index | planned | slt | Vershynin Ch9 | legacy | placeholder | allowed |
| MLTheory.InfoTheory | Statistics | partial | mathlib | BanditAlgorithms Ch20-21; FoML2 Ch12-13; SuttonBartoRL2 Ch2/Ch13 | legacy | statement | allowed |
| MLTheory.LLM | LLM Theory | planned | mathlib | Vershynin Ch8.4（扩展应用） | legacy | statement | allowed |
| MLTheory.LLM.AlignmentObjectives | LLM | planned | mathlib | Vershynin Ch8.4（扩展） | legacy | placeholder | allowed |
| MLTheory.LLM.Autoregressive | LLM | planned | mathlib | Vershynin Ch8.4（扩展） | legacy | placeholder | allowed |
| MLTheory.LLM.Sampling | LLM | planned | mathlib | Vershynin Ch7-8（扩展） | legacy | placeholder | allowed |
| MLTheory.Learning | ML Theory | planned | mathlib | Vershynin Ch7-9; BanditAlgorithms Part IV-VII; HazanOCO2 Ch9-13; FoML2 Ch1-11/Ch14-16; SuttonBartoRL2 Ch1/Ch6-13 | legacy | statement | allowed |
| MLTheory.Learning.AdvancedSLT | Learning | planned | slt | Vershynin Ch8-9; FoML2 Ch3 | legacy | placeholder | allowed |
| MLTheory.Learning.AutomataLanguage | Learning | gap | external | FoML2 Ch16 | legacy | placeholder | allowed |
| MLTheory.Learning.Capacity | Learning | partial | mathlib | Vershynin Ch4.2/Ch8; FoML2 Ch2-5/Ch15 | legacy | statement | allowed |
| MLTheory.Learning.DiscreteModeling | Learning | planned | mathlib | Vershynin Ch2/Ch8; FoML2 Ch9-11 | legacy | placeholder | allowed |
| MLTheory.Learning.KernelBayes | Learning | partial | mathlib | Vershynin Ch7-8; Durrett VI; FoML2 Ch6 | legacy | statement | allowed |
| MLTheory.Learning.Sequential | Learning | partial | mathlib | Vershynin Ch7; Durrett VII; FoML2 Ch8; SuttonBartoRL2 Ch6-8 | legacy | statement | allowed |
| MLTheory.Methods | Architecture | partial | mathlib | FoML2 Ch4-6; SuttonBartoRL2 Ch4 | methods | statement | forbidden |
| MLTheory.Methods.Learning | Architecture | partial | mathlib | FoML2 Ch4-6 | methods | statement | forbidden |
| MLTheory.Methods.Learning.Contraction | Learning | partial | mathlib | FoML2 Ch3; Vershynin Ch6 | methods | proved | forbidden |
| MLTheory.Methods.Learning.GeneralizationTools | Learning | partial | mathlib | FoML2 Ch2-Ch3; Vershynin Ch2 | methods | proved | forbidden |
| MLTheory.Methods.Learning.KernelMethods | Learning | partial | mathlib | FoML2 Ch6 | methods | statement | forbidden |
| MLTheory.Methods.Learning.ModelSelection | Learning | partial | mathlib | FoML2 Ch4 | methods | statement | forbidden |
| MLTheory.Methods.Learning.Rademacher | Learning | partial | mathlib | FoML2 Ch3; Vershynin Ch6 | methods | proved | forbidden |
| MLTheory.Methods.Learning.SVM | Learning | partial | mathlib | FoML2 Ch5 | methods | statement | forbidden |
| MLTheory.Methods.RL | Architecture | partial | mathlib | SuttonBartoRL2 Ch4 | methods | statement | forbidden |
| MLTheory.Methods.RL.DynamicProgramming | RL | partial | mathlib | SuttonBartoRL2 Ch4 | methods | statement | forbidden |
| MLTheory.OCO | OCO | planned | mathlib | HazanOCO2 Ch1-13 | legacy | statement | allowed |
| MLTheory.OCO.BanditConvex | OCO | gap | external | HazanOCO2 Ch6 | legacy | placeholder | allowed |
| MLTheory.OCO.Boosting | OCO | gap | external | HazanOCO2 Ch11-12; FoML2 Ch7 | legacy | placeholder | allowed |
| MLTheory.OCO.DynamicRegret | OCO | gap | external | HazanOCO2 Ch10 | legacy | placeholder | allowed |
| MLTheory.OCO.GamesAndDuality | OCO | gap | external | HazanOCO2 Ch8/Ch13 | legacy | placeholder | allowed |
| MLTheory.OCO.Generalization | OCO | planned | mathlib | HazanOCO2 Ch9 | legacy | placeholder | allowed |
| MLTheory.OCO.OptimizationCore | OCO | planned | mathlib | HazanOCO2 Ch2-5/Ch7; FoML2 Ch8; SuttonBartoRL2 Ch13 | legacy | placeholder | allowed |
| MLTheory.OR | Operations Research | planned | mathlib | Vershynin Ch3-4; HazanOCO2 Ch2-8; FoML2 Ch4-6/Ch12-13/Ch15 | legacy | statement | allowed |
| MLTheory.OR.ConvexCore | OR | partial | mathlib | Vershynin Ch1.1/Ch3; FoML2 Ch4-5/Ch12-13 | legacy | statement | allowed |
| MLTheory.OR.DiscreteOptimization | OR | partial | mathlib | Vershynin Ch3.6/Ch4.3 | legacy | statement | allowed |
| MLTheory.OR.GraphOptimization | OR | partial | mathlib | Vershynin Ch3.6 | legacy | statement | allowed |
| MLTheory.OR.StochasticMatrix | OR | partial | mathlib | Vershynin Ch3-4; FoML2 Ch15 | legacy | statement | allowed |
| MLTheory.Optimization | Operations Research | partial | mathlib | Vershynin Ch3-4; HazanOCO2 Ch2-8; FoML2 Ch4-6/Ch12-13/Ch15 | legacy | statement | allowed |
| MLTheory.Probability | Probability | planned | mathlib | Vershynin Ch1-2; Durrett I-VIII; BanditAlgorithms Part I-IV; HazanOCO2 Ch3-10; FoML2 Ch2-3/Ch11 | legacy | statement | allowed |
| MLTheory.Probability.BasicMeasure | Probability | planned | mathlib | Durrett I-II | legacy | placeholder | allowed |
| MLTheory.Probability.Brownian | Probability | gap | external | Durrett VIII | legacy | placeholder | allowed |
| MLTheory.Probability.CLTBridge | Probability | gap | external | Durrett IV | legacy | placeholder | allowed |
| MLTheory.Probability.CTMC | Probability | gap | external | Durrett X | legacy | placeholder | allowed |
| MLTheory.Probability.Conditioning | Probability | partial | mathlib | Vershynin Ch1.5; Durrett II-III | legacy | statement | allowed |
| MLTheory.Probability.DensityCDF | Probability | partial | mathlib | Vershynin Ch1.3/Ch2; Durrett II | legacy | statement | allowed |
| MLTheory.Probability.Ergodic | Probability | partial | mathlib | Durrett XI | legacy | statement | allowed |
| MLTheory.Probability.LimitLaws | Probability | partial | mathlib | Vershynin Ch1.7; Durrett IV | legacy | statement | allowed |
| MLTheory.Probability.MarkovKernels | Probability | partial | mathlib | Durrett VI | legacy | statement | allowed |
| MLTheory.Probability.Martingales | Probability | partial | mathlib | Durrett VII; BanditAlgorithms Ch31-38; HazanOCO2 Ch10 | legacy | statement | allowed |
| MLTheory.Probability.Moments | Probability | partial | mathlib | Vershynin Ch2.6-2.9; Durrett III-IV | legacy | statement | allowed |
| MLTheory.Probability.PoissonApprox | Probability | gap | external | Durrett V | legacy | placeholder | allowed |
| MLTheory.Probability.ProbIneq | Probability | planned | mathlib | Vershynin Ch1.6/Ch2; Durrett II-IV; BanditAlgorithms Ch4/Ch16/Ch38; HazanOCO2 Ch3-4/Ch10; FoML2 Ch2/Ch11 | legacy | placeholder | allowed |
| MLTheory.Probability.Stationary | Probability | gap | external | Durrett IX | legacy | placeholder | allowed |
| MLTheory.RL | RL | planned | mathlib | SuttonBartoRL2 Ch1-17 | legacy | statement | allowed |
| MLTheory.RL.CaseStudies | RL | gap | external | SuttonBartoRL2 Ch16 | legacy | placeholder | allowed |
| MLTheory.RL.DynamicProgramming | RL | gap | external | SuttonBartoRL2 Ch4 | legacy | placeholder | allowed |
| MLTheory.RL.EligibilityTraces | RL | gap | external | SuttonBartoRL2 Ch12 | legacy | placeholder | allowed |
| MLTheory.RL.Frontiers | RL | gap | external | SuttonBartoRL2 Ch17 | legacy | placeholder | allowed |
| MLTheory.RL.FunctionApproximation | RL | gap | external | SuttonBartoRL2 Ch9-10 | legacy | placeholder | allowed |
| MLTheory.RL.MDP | RL | gap | external | SuttonBartoRL2 Ch3 | legacy | placeholder | allowed |
| MLTheory.RL.ModelBasedPlanning | RL | gap | external | SuttonBartoRL2 Ch8 | legacy | placeholder | allowed |
| MLTheory.RL.MonteCarlo | RL | gap | external | SuttonBartoRL2 Ch5 | legacy | placeholder | allowed |
| MLTheory.RL.NeuroscienceBridge | RL | gap | external | SuttonBartoRL2 Ch15 | legacy | placeholder | allowed |
| MLTheory.RL.OffPolicy | RL | gap | external | SuttonBartoRL2 Ch11 | legacy | placeholder | allowed |
| MLTheory.RL.PolicyGradient | RL | gap | external | SuttonBartoRL2 Ch13 | legacy | placeholder | allowed |
| MLTheory.RL.PsychologyBridge | RL | gap | external | SuttonBartoRL2 Ch14 | legacy | placeholder | allowed |
| MLTheory.RL.TemporalDifference | RL | gap | external | SuttonBartoRL2 Ch6-7 | legacy | placeholder | allowed |
| MLTheory.Statistics | Statistics | planned | mathlib | Vershynin Ch2/Ch8; Durrett III-IV; BanditAlgorithms Ch20-21; FoML2 Ch4/Ch10-13 | legacy | statement | allowed |
| MLTheory.Statistics.Information | Statistics | partial | mathlib | Vershynin Ch8.4; BanditAlgorithms Ch20-21; FoML2 Ch12-13 | legacy | statement | allowed |
| MLTheory.Statistics.Risk | Statistics | partial | mathlib | Vershynin Ch8.4; FoML2 Ch4/Ch10-11 | legacy | statement | allowed |
