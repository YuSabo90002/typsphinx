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
REF_TESTPYPI_SECRET_REFS = 1 (the control that the grep reads the right file)

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

REF_ATT01_VERDICT = MET (`ATT01_SC1_VERDICT` read from this same file at that SHA)
REF_MSG06_VERDICT = MET (`MSG06_SC5_VERDICT` read from `76-MSG06-EVIDENCE.md` at that SHA)

Command: `git diff --name-only 987ec3fe80ae6f6379e6c4e60dc6ce8c1ab6df78 HEAD -- . ':(exclude).planning'`
```
(no output — empty)
```
WORKTREE_MATCHES_REF_OUTSIDE_PLANNING = yes

Command: `git ls-remote origin 'refs/heads/gsd/v0.9.7*' | wc -l`
```
1
```
ORIGIN_V097_BRANCHES = 1 (no `-milestone` decoy on origin)

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
