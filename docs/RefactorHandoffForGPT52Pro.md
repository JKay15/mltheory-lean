# GPT5.2pro 重构交接包（MLTheory 全量实现快照）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

## 目的（给重构模型）
1. 这份文档是“已做工作全量快照”，用于避免重构时丢上下文。
2. 数据全部来自 `docs/ssot/registry.json`（和审查文件 `docs/ssot/lean4_contract_audit.json`）。
3. 你可以把这份文档直接喂给 GPT5.2pro，让它基于真实现状更新重构方案。

## 一眼看懂当前状态
- SSOT schema_version：`1.4.0`
- last_updated：`2026-02-18`
- 决策总数：`165`
- 真实模块（file-backed）总数：`69`
- 规划模块（non-file-backed）总数：`58`
- 执行短清单（execution_backlog）条数：`1`
- aliases 总数：`22`
- gaps 总数：`55`

## 当前下一步（短清单）
| horizon | priority | module_path | target_node | why_now | done_when |
|---|---|---|---|---|---|
| near | P3 | MLTheory.Core.Probability.CLTBridge | Probability | BasicMeasure 已落地，继续补概率主线与极限定理连接层，服务上游 concentration 与 learning 接口。 | 形成 CLT bridge 最小接口（标准化和、极限分布占位接口）并接入 ImportSmoke。 |

## 架构契约（重构时默认不可破）
### 1) taxonomy 主树
| node_id | name | tier | primary_parent_id | status | order |
|---|---|---|---|---|---|
| ml_root | MLTheory Root | support | root | active | 0 |
| foundations | Foundations | foundation | ml_root | active | 10 |
| methods_problems | Methods and Problems | methods | ml_root | active | 20 |
| applications_systems | Applications and Systems | application | ml_root | active | 30 |
| support_infrastructure | Support Infrastructure | support | ml_root | active | 40 |
| probability | Probability | foundation | foundations | active | 100 |
| statistics | Statistics | foundation | foundations | active | 110 |
| learning | Learning | methods | methods_problems | active | 200 |
| or | OR | methods | methods_problems | active | 210 |
| rl | RL | methods | learning | active | 220 |
| oco | OCO | methods | or | active | 230 |
| bandits | Bandits | methods | or | active | 240 |
| ai | AI | application | learning | active | 300 |
| llm | LLM | application | ai | active | 310 |
| architecture | Architecture | support | support_infrastructure | active | 400 |

### 2) taxonomy 关系边（secondary_parent/related）
| from_node | from_name | to_node | to_name | relation_type | strength |
|---|---|---|---|---|---|
| statistics | Statistics | probability | Probability | related | 0.8 |
| rl | RL | ai | AI | related | 0.6 |
| bandits | Bandits | rl | RL | related | 0.8 |

### 3) 官方工作流对齐（Lean 官方资源映射）
| capability | source_url | status | local_enforcement |
|---|---|---|---|
| Loogle | https://lean-lang.org/learn/ | active | lean-lsp-mcp: `lean_loogle` + `--loogle-local`；CI: tools/ci/check_official_workflow_alignment.sh |
| LeanSearch | https://lean-lang.org/learn/ | active | lean-lsp-mcp: `lean_leansearch`；CI: tools/ci/check_official_workflow_alignment.sh |
| InfoView/LoogleView | https://raw.githubusercontent.com/leanprover/vscode-lean4/master/vscode-lean4/manual/manual.md | active | lean-lsp-mcp: `lean_goal` + `lean_diagnostic_messages`；augmented 模式要求关键结论进行 InfoView/LoogleView 人工复核并记录到契约评审说明（formalization-contract skill） |
| REPL | https://lean-lang.org/learn/ | active | lean-lsp-mcp 启动参数要求包含 `--repl`；CI: tools/ci/check_official_workflow_alignment.sh |

### 4) canonical spec 契约
| spec_id | repo | entry_file | entry_decl | axiom_policy | status | required_decl_refs |
|---|---|---|---|---|---|---|
| mltheory_pac_badEvent_uniform_bound | MLTheory | MLTheory/Methods/Learning/GeneralizationTools.lean | pac_badEvent_uniform_bound | standard_only | active | pac_badEvent_uniform_bound, pac_badEvent_union_bound |
| mltheory_stone_exists_uniform_near | MLTheory | MLTheory/Methods/Learning/StoneWeierstrassBridge.lean | stone_exists_uniform_near | standard_only | active | stone_exists_uniform_near, stone_closure_eq_top |

