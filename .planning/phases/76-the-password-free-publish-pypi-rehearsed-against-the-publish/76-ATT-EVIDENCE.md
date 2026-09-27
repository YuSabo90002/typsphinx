# Phase 76 — ATT-01 / ATT-02 Evidence (D-08)

## Provisioning (76-01)

Command: `date -u +%FT%TZ`
```
2026-09-27T12:06:57Z
```

Command: `pwd -P`
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-ad8d2fe09cccd1de5
```

Command: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
Exit code: 0

ATT01_BASE_SHA = e3c169d4e7b52d828f6ebe2b04e55513df49ddfc
Taken from `git rev-parse HEAD` before any edit in this plan.

## ATT-01 — measurement at the phase base

Re-measured rather than trusted from ROADMAP.md, REQUIREMENTS.md, or 76-CONTEXT.md — each has been
wrong about this file's line numbers once.

Command: `grep -nF 'secrets.PYPI_API_TOKEN' .github/workflows/release.yml`
```
144:          password: ${{ secrets.PYPI_API_TOKEN }}
```
Exactly one line returned: P = 144.

Command: `sed -n '141,144p' .github/workflows/release.yml`
```
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```
Confirmed: line P-1 (143) is exactly eight spaces plus `with:`; line P-2 (142) is exactly eight
spaces plus `uses: pypa/gh-action-pypi-publish@release/v1`; line P-3 (141) is exactly six spaces
plus `- name: Publish to PyPI`. The measured shape matches the plan's expected shape exactly — no
HALT needed.

ATT01_DELETED_WITH_LINE = 143
ATT01_DELETED_PASSWORD_LINE = 144

Command: `sed -n '141,146p' .github/workflows/release.yml` (lines P-3 through P+2, quoted verbatim)
```
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}

  # Create GitHub Release
