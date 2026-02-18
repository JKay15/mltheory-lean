# 决策日志

<!-- GENERATED FROM docs/ssot/registry.json. DO NOT EDIT MANUALLY. -->

| date | decision | status | impact |
|---|---|---|---|
| 2026-02-13 | Lean 包名采用 `MLTheory`（CamelCase），GitHub 仓库名采用 `mltheory-lean`。 | locked | 统一 import 体验并保持仓库命名可读性。 |
| 2026-02-13 | 项目初始化流程采用 mathlib 模板：`lake +leanprover-community/mathlib4:lean-toolchain new MLTheory math`，并执行 `lake exe cache get` + `lake build`。 | locked | 保证 mathlib 依赖与 toolchain 一致，降低首次构建成本。 |
| 2026-02-13 | 主题层模块固定为 `Probability/Statistics/OR/Learning/AI/LLM`。 | locked | 建立长期稳定的公共库边界，避免后续重命名破坏下游。 |
| 2026-02-13 | HDP（Vershynin）采用“混合层”：主题模块承载实现，`HDP/Ch01..Ch09` 作为章节索引（re-export）。 | locked | 兼顾按主题复用与按章节检索。 |
| 2026-02-13 | 机器学习高级理论（SLT）策略：`v0.1` 先占位后接入。 | locked | 先稳住基础依赖，降低首版复杂度与版本风险。 |
| 2026-02-13 | Durrett 覆盖基线采用第 5 版（I–XI 章）并先建占位模块（`CLTBridge/Brownian/CTMC/...`）。 | locked | 明确概率主线补漏范围，支持分阶段迭代。 |
| 2026-02-13 | 本阶段保持现有 toolchain（4.27.x），不立即接入外部仓库作为硬依赖。 | locked | 避免版本漂移导致构建不稳定。 |
| 2026-02-13 | 外部候选仓库仅登记不集成：`RemyDegenne/CLT`、`RemyDegenne/brownian-motion`、`BasharHamade12/MarkovChain_Formalisation_Lean`。 | active | 为后续补齐 CLT/Brownian/Markov chain 留出路线图。 |
| 2026-02-13 | 文档治理采用“中文 + 多文档索引制”，并固定 `INDEX/DecisionLog/ModuleCatalog/GapLedger/books/*` 结构。 | locked | 后续扩展到多本书时可持续维护。 |
| 2026-02-13 | 增加 `AGENTS.md` 作为仓库级执行规范；要求“新信息必回写文档系统”，并执行“非随意删除、删除必须留痕”。 | locked | 后续所有任务都有统一约束，降低信息丢失和误删风险。 |
| 2026-02-13 | 新增书籍覆盖基线：Lattimore & Szepesvari《Bandit Algorithms》，采用 Part I-VII 组织并引入 `MLTheory.Bandits.*` 模块族。 | locked | 建立 bandit/在线决策主线，补齐与现有概率/学习模块的连接。 |
| 2026-02-13 | Bandit 当前策略：先建定义与章节索引占位，不立即引入外部依赖（GitHub 检索暂未发现成熟 Lean4 bandit 专项仓库）。 | active | 降低初期实现风险，同时保留后续并入外部成果的空间。 |
| 2026-02-13 | 新增书籍覆盖基线：Hazan《Introduction to Online Convex Optimization (Second Edition)》，采用“优先复用已有模块 + 最小新增 OCO 模块”策略。 | locked | 控制模块冗余，确保 OCO 与 Bandit/Convex/Probability 模块一致协作。 |
| 2026-02-13 | 执行全量文档去重：移除各书覆盖文档中的重复治理说明，统一以 `INDEX.md` + 模板文档作为规则单一来源。 | locked | 降低文档冗余，避免多处规则漂移。 |
| 2026-02-13 | 第二轮去重：移除书籍覆盖文档中与 `ModuleCatalog.md` 重复的模块长列表，保留“章节映射 + 缺口动作 + 证据”三要素。 | locked | 将模块清单收敛到单一事实源（`ModuleCatalog.md`），降低跨文档维护成本。 |
| 2026-02-13 | 新增书籍覆盖基线：Mohri-Rostamizadeh-Talwalkar《Foundations of Machine Learning (2nd)》，采用“复用既有 Learning/OCO/Bandit 模块 + 最小新增缺口模块”策略。 | locked | 在不扩散模块命名的前提下纳入 FoML2 主线，保持跨书一致性。 |
| 2026-02-13 | FoML2 信息源限定为官方 MIT Press 页面与官方 TOC PDF；Lean 生态状态以 GitHub API 检索结果为准，不使用未验证二手摘要。 | locked | 降低目录与生态判断误差，满足“不可编造”约束。 |
| 2026-02-13 | 实施 FoML2 第一批代码骨架：`Ch02_PACLearning`、`Ch03_RademacherVCDimension`、`Ch04_ModelSelection` 三个占位模块已创建并接入 `MLTheory` 入口。 | locked | FoML2 从“纯文档规划”进入“可编译占位实现”阶段，便于后续逐章填充定理。 |
| 2026-02-13 | 网络超时场景采用 `terminal-vpn-proxy`（`run_with_proxy.sh`）拉取 mathlib cache，并完成 `lake build`。 | active | 形成可复用的网络故障处理路径，降低后续依赖拉取失败风险。 |
| 2026-02-13 | 实施 FoML2 第二批代码骨架：`Ch05_SupportVectorMachines`、`Ch06_KernelMethods` 已创建并接入 `MLTheory.Books.FoML2` 入口。 | locked | FoML2 的 SVM/Kernel 主线已进入可编译占位阶段，后续可直接叠加 primal-dual 与 representer theorem 证明。 |
| 2026-02-13 | 新增书籍覆盖基线：Sutton-Barto《Reinforcement Learning: An Introduction (2nd)》，采用“复用 Bandits/OCO/Learning 模块 + 最小新增 RL 模块族”策略。 | locked | 在不重复造轮子的前提下纳入 RL 主线，并与既有书籍共享术语与证明接口。 |
| 2026-02-13 | RL2 目录证据优先使用作者官方书页与 MIT Press eTextbook TOC；Lean 生态状态以 GitHub API 检索结果为准。 | locked | 降低章节映射与生态判断误差，满足“不可编造”约束。 |
| 2026-02-13 | 实施 RL2 第一批代码骨架：`Ch03_MDP`、`Ch04_DynamicProgramming` 已创建并接入 `MLTheory.Books.SuttonBartoRL2` 入口。 | locked | RL2 从纯文档规划进入可编译占位实现阶段，后续可直接追加 Bellman/DP 收敛定理陈述。 |
| 2026-02-13 | 文档检索与展示采用 JSON 单一事实源：`docs/ssot/registry.json`；Markdown 文档全部改为派生文件。 | locked | 避免多处手工维护导致漂移，支持 Codex/jq/python 稳定检索与自动更新。 |
| 2026-02-13 | 新增 `tools/docs/validate_ssot.py` 与 `tools/docs/sync_docs.py`，文档维护流程固定为“先改 SSOT，再生成派生文档”。 | locked | 建立可重复执行的文档契约校验与生成流水线。 |
| 2026-02-13 | 代码组织改为概念优先分层：`Core/Methods/Applications` 承载定义与方法，`Books/*` 收敛为兼容适配层。 | locked | 实现跨书复用与稳定导入路径，同时不破坏既有章节 import。 |
| 2026-02-13 | 接入本地 Lean 专用技能：从同级仓库 `lean-proof-skills` 安装 `lean4` skill 到 `~/.codex/skills/lean4`，后续 Lean 任务优先按该技能流程执行。 | active | 统一 Lean 证明与排错流程，降低 tactic 试错与检索成本，提高 mathlib/LSP 使用一致性。 |
| 2026-02-13 | 三仓协同关系锁定：`paper-template` 作为运行入口，`lean-proof-skills` 作为 skillpack 父仓（含 `lean4` 与 `ml-paper-workflow`），`MLTheory` 作为 Lake `git + tag` 依赖。 | locked | 明确职责边界并支持独立升级/回滚。 |
| 2026-02-13 | 模板仓技能接入方式锁定：`.agents/skillpacks/lean-proof-skills` 使用 submodule；`.agents/skills/lean4` 与 `.agents/skills/ml-paper-workflow` 使用 facade symlink。 | locked | 确保 Codex 在 repo-scope 优先加载项目技能，减少全局配置漂移。 |
| 2026-02-13 | Lean LSP 统一接入策略锁定为 `codex mcp add lean-lsp -- uvx lean-lsp-mcp`，全局技能仅作兜底，正式链路以模板仓 repo-scope 配置为准。 | active | 提升交互式证明与检索稳定性，并降低环境差异。 |
| 2026-02-13 | 占位治理采用两阶段门禁：Phase 1 允许 `Applications/Books/Legacy` 占位但 `Core/Methods` 必须为 0；Phase 2 在 CI 对 `Core/Methods` 占位回归硬失败。 | active | 在保证迭代速度的同时，持续收敛核心层证明质量。 |
| 2026-02-13 | 补齐旧路径兼容层：新增 `MLTheory.Probability/Statistics/OR/Learning/AI/LLM/OCO/RL/Bandits/HDP` 与 `Concentration/Optimization/InfoTheory` 薄封装入口，避免历史 import 断裂。 | active | 新旧导入路径可并行编译，迁移成本可控。 |
| 2026-02-13 | CI 增加导入回归冒烟：`Eval/ImportSmoke.lean` 同时验证分层路径与兼容路径可编译。 | active | 防止后续重构破坏兼容入口。 |
| 2026-02-14 | 新增术语白话表 `docs/Glossary.md` 并纳入自动生成流程，用于统一解释 JSON/SSOT/Lean/CI 相关术语。 | active | 减少沟通黑话，确保用户与 Codex 对关键概念的语义一致。 |
| 2026-02-14 | 删除 `AGENT.md` 兼容入口并将唯一规范入口统一为 `AGENTS.md`；无语义损失，相关约束已并入主规范文件。 | locked | 减少重复入口与维护歧义，避免规范分叉。 |
| 2026-02-14 | 执行“工具优先重排”：MLTheory 主库只承载通用学习理论工具（Rademacher/Contraction/PAC+Concentration），题目专用定理留在 paper-template。 | locked | 避免把单题建模污染共享库接口，提升跨论文复用性。 |
| 2026-02-14 | 完成外部库审计：`auto-res/lean-rademacher`（Lean 4.27.0-rc1，MIT）可作为高优先参考；`YuanheZ/lean-stat-learning-theory`（Lean 4.27.0-rc1，license 未声明）暂不作为直接依赖。 | active | 形成“可复用声明名 + 许可证 + 直接依赖可行性”的审计基线，后续接入可追溯。 |
| 2026-02-14 | 外部库二次审计补充：`google/formal-ml` 为 Lean3 体系（含 PAC/VC 文件但非 Lean4 toolchain），`mahi97/ml-proofs-lean4` 偏优化方向且与当前 Rademacher/PAC 工具主链不匹配，均暂不纳入直接依赖。 | active | 补全“优先现成库”审计覆盖面，并避免把版本/主题不匹配仓库误接入主链。 |
| 2026-02-14 | 确认 `banr1/tailored-lean-stat-learning-theory` 与 `YuanheZ/lean-stat-learning-theory` 当前提交一致（同 HEAD），按同一候选去重管理。 | active | 减少候选重复记录，避免审计结果分叉。 |
| 2026-02-14 | 锁定“完全形式化（严格版）”完成标准：Theorem42/43 最终入口不暴露中间桥接接口，且以 Lean 编译通过与签名门禁作为验收条件。 | locked | 为后续实现提供统一的终态定义与自动化验收口径。 |
| 2026-02-14 | Theorem42 严格版主路线锁定为 Stone-Weierstrass：先用可分离点子代数建立 epsilon 逼近，再回灌到二层参数化接口。 | locked | 优先复用 mathlib 成熟定理，减少重复造轮子并提高证明稳定性。 |
| 2026-02-14 | 外部库复用策略锁定为“先本地复刻后评估依赖”：候选声明先在本仓实现与验证，再决定是否引入 git 依赖。 | locked | 避免上游版本与许可证不确定性直接传导到主仓构建链。 |
| 2026-02-14 | Theorem42 strict 入口从“精确表示 witness”升级为“闭包桥接 witness”（`A ⊆ closure(range F₂)`），并保留精确表示兼容包装器。 | active | 降低对代数元素可精确表示的强假设，向课件“二层类稠密”目标更接近。 |
| 2026-02-14 | Theorem42 严格化推进：新增 `TwoLayerStoneRoutePrimitiveData`，并通过 `toClosureData` 自动把“witnessAlg 内稠密”降解为 strict final 所需的闭包见证接口。 | active | 最终入口不再要求手工提供 `hWitnessInClosure`，Theorem42 向“仅保留原始前提”再前进一步。 |
| 2026-02-14 | Theorem42 严格化继续下沉：新增 `TwoLayerStoneRouteGeneratedData`，固定 `witnessAlg = adjoin(range realizeC)`，由 `hSepRange` 自动推出 `hSep`，并新增 strict 入口包装器 `theorem42_strict_final_of_generated`。 | active | 最终接口进一步移除手工子代数字段，用户仅需提供“range 分离点 + 在 adjoin 子类型的稠密性”两类更原始条件。 |
| 2026-02-14 | Theorem42 再下沉：新增 `TwoLayerStoneRouteAlgebraClosedData`，用 `Algebra.adjoin_induction` 从“常数/加法/乘法可实现”自动推出 `adjoin(range)` 的精确可表示，并新增 `theorem42_strict_final_of_algebra_closed` 包装器。 | active | 该分支不再要求 `hDenseInAdjoin`；strict final 可由更原始、可检验的代数闭包前提驱动。 |
| 2026-02-14 | Theorem42 接口再降黑话：新增参数级分离点接口（`hSepParam : ∀ x ≠ y, ∃ p, realizeC p x ≠ realizeC p y`）及自动转换链，新增 strict 包装器 `theorem42_strict_final_of_generated_param_sep` 与 `theorem42_strict_final_of_algebra_closed_param_sep`。 | active | 调用端不再需要直接书写 `Set.SeparatesPoints`；可用更直观的参数级分离条件接入 strict 路线。 |
| 2026-02-14 | Theorem42 接口结构化：新增 `TwoLayerRealizationAlgebraOps` 与 `TwoLayerStoneRouteAlgebraicGeneratorParamSepData`，将 `hConst/hAdd/hMul` 三个存在性前提收敛为可计算代数操作接口，并新增 strict 包装器 `theorem42_strict_final_of_algebraic_generator_param_sep`。 | active | 调用端前提从“存在性引理集合”收敛为“操作对象 + 语义等式”，更便于 Codex 在项目内复用与自动构造证明上下文。 |
| 2026-02-14 | Theorem42 接口再下沉：新增 `TwoLayerStoneRouteAlgebraicExistsParamSepData`，仅需给出 const/add/mul 的存在性条件；通过 `Classical.choose` 自动生成 `TwoLayerRealizationAlgebraOps`，并新增 strict 包装器 `theorem42_strict_final_of_algebraic_exists_param_sep`。 | active | 调用端可从“显式操作构造”降到“存在性证明”，进一步减少样板并保持 strict 路线可编译验证。 |
| 2026-02-14 | Theorem42 接口继续下沉：新增 `TwoLayerStoneRouteEvalExistsParamSepData`，仅要求在 `evalTwoLayerParams` 层给出 const/add/mul 闭包存在性；自动提升为函数层存在性并新增 strict 包装器 `theorem42_strict_final_of_eval_exists_param_sep`。 | active | 调用端可只在网络公式级别证明闭包条件，不必手写 `C(UnitCube d, ℝ)` 等式，进一步降低接入成本。 |
| 2026-02-14 | Theorem42 接口继续构造化：新增 `TwoLayerEvalAlgebraOps` 与 `TwoLayerStoneRouteEvalConstructiveParamSepData`，调用端直接提供 const/add/mul 参数构造子及 eval 语义；系统自动降解到 strict 路线。 | active | 调用端从“存在性证明”进一步收敛为“构造函数 + 语义证明”，便于后续从网络拼接算子自动派生接口实例。 |
| 2026-02-14 | Theorem42 分离点接口构造化：新增 `TwoLayerStoneRouteEvalSeparationOpsData`，调用端通过 `sepParam + sep_spec` 显式给出点分离构造子；系统自动生成 `hSepParam` 并接入 strict 路线。 | active | 调用端不再手写分离点存在性 `∃ p`，接口向“网络构造子驱动”进一步收敛。 |
| 2026-02-14 | Theorem42 最终自然入口落地：新增 `TwoLayerTheorem42NaturalData`，并给出 `theorem42_strict_final_natural`/`theorem42_strict_final_natural_formula`；最终调用接口不再暴露 Stone 中间结构名。 | active | 对外可直接使用“网络构造子 + 分离构造子”接口调用 strict 定理，内部保持 Stone 路线证明闭环。 |
| 2026-02-14 | 补充单点域自动实例化路径：新增 `TwoLayerEvalAlgebraOps.toNaturalData_of_subsingleton` 与 `theorem42_strict_final_natural_of_subsingleton`，在 `UnitCube d` 为 subsingleton 时免去分离构造子输入。 | active | 为最终自然入口提供可执行的零样板实例化通道，降低最小可用接入成本。 |
| 2026-02-14 | 外部候选复检：发现 `Leorasz/uat_proof`（Lean4，Leshno 1993 UAT 方向，当前 WIP，仓库仅 `README.md` 与 `step1.lean`，无可直接依赖的 Lake 项目骨架）。 | active | 可作为定理路线参考证据，但暂不适合作为 git 依赖；继续采用“本仓自研 + 声明级复刻评估”策略。 |
| 2026-02-15 | Theorem42 接口继续去前提化：新增 `TwoLayerTheorem42NaturalLocalData` 与 `TwoLayerTheorem42SurjectiveData`，并提供 strict 包装器 `theorem42_strict_final_natural_local` / `theorem42_strict_final_of_surjective_realizeC`。 | active | 调用端可用“局部闭包”或“满射实现”两条路径接入 strict 最终定理，进一步降低手工装配成本，且不改变 Stone 主证明链。 |
| 2026-02-15 | Theorem42 接口补桥：新增 `TwoLayerStoneRouteEvalSeparationOpsData.toNaturalData` 与 strict 包装器 `theorem42_strict_final_natural_of_eval_separation_ops`，使 EvalSeparationOps 可直接走自然入口。 | active | 调用端若已有 `ops + sepParam` 可直接接入自然 strict 接口，减少 Stone 中间对象显式装配。 |
| 2026-02-15 | 外部复检新增 `or4nge19/NeuralNetworks`（Apache-2.0，Lean4 v4.24.0-rc1）：内容以 Hopfield/LLM/NN 建模为主，未提供可直接复用的 UAT（Theorem42）定理入口。 | active | 作为神经网络形式化参考候选保留，但当前不作为 Theorem42 严格路线依赖。 |
| 2026-02-15 | Theorem42 接口再去前提化：新增 `TwoLayerStoneRouteEvalCoordinateOpsData` 与 `toEvalSeparationOpsData`，并提供 strict 包装器 `theorem42_strict_final_natural_of_eval_coordinate_ops`。 | active | 调用端只需给出坐标参数族 `coordParam` 与代数操作，即可自动合成点分离并接入自然 strict 入口。 |
| 2026-02-15 | Theorem42 主接口收口：引入 `TwoLayerTheorem42FinalData`（最终对象）与 `theorem42_strict_final_final`/`theorem42_strict_final_class_dense`，并在最终对象上显式提供 const/add/mul/separatesPoints 能力定理。 | active | Theorem42 现在具备‘函数类本身稠密’的稳定最终入口，后续工作聚焦于具体激活函数实例化，不再扩展中间桥接层。 |
| 2026-02-15 | 签名门禁升级：`check_final_signature.sh` 新增对 `theorem42_strict_final_final` 的禁止中间前提检查。 | active | 保证 canonical Theorem42 最终入口不回归到 `hDense/UniversalApprox.../SampleConcentration...` 等中间假设接口。 |
| 2026-02-15 | 进入“架构反思与重构”阶段：Theorem42/43 不再扩展新中间桥接定理，后续仅允许 API 收敛、边界整理与门禁补强。 | locked | 将迭代重点从定理数量增长转向接口稳定性与维护成本收敛。 |
| 2026-02-15 | 三仓职责边界细化：MLTheory 仅承载跨论文可复用的通用工具接口；paper-template 保留题目/讲义绑定对象（如 `TwoLayerTheorem42FinalData`、`theorem42_strict_final_*`、`Theorem43PrimitiveModel`）与实例化证明。 | locked | 避免题目专用命名污染公共库，降低跨仓升级时的耦合与回归风险。 |
| 2026-02-15 | 下一阶段最小 canonical API 基线锁定为 `MLTheory.Core.Learning.{PACProblem,HypothesisClass}` 与 `MLTheory.Methods.Learning.{stone_exists_uniform_near,stone_closure_eq_top,FiniteClassConcentrationBundle,subgaussianTailENN,radStd,radAbs,pac_badEvent_uniform_bound}`。 | active | 为重构提供可验收的稳定符号集合，并明确“上移 MLTheory”范围。 |
| 2026-02-15 | 新增架构门禁：`Eval/CanonicalAPISmoke.lean` 校验 canonical API 可见性，`tools/ci/check_layer_imports.sh` 校验 Core/Methods 分层边界并禁止 `import Paper.*` 泄漏。 | active | 重构过程可回滚且可验收，边界回归可在 CI 第一时间暴露。 |
| 2026-02-15 | Phase 0 增加 `lean4` 外部基线审查门槛：先审 `/Users/xiongjiangkai/.codex/skills/lean4` 是否覆盖独立验证契约，再判定 native/augmented 模式。 | active | 保证不盲改外部复制 skill，同时把“是否补契约层”变成可复现判定。 |
| 2026-02-15 | SSOT 升级到 schema v1.2.0：新增 `concepts`、`official_workflow_refs`、`canonical_specs`，并给 `modules` 增加 `concept_id/role/user_surface/formal_decl_refs`。 | locked | 从“模块台账”升级为“概念-工具-契约”统一数据源，支持森林可视化与独立验证门禁。 |
| 2026-02-15 | 官方对齐策略锁定：工具组织与检索流程必须显式映射 Lean Learn 与 VSCode Lean4 Manual 推荐能力（Loogle/LeanSearch/InfoView+LoogleView/REPL）。 | locked | 避免仅基于本地工程经验定义流程，提升跨环境可解释性与一致性。 |
| 2026-02-15 | skills 分流策略锁定：`lean4` skill 保持外部基线不修改；`ml-paper-workflow` 作为入口按审查结论分流 native/augmented，augmented 先执行 formalization-contract 再调用 lean4。 | active | 在不破坏现有 lean4 工作流的前提下补齐项目级独立验证约束。 |
| 2026-02-16 | Taxonomy v2 重整：采用层级树主导 + 三层标签；modules 仅保留真实 file-backed 模块，无文件条目迁移到 planned_modules；Books/Legacy 改为 source_track 轴。 | active | 结构可视化与治理从扁平 domain 迁移到 taxonomy_nodes/taxonomy_relations，减少语义混杂并提升独立验证可追踪性。 |
| 2026-02-16 | canonical_specs 三仓边界收敛：MLTheory SSOT 仅保留 repo=MLTheory 的通用 canonical 契约；paper-template 题目专属契约迁回论文仓脚本配置。 | active | 避免跨仓 canonical 规则混放，降低边界漂移风险。 |
| 2026-02-16 | 结构重整 Phase E 采用“先证据清单、后删除”：新增 StructureCleanupCandidates 台账，记录定义文件/引用证据/风险/动作。 | active | 把删除讨论从主观判断改为可审计证据，避免误删兼容入口。 |
| 2026-02-16 | 结构清理候选进入执行排期：按 B1/B2/B3 分批，统一先 deprecated 再删；每条候选明确 compatibility_window 与 replacement_imports。 | active | 把“是否删除”从讨论变成可执行排期，降低外部导入断裂风险。 |
| 2026-02-16 | 执行结构清理 B1：在 MLTheory.Applications / MLTheory.LLM / MLTheory.OCO 落地 deprecated 标记与迁移提示，不做物理删除。 | active | B1 进入“已公告弃用”状态，兼容入口仍可用，调用方可按 replacement_imports 渐进迁移。 |
| 2026-02-16 | 执行结构清理 B2：在 MLTheory.Bandits / MLTheory.HDP / MLTheory.RL 落地 deprecated 标记与迁移提示，不做物理删除。 | active | B2 进入“已公告弃用”状态，兼容入口仍可用，调用方可按 replacement_imports 渐进迁移。 |
| 2026-02-16 | 执行结构清理 B3：在 MLTheory.Books 落地 deprecated 标记与迁移提示，不做物理删除。 | active | B3 进入“已公告弃用”状态，兼容入口仍可用，调用方可按 replacement_imports 渐进迁移。 |
| 2026-02-16 | 迁移阶段启动：主入口 MLTheory.lean 已移除对 7 个弃用兼容模块的直接 import，deprecated_import allowlist 收敛为 0。 | active | 结构清理候选从 deprecated_announced 统一进入 migrating；后续仅保留防回流门禁并按窗口评估 ready_to_remove。 |
| 2026-02-16 | 新增 release 窗口自动判定门禁：以 cleanup_release_epoch + remove_after_releases + migration_started_epoch 计算 ready_to_remove，禁止人工拍脑袋判定。 | active | ready_to_remove 进入机器可审计流程，迁移窗口到期会被 CI 主动提示。 |
| 2026-02-16 | 推进 cleanup_release_epoch 到 2，并将到期候选切换为 ready_to_remove：MLTheory.Applications / MLTheory.LLM / MLTheory.OCO。 | active | release 窗口推进由脚本统一落地，ready_to_remove 转换可复现且可审计。 |
| 2026-02-16 | 执行物理删除 B1：移除兼容入口文件 MLTheory.Applications / MLTheory.LLM / MLTheory.OCO，并在 aliases 保留迁移映射。 | active | B1 从 ready_to_remove 进入已落地删除；旧入口不再可 import，迁移路径由 aliases 与文档明确给出。 |
| 2026-02-16 | 推进 cleanup_release_epoch 到 3，并将到期候选切换为 ready_to_remove：MLTheory.Bandits / MLTheory.HDP / MLTheory.RL。 | active | release 窗口推进由脚本统一落地，ready_to_remove 转换可复现且可审计。 |
| 2026-02-16 | 执行物理删除 B2：移除兼容入口文件 MLTheory.Bandits / MLTheory.HDP / MLTheory.RL，并在 aliases 保留迁移映射。 | active | B2 从 ready_to_remove 进入已落地删除；旧入口不再可 import，迁移路径由 aliases 与文档明确给出。 |
| 2026-02-16 | 推进 cleanup_release_epoch 到 4，并将到期候选切换为 ready_to_remove：MLTheory.Books。 | active | release 窗口推进由脚本统一落地，ready_to_remove 转换可复现且可审计。 |
| 2026-02-16 | 执行物理删除 B3：移除兼容入口文件 MLTheory.Books，并在 aliases 保留迁移映射。 | active | B3 从 ready_to_remove 进入已落地删除；旧总入口不再可 import，迁移路径由 aliases 与文档明确给出。 |
| 2026-02-16 | 进入命名空间收敛阶段：新增 check_namespace_layout 门禁，强制分层前缀与 alias 收敛规则。 | active | 后续结构调整不再依赖人工约定，模块路径/兼容映射漂移会被 CI 直接拦截。 |
| 2026-02-16 | 新增 NamespaceConvergence 视图并纳入文档索引，用于展示分层前缀、legacy 入口与 alias 迁移关系。 | active | 使用者可直接看到“现在该 import 什么”，降低结构重整后的认知负担。 |
| 2026-02-16 | 启动 legacy 顶层入口收敛排期：AI/Concentration/InfoTheory/Learning/OR/Optimization/Probability/Statistics 纳入 cleanup 候选（pending），先迁移后弃用。 | active | 顶层 legacy 入口进入证据化治理阶段；后续可按 batch/窗口推进，不再拍脑袋删。 |
| 2026-02-16 | 执行结构清理 B4：在 MLTheory.AI / MLTheory.Concentration / MLTheory.InfoTheory / MLTheory.Optimization 落地 deprecated 标记与迁移提示，不做物理删除。 | active | B4 进入已公告弃用状态；兼容入口仍可导入，调用方可按 replacement_imports 渐进迁移。 |
| 2026-02-16 | 执行结构清理 B4 迁移：MLTheory.AI / MLTheory.Concentration / MLTheory.InfoTheory / MLTheory.Optimization 已从主入口与 ImportSmoke 移除，状态切换为 migrating。 | active | B4 兼容入口已无仓内直接 import，后续按 release 窗口推进 ready_to_remove 与物理删除。 |
| 2026-02-16 | 执行结构清理 B5：在 MLTheory.Learning / MLTheory.OR / MLTheory.Probability / MLTheory.Statistics 落地 deprecated 标记与迁移提示，不做物理删除。 | active | B5 进入已公告弃用状态；兼容入口仍可导入，调用方可按 replacement_imports 渐进迁移。 |
| 2026-02-16 | 执行结构清理 B5 迁移：MLTheory.Learning / MLTheory.OR / MLTheory.Probability / MLTheory.Statistics 已从主入口与兼容链路移除，状态切换为 migrating。 | active | B5 兼容入口已无仓内直接 import，后续按 release 窗口推进 ready_to_remove 与物理删除。 |
| 2026-02-16 | 推进 cleanup_release_epoch 到 5，本次无候选到期切换为 ready_to_remove。 | active | release 窗口推进由脚本统一落地，ready_to_remove 转换可复现且可审计。 |
| 2026-02-16 | 推进 cleanup_release_epoch 到 6，并将到期候选切换为 ready_to_remove：MLTheory.AI / MLTheory.Concentration / MLTheory.InfoTheory / MLTheory.Optimization。 | active | release 窗口推进由脚本统一落地，ready_to_remove 转换可复现且可审计。 |
| 2026-02-16 | 执行物理删除 B4：移除兼容入口文件 MLTheory.AI / MLTheory.Concentration / MLTheory.InfoTheory / MLTheory.Optimization，并在 aliases 保留迁移映射。 | active | B4 从 ready_to_remove 进入已落地删除；旧入口不再可 import，迁移路径由 aliases 与文档明确给出。 |
| 2026-02-16 | 推进 cleanup_release_epoch 到 7，并将到期候选切换为 ready_to_remove：MLTheory.Learning / MLTheory.OR / MLTheory.Probability / MLTheory.Statistics。 | active | release 窗口推进由脚本统一落地，ready_to_remove 转换可复现且可审计。 |
| 2026-02-16 | 执行物理删除 B5：移除兼容入口文件 MLTheory.Learning / MLTheory.OR / MLTheory.Probability / MLTheory.Statistics，并在 aliases 保留迁移映射。 | active | B5 从 ready_to_remove 进入已落地删除；旧入口不再可 import，迁移路径由 aliases 与文档明确给出。 |
| 2026-02-16 | 结构清理批次收敛：B1/B2/B3/B4/B5 兼容入口已全部完成物理删除，后续仅保留 aliases 迁移映射与门禁防回流。 | active | 兼容层清理进入稳定态；结构治理重心转为 canonical API 与分层边界长期维护。 |
| 2026-02-16 | 防回流门禁升级：check_no_new_deprecated_imports 从“仅候选期”扩展为“候选期 allowlist + 已删除入口硬禁止 import”。 | active | 结构清理完成后仍可持续拦截旧入口回流，不再出现“候选清零后门禁失效”的窗口。 |
| 2026-02-16 | StrictFormalization Phase4 状态更新：ArchitectureRefactor 与 CanonicalAPIAndGates 已收敛为 covered，转入长期维护门禁。 | active | 架构重整从执行阶段进入维护阶段；后续新增能力必须先过 canonical/分层/官方对齐门禁。 |
| 2026-02-16 | SSOT 质量收敛：纯重导出模块角色统一为 bridge，并为有声明的 tool 模块补齐 formal_decl_refs，清除 validate_ssot 噪声警告。 | active | 文档与门禁输出更干净，tool/bridge 语义边界更明确，后续审计不再被空声明提示干扰。 |
| 2026-02-16 | planned_modules 命名空间收敛：legacy 规划项已迁移到 canonical 分层前缀（Core/Methods/Applications），并统一 source_track= native。 | active | 规划层不再使用 MLTheory.Probability/OR/RL 等旧根命名；主树和分层语义在“未落地模块”上也保持一致。 |
| 2026-02-16 | book 规划命名修复：`MLTheory.HDP.*` 规划项迁移到 `MLTheory.Books.VershyninHDP.*`，并同步覆盖台账/缺口中的旧路径文本。 | active | Books 轴命名统一到 `MLTheory.Books.*`，避免 source_track=books 与模块路径不一致。 |
| 2026-02-16 | 去重收敛：移除与现有真实模块重复的规划项 `MLTheory.RL.DynamicProgramming`。 | active | 避免 modules 与 planned_modules 语义重叠，减少结构台账噪声。 |
| 2026-02-16 | SSOT 契约硬化：planned_modules 的 source_track 收敛为 {native, books}，legacy 仅保留给已落地兼容模块。 | active | 规划层与兼容层语义彻底分离；legacy 命名不再通过 schema/validator。 |
| 2026-02-16 | 迁移脚本收敛：migrate_ssot_to_taxonomy_v2 对 v2 registry 保持幂等，并遵守 planned_modules 的 canonical 前缀与 source_track 契约。 | active | 重复执行迁移不会清空或重排现有规划数据，迁移工具与门禁/SSOT 契约保持一致。 |
| 2026-02-16 | 新增门禁 check_ssot_migration_idempotent：CI + formalization_preflight 强制校验迁移脚本幂等，防止 SSOT 工具回归。 | active | 任何会改写现有 registry 的迁移脚本变更都会被立即拦截，独立验证链路更完整。 |
| 2026-02-16 | 新增 StructureIssues 派生文档：从当前 SSOT 自动提取结构问题证据，并给出分批整改顺序与回滚点。 | active | 结构重整从“看图主观判断”升级为“问题台账驱动”，用户可直接看到先后顺序和验收门禁。 |
| 2026-02-16 | 执行结构重整 Phase-1：新增 Probability/Statistics/OR/OCO/Bandits/AI/LLM 的 file-backed 骨架根模块。 | active | 主树空心节点显著减少，用户可从分层根模块直接定位对应领域入口。 |
| 2026-02-16 | Applications 层占位入口收敛：`MLTheory.Applications.Learning` 与 `MLTheory.Applications.RL` 从 placeholder 角色升级为 bridge。 | active | 公开入口不再以 placeholder 语义暴露，结构文档与用户直觉更一致。 |
| 2026-02-16 | deprecated alias 目标重锚：Bandits/OCO/OR/Probability/Statistics/AI/LLM 等旧入口改指向对应分层根模块。 | active | 旧入口迁移路径从“泛化指向”变为“领域对位指向”，降低迁移歧义。 |
| 2026-02-16 | Phase-2 启动：将 7 条 active alias 纳入 `structure_cleanup_candidates`（B6, pending），先迁移导入再退役。 | active | active alias 进入可审计迁移队列；后续可按 release 窗口推进到 deprecated_announced/migrating。 |
| 2026-02-16 | B6 候选窗口策略：compatibility_window=2 releases，migration_started_epoch=7。 | active | 为 FoML2/SB2 章节 alias 设定统一退役节奏，保证可回滚且可验证。 |
| 2026-02-16 | 执行 Phase-2/B6 第一批：FoML2 五个章节 alias 完成导入迁移，候选状态切换为 deprecated_announced。 | active | active alias 从 7 降到 2；旧章节入口进入公告退役期并受防回流门禁约束。 |
| 2026-02-16 | 执行 Phase-2/B6 第二批：SuttonBartoRL2 两个章节 alias 完成导入迁移，候选状态切换为 deprecated_announced。 | active | active alias 清零；章节兼容入口全部进入公告退役期。 |
| 2026-02-16 | 执行结构重整 Phase-3 第一批：将 7 个 canonical/tool 的 statement hook 升级为可检查 theorem 证明，并把对应模块 proof_status 从 statement 收敛为 proved。 | active | S4（关键入口仍是 statement）进入收敛状态；后续可在不改接口名的前提下继续补强真实理论命题。 |
| 2026-02-16 | 执行结构重整 Phase-4：清理 planned_modules 状态语义，将无外部可复用证据的 partial 统一收敛为 planned，并建立 partial 需证据的校验规则。 | active | S5（规划模块状态混杂）收敛；路线图状态更直观且可由 validate_ssot 自动门禁。 |
| 2026-02-16 | 推进 cleanup_release_epoch 到 8，本次无候选到期切换为 ready_to_remove。 | active | release 窗口推进由脚本统一落地，ready_to_remove 转换可复现且可审计。 |
| 2026-02-16 | 推进 cleanup_release_epoch 到 9，并将到期候选切换为 ready_to_remove：MLTheory.Books.FoML2.Ch02_PACLearning / MLTheory.Books.FoML2.Ch03_RademacherVCDimension / MLTheory.Books.FoML2.Ch04_ModelSelection / MLTheory.Books.FoML2.Ch05_SupportVectorMachines / MLTheory.Books.FoML2.Ch06_KernelMethods / MLTheory.Books.SuttonBartoRL2.Ch03_MDP / MLTheory.Books.SuttonBartoRL2.Ch04_DynamicProgramming。 | active | release 窗口推进由脚本统一落地，ready_to_remove 转换可复现且可审计。 |
| 2026-02-16 | 执行物理删除 B6：移除兼容入口文件 MLTheory.Books.FoML2.Ch02_PACLearning / MLTheory.Books.FoML2.Ch03_RademacherVCDimension / MLTheory.Books.FoML2.Ch04_ModelSelection / MLTheory.Books.FoML2.Ch05_SupportVectorMachines / MLTheory.Books.FoML2.Ch06_KernelMethods / MLTheory.Books.SuttonBartoRL2.Ch03_MDP / MLTheory.Books.SuttonBartoRL2.Ch04_DynamicProgramming，并在 aliases 保留迁移映射。 | active | B6 从 ready_to_remove 进入已落地删除；FoML2/SB2 章节兼容入口不再可 import，迁移路径由 aliases 与文档明确给出。 |
| 2026-02-16 | 维护态数据清洁：覆盖映射与缺口台账移除 deprecated alias 引用，并去重 coverage_rows 中重复模块引用。 | active | 文档层面不再回流旧入口名；覆盖表可读性提升，后续可由新增引用卫生门禁持续约束。 |
| 2026-02-16 | 新增引用卫生门禁 `check_registry_reference_hygiene.py` 并接入 CI 与 formalization_preflight，禁止 books/gaps 引用 deprecated alias，禁止 coverage 行重复模块引用。 | active | 维护态下文档引用不再回流旧入口；覆盖映射文本质量可持续由门禁自动校验。 |
| 2026-02-16 | 维护态收口：清理 meta.policy 中已过期的 cleanup 瞬时状态标签，并在 validate_ssot 增加一致性校验（cleanup 候选清零后禁止保留 pending/migrating/ready_to_remove 标签）。 | active | 避免“实际已完成但策略标签仍显示进行中”的误导，确保结构状态可被机器与人一致解读。 |
| 2026-02-16 | 结构语义修正：`MLTheory` 根入口模块在 SSOT 中从 `legacy/compat` 收敛为 `native/bridge`，仅调整结构标注，不改变任何导入与定理行为。 | active | 根入口在可视化与台账中不再被误判为历史兼容层，分层解释更直观。 |
| 2026-02-16 | 规划收敛：新增 `execution_backlog`（near/mid/far）短清单，把 96 条 planned_modules 收敛为可执行队列；ToolForestInteractive 默认先显示真实模块。 | active | 用户查看结构时先看真实层、再看短清单，减少信息噪声并提升执行节奏。 |
| 2026-02-16 | 执行 backlog 近期批次：`MLTheory.Core.Probability.Conditioning` 与 `MLTheory.Core.Probability.ProbIneq` 已从 planned_modules 提升为真实 file-backed modules，并接入 ImportSmoke。 | active | 概率核心层新增可复用 conditioning/inequality 入口，execution_backlog 的 near 项开始实质消化。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Core.Statistics.Risk` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | 统计核心层新增 risk 语义壳层，near 短清单进一步收敛。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Methods.OR.ConvexCore` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | OR 方法层新增凸优化核心抽象，near backlog 继续收敛。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Methods.Bandits.Foundations` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Bandits 方法层形成统一 foundations 入口，near backlog 继续缩短。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Methods.OCO.OptimizationCore` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | OCO 主线补齐问题定义/comparator/update 抽象，execution_backlog 近期项完成并进入下一轮中期队列。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Methods.Bandits.Stochastic` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Bandits 主线补齐 UCB/ETC 最小声明壳并复用 Foundations regret 接口，近期队列继续向 OCO/RL 中期项推进。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Methods.OCO.Generalization` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | OCO->Learning 的 online-to-batch 最小桥接接口落地，execution_backlog 近期焦点顺延至 RL.MDP。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Methods.RL.MDP` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | RL 方法层补齐 MDP 入口壳并对齐 Core/DP 接口，execution_backlog 近期焦点顺延至 TemporalDifference。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Methods.RL.TemporalDifference` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | RL 主线补齐 TD 更新与误差递推接口；execution_backlog 近期焦点顺延至 Applications.AI.Generalization。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Applications.AI.Generalization` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | 应用层 AI 泛化桥接入口落地且不新增底层概念；execution_backlog 近期焦点顺延至 Applications.LLM.Autoregressive。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Applications.LLM.Autoregressive` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | 应用层 LLM 自回归入口落地并复用 AI 泛化契约；当前 execution_backlog 清空，后续需人工确定下一批 near 队列。 |
| 2026-02-16 | 执行短清单复位：重建 execution_backlog 为 Capacity(near) / AI.DecisionLearning(mid) / LLM.Sampling(far)。 | active | 恢复“近期-中期-远期”可执行队列，避免 backlog 为空导致推进失焦。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Core.Statistics.Information` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | 统计信息论主线新增 KL/maxent/conditional-gap 最小接口，近期焦点顺延至 Methods.Learning.Capacity。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Methods.Learning.Capacity` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Learning 方法层补齐 capacity/JL 占位接口并连通概率尾界桥接；近期焦点顺延至 Applications.AI.DecisionLearning。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Applications.AI.DecisionLearning` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | AI 应用层补齐 decision-learning 场景入口并复用 Learning/OCO/RL 接口；近期焦点顺延至 Applications.LLM.Sampling。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Applications.LLM.Sampling` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | LLM 应用层补齐 sampling 策略最小接口并与 autoregressive 契约对齐；近期焦点顺延至 Applications.LLM.AlignmentObjectives。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Applications.LLM.AlignmentObjectives` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | LLM 应用层补齐 alignment objective 入口并与 sampling/autoregressive 契约打通；近期焦点切换到 Methods.Bandits.InformationTheory。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Methods.Bandits.InformationTheory` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Bandits 方法层补齐 information-theoretic bonus/regret 入口并复用 cumulativeRegret；近期焦点切换到 Methods.Bandits.Adversarial。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Methods.Bandits.Adversarial` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Bandits 方法层补齐 adversarial regret/EXP3 入口并与共享 cumulativeRegret 对齐；近期焦点切换到 Methods.Bandits.BestArmIdentification。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Methods.Bandits.BestArmIdentification` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Bandits 方法层补齐 BAI/simple-regret/sample-complexity 最小接口；近期焦点切换到 Methods.Bandits.ContextualLinear。 |
| 2026-02-16 | 执行 backlog 近期批次追加：`MLTheory.Methods.Bandits.ContextualLinear` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Bandits 方法层补齐 contextual-linear 问题定义/置信半径/regret 入口；近期焦点切换到 Methods.Bandits.Dueling。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.Bandits.Dueling` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Bandits 方法层补齐 dueling 偏好反馈与 regret 入口；近期焦点切换到 Methods.Bandits.LargeActionSpaces。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.Bandits.LargeActionSpaces` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Bandits 方法层补齐大动作空间候选池规模与 regret 入口；近期焦点切换到 Methods.Bandits.PureExplorationLinear。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.Bandits.PureExplorationLinear` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Bandits 方法层补齐 pure-exploration-linear 的误差半径与 simple-regret 接口；近期焦点切换到 Methods.Bandits.RLBridge。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.Bandits.RLBridge` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Bandits 方法层补齐与 RL.TD 的桥接接口；近期焦点切换到 Methods.OR.DiscreteOptimization。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.OR.DiscreteOptimization` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Methods.OR 形成离散优化最小接口并复用 ConvexCore.objectiveGap；近期焦点切换到 Methods.OR.GraphOptimization。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.OR.GraphOptimization` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Methods.OR 补齐图优化最小接口（路径/割差距）并复用 ConvexCore.objectiveGap；近期焦点切换到 Methods.OR.StochasticMatrix。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.OR.StochasticMatrix` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Methods.OR 随机矩阵最小接口落地并复用 ConvexCore.objectiveGap；OR 近期三项完成，近期焦点切换到 Methods.OCO.BanditConvex。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.OCO.BanditConvex` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Methods.OCO 增加 bandit-convex 估计/遗憾差距接口并复用 OCO regret 核心；近期焦点切换到 Methods.OCO.DynamicRegret。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.OCO.DynamicRegret` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Methods.OCO 增加动态比较器与动态遗憾最小接口；近期焦点切换到 Methods.OCO.GamesAndDuality。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.OCO.GamesAndDuality` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Methods.OCO 补齐 games/duality 最小接口（博弈遗憾与对偶差距）；近期焦点切换到 Methods.OCO.Boosting。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.OCO.Boosting` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Methods.OCO 近期待办全部收口完成；近期焦点切换到 Methods.Learning.AdvancedSLT。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.Learning.AdvancedSLT` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Methods.Learning 补齐 advanced SLT 最小接口；近期焦点切换到 Methods.Learning.Sequential。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.Learning.Sequential` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | active | Methods.Learning 补齐 sequential 学习最小接口并连通 OCO 遗憾定义；近期焦点切换到 Methods.Learning.KernelBayes。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.Learning.KernelBayes` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | locked | Learning 主线补齐 kernel-Bayes 后验更新与风险差距最小接口，execution_backlog 近期焦点顺延至 AutomataLanguage。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.Learning.AutomataLanguage` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | locked | Learning 子线新增离散自动机语言风险接口，execution_backlog 近期焦点顺延至 DiscreteModeling。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Methods.Learning.DiscreteModeling` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | locked | Learning 近期短清单三项（KernelBayes/AutomataLanguage/DiscreteModeling）已全部落地，execution_backlog 转入概率基础补齐。 |
| 2026-02-17 | 执行 backlog 近期批次追加：`MLTheory.Core.Probability.BasicMeasure` 已从 planned_modules 提升为真实 file-backed module，并接入 ImportSmoke。 | locked | foundations 概率层补齐测度基础入口，execution_backlog 近期焦点顺延至 CLTBridge。 |
| 2026-02-18 | 执行 Phase 1 占位清理：Core/Methods 层删除 `*Placeholder*` theorem/lemma，统一替换为 `...Spec : Prop` 声明，并修复 RL bridge 到新 Spec 接口。 | locked | 消除检索与图谱噪音源，确保 Core/Methods 未完成内容以可追踪规格表达而非假定理。 |
| 2026-02-18 | 落地 Phase 3 的 mathlib 结构探索脚本：从 `lake-manifest.json` 自动定位 mathlib，生成 modules/imports/hubs/aggregators/slice 与 `MLTheory→mathlib` 映射产物。 | active | 形成可重复的一键索引与切片管线，为限域检索与后续子图构建提供机器可读基础数据。 |
| 2026-02-18 | 落地 Phase 4 的声明依赖导出：新增 `tools/index/ExtractDeclDeps.lean` 与 `gen_decl_graph.sh`，导出 `uses_type/uses_value` 到 `artifacts/graphs/decl_graph.json`。 | active | 子图从模块级 import 图升级到声明级真实依赖边，可用于邻域检索与“骨干+可展开”可视化。 |
