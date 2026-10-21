# Benchmark-only evidence policy

Datasets, measured results, request logs, timings and experimental Release assets
belong in `vLLM-HUST/vllm-hust-benchmark`. Other repositories retain implementation,
method descriptions and immutable source references. Software installation
packages are not experimental evidence and must not be deleted as duplicates.

The public audit inventories only public, non-archived repositories (except the
benchmark source), detects changed/new candidate paths and Release assets, and
fails closed on API errors or incomplete trees. Truncated recursive trees are
walked non-recursively. The baseline records existing **migration debt**, not
approval of those files, and must only change through reviewed PRs. Baseline
removals do not fail the drift check. New software assets also require review
before refreshing their baseline fingerprints.

The reusable PR check runs only trusted central policy, never PR code. Consumers
must invoke it from `pull_request_target` and require its check via branch
protection. It checks renamed source paths and complete paginated file counts;
removal-only migration passes. Synthetic fixtures have no blanket exemption:
review and narrow policy changes are needed if a legitimate fixture is flagged.

Path and added-line heuristics are not a semantic proof: arbitrary filenames,
embedded measurements, binary packages and subtle prose still need human review.
The central drift audit detects after publication and is NOT an organization-wide
merge gate. Private repository metadata must remain inside its original access
boundary; private repositories use their own PR checks and protected branches,
not a public path inventory. Unknown visibility is excluded, not assumed public.
Per-repository callers and required checks must be inventoried before
claiming enforcement. The organization ruleset API currently requires GitHub Team
(403 on 2026-10-21); no protection is bypassed to compensate.