```

Command: `grep -c 'PYPI_API_TOKEN' .github/workflows/release.yml`
```
2
```
ATT01_PYPI_API_TOKEN_COUNT_BASE = 2

The 2 count is the production credential line (`:144`) plus the `TEST_PYPI_API_TOKEN` line in
`publish-testpypi` (`:244`), which contains the `PYPI_API_TOKEN` substring.

ROADMAP.md's stale `:141-144` citation would have deleted the `Publish to PyPI` step itself
(`- name:` and `uses:` lines included), publishing nothing. The measured deletion here is the two
lines `:143-144` only — `with:` and `password:` — leaving the step's name and action reference
intact.

## ATT-01 — the two-line deletion

Command: `sed -i '143,144d' .github/workflows/release.yml`

Nothing added: no replacement key, no comment, no blank line, no change anywhere else in the file.

Command: `git diff --numstat e3c169d4e7b52d828f6ebe2b04e55513df49ddfc -- .github/workflows/release.yml`
```
0	2	.github/workflows/release.yml
```
ATT01_DIFF_INSERTIONS = 0
ATT01_DIFF_DELETIONS = 2

Command: `git diff -U0 e3c169d4e7b52d828f6ebe2b04e55513df49ddfc -- .github/workflows/release.yml`
```
diff --git a/.github/workflows/release.yml b/.github/workflows/release.yml
index fedc843a..d01f4db4 100644
--- a/.github/workflows/release.yml
+++ b/.github/workflows/release.yml
@@ -143,2 +142,0 @@ jobs:
-        with:
-          password: ${{ secrets.PYPI_API_TOKEN }}
```

Command (structural parse — asserts the `publish-pypi` step list, the exact step mapping with no
`with` key, the `pypi` environment, the five job names, the top-level `permissions`, and the
untouched `publish-testpypi` credential mapping):
```
uv run python -c 'import yaml; d=yaml.safe_load(open(".github/workflows/release.yml")); j=d["jobs"]; s=j["publish-pypi"]["steps"]; assert [x["name"] for x in s]==["Download build artifacts","Publish to PyPI"], s; assert s[1]=={"name":"Publish to PyPI","uses":"pypa/gh-action-pypi-publish@release/v1"}, s[1]; assert j["publish-pypi"]["environment"]=={"name":"pypi","url":"https://pypi.org/p/typsphinx"}; assert sorted(j)==["build","create-release","publish-pypi","publish-testpypi","validate"], sorted(j); assert d["permissions"]=={"contents":"write","id-token":"write"}; t=j["publish-testpypi"]["steps"][-1]; assert t["with"]=={"password":"${{ secrets.TEST_PYPI_API_TOKEN }}","repository-url":"https://test.pypi.org/legacy/"}, t; print("YAML_STRUCT_OK")'
```
Output:
```
YAML_STRUCT_OK
```
ATT01_YAML_STRUCT = ok

## ATT-01 — SC #1 readout

Command: `grep -c 'PYPI_API_TOKEN' .github/workflows/release.yml`
```
1
```
ATT01_PYPI_API_TOKEN_COUNT_AFTER = 1

The one remaining hit is the `TEST_PYPI_API_TOKEN` line in `publish-testpypi`. Command:
`grep -n 'TEST_PYPI_API_TOKEN' .github/workflows/release.yml`
```
242:          password: ${{ secrets.TEST_PYPI_API_TOKEN }}
```

Command: `grep -c 'attestations' .github/workflows/release.yml || true`
```
0
```
ATT01_FORBIDDEN_KEY_A_COUNT_AFTER = 0
(Key A: "Adding `attestations: true` to the workflow" — REQUIREMENTS.md § Out of Scope.)

Command: `grep -c 'skip-existing' .github/workflows/release.yml || true`
```
0
```
ATT01_FORBIDDEN_KEY_B_COUNT_AFTER = 0
(Key B: "Adding `skip-existing:` to the workflow" — REQUIREMENTS.md § Out of Scope.)

Command: `grep -c 'pypa/gh-action-pypi-publish@release/v1' .github/workflows/release.yml`
```
2
```
ATT01_RELEASE_V1_COUNT_AFTER = 2

Command: `diff <(git show e3c169d4e7b52d828f6ebe2b04e55513df49ddfc:.github/workflows/release.yml | sed -n '/^  publish-testpypi:/,$p') <(sed -n '/^  publish-testpypi:/,$p' .github/workflows/release.yml)`
```
(no output — identical)
```
ATT01_TESTPYPI_REGION_IDENTICAL = yes

Command: `diff <(git show e3c169d4e7b52d828f6ebe2b04e55513df49ddfc:.github/workflows/release.yml | sed -n '/^permissions:/,/^$/p') <(sed -n '/^permissions:/,/^$/p' .github/workflows/release.yml)`
```
(no output — identical)
```
ATT01_PERMISSIONS_BLOCK_IDENTICAL = yes

Command: `grep -nF '  password: ${{ secrets.PYPI_API_TOKEN }}' .github/workflows/release.yml || true`
```
(no output — zero matches)
```
ATT01_REAPPLY_TARGETS = 0

The adjacency readout — command: `sed -n '141,145p' .github/workflows/release.yml` (five lines
starting at `ATT01_DELETED_WITH_LINE - 2` = 141):
```
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1

  # Create GitHub Release
  create-release:
```
Matches the expected shape: `- name: Publish to PyPI`, the `uses:` line, a blank line,
`  # Create GitHub Release`, and `  create-release:`.

## ATT-01 — env-not-interpolation invariant

Command (PyYAML walk over every `run:` step of every job, asserting none contains `${{`):
```
uv run python -c 'import yaml; d=yaml.safe_load(open(".github/workflows/release.yml")); r=[st["run"] for jb in d["jobs"].values() for st in jb["steps"] if "run" in st]; assert r, "no run steps"; bad=[x for x in r if "${{" in x]; assert not bad, bad; print(len(r))'
```
Output:
```
15
```
ATT01_RUN_STEPS_CHECKED = 15
ATT01_RUN_BLOCK_INTERPOLATIONS = 0

The deletion touched no `run:` block, so the invariant the file's own comment records (`:38-44`,
the `env:`-not-interpolation contract) is preserved by construction and is now also confirmed by
measurement across all 15 `run:` steps.

## ATT-01 verdict

Every key above holds:

ATT01_SC1_VERDICT = MET

The workflow file is not evidence on its own (ROADMAP constraint 10) — ATT-01 is closed together
with the wave-2 rehearsal in plan 76-03, which dispatches this exact copy of the file.

## ATT-02 pre-dispatch — provisioning

