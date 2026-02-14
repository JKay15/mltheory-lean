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
