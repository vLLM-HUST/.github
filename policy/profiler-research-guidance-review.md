# Profiler research-output guidance review

Issue: vLLM-HUST/vllm-hust-benchmark#326.

Organization audit [40072242735](https://github.com/vLLM-HUST/.github/actions/runs/40072242735)
flagged one changed candidate path after
[Profiler #41](https://github.com/vLLM-HUST/vllm-hust-request-lifecycle-profiler/pull/41)
merged as `3861e7caa276d6696b9354c1850a7c8ebf9b3ba3`.

The complete diff of `paper/request_lifecycle_causal_profiler/results/README.md`
was reviewed against previous blob `17c84c37a8d1f80e30911fd7a19a073afd184d5c`.
New blob `740abf5ab17d4cbf880ff3199f9b1ff70fdc090b` removes instructions to
commit raw/intermediate measurements in the MOD. It instead points to canonical
benchmark inputs, identifies template fixtures as non-measurements, and records
that existing tracked paper projections still need separate custody/consumer
migration. It contains no measured results or newly embedded experiment inputs.

Only this reviewed fingerprint changes. No baseline debt entries are removed,
no path/type exemptions or detector changes are introduced, and future byte
changes require review. Profiler's missing per-repository trusted policy caller
and branch protection remain a separate enforcement gap; successful drift audit
does not establish a pre-merge gate. No hardware runner or approval is bypassed.