Command: `test -f .git`
```
(exit 0 — this is a worktree checkout)
```

Command: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`
Exit code: 0 (dev dependencies provisioned into this worktree's own `.venv`)

Command: `date -u +%FT%TZ`
```
2026-09-27T12:48:07Z
```

SCRATCH_76_03 = /tmp/p7603.oGoetI
BASE_76_03 = 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78
GH_ACTOR = YuSabo90002

## ATT-02 pre-dispatch — the pushed ref (D-06)

DISPATCH_REF = gsd/v0.9.7-trusted-publishing-and-release

Command: `git ls-remote origin refs/heads/gsd/v0.9.7-trusted-publishing-and-release`
```
987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78	refs/heads/gsd/v0.9.7-trusted-publishing-and-release
```
ORIGIN_REF_SHA = 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78

Command: `git fetch -q origin gsd/v0.9.7-trusted-publishing-and-release` — exit 0.

Measured at that SHA with `git show <SHA>:<path>`:

Command: `git show 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78:.github/workflows/release.yml | grep -c 'secrets.PYPI_API_TOKEN'` (`|| true` — zero is expected)
```
0
```
REF_PYPI_SECRET_REFS = 0

Command: `git show 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78:.github/workflows/release.yml | grep -c 'secrets.TEST_PYPI_API_TOKEN'`
```
1
```
REF_TESTPYPI_SECRET_REFS = 1
The control that the grep reads the right file.

Command: `git show 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78:typsphinx/translator.py | grep -cx 'from typsphinx.pathfmt import quote_path'`
```
1
```
REF_TRANSLATOR_QUOTE_PATH_IMPORT = 1

Command: `git show 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78:pyproject.toml | grep -m1 '^version = '`
```
version = "0.9.6"
```
REF_PYPROJECT_VERSION = 0.9.6

REF_ATT01_VERDICT = MET
Read from `ATT01_SC1_VERDICT` in this same file at that SHA.
REF_MSG06_VERDICT = MET
Read from `MSG06_SC5_VERDICT` in `76-MSG06-EVIDENCE.md` at that SHA.

Command: `git diff --name-only 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78 HEAD -- . ':(exclude).planning'`
```
(no output — empty)
```
WORKTREE_MATCHES_REF_OUTSIDE_PLANNING = yes

Command: `git ls-remote origin 'refs/heads/gsd/v0.9.7*' | wc -l`
```
1
```
ORIGIN_V097_BRANCHES = 1
No `-milestone` decoy on origin.

Command: `git ls-remote --tags origin 'refs/tags/v0.9.7*' | wc -l`
```
0
```
ORIGIN_V097_TAGS = 0

No mismatch — the pushed ref is ready; no HALT needed.

## ATT-02 pre-dispatch — validate-job checks CI does not run

`release.yml`'s `validate` job runs two release-only steps neither `ci.yml` job reproduces:
"Verify version matches pyproject.toml" and "Verify CHANGELOG has a section for this version"
(Pitfall 4 — `ci.yml` has no equivalent of either step; its `lint`/`type-check`/`test` jobs cover
the same underlying `tox` commands as `validate`'s test/lint/type steps, but not these two).

Command: `uv run python -c "import sys, importlib; tomllib = importlib.import_module('tomllib' if sys.version_info >= (3, 11) else 'tomli'); print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"`
```
0.9.6
```
VALIDATE_PYPROJECT_VERSION = 0.9.6

The tag input for the rehearsal dispatch is `v0.9.6`; stripped of its `v` that is `0.9.6`, which
equals `VALIDATE_PYPROJECT_VERSION`.
VALIDATE_VERSION_MATCH = yes

Command: `uv run python scripts/extract_changelog_section.py 0.9.6 > $SCRATCH_76_03/p7603_notes.md`
```
exit=0
```
VALIDATE_CHANGELOG_EXTRACT_EXIT = 0

Both release-only `validate` steps are reproduced here and pass, on this exact tree, ahead of the
one dispatch.

## ATT-02 pre-dispatch — CI on the dispatch SHA

Command: `gh run list --workflow=ci.yml --branch gsd/v0.9.7-trusted-publishing-and-release --event workflow_dispatch --limit 20 --json databaseId,headSha,status,conclusion,createdAt`
```
[]
```
No existing run at `ORIGIN_REF_SHA` — this is not a resumed executor. Proceeding to dispatch.

CI_DISPATCHED_AT = 2026-09-27T12:50:15Z

Command: `gh workflow run ci.yml --ref gsd/v0.9.7-trusted-publishing-and-release`
```
https://github.com/YuSabo90002/typsphinx/actions/runs/36320335404
exit=0
```

Command (15s later): `gh run list --workflow=ci.yml --branch gsd/v0.9.7-trusted-publishing-and-release --event workflow_dispatch --limit 20 --json databaseId,headSha,status,conclusion,createdAt`
```
[{"conclusion":"","createdAt":"2026-09-27T12:50:32Z","databaseId":36320335404,"headSha":"987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78","status":"in_progress"}]
```
Exactly one run at `ORIGIN_REF_SHA`, created after `CI_DISPATCHED_AT` — no re-dispatch needed.

CI_RUN_ID = 36320335404

Bounded polling: `gh run view 36320335404 --json status --jq .status` on a 30 s sleep loop; status
read `completed` on iteration 13 (2026-09-27T12:57:27Z), well inside the 45-minute bound.

Command: `gh run view 36320335404 --json headSha,conclusion,jobs --jq '{headSha,conclusion,jobcount:(.jobs|length)}'`
```
{"conclusion":"success","headSha":"987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78","jobcount":12}
```
CI_RUN_HEAD_SHA = 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78
CI_RUN_CONCLUSION = success
CI_JOB_COUNT = 12

Command: `gh run view 36320335404 --json jobs --jq '.jobs[] | "\(.name)\t\(.conclusion)"'`
```
Code Coverage	success
Test Python 3.13 on macos-latest	success
Integration Test - advanced	success
Integration Test - basic	success
Build Package	success
Lint and Format Check	success
Test Python 3.12 on windows-latest	success
Type Check	success
Test Python 3.12 on macos-latest	success
Test Python 3.13 on ubuntu-latest	success
Test Python 3.12 on ubuntu-latest	success
Test Python 3.13 on windows-latest	success
```
CI_NON_SUCCESS_JOBS = 0

Conclusion `success` at the exact dispatch SHA, zero non-success jobs — CI on the dispatch SHA is
green; no HALT.

## ATT-02 pre-dispatch — control run 35730551619

Command: `LC_ALL=C gh run view 35730551619 --log > $SCRATCH_76_03/p7603_control.log`; `wc -l`
```
3356 /tmp/p7603.oGoetI/p7603_control.log
```
CONTROL_LOG_LINES = 3356

Command: `LC_ALL=C grep -c 'disabling Trusted Publishing' $SCRATCH_76_03/p7603_control.log || true`
```
1
```
CONTROL_GREP_DISABLING_TP = 1

Command: `LC_ALL=C grep -c 'attestations input is ignored' $SCRATCH_76_03/p7603_control.log || true`
```
1
```
CONTROL_GREP_ATTESTATIONS_IS_IGNORED = 1

Command: `LC_ALL=C grep -c 'Generating and uploading digital attestations' $SCRATCH_76_03/p7603_control.log || true`
```
0
```
CONTROL_GREP_GENERATING_ATTESTATIONS = 0
The action prints this notice only on the Trusted Publishing path; the control ran on the token
path, so it is absent here as expected.

The single matching warning line, verbatim (`LC_ALL=C grep -F 'disabling Trusted Publishing'
$SCRATCH_76_03/p7603_control.log`):
```
Publish to PyPI	UNKNOWN STEP	2026-09-22T13:46:50.5362201Z ##[warning]The workflow was run with the 'attestations: true' input, but an explicit password was also set, disabling Trusted Publishing. As a result, the attestations input is ignored.
```

Control run's job table (`gh run view 35730551619 --json jobs --jq '.jobs[] | "\(.name)\t\(.conclusion)"'`):
```
Validate Release	success
Build Distribution	success
Publish to PyPI	success
Publish to TestPyPI (Optional)	skipped
Create GitHub Release	success
```

Per D-08 AMENDED: the literal three-word annotation title `attestations input ignored` lives only
in the GitHub Actions workflow-command's `title=` attribute, which `gh run view --log` never
renders — so it is not used as an evidence grep in this phase. The two greps above (against the
log body) are the discriminating pair.

## ATT-02 pre-dispatch — PyPI served state

PRE_PYPI_CAPTURED_AT = 2026-09-27T12:58:33Z

Command: `curl -sf https://pypi.org/simple/typsphinx/ -H 'Accept: application/vnd.pypi.simple.v1+json'`
into `$SCRATCH_76_03/p7603_simple_pre.json`.

