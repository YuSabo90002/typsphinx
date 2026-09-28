# Phase 77 — Handoff to /gsd-complete-milestone

This document is standalone: every number it cites is written into it, not linked. A reader with
only this file can execute the whole release, in order.

The ordered publish-half sequence — the merge to `main`, the `v0.9.7` tag push, the `pypi`
environment's manual approval, ATT-04, ATT-03, ATT-05, DOC-25, the translations pin dispatch and
the Read the Docs re-measurement — is written above this rollback section by a later plan of this
phase (77-07). Every command below writes to `/tmp/p77close/` (create it first with
`mkdir -p /tmp/p77close`) and reads its own output back from a named file rather than substituting
it inline; values known only at the close are written as `<PLACEHOLDER>` (for example
`<RELEASE_RUN_ID>`).

## What this phase satisfied

**ATT-06**, quoted verbatim from `.planning/REQUIREMENTS.md`:

> - [ ] **ATT-06**: A rollback procedure is recorded before the tag is pushed, and names: restoring
>       `password:`, bumping to 0.9.8 rather than retrying 0.9.7 (PyPI permanently refuses a
>       re-uploaded filename regardless of git-tag state), and **deleting the failed `v0.9.7` tag both
>       locally and on `origin`** (owner decision, 2026-09-23 — this repository has no precedent: a
>       `git tag -l` measurement shows 0.9.1 and 0.9.3–0.9.5 were never tagged at all, so a pushed tag
>       with no release would be a first).

ATT-06 closed in this phase: the rollback procedure below (`## Rollback procedure (ATT-06)`) was
committed as `ROLLBACK_COMMIT_SHA = fe4e87638220ec8c7574f73050e336e0fe28110b` while no `v0.9.7` tag
existed locally or on `origin` — see `77-ATT06-EVIDENCE.md` (D-04).

None of the following five is closed here. `REL-17`, `ATT-03`, `ATT-04`, `ATT-05` and `DOC-25`,
quoted verbatim:

> - [ ] **REL-17**: 0.9.7 is published — `pyproject.toml` bumped as the **sole** version literal with
>       `uv.lock` and `README.md` in lockstep, one curated `## [0.9.7]` CHANGELOG section (with its
>       tag link and the `[Unreleased]` compare advanced, per the release-prep convention), the
>       `v0.9.7` tag pushed, the PyPI upload live, and a GitHub Release whose body comes from
>       `scripts/extract_changelog_section.py`. The release notes describe attestations as **audit
>       provenance, not an install-time gate** — neither `pip` nor `uv` verifies them today.