## Phase-0 / skill 对齐审查快照
- date=2026-02-17；mode=augmented；score=6/10；status=ok
| # | check_id | title | result | hits |
|---|---|---|---|---|
| 1 | build_gate | 构建门禁（lake build） | PASS | 1 |
| 2 | sorry_zero_gate | sorry 清零门禁 | PASS | 1 |
| 3 | axiom_whitelist_gate | 自定义 axiom 白名单门禁 | PASS | 4 |
| 4 | declaration_immutability | 定理声明不可私改规则 | PASS | 1 |
| 5 | checkpoint_reproducible | 可复现 checkpoint 流程 | PASS | 2 |
| 6 | canonical_signature_lock | canonical 入口签名锁定 | FAIL | 2 |
| 7 | dependency_closure_verifiable | 依赖闭包可验证（声明级） | PASS | 2 |
| 8 | intermediate_to_canonical_mapping | 中间概念到 canonical 映射约束 | FAIL | 0 |
| 9 | official_toolchain_mapping | 官方工具链映射约束（Loogle/LeanSearch/InfoView/REPL） | FAIL | 2 |
| 10 | three_repo_boundary | 三仓边界约束 | FAIL | 0 |

## 已完成实现（planned -> file-backed 提升轨迹）
| date | module_path | node | state(layer/role/proof) | impact |
|---|---|---|---|---|
| 2026-02-16 | MLTheory.Core.Probability.ProbIneq | Probability | core/tool/proved | 概率核心层新增可复用 conditioning/inequality 入口，execution_backlog 的 near 项开始实质消化。 |
| 2026-02-16 | MLTheory.Core.Statistics.Risk | Statistics | core/tool/proved | 统计核心层新增 risk 语义壳层，near 短清单进一步收敛。 |
| 2026-02-16 | MLTheory.Methods.OR.ConvexCore | OR | methods/tool/proved | OR 方法层新增凸优化核心抽象，near backlog 继续收敛。 |
| 2026-02-16 | MLTheory.Methods.Bandits.Foundations | Bandits | methods/canonical/proved | Bandits 方法层形成统一 foundations 入口，near backlog 继续缩短。 |
| 2026-02-16 | MLTheory.Methods.OCO.OptimizationCore | OCO | methods/tool/proved | OCO 主线补齐问题定义/comparator/update 抽象，execution_backlog 近期项完成并进入下一轮中期队列。 |
| 2026-02-16 | MLTheory.Methods.Bandits.Stochastic | Bandits | methods/tool/proved | Bandits 主线补齐 UCB/ETC 最小声明壳并复用 Foundations regret 接口，近期队列继续向 OCO/RL 中期项推进。 |
| 2026-02-16 | MLTheory.Methods.OCO.Generalization | OCO | methods/tool/proved | OCO->Learning 的 online-to-batch 最小桥接接口落地，execution_backlog 近期焦点顺延至 RL.MDP。 |
| 2026-02-16 | MLTheory.Methods.RL.MDP | RL | methods/tool/proved | RL 方法层补齐 MDP 入口壳并对齐 Core/DP 接口，execution_backlog 近期焦点顺延至 TemporalDifference。 |
| 2026-02-16 | MLTheory.Methods.RL.TemporalDifference | RL | methods/tool/proved | RL 主线补齐 TD 更新与误差递推接口；execution_backlog 近期焦点顺延至 Applications.AI.Generalization。 |
| 2026-02-16 | MLTheory.Applications.AI.Generalization | AI | applications/tool/proved | 应用层 AI 泛化桥接入口落地且不新增底层概念；execution_backlog 近期焦点顺延至 Applications.LLM.Autoregressive。 |
| 2026-02-16 | MLTheory.Applications.LLM.Autoregressive | LLM | applications/tool/proved | 应用层 LLM 自回归入口落地并复用 AI 泛化契约；当前 execution_backlog 清空，后续需人工确定下一批 near 队列。 |
| 2026-02-16 | MLTheory.Core.Statistics.Information | Statistics | core/tool/proved | 统计信息论主线新增 KL/maxent/conditional-gap 最小接口，近期焦点顺延至 Methods.Learning.Capacity。 |
| 2026-02-16 | MLTheory.Methods.Learning.Capacity | Learning | methods/tool/proved | Learning 方法层补齐 capacity/JL 占位接口并连通概率尾界桥接；近期焦点顺延至 Applications.AI.DecisionLearning。 |
| 2026-02-16 | MLTheory.Applications.AI.DecisionLearning | AI | applications/tool/proved | AI 应用层补齐 decision-learning 场景入口并复用 Learning/OCO/RL 接口；近期焦点顺延至 Applications.LLM.Sampling。 |
| 2026-02-16 | MLTheory.Applications.LLM.Sampling | LLM | applications/tool/proved | LLM 应用层补齐 sampling 策略最小接口并与 autoregressive 契约对齐；近期焦点顺延至 Applications.LLM.AlignmentObjectives。 |
| 2026-02-16 | MLTheory.Applications.LLM.AlignmentObjectives | LLM | applications/tool/proved | LLM 应用层补齐 alignment objective 入口并与 sampling/autoregressive 契约打通；近期焦点切换到 Methods.Bandits.InformationTheory。 |
| 2026-02-16 | MLTheory.Methods.Bandits.InformationTheory | Bandits | methods/tool/proved | Bandits 方法层补齐 information-theoretic bonus/regret 入口并复用 cumulativeRegret；近期焦点切换到 Methods.Bandits.Adversarial。 |
| 2026-02-16 | MLTheory.Methods.Bandits.Adversarial | Bandits | methods/tool/proved | Bandits 方法层补齐 adversarial regret/EXP3 入口并与共享 cumulativeRegret 对齐；近期焦点切换到 Methods.Bandits.BestArmIdentification。 |
| 2026-02-16 | MLTheory.Methods.Bandits.BestArmIdentification | Bandits | methods/tool/proved | Bandits 方法层补齐 BAI/simple-regret/sample-complexity 最小接口；近期焦点切换到 Methods.Bandits.ContextualLinear。 |
| 2026-02-16 | MLTheory.Methods.Bandits.ContextualLinear | Bandits | methods/tool/proved | Bandits 方法层补齐 contextual-linear 问题定义/置信半径/regret 入口；近期焦点切换到 Methods.Bandits.Dueling。 |
| 2026-02-17 | MLTheory.Methods.Bandits.Dueling | Bandits | methods/tool/proved | Bandits 方法层补齐 dueling 偏好反馈与 regret 入口；近期焦点切换到 Methods.Bandits.LargeActionSpaces。 |
| 2026-02-17 | MLTheory.Methods.Bandits.LargeActionSpaces | Bandits | methods/tool/proved | Bandits 方法层补齐大动作空间候选池规模与 regret 入口；近期焦点切换到 Methods.Bandits.PureExplorationLinear。 |
| 2026-02-17 | MLTheory.Methods.Bandits.PureExplorationLinear | Bandits | methods/tool/proved | Bandits 方法层补齐 pure-exploration-linear 的误差半径与 simple-regret 接口；近期焦点切换到 Methods.Bandits.RLBridge。 |
| 2026-02-17 | MLTheory.Methods.Bandits.RLBridge | Bandits | methods/tool/proved | Bandits 方法层补齐与 RL.TD 的桥接接口；近期焦点切换到 Methods.OR.DiscreteOptimization。 |
| 2026-02-17 | MLTheory.Methods.OR.DiscreteOptimization | OR | methods/tool/proved | Methods.OR 形成离散优化最小接口并复用 ConvexCore.objectiveGap；近期焦点切换到 Methods.OR.GraphOptimization。 |
| 2026-02-17 | MLTheory.Methods.OR.GraphOptimization | OR | methods/tool/proved | Methods.OR 补齐图优化最小接口（路径/割差距）并复用 ConvexCore.objectiveGap；近期焦点切换到 Methods.OR.StochasticMatrix。 |
| 2026-02-17 | MLTheory.Methods.OR.StochasticMatrix | OR | methods/tool/proved | Methods.OR 随机矩阵最小接口落地并复用 ConvexCore.objectiveGap；OR 近期三项完成，近期焦点切换到 Methods.OCO.BanditConvex。 |
| 2026-02-17 | MLTheory.Methods.OCO.BanditConvex | OCO | methods/tool/proved | Methods.OCO 增加 bandit-convex 估计/遗憾差距接口并复用 OCO regret 核心；近期焦点切换到 Methods.OCO.DynamicRegret。 |
| 2026-02-17 | MLTheory.Methods.OCO.DynamicRegret | OCO | methods/tool/proved | Methods.OCO 增加动态比较器与动态遗憾最小接口；近期焦点切换到 Methods.OCO.GamesAndDuality。 |
| 2026-02-17 | MLTheory.Methods.OCO.GamesAndDuality | OCO | methods/tool/proved | Methods.OCO 补齐 games/duality 最小接口（博弈遗憾与对偶差距）；近期焦点切换到 Methods.OCO.Boosting。 |
| 2026-02-17 | MLTheory.Methods.OCO.Boosting | OCO | methods/tool/proved | Methods.OCO 近期待办全部收口完成；近期焦点切换到 Methods.Learning.AdvancedSLT。 |
| 2026-02-17 | MLTheory.Methods.Learning.AdvancedSLT | Learning | methods/tool/proved | Methods.Learning 补齐 advanced SLT 最小接口；近期焦点切换到 Methods.Learning.Sequential。 |
| 2026-02-17 | MLTheory.Methods.Learning.Sequential | Learning | methods/tool/proved | Methods.Learning 补齐 sequential 学习最小接口并连通 OCO 遗憾定义；近期焦点切换到 Methods.Learning.KernelBayes。 |
| 2026-02-17 | MLTheory.Methods.Learning.KernelBayes | Learning | methods/tool/proved | Learning 主线补齐 kernel-Bayes 后验更新与风险差距最小接口，execution_backlog 近期焦点顺延至 AutomataLanguage。 |
| 2026-02-17 | MLTheory.Methods.Learning.AutomataLanguage | Learning | methods/tool/proved | Learning 子线新增离散自动机语言风险接口，execution_backlog 近期焦点顺延至 DiscreteModeling。 |
| 2026-02-17 | MLTheory.Methods.Learning.DiscreteModeling | Learning | methods/tool/proved | Learning 近期短清单三项（KernelBayes/AutomataLanguage/DiscreteModeling）已全部落地，execution_backlog 转入概率基础补齐。 |
| 2026-02-17 | MLTheory.Core.Probability.BasicMeasure | Probability | core/tool/proved | foundations 概率层补齐测度基础入口，execution_backlog 近期焦点顺延至 CLTBridge。 |

