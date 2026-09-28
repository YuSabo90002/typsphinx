# Stack Research

**Domain:** CI/CD publishing pipeline — PyPI Trusted Publishing (OIDC) + PEP 740 attestations for an existing, working GitHub Actions release workflow
**Researched:** 2026-09-23
**Confidence:** HIGH (all load-bearing claims verified against primary sources: the action's own README fetched verbatim, PyPI's own docs fetched verbatim, and a corroborating cross-check)

**Scope note:** This is not a greenfield stack pick. `.github/workflows/release.yml` already has the job graph, the `pypi` environment, and `id-token: write`. The only required GitHub-side change is deleting one line (`password:`) from the `publish-pypi` step; the only required PyPI-side change is a one-time form submission. This document nails down the exact values for both, and an explicit do-not-touch list.

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `pypa/gh-action-pypi-publish` | `@release/v1` (already pinned in the file; currently resolves to **v1.14.2**, tagged 2026-07-29) | Uploads `dist/*` to PyPI and generates PEP 740 attestations | This is the PyPA-maintained, docker-based reference publisher. It is the *only* thing that needs no version bump — the ref is already correct. `master` was sunset; `release/v1` (a moving tag, not a branch) is the currently-documented replacement, alongside pinning to an exact tag or full commit SHA. [Source: action README, "🌇 `master` branch sunset"] |
| PyPI Trusted Publisher registration | n/a (PyPI web form, one-time) | Lets PyPI mint a short-lived API token to the `publish-pypi` job via OIDC, replacing `PYPI_API_TOKEN` | This is the prerequisite the workflow file cannot satisfy on its own — Trusted Publishing is bilateral: the workflow must *not* pass a password, and PyPI must have a registered publisher matching the workflow's OIDC claims, or the exchange fails with `invalid-publisher`. [Source: docs.pypi.org/trusted-publishers/adding-a-publisher/, fetched verbatim] |
| PEP 740 digital attestations (Sigstore-backed) | n/a (action behavior, not a pinned dependency) | Cryptographically ties the uploaded files to the exact GitHub Actions run/identity that built them | Free once Trusted Publishing is on — no extra input required. Requires no new secret, no new job. [Source: action README, "Generating and uploading attestations" section, verbatim] |

### Supporting Inputs (already-present action, just don't add these)

| Input | Current default (v1.14.2) | Needed here? | Notes |
|-------|---------|-------------|-------|
| `attestations` | `true` when authenticated via Trusted Publishing; the action silently has nothing to attest when a `password`/API-token is used instead | **Do not set.** Already the default once `password:` is removed. | Verbatim from README: *"Generating signed digital attestations for all the distribution files and uploading them all together is now on by default for all projects using Trusted Publishing. To disable it, set `attestations: false`."* There is no positive value to set — `attestations: true` would be a no-op restating the default (this is exactly what the ATT-01 todo already concluded; confirmed independently here). |
| `password` | none | **Delete this line** from `publish-pypi` (line 141-144). Leave `publish-testpypi`'s alone — out of scope. | Supplying `password` (an API token) takes the action down the token-auth path entirely; per README, attestation generation "currently requires authentication with a trusted publisher," so a non-empty `password` silently forecloses attestations even if Trusted Publishing is separately registered on PyPI — this is precisely the GitHub-annotation warning ATT-01 recorded. |
| `repository-url` | PyPI (`https://upload.pypi.org/legacy/`) implicit | Not needed on `publish-pypi` (already targets PyPI by omission). `publish-testpypi` already sets it explicitly to TestPyPI and is out of scope. | Only used to redirect to TestPyPI/other indexes. |
| `skip-existing` | `false` | Not needed | Only relevant for re-publishing over race conditions; not this migration's concern. |
| `verbose` | opt-in (`with: verbose: true`) per current README prose | Not needed | Debugging-only aid; adding it is harmless but not required by this change. **Note:** one secondary source (a GitHub tags-page summary) claimed v1.14.0 flipped `verbose`/`print-hash` to default-`true`; the action's own current README, fetched verbatim, still documents both as opt-in toggles ("Sometimes twine upload can fail. To debug, use the verbose setting..."). Treat the "defaults changed" claim as **unverified** — it does not affect what to write in this file either way, since neither input needs to be touched. |
| `user` | `__token__` | Not needed | Only relevant for non-PyPI/non-token auth (e.g. `devpi`). |

## Installation / Exact Change Required

No package installation. The entire GitHub-side change is a 4-line deletion in one place:

```diff
       - name: Publish to PyPI
         uses: pypa/gh-action-pypi-publish@release/v1
-        with:
-          password: ${{ secrets.PYPI_API_TOKEN }}
```

Nothing replaces the deleted `with:` block. With `permissions: id-token: write` (already present, top-level, lines 13-15) and `environment: { name: pypi, ... }` (already present on the `publish-pypi` job, lines 131-133), the action mints its own OIDC-derived token once no `password`/`user` input is supplied. Do not add a `with:` block at all for this step unless a future need (e.g. `verbose: true` for debugging a failed run) arises.