> - [ ] **ATT-03**: The switch is proven on **PyPI's own served state** for the real 0.9.7 upload, not
>       on the run log and not on the workflow file. Both checks must hold:
>       (a) the Simple JSON API — `curl -s https://pypi.org/simple/typsphinx/ -H 'Accept:
>       application/vnd.pypi.simple.v1+json'` — returns a **non-null `provenance`** for **both** the
>       0.9.7 wheel and the 0.9.7 sdist (measured baseline: 0.9.6's files carry `"provenance": null`);
>       and (b) the Integrity API —
>       `https://pypi.org/integrity/typsphinx/0.9.7/<filename>/provenance` — returns **200** with
>       `publisher` naming `repository` `YuSabo90002/typsphinx`, `workflow` `release.yml` and
>       `environment` `pypi` (measured baseline: 404 for 0.9.6's wheel). The legacy
>       `/pypi/<project>/<version>/json` endpoint never carries this field and does not count.

> - [ ] **ATT-04**: The v0.9.7 release run carries **zero** occurrences of the action's
>       `attestations input ignored` / `disabling Trusted Publishing` annotation — the line
>       `release.yml` run `35730551619` emitted for v0.9.6. This is a necessary but **not sufficient**
>       signal: the action emits it locally from the presence of `password:` before any network call,
>       so its absence alone does not prove PyPI served provenance. ATT-03 is what proves that.

> - [ ] **ATT-05**: `PYPI_API_TOKEN` is retired from **both** GitHub scopes — the repository-scoped
>       secret and the `pypi`-environment-scoped secret, which are two distinct secrets — and the
>       token is separately revoked on PyPI's own token-management page. This happens **strictly after
>       ATT-03 passes**; until then the token is the rollback path. `TEST_PYPI_API_TOKEN` is left in
>       place, repository-scoped and environment-scoped alike.

> - [ ] **DOC-25**: `.planning/codebase/INTEGRATIONS.md:116-117` no longer describes `PYPI_API_TOKEN`
>       as the trusted-publishing mechanism. It describes what the repository actually does after
>       ATT-01 and ATT-05 land.

REL-17's prep half is proven by the SC table below and its publish half by Steps 2, 5 and 11.
ATT-03, ATT-04, ATT-05 and DOC-25 are coverage-only and are checked only in Step 12, by the
operator, against the observations the steps below record — never by phase-completion tooling.
Every `77-0N-SUMMARY.md` of this phase declares `requirements-completed: []` except 77-03's, which
declares ATT-06 alone.

## Success criteria

| SC | Verdict | Evidence |
|----|---------|----------|
| SC1 | MET | `77-BUMP-EVIDENCE.md`: the one five-file commit `BUMP_COMMIT_SHA = 39cb79f970c4137d4238023e1df7291c7c282c3a` (`BUMP_COMMIT_FILES = CHANGELOG.md\|README.md\|pyproject.toml\|tests/test_changelog_page_gate.py\|uv.lock`), `uv lock --check` exit 0, and the changelog page gate runs zero skips. |
| SC2 | MET | `77-CHANGELOG-EVIDENCE.md`: the extractor's stdout (`scripts/extract_changelog_section.py 0.9.7`, `EXTRACT_BYTES = 3132` bytes, `EXTRACT_LINES = 50` lines) is byte-identical to the committed `## [0.9.7]` section, both digests `EXTRACT_SHA256 = 82f27b346b89163e08e6f64ba7b119c3fcc4ab20d300d06f6cf94d86a96983f6`; the file carries three `### Known Limitations` headings (`[0.1.0b1]`, `[0.9.6]`, `[0.9.7]`); the provenance wording states audit provenance, not an install-time gate. |
| SC3 | MET | Local half `77-GREEN-TREE-EVIDENCE.md`: both pytest runs `FULL_PYTEST_PASSED = 1573` and `FULL_PYTEST_C_PASSED = 1573` on interpreter `PYVENV_VERSION_INFO = 3.14`, both documentation warning counts `TIP_HTML_WARNINGS = 0` and `TIP_PDF_WARNINGS = 0` against a `0` base; `TIP_LINKCHECK_TOTAL = 97` / `TIP_LINKCHECK_WORKING = 95` with the two classified `v0.9.7` tag-referencing records. CI half `77-CI-EVIDENCE.md`: `RUN_ID = 36430787178` with `JOB_COUNT = 12`, zero non-success jobs. Trial-merge half `77-PREFLIGHT-EVIDENCE.md`: `MERGE_TREE = d41a910e448f7205e395aaba0f1d1c6e642e6190`. |
| SC4 | MET | `77-ATT06-EVIDENCE.md`: `ROLLBACK_COMMIT_SHA = fe4e87638220ec8c7574f73050e336e0fe28110b`, and this document. |
| SC5 | observed at phase close; see § Phase-close observations at the end of this document | `77-CLOSEOUT-GUARD.md`: the phase-head digest `REQ_SHA256_BASE = 35eb6122efd878cad4083a18b84c006f315c3cfe5229f3d443e6c712e6954351`. |

The linkcheck reading carries two classified pre-tag records under the owner's 2026-09-20 reading
(the same shape the owner approved at Phase 75's close), and Step 11 below is where they close —
stated plainly here so it is not mistaken for an unqualified clean run.

## The tip this phase hands over

`PUSHED_SHA = df6357faf3d6ce93ac99bbfc3bdad58168a95a14` is the tree CI verified in
`RUN_ID = 36430787178`; local `HEAD` continues past it with `.planning/`-only commits, so the
branch is pushed again before Step 1 opens the pull request — the product tree is identical and
the tag must sit on a pushed merge commit.

## Publish-half sequence

The order below is load-bearing: tag → ATT-04 → ATT-03 → ATT-05 → DOC-25 is fixed by the
requirements, ATT-05 must never precede an ATT-03 PASS because the token is the rollback path
until then, and DOC-25 must never precede ATT-05 because it describes the post-ATT-05 state. Every
step has three lines — `**Owner:**`, `**Ordering:**`, `**On failure here:**` — and every
`**On failure here:**` line names a subsection of `## Rollback procedure (ATT-06)` by its exact
heading (D-04). All commands write under `/tmp/p77close/`.

### Step 1 — Merge the milestone branch to main

**Owner:** `/gsd-complete-milestone`.
**Ordering:** first; nothing irreversible has happened yet.

Push the branch again: `git push --no-follow-tags origin gsd/v0.9.7-trusted-publishing-and-release`.
Confirm with `git branch --list 'gsd/v0.9.7*'` and
`git ls-remote --heads origin 'refs/heads/gsd/v0.9.7*'` that only the canonical branch exists — the
GSD commit helper has created a `gsd/v0.9.7-milestone` decoy in past milestones; the pull request's
head is the canonical branch only. Re-read `origin/main` live with `git fetch origin main` and
`git merge-base HEAD origin/main` against `git rev-parse origin/main` — this phase's reading
(`ORIGIN_MAIN_SHA = eeba55aa9b62aecb208bf7abecb051b476592b66`, `MAIN_MOVED = yes`,
`MAIN_MOVED_FILES = uv.lock`, a clean trial merge at
`MERGE_TREE = d41a910e448f7205e395aaba0f1d1c6e642e6190` with ruff
`MERGED_RUFF_VERSION = 0.16.9`) is context, not permission. Because strict is
`PROTECTION_STRICT = true`, when `origin/main` has moved run `git merge --no-ff origin/main` into
the branch, then `uv lock --check`, `uv run ruff check .`, `uv run black --check .`, push, and a
green CI run on the merged tip before merging; after that merge, re-check that the `uv.lock`
package-name set still matches the `v0.9.6` tag's (this phase's reading:
`MERGED_PACKAGE_SET_MATCHES_V096 = yes`), so the `### Verified` "no new dependency" sentence stays
true. Name every required context from `PROTECTION_CONTEXTS` verbatim: `Build Package`,
`Code Coverage`, `Lint and Format Check`, `Test Python 3.12 on ubuntu-latest`,
`Test Python 3.13 on ubuntu-latest`, `Type Check`. The merge lands as a real merge commit
(`MERGE_PRECEDENT_HITS = 111` first-parent precedents). Before opening the pull request, confirm
the fence's third observation (§ "Before and after phase.complete-family tooling") reads MATCH on
the guarded-region digest. Record `MERGE_SHA`.

**On failure here:** § Rollback procedure (ATT-06) › R0 — Before the tag exists.

### Step 2 — Push the v0.9.7 tag

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after Step 1; the first irreversible act — every `v*` tag push reaches production
PyPI and there is no dry-run path.

Re-confirm no `v0.9.7` tag exists: `git tag -l 'v0.9.7'` empty,
`git ls-remote --tags origin > /tmp/p77close/tags-before.txt` without `refs/tags/v0.9.7`, the
`v0.9.6` control present. Then `git tag -a v0.9.7 <MERGE_SHA> -m "Release v0.9.7"` and
`git push origin v0.9.7`. Then
`gh run list --workflow=release.yml --limit 5 --json databaseId,event,headBranch,status > /tmp/p77close/release-runs.json`
and record `RELEASE_RUN_ID` as the `push` run on `headBranch` `v0.9.7`.

**On failure here:** a rejected tag push routes to § Rollback procedure (ATT-06) › R0 — Before the
tag exists; a release run that fails before any file lands routes to § Rollback procedure
(ATT-06) › Failure shapes, then § Rollback procedure (ATT-06) › R1 — Same-run re-run (shape 1).

### Step 3 — Approve the pypi environment and let the release run finish

**Owner:** the project owner approves; `/gsd-complete-milestone` waits.
**Ordering:** after Step 2.

The `pypi` environment requires a reviewer and then a 15-minute wait timer (measured this phase) —
waiting there is an expected gate, not a failure, and the approval is never given by an agent
through the API. Wait in bounded foreground calls until the run completes. Expected job
conclusions: `Validate Release`, `Build Distribution`, `Publish to PyPI` and
`Create GitHub Release` success; `Publish to TestPyPI (Optional)` skipped (its `if:` matches only
`alpha`, `beta` or `rc`). Record every job's conclusion.

**On failure here:** § Rollback procedure (ATT-06) › Failure shapes — classify with its
exact-filename count, then R1, R2 or R3.

### Step 4 — ATT-04: the release run log

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after Step 3 completes.

Commands: `gh run view <RELEASE_RUN_ID> --json attempt` to read the attempt that published, then
`LC_ALL=C gh run view <RELEASE_RUN_ID> --attempt <N> --log > /tmp/p77close/release.log`, then
`LC_ALL=C grep -c 'disabling Trusted Publishing' /tmp/p77close/release.log` and
`LC_ALL=C grep -c 'attestations input is ignored' /tmp/p77close/release.log`, each expected `0`.

Control, re-run live at the close: the same two greps over
`LC_ALL=C gh run view 35730551619 --log > /tmp/p77close/control.log` read
`CTRL_C_DISABLING_TP = 1` and `CTRL_C_ATTESTATIONS_IS_IGNORED = 1`. Corroboration:
`grep -c 'Generating and uploading digital attestations'` is expected at least 1 (the rehearsal
run `36321530105` read `CTRL_R_GENERATING = 1`; the control read 0).

State that this signal is necessary but not sufficient — the action decides it locally from the
presence of a credential before any network call — and that ATT-03 is what proves PyPI served
provenance.

Add the one Discretion A sentence: the requirement's literal phrase, `attestations input ignored`
— which lives only in the annotation's `title` attribute, a title attribute that
`gh run view --log` never prints (measured `CTRL_C_TITLE_PHRASE = 0` even on the control) — is
superseded by the two-grep pair above. `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` keep
their literal wording. Never write a grep command whose pattern is that title phrase.

Record the attempt number with both counts.

**On failure here:** a non-zero count means the release ran on the credential path and the upload
carries no attestations — § Rollback procedure (ATT-06) › R3 — Shape 3: HALT the close and fix
inside v0.9.7 (D-01).

### Step 5 — ATT-03(a): the PyPI Simple JSON API

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after Step 4.

Commands:
`curl -sf https://pypi.org/simple/typsphinx/ -H 'Accept: application/vnd.pypi.simple.v1+json' -o /tmp/p77close/simple.json`;
a `jq` listing of `filename` and `provenance | tostring` for files whose `filename` equals
`typsphinx-0.9.7-py3-none-any.whl` or `typsphinx-0.9.7.tar.gz`; and a second `jq` count of every
filename beginning `typsphinx-0.9.7`.

Expected: exactly two exact-name files, each `provenance` a non-null string equal to
`https://pypi.org/integrity/typsphinx/0.9.7/<filename>/provenance`, and a prefix count of 2.

Controls: 0.9.6's two files read `CTRL_V096_PROVENANCE = null,null`; an attested `pip` wheel reads
the URL string
`CTRL_PIP_WHEEL_PROVENANCE = https://pypi.org/integrity/pip/26.2.1/pip-26.2.1-py3-none-any.whl/provenance`
(type `CTRL_PIP_PROVENANCE_TYPE = string`) — so the check is non-null plus URL shape, never a
comparison with a boolean. The legacy `/pypi/typsphinx/0.9.7/json` endpoint never carries this
field and does not count.

If zero 0.9.7 files are listed while Step 3 recorded `Publish to PyPI` success, re-read every
60 seconds for up to 10 minutes before classifying (the Simple API can serve a cached listing).

**On failure here:** one exact-name file is shape 2 → § Rollback procedure (ATT-06) › R2 — Leave
0.9.7: delete the tag and re-prep as 0.9.8 (D-02); two files with a null `provenance` is shape 3 →
§ Rollback procedure (ATT-06) › R3 — Shape 3: HALT the close and fix inside v0.9.7 (D-01); zero
files after the re-read window → § Rollback procedure (ATT-06) › Failure shapes; a prefix count
above 2 → HALT.

### Step 6 — ATT-03(b): the PyPI Integrity API

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after Step 5 passes.

For each of the two filenames:
`curl -s -o /tmp/p77close/int-<FILENAME>.json -w '%{http_code}\n' https://pypi.org/integrity/typsphinx/0.9.7/<FILENAME>/provenance`,
expected `200`; then `jq '.attestation_bundles | length'` read before indexing, expected `1` (the
`pip` control read `CTRL_INTEGRITY_PIP_BUNDLES = 1`; any other count HALTs for investigation);
then
`jq -r '.attestation_bundles[0].publisher | [.kind, .repository, .workflow, .environment] | join("|")'`,
expected exactly `GitHub|YuSabo90002/typsphinx|release.yml|pypi`.

Controls: the 0.9.6 wheel's Integrity URL read `CTRL_INTEGRITY_V096_WHEEL_HTTP = 404` and its
sdist `CTRL_INTEGRITY_V096_SDIST_HTTP = 404`; `pip` read `CTRL_INTEGRITY_PIP_HTTP = 200` with
publisher `CTRL_INTEGRITY_PIP_PUBLISHER = GitHub|pypa/pip|release.yml|pypi`.

ATT-03 passes only when Steps 5 and 6 both pass for both files; record `ATT03_VERDICT = PASS` in
the close's evidence only then. Any non-200 status, a wrong bundle count or a publisher mismatch
fails it.

**On failure here:** § Rollback procedure (ATT-06) › R3 — Shape 3: HALT the close and fix inside
v0.9.7 (D-01).

### Step 7 — ATT-05: retire PYPI_API_TOKEN, only after ATT-03 passes

**Owner:** `/gsd-complete-milestone` for the two GitHub deletions; the project owner for the PyPI
revocation.
**Ordering:** strictly after Steps 5 and 6 have both recorded PASS; never on shape 3 (D-01) —
until ATT-03 passes the token is the rollback path.

Commands: list every scope by name before —
`gh secret list --json name --jq '.[].name' > /tmp/p77close/secrets-repo-before.txt`, the same
with `--env pypi` and `--env testpypi` (expected this phase:
`CTRL_REPO_SECRETS = PYPI_API_TOKEN|TEST_PYPI_API_TOKEN`, `CTRL_ENV_PYPI_SECRETS = PYPI_API_TOKEN`,
`CTRL_ENV_TESTPYPI_SECRETS = none`); then `gh secret delete PYPI_API_TOKEN` and
`gh secret delete PYPI_API_TOKEN --env pypi` — two distinct secrets; then the same three listings
after, expecting `PYPI_API_TOKEN` gone from the repository and `pypi` scopes and
`TEST_PYPI_API_TOKEN` still present at every scope that listed it before (measured this phase:
`TEST_PYPI_API_TOKEN_SCOPES = repository`).

The third leg is the owner revoking the token on PyPI's own token-management page (account
settings, API tokens); no API can observe it, so the owner states it was done and the close
records that statement. Never print a secret value.

This step runs only after Step 5 and Step 6 have both recorded PASS.

**On failure here:** a failed deletion is repeated and every scope re-listed — § Rollback
procedure (ATT-06) › Failures that are not rollback shapes; if ATT-03 has not passed, this step is
not run — § Rollback procedure (ATT-06) › R3 — Shape 3: HALT the close and fix inside v0.9.7
(D-01).

### Step 8 — DOC-25: correct INTEGRATIONS.md, only after ATT-05

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after all three legs of Step 7 are complete, so the line describes a state that is
already true.

Commands: re-measure with `grep -n 'PYPI_API_TOKEN' .planning/codebase/INTEGRATIONS.md` (this
phase: the target at line `DOC25_TARGET_LINE = 116`, the `TEST_PYPI_API_TOKEN` line at
`DOC25_KEEP_LINE = 117`, which stays), then replace only the target line with the pre-drafted text
written here in a fenced block:

```
- `PYPI_API_TOKEN` - retired: `release.yml`'s `publish-pypi` job now publishes through PyPI Trusted
  Publishing (GitHub OIDC, environment `pypi`, PEP 740 attestations); no PyPI API token is stored.
  The former `PYPI_API_TOKEN` was deleted at repository and `pypi`-environment scope and revoked on
  PyPI at the v0.9.7 close (Step 7).
```

State that the draft is rewritten to what Step 7 actually observed if that differs.

**On failure here:** § Rollback procedure (ATT-06) › Failures that are not rollback shapes; if
Step 7 is incomplete this step is not run — § Rollback procedure (ATT-06) › R3 — Shape 3: HALT the
close and fix inside v0.9.7 (D-01).

### Step 9 — Advance the translations pin and tag the translations repository

**Owner:** human plus `/gsd-complete-milestone`.
**Ordering:** after Step 8.

The dispatch is **manual** and does not happen as a side effect of this repository's tag push (a
daily schedule also exists, but the close does not wait for it):
`gh workflow run update-pin.yml -R YuSabo90002/typsphinx-doc-translations`, then
`gh run list -R YuSabo90002/typsphinx-doc-translations --workflow update-pin.yml --limit 3 --json databaseId,status,conclusion > /tmp/p77close/pin-runs.json`,
then confirm the submodule pin with
`gh api repos/YuSabo90002/typsphinx-doc-translations/contents/typsphinx --jq .sha` equals
`<MERGE_SHA>` (this phase: `CTRL_TRANSLATIONS_PIN = 9fa1cb894137933f4dbb49d1668fc193e2ef1bc8`).
Then tag that repository `v0.9.7` as an annotated tag on its resulting commit, as `v0.9.6` was
(`CTRL_TRANSLATIONS_V096_TAG_TYPE = tag`) — a separate action.

