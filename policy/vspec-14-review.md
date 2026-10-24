# Exact adaptive evidence navigation review

Scope: vLLM-HUST/vllm-hust-vSpec#14, continuing benchmark#326.

The full change is navigation and custody metadata, not new measurements. The
complete historical reports and LICENSE are already merged at benchmark
`5eeccc2d69b2c4a634e273a9f926584c8d252cf7`, capsule
`archive/mod-targeted-20261023/vspec-adaptive-narratives`. All original bytes
were downloaded and compared with the source Git and worktree before editing.

- `BENCHMARK_ORIGINALS.json`: parsed both old and new complete documents. The
  source identity, all existing capsules, migrated paths and earlier document
  bindings remain unchanged. Additions are one pinned manifest/hash, two frozen
  report URL/hash bindings and two lists of raw path/URL/hash bindings. No metric
  payload is added. Existing raw capsules are reused, not duplicated.
- `docs/vspec_adaptive_npu_report_20260902.md`: the complete diff replaces
  numerical tables and historical narrative with the frozen original and 17
  fixed JSON targets. Quality differences, failures, diagnostic scope and missing
  checkpoint limits remain in the linked original. Legacy filenames containing
  latency and digits trigger the unchanged heuristic; those lines are source
  identities, not new results. All new direct targets across this PR (23 distinct
  JSON/log files) were downloaded and their SHA256 matched the custody bindings.

The exact PR/file/blob/full-diff fingerprints in the central ledger alone are
approved. Source CI still checks downloads, SHA, documents and packaging. No
path exemption, changed baseline, hardware qualification, runner approval or
branch-protection change. Further diffs require fresh review. Merge this central
record first, then update the caller pin in a separate base-branch PR, then
rerun the trusted check for #14; #14 cannot authorize its own policy.
