---
phase: 30
slug: japanese-rtd-site-hand-rolled-machinery-orphan-removal
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-07-27
---

# Phase 30 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Repository content → `gh-pages` branch | `peaceiris/actions-gh-pages` copies `publish_dir` into a publicly served branch using a repo-write token | Public documentation HTML |
| Workflow YAML → Actions runner token scopes | The `permissions:` block bounds what an edited workflow may do with `GITHub_TOKEN` | CI token scopes |
| `docs/source/conf.py` → `typsphinx-doc-translations` RTD build | conf.py is consumed byte-for-byte via git submodule by a second repository's build | Build configuration |
| Furo theme defaults → published page | Deleting the sidebar override hands template selection back to the theme, whose upstream default includes READTHEDOCS-gated third-party slots | Rendered sidebar HTML |
| Deleted client-side script → reader's browser | Removed `page.html` override wrote a language flag into sessionStorage | Two-letter language code (non-sensitive) |
| Hand-authored `.po` translations → sole remaining copy | Plan 03 deleted one of exactly two copies of 257 translated msgids | Human translation work |
| Phase evidence record → later readers | A gate recorded as passing becomes the basis for Phase 32's irreversible teardown | Verification evidence |
| Public RTD HTTP endpoint → verification record | Unauthenticated live fetch is the only observation for the RTD-04 invariant | Status code / page markup counts |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-30-01 | Tampering | `publish_dir` on `peaceiris/actions-gh-pages` step | low | mitigate | Exact-string gate in 30-01 verify; re-measured 2026-07-27: `publish_dir == ./docs/_build/html`, step's `if:`/`github_token`/`cname` intact | closed |
| T-30-02 | Elevation of Privilege | `docs.yml` `permissions:` block | medium | mitigate | Parsed-mapping equality gate; re-measured 2026-07-27: exactly `{contents: write, pages: write, id-token: write}` | closed |
| T-30-03 | Denial of Service | Docs pipeline caller/callee mismatch | medium | mitigate | Every `tox -e` env in workflow cross-checked against `tox.ini` sections (re-measured: `docs-html`, `docs-pdf` both present); docs.yml run 30269906943 on PR #124 completed green | closed |
| T-30-04 | Tampering | Premature removal of GitHub Pages deploy step | medium | mitigate | Structural gate: exactly one `peaceiris/actions-gh-pages` step survives (re-measured 2026-07-27: count = 1); teardown stays behind Phase 32's gate | closed |
| T-30-05 | Tampering | `conf.py` cross-repository regions | medium | mitigate | Regions SHA-256-pinned in 30-02 verify (gate passed per SUMMARY); language seam re-measured intact (`_resolve_language` / `READTHEDOCS_LANGUAGE` present, 4 refs) | closed |
| T-30-06 | Information Disclosure | Furo's restored `ethical-ads` slot | low | accept | Accepted per plan; resolved better than feared — UAT test 3 measured `furo-sidebar-ad-placement = 0` and `furo-readthedocs-versions = 0` on RTD build 33763874 | closed |
| T-30-07 | Information Disclosure | Removal of sessionStorage language flag | low | accept | Flag held a two-letter language code, no credential; removal narrows client-side surface | closed |
| T-30-08 | Repudiation | Test coverage reduced under cover of deletion | medium | mitigate | Count gates in 30-02 verify; re-measured 2026-07-27: `tests/test_readthedocs_config.py` has 4 `def test_` and 39 `assert ` — unchanged | closed |
| T-30-09 | Tampering | Irrecoverable loss of hand-authored `.po` translations | medium | mitigate | Live pre-deletion query proved 13 `.po` files in `typsphinx-doc-translations` (30-03 gate); git history retains every removed file | closed |
| T-30-10 | Repudiation | Coverage reduced inside all-deletions commit | medium | mitigate | Commit file-list asserted exactly four deleted paths, zero adds/mods; collected-test delta accounted (30-03 gate passed) | closed |
| T-30-11 | Tampering | Deleting live `installation.rst` by basename confusion | medium | mitigate | Existence + byte-equality gate; re-measured 2026-07-27: `docs/source/installation.rst` present, 76 lines | closed |
| T-30-12 | Denial of Service | Build broken by dangling `locale_dirs` reference | low | mitigate | English build measured green with locale dir absent (re-confirmed: dir absent, docs.yml build green on PR #124) | closed |
| T-30-13 | Repudiation | Evidence record asserting an unmeasured pass | medium | mitigate | Every gate in 30-EVIDENCE.md carries verbatim command+output; unobservables authored as `backstop` truths that abstained to `human_needed`, now resolved by UAT (3/3 pass) | closed |
| T-30-14 | Tampering | Gate satisfied by editing unrelated files | medium | mitigate | Positive survivor checks (7 static-path occurrences + `confval` fixture line) enforced in 30-04 verify | closed |
| T-30-15 | Tampering | Evidence destroyed by filename collision | low | mitigate | Record named `30-EVIDENCE.md`; `30-VERIFICATION.md` reserved for verify-work — both exist separately (re-confirmed) | closed |
| T-30-16 | Information Disclosure | Unauthenticated fetch of public RTD URL | low | accept | Public GET, no credential, no body; recorded output is status code and markup counts only | closed |
| T-30-SC | Tampering | npm/pip/cargo installs | low | accept | Phase installs nothing and touches no dependency list (30-RESEARCH.md Package Legitimacy Audit: zero packages) | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-30-01 | T-30-06 | Furo READTHEDOCS-gated sidebar slots are upstream theme defaults; suppressing them is out of scope (SC#2 mandates the override deletion). Measured post-merge: neither slot renders on the hosted site | plan-time disposition (30-02-PLAN) | 2026-07-27 |
| R-30-02 | T-30-07 | sessionStorage flag was a non-sensitive two-letter language code; removal narrows surface | plan-time disposition (30-02-PLAN) | 2026-07-27 |
| R-30-03 | T-30-16 | One-off unauthenticated GET of a public docs URL for verification evidence, never an integration | plan-time disposition (30-04-PLAN) | 2026-07-27 |
| R-30-04 | T-30-SC | No packages installed, no dependency list touched anywhere in the phase | plan-time disposition (all plans) | 2026-07-27 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-07-27 | 17 | 17 | 0 | gsd-secure-phase (L1 short-circuit: plan-time register, no open threats ≥ high) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-27