**On failure here:** § Rollback procedure (ATT-06) › Failures that are not rollback shapes.

### Step 10 — Read the Docs stable on en and ja, cache-busted

**Owner:** human, via the unauthenticated public API and real fetches.
**Ordering:** after Step 9.

Commands: `curl -s https://readthedocs.org/api/v3/projects/typsphinx/versions/stable/ -o /tmp/p77close/rtd-en.json`
and the `typsphinx-ja` equivalent, read with `jq -r .identifier`; expected the `en` identifier to
be `<MERGE_SHA>` and the `ja` identifier the translations repository's `v0.9.7` commit (this
phase: `CTRL_RTD_EN_IDENTIFIER = 6fcc5adb02f5eefffd88ecda5258dca842d1acaa`,
`CTRL_RTD_JA_IDENTIFIER = 158fa1c4a29376478e62c02bce72abf06750455a`). Then fetch
`https://typsphinx.readthedocs.io/en/stable/?cb=<any fresh number>` and the `ja` page the same
way, expecting `typsphinx 0.9.7` (this phase's pre-close control read
`CTRL_RTD_EN_VERSION = 0.9.6` / `CTRL_RTD_JA_VERSION = 0.9.6`, since 0.9.7 was not yet released).
A stale page is a cached response until a cache-busted fetch says otherwise — the `ja` page served
a stale version from cache at the v0.9.6 close. No Default Version setting change is expected.

