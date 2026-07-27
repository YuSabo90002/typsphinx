---
phase: 31
slug: published-url-cutover-repo-wide-link-guard
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-07-27
---

# Phase 31 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| GitHub Actions runner → third-party action | `lycheeverse/lychee-action@v2` executes with the workflow's token and permissions | `GITHUB_TOKEN` scoped `contents: read` |
| CI runner → arbitrary external hosts | lychee issues real HTTP requests to every URL found in the repository | URLs + status codes only |
| Local `gh` CLI → GitHub API | Repository metadata write (`homepage` PATCH) and run inspection | Admin-scoped local credential |
| Public visitor → About panel / README / PyPI → external documentation host | Published URLs followed by untrusted third parties | Reader traffic (IP, UA) |
| README rendering context → badge image host | GitHub fetches the badge image from `app.readthedocs.org` on every repo page view | Viewer IP + user agent |
| Documentation build → Read the Docs build environment | Third-party runner executes this repository's build commands | Repo contents, build env vars |
| Typst compile → `packages.typst.org` | Four `@preview` packages fetched at documentation build time | Package tarballs |
| Local `gh` CLI → third party's public issue thread | Close-reply for Issue #119 posted under the owner's identity | Public reply text |
| INTEGRATIONS.md → future GSD phases | A wrong claim propagates silently into later planning | Factual claims about CI/hosting |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-31-01 | Tampering | `lycheeverse/lychee-action@v2` in links.yml | high | mitigate | Pinned to maintained major tag `@v2`, matching repo convention — verified in `.github/workflows/links.yml` | closed |
| T-31-02 | Elevation of Privilege | links.yml `permissions:` block | medium | mitigate | `permissions: contents: read` only; no `issues:` grant — verified in links.yml | closed |
| T-31-03 | Information Disclosure | `GITHUB_TOKEN` passed to third-party action | medium | mitigate | No `token:` override, no `secrets.*` reference anywhere in links.yml (grep: 0 hits) | closed |
| T-31-04 | Denial of Service | Repo-wide scan on every push and PR | low | mitigate | `--max-retries 3`, `--timeout 30`, `--accept …429`, 3 path excludes present in links.yml; `lock` absent from `--extensions` | closed |
| T-31-05 | Spoofing | Content fetched from arbitrary hosts during scan | low | accept | lychee reads status codes only — see Accepted Risks Log (R-31-01) | closed |
| T-31-06 | Tampering | `gh api … -X PATCH` on repository settings | medium | mitigate | Single-field PATCH (`-f homepage=…`), read-back byte-equal, `description`/`private`/`archived`/`has_issues` asserted identical before/after — recorded in 31-ABOUT-EVIDENCE.md | closed |
| T-31-07 | Spoofing | URL published in the About panel | medium | mitigate | First-party RTD project; curl-verified with `url_effective` staying on `typsphinx.readthedocs.io` — recorded in 31-ABOUT-EVIDENCE.md | closed |
| T-31-08 | Repudiation | Owner-manual fallback leaves no record | low | mitigate | 31-ABOUT-EVIDENCE.md records before-value, exact command, and outcome (API path taken) | closed |
| T-31-09 | Information Disclosure | `gh` token with `repo` scope used for settings write | low | accept | Existing local developer credential, no new secret — see Accepted Risks Log (R-31-02) | closed |
| T-31-10 | Spoofing | The 11 rewritten documentation URLs | high | mitigate | All targets first-party RTD hosts; curl-verified 200 in Plan 03 and independently re-verified in Plan 05 (35/35 fetches → 200, 31-EVIDENCE.md) | closed |
| T-31-11 | Tampering | `project.urls.Documentation` in published release metadata | medium | mitigate | `tomllib` parse assertion; sibling URL fields byte-unchanged — verified: pyproject.toml `[project.urls]` correct, Homepage/Repository/Issues intact | closed |
| T-31-12 | Information Disclosure | Badge image fetched from `app.readthedocs.org` | low | accept | Standard badge mechanics — see Accepted Risks Log (R-31-03) | closed |
| T-31-13 | Denial of Service | Badge host outage renders README badge broken | low | accept | Cosmetic and self-announcing; deliberate D-12 tradeoff — see Accepted Risks Log (R-31-04) | closed |
| T-31-14 | Tampering | Future edit silently reverts the URL rewrite | medium | mitigate | `tests/test_no_stale_github_io_links.py` exists, runs in every pytest/CI invocation; Link Check is second network-level layer | closed |
| T-31-15 | Tampering | INTEGRATIONS.md factual claims | medium | mitigate | Claims re-derived by command at execution time; verification transcript in 31-04-SUMMARY.md | closed |
| T-31-16 | Information Disclosure | Codebase note enumerating secret names | low | accept | Names only, already public in workflow files — see Accepted Risks Log (R-31-05) | closed |
| T-31-17 | Spoofing | URLs in a codebase note no ongoing check watches | medium | mitigate | Exhaustive blocking curl sweep: 7/7 distinct URLs → 200, transcript in 31-04-SUMMARY.md | closed |
| T-31-18 | Tampering | Unguarded `@preview` pin site (`custom_template.typ`) documented but not guarded | medium | accept | Gap converted from silent to tracked; repair deferred to future milestone — see Accepted Risks Log (R-31-06) | closed |
| T-31-19 | Repudiation | Green Link Check run trusted without checking scan surface | high | mitigate | Green run `30265271094` (93 links / 0 errors) compared side-by-side against negative control `30205112477` (8 errors); structural facts re-confirmed — 31-EVIDENCE.md | closed |
| T-31-20 | Tampering | Resolving a red run by weakening the detector | high | mitigate | No `continue-on-error`, no bare URL-exclusion, exactly 3 path excludes (all verified in links.yml); temporary `--accept 403` widening reverted and re-observed green under the tighter set | closed |
| T-31-21 | Information Disclosure | Public reply to an external reporter | medium | mitigate | 31-ISSUE-119-REPLY-DRAFT.md contains zero retired-host references (grep: 0); owner review precedes posting (D-16); issue left OPEN/untouched | closed |
| T-31-22 | Repudiation | Deferred commitment lost at phase boundary | medium | mitigate | `## Handoffs` section present in 31-05-SUMMARY.md listing both deferred items plus the four owed from Phases 29/30.1 | closed |
| T-31-23 | Denial of Service | Wave merge blocked by an avoidable deletion | medium | mitigate | Todo annotated in place; `git diff --diff-filter=D --name-only` asserted empty (31-05-SUMMARY.md) | closed |
| T-31-SC | Tampering | npm/pip/cargo installs (all 5 plans) | high | mitigate | Zero package-registry dependencies added anywhere in the phase; tool arrives solely via `uses: lycheeverse/lychee-action@v2`; guard test uses stdlib only (`pathlib`, `re`, `tomllib`) | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-31-01 | T-31-05 | lychee only reads HTTP status codes; response bodies are neither executed nor persisted. A hostile host can at most falsify its own link's pass/fail. | Plan 31-01 (plan-time disposition) | 2026-07-27 |
| R-31-02 | T-31-09 | The `repo`-scoped `gh` token is the developer's existing local credential, used throughout the milestone; no new secret, storage, or CI exposure introduced. | Plan 31-02 (plan-time disposition) | 2026-07-27 |
| R-31-03 | T-31-12 | Badge fetch from `app.readthedocs.org` follows standard badge mechanics already accepted for five shields.io badges; only viewer IP/UA crosses. | Plan 31-03 (plan-time disposition) | 2026-07-27 |
| R-31-04 | T-31-13 | A broken badge is cosmetic and self-announcing; D-12 deliberately chose a live build-status badge over a permanently-blue static one. | Plan 31-03 (plan-time disposition) | 2026-07-27 |
| R-31-05 | T-31-16 | INTEGRATIONS.md records secret *names* only (`CODECOV_TOKEN`, `PYPI_API_TOKEN`, `TEST_PYPI_API_TOKEN`), all already public in workflow files. | Plan 31-04 (plan-time disposition) | 2026-07-27 |
| R-31-06 | T-31-18 | Guarding `docs/source/_typst/custom_template.typ` against `@preview` drift requires touching the version-sync surface frozen by milestone invariant #2; documenting converts a silent gap into a tracked one. Repair belongs to a future milestone. | Plan 31-04 (plan-time disposition) | 2026-07-27 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-07-27 | 24 | 24 | 0 | /gsd-secure-phase (L1 grep-depth, short-circuit — register authored at plan time) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-27
