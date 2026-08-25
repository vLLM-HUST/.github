# vLLM-HUST

vLLM-HUST 面向国产算力维护 vLLM 推理运行时、Ascend 适配和配套工程工具。研究项目以成果仓库的形式保存核心实现、论文、实验和运行时插件。

vLLM-HUST maintains an upstream-compatible vLLM stack for domestic hardware, together with research artifacts, runtime plugins, benchmarks, and developer tooling.

| 快速入口 | 仓库 |
| --- | --- |
| 推理运行时 | [vllm-hust](https://github.com/vLLM-HUST/vllm-hust) · [vllm-ascend-hust](https://github.com/vLLM-HUST/vllm-ascend-hust) |
| 插件生态 | [插件目录与路线图](https://vllm-hust.sage.org.ai/plugins.html) |
| 编译与模型工具 | [triton-ascend-hust](https://github.com/vLLM-HUST/triton-ascend-hust) · [vllm-ascend-quant-hust](https://github.com/vLLM-HUST/vllm-ascend-quant-hust) |
| 成果仓库 | [BidKV](https://github.com/vLLM-HUST/vllm-ascend-hust-bidkv) · [DiffSpec](https://github.com/vLLM-HUST/vllm-ascend-hust-diffspec) |
| 开发与验证 | [Dev Hub](https://github.com/vLLM-HUST/vllm-hust-dev-hub) · [Benchmark](https://github.com/vLLM-HUST/vllm-hust-benchmark) · [Performance Analyzer](https://github.com/vLLM-HUST/vllm-hust-perf-analyzer) |
| 文档与展示 | [Docs](https://github.com/vLLM-HUST/vllm-hust-docs) · [Website](https://github.com/vLLM-HUST/vllm-hust-website) · [Workstation](https://github.com/vLLM-HUST/vllm-hust-workstation) |

## 生态边界 / Ecosystem Boundary

[SAGE](https://github.com/RIDE-Lab/SAGE)（Streaming-Augmented Generative Execution）是 IntelliStream 研究生态的共同旗舰产品，以流计算思维赋能大模型推理与智能体执行。[RIDE Lab](https://github.com/RIDE-Lab) 负责其核心仓库的主要维护，[Sage Mate](https://github.com/RIDE-Lab/sage-mate) 是基于 SAGE 构建的应用。这些调用方使用 vLLM-HUST 完成模型执行。

[SAGE](https://github.com/RIDE-Lab/SAGE) — Streaming-Augmented Generative Execution — is the IntelliStream research ecosystem's shared flagship product, applying streaming-computing principles to LLM inference and agent execution. [RIDE Lab](https://github.com/RIDE-Lab) is the principal steward of its core repositories, while [Sage Mate](https://github.com/RIDE-Lab/sage-mate) is an application built with SAGE. These caller-side systems use vLLM-HUST for model execution.

vLLM-HUST 是独立的推理底座，拥有模型执行、KV-cache、解码调度、编译、算子与硬件后端；RIDE Lab 和 SAGE 不是 vLLM-HUST 内部的运行时层。

## 成果仓库 / Research Outcomes

每个成果仓库对应一项可独立使用的研究成果，集中维护核心实现、论文、实验和运行时集成。

| Repository | Core technique | Publication | Team | Runtime integration |
| --- | --- | --- | --- | --- |
| [BidKV](https://github.com/vLLM-HUST/vllm-ascend-hust-bidkv) | Utility-guided KV-cache victim selection | *BidKV: Utility-Guided Preemption Scheduling for KV-Pressure LLM Serving*, SC 2026 | 主要作者：陈彦博、王明琪<br>指导老师：张书豪 | `vllm-hust` · `vllm-ascend-hust` · `vLLM / SGLang adapters` |
| [DiffSpec](https://github.com/vLLM-HUST/vllm-ascend-hust-diffspec) | Differential speculative decoding | *DiffSpec: Accelerating Long Sequence Generation with Differential Speculative Decoding* | 主要作者：杜忠承<br>指导老师：黄禹 | `vllm-hust` · `vllm-ascend-hust` · `vLLM adapters` |

## 仓库索引 / Repository Index

| 类别 | 仓库 | 用途 |
| --- | --- | --- |
| 核心运行时 | [vllm-hust](https://github.com/vLLM-HUST/vllm-hust) · [vllm-ascend-hust](https://github.com/vLLM-HUST/vllm-ascend-hust) | vLLM 服务与 Ascend 硬件插件 |
| 编译与算子基础设施 | [triton-ascend-hust](https://github.com/vLLM-HUST/triton-ascend-hust) | Triton Ascend 编译后端；为运行时插件提供基础设施，但本身不是插件 |
| 成果仓库 | [vllm-ascend-hust-bidkv](https://github.com/vLLM-HUST/vllm-ascend-hust-bidkv) | 核心技术、论文、实验与运行时插件 |
| 成果仓库 | [vllm-ascend-hust-diffspec](https://github.com/vLLM-HUST/vllm-ascend-hust-diffspec) | 核心技术、论文、实验与运行时集成 |
| Ascend 工具 | [vllm-ascend-quant-hust](https://github.com/vLLM-HUST/vllm-ascend-quant-hust) · [ascend-runtime-manager](https://github.com/vLLM-HUST/ascend-runtime-manager) | 模型量化准备、环境诊断与运行时维护；不作为 vLLM 运行时插件展示 |
| 开发与验证 | [vllm-hust-dev-hub](https://github.com/vLLM-HUST/vllm-hust-dev-hub) · [vllm-hust-benchmark](https://github.com/vLLM-HUST/vllm-hust-benchmark) · [vllm-hust-perf-analyzer](https://github.com/vLLM-HUST/vllm-hust-perf-analyzer) · [claude-code-hust](https://github.com/vLLM-HUST/claude-code-hust) | 多仓工作区、Benchmark、Profiler 分析与开发工具 |
| 产品与应用 | [vllm-hust-website](https://github.com/vLLM-HUST/vllm-hust-website) · [vllm-hust-workstation](https://github.com/vLLM-HUST/vllm-hust-workstation) · [EvoScientist](https://github.com/vLLM-HUST/EvoScientist) | 官网、Web 工作台与科研智能体应用 |
| 文档与社区 | [vllm-hust-docs](https://github.com/vLLM-HUST/vllm-hust-docs) · [.github](https://github.com/vLLM-HUST/.github) · [vllm-hust.github.io](https://github.com/vLLM-HUST/vllm-hust.github.io) | 文档、组织级社区配置与 Pages 入口 |
| 论文与活动 | [CCCF 综述](https://github.com/vLLM-HUST/cccf-domestic-inference-engine-survey) · `fcs-domestic-chip-llm-recsys`（链接未公开） · [StateSys 2026](https://github.com/vLLM-HUST/statesys-2026) | 论文仓库与学术活动 |

## Fork Status

核心 fork 持续跟踪上游；精确基线以各仓库的 `upstream_version.json` 为准。

| Repository | Upstream |
| --- | --- |
| `vllm-hust` | `vllm-project/vllm` |
| `vllm-ascend-hust` | `vllm-project/vllm-ascend` |
| `triton-ascend-hust` | `triton-lang/triton-ascend` |
| `EvoScientist` | `EvoScientist/EvoScientist` |

## Publications

| Paper | Venue | Repository |
| --- | --- | --- |
| BidKV: Utility-Guided Preemption Scheduling for KV-Pressure LLM Serving | SC 2026 | [BidKV](https://github.com/vLLM-HUST/vllm-ascend-hust-bidkv) |
| DiffSpec: Accelerating Long Sequence Generation with Differential Speculative Decoding | SC 2026 | [DiffSpec](https://github.com/vLLM-HUST/vllm-ascend-hust-diffspec) |
| 国产算力推理引擎综述 | CCCF 通讯专刊 | [cccf-domestic-inference-engine-survey](https://github.com/vLLM-HUST/cccf-domestic-inference-engine-survey) |
| LLM-Powered Recommendation Systems on Domestic AI Chips | Frontiers of Computer Science | `fcs-domestic-chip-llm-recsys`（链接未公开） |

## 贡献者

贡献者名单、身份合并规则与统计方法见 [CONTRIBUTORS.md](../CONTRIBUTORS.md)。

## Contributing

- 运行时与服务： [vllm-hust](https://github.com/vLLM-HUST/vllm-hust)
- Ascend 支持： [vllm-ascend-hust](https://github.com/vLLM-HUST/vllm-ascend-hust)
- 研究成果与复现： [BidKV](https://github.com/vLLM-HUST/vllm-ascend-hust-bidkv) · [DiffSpec](https://github.com/vLLM-HUST/vllm-ascend-hust-diffspec)
- 开发环境与文档： [vllm-hust-dev-hub](https://github.com/vLLM-HUST/vllm-hust-dev-hub) · [vllm-hust-docs](https://github.com/vLLM-HUST/vllm-hust-docs)
