# Exact Unified Communication model-serving smoke review

Scope: `vLLM-HUST/vllm-hust-unified-comm#10`, reviewed head
`d77ce89ffc3311ef09482530e405da14c713ce10`, base
`5dd61585910d3109b258cf25f846adf4ba337c5b`. The ledger binds
`evidence/model-serving-smoke-20261107.json` to its exact Git blob and complete
GitHub diff fingerprint. Any byte change, missing diff, different PR, or
different repository requires a new review.

The record describes a same-operator correctness smoke on two Ascend 910B2
devices. Both HCCL workers logged the independent provider for `tp:0`, loaded
Qwen3-0.6B with tensor parallel size 2, and completed Chat Completions and
Completions requests with HTTP 200 and non-empty generated tokens. The command,
process logs, API responses, and zero-process post-run NPU state were observed
during the project-side run that produced the PR. This review does not turn that
record into an independent hardware attestation.

The evidence preserves negative findings rather than hiding them. It records a
newer host/adapter source incompatibility before provider initialization, the
lazy host compatibility fix in `vllm-hust#75`, one forced worker cleanup, and
resource-tracker warnings associated with the existing shutdown issue. The final
process and NPU inventories were empty.

The file explicitly excludes throughput, latency, goodput, memory-efficiency,
native-path comparison, CUDA/NCCL, and injected HCCL failure qualification.
Metadata advances only from `mount-smoke-only` to `model-serving-smoke`; the MOD
remains `validating`. No performance or production-support claim is approved.

This central entry approves only the exact evidence-file custody change. It does
not exempt future evidence, change the detector or debt baseline, waive target
CI, approve the host fix, or close remaining compatibility and shutdown work.