Command: `jq -r '.files | length' $SCRATCH_76_03/p7603_simple_pre.json`
```
38
```
PRE_PYPI_FILE_COUNT = 38

Full list, every file with its `upload-time`, LC_ALL=C-sorted, tabs literal
(`jq -r '.files[] | "PYPI_PRE\t\(.filename)\t\(."upload-time")"' | LC_ALL=C sort`):
```
PYPI_PRE	typsphinx-0.3.0-py3-none-any.whl	2025-10-23T14:19:40.288949Z
PYPI_PRE	typsphinx-0.3.0.tar.gz	2025-10-23T14:19:41.643637Z
PYPI_PRE	typsphinx-0.4.0-py3-none-any.whl	2025-10-26T06:21:56.637359Z
PYPI_PRE	typsphinx-0.4.0.tar.gz	2025-10-26T06:21:58.012140Z
PYPI_PRE	typsphinx-0.4.1-py3-none-any.whl	2025-10-26T07:03:54.112773Z
PYPI_PRE	typsphinx-0.4.1.tar.gz	2025-10-26T07:03:55.538046Z
PYPI_PRE	typsphinx-0.4.2-py3-none-any.whl	2025-10-29T12:56:02.146763Z
PYPI_PRE	typsphinx-0.4.2.tar.gz	2025-10-29T12:56:03.071014Z
PYPI_PRE	typsphinx-0.4.3-py3-none-any.whl	2025-11-01T03:56:12.714940Z
PYPI_PRE	typsphinx-0.4.3.tar.gz	2025-11-01T03:56:14.085299Z
PYPI_PRE	typsphinx-0.4.4-py3-none-any.whl	2026-07-05T06:28:26.332037Z
PYPI_PRE	typsphinx-0.4.4.tar.gz	2026-07-05T06:28:27.401534Z
PYPI_PRE	typsphinx-0.5.0-py3-none-any.whl	2026-07-11T13:21:32.461359Z
PYPI_PRE	typsphinx-0.5.0.tar.gz	2026-07-11T13:21:33.575063Z
PYPI_PRE	typsphinx-0.6.0-py3-none-any.whl	2026-07-12T22:21:35.277102Z
PYPI_PRE	typsphinx-0.6.0.tar.gz	2026-07-12T22:21:36.290646Z
PYPI_PRE	typsphinx-0.6.1-py3-none-any.whl	2026-07-20T03:35:38.486351Z
PYPI_PRE	typsphinx-0.6.1.tar.gz	2026-07-20T03:35:39.794148Z
PYPI_PRE	typsphinx-0.6.2-py3-none-any.whl	2026-07-23T11:33:43.131979Z
PYPI_PRE	typsphinx-0.6.2.tar.gz	2026-07-23T11:33:44.325709Z
PYPI_PRE	typsphinx-0.6.3-py3-none-any.whl	2026-07-25T10:23:44.410187Z
PYPI_PRE	typsphinx-0.6.3.tar.gz	2026-07-25T10:23:45.535209Z
PYPI_PRE	typsphinx-0.6.4-py3-none-any.whl	2026-07-27T22:20:54.325266Z
PYPI_PRE	typsphinx-0.6.4.tar.gz	2026-07-27T22:20:55.665777Z
PYPI_PRE	typsphinx-0.6.5-py3-none-any.whl	2026-07-28T21:15:39.074779Z
PYPI_PRE	typsphinx-0.6.5.tar.gz	2026-07-28T21:15:40.306581Z
PYPI_PRE	typsphinx-0.7.0-py3-none-any.whl	2026-08-03T20:26:50.991987Z
PYPI_PRE	typsphinx-0.7.0.tar.gz	2026-08-03T20:26:52.268288Z
PYPI_PRE	typsphinx-0.7.1-py3-none-any.whl	2026-08-11T05:52:38.757230Z
PYPI_PRE	typsphinx-0.7.1.tar.gz	2026-08-11T05:52:40.280172Z
PYPI_PRE	typsphinx-0.8.0-py3-none-any.whl	2026-08-15T03:27:57.000952Z
PYPI_PRE	typsphinx-0.8.0.tar.gz	2026-08-15T03:27:58.253347Z
PYPI_PRE	typsphinx-0.9.0-py3-none-any.whl	2026-08-22T09:54:54.347109Z
PYPI_PRE	typsphinx-0.9.0.tar.gz	2026-08-22T09:54:55.464914Z
PYPI_PRE	typsphinx-0.9.2-py3-none-any.whl	2026-08-30T15:30:18.769671Z
PYPI_PRE	typsphinx-0.9.2.tar.gz	2026-08-30T15:30:20.137778Z
PYPI_PRE	typsphinx-0.9.6-py3-none-any.whl	2026-09-22T13:46:52.492146Z
PYPI_PRE	typsphinx-0.9.6.tar.gz	2026-09-22T13:46:54.261506Z
```

