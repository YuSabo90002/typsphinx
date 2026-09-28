# Phase 77 — Publish-half Controls (read-only rehearsal of the handoff's commands)

Every reading here is a control that fixes the expected shape of a command the handoff prescribes;
none of it is ATT-03, ATT-04, ATT-05 or DOC-25 evidence, which exists only once the v0.9.7 release
run has happened. Each section records the verbatim command and output.

## Head check and provisioning

Command: `date -u +%FT%TZ`
```
2026-09-28T13:16:43Z
```

Command: `pwd -P`
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a9cf7dde6a8321350
```

Command: `test -f .git; echo "exit:$?"`
```
exit:0
```

SCRATCH_77_03 = /tmp/p7703.ZqqrdO
Quoted from `77-ATT06-EVIDENCE.md`.

## ATT-04 control readings

Command: `LC_ALL=C gh run view 35730551619 --log > $S/p7703_control.log`
```
3356 lines
```

Command: `LC_ALL=C gh run view 36321530105 --attempt 1 --log > $S/p7703_rehearsal.log`
```
3004 lines
```

Command: `LC_ALL=C grep -c 'disabling Trusted Publishing' $S/p7703_control.log || true`
```
1
```
CTRL_C_DISABLING_TP = 1

Command: `LC_ALL=C grep -c 'attestations input is ignored' $S/p7703_control.log || true`
```
1
```
CTRL_C_ATTESTATIONS_IS_IGNORED = 1

Command: `LC_ALL=C grep -c 'attestations input ignored' $S/p7703_control.log || true` (the
requirement's literal phrase — lives only in the annotation's `title=` attribute, which
`gh run view --log` never prints; this is the measured reason Discretion A replaces it with the
two-grep pair above)
```
0
```
CTRL_C_TITLE_PHRASE = 0

Command: `LC_ALL=C grep -c 'Generating and uploading digital attestations' $S/p7703_control.log || true`
```
0
```
CTRL_C_GENERATING = 0

Command: `LC_ALL=C grep -c 'disabling Trusted Publishing' $S/p7703_rehearsal.log || true`
```
0
```
CTRL_R_DISABLING_TP = 0

Command: `LC_ALL=C grep -c 'attestations input is ignored' $S/p7703_rehearsal.log || true`
```
0
```
CTRL_R_ATTESTATIONS_IS_IGNORED = 0

Command: `LC_ALL=C grep -c 'Generating and uploading digital attestations' $S/p7703_rehearsal.log || true`
```
1
```
CTRL_R_GENERATING = 1

Command: `gh run view 35730551619 --json jobs --jq '.jobs[] | select(.name == "Publish to PyPI") | .databaseId'`
```
106756389696
```
CTRL_C_PUBLISH_JOB_ID = 106756389696

Command: `gh run view --job 106756389696 --log | wc -l` — the command shape R3 uses
```
251
```
Returns lines, as expected — the shape works on a real job id.

## ATT-03(a) control readings

Command: `curl -sf https://pypi.org/simple/typsphinx/ -H 'Accept: application/vnd.pypi.simple.v1+json' -o $S/p7703_simple.json`
```
exit:0, 19902 bytes
```

Command: `jq -r '[.files[] | select(.filename == "typsphinx-0.9.6-py3-none-any.whl" or .filename == "typsphinx-0.9.6.tar.gz") | .provenance | tostring] | join(",")' $S/p7703_simple.json`
```
null,null
```
CTRL_V096_PROVENANCE = null,null

Command: `jq '[.files[] | select(.filename | test("^typsphinx-0\\.9\\.7(-|\\.tar\\.gz$)"))] | length' $S/p7703_simple.json`
```
0
```
CTRL_V097_FILES = 0

Command: `curl -sf https://pypi.org/simple/pip/ -H 'Accept: application/vnd.pypi.simple.v1+json' -o $S/p7703_pip_simple.json`
```
exit:0, 149904 bytes
```

Command: `jq -r '.files[] | select(.filename == "pip-26.2.1-py3-none-any.whl") | .provenance' $S/p7703_pip_simple.json`
```
https://pypi.org/integrity/pip/26.2.1/pip-26.2.1-py3-none-any.whl/provenance
```
CTRL_PIP_WHEEL_PROVENANCE = https://pypi.org/integrity/pip/26.2.1/pip-26.2.1-py3-none-any.whl/provenance

Command: `jq -r '.files[] | select(.filename == "pip-26.2.1-py3-none-any.whl") | .provenance | type' $S/p7703_pip_simple.json`
```
string
```
CTRL_PIP_PROVENANCE_TYPE = string

An attested file's `provenance` is a URL string naming its Integrity API endpoint, not a boolean —
so the ATT-03(a) check on the real 0.9.7 files must be non-null plus that URL shape, never an
equality with `true`.

## ATT-03(b) control readings

Command: `curl -s -o /dev/null -w '%{http_code}' https://pypi.org/integrity/typsphinx/0.9.6/typsphinx-0.9.6-py3-none-any.whl/provenance`
```
404
```
CTRL_INTEGRITY_V096_WHEEL_HTTP = 404

Command: `curl -s -o /dev/null -w '%{http_code}' https://pypi.org/integrity/typsphinx/0.9.6/typsphinx-0.9.6.tar.gz/provenance`
```
404
```
CTRL_INTEGRITY_V096_SDIST_HTTP = 404

Command: `curl -s -o $S/p7703_pip_int.json -w '%{http_code}' https://pypi.org/integrity/pip/26.2.1/pip-26.2.1-py3-none-any.whl/provenance`
```
200
```
CTRL_INTEGRITY_PIP_HTTP = 200

