# Exact consumer migration review

Issue: vLLM-HUST/vllm-hust-benchmark#326. Originals are merged in benchmark
#467, with per-file SHA256/size verification and remote readback before deletion.

- vSpec #10, `BENCHMARK_ORIGINALS.json`: inspected the parsed complete document
  and change. Only a pinned manifest URL/hash and 316 migrated path strings are
  added. Historical filenames containing latency and batch numbers trigger the
  prose heuristic; these are custody identities, not new measurement payloads.
- KVCompress #26, `docs/results/benchmark-leaderboard.html`: the complete diff
  replaces local executable data bundles with immutable benchmark JSON, rewrites
  evidence links, labels missing raw kernel timing as method-only, and exposes
  fetch errors. No measured values are added or altered. The old page URL stays
  valid. Browser checks remain mandatory in the source PR.

Only the ledger's exact PR, blob and full diff fingerprints are approved. No
path exemption, generic allowlist, runner approval or branch protection change.
Any further modification requires a fresh review. The retained HTML's inventory
fingerprint will be reconciled after its source PR merges, not before.