PRE_PYPI_FILELIST_SHA256 = 21e92e71c1b5cc7836ba56a10945e06aedd8f6b7eeafe4e3c260ce510e5a2946
(sha256 of the jq-produced `filename<TAB>upload-time` lines after `LC_ALL=C sort` — the same bytes
the `awk -F'\t' '$1=="PYPI_PRE"{print $2"\t"$3}'` extraction of the lines above reproduces)

Command: `jq -r '.files[] | select(.filename | startswith("typsphinx-0.9.6")) | "\(.filename)\t\(.hashes.sha256)\t\(.provenance | tostring)"' $SCRATCH_76_03/p7603_simple_pre.json`
```
typsphinx-0.9.6-py3-none-any.whl	0289f1adcd361dd773cc0c89d9abe874b8dd6c7ed74ce042bb6bb23e98c5b7c1	null
typsphinx-0.9.6.tar.gz	74d588b465895f68d041d7376f39fc203f8754aa4ab893a337552f3dc5f07ce8	null
```
PRE_PYPI_096_WHEEL_SHA256 = 0289f1adcd361dd773cc0c89d9abe874b8dd6c7ed74ce042bb6bb23e98c5b7c1
PRE_PYPI_096_SDIST_SHA256 = 74d588b465895f68d041d7376f39fc203f8754aa4ab893a337552f3dc5f07ce8
PRE_PYPI_096_WHEEL_PROVENANCE = null
PRE_PYPI_096_SDIST_PROVENANCE = null