`publish-testpypi` (lines 241-245) is explicitly out of scope per the todo and milestone context — leave its `password: ${{ secrets.TEST_PYPI_API_TOKEN }}` untouched unless the TestPyPI Trusted Publisher is *also* registered (see below); until then, changing that step would break it.

### PyPI-side registration — exact values to type

On https://pypi.org/manage/project/typsphinx/publishing/ (logged in as a `typsphinx` owner), "Add a new publisher" → GitHub Actions tab:

| Field | Value for `publish-pypi` | Verified format |
|-------|---------------------------|------------------|
| Owner | the GitHub org/user that owns the `typsphinx` repo | — |
| Repository name | `typsphinx` | — |
| **Workflow name** | `release.yml` — **bare filename, not a path** | Confirmed by three independent sources: (1) PyPI's own docs prose refers to the registered workflow simply as "the `release.yml` workflow on `octo-org/sampleproject`" after registration [docs.pypi.org/trusted-publishers/adding-a-publisher/, verbatim]; (2) Simon Willison's account of actually filling the form: *"I used `publish.yml` as the name of my workflow file"* with the field's own on-page help text reading *"This file should exist in the `github/workflows/` directory"* — i.e. the directory is implied, not typed; (3) pyopensci's walkthrough table: "Workflow name: Should be `release.yaml`", also bare. **Do not type `.github/workflows/release.yml`.** |
| Environment name | `pypi` | Must match the workflow's `environment: name:` value **exactly**. The field is optional on PyPI's side, but this workflow already declares `environment: { name: pypi }`, so leaving the PyPI field blank while the workflow declares an environment is a mismatch risk — register `pypi` explicitly. Case sensitivity: not stated in PyPI's own prose docs, but a filed upstream bug (`pypi/warehouse#18330`, "Trusted publishing from GitLab CI/CD fails with caps in environment name") demonstrates the match is case-sensitive in practice — use lowercase `pypi`, matching the file exactly. |

Repeat for `publish-testpypi` **only if** that job is meant to keep working: Workflow name `release.yml` (same file, both jobs are defined in it), Environment name `testpypi` (matches its existing `environment: { name: testpypi }`) — this is the todo's own step 1 recommendation and is independent of the `publish-pypi` change.

**Failure mode to know about:** if owner/repo/workflow-filename/environment don't all match the OIDC claims from the actual run, the action fails at the token-exchange step with PyPI returning `invalid-publisher` (not a silent skip) — this is a loud failure, not a repeat of the silent-attestation-skip problem ATT-01 describes. [Source: pydevtools.com troubleshooting guide, corroborating]

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|--------------------------|
| Keep `@release/v1` (moving tag) | Pin to an exact tag (`@v1.14.2`) or full commit SHA + Dependabot | The action's own README recommends this as a general security "pro tip" ("pin versions of Actions... to tagged versions or sha1 commit identifiers"), but this is an orthogonal hardening step, not required to fix ATT-01, and changing the ref is **not** part of this todo's scope — flag as a separate future improvement if the owner wants it. |
| `id-token: write` at top level (current, unchanged) | Move to job-level-only on `publish-pypi` | PyPA's own OIDC docs and the action's README both phrase job-level as the stronger practice ("Pro tip: only set the `id-token: write` permission in the job that does publishing, not globally" — action README; "strongly encouraged... reduces unnecessary credential exposure" — docs.pypi.org). **Not required**: top-level `permissions: id-token: write` is functionally sufficient — every job in the file inherits it, and only `publish-pypi`/`publish-testpypi` actually exercise it. This workflow's existing top-level placement already works and is explicitly called out in the milestone context as an already-validated capability; tightening it to job-level is an optional follow-on hardening outside ATT-01's scope, not a blocker. |

## What NOT to Use / NOT to Add

| Avoid | Why | Instead |
|-------|-----|---------|
| `attestations: true` written explicitly | Already the default the moment Trusted Publishing is active (no `password`); writing it restates current behavior and, per the todo's own reasoning, invites the same misreading that produced ATT-01 in the first place (someone `grep`s for `attestations:` expecting to find the cause and finds nothing, or finds a redundant `true` and assumes it "did something"). | Leave the `with:` block for `publish-pypi` empty/absent entirely. |
| `repository-url`, `skip-existing`, `verbose`, `print-hash`, `user` on `publish-pypi` | None of these inputs are implicated in the Trusted-Publishing/attestations switch; adding any of them is scope creep against this specific todo. | Don't add. |
| Any `${{ }}` interpolated directly into a `run:` block anywhere in this file | Pre-existing, unrelated invariant already documented at the top of `release.yml` (secrets/tag values must flow through `env:`) — not this migration's concern, but do not violate it while editing nearby lines. | N/A — just don't touch `run:` blocks. |
| Retiring `PYPI_API_TOKEN` from repo secrets in the same change | The todo's own step 5: the token is the rollback path if the OIDC exchange fails on the first real tag push after this change. | Remove the secret only *after* a real tag push succeeds via Trusted Publishing with no `invalid-publisher`/`disabling Trusted Publishing` annotation. |

