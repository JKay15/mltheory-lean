# 全局缺口台账（Gap Ledger）

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

字段约束：`book`、`chapter`、`topic`、`status`、`last_search_date`、`sources_checked`、`candidate_repo`、`next_action`

| book | chapter | topic | status | last_search_date | sources_checked | candidate_repo | next_action |
|---|---|---|---|---|---|---|---|
| BanditAlgorithms | Part I | Explore-Then-Commit / Optimism 形式化接口 | partial | 2026-02-13 | mathlib4（概率不等式/鞅） | 无明确仓库 | 在 `MLTheory.Bandits.Foundations` 建立 regret、arm、policy 核心定义。 |
| BanditAlgorithms | Part II | UCB/Thompson Sampling 的有限时间 regret 证明链 | gap | 2026-02-13 | mathlib4、GitHub 检索 | 无明确仓库 | 在 `MLTheory.Bandits.Stochastic` 先写 theorem statement 占位和依赖清单。 |
| BanditAlgorithms | Part III | Adversarial bandits（EXP3, first/second-order） | gap | 2026-02-13 | mathlib4、GitHub 检索 | 无明确仓库 | 在 `MLTheory.Bandits.Adversarial` 先定义对手模型与性能基准。 |
| BanditAlgorithms | Part IV | Contextual/Linear/Kernels（自归一化过程、线性 UCB/TS） | gap | 2026-02-13 | mathlib4、GitHub 检索 | 无明确仓库 | 在 `MLTheory.Bandits.ContextualLinear` + `InformationTheory` 先建符号层与置信集接口。 |
| BanditAlgorithms | Part VI | Best-arm identification / Dueling / 线性纯探索 | gap | 2026-02-13 | mathlib4、GitHub 检索 | 无明确仓库 | 在 `BestArmIdentification/Dueling/PureExplorationLinear` 写固定预算与固定置信定义。 |
| BanditAlgorithms | Part VII | MDP regret（有限时域/折扣/渐近） | gap | 2026-02-13 | mathlib4、GitHub 检索 | 无明确仓库 | 在 `RLBridge` 增加 bandit 与 MDP 的接口桥接层。 |
| BanditAlgorithms | 全书生态 | Lean4 专门 bandit 仓库可用性 | gap | 2026-02-13 | GitHub API：`bandit lean4`、`multi-armed bandit lean`、`reinforcement learning lean4 mdp` | 无 | 每月复检一次，发现可用仓库后更新 candidate_repo。 |
| Durrett5 | Ch10 | Continuous-time Markov chains | gap | 2026-02-13 | mathlib4、MarkovChain_Formalisation_Lean | `BasharHamade12/MarkovChain_Formalisation_Lean` | 先在 `CTMC` 写状态空间与生成元占位定义。 |
| Durrett5 | Ch11 | Ergodic theorems (probability flavor) | partial | 2026-02-13 | mathlib4（Dynamics/Ergodic） | 无 | 在 `Ergodic` 对齐概率记号并补示例定理入口。 |
| Durrett5 | Ch4 | Central Limit Theorem 主定理接入 | partial | 2026-02-13 | mathlib4、RemyDegenne/CLT | `RemyDegenne/CLT` | 保持 4.27.x 下先做 `CLTBridge` 占位；后续评估依赖兼容再接入。 |
| Durrett5 | Ch5 | Poisson approximation/Stein 方法 | gap | 2026-02-13 | mathlib4、GitHub 检索 | 无明确仓库 | 在 `PoissonApprox` 写占位接口与关键词检索脚本。 |
| Durrett5 | Ch8 | Brownian motion / Itô calculus | partial | 2026-02-13 | mathlib4、RemyDegenne/brownian-motion | `RemyDegenne/brownian-motion` | 先 `Brownian` 占位，不升级 toolchain；持续跟踪迁移到 mathlib 的进度。 |
| Durrett5 | Ch9 | Stationary processes | gap | 2026-02-13 | mathlib4、GitHub 检索 | 无明确仓库 | 在 `Stationary` 定义平稳过程接口与 TODO。 |
| ExternalAudit | lean-rademacher | Rademacher/PAC 通用工具可复用性审计 | partial | 2026-02-14 | GitHub API + README/lakefile/lean-toolchain；可复用声明名：`empiricalRademacherComplexity`、`rademacherComplexity`、`le_two_smul_rademacher`、`linear_predictor_l2_bound`、`dudley_entropy_integral`；Lean 4.27.0-rc1；license=MIT | auto-res/lean-rademacher | 保持“先不直接依赖”；以该仓声明命名为参考，在 MLTheory 自实现最小通用接口后再评估按 tag 接入。 |
| ExternalAudit | lean-stat-learning-theory | 经验过程/覆盖数/Dudley 工具可复用性审计 | partial | 2026-02-14 | GitHub API + README/lakefile/lean-toolchain；可复用声明名：`dudley`、`coveringNumber`、`coveringNumber_euclideanBall_le`；Lean 4.27.0-rc1；license=null | YuanheZ/lean-stat-learning-theory | 许可证未声明，暂不直接依赖；仅作为证明结构与术语参考，待 license 明确后再评估接入。 |
| FoML2 | Ch10-Ch11 | Ranking/Regression 泛化界主线 | gap | 2026-02-13 | MIT TOC、mathlib4 | 无明确仓库 | 在 `MLTheory.Learning.DiscreteModeling` 增加 ranking 与 regression 风险接口。 |
| FoML2 | Ch12-Ch13 | Maximum entropy / Conditional maximum entropy | gap | 2026-02-13 | MIT TOC、mathlib4 | 无明确仓库 | 在 `MLTheory.Statistics.Information` 增加 maxent/conditional maxent 占位层。 |
| FoML2 | Ch16 | Learning automata and languages | gap | 2026-02-13 | MIT TOC、GitHub 检索 | 无明确仓库 | 新建 `MLTheory.Learning.AutomataLanguage` 作为缺口承载模块。 |
| FoML2 | Ch17 | Reinforcement learning（MDP/TD/Q-learning） | gap | 2026-02-13 | MIT TOC、Bandit 覆盖文档、GitHub 检索 | 无明确仓库 | 复用 `MLTheory.Bandits.RLBridge`，补 TD/Q-learning 术语与接口。 |
| FoML2 | Ch3 | VC dimension / Rademacher complexity 与书中记号对齐 | partial | 2026-02-14 | MIT TOC、MLTheory 新增通用模块、`auto-res/lean-rademacher`、`YuanheZ/lean-stat-learning-theory` | `YuanheZ/lean-stat-learning-theory`; `auto-res/lean-rademacher` | 优先以 `MLTheory.Methods.Learning.Rademacher/Contraction/GeneralizationTools` 对齐 FoML2 记号，再逐步补 VC 维相关引理。 |
| FoML2 | Ch4 | Model selection（SRM/CV/regularization） | partial | 2026-02-13 | MIT TOC、mathlib4、本仓库占位模块 | 无明确仓库 | 在 `MLTheory.Books.FoML2.Ch04_ModelSelection` 补 SRM/CV theorem statement。 |
| FoML2 | Ch5 | Support Vector Machines（primal/dual/margin） | partial | 2026-02-13 | MIT TOC、mathlib4、本仓库占位模块 | 无明确仓库 | 在 `MLTheory.Books.FoML2.Ch05_SupportVectorMachines` 补 primal/dual theorem statement。 |
| FoML2 | Ch6 | Kernel Methods（PSD kernel / representer theorem） | partial | 2026-02-13 | MIT TOC、mathlib4、本仓库占位模块 | 无明确仓库 | 在 `MLTheory.Books.FoML2.Ch06_KernelMethods` 补 representer theorem 接口。 |
| FoML2 | Ch7 | Boosting（AdaBoost 与博弈视角） | gap | 2026-02-13 | MIT TOC、HazanOCO2 覆盖文档 | 无明确仓库 | 复用 `MLTheory.OCO.Boosting`，补 FoML2 专用术语与定理入口。 |
| FoML2 | 全书生态 | Lean4 专门 FoML2 书级仓库可用性 | gap | 2026-02-13 | GitHub API：`\"Foundations of Machine Learning\" lean4`、`lean4 \"statistical learning theory\"`、`lean4 PAC learning` | `YuanheZ/lean-stat-learning-theory`; `auto-res/lean-rademacher` | 每月复检一次；若出现书级仓库则更新 candidate_repo 并评估接入。 |
| HazanOCO2 | Ch10 | Learning in changing environments（dynamic regret） | gap | 2026-02-13 | mathlib4、GitHub 检索 | 无明确仓库 | 在 `MLTheory.OCO.DynamicRegret` 增加 comparator drift 与 adaptive regret 定义。 |
| HazanOCO2 | Ch11-Ch12 | Boosting and regret minimization / Online boosting | gap | 2026-02-13 | mathlib4、GitHub 检索 | 无明确仓库 | 在 `MLTheory.OCO.Boosting` 增加 weak learner/oracle 抽象。 |
| HazanOCO2 | Ch3-Ch5 | OGD/second-order/regularization regret 证明链 | gap | 2026-02-13 | mathlib4、GitHub 检索 | 无明确仓库 | 在 `MLTheory.OCO.OptimizationCore` 先落 theorem statement 与假设模板。 |
| HazanOCO2 | Ch6 | Bandit convex optimization | gap | 2026-02-13 | mathlib4、BanditAlgorithms 覆盖文档、GitHub 检索 | 无明确仓库 | 复用 `MLTheory.Bandits.*`，并在 `MLTheory.OCO.BanditConvex` 补连续动作反馈模型。 |
| HazanOCO2 | Ch7 | Projection-free OCO | gap | 2026-02-13 | mathlib4、GitHub 检索 | 无明确仓库 | 在 `MLTheory.OCO.OptimizationCore` 增加 online Frank-Wolfe 接口。 |
| HazanOCO2 | Ch8/Ch13 | Games/duality/Blackwell approachability | gap | 2026-02-13 | mathlib4、GitHub 检索 | 无明确仓库 | 在 `MLTheory.OCO.GamesAndDuality` 先建立对偶与 approachability 定义层。 |
| HazanOCO2 | Ch9 | Generalization and OCO | partial | 2026-02-13 | mathlib4、现有 `MLTheory.AI.Generalization` | 无 | 先复用 AI 泛化模块，再补在线学习特有的稳定性/遗憾转化。 |
| HazanOCO2 | 全书生态 | Lean4 专门 OCO 仓库可用性 | gap | 2026-02-13 | GitHub API：`online convex optimization lean`、`mirror descent lean4`、`online learning regret lean4`、`blackwell approachability lean` | 无 | 每月复检一次，若出现可用仓库则更新 candidate_repo 并评估接入。 |
| SuttonBartoRL2 | Ch14-Ch15 | Psychology / Neuroscience 跨学科桥接 | gap | 2026-02-13 | MIT TOC、GitHub 检索 | 无明确仓库 | 在 `MLTheory.RL.PsychologyBridge`、`MLTheory.RL.NeuroscienceBridge` 仅做术语层。 |
| SuttonBartoRL2 | Ch16-Ch17 | 案例与前沿（应用/开放问题） | gap | 2026-02-13 | MIT TOC、GitHub 检索 | 无明确仓库 | 在 `MLTheory.RL.CaseStudies`、`MLTheory.RL.Frontiers` 维护映射与待办。 |
| SuttonBartoRL2 | Ch3-Ch4 | 有限 MDP 与动态规划主链 | partial | 2026-02-13 | MIT TOC、mathlib4、Bandit 覆盖文档、本仓库占位模块 | 无明确仓库 | 在 `MLTheory.Books.SuttonBartoRL2.Ch03_MDP` 与 `MLTheory.Books.SuttonBartoRL2.Ch04_DynamicProgramming` 补 Bellman 与收敛陈述。 |
| SuttonBartoRL2 | Ch5-Ch8 | MC/TD/n-step/规划学习（表格法） | gap | 2026-02-13 | MIT TOC、mathlib4 | 无明确仓库 | 在 `MLTheory.RL.MonteCarlo`、`MLTheory.RL.TemporalDifference`、`MLTheory.RL.ModelBasedPlanning` 建算法接口。 |
| SuttonBartoRL2 | Ch9-Ch13 | 函数逼近与策略梯度主链 | gap | 2026-02-13 | MIT TOC、FoML2/Hazan 覆盖文档、mathlib4 | 无明确仓库 | 先在 `MLTheory.RL.FunctionApproximation` 与 `MLTheory.RL.PolicyGradient` 建占位证明接口。 |
| SuttonBartoRL2 | 全书生态 | Lean4 专门 RL2 书级仓库可用性 | gap | 2026-02-13 | GitHub API：`lean4 reinforcement learning`、`lean4 markov decision process`、`lean4 q-learning` | `fraware/saferl-proof-stack`（非书级、待评估） | 每月复检；若出现书级仓库或稳定 MDP 形式化则更新 candidate_repo。 |
| Vershynin | Ch2 | Subexponential/Bernstein 全链路 | gap | 2026-02-13 | mathlib4、SLT、FoML | `lean-stat-learning-theory` | 在 `MLTheory.Probability.ProbIneq` 增加占位定理列表并继续检索对应实现。 |
| Vershynin | Ch2 | median-of-means estimator | gap | 2026-02-13 | mathlib4、SLT | 无明确仓库 | 先建立定义层与误差分解接口，后续补具体浓缩不等式。 |
| Vershynin | Ch3 | PCA/Grothendieck/MaxCut/kernel trick | gap | 2026-02-13 | mathlib4（线代/图论）、SLT | 无明确仓库 | 先在 `MLTheory.OR.GraphOptimization` 写问题定义与松弛框架占位。 |
| Vershynin | Ch4 | error correcting codes/community detection/clustering | gap | 2026-02-13 | mathlib4、SLT | 无明确仓库 | 先建章节索引 TODO，后续按主题拆分到 OR 与 Learning。 |
| Vershynin | Ch5 | Johnson-Lindenstrauss 与 Matrix Bernstein | gap | 2026-02-13 | mathlib4、SLT、FoML | `lean-stat-learning-theory` | 先在 `MLTheory.Learning.Capacity` 增加 JL 占位接口。 |
| Vershynin | Ch6 | Hanson-Wright/Decoupling/Contraction | gap | 2026-02-13 | mathlib4、SLT、FoML | `lean-stat-learning-theory` | 在 `MLTheory.Learning.AdvancedSLT` 增加子模块占位。 |
| Vershynin | Ch7 | Slepian/Sudakov-Fernique/Gordon/Gaussian width | gap | 2026-02-13 | mathlib4、SLT | 无明确仓库 | 先定义 `GaussianWidth` 接口与估计模板，挂在 `Learning.AdvancedSLT`。 |
| Vershynin | Ch8 | VC dimension/generic chaining/Chevet | gap | 2026-02-13 | mathlib4、SLT、FoML | `lean-stat-learning-theory` | Ch8 索引保留 TODO；优先补 VC 与 generic chaining 文献线索。 |
| Vershynin | Ch9 | M* bound/escape theorem/Dvoretzky-Milman | gap | 2026-02-13 | mathlib4、SLT | 无明确仓库 | 先记录术语与定义依赖，再分拆到线性代数与测度模块。 |