## ATT-02 pre-dispatch — GitHub Release v0.9.6

Command: `gh release view v0.9.6 --json assets --jq '.assets[] | ["RELEASE_PRE", .name, (.size|tostring), (.digest // "none"), .createdAt, .updatedAt] | @tsv'`, `LC_ALL=C sort`:
```
RELEASE_PRE	typsphinx-0.9.6-py3-none-any.whl	194339	sha256:0289f1adcd361dd773cc0c89d9abe874b8dd6c7ed74ce042bb6bb23e98c5b7c1	2026-09-22T13:47:15Z	2026-09-22T13:47:15Z
RELEASE_PRE	typsphinx-0.9.6.tar.gz	860244	sha256:74d588b465895f68d041d7376f39fc203f8754aa4ab893a337552f3dc5f07ce8	2026-09-22T13:47:15Z	2026-09-22T13:47:15Z
RELEASE_PRE	typsphinx.pdf	2823877	sha256:4ff29f5dc1000d15c99fa3371ab6eaec5450194c5cdf5c3d228f21212cf1b97a	2026-09-22T13:00:08Z	2026-09-22T13:00:08Z
```

PRE_RELEASE_ASSET_COUNT = 3

Command: `gh release view v0.9.6 --json assets --jq '.assets[] | [.name, (.size|tostring), (.digest // "none"), .createdAt, .updatedAt] | @tsv' | LC_ALL=C sort | sha256sum | cut -d' ' -f1`
```
793dc12a533652e872d1f7207cb2ef4ce5c496aaf3cc27271d09d289a0b26025
```
PRE_RELEASE_ASSETS_SHA256 = 793dc12a533652e872d1f7207cb2ef4ce5c496aaf3cc27271d09d289a0b26025