## 真实模块全量清单（实现细节）
| module_path | file_path | node | source_track | layer | role | proof_status | formal_decl_refs |
|---|---|---|---|---|---|---|---|
| MLTheory | MLTheory.lean | Architecture | native | legacy | bridge | statement |  |
| MLTheory.Applications.AI | MLTheory/Applications/AI.lean | AI | native | applications | bridge | statement |  |
| MLTheory.Applications.AI.DecisionLearning | MLTheory/Applications/AI/DecisionLearning.lean | AI | native | applications | tool | proved | DecisionLearningScenario, policyImprovementGap, policyImprovementGap_nonneg_of_le, decisionLearning_from_onlineToBatch, decisionLearning_td_error_after_update, decisionLearning_capacity_bridge_exists, decisionLearning_vc_witness, decisionLearning_pac_constant_exists |
| MLTheory.Applications.AI.Generalization | MLTheory/Applications/AI/Generalization.lean | AI | native | applications | tool | proved | AIGeneralizationScenario, deploymentGap, deploymentGap_nonneg_of_le, ai_generalization_from_onlineToBatch, ai_pac_constant_exists |
| MLTheory.Applications.LLM | MLTheory/Applications/LLM.lean | LLM | native | applications | bridge | statement |  |
| MLTheory.Applications.LLM.AlignmentObjectives | MLTheory/Applications/LLM/AlignmentObjectives.lean | LLM | native | applications | tool | proved | AlignmentObjective, preferenceMargin, preferenceMargin_nonneg_of_le, alignmentPenalty, alignedScore, alignedScore_le_objectiveScore, AlignmentScenario, alignment_pac_constant_exists |
| MLTheory.Applications.LLM.Autoregressive | MLTheory/Applications/LLM/Autoregressive.lean | LLM | native | applications | tool | proved | AutoregressiveModel, sequenceScore, autoregressiveRiskGap, AutoregressiveScenario, autoregressive_pac_constant_exists |
| MLTheory.Applications.LLM.Sampling | MLTheory/Applications/LLM/Sampling.lean | LLM | native | applications | tool | proved | SamplingPolicy, sampledToken, samplingStepScore, sequenceScore_singleton_sampled, samplingRiskGap, samplingRiskGap_nonneg_of_le, SamplingScenario, sampling_pac_constant_exists |
| MLTheory.Applications.Learning | MLTheory/Applications/Learning.lean | Learning | native | applications | bridge | statement |  |
| MLTheory.Applications.RL | MLTheory/Applications/RL.lean | RL | native | applications | bridge | statement |  |
| MLTheory.Books.FoML2 | MLTheory/Books/FoML2.lean | Learning | books | books | compat | statement |  |
| MLTheory.Books.SuttonBartoRL2 | MLTheory/Books/SuttonBartoRL2.lean | RL | books | books | compat | statement |  |
| MLTheory.Core | MLTheory/Core.lean | Architecture | native | core | bridge | statement |  |
| MLTheory.Core.Learning | MLTheory/Core/Learning.lean | Learning | native | core | bridge | statement |  |
| MLTheory.Core.Learning.Capacity | MLTheory/Core/Learning/Capacity.lean | Learning | native | core | tool | proved | CapacityBridge, vcDimensionBound, rademacherBound |
| MLTheory.Core.Learning.FunctionClass | MLTheory/Core/Learning/FunctionClass.lean | Learning | native | core | canonical | proved | HypothesisClass |
| MLTheory.Core.Learning.PAC | MLTheory/Core/Learning/PAC.lean | Learning | native | core | canonical | proved | PACProblem |
| MLTheory.Core.Probability | MLTheory/Core/Probability.lean | Probability | native | core | bridge | statement |  |
| MLTheory.Core.Probability.BasicMeasure | MLTheory/Core/Probability/BasicMeasure.lean | Probability | native | core | tool | proved | isMeasurableEvent, eventMass, eventMass_mono, eventMass_union_le, conditionedEvent_mass_le_left, conditionedEvent_mass_le_right |
| MLTheory.Core.Probability.Conditioning | MLTheory/Core/Probability/Conditioning.lean | Probability | native | core | tool | proved | conditionedEvent, conditionedEvent_subset_left, condWeight_nonneg |
| MLTheory.Core.Probability.ProbIneq | MLTheory/Core/Probability/ProbIneq.lean | Probability | native | core | tool | proved | tailUpperEnvelope, tailUpperEnvelope_trans, tailUpperEnvelope_add, scale_nonneg |
| MLTheory.Core.RL | MLTheory/Core/RL.lean | RL | native | core | bridge | statement |  |
| MLTheory.Core.RL.MDP | MLTheory/Core/RL/MDP.lean | RL | native | core | tool | statement | FiniteMDP, DeterministicPolicy, bellmanExpectationSpec, bellmanOptimalitySpec |
| MLTheory.Core.Statistics | MLTheory/Core/Statistics.lean | Statistics | native | core | bridge | statement |  |
| MLTheory.Core.Statistics.Information | MLTheory/Core/Statistics/Information.lean | Statistics | native | core | tool | proved | InformationPair, klSurrogate, klSurrogate_nonneg_of_le, MaxEntropyTemplate, maxEntGap, conditionalMaxEntGap |
| MLTheory.Core.Statistics.Risk | MLTheory/Core/Statistics/Risk.lean | Statistics | native | core | tool | proved | RiskPair, excessRisk, excessRisk_nonneg_of_le, excessRisk_add_empirical |
| MLTheory.Methods | MLTheory/Methods.lean | Architecture | native | methods | bridge | statement |  |
| MLTheory.Methods.Bandits | MLTheory/Methods/Bandits.lean | Bandits | native | methods | bridge | statement |  |
| MLTheory.Methods.Bandits.Adversarial | MLTheory/Methods/Bandits/Adversarial.lean | Bandits | native | methods | tool | proved | AdversarialBanditModel, adversarialRoundRegret, adversarialRoundRegret_nonneg_of_le, adversarialCumulativeRegret, adversarialCumulativeRegret_nonneg, exp3LearningRate, exp3LearningRate_nonneg, adversarialScalarCumulativeRegret, adversarialScalarCumulativeRegret_eq_foundation |
| MLTheory.Methods.Bandits.BestArmIdentification | MLTheory/Methods/Bandits/BestArmIdentification.lean | Bandits | native | methods | tool | proved | BAIProblem, simpleRegret, simpleRegret_nonneg_of_le, simpleRegret_self, cumulativeSimpleRegret, cumulativeSimpleRegret_nonneg, fixedConfidenceSampleComplexity, fixedConfidenceSampleComplexity_nonneg |
| MLTheory.Methods.Bandits.ContextualLinear | MLTheory/Methods/Bandits/ContextualLinear.lean | Bandits | native | methods | tool | proved | ContextualLinearBanditProblem, LinearScorer, predictedReward, optimisticScore, optimisticScore_ge_predicted, contextualRoundRegret, contextualRoundRegret_nonneg_of_le, contextualCumulativeRegret, contextualCumulativeRegret_nonneg, confidenceRadius, confidenceRadius_nonneg |
| MLTheory.Methods.Bandits.Dueling | MLTheory/Methods/Bandits/Dueling.lean | Bandits | native | methods | tool | proved | DuelingBanditProblem, duelAdvantage, duelAdvantage_swap_neg, duelingRegret, duelingRegret_nonneg_of_le, cumulativeDuelingRegret, cumulativeDuelingRegret_nonneg, preferenceMargin, preferenceMargin_nonneg_of_le |
| MLTheory.Methods.Bandits.Foundations | MLTheory/Methods/Bandits/Foundations.lean | Bandits | native | methods | canonical | proved | BanditInstance, regret, regret_nonneg_of_le, cumulativeRegret, cumulativeRegret_nonneg |
| MLTheory.Methods.Bandits.InformationTheory | MLTheory/Methods/Bandits/InformationTheory.lean | Bandits | native | methods | tool | proved | InformationBanditModel, klStyleBonus, klStyleBonus_nonneg, informationRegret, informationRegret_nonneg_of_le, informationCumulativeRegret, informationCumulativeRegret_nonneg, informationRegret_eq_stochasticPseudoRegret |
| MLTheory.Methods.Bandits.LargeActionSpaces | MLTheory/Methods/Bandits/LargeActionSpaces.lean | Bandits | native | methods | tool | proved | LargeActionBanditProblem, actionPoolSize, actionPoolSize_nonneg, explorationBudget, candidateApproximationGap, candidateApproximationGap_nonneg_of_le, largeActionCumulativeRegret, largeActionCumulativeRegret_nonneg |
| MLTheory.Methods.Bandits.PureExplorationLinear | MLTheory/Methods/Bandits/PureExplorationLinear.lean | Bandits | native | methods | tool | proved | PureExplorationLinearProblem, estimationError, estimationError_nonneg, confidenceRadiusPE, confidenceRadiusPE_nonneg, pureExplorationSimpleRegret, pureExplorationSimpleRegret_nonneg_of_le, fixedConfidenceSampleComplexityPE, fixedConfidenceSampleComplexityPE_nonneg |
| MLTheory.Methods.Bandits.RLBridge | MLTheory/Methods/Bandits/RLBridge.lean | Bandits | native | methods | tool | proved | BanditRLBridgeProblem, banditValueGap, tdErrorProxy, banditValueGap_eq_tdErrorProxy, banditToRLCumulativeGap, banditToRLCumulativeGap_nonneg, banditTdUpdate, banditTdError_after_update |
| MLTheory.Methods.Bandits.Stochastic | MLTheory/Methods/Bandits/Stochastic.lean | Bandits | native | methods | tool | proved | StochasticBanditModel, ucbBonus, ucbScore, ucbBonus_nonneg, ucbScore_ge_empiricalMean, etcExplorationRounds, stochasticPseudoRegret, stochasticPseudoRegret_nonneg |
| MLTheory.Methods.Learning | MLTheory/Methods/Learning.lean | Learning | native | methods | bridge | statement |  |
| MLTheory.Methods.Learning.AdvancedSLT | MLTheory/Methods/Learning/AdvancedSLT.lean | Learning | native | methods | tool | proved | AdvancedSLTProblem, advancedExcessRisk, complexityPenalty, advancedExcessRiskBound, advancedExcessRisk_le_bound, sampleComplexityProxy |
| MLTheory.Methods.Learning.AutomataLanguage | MLTheory/Methods/Learning/AutomataLanguage.lean | Learning | native | methods | tool | proved | AutomataLanguageProblem, runState, accepts, zeroOneLoss, languageEmpiricalRisk, languageRiskGap |
| MLTheory.Methods.Learning.Capacity | MLTheory/Methods/Learning/Capacity.lean | Learning | native | methods | tool | proved | CapacityMethodBundle, jlDistortionGap, jlDistortionGap_nonneg_of_le, method_vcDimensionBound, method_rademacherBound, capacity_tailUpperEnvelope_refl |
| MLTheory.Methods.Learning.ConcentrationPackaging | MLTheory/Methods/Learning/ConcentrationPackaging.lean | Learning | native | methods | canonical | proved | FiniteClassConcentrationBundle, subgaussianTailENN |
| MLTheory.Methods.Learning.Contraction | MLTheory/Methods/Learning/Contraction.lean | Learning | native | methods | tool | proved | OneLipschitzAtZero, lip_contraction_abs, lip_contraction_std |
| MLTheory.Methods.Learning.DiscreteModeling | MLTheory/Methods/Learning/DiscreteModeling.lean | Learning | native | methods | tool | proved | DiscreteModelingProblem, discretePointLoss, discreteEmpiricalRisk, DiscreteComparator, discreteRiskGap, averageDiscreteRiskGap |
| MLTheory.Methods.Learning.GeneralizationTools | MLTheory/Methods/Learning/GeneralizationTools.lean | Learning | native | methods | canonical | proved | pac_badEvent_uniform_bound, pac_badEvent_union_bound |
| MLTheory.Methods.Learning.KernelBayes | MLTheory/Methods/Learning/KernelBayes.lean | Learning | native | methods | tool | proved | KernelBayesProblem, posteriorWeightUnnormalized, posteriorNormalization, posteriorWeight, kernelBayesPredictiveMean, kernelBayesRiskGap |
| MLTheory.Methods.Learning.KernelMethods | MLTheory/Methods/Learning/KernelMethods.lean | Learning | native | methods | tool | statement | KernelFunction, isPSDKernel, KernelLearningProblem, representerTheoremSpec |
| MLTheory.Methods.Learning.ModelSelection | MLTheory/Methods/Learning/ModelSelection.lean | Learning | native | methods | tool | proved | ModelSelectionProblem, structuralRiskMinimizationBound |
| MLTheory.Methods.Learning.Rademacher | MLTheory/Methods/Learning/Rademacher.lean | Learning | native | methods | canonical | proved | radStd, radAbs |
| MLTheory.Methods.Learning.SVM | MLTheory/Methods/Learning/SVM.lean | Learning | native | methods | tool | proved | BinaryClassificationDataset, boolLabelToSign, hingeLoss, svmPrimalGuarantee, svmDualGuarantee |
| MLTheory.Methods.Learning.Sequential | MLTheory/Methods/Learning/Sequential.lean | Learning | native | methods | tool | proved | SequentialLearningProblem, sequentialInstantLoss, sequentialPrefixRegret, averagePrefixRegret, sequentialRegretFromOCO, sequentialRegretFromOCO_eq_prefix |
| MLTheory.Methods.Learning.StoneWeierstrassBridge | MLTheory/Methods/Learning/StoneWeierstrassBridge.lean | Learning | native | methods | canonical | proved | stone_exists_uniform_near, stone_closure_eq_top |
| MLTheory.Methods.OCO | MLTheory/Methods/OCO.lean | OCO | native | methods | bridge | statement |  |
| MLTheory.Methods.OCO.BanditConvex | MLTheory/Methods/OCO/BanditConvex.lean | OCO | native | methods | tool | proved | BanditConvexProblem, estimationGap, trueInstantRegret, instantRegretGap, cumulativeRegretGap, banditCumulativeRegret_nonneg_of_le |
| MLTheory.Methods.OCO.Boosting | MLTheory/Methods/OCO/Boosting.lean | OCO | native | methods | tool | proved | BoostingRound, weightedExpertLoss, boostingInstantRegret, boostingCumulativeRegret, expWeightUpdate, boostingRegretFromOCO |
| MLTheory.Methods.OCO.DynamicRegret | MLTheory/Methods/OCO/DynamicRegret.lean | OCO | native | methods | tool | proved | DynamicComparator, dynamicInstantRegret, dynamicCumulativeRegret, dynamicCumulativeRegret_nonneg_of_le, staticToDynamicComparator, dynamicCumulativeRegret_eq_static |
| MLTheory.Methods.OCO.GamesAndDuality | MLTheory/Methods/OCO/GamesAndDuality.lean | OCO | native | methods | tool | proved | GameProblem, SaddleComparator, gameInstantRegret, gameCumulativeRegret, dualityGap, averageGameRegret |
| MLTheory.Methods.OCO.Generalization | MLTheory/Methods/OCO/Generalization.lean | OCO | native | methods | tool | proved | averageRegret, averageRegret_nonneg_of_le, onlineToBatch_bridge_statement, oco_pacSampleComplexityBound |
| MLTheory.Methods.OCO.OptimizationCore | MLTheory/Methods/OCO/OptimizationCore.lean | OCO | native | methods | tool | proved | OCOProblem, Comparator, OnlineUpdate, instantRegret, cumulativeRegret, instantRegret_nonneg_of_le, cumulativeRegret_nonneg_of_le, instantRegret_eq_objectiveGap |
| MLTheory.Methods.OR | MLTheory/Methods/OR.lean | OR | native | methods | bridge | statement |  |
| MLTheory.Methods.OR.ConvexCore | MLTheory/Methods/OR/ConvexCore.lean | OR | native | methods | tool | proved | ConvexObjective, FeasibleSet, objectiveGap, objectiveGap_nonneg_of_le, scaled_objectiveGap_nonneg |
| MLTheory.Methods.OR.DiscreteOptimization | MLTheory/Methods/OR/DiscreteOptimization.lean | OR | native | methods | tool | proved | DiscreteOptimizationProblem, feasibleCandidates, discreteObjectiveGap, discreteObjectiveGap_nonneg_of_le, cumulativeDiscreteObjectiveGap, cumulativeDiscreteObjectiveGap_nonneg |
| MLTheory.Methods.OR.GraphOptimization | MLTheory/Methods/OR/GraphOptimization.lean | OR | native | methods | tool | proved | GraphOptimizationProblem, pathCost, pathObjectiveGap, pathObjectiveGap_nonneg_of_le, cutObjectiveGap, cumulativePathObjectiveGap_nonneg |
| MLTheory.Methods.OR.StochasticMatrix | MLTheory/Methods/OR/StochasticMatrix.lean | OR | native | methods | tool | proved | StochasticMatrixProblem, rowMass, rowMassGap, rowMassGap_nonneg_of_le, entrywiseDeviation, cumulativeRowMassGap_nonneg |
| MLTheory.Methods.RL | MLTheory/Methods/RL.lean | RL | native | methods | bridge | statement |  |
| MLTheory.Methods.RL.DynamicProgramming | MLTheory/Methods/RL/DynamicProgramming.lean | RL | native | methods | tool | statement | valueIterationUpdate, policyEvaluationSpec, policyImprovementSpec, policyIterationConvergenceSpec |
| MLTheory.Methods.RL.MDP | MLTheory/Methods/RL/MDP.lean | RL | native | methods | tool | proved | MDPMethodProblem, bellmanOperator, valueIterationUpdate_eq_bellmanOperator, bellmanBridgeSpec |
| MLTheory.Methods.RL.TemporalDifference | MLTheory/Methods/RL/TemporalDifference.lean | RL | native | methods | tool | proved | TemporalDifferenceProblem, tdTarget, tdError, tdUpdate, tdError_after_update, tdError_sq_nonneg |

