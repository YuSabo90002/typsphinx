---
phase: "77"
slug: "v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-28"
---

# Phase 77 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
> Register authored at plan time (8 PLAN `<threat_model>` blocks); no `## Threat Flags` in any SUMMARY.
> ASVS L1, `block_on: high` — grep-depth verification against phase evidence files and the live tree at `4b39d7aa`.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `.planning/REQUIREMENTS.md` → phase-completion tooling | automation writes to a file this phase must hold line-stable | requirement checkbox state (integrity) |
| local measurement → published claim | warning counts / linkcheck sets become SC#3's comparison basis | build logs (integrity) |
| repository state → remote publish surfaces | tag, PyPI, Release and secret probes prove nothing irreversible happened | remote state readings (integrity) |
| `CHANGELOG.md` → docs / GitHub Release body | changelog is published prose and the Release body via the extractor | public release notes |
| `pyproject.toml` → `uv.lock` → installed distribution | lock must stay resolver-derivable | dependency pins (supply chain) |
| handoff text → operator shell / later `/gsd-complete-milestone` session | irreversible steps executed from `77-HANDOFF.md` alone | commands touching tag, PyPI, secrets |
| step order → secret lifecycle | ATT-05 retires the only rollback credential | `PYPI_API_TOKEN` (secret, names only) |
| local branch → `origin` / dispatch → GitHub Actions | first remote write; CI verdict gates merge readiness | branch push, CI run |
| `origin/main` → release pull request | merge under `strict` protection | merged tree |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-77-01 | Tampering | REQUIREMENTS.md fenced checkboxes | high | mitigate | full + guarded-region SHA-256 in `77-CLOSEOUT-GUARD.md` (`REQ_SHA256_BASE/CLOSE`, `REQ_SHA256_GUARDED_*`); re-derived in `77-VERIFICATION.md` | closed |
| T-77-02 | Repudiation | empty tag/PyPI/Release probes | medium | mitigate | `v0.9.6` positive controls in `77-PREFLIGHT-EVIDENCE.md` / `77-SC5-INVARIANTS.md` (`RELEASE_POSITIVE_CONTROL = 35730551619`) | closed |
| T-77-03 | Information Disclosure | secret values in evidence | high | mitigate | all 9 `gh secret list` calls across evidence/handoff carry `--json name`; no `gh auth token`; token-pattern scan clean | closed |
| T-77-04 | Denial of Service | incremental/localised docs baseline | medium | mitigate | `rm -rf docs/_build` + `LC_ALL=C` recorded in `77-GREEN-TREE-EVIDENCE.md` / preflight | closed |
| T-77-05 | Tampering | ROADMAP.md / STATE.md mangling | medium | mitigate | `77-CLOSEOUT-GUARD.md` § "Scratch backups" captures both; operator section in handoff | closed |
| T-77-06 | Spoofing | `### Changed` overclaiming PEP 740 | high | mitigate | `CHANGELOG.md` `[0.9.7]` contains `audit provenance`, `install-time gate`, `` `uv` ``, `` `pip` `` | closed |
| T-77-07 | Repudiation | `### Verified` invariance claims | high | mitigate | keyed in `77-CHANGELOG-EVIDENCE.md` (`UV_LOCK_PACKAGE_SET_UNCHANGED`, `PREVIEW_SITES_UNCHANGED_SINCE_V096`, MSG-06 gate) | closed |
| T-77-08 | Repudiation | NUM-01 dropped from newest section | medium | mitigate | NUM-01 present in both `[0.9.7]` and `[0.9.6]`; anchored heading count = 3 | closed |
| T-77-09 | Tampering | hand-edited `uv.lock` | medium | mitigate | `uv lock --check` passes at HEAD; bump commit `39cb79f9` changes one lock line | closed |
| T-77-10 | Information Disclosure | scratch "Planned for Future Releases" leaking into Release body | medium | mitigate | `scripts/extract_changelog_section.py 0.9.7` stdout: 0 scratch headings, 0 `## [` lines (re-run live) | closed |
| T-77-11 | Denial of Service | version bump landing alone | high | mitigate | `39cb79f9 chore(release): prepare 0.9.7` carries exactly the five-file union | closed |
| T-77-12 | Elevation of Privilege | rollback reintroducing long-lived token by default | high | mitigate | handoff R4 is last, owner-gated, after R1/R2/R3 (section order verified) | closed |
| T-77-13 | Tampering | re-tagged 0.9.7 after failure | high | mitigate | handoff R2 (D-02) routes non-re-run failures to 0.9.8; "What never happens" restates | closed |
| T-77-14 | Repudiation | ATT-05/DOC-25 executed while provenance unproven | high | mitigate | R3 forbids both on shape 3; Step 7 gated on Steps 5+6 PASS | closed |
| T-77-15 | Information Disclosure | secret values printed while listing scopes | high | mitigate | same as T-77-03 — every `gh secret list` uses `--json name` | closed |
| T-77-16 | Elevation of Privilege | handoff command via command substitution | medium | mitigate | 0 `$(` occurrences in `77-HANDOFF.md`; commands use `/tmp/p77close/` files | closed |
| T-77-17 | Repudiation | control reading on wrong run/attempt/file | medium | mitigate | `77-CONTROLS-EVIDENCE.md` names run id, `--attempt 1`, exact filename | closed |
| T-77-18 | Repudiation | linkcheck classification absorbing a real broken link | high | mitigate | `77-GREEN-TREE-EVIDENCE.md`: exactly two pre-tag 404 URIs (`compare/v0.9.7...HEAD`, `releases/tag/v0.9.7`) with delta recorded | closed |
| T-77-19 | Tampering | red gate turned green by editing product/test/docs | high | mitigate | phase-range diff over `docs/source typsphinx tests .github` = only `tests/test_changelog_page_gate.py` (bump-commit version literal) | closed |
| T-77-20 | Denial of Service | incremental docs build false comparison | medium | mitigate | clean `docs/_build` removal + `LC_ALL=C` recorded (as T-77-04) | closed |
| T-77-21 | Repudiation | pytest count from another interpreter | medium | mitigate | interpreter recorded beside counts in `77-GREEN-TREE-EVIDENCE.md` | closed |
| T-77-22 | Tampering | real merge/rebase while checking | high | mitigate | only `git merge-tree --write-tree` (`MERGE_TREE_EXIT = 0`); no merge/trial branches locally or on `origin` | closed |
| T-77-23 | Repudiation | trial merge clean only in this worktree | medium | mitigate | merged tree checked in scratch with its own locked env + ruff (`77-BASE-EVIDENCE.md`) | closed |
| T-77-24 | Spoofing | stale protection/merge-method readings | medium | mitigate | live `gh api …/required_status_checks` → `PROTECTION_STRICT = true` vs `REQUIRED_STRICT_CLOSE_75` | closed |
| T-77-25 | Tampering | force-push / decoy out of order | high | mitigate | `ORIGIN_BEFORE` measured; plain `git push --no-follow-tags`; no decoy branch on origin | closed |
| T-77-26 | Repudiation | two CI runs | high | mitigate | `DISPATCH_ATTEMPTED = yes` before dispatch; single `RUN_ID = 36430787178` | closed |
| T-77-27 | Tampering | irreversible action beside push | critical | mitigate | `--no-follow-tags`; `RELEASE_RUNS_AT_PUSHED = 0`; `v0.9.7` absent locally and on `origin` (re-probed live) | closed |
| T-77-28 | Repudiation | green status while a job failed | high | mitigate | per-job conclusions transcribed; job set compared to `REFERENCE_RUN_ID = 36320335404` | closed |
| T-77-29 | Information Disclosure | job log transcribed wholesale | medium | mitigate | `77-CI-EVIDENCE.md` quotes only named step lines; no token/env dump present | closed |
| T-77-30 | Elevation of Privilege | ATT-05 before ATT-03 passes | critical | mitigate | Step 7 "Ordering: strictly after Steps 5 and 6 have both recorded PASS; never on shape 3" | closed |
| T-77-31 | Repudiation | step skipped due to un-opened dependency file | high | mitigate | values inlined in `77-HANDOFF.md` (fence protocol reproduced in § "Before and after phase.complete-family tooling") | closed |
| T-77-32 | Spoofing | provenance check passing on wrong shape | high | mitigate | Steps 5–6 use `tostring` non-null checks; no `== true/false` boolean comparisons | closed |
| T-77-33 | Repudiation | ATT-04 vacuous zero on title phrase | high | mitigate | Step 4 two-grep pair + live non-zero control (`Generating and uploading digital attestations`) | closed |
| T-77-34 | Elevation of Privilege | command substitution in handoff | medium | mitigate | 0 `$(` in `77-HANDOFF.md` | closed |
| T-77-35 | Tampering | ATT-06 rollback section edited post-commit | medium | mitigate | section digest re-computed at HEAD = `ROLLBACK_SECTION_SHA256` `4406fb65…192b` | closed |
| T-77-36 | Tampering | checkbox flipped by tooling after close | high | mitigate | close MATCH on both digests + third-observation recipe in guard and handoff | closed |
| T-77-37 | Repudiation | scope fence passing on empty pathspec | high | mitigate | `77-SC5-INVARIANTS.md` pairs each probe with a non-empty control | closed |
| T-77-38 | Repudiation | SC5 from one/stale observation | high | mitigate | observation 2 repeats observation-1 probes live in `77-SC5-INVARIANTS.md` | closed |
| T-77-39 | Spoofing | SUMMARY declaring fenced requirement complete | medium | mitigate | census: only `77-03` lists `[ATT-06]`; all others empty (`77-SC5-INVARIANTS.md` § "SUMMARY requirements census") | closed |
| T-77-40 | Tampering | rollback section altered after ATT-06 commit | medium | mitigate | digest matches `ROLLBACK_SECTION_SHA256` at HEAD (as T-77-35) | closed |
| T-77-SC | Tampering | package installs | low | accept | no package added/upgraded; locked syncs only | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-77-01 | T-77-SC | No package is added or upgraded in any of the 8 plans; `uv sync --locked` / `uv lock` only provision or regenerate from already-pinned `uv.lock` requirements. Residual supply-chain risk equals the pre-existing lock. | plan-time disposition (77-01..08) | 2026-09-28 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-28 | 41 | 41 | 0 | /gsd-secure-phase orchestrator (L1 grep-depth; auditor skipped per short-circuit: register authored at plan time, ASVS 1) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-28