Command: `gh release view v0.9.6 --json body --jq .body | sha256sum | cut -d' ' -f1`
```
66a83e4fcee3536b393b9c97121a1f810f5db0902af0c698cde7502d6a7b1d6b
```
PRE_RELEASE_BODY_SHA256 = 66a83e4fcee3536b393b9c97121a1f810f5db0902af0c698cde7502d6a7b1d6b

Download counts are deliberately excluded from this fingerprint (they change on any fetch).

## ATT-02 pre-dispatch — publish-testpypi if: evaluation

The `if:` block from the dispatch SHA's `release.yml`, verbatim (`git show
987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78:.github/workflows/release.yml`, `publish-testpypi` job):
```
    if: |
      contains(github.ref, 'beta') ||
      contains(github.ref, 'alpha') ||
      contains(github.ref, 'rc') ||
      contains(inputs.tag, 'beta') ||
      contains(inputs.tag, 'alpha') ||
      contains(inputs.tag, 'rc')
```

Evaluated against `github.ref = refs/heads/gsd/v0.9.7-trusted-publishing-and-release` and
`inputs.tag = v0.9.6`, via a shell substring test on each operand:

| operand | value | contains |
|---|---|---|
| `github.ref` contains `beta` | `refs/heads/gsd/v0.9.7-trusted-publishing-and-release` | false |
| `github.ref` contains `alpha` | `refs/heads/gsd/v0.9.7-trusted-publishing-and-release` | false |
| `github.ref` contains `rc` | `refs/heads/gsd/v0.9.7-trusted-publishing-and-release` | false |
| `inputs.tag` contains `beta` | `v0.9.6` | false |
| `inputs.tag` contains `alpha` | `v0.9.6` | false |
| `inputs.tag` contains `rc` | `v0.9.6` | false |

TESTPYPI_IF_TRUE_OPERANDS = 0

`Publish to TestPyPI (Optional)` is therefore expected to conclude `skipped` (constraint 7).

## ATT-02 pre-dispatch — content non-identity

Command: `git diff --quiet v0.9.6 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78 -- typsphinx/` — exit 1
(differs).
Command: `git diff --name-only v0.9.6 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78 -- typsphinx/`
```
typsphinx/translator.py
```
REF_DIFFERS_FROM_V096_UNDER_TYPSPHINX = yes

Command: `uv build --out-dir $SCRATCH_76_03/build` (from this worktree, equal to the ref outside
`.planning/`) — full build log fenced separately; final lines:
```
Successfully built /tmp/p7603.oGoetI/build/typsphinx-0.9.6.tar.gz
Successfully built /tmp/p7603.oGoetI/build/typsphinx-0.9.6-py3-none-any.whl
exit=0
```
LOCAL_BUILD_EXIT = 0

Command: `sha256sum $SCRATCH_76_03/build/*.whl $SCRATCH_76_03/build/*.tar.gz`
```
3f45e0746134c0fa5731fd84a6d679f1b19cf5d5e01c11fd700420393fcd0534  typsphinx-0.9.6-py3-none-any.whl
764471803679a6d7f608665628a6fdfe1b5c28bb0a05da7381069346edf6fab3  typsphinx-0.9.6.tar.gz
```
LOCAL_WHEEL_SHA256 = 3f45e0746134c0fa5731fd84a6d679f1b19cf5d5e01c11fd700420393fcd0534
LOCAL_SDIST_SHA256 = 764471803679a6d7f608665628a6fdfe1b5c28bb0a05da7381069346edf6fab3

Both differ from `PRE_PYPI_096_WHEEL_SHA256` (`0289f1ad…`) and `PRE_PYPI_096_SDIST_SHA256`
(`74d588b4…`).
LOCAL_BUILD_MATCHES_PYPI = no

PyPI answers 200 and writes nothing only for byte-identical files; the sdist embeds a build-time
gzip mtime and the ref's `typsphinx/translator.py` differs from the tag, so the identical-hash
branch is unreachable. Task 3's artifact comparison against the run's own `dist-packages` artifact
is the binding reading.

## ATT-02 pre-dispatch — rollback-path secrets

Names only, never values.

Command: `gh secret list --json name --jq '.[].name'`
```
PYPI_API_TOKEN
TEST_PYPI_API_TOKEN
```
PRE_REPO_SECRET_PYPI_API_TOKEN = present

Command: `gh secret list --env pypi --json name --jq '.[].name'`
```
PYPI_API_TOKEN
```
PRE_ENV_SECRET_PYPI_API_TOKEN = present

Both stay (constraint 11) — ATT-05 retires them later, at `/gsd-complete-milestone`.

## ATT-02 pre-dispatch verdict

Command: `gh run list --workflow=release.yml --branch gsd/v0.9.7-trusted-publishing-and-release --event workflow_dispatch --limit 50 --json databaseId`
```
[]
```
PRIOR_REHEARSAL_RUNS = 0

Every key recorded above holds its expected value:
- `ORIGIN_REF_SHA` measured, ref content matches expectations, worktree matches it outside
  `.planning/`, no decoy branch, no `v0.9.7` tag.
- `VALIDATE_VERSION_MATCH = yes`, `VALIDATE_CHANGELOG_EXTRACT_EXIT = 0`.
- CI run `36320335404` completed `success` on `ORIGIN_REF_SHA`, zero non-success jobs.
- Control run annotation greps read 1/1/0 as expected.
- PyPI and GitHub Release baselines captured; both 0.9.6 provenance values `null`.
- `publish-testpypi`'s `if:` evaluates false on all six operands.
- Content non-identity confirmed on both the tag-diff and the local-build-hash legs.
- Both rollback secrets present; zero prior rehearsal runs on this branch.

PRE_DISPATCH_VERDICT = READY

## ATT-02 dispatch — owner checkpoint

The Task 2 checkpoint was relayed by the orchestrator with the owner's explicit answer, given
after being shown `ORIGIN_REF_SHA` (`987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78`), `CI_RUN_ID`
(`36320335404`, `success`), `PRE_DISPATCH_VERDICT` (`READY`), the one-way nature of the dispatch,
the Sigstore/Rekor side effect, and the approval + 15-minute `wait_timer` + 90-minute bound:

```
"dispatch" (given verbatim by the owner at 2026-09-27, after being shown ORIGIN_REF_SHA
987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78, CI run 36320335404 success, PRE_DISPATCH_VERDICT READY,
the one-way nature, the Sigstore/Rekor side effect, and the approval + 15-min wait_timer + 90-min
bound.)
```

OWNER_CHECKPOINT_CHOICE = dispatch
OWNER_CHECKPOINT_AT = 2026-09-27T13:08:39Z

SCRATCH_76_03_T3 = /tmp/p7603t3.rUrDb0

Resume guard (step 1): `REHEARSAL_RUN_ID` / `DISPATCH_ATTEMPTED` are not yet recorded in this
file, and `gh run list --workflow=release.yml --branch gsd/v0.9.7-trusted-publishing-and-release
--event workflow_dispatch --limit 20 --json databaseId,headSha,createdAt,status,conclusion` returns
`[]` — an empty list with no marker, so this is a fresh dispatch, not a resumed one. Continuing to
step 2.

Pre-dispatch re-measure (step 2): `git ls-remote origin
refs/heads/gsd/v0.9.7-trusted-publishing-and-release`
```
987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78	refs/heads/gsd/v0.9.7-trusted-publishing-and-release
```
ORIGIN_REF_SHA_AT_DISPATCH = 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78

Equal to `ORIGIN_REF_SHA` — no fetch/accept step needed.
DISPATCH_REF_SHA = 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78

Command: `curl -sf https://pypi.org/simple/typsphinx/ -H 'Accept:
application/vnd.pypi.simple.v1+json' | jq -r '.files[] | "\(.filename)\t\(."upload-time")"' |
LC_ALL=C sort | sha256sum`
```
21e92e71c1b5cc7836ba56a10945e06aedd8f6b7eeafe4e3c260ce510e5a2946
```
PRE_DISPATCH_RECHECK_FILELIST_SHA256 = 21e92e71c1b5cc7836ba56a10945e06aedd8f6b7eeafe4e3c260ce510e5a2946

Equal to `PRE_PYPI_FILELIST_SHA256` — PyPI state has not moved since Task 1's capture.