**On failure here:** § Rollback procedure (ATT-06) › Failures that are not rollback shapes.

### Step 11 — REL-17: the tag, the upload, the GitHub Release and the linkcheck obligation

**Owner:** `/gsd-complete-milestone`.
**Ordering:** after Step 10, reading evidence the earlier steps produced.

Checks: `git ls-remote --tags origin` lists `refs/tags/v0.9.7`; Step 5's two files are live;
`gh release view v0.9.7 --json body --jq .body > /tmp/p77close/body.md` and
`uv run python scripts/extract_changelog_section.py 0.9.7 > /tmp/p77close/notes.md`, then
`head -n <EXTRACT_LINES> /tmp/p77close/body.md | diff - /tmp/p77close/notes.md` prints nothing
(inline `EXTRACT_LINES = 50`, `EXTRACT_BYTES = 3132` and
`EXTRACT_SHA256 = 82f27b346b89163e08e6f64ba7b119c3fcc4ab20d300d06f6cf94d86a96983f6`; the same
comparison matched on v0.9.6: `CTRL_RELEASE_BODY_PREFIX_MATCH = yes`, 100 lines); the body carries
no scratch-block heading; the Release carries the wheel and the sdist. The `## [0.9.7]` heading
date (`RELEASE_HEADING_DATE = 2026-09-28`) is the prep date and is **not rewritten** if the tag
lands later.

