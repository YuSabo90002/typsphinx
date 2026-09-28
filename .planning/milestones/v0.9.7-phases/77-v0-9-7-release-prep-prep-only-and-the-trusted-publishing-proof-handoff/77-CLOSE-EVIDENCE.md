# Phase 77 — Close evidence (v0.9.7 publish half)

Recorded at `/gsd-complete-milestone`, 2026-09-28, executing `77-HANDOFF.md` Steps 1–12 in order.
Raw captures were written under `/tmp/p77close/` (not committed).

## Step 1 — Merge
- `origin/main` had moved to `121feb3f` (Dependabot #157–#160; product diff `uv.lock` only).
  Merged into the branch as `3187aac0`; `uv lock --check` exit 0, ruff 0.16.9 clean, black clean,
  `uv.lock` package-name set identical to `v0.9.6` (`MERGED_PACKAGE_SET_MATCHES_V096 = yes`).
- CI dispatch `36438826267` on `3187aac0`: 12/12 success. PR #161: 15/15 checks pass.
- Fence before PR: guarded-region digest `fce6cc7d…` = `REQ_SHA256_GUARDED_BASE` → MATCH.
- `MERGE_SHA = d1df28aeb48556910ac6a2e63ac5455d237d6d79` (real merge commit, parents `121feb3f` + `3187aac0`;
  tree identical to `3187aac0`).

## Step 2 — Tag
- Before: no local `v0.9.7`, none on `origin`, `v0.9.6` control present.
- `v0.9.7` annotated on `MERGE_SHA`, pushed. `RELEASE_RUN_ID = 36439849556` (push, headBranch `v0.9.7`).

## Step 3 — Release run
- `pypi` environment approved by the owner (`YuSabo90002`); 15-minute timer from 15:01:48Z.
- Attempt 1: `Validate Release` success, `Build Distribution` success, `Publish to PyPI` success,
  `Create GitHub Release` success, `Publish to TestPyPI (Optional)` skipped.

## Step 4 — ATT-04 (attempt 1)
- `disabling Trusted Publishing` → **0**; `attestations input is ignored` → **0**.
- Corroboration: `Generating and uploading digital attestations` → 1.
- Control run `35730551619` re-read live: 1 / 1 / 0.
- Necessary, not sufficient: the action decides this locally from the presence of a credential;
  ATT-03 is what proves PyPI served provenance. Per Discretion A, the requirement's literal title
  phrase is superseded by the two-grep pair (the title attribute is never printed by `gh run view --log`;
  control read 0).

## Steps 5–6 — ATT-03
| File | Simple JSON `provenance` | Integrity HTTP | bundles | publisher |
|---|---|---|---|---|
| `typsphinx-0.9.7-py3-none-any.whl` | `https://pypi.org/integrity/typsphinx/0.9.7/typsphinx-0.9.7-py3-none-any.whl/provenance` | 200 | 1 | `GitHub\|YuSabo90002/typsphinx\|release.yml\|pypi` |
| `typsphinx-0.9.7.tar.gz` | `https://pypi.org/integrity/typsphinx/0.9.7/typsphinx-0.9.7.tar.gz/provenance` | 200 | 1 | `GitHub\|YuSabo90002/typsphinx\|release.yml\|pypi` |

Prefix count `typsphinx-0.9.7*` = 2. Control: 0.9.6 files `null,null`.

`ATT03_VERDICT = PASS`

## Step 7 — ATT-05
- Before: repo `PYPI_API_TOKEN|TEST_PYPI_API_TOKEN`; env `pypi` `PYPI_API_TOKEN`; env `testpypi` none.
- `gh secret delete PYPI_API_TOKEN` and `gh secret delete PYPI_API_TOKEN --env pypi` (after ATT-03 PASS).
- After: repo `TEST_PYPI_API_TOKEN`; env `pypi` none; env `testpypi` none.
- PyPI revocation: the owner stated "失効した" (revoked) on 2026-09-28.

## Step 8 — DOC-25
- `.planning/codebase/INTEGRATIONS.md:116` replaced with the pre-drafted text (matches what Step 7
  observed); line for `TEST_PYPI_API_TOKEN` kept.

## Step 9 — Translations
- `update-pin.yml` run `36443440802` success; submodule pin = `d1df28ae…` (= `MERGE_SHA`);
  resulting commit `3c0f43db80d4b897e01f329a973105bd8c77c1b5`.
- `typsphinx-doc-translations` tagged `v0.9.7` (annotated, object `216c36b0`) on `3c0f43db`.

## Step 10 — Read the Docs
- `typsphinx` stable identifier `d1df28ae…` (build 34805939 success); `typsphinx-ja` stable
  identifier `3c0f43db…` (build 34806699 success).
- Cache-busted fetches: `en/stable` and `ja/stable` both render `typsphinx 0.9.7`.

## Step 11 — REL-17
- `refs/tags/v0.9.7` on `origin` → `d1df28ae`.
- Release body: first 50 lines byte-identical to `extract_changelog_section.py 0.9.7`
  (3132 bytes, sha256 `82f27b34…`); remaining lines are GitHub's Installation / What's Changed;
  no scratch-block heading. Assets: wheel (194,358 B), sdist (861,641 B), `typsphinx.pdf` (as v0.9.6).
- Linkcheck obligation: `rm -rf docs/_build && tox -e linkcheck` → 97/97 `working`, including
  `compare/v0.9.7...HEAD` and `releases/tag/v0.9.7`.

## Step 12
REL-17, ATT-03, ATT-04, ATT-05 and DOC-25 checked by hand, each against its own observations above.
