# Split-Batch v0.2.0 installation asset review

Reviewed 2026-10-24 for [benchmark #326](https://github.com/vLLM-HUST/vllm-hust-benchmark/issues/326).
Scope: three new installation assets, not a refresh of all migration debt.

## Identity and byte verification

[Release v0.2.0](https://github.com/vLLM-HUST/vllm-ascend-split-batch-hust/releases/tag/v0.2.0)
was published at 2026-10-24T03:07:31Z. Annotated tag object
`77a2d6c3139c2d865f7debfd193aba481c7290a9` resolves to source
`2ce803283f985f578ad4a7c2d45f6f0f5865f1f9`. The tag is unsigned;
this is content verification, not a signature or hardware qualification.

| Asset ID | Name | Bytes | SHA256 |
| --- | --- | ---: | --- |
| 671115563 | vllm_ascend_split_batch-0.2.0-py3-none-any.whl | 136281 | 578ddf07f932524f4b0a3324e21f677545506a5afabb9e5d02152c063aca28e7 |
| 671115564 | dist.sha256 | 216 | fcbb282645dab8d5cb2a391e6b6125615223386de7fd66488c894a34c7e7aef0 |
| 671115566 | vllm_ascend_split_batch-0.2.0.tar.gz | 108898 | fa30f16cc856afaca81c6deef82d6e357ef3c8f1933a8d243a19d5e7dde4274b |

Downloaded each GitHub asset through its asset API; size and SHA256 match the
GitHub digest. Both lines of `dist.sha256` match. Downloaded both artifacts from
the URLs returned by [PyPI version metadata](https://pypi.org/pypi/vllm-ascend-split-batch/0.2.0/json):
their bytes equal the GitHub attachments. No rebuild substituted for published bytes.

Read-only ZIP/tar inspection found 54 wheel and 55 sdist members, unique names,
no absolute/traversal paths and only regular tar members. All populated wheel
RECORD hashes and lengths verify. Every wheel runtime member equals the sdist
`src/` counterpart and its Git blob at the peeled tag. No result/log directory
or standalone CSV/JSONL/log evidence payload is included. Six JSON members are
extension manifests, not measurement results. The sdist additionally carries
README, provenance, license, build metadata and `.gitignore`; the wheel carries
license and dist-info metadata. The release's
[distribution guard](https://github.com/vLLM-HUST/vllm-ascend-split-batch-hust/blob/2ce803283f985f578ad4a7c2d45f6f0f5865f1f9/tools/check_distribution.py)
checks evidence paths, matching source inventories and manifest presence.
Path heuristics alone are not a semantic proof.

## Installation consumers and disposition

- `pip install vllm-ascend-split-batch` in the repository README consumes PyPI;
  the Release attachments are the same install/build artifacts, with the checksum
  file as their integrity companion. Retain all three, not evidence duplicates.
- [Publish workflow](https://github.com/vLLM-HUST/vllm-ascend-split-batch-hust/blob/2ce803283f985f578ad4a7c2d45f6f0f5865f1f9/.github/workflows/publish.yml)
  builds and gates the distributions before OIDC publication; the
  [Release workflow](https://github.com/vLLM-HUST/vllm-ascend-split-batch-hust/blob/2ce803283f985f578ad4a7c2d45f6f0f5865f1f9/.github/workflows/release.yml)
  downloads PyPI bytes, verifies hashes, runs the distribution guard and uploads
  them with `dist.sha256`. Existing-asset replacement is possible in that workflow;
  a changed asset ID or fingerprint still requires a new central review.
- Wheel metadata exposes 9 `vllm.general_plugins` and 6
  `vllm_hust.extension_bundles`. Manager's
  [metadata discovery consumer](https://github.com/vLLM-HUST/extension-manager/blob/be30e724ea4b8fdae7449ea716bb7aee2666f8bd/src/vllm_hust_ext/discovery.py)
  reads that bundle group and packaged manifests without importing implementations.
  Static consumer compatibility does not prove a live deployment loaded them.
- Package version is 0.2.0, Python >=3.10, no runtime dependency, only `test`
  extra. All six manifests use host range `>=0.25.1rc2.dev125,<0.25.2`.
  Split-batch planner, rope-fix and gdn-merge-inproj are `import_only`;
  fia-demask, gate-fp32 and zerocost-wiring are `active` descriptors with explicit
  activation environment gates. There is no cascade entry point or kernels extra.
  Descriptor presence is not execution or performance qualification.
- [Current release receipt](https://github.com/vLLM-HUST/vllm-ascend-split-batch-hust/blob/185f48f3ac845833beb41bf2b8d34f7f82388128/docs/release.md)
  documents wheel reinstall, process restart and graph recapture. Existing
  installed entry-point metadata and live wrappers are consumers too; deleting
  Release files would not retire them. This review did not install/import the
  package, restart services or run NPU tests.

Published tag workflows independently succeeded:
[Publish](https://github.com/vLLM-HUST/vllm-ascend-split-batch-hust/actions/runs/40056940941),
[Release](https://github.com/vLLM-HUST/vllm-ascend-split-batch-hust/actions/runs/40056940984),
[Extension CI](https://github.com/vLLM-HUST/vllm-ascend-split-batch-hust/actions/runs/40056882910),
[custody](https://github.com/vLLM-HUST/vllm-ascend-split-batch-hust/actions/runs/40056882896).
Their CPU/package scope does not clear host-tree or hardware gates.

## Historical prose and remaining boundaries

The packaged README still says 0.2.0 is not yet on the index and describes a
single-build host pin; actual PyPI presence and the manifest range above supersede
those stale statements. Cascade prose is historical despite source removal.
README timing/correctness observations already point to fixed benchmark snapshots;
it still contains historical cohort descriptions and qualitative claims.
PROVENANCE retains attribution/hash history, a historical `191 PASS / 0 FAIL`
summary and legacy relative references (including unshipped documentation).
These are not newly produced raw measurements or current acceptance evidence.
Do not promise that every relative link resolves inside an installed distribution.
Future source-document cleanup remains separate; published bytes are not rewritten.

Only asset IDs 671115563/671115564/671115566 are added to the baseline, with exact
name, size, digest, tag, draft and prerelease fields. No path, heuristic, reviewed-PR
exemption, old asset or branch protection changes. Regression coverage checks every
fingerprint field, a replacement ID and a new measured-data path still fail drift.
Other 27 assets remain unchanged and retained without proof of zero consumers.
Search/index visibility cannot establish absence of external installers.

Work-record check: installation review | user requests exact v0.2.0 asset/consumer
review then CI-green baseline merge | published bytes, tag tree, PyPI and pinned
consumer sources above | E04/E31/E34/E37/E42/E47 | no deletion, hardware claim,
blanket baseline refresh or unauthorized storage; update #326 body and receipt.
