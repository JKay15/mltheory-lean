# MLTheory

`MLTheory` 是三仓协同中的共享 Lean 理论库，定位为论文仓可复用的基础定理层。

## 分层结构

- `MLTheory/Core/*`：核心对象与基础陈述（禁止 `Prop := True` 占位）。
- `MLTheory/Methods/*`：方法层接口与可复用构造（禁止 `Prop := True` 占位）。
- `MLTheory/Applications/*`：应用适配层（允许阶段性占位）。
- `MLTheory/Books/*`：书籍章节兼容层与重导出（不承载核心定义）。

公共入口：`/Users/xiongjiangkai/xjk_papers/MLTheory/MLTheory.lean`。

## 开发与验证

```bash
lake exe cache get
lake build
python3 tools/docs/validate_ssot.py
python3 tools/docs/sync_docs.py --check
tools/ci/check_no_sorry_axiom.sh
tools/ci/check_placeholder_policy.sh
```

## 文档系统（SSOT）

- 单一事实源：`/Users/xiongjiangkai/xjk_papers/MLTheory/docs/ssot/registry.json`
- 字段契约：`/Users/xiongjiangkai/xjk_papers/MLTheory/docs/ssot/schema.json`
- 派生文档生成：`python3 tools/docs/sync_docs.py --write`

除 `registry.json` 外，`docs/*.md` 与 `docs/books/*.md` 都是派生文件，不直接手改正文数据。

## 下游依赖（论文模板仓）

在下游仓 `lakefile.toml` 中用 `git + rev(tag)` pin 版本：

```toml
[[require]]
name = "MLTheory"
git = "https://github.com/<YOUR_GITHUB>/mltheory-lean.git"
rev = "v0.1.0"
```

## 与 skills 协作

正式链路使用论文模板仓的 repo-scope skills：

- `.agents/skills/lean4`
- `.agents/skills/ml-paper-workflow`

`~/.codex/skills/lean4` 仅作为临时兜底，不作为正式协同入口。
