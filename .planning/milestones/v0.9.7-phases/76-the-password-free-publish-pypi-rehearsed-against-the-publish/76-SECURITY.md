---
phase: "76"
slug: "the-password-free-publish-pypi-rehearsed-against-the-publish"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-28"
---

# Phase 76 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
>
> Retroactive run (2026-09-28, after the phase closed and after the v0.9.7 milestone audit flagged
> this file as missing). Register taken verbatim from the `<threat_model>` blocks of 76-01, 76-02
> and 76-03 (authored at plan time); `T-76-SC`, declared identically in all three plans, is listed
> once. No SUMMARY carries a `## Threat Flags` section. ASVS L1 with every threat closed, so the
> workflow's short-circuit applied: evidence below is L1 grep-depth, re-measured against the live
> tree, `gh`, and `76-ATT-EVIDENCE.md` — no auditor subagent was spawned.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| workflow file → GitHub Actions runner | The edited YAML decides which credential `publish-pypi` presents to PyPI | publish credential (high) |
| GitHub OIDC → PyPI `/_/oidc/mint-token` → upload endpoint | Short-lived token minted from the job's OIDC identity; registration check, then duplicate-file check | OIDC identity token, upload (high) |
| executor → GitHub Actions (`workflow_dispatch`) | Agent-issued, irreversible run on the production release workflow | workflow trigger (high) |
| `pypi` environment gate | Required reviewer (owner) + 15-minute `wait_timer` before the OIDC mint | deployment approval (high) |
| action container → Sigstore (Fulcio, Rekor) | Public, permanent signing records on the Trusted Publishing path | provenance metadata (public) |
| docname / image URI → DEBUG log text | Author-controlled path strings rendered into a diagnostic | file paths (low) |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-76-01 | Tampering | `release.yml` edit | medium | mitigate | `git diff --stat v0.9.6..HEAD -- .github/workflows/release.yml` → `2 deletions(-)`, 0 insertions; `${{` count inside `run: \|` blocks → 0 | closed |
| T-76-02 | Elevation of Privilege | long-lived `PYPI_API_TOKEN` read by `publish-pypi` | high | mitigate | `publish-pypi` step is `uses: pypa/gh-action-pypi-publish@release/v1` with no `with:`; the file's only `password:` is `release.yml:242` (`TEST_PYPI_API_TOKEN`, publish-testpypi). OIDC path proven by rehearsal run 36321530105 (76-ATT-EVIDENCE.md ATT-02 verdict, re-verified in 76-VERIFICATION.md) | closed |
| T-76-03 | Information Disclosure | the two remaining `PYPI_API_TOKEN` secrets (repo + `pypi` env) | medium | transfer | Retained as rollback path; retirement transferred to ATT-05 at `/gsd-complete-milestone`, strictly after ATT-03 (77-HANDOFF.md Step 7). `POST_REPO_/POST_ENV_SECRET_PYPI_API_TOKEN = present` (76-ATT-EVIDENCE.md:955/961) | closed |
| T-76-04 | Tampering | replacement keys / action pin / permissions narrowing slipping in | medium | mitigate | Same 0-insertion diff as T-76-01; `id-token: write` still at `release.yml:15`; `publish-testpypi` untouched | closed |
| T-76-05 | Repudiation | cross-directory DEBUG logs in `translator.py` | low | mitigate | `translator.py:5123` and `:5228` read `quote_path(up_path)` / `quote_path(down_path)`; hardcoded `'{up_path}'`/`'{down_path}'` count → 0; `tests/test_translator_path_quoting_gate.py` 4 passed (76-VERIFICATION.md) | closed |
| T-76-06 | Tampering | scope creep into `builder.py`/`writer.py`/`template_registry.py`/`pathfmt.py` | low | mitigate | `git diff --stat v0.9.6..HEAD -- typsphinx/` → only `translator.py` (4+/2−: the import and the two log lines) | closed |
| T-76-07 | Information Disclosure | treating `quote_path()` output as sanitized | low | accept | See Accepted Risks AR-76-01 | closed |
| T-76-08 | Repudiation | silent second `release.yml` run (5xx retry / resumed executor) | high | mitigate | `NEW_RUN_COUNT = 1`, `REHEARSAL_DISPATCH_COUNT = 1` (76-ATT-EVIDENCE.md:690/948); live `gh run list --workflow release.yml --event workflow_dispatch` → exactly one run on the milestone branch (36321530105) | closed |
| T-76-09 | Elevation of Privilege | agent self-approving the `pypi` deployment | high | mitigate | `APPROVAL_POSTS_BY_EXECUTOR = 0` (76-ATT-EVIDENCE.md:976); pending_deployments read with GET only; approval via the owner's own GitHub notification | closed |
| T-76-10 | Tampering | identical-hash 200-OK upload letting `create-release` run against v0.9.6 | medium | mitigate | `JOB_CREATE_RELEASE = skipped` (:754); `PRE_/POST_RELEASE_BODY_SHA256` equal (:501/:922) | closed |
| T-76-11 | Spoofing | dispatching a ref still carrying the token, or a stale SHA | medium | mitigate | `REHEARSAL_HEAD_SHA` equals `DISPATCH_REF_SHA` (:702); pushed-ref content check passed before dispatch (:279) | closed |
| T-76-12 | Repudiation | rehearsal's clean annotation reading laundered into ATT-04 | medium | mitigate | `## Rehearsal is not ATT-04` section (:1000); ATT-03/04/05 checkboxes still `- [ ]` in REQUIREMENTS.md | closed |
| T-76-13 | Tampering | secret deletion / tag push / version bump slipping into the rehearsal | medium | mitigate | `POST_ORIGIN_V097_TAGS = 0` (:967); both `PYPI_API_TOKEN` secrets present post-run (:955/:961) | closed |
| T-76-14 | Information Disclosure | permanent public Sigstore/Rekor entries for a rehearsal build | low | accept | See Accepted Risks AR-76-02 | closed |
| T-76-15 | Denial of Service | approval never arriving, executor hanging | low | mitigate | D-04 90-minute bound applied; run completed well inside it, no HALT (:730) | closed |
| T-76-16 | Elevation of Privilege | top-level `id-token: write` granted to every job | low | accept | See Accepted Risks AR-76-03 | closed |
| T-76-SC | Tampering | package installs | low | accept | See Accepted Risks AR-76-04 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-76-01 | T-76-07 | `pathfmt.py` documents `quote_path()` as a delimiter chooser for human-readable diagnostics, not a sanitizer; the phase only routes a DEBUG log through it | plan 76-02 (owner-approved plan) | 2026-09-27 |
| AR-76-02 | T-76-14 | Sigstore/Rekor entries are public by design and carry provenance metadata, not secrets; disclosed to the owner in the 76-03 Task 2 checkpoint before dispatch | owner (76-03 checkpoint) | 2026-09-27 |
| AR-76-03 | T-76-16 | Job-level `permissions:` narrowing is explicitly Out of Scope in REQUIREMENTS.md; unchanged by this phase | owner (REQUIREMENTS.md § Out of Scope) | 2026-09-23 |
| AR-76-04 | T-76-SC | No package added or upgraded; `uv sync` provisions only `uv.lock`-pinned dependencies | plans 76-01/02/03 | 2026-09-27 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-28 | 17 | 17 | 0 | `/gsd-secure-phase 76` orchestrator (L1 short-circuit, retroactive) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-28