## Version Compatibility

| Component | Compatible With | Notes |
|-----------|------------------|-------|
| `pypa/gh-action-pypi-publish@release/v1` (→ v1.14.2, 2026-07-29) | `actions/upload-artifact@v7` → `actions/download-artifact@v8` artifact handoff already in the file | **No constraint.** The action's own README explicitly documents build/publish job separation via `upload-artifact`/`download-artifact` as the *recommended* pattern (see "Non-goals" section: "use `actions/upload-artifact` and `actions/download-artifact` actions for sharing the built dists across stages and jobs... use the `needs` setting to order the build, test and publish stages"). Attestations are generated by the *publish* step against whatever files sit in `dist/` at that point in the `publish-pypi` job, signed with the OIDC identity of the **current** (publish) job/workflow-run — not the build job. The existing two-job split with an artifact handoff is not a blocker to attestation generation; it is the documented-preferred shape. |
| Trusted Publishing | GitHub-hosted `ubuntu-latest` runner (already used) | Self-hosted runners are "best effort" per the README (OIDC-backed, expected to work, but untested by the action's own CI) — not relevant here since this workflow already runs on `ubuntu-latest`. |
| Trusted Publishing | Reusable workflows | **Not supported** — irrelevant here since `release.yml` calls `pypa/gh-action-pypi-publish` directly from a top-level job, not through `workflow_call`. Noted only because it's the one hard incompatibility the README documents. |

## Sources

- https://raw.githubusercontent.com/pypa/gh-action-pypi-publish/release/v1/README.md — fetched verbatim via `tavily_extract`; primary source for the action's default `attestations` behavior, the `master`-sunset/`release/v1` guidance, the job-level `id-token: write` "pro tip," the build/publish-job-separation being the *recommended* (not merely tolerated) pattern, and the full input list (`repository-url`, `skip-existing`, `verbose`, `print-hash`, `user`, `packages-dir`, `verify-metadata`). Confidence: HIGH (primary, verbatim).
- https://docs.pypi.org/trusted-publishers/adding-a-publisher/ and https://raw.githubusercontent.com/pypi/warehouse/main/docs/user/trusted-publishers/adding-a-publisher.md — fetched verbatim via `tavily_extract`; primary source for the required/optional field list (owner, repository name, workflow filename, optional environment name) and the "will appear... the `release.yml` workflow on `octo-org/sampleproject`" phrasing that establishes bare-filename registration. Confidence: HIGH (primary, verbatim).
- https://til.simonwillison.net/pypi/pypi-releases-from-github — third-party first-hand account confirming the "Workflow name" field takes a bare filename (`publish.yml`) with on-page help text "This file should exist in the `github/workflows/` directory." Confidence: MEDIUM (third-party, but a direct first-hand account of the actual form, corroborating the primary source). Used only as corroboration, not as the sole basis for the bare-filename conclusion.
- https://www.pyopensci.org/python-package-guide/tutorials/trusted-publishing.html — third-party tutorial; corroborates field table (Owner/Repository name/Workflow name/Environment name) and shows an example pin to `pypa/gh-action-pypi-publish@<sha> # v1.14.2`, used to corroborate current version currency. Confidence: MEDIUM.
- https://pydevtools.com/handbook/how-to/how-to-publish-to-pypi-with-trusted-publishing — third-party; corroborates field table and documents the `invalid-publisher` failure mode and the "environment name matches or is blank on both sides" requirement. Confidence: MEDIUM.
- https://github.com/pypi/warehouse/issues/18330 ("Trusted publishing from GitLab CI/CD fails with caps in environment name") — used only to support the case-sensitivity claim on environment-name matching, since neither primary doc states this explicitly. Confidence: MEDIUM (real upstream issue, but about GitLab not GitHub Actions specifically — the underlying PyPI-side claim-matching logic is shared across publisher types, but this is flagged as the weakest-sourced claim in this document). **This specific case-sensitivity claim should be treated as the one item in this file that is not HIGH-confidence-verified against a GitHub-Actions-specific primary source.**
- https://blog.pypi.org/posts/2023-04-20-introducing-trusted-publishers — PyPI's own announcement post; corroborates the diff-shaped before/after example (`id-token: write` added, `username`/`password` removed) and that environment configuration is "additional security hardening," optional. Confidence: HIGH (primary, PyPI's own blog).
- https://github.com/pypa/gh-action-pypi-publish/tags — used only to establish current version currency (latest observed tag: v1.14.2, 2026-07-29); fetched through a summarizing tool rather than raw content, so treat exact dates as MEDIUM confidence, though corroborated independently by pyopensci's pinned-SHA comment (`# v1.14.2`).
- https://peps.python.org/pep-0740/ — PEP 740 itself, referenced by the action's own README as the definition of "digital attestations." Not independently re-fetched in this session; cited via the action README's own link. Confidence: HIGH (the action README's citation of it is primary; the PEP's content itself was not separately re-verified here).

---
*Stack research for: PyPI Trusted Publishing + PEP 740 attestations migration on typsphinx's existing `release.yml`*
*Researched: 2026-09-23*