## 规划模块全量清单（未落地）
| module_path | target_node | source_track | status | reason |
|---|---|---|---|---|
| MLTheory.Books.BanditAlgorithms | Bandits | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartIII_AdversarialBandits | Bandits | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartII_StochasticBandits | Bandits | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartIV_ContextualLinearBandits | Bandits | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartI_Foundations | Bandits | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartVII_ReinforcementLearning | Bandits | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartVI_PureExploration | Bandits | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.BanditAlgorithms.PartV_LargeActionSpaces | Bandits | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5 | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch01_MeasureTheory | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch02_ProbabilityTheory | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch03_IndependenceExpectations | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch04_LimitTheorems | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch05_PoissonApproximation | Probability | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch06_MarkovChains | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch07_Martingales | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch08_BrownianMotion | Probability | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch09_StationaryProcesses | Probability | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch10_CTMC | Probability | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.Durrett5.Ch11_ErgodicTheorems | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.HazanOCO2 | OCO | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.HazanOCO2.PartIII_GeneralizationAndAdaptivity | OCO | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.HazanOCO2.PartII_BanditAndGames | OCO | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.HazanOCO2.PartIV_BoostingAndApproachability | OCO | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.HazanOCO2.PartI_Core | OCO | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.SuttonBartoRL2.PartIII_LookingDeeper | RL | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.SuttonBartoRL2.PartII_ApproximateMethods | RL | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.SuttonBartoRL2.PartI_TabularMethods | RL | books | gap | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch01_Refresher | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch02_IndependentSums | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch03_RandomVectors | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch04_RandomMatrices | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch05_WithoutIndependence | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch06_QuadraticSymmContraction | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch07_RandomProcesses | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch08_Chaining | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Books.VershyninHDP.Ch09_MatrixDeviations | Probability | books | planned | No local .lean file yet; keep as roadmap/planned module (layer=books, role=placeholder, proof_status=placeholder). |
| MLTheory.Core.Probability.Brownian | Probability | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=core, role=placeholder, proof_status=placeholder). |
| MLTheory.Core.Probability.CLTBridge | Probability | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=core, role=placeholder, proof_status=placeholder). |
| MLTheory.Core.Probability.CTMC | Probability | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=core, role=placeholder, proof_status=placeholder). |
| MLTheory.Core.Probability.DensityCDF | Probability | native | planned | No local .lean file yet; roadmap item pending file-backed implementation. |
| MLTheory.Core.Probability.Ergodic | Probability | native | planned | No local .lean file yet; roadmap item pending file-backed implementation. |
| MLTheory.Core.Probability.LimitLaws | Probability | native | planned | No local .lean file yet; roadmap item pending file-backed implementation. |
| MLTheory.Core.Probability.MarkovKernels | Probability | native | planned | No local .lean file yet; roadmap item pending file-backed implementation. |
| MLTheory.Core.Probability.Martingales | Probability | native | planned | No local .lean file yet; roadmap item pending file-backed implementation. |
| MLTheory.Core.Probability.Moments | Probability | native | planned | No local .lean file yet; roadmap item pending file-backed implementation. |
| MLTheory.Core.Probability.PoissonApprox | Probability | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=core, role=placeholder, proof_status=placeholder). |
| MLTheory.Core.Probability.Stationary | Probability | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=core, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.CaseStudies | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.EligibilityTraces | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.Frontiers | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.FunctionApproximation | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.ModelBasedPlanning | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.MonteCarlo | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.NeuroscienceBridge | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.OffPolicy | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.PolicyGradient | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |
| MLTheory.Methods.RL.PsychologyBridge | RL | native | gap | No local .lean file yet; keep as roadmap/planned module (layer=methods, role=placeholder, proof_status=placeholder). |

