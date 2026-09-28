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
