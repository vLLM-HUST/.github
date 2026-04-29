# vLLM-HUST

国产算力友好的 vLLM fork 组织，围绕推理运行时、Ascend 使能、开发工作区、Benchmark、Website 与 AI 应用集成构建完整工程链路。

An upstream-compatible vLLM fork organization focused on domestic-hardware enablement, Ascend support, AGI4S serving, benchmark-driven validation, and a practical multi-repository developer experience.

## Quick Links

- Core runtime: [vllm-hust](https://github.com/vLLM-HUST/vllm-hust)
- Ascend plugin: [vllm-ascend-hust](https://github.com/vLLM-HUST/vllm-ascend-hust)
- Runtime manager: [ascend-runtime-manager](https://github.com/vLLM-HUST/ascend-runtime-manager)
- Dev workspace: [vllm-hust-dev-hub](https://github.com/vLLM-HUST/vllm-hust-dev-hub)
- Benchmark wrapper: [vllm-hust-benchmark](https://github.com/vLLM-HUST/vllm-hust-benchmark)
- Website: [vllm-hust-website](https://github.com/vLLM-HUST/vllm-hust-website)
- Workstation: [vllm-hust-workstation](https://github.com/vLLM-HUST/vllm-hust-workstation)
- Docs: [vllm-hust-docs](https://github.com/vLLM-HUST/vllm-hust-docs)
- Research app: [EvoScientist](https://github.com/vLLM-HUST/EvoScientist)

## What We Build

`vLLM-HUST` 以上游 `vLLM` 生态为基础，重点面向下面几类工作：

- 保持与上游 `vLLM` / `vLLM Ascend` 的兼容与可持续同步
- 支持 Ascend 等国产硬件上的推理与部署
- 强化 AGI4S 场景，包括长上下文、工具调用、结构化输出与服务稳定性
- 提供从开发工作区到 Website、Benchmark、Workstation 的完整配套仓库

In practice, the organization concentrates on four goals:

- keep `vllm-hust` mergeable with upstream `vllm` whenever possible
- isolate hardware-specific logic in plugins, managers, and deployment tooling
- validate runtime behavior with real benchmarks, smoke tests, and website-facing artifacts
- connect low-level serving infrastructure to end-user and research-facing products

<!-- contributor-leaderboard:start -->
## 核心贡献者排行榜

下面的榜单展示 `vLLM-HUST` 主要仓库里持续推动组织工程演进的核心贡献者，方便新成员快速了解当前的主要维护力量分布。

说明：

- 统计范围：`vllm-hust`、`vllm-ascend-hust`、`vllm-hust-benchmark`、`vllm-hust-dev-hub`、`vllm-hust-docs`、`vllm-hust-website`、`vllm-hust-workstation`
- fork 去上游：`vllm-hust` 与 `vllm-ascend-hust` 仍以官方上游为参照，但统计时优先按主线首父链上的 PR merge 净 diff 归因给 PR 作者；纯同步上游的 merge 与 main2main / upgrade / sync 型提交不计入榜单
- 统计方式：fork 仓库按 PR merge 的净变更量统计，其他仓库按 `git log --numstat` 聚合；统一指标为 `added + deleted`；直接提交到主线的 author identity 仍按本仓库 `.mailmap` 合并
- 展示规则：排除 bot 账号，列出在至少 1 个主要仓库里有提交的全部贡献者
- 快照时间：`2026-04-29`

| Rank | Contributor | Changed lines | Added / Deleted | Active repos |
| --- | --- | ---: | ---: | ---: |
| 1 | [Shuhao Zhang](https://github.com/ShuhaoZhangTony) | 450,367 | 312,721 / 137,646 | 7 |
| 2 | [MingqiWang-coder](https://github.com/MingqiWang-coder) | 21,098 | 7,282 / 13,816 | 2 |
| 3 | [Xiling Gao](https://github.com/XilingGao) | 12,538 | 12,305 / 233 | 1 |
| 4 | [KimmoZAG](https://github.com/KimmoZAG) | 6,244 | 4,759 / 1,485 | 2 |
| 5 | [iliujunn](https://github.com/iliujunn) | 2,095 | 1,186 / 909 | 2 |
| 6 | [CubeLander](https://github.com/CubeLander) | 802 | 48 / 754 | 1 |
| 7 | [pygone](https://github.com/Pygone) | 187 | 164 / 23 | 1 |
| 8 | [moonandlife](https://github.com/moonandlife) | 32 | 17 / 15 | 2 |

这份榜单更适合表达 `vLLM-HUST` 组织自有工程链路中的持续活跃度，不等价于代码质量、技术难度、设计贡献或社区影响力的完整排序。后续如果需要，也可以继续补充运行时、Ascend、Benchmark / Website 等分榜。
<!-- contributor-leaderboard:end -->

## 组织仓库关系

```mermaid
flowchart TD
    A[vllm-hust\n核心运行时与 OpenAI 兼容服务]
    B[vllm-ascend-hust\nAscend 硬件插件]
    C[ascend-runtime-manager\nAscend 运行时诊断与修复]
    D[vllm-hust-dev-hub\n多仓开发工作区与 quickstart]
    E[vllm-hust-benchmark\nBenchmark 编排与结果导出]
    F[vllm-hust-website\n官网与 Leaderboard 展示]
    G[vllm-hust-workstation\n本地/私有化 Web 工作台]
    H[vllm-hust-docs\n操作手册与同步记录]
    I[EvoScientist\n面向科研智能体的上层应用]

    B --> A
    C --> A
    D --> A
    D --> B
    D --> C
    E --> A
    E --> F
    G --> A
    H --> A
    H --> B
    I --> A
```

## 仓库地图

### Repository Map At A Glance

| Repository | Primary role | Depends on / connects to |
| --- | --- | --- |
| `vllm-hust` | core inference runtime and serving fork | upstream `vllm`, benchmark, workstation, plugin |
| `vllm-ascend-hust` | Ascend hardware plugin | `vllm-hust`, upstream `vllm-ascend` |
| `ascend-runtime-manager` | runtime repair and deployment tooling | `vllm-hust`, `vllm-ascend-hust` |
| `vllm-hust-dev-hub` | multi-repo workspace and bootstrap | all local sibling repos |
| `vllm-hust-benchmark` | benchmark orchestration and export | `vllm-hust`, `vllm-hust-website` |
| `vllm-hust-website` | landing page and leaderboard snapshots | benchmark exports, workstation embeds |
| `vllm-hust-workstation` | user-facing web console | `vllm-hust`, EvoScientist |
| `vllm-hust-docs` | operations, sync notes, internal docs | runtime and plugin repos |
| `EvoScientist` | higher-level research agent product | `vllm-hust` APIs and tools |

### 核心运行时

- [vllm-hust](https://github.com/vLLM-HUST/vllm-hust)
  基于上游 `vLLM` 的主运行时 fork，是整个组织的核心仓库，负责推理引擎、OpenAI 兼容服务、CLI 与主要 CI。

- [vllm-ascend-hust](https://github.com/vLLM-HUST/vllm-ascend-hust)
  `vllm-hust` 的 Ascend 插件与本地化发行仓库，遵循上游硬件插件模式，尽量把硬件相关逻辑隔离在插件层。

- [ascend-runtime-manager](https://github.com/vLLM-HUST/ascend-runtime-manager)
  独立的 Ascend 运行时修复与诊断工具，负责环境探测、容器化部署、依赖修复与 Python 栈对齐。

### 工程与开发体验

- [vllm-hust-dev-hub](https://github.com/vLLM-HUST/vllm-hust-dev-hub)
  多仓开发入口，提供 VS Code workspace、quickstart、clone 脚本与自托管 CI 相关工具。

- [vllm-hust-docs](https://github.com/vLLM-HUST/vllm-hust-docs)
  组织级文档仓库，用于放置部署手册、兼容性说明、上游同步记录和团队操作指南。

### 验证、展示与应用层

- [vllm-hust-benchmark](https://github.com/vLLM-HUST/vllm-hust-benchmark)
  `vllm-hust` benchmark 的稳定包装层，负责场景编排、结果导出和与 Website 的对接。

- [vllm-hust-website](https://github.com/vLLM-HUST/vllm-hust-website)
  官网、Leaderboard 与演示入口，展示组织介绍、版本信息和 Benchmark 结果快照。

- [vllm-hust-workstation](https://github.com/vLLM-HUST/vllm-hust-workstation)
  面向终端用户的 Web 工作站，提供统一推理入口、可视化控制台与 EvoScientist 嵌入能力。

- [EvoScientist](https://github.com/vLLM-HUST/EvoScientist)
  面向科研工作流的智能体应用，可把 `vllm-hust` 作为底层推理与工具调用后端。

## 推荐理解顺序

如果你第一次进入 `vLLM-HUST` 组织，推荐按这个顺序理解：

1. 从 [vllm-hust](https://github.com/vLLM-HUST/vllm-hust) 开始，理解核心运行时与服务接口。
2. 如果你关注 Ascend 或国产硬件，再看 [vllm-ascend-hust](https://github.com/vLLM-HUST/vllm-ascend-hust) 与 [ascend-runtime-manager](https://github.com/vLLM-HUST/ascend-runtime-manager)。
3. 如果你要搭本地开发环境，直接使用 [vllm-hust-dev-hub](https://github.com/vLLM-HUST/vllm-hust-dev-hub)。
4. 如果你要做结果展示或性能验证，再看 [vllm-hust-benchmark](https://github.com/vLLM-HUST/vllm-hust-benchmark) 与 [vllm-hust-website](https://github.com/vLLM-HUST/vllm-hust-website)。
5. 如果你关注最终用户体验或上层应用，再看 [vllm-hust-workstation](https://github.com/vLLM-HUST/vllm-hust-workstation) 与 [EvoScientist](https://github.com/vLLM-HUST/EvoScientist)。

For English-speaking contributors, the same reading order applies:

1. Start with `vllm-hust` for the runtime and serving surface.
2. Move to `vllm-ascend-hust` and `ascend-runtime-manager` for Ascend-specific support.
3. Use `vllm-hust-dev-hub` for the intended multi-repo development workflow.
4. Read `vllm-hust-benchmark` and `vllm-hust-website` for validation and result publication.
5. Finish with `vllm-hust-workstation` and `EvoScientist` for user-facing and research-facing applications.

## 与上游的关系

`vLLM-HUST` 不是从零开始的新推理栈，而是围绕上游项目进行工程化增强：

- 上游运行时参考：`vllm-project/vllm`
- 上游 Ascend 插件参考：`vllm-project/vllm-ascend`
- 相关比较与生态参考：`sgl-project/sglang`

组织内仓库默认优先保持可维护、可同步、可验证，而不是无边界地与上游分叉。

## 开始贡献

- 想要改运行时或服务链路：从 [vllm-hust](https://github.com/vLLM-HUST/vllm-hust) 开始
- 想要改 Ascend 支持：从 [vllm-ascend-hust](https://github.com/vLLM-HUST/vllm-ascend-hust) 和 [ascend-runtime-manager](https://github.com/vLLM-HUST/ascend-runtime-manager) 开始
- 想要快速拉起完整开发环境：使用 [vllm-hust-dev-hub](https://github.com/vLLM-HUST/vllm-hust-dev-hub)
- 想要补文档、操作流程、同步记录：前往 [vllm-hust-docs](https://github.com/vLLM-HUST/vllm-hust-docs)

欢迎通过 issue、pull request 和 benchmark / deployment 反馈一起完善这个组织。

## Community Defaults

This organization also uses this repository for shared community health files:

- default issue templates
- default pull request template
- shared security policy
- shared code of conduct

If a specific repository does not override those files, GitHub will fall back to the defaults provided here.