Then the linkcheck obligation: with the tag and the Release existing, `rm -rf docs/_build` and
`tox -e linkcheck` must now report the two records classified in this phase as `working` —
`https://github.com/YuSabo90002/typsphinx/compare/v0.9.7...HEAD` and
`https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.7` (`TIP_LINKCHECK_NONWORKING_URIS`);
if either is still broken, investigate it as a regression and do not re-amend the reading.

**On failure here:** a failed `Create GitHub Release` job or a body mismatch is § Rollback
procedure (ATT-06) › Failures that are not rollback shapes — re-run that job, never re-tag.

### Step 12 — The operator checks the five fenced checkboxes

**Owner:** `/gsd-complete-milestone`, by hand.
**Ordering:** last.

Each checkbox and its traceability row flip only against its own observations: ATT-04 against
Step 4; ATT-03 against Steps 5 and 6 and the recorded `ATT03_VERDICT = PASS`; ATT-05 against
Step 7's before-and-after listings and the owner's revocation statement; DOC-25 against Step 8's
edited line; REL-17 against Steps 2, 5 and 11. Phase-completion tooling has flipped a deferred
release checkbox at 9 of the 10 prior release-prep closes; these flips are the operator's own.

**On failure here:** leave the box unchecked and HALT — § Rollback procedure (ATT-06) › What never
happens on any branch.

## Recorded without acting

Quoted from `77-PREFLIGHT-EVIDENCE.md`: `OPEN_PRS = 1`, `DEPENDABOT_OPEN_PRS = 1`,
`OPEN_PR_NUMBERS = 157`, `PR_CENSUS_AT = 2026-09-28T13:28:46Z`.

Live re-read, taken during this task's own execution:

```
$ gh pr list --state open --json number --jq 'length'
1
```

HANDOFF_OPEN_PRS_LIVE = 1
HANDOFF_OPEN_PRS_AT = 2026-09-28T14:05:19Z

The live count agrees with the earlier census — no drift between that census and this task's own
moment.

The ordering rule, stated conditionally: any Dependabot pull request open at release time is
ordered after the milestone pull request (the v0.9.3 precedent), and one merging into `origin/main`
first is exactly why Step 1 re-reads `origin/main` live.

Also quoted: `MAIN_MOVED = yes`, `MAIN_MOVED_FILES = uv.lock` — `origin/main` had already moved
past the milestone base by three Dependabot merges before this phase's own preflight reading,
which is why Step 1 re-reads it live rather than trusting this recorded value.
`MERGED_PACKAGE_SET_MATCHES_V096 = yes` — the merged tree's `uv.lock` package-name set is
identical to the `v0.9.6` tag's, so the `### Verified` "no new dependency" CHANGELOG sentence
survives the Step 1 merge unchanged.

## Deferred with this phase

- **NUM-01** — disclosed again in `## [0.9.7]`'s `### Known Limitations`, not fixed; its todo
  (`2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md`) stays
  pending.
- **QUA-08** — the weekly advisory linkcheck workflow, still Future; its todo
  (`2026-07-22-add-sphinx-linkcheck-ci-job.md`) stays pending.
- **WR-02**, **WR-03** and **LNK-01** — still Future.
- The two todos above were reviewed at discussion time and not folded into this phase.

## Before and after phase.complete-family tooling

Reproduced inline from `77-CLOSEOUT-GUARD.md` so no second file need be open.

```bash
sha256sum .planning/REQUIREMENTS.md
# compare against REQ_SHA256_BASE: 35eb6122efd878cad4083a18b84c006f315c3cfe5229f3d443e6c712e6954351

wc -l .planning/REQUIREMENTS.md
# compare against REQ_LINES_BASE: 189

git diff --name-only -- .planning/REQUIREMENTS.md
# expected: no output

grep -vE '^- \[.\] \*\*ATT-06\*\*|^\| ATT-06 \|' .planning/REQUIREMENTS.md | sha256sum
# compare against REQ_SHA256_GUARDED_BASE: fce6cc7d403e4c68b4cf12a6e58bf990f94f9a5f7db2943ce9da2469953d4af5
```

The five `grep -n` transcripts, pasted verbatim, expected unchanged:

```
$ grep -n 'ATT-03' .planning/REQUIREMENTS.md
37:- [ ] **ATT-03**: The switch is proven on **PyPI's own served state** for the real 0.9.7 upload, not
51:      so its absence alone does not prove PyPI served provenance. ATT-03 is what proves that.
55:      ATT-03 passes**; until then the token is the rollback path. `TEST_PYPI_API_TOKEN` is left in
162:| ATT-03 | Phase 77 | publish (coverage only) | Pending |
183:→ ATT-03 (PyPI Simple JSON + Integrity APIs) → ATT-05 (both secret scopes + PyPI revocation, and
184:only once ATT-03 has passed) → DOC-25 (written after ATT-05, so it describes a state that is
```

