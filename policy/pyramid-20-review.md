# Exact migration review: PyramidKV PR 20

Codex review under the user's instruction to migrate evidence and consumers,
without weakening gates. This is not independent human approval or new hardware
acceptance. Repository: `vLLM-HUST/vllm-ascend-pyramidkv-hust`, PR 20, reviewed
head `b2eccd07098032d6f0bcdfa7b89414cb09c3dd48`, base
`534bcc043ee3750a7c0caa4278e3690bf0b74b7b`.

The only remaining heuristic finding is `docs/support-matrix.md`. The complete
file diff changes five link destinations to fixed benchmark originals. Visible
wording, tables, version identities, failed qualification, throughput regression,
HBM increase and release-acceptance limitations are unchanged. The added-line
throughput heuristic correctly asks for review; this entry approves only the
exact recorded blob and complete GitHub diff fingerprint, not a path exemption.

Originals were downloaded and every length/SHA256 checked. All 118 former
`evidence/current/` members were also byte-compared with the pre-migration source.
The combined downloader resolves 122 unique files including retained context.
Six remaining original SHA256SUMS files independently validate 68 covered members.
No original report was re-signed after changing a link: the checksum-covered
public-package report and related current collections are preserved unchanged.

- Existing paired capsule (benchmark PR 464):
  <https://github.com/vLLM-HUST/vllm-hust-benchmark/blob/9b81690f767aca56524ec6651535a9b8d484a4c3/archive/mod-git-20261022/pyramidkv-website-source/manifest.json>
- Remaining current capsule (benchmark PR 466, merged as
  `fb5a365d3e45144cd2744942a6f7a1b94ac33141`; immutable reviewed PR head below):
  <https://github.com/vLLM-HUST/vllm-hust-benchmark/blob/93090eda628b9c6038d1d7aa87ee115808e50ced/archive/mod-targeted-20261023/pyramid-current/manifest.json>

Source cleanup and consumer changes have nine local custody/link tests. Package
tests, remote readback and trusted organization checks remain mandatory. Five
legacy records and their semantic tests remain unchanged. No hardware task starts.

Rollout: merge this central ledger after CI, then merge a separate source caller
update under its old trusted policy. Only after that base update is merged may
PR 20 use this review. The caller executes no target PR code. Rules, baseline,
required checks, strict/admin/App protection and unrelated review requirements
are unchanged. A changed file/diff, another repository or PR fails closed.

Checkpoint: custody/consumer migration | fixed originals and full diff |
E04/E31/E37/E43 | retain failures and original checksum chains; no gate bypass.
