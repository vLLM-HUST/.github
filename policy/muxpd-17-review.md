# Exact migration review: MuxPD PR 17

Reviewed by Codex under the user's explicit instruction to complete the trusted
review without weakening gates. This is a recorded code/data-custody review,
not an assertion of independent human approval or hardware acceptance.

Scope: `vLLM-HUST/vllm-ascend-MuxPD-hust#17`, reviewed head
`c9b09a1baf17543792d5e31fbbd7366f768b663a`, base
`935ce04ab2b52e8b7f8bc43b53cc74475bc19f60`. The ledger binds each reviewed
file's Git blob and complete GitHub diff metadata, including source rename path,
status and line counts. Unrelated changes, another PR/repository, missing diffs,
or a changed reviewed file remain rejected. No labels or PR-provided approvals
are consulted. The reviewed file may survive an unrelated base synchronization
only if its exact fingerprint is unchanged.

## Evidence and decisions

Original source bytes are preserved by the merged benchmark manifest:
<https://github.com/vLLM-HUST/vllm-hust-benchmark/blob/812ef01ae992475d4ce6a3bb6a6ce4bda43b5f12/archive/mod-collections-20261023/muxpd/manifest.json>.
The capsule has been downloaded and every member size/SHA256 verified. It binds
the original MuxPD source commit; source Git history is not rewritten.

- `scripts/archive_tp4_evidence.py` is implementation, moved from
  `evidence/2026-10-11-tp4-goodput/archive_tp4_evidence.py`. The entire file was
  compared with the verified archived original: the only change is default
  repository discovery from `parents[2]` to `parents[1]`, required by the move.
  No embedded measured record was added, no verification assertion removed.
- `scripts/archive_tp8_evidence.py` is implementation, moved from
  `evidence/2026-10-11-tp8-contention/archive_evidence.py`. Entire-file comparison
  shows only `REPO = BASE.parents[1]` becoming `REPO = BASE.parent`. Hash,
  traversal, symlink, extra-member, rank completeness and deterministic gzip
  validation are unchanged. The existing synthetic self-tests are code fixtures,
  not measured results. This review does not grant a generic fixture exemption.
- `docs/performance-tp8-contention.md` changes links to immutable benchmark
  manifests and names the original member paths. Historical metric tables,
  observations, failed/excluded trials and limitations are unchanged. Two inline
  figures become archive links. Current verification/unpack commands use the
  maintained script and explicit external input. Commands executing downloaded
  archived Python are removed, with historical replay distinguished from this
  migration. The added-line metric heuristic matches the preserved TTFT figure
  label followed by a dated member path; this is not a new performance claim.

Existing CPU and custody checks remain mandatory. TP8 self-tests cover corruption,
extra files, traversal, symlinks, missing ranks, private fields, source mutation,
and destination isolation. Original negative results and unavailable private
source verification are not relabelled as passing. No hardware test is started.

## Trust boundary and rollout

The ledger and evaluator must first pass CI and merge in the central policy repo.
MuxPD's caller then pins that merged commit via a separate base-branch PR under
the old policy. Only after that base change is merged is PR 17 reevaluated.
The check executes no target PR code and cannot read a target PR's own ledger.
`DATA_PARTS`, `DATA_SUFFIXES`, `MEASURED`, complete-list validation, removal
semantics, branch protection and the organization debt baseline are unchanged.

Review checkpoint: requested exact trusted review | archived originals and
three-file diff | E04/E37/E43 | retain failures, no broad allowlist, no bypass.