```
$ grep -n 'ATT-04' .planning/REQUIREMENTS.md
47:- [ ] **ATT-04**: The v0.9.7 release run carries **zero** occurrences of the action's
161:| ATT-04 | Phase 77 | publish (coverage only) | Pending |
182:The publish half runs in a fixed order that `77-HANDOFF.md` enforces: tag push → ATT-04 (run log)
```

```
$ grep -n 'ATT-05' .planning/REQUIREMENTS.md
52:- [ ] **ATT-05**: `PYPI_API_TOKEN` is retired from **both** GitHub scopes — the repository-scoped
86:      ATT-01 and ATT-05 land.
163:| ATT-05 | Phase 77 | publish (coverage only) | Pending |
183:→ ATT-03 (PyPI Simple JSON + Integrity APIs) → ATT-05 (both secret scopes + PyPI revocation, and
184:only once ATT-03 has passed) → DOC-25 (written after ATT-05, so it describes a state that is
```

```
$ grep -n 'REL-17' .planning/REQUIREMENTS.md
75:- [ ] **REL-17**: 0.9.7 is published — `pyproject.toml` bumped as the **sole** version literal with
160:| REL-17 | Phase 77 | split — prep in phase, publish at close | Pending |
185:already true). REL-17's publish clauses are checked across the whole of it.
```

```
$ grep -n 'DOC-25' .planning/REQUIREMENTS.md
84:- [ ] **DOC-25**: `.planning/codebase/INTEGRATIONS.md:116-117` no longer describes `PYPI_API_TOKEN`
164:| DOC-25 | Phase 77 | publish (coverage only) | Pending |
184:only once ATT-03 has passed) → DOC-25 (written after ATT-05, so it describes a state that is
```

**ATT-06's lines — expected to move.** `- [ ] **ATT-06**` (line 57) and
`| ATT-06 | Phase 77 | pre-tag | Pending |` (line 159) are **not** part of this guard — ATT-06
closes inside this phase, so both may legitimately read `[x]` / `Complete` once phase-completion
tooling runs.

**The third observation.** `phase.complete`-family tooling, including `/gsd-verify-work`'s inline
transition and `/gsd-execute-phase`'s own `phase.complete` step, is what actually catches the
flip — take this observation only after one of those has run. Copy `.planning/REQUIREMENTS.md`,
`.planning/ROADMAP.md` and `.planning/STATE.md` to a fresh `mktemp -d` immediately before that
tooling runs, since `ROADMAP.md` and `STATE.md` change legitimately throughout execution.

**Line-scoped reversion recipe.** If the guarded-region digest differs from
`REQ_SHA256_GUARDED_BASE`: `git checkout -- .planning/REQUIREMENTS.md`; if ATT-06's checkbox and
row had also flipped to `[x]` / `Complete`, re-apply only those two lines by an in-place edit;
re-run the probes until the guarded-region digest MATCHes; report; never commit a flipped guarded
line (one of ATT-03, ATT-04, ATT-05, REL-17 or DOC-25).

**Phase-head backup paths:** `BACKUP_ROADMAP = /tmp/p7701.p8Y5y6/p7701_ROADMAP.md`,
`BACKUP_STATE = /tmp/p7701.p8Y5y6/p7701_STATE.md`.

## Rollback procedure (ATT-06)

### Measured basis

Anchors in `.github/workflows/release.yml`, cited as `release.yml:<N>` and re-measured at this
phase's own base (`BASE_77_03`, see `77-ATT06-EVIDENCE.md`):

- `publish-pypi:` at `release.yml:127` runs `needs: build` (`release.yml:129`) with **no `if:`**
  anywhere in the job (`release.yml:127`–`142`) — so every `v*` tag that reaches this job reaches
  production PyPI, and there is no dry-run path.
- `build:` (`release.yml:93`) uploads `dist-packages` and keeps it for `retention-days: 7`
  (`release.yml:124`) — the window R1's same-run re-run depends on.
- `create-release:` at `release.yml:145` needs `[build, publish-pypi]` (`release.yml:147`) with
  **no `if:`** override — so a failed `publish-pypi` leaves `create-release` *skipped*, no GitHub
  Release is created, and the tag itself is not consumed.
- The `pypi` GitHub Environment (`release.yml:131`–`132`) requires a reviewer and carries a
  15-minute wait timer before `publish-pypi` can run — an expected gate, not a failure.
- The `- name: Publish to PyPI` step is `release.yml:141`; its
  `uses: pypa/gh-action-pypi-publish@release/v1` line is `release.yml:142` (the first of two hits
  in the file; the second belongs to `publish-testpypi`).
- **PyPI permanently refuses a re-uploaded filename, whatever the git-tag state.** This is why this
  section exists before the tag does: once a filename lands, no tag manipulation can make PyPI
  accept it again under the same name.

### Failure shapes

| Shape | What happened | Path |
|---|---|---|
| ① pre-upload rejection — `invalid-publisher` / `invalid-pending-publisher`, or any failure before a file lands | nothing on PyPI | fix the registration → R1, then R2 if R1 cannot succeed |
| ② partial upload (e.g. wheel landed, sdist failed) | one 0.9.7 filename consumed | R2 |
| ③ upload succeeded but ATT-03 fails | 0.9.7 is live and cannot be retried under this name | R3 |

The one discriminating reading, written as two commands:

```
curl -sf https://pypi.org/simple/typsphinx/ -H 'Accept: application/vnd.pypi.simple.v1+json' -o /tmp/p77close/simple.json
jq '[.files[] | select(.filename == "typsphinx-0.9.7-py3-none-any.whl" or .filename == "typsphinx-0.9.7.tar.gz")] | length' /tmp/p77close/simple.json > /tmp/p77close/v097_count.txt
cat /tmp/p77close/v097_count.txt
```

Classification rule, read against the `Publish to PyPI` job's own conclusion:

