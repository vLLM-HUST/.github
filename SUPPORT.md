# Support

This repository provides the default support guidance for the `vLLM-HUST` GitHub organization.

If a specific repository does not define its own `SUPPORT.md`, maintainers and contributors can use the guidance below.

## Where To Ask For Help

Use the repository that is closest to the problem you are trying to solve:

- `vllm-hust`: core runtime, serving, CLI, CI, and inference behavior
- `vllm-ascend-hust`: Ascend plugin behavior and hardware-specific runtime issues
- `ascend-runtime-manager`: environment repair, container workflow, runtime diagnosis, and setup tooling
- `vllm-hust-dev-hub`: workspace bootstrap, quickstart, multi-repo workflow, and self-hosted CI setup
- `vllm-hust-benchmark`: benchmark orchestration, export format, and leaderboard artifact generation
- `vllm-hust-website`: organization site, leaderboard snapshots, and website publication flow
- `vllm-hust-workstation`: end-user workstation UI and application-facing integration issues
- `vllm-hust-docs`: operation guides, sync notes, and documentation gaps
- `EvoScientist`: research-agent application behavior and upper-layer workflows

## Before Opening An Issue

Please do the following first:

1. Search existing issues in the target repository.
2. Reduce the problem to the smallest reproducible command, request, or config.
3. Remove secrets, tokens, private hostnames, and internal paths from logs.
4. State the exact repository, branch or version, hardware, and environment involved.

## What Maintainers Need

Good reports usually include:

- the affected repository
- exact commands or API requests
- sanitized logs or traceback
- model name, backend, hardware, and deployment mode
- whether the issue is a regression and what commit or release range may be involved

## Security Issues

Do not file public issues for vulnerabilities, exposed credentials, or sensitive incident reports.

Use the process in [SECURITY.md](SECURITY.md) instead.

## Upstream Vs Fork Scope

Some issues belong upstream rather than in `vLLM-HUST`.

When the bug is reproducible in upstream `vllm` or upstream `vllm-ascend` without fork-specific changes, it is often better to report it upstream and link that discussion back to the relevant `vLLM-HUST` repository.