Command: `jq '.attestation_bundles | length' $S/p7703_pip_int.json`
```
1
```
CTRL_INTEGRITY_PIP_BUNDLES = 1

Command: `jq -r '.attestation_bundles[0].publisher | [.kind, .repository, .workflow, .environment] | join("|")' $S/p7703_pip_int.json`
```
GitHub|pypa/pip|release.yml|pypi
```
CTRL_INTEGRITY_PIP_PUBLISHER = GitHub|pypa/pip|release.yml|pypi

The handoff reads `attestation_bundles | length` before indexing `[0]`, and HALTs rather than
guessing when the count is not 1 — confirmed here as exactly 1 for a real attested file.

## ATT-05 before-state, names only

Command: `gh secret list --json name --jq '.[].name'`
```
PYPI_API_TOKEN
TEST_PYPI_API_TOKEN
```
CTRL_REPO_SECRETS = PYPI_API_TOKEN|TEST_PYPI_API_TOKEN

Command: `gh secret list --env pypi --json name --jq '.[].name'`
```
PYPI_API_TOKEN
```
CTRL_ENV_PYPI_SECRETS = PYPI_API_TOKEN

Command: `gh secret list --env testpypi --json name --jq '.[].name'`
```
(empty)
```
CTRL_ENV_TESTPYPI_SECRETS = none

TEST_PYPI_API_TOKEN_SCOPES = repository

`TEST_PYPI_API_TOKEN` is listed only at repository scope (`CTRL_REPO_SECRETS` above); it is absent
from both the `pypi` and `testpypi` environment scopes. ATT-05's survival check for it is
therefore: every scope that lists it before the deletion — here, repository scope alone — still
lists it afterwards.

## DOC-25 target

Command: `grep -n 'PYPI_API_TOKEN' .planning/codebase/INTEGRATIONS.md`
```
116:- `PYPI_API_TOKEN` - PyPI trusted publishing (used in release.yml, alternative to deprecated password)
117:- `TEST_PYPI_API_TOKEN` - TestPyPI API token (optional, for pre-release testing)
```
DOC25_TARGET_LINE = 116
DOC25_KEEP_LINE = 117

The target line is edited only at the close, after ATT-05, so it describes a state that is already
true.

## Release body control

Command: `uv run python scripts/extract_changelog_section.py 0.9.6 > $S/p7703_notes_096.md`
```
exit:0, 100 lines
```
CTRL_EXTRACT_096_LINES = 100

Command: `gh release view v0.9.6 --json body --jq .body > $S/p7703_body_096.md`
```
exit:0, 132 lines
```

Command: `head -n 100 $S/p7703_body_096.md | diff - $S/p7703_notes_096.md`
```
(empty — no differences)
```
CTRL_RELEASE_BODY_PREFIX_MATCH = yes

This proves the comparison the handoff prescribes for 0.9.7 works on a known release: the
published body's first `CTRL_EXTRACT_096_LINES` lines are byte-identical to the extractor's own
stdout, and the remaining 32 lines are the create-release step's appended Installation block and
GitHub's generated notes.

## Translations and Read the Docs controls

Command: `gh api repos/YuSabo90002/typsphinx-doc-translations/contents/.github/workflows/update-pin.yml --jq .content` decoded with `base64 -d`
```
...
  workflow_dispatch: {}
...
```
CTRL_UPDATE_PIN_DISPATCHABLE = yes

Command: `gh api repos/YuSabo90002/typsphinx-doc-translations/contents/typsphinx --jq .sha`
```
9fa1cb894137933f4dbb49d1668fc193e2ef1bc8
```
CTRL_TRANSLATIONS_PIN = 9fa1cb894137933f4dbb49d1668fc193e2ef1bc8

Command: `gh api repos/YuSabo90002/typsphinx-doc-translations/git/refs/tags/v0.9.6 --jq .object.type`
```
tag
```
CTRL_TRANSLATIONS_V096_TAG_TYPE = tag

Command: `curl -s https://readthedocs.org/api/v3/projects/typsphinx/versions/stable/ | jq -r .identifier`
```
6fcc5adb02f5eefffd88ecda5258dca842d1acaa
```
CTRL_RTD_EN_IDENTIFIER = 6fcc5adb02f5eefffd88ecda5258dca842d1acaa

Command: `curl -s https://readthedocs.org/api/v3/projects/typsphinx-ja/versions/stable/ | jq -r .identifier`
```
158fa1c4a29376478e62c02bce72abf06750455a
```
CTRL_RTD_JA_IDENTIFIER = 158fa1c4a29376478e62c02bce72abf06750455a

Command: cache-busted fetch of `https://typsphinx.readthedocs.io/en/stable/?cb=<fresh number>`, read with `grep -o 'typsphinx 0\.9\.[0-9]*' | sort -u`
```
typsphinx 0.9.6
```
CTRL_RTD_EN_VERSION = 0.9.6

Command: the `ja` equivalent, `https://typsphinx.readthedocs.io/ja/stable/?cb=<fresh number>`
```
typsphinx 0.9.6
```
CTRL_RTD_JA_VERSION = 0.9.6

## Controls verdict

Every expected value above held: the ATT-04 two-grep pair reads 1/1 on the control and 0/0 on the
rehearsal, with the literal title-attribute phrase reading 0 even on the control; the Simple JSON
API reads `null,null` for the 0.9.6 files and a URL string for `pip`'s attested wheel; the
Integrity API reads 404 for the 0.9.6 wheel and 200 with one bundle and the `GitHub|pypa/pip
|release.yml|pypi` publisher for `pip`; the name-only secret listings, the DOC-25 line, the v0.9.6
Release-body prefix match, and the translations and Read the Docs identifiers all read as recorded
above.

CONTROLS_VERDICT = READY