- **0** files with a failed `Publish to PyPI` job (or an earlier failed job) → shape ① → **R1**.
- **exactly 1** file → shape ② → **R2**.
- **2** files with ATT-03 failing → shape ③ → **R3**.
- **2** files with ATT-03 passing → no rollback needed.
- **0** files while `Publish to PyPI` concluded `success` → not classified yet. The Simple API can
  serve a cached listing; re-read every 60 seconds for up to 10 minutes, and HALT to investigate if
  it is still 0 after that window.

A second count catches anything unexpected:

```
jq '[.files[] | select(.filename | startswith("typsphinx-0.9.7"))] | length' /tmp/p77close/simple.json > /tmp/p77close/v097_any_count.txt
cat /tmp/p77close/v097_any_count.txt
```

A count above 2 HALTs — a third `typsphinx-0.9.7*` artifact is not a shape this procedure accounts
for.

### Default recovery order

1. **R1** — the same-run re-run, tried first, inside the 7-day artifact retention window.
2. Otherwise **R2** — tag deletion and re-prep as 0.9.8, still without the credential.
3. **R4** only on the owner's explicit statement, which lands the close in R3's state.

Never skip ahead of this order.

### R0 — Before the tag exists

A failure at the merge step, or at any pre-tag re-read, changes nothing irreversible: fix it and
retry in place. Nothing below this point applies until the `v0.9.7` tag has actually been pushed.

### R1 — Same-run re-run (shape 1)

Record the run's failing lines:

```
gh run view <RELEASE_RUN_ID> --log-failed > /tmp/p77close/failed.log
cat /tmp/p77close/failed.log
```

The owner fixes the cause. For a registration error, that means the Trusted Publisher entry in the
**existing** `typsphinx` project's Publishing settings on PyPI: owner `YuSabo90002`, repository
`typsphinx`, workflow `release.yml`, environment `pypi`.

Confirm the `build` artifact is still inside its retention window:

```
gh api repos/YuSabo90002/typsphinx/actions/runs/<RELEASE_RUN_ID>/artifacts --jq '.artifacts[] | [.name, (.expired|tostring), .expires_at] | @tsv' > /tmp/p77close/artifacts.txt
cat /tmp/p77close/artifacts.txt
```

Expect `dist-packages` with `false`. Then re-run the **same** run — never a new tag, never a new
`workflow_dispatch`:

```
gh run rerun <RELEASE_RUN_ID> --failed
gh run view <RELEASE_RUN_ID> --json headSha,attempt > /tmp/p77close/rerun_check.json
cat /tmp/p77close/rerun_check.json
```

Confirm the head SHA is unchanged and the attempt number rose. The owner approves the `pypi`
environment again; resume at the ATT-04 step, reading that new attempt.

If the artifact has expired, the cause needs a real code change, or the re-run fails again →
**R2**.

### R2 — Leave 0.9.7: delete the tag and re-prep as 0.9.8 (D-02)

The unconditional rule, stated as D-02 states it: leaving the same-run re-run always means 0.9.8,
never a re-tagged 0.9.7 — even when the Simple JSON API shows zero 0.9.7 files (shape ①). No
branching on whether any file was uploaded.

Record the Simple JSON response and the run's job table first (the same `simple.json` capture
above, plus):

```
gh run view <RELEASE_RUN_ID> --json jobs --jq '.jobs[] | "\(.name)\t\(.conclusion)"' > /tmp/p77close/job_table.txt
cat /tmp/p77close/job_table.txt
```

Delete the tag, locally and on `origin`:

```
git tag -d v0.9.7
git push origin --delete v0.9.7
```

Verify the deletion:

```
git tag -l 'v0.9.7' > /tmp/p77close/local_tag_check.txt
cat /tmp/p77close/local_tag_check.txt
git ls-remote --tags origin > /tmp/p77close/tags.txt
cat /tmp/p77close/tags.txt
gh release list > /tmp/p77close/release_list.txt
cat /tmp/p77close/release_list.txt
```

`local_tag_check.txt` must be empty; `tags.txt` must list no `refs/tags/v0.9.7` while still
listing `refs/tags/v0.9.6`; `release_list.txt` must show no `v0.9.7` release.

Then re-run release prep as 0.9.8: `pyproject.toml` to `0.9.8` with `uv lock`, `README.md`'s
Status line, the `## [0.9.7]` heading rewritten to `## [0.9.8]` dated at the new prep, the tail
links moved to `[0.9.8]` and a `v0.9.8` compare base, `tests/test_changelog_page_gate.py`'s
`RELEASE_VERSIONS` gaining `"0.9.8"` in place of `"0.9.7"`, the provenance wording revisited in
that prep rather than patched afterwards, and the green-tree proof and one CI dispatch re-taken —
still with no credential in the workflow (D-03). Publish 0.9.8 through this same handoff, with
every 0.9.7 reading in it read as 0.9.8. 0.9.7 then joins 0.9.1 and 0.9.3–0.9.5 as unclaimed. No
`password:` is added at any point in this path.

**Rating: one-way** — a pushed-then-deleted tag with no release would be a first in this
repository, and is visible to anyone who already fetched it.

### R3 — Shape 3: HALT the close and fix inside v0.9.7 (D-01)

Record, before anything else:

- The Simple JSON response, already at `/tmp/p77close/simple.json`.
- Both Integrity API responses, status and body, one file at a time:

```
curl -s -o /tmp/p77close/int-<FILENAME>.json -w '%{http_code}\n' https://pypi.org/integrity/typsphinx/0.9.7/<FILENAME>/provenance > /tmp/p77close/int-<FILENAME>.status
cat /tmp/p77close/int-<FILENAME>.status
cat /tmp/p77close/int-<FILENAME>.json
```

- The `Publish to PyPI` job's log:

```
gh run view <RELEASE_RUN_ID> --json jobs --jq '.jobs[] | select(.name == "Publish to PyPI") | .databaseId' > /tmp/p77close/publish_job_id.txt
cat /tmp/p77close/publish_job_id.txt
gh run view --job <PUBLISH_JOB_ID> --log > /tmp/p77close/publish.log
```

