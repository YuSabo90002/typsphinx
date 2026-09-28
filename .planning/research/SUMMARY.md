# Project Research Summary

**Project:** typsphinx v0.9.7 — Trusted Publishing and Release  
**Domain:** CI/CD release pipeline migration (GitHub Actions + PyPI publishing)  
**Researched:** 2026-09-23  
**Confidence:** HIGH overall (HIGH for Stack/Features/Architecture; MEDIUM-HIGH for Pitfalls)

## Executive Summary

This milestone migrates typsphinx's PyPI publishing workflow from a long-lived API token (`PYPI_API_TOKEN`) to PyPI Trusted Publishing (OIDC), which enables automatic PEP 740 digital attestations without any new infrastructure or action pinning — the action is already correctly configured at `@release/v1`. The **core code change** is deleting exactly one line (`password: ${{ secrets.PYPI_API_TOKEN }}`) from `.github/workflows/release.yml:144`. The **critical sequencing requirement** is that this deletion must happen *after* manually registering a Trusted Publisher on PyPI's web form (a one-time owner action with four fields: owner/repo/workflow-filename/environment), and *before* the real `v0.9.7` tag is pushed.

The central risk is not code correctness (the workflow already has `id-token: write` and the `pypi` environment in place) but **registration correctness** (if PyPI's form is filled with the wrong workflow filename or environment name, the token exchange fails outright on the real tag with `invalid-publisher`). The secondary risk is **false-positive verification**: green CI and a successful upload are *not* proof that attestations are attached — proof requires checking PyPI's own served state via the Simple JSON API's `provenance` field or the Integrity API's publisher claims, not just reading the workflow file or watching CI pass.

The milestone also includes MSG-06 (a one-line `quote_path()` fix in `translator.py`, independent of all release-pipeline work), with the same tag delivering both ATT-01 and MSG-06. There is no dry-run path for Trusted Publishing in this workflow (no `if:` gate on `publish-pypi`, so `workflow_dispatch` still hits production PyPI), but a safe pre-tag rehearsal exists: dispatching against the already-published `v0.9.6` exercises real OIDC while PyPI safely rejects the duplicate upload—a mismatch between registration fields would fail differently (as `invalid-publisher` before upload, not as `400 File already exists` after).

## Key Findings

### Recommended Stack

The stack is **fully already in place**. No new dependencies, no version bumps, no new workflow inputs.

**Core technologies:**
- **`pypa/gh-action-pypi-publish@release/v1`** (currently v1.14.2, tagged 2026-07-29) — the PyPA-maintained publisher action. Already correctly pinned in the file; `@release/v1` is a moving tag that tracks the v1 release line and currently includes attestations-on-by-default (enabled in v1.11.0+).

- **PyPI Trusted Publisher registration** (manual form on `pypi.org`, one-time) — the prerequisite PyPI must have before the workflow can exchange OIDC tokens. Fields: repository owner, repository name, workflow filename (bare: `release.yml`), environment name (`pypi`).

- **PEP 740 digital attestations** (Sigstore-backed, action behavior, no new config) — signed provenance linking each uploaded file to the GitHub Actions run/identity. Currently *silently dropped* in v0.9.6 due to the `password:` line. Once `password:` is removed and Trusted Publishing succeeds, attestations are automatically on.

### Expected Features

The acceptance oracle is **PyPI's own served state**, not the log or CI exit code.

**Must check at v0.9.7's real tag push (P1):**

1. **S1 — Absence of the disabling annotation:** `gh run view <run-id> --log | grep -c "attestations input ignored"` → expect `0`

2. **S4 — PyPI Simple JSON API carries non-null `provenance` field (PRIMARY oracle):**
   ```bash
   curl -s "https://pypi.org/simple/typsphinx/" -H "Accept: application/vnd.pypi.simple.v1+json" \
     | jq '.files[] | select(.filename | test("0\\.9\\.7")) | {filename, provenance}'
   ```
   Expect: non-null `provenance` URL for both wheel and sdist  
   **CRITICAL:** Use **Simple Index JSON API** (`/simple/<project>/`), not legacy (`/pypi/<project>/<version>/json`)  
   Baseline (v0.9.6 today): `"provenance": null`

3. **S5 — PyPI Integrity API names the workflow:**
   ```bash
   curl -s "https://pypi.org/integrity/typsphinx/0.9.7/typsphinx-0.9.7-py3-none-any.whl/provenance" \
     -H "Accept: application/vnd.pypi.integrity.v1+json" | jq '.attestation_bundles[0].publisher'
   ```
   Expect: `{"kind": "GitHub", "repository": "YuSabo90002/typsphinx", "workflow": "release.yml", "environment": "pypi"}`  
   Baseline (v0.9.6 today): `404 Not Found`

**What does NOT count as proof:**
- ✗ "The upload succeeded" (v0.9.6 succeeded with `provenance: null`)
- ✗ "CI is green" (7+ ways attestations can be silently absent)
- ✗ "The workflow file looks correct" (code review cannot observe PyPI-side registration)

### Architecture Approach

The pipeline is a fixed five-job DAG; this is **not a redesign**. Critical finding: **sequencing of manual PyPI registration against code changes and tagging**, and the **false-pass verification trap** (REL-04 in v0.7.0 uncaught until real tag).

**Sequencing requirement:**

1. **PyPI-side registration FIRST** — use **existing `typsphinx` project's own Publishing settings page** (not pending-publisher flow). Capture four fields directly from file/repo, not memory.

2. **Code change (MSG-06 independent, ATT-01 workflow edit)** merged to `main` — must not land before PyPI registration.

3. **Version bump + release-prep** — standard release-prep shape.

4. **Tag push + proof gathering** — only moment Trusted Publishing is exercised on production PyPI. If `invalid-publisher`, re-run same failed run (within 7-day artifact window) once registration fixed.

5. **Secret retirement** (strictly after proof) — delete both `PYPI_API_TOKEN` copies (repo-scoped and env-scoped); separately revoke on PyPI.

### Critical Pitfalls

**Top 5 pitfalls:**

1. **Workflow filename/environment name mismatch** — Copy fields directly from `release.yml` and repo URL to registration form, not memory.

2. **Wrong registration flow** — Use **existing project's Publishing settings**, not account-level pending-publisher page.

3. **"Looks correct but unexercised"** — Treat "proof" as *mandatory*: check PyPI state (S4/S5), not just green CI. This project already failed this (REL-04).

4. **Attestations silently absent (7 ways)** — Verification step must check actual PyPI state (S4/S5) to rule out all 7 causes.

5. **Secret retirement sequencing** — Delete GitHub secret *after* proof. Delete *both* copies. Separately revoke on PyPI. Leave `TEST_PYPI_API_TOKEN` untouched.

## Implications for Roadmap

**Suggested phases:**

### Phase A: MSG-06
- Independent; can run anytime
- One-line `quote_path()` fix in `translator.py`

### Phase B: ATT-01 Workflow Edit + PyPI Registration
- PyPI registration must complete *before* this code lands
- Delete `password:` at line 144 only
- Checklist: PyPI registration done with fields from file/repo

### Phase C: Version Bump + Release-Prep
- Bump `pyproject.toml` 0.9.6→0.9.7
- Regenerate `uv.lock`, update `README.md`, promote CHANGELOG
- Precedented by v0.9.6; standard release pattern

### Phase D: Tag Push + Proof Gathering
- Push `v0.9.7` tag
- **Mandatory proof gates:**
  - [ ] Run log: 0 of `"attestations input ignored"`
  - [ ] Simple JSON API: non-null `provenance` for 0.9.7 files
  - [ ] Integrity API: `200` with correct workflow/repo in publisher
- Optional pre-tag: dispatch against v0.9.6 (will reject with `400 File already exists` — expected)
- Recovery: if `invalid-publisher`, fix registration and re-run; if attestations absent, bump to 0.9.8

### Phase E: Secret Retirement
- Delete repo-scoped: `gh secret delete PYPI_API_TOKEN`
- Delete env-scoped: `gh secret delete PYPI_API_TOKEN --env pypi`
- Revoke on PyPI's token management page
- Leave `TEST_PYPI_API_TOKEN` untouched

**Phase ordering rationale:**
- A and B parallel (MSG-06 independent)
- B precedes C only in that both reach `main` before D
- D strictly depends on B+C+registration
- E strictly depends on D proof passing

### Research Flags

**Phases needing owner decisions (not requiring deeper research):**
- **Phase B:** Owner confirmation that PyPI registration is complete before merge
- **Phase D (optional):** Whether to include pre-tag v0.9.6 rehearsal
- **Phase D (failure mode):** If rollback needed, delete or leave dangling the `v0.9.7` git tag?

**Phases with standard patterns (skip research):**
- **Phase A:** Straightforward one-line bug fix
- **Phase C:** Precedented release-prep pattern
- **Phase E:** Straightforward CLI secret management

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| **Stack** | **HIGH** | All claims vs. primary sources: action README (verbatim), PyPI docs (verbatim), v1.14.2 tag confirmed. No new dependencies. |
| **Features** | **HIGH** | Success signals vs. action source code + live curl against PyPI APIs. Endpoint URLs, headers, field names verified. MEDIUM: PyPI web UI wording (JS SPA, not re-verified) but capability corroborated by 2 sources. |
| **Architecture** | **HIGH** | Repo state via gh CLI (2026-09-23). Phase sequencing vs. release.yml DAG, artifact retention, git history. Failure modes vs. pypa/gh-action-pypi-publish corroborated 3+ sources. |
| **Pitfalls** | **MEDIUM-HIGH** | Primary: PyPI docs + action README. Community: pypa/gh-action-pypi-publish issues across 2+ sources. Pitfall 4 precedented by this repo's own REL-04. |

**Overall: HIGH** — Authoritative for immediate roadmap creation. Open decisions flagged explicitly; no fundamental unknowns remain.

### Gaps to Address

1. **Pre-tag rehearsal decision:** Clarify in CONTEXT whether Phase D includes optional v0.9.6 dispatch or goes straight to production tag.

2. **Rollback git-tag handling:** Confirm owner preference for `v0.9.7` git tag deletion/retention if rollback needed (repo has no precedent).

3. **INTEGRATIONS.md stale documentation:** `.planning/codebase/INTEGRATIONS.md:116-117` describes `PYPI_API_TOKEN` backwards. Fix as post-Phase E documentation.

4. **Environment-name case sensitivity:** One upstream GitHub issue (GitLab) supports case-sensitivity claim; PyPI own docs silent. Already tested via Phase D real tag.

## Sources

### Primary (HIGH confidence — fetched this session)

**Stack:**
- pypa/gh-action-pypi-publish README (verbatim)
- PyPI Trusted Publishers docs (verbatim)
- PyPI blog announcement

**Features:**
- pypa/gh-action-pypi-publish source @ release/v1
- PyPI Simple JSON API (live vs. typsphinx 0.9.6 + sigstore 4.5.0, 2026-09-23)
- PyPI Integrity API (live, URLs/fields verified)
- PyPI Attestations docs

**Architecture:**
- `.github/workflows/release.yml` (2026-09-23)
- gh CLI: environments, secrets
- git history: v0.9.x tags/changelog
- ATT-01 todo, PROJECT.md

**Pitfalls:**
- PyPI Trusted Publishers troubleshooting, Security Model
- pypi/warehouse issues (#18330, #6872, #10541)
- pypa/gh-action-pypi-publish issues/discussions (#138, #173, #217, #283, #256, #16)

### Secondary (MEDIUM confidence)

Simon Willison account, pyOpenSci tutorial, Trail of Bits, pydevtools, Sigstore, PEP 740 tracker

---

*Research completed: 2026-09-23*  
*Ready for roadmap: YES*
