# Exact Unified Communication mount-smoke review

Scope: `vLLM-HUST/vllm-hust-unified-comm#8`, reviewed head
`75162dd3ec41d20f8082caf595c1039f1e395127`, base
`4069e64e68bfa332841aa0c9bc5400f716edba20`. The ledger binds the added
`evidence/hccl-mount-smoke-20261107.json` file to its exact Git blob and complete
GitHub diff fingerprint. Any byte change, missing diff, different PR, or
different repository still requires a new review.

The record describes a two-rank HCCL mount smoke on two allocated Ascend 910B2
devices. It identifies the MOD and tested host commits, activation entry point,
host-owned process-group boundary, four collective outcomes, and cleanup state.
The command and result were observed during the project-side run that produced
the PR. This custody review does not turn that same-operator record into an
independent hardware attestation.

The file contains no throughput, latency, memory, or comparative performance
measurement. It explicitly says that no model was loaded, no serving request
was issued, no CUDA/NCCL hardware run was performed, and no live HCCL failure
was injected. The MOD metadata therefore remains `mount-smoke-only` and
`validating`; production qualification is not approved here.

The accompanying implementation keeps installation inert until explicit
activation, delegates to the host-owned communicator, and does not create or
destroy the process group. Source tests, wheel inspection, Extension Manager
enable/disable rollback, direct host-loader delegation, and the focused HCCL
run were completed separately in the target PR. This central entry approves
only the exact evidence-file custody change; it does not exempt future evidence,
weaken the detector, alter the debt baseline, or bypass target-repository CI.