Do **not** run the ATT-05 step — the token stays the rollback path. Do **not** run the DOC-25
step, which would describe a state that is not true. Suspend `/gsd-complete-milestone`;
investigate; insert a decimal phase (for example `77.1`) into v0.9.7 to fix the cause; re-prove
ATT-03 on **0.9.8** in the same milestone.

0.9.7 is **not** yanked: missing provenance is not a user-facing defect. The five fenced
checkboxes stay `[ ]` throughout.

**Rating: one-way** — by the time this branch is taken 0.9.7 is permanently on PyPI; this decision
governs only what the close does next.

### R4 — Last resort: restore the token credential (D-03, owner-gated)

**The gate first.** This subsection is reached only when the owner explicitly states that "Trusted Publishing is being abandoned for this release" — never a default step, never inferred from a failure alone.

**Why it is last.** With an explicit `password:` the publish action turns Trusted Publishing off
and ignores its `attestations` input, so ATT-03 fails by construction. This path ships the
release, but it lands the milestone in R3's state — no ATT-05, no DOC-25, close suspended.

**The restore**, copied byte-for-byte from `git show efde71a9` (indentation included), to be
inserted directly after the `uses: pypa/gh-action-pypi-publish@release/v1` line of the
`- name: Publish to PyPI` step — `release.yml:142` at this phase; re-measure with
`grep -n 'uses: pypa/gh-action-pypi-publish@release/v1' .github/workflows/release.yml` before
using it, whose first hit is the PyPI step and second hit is the TestPyPI step:

```yaml
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

A same-run re-run replays the run's original commit, so a restored credential takes effect only on
a **new** tag — 0.9.8 under R2. `gh run view <id> --json headSha` shows which commit actually ran.

**Rating: costly** — a token-path upload is permanent and carries no provenance for that version.

### Failures that are not rollback shapes

After a successful upload, none of the following touches PyPI and none of them is a rollback
shape:

- A failed `Create GitHub Release` job is re-run alone, never by re-tagging:

```
gh run view <RELEASE_RUN_ID> --json jobs --jq '.jobs[] | select(.name == "Create GitHub Release") | .databaseId' > /tmp/p77close/release_job_id.txt
cat /tmp/p77close/release_job_id.txt
gh run rerun <RELEASE_RUN_ID> --job <JOB_ID>
```

- A failed secret deletion is repeated, and both scopes are listed again.
- A failed DOC-25 edit is redone.
- A failed `update-pin.yml` run is dispatched again.
- A stale Read the Docs page is re-fetched cache-busted, or waited out.

### What never happens on any branch

- No re-tagged 0.9.7 once the same-run re-run is left (D-02).
- No yank of 0.9.7 (D-01).
- No restored credential without the owner's explicit statement (D-03).
- No ATT-05 and no DOC-25 before ATT-03 passes (D-01).
- None of the five fenced checkboxes checked by tooling, or on an unobserved reading.
- No key added to the workflow in place of the deleted credential (ROADMAP constraint 9).

Every ordered step of the publish-half sequence names the subsection above that applies when it
fails (D-04).

---
*Phase: 77-v0-9-7-release-prep-prep-only-and-the-trusted-publishing-proof-handoff*
*Plan: 03*

## Phase-close observations

Recorded by `77-08`, after every other plan of this phase had run — the second of the three
observations named in `77-CLOSEOUT-GUARD.md` § "Re-verification protocol (phase close)".

The fence held: `FENCE_CLOSE_VERDICT = MATCH`. Re-run at phase close, the full digest of
`.planning/REQUIREMENTS.md` read `REQ_SHA256_CLOSE = 35eb6122efd878cad4083a18b84c006f315c3cfe5229f3d443e6c712e6954351`
and the guarded-region digest (ATT-06's two lines excluded) read
`REQ_SHA256_GUARDED_CLOSE = fce6cc7d403e4c68b4cf12a6e58bf990f94f9a5f7db2943ce9da2469953d4af5` —
both byte-identical to the phase-head baseline recorded in `77-CLOSEOUT-GUARD.md`. Each of the five
fenced checkboxes (ATT-03, ATT-04, ATT-05, REL-17, DOC-25) still reads `- [ ]` and each traceability
row still ends `Pending |`, read directly out of the file.

Probe observation 2 of 2 ran at `OBS2_AT = 2026-09-28T14:12:55Z`, repeating every observation-1
probe: no `v0.9.7` tag exists locally or on `origin` (the `v0.9.6` control still present), zero
`typsphinx-0.9.7*` files are listed on PyPI's Simple JSON API (both `typsphinx-0.9.6` files still
present as the control), no `v0.9.7` GitHub Release exists (`v0.9.6` is still the latest), no
`release.yml` run has happened since the Phase 76 rehearsal, `PYPI_API_TOKEN` is present at both the
repository and the `pypi`-environment scope with `TEST_PYPI_API_TOKEN` still present at repository
scope, and no pull request of any state exists against the milestone branch. The two observations
are separated by the bump commit, the rollback-section commit, the local green-tree runs, the trial
merge, the push and dispatched CI run, and the handoff commits themselves — recorded work, not
wall-clock luck.

The scope fence held with controls: `PHASE_PRODUCT_DIFF = CHANGELOG.md|README.md|pyproject.toml|tests/test_changelog_page_gate.py|uv.lock`
and nothing else changed outside `.planning/` over the phase — zero changes under `typsphinx/`,
`.github/`, `docs/source/` and `.planning/codebase/`, each pathspec proven to resolve by a
milestone-range or tracked-file control. `POST_DISPATCH_PRODUCT_FILES = 0` — no product file changed
after the tip CI actually tested (`PUSHED_SHA = df6357faf3d6ce93ac99bbfc3bdad58168a95a14`,
`RUN_ID = 36430787178`).

SC5 reads MET on both digests, both probe observations and the scope fence with its controls. The
third observation — after `phase.complete`-family tooling has actually run, the observation that
has historically caught the flip — belongs to the operator running that tooling, per
`77-CLOSEOUT-GUARD.md` § "Handoff to the third observation"; it is documented there, not taken by
any plan.
