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
