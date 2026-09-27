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
