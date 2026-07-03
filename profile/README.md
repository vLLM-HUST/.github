<!-- markdownlint-disable MD013 MD033 MD041 -->

# vLLM-HUST

`vLLM-HUST` maintains an upstream-compatible vLLM stack for Ascend/NPU
research, serving experiments, benchmarking, profiling, and HUST-managed
deployment workflows.

`vLLM-HUST` 是围绕上游 vLLM 生态维护的国产算力推理系统组织，重点服务
Ascend/NPU 运行时适配、真实服务实验、benchmark、profiler 分析和 HUST
本地托管部署流程。

The organization is intentionally built around forks that stay close to
upstream instead of drifting into a separate framework. Core runtime changes
belong in `vllm-hust`; Ascend-specific runtime behavior belongs in
`vllm-ascend-hust`.

## Core Repositories

| Repository | Role | Upstream anchor |
| --- | --- | --- |
| [`vllm-hust`](https://github.com/vLLM-HUST/vllm-hust) | Core vLLM fork and OpenAI-compatible serving runtime | `vllm-project/vllm`, anchored by `upstream_version.json` to `0.23.1rc0` |
| [`vllm-ascend-hust`](https://github.com/vLLM-HUST/vllm-ascend-hust) | Ascend/NPU plugin paired with `vllm-hust` | `vllm-project/vllm-ascend`, anchored by `upstream_version.json` to `0.19.1rc1` |
| [`vllm-hust-dev-hub`](https://github.com/vLLM-HUST/vllm-hust-dev-hub) | Multi-repo workspace, managed service scripts, and local NPU smoke-test entrypoint | HUST workflow repo |
| [`vllm-hust-benchmark`](https://github.com/vLLM-HUST/vllm-hust-benchmark) | Benchmark orchestration and result export | HUST validation repo |
| [`vllm-hust-perf-analyzer`](https://github.com/vLLM-HUST/vllm-hust-perf-analyzer) | TraceLoom-style offline profiler timeline analysis | HUST profiling repo |
| [`vllm-hust-website`](https://github.com/vLLM-HUST/vllm-hust-website) | Website, leaderboard snapshots, and public result presentation | HUST website repo |
| [`vllm-hust-workstation`](https://github.com/vLLM-HUST/vllm-hust-workstation) | User-facing web console and application surface | HUST product repo |

## Related Runtime And Tooling

| Repository | Role |
| --- | --- |
| [`vllm-ascend-quant-hust`](https://github.com/vLLM-HUST/vllm-ascend-quant-hust) | Ascend-oriented quantization and compression experiments. |
| [`triton-ascend-hust`](https://github.com/vLLM-HUST/triton-ascend-hust) | Triton Ascend backend and kernel-development work. |
| [`ascend-runtime-manager`](https://github.com/vLLM-HUST/ascend-runtime-manager) | Ascend environment diagnosis, repair, and runtime management. |
| [`claude-code-hust`](https://github.com/vLLM-HUST/claude-code-hust) | AI-assisted development tooling and local adapters. |
| [`vllm-hust-docs`](https://github.com/vLLM-HUST/vllm-hust-docs) | Operational notes, sync records, and team-facing documentation. |
| [`EvoScientist`](https://github.com/vLLM-HUST/EvoScientist) | Research-agent application using the HUST serving stack. |

## Version And Upstream Policy

The two core forks use an upstream-anchored version rule:

```text
<upstream release>.post1.dev<HUST-only commit count>+g<short sha>
```

Each core repository keeps an `upstream_version.json` file containing:

- `upstream_commit`: exact upstream commit included in the fork graph.
- `upstream_version`: upstream-compatible version, including rc suffix when
  present.
- `release_version`: the release line without the rc suffix.

After an upstream sync lands, the target state is:

```bash
git rev-list --left-right --count origin/main...upstream/main
# <HUST-only commits>  0
```

That is: the fork may be ahead by HUST-specific commits, but it should not
remain behind upstream after a completed sync PR.

## Recommended Reading Order

1. Start with [`vllm-hust`](https://github.com/vLLM-HUST/vllm-hust) to
   understand the core runtime and serving surface.
2. Read [`vllm-ascend-hust`](https://github.com/vLLM-HUST/vllm-ascend-hust) for
   Ascend/NPU plugin behavior.
3. Use [`vllm-hust-dev-hub`](https://github.com/vLLM-HUST/vllm-hust-dev-hub) to
   launch the intended multi-repo local workflow.
4. Use [`vllm-hust-benchmark`](https://github.com/vLLM-HUST/vllm-hust-benchmark)
   and [`vllm-hust-perf-analyzer`](https://github.com/vLLM-HUST/vllm-hust-perf-analyzer)
   for validation and profiling.
5. Look at [`vllm-hust-website`](https://github.com/vLLM-HUST/vllm-hust-website),
   [`vllm-hust-workstation`](https://github.com/vLLM-HUST/vllm-hust-workstation),
   and [`EvoScientist`](https://github.com/vLLM-HUST/EvoScientist) for
   public-facing and application-facing work.

## Local NPU Testing

For production-like NPU smoke tests, use `manage.sh` from the dev-hub
repository:

```bash
cd /path/to/vllm-hust-dev-hub
./manage.sh status
./manage.sh restart
./manage.sh health --json
```

On shared HUST machines, use only the allocated device. The current default
smoke workflow is constrained to NPU 1 unless the operator explicitly assigns
another device.

## How We Contribute

- Keep upstream merges real whenever possible; avoid long-lived
  cherry-pick-only sync stacks.
- Keep hardware-specific behavior in plugin/runtime-manager layers when it does
  not belong in core vLLM.
- Prefer small, reviewable HUST deltas that can be explained and tested.
- Run syntax checks, targeted tests, and managed NPU smoke tests before
  promoting runtime changes.
- Document version anchors, benchmark assumptions, and operational constraints
  in the relevant repository.

## Community Defaults

This `.github` repository also provides organization-level community defaults:

- issue templates
- pull request templates
- security and contribution notes
- organization profile content

Repository-specific files take precedence when a project needs stricter local
rules.