## 结构风险与重构优先级（自动识别）
| issue_id | severity | title | evidence | action | acceptance_gate |
|---|---|---|---|---|---|
| S4 | P2 | 关键入口声明已在，但证明状态仍是 statement | 3 个模块；示例：MLTheory.Core.RL.MDP, MLTheory.Methods.Learning.KernelMethods, MLTheory.Methods.RL.DynamicProgramming | 按 canonical_specs 优先级把 statement 入口逐批推进到 proved；先补依赖闭包最短链路。 | canonical/tool 的 proved 比例按批次上升，且 canonical_contract 持续通过。 |

## 可复现验收命令（重构后至少跑这些）
```bash
python3 tools/docs/validate_ssot.py
python3 tools/docs/sync_docs.py --check
python3 tools/ci/check_taxonomy_contract.py
python3 tools/ci/check_namespace_layout.py
python3 tools/ci/check_tool_forest_consistency.py
python3 tools/ci/check_review_views_consistency.py
python3 tools/ci/check_registry_reference_hygiene.py
python3 tools/ci/check_ready_to_remove.py
bash tools/ci/check_ssot_migration_idempotent.sh
bash tools/ci/check_layer_imports.sh
bash tools/ci/check_no_new_deprecated_imports.sh
bash tools/ci/check_canonical_contract.sh
bash tools/ci/check_official_workflow_alignment.sh
bash tools/ci/check_placeholder_policy.sh
bash tools/ci/check_no_sorry_axiom.sh
~/.elan/bin/lake build
bash /Users/xiongjiangkai/xjk_papers/paper-template/scripts/formalization_preflight.sh --mode augmented
bash /Users/xiongjiangkai/xjk_papers/paper-template/scripts/check_final_signature.sh
```

## 给 GPT5.2pro 的建议阅读顺序
1. 先看“架构契约”与“Phase-0 审查快照”，确认硬约束。
2. 再看“已完成实现轨迹”与“真实模块全量清单”，避免重复造轮子。
3. 最后看“规划模块全量清单 + 结构风险”，决定推翻重做范围与迁移策略。
