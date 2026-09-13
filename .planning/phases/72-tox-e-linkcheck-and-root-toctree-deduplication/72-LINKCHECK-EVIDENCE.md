# Phase 72 — Linkcheck Evidence (QUA-13, SC#1)

## Head check and provisioning

`date -u +%FT%TZ`:
```
2026-09-13T13:23:39Z
```

`pwd -P`:
```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a3a24a1f6d1679229
```

`test -f .git; echo "exit:$?"`:
```
exit:0
```

Shim check `grep -q typsphinx-fhs-run "$(command -v uv)"`: matched (shim present).

Provisioning line:
```
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs --python 3.13.13
```
Provisioning exit: 0.

PYVENV_HOME = /nix/store/l9k0anq0z7zz81zcwy035jfwap9ga6rl-python3-3.13.13/bin
PYVENV_VERSION_INFO = 3.13.13
BASE_72_02 = 34c77f59266acb028c8934ff56715dd4454bdfe8
SCRATCH_72_02 = /tmp/tmp.PBHZQzgAe5

## tox.ini diff

TOX_EDIT_COMMIT = 328f447eb2dd0984aa93c84d667409d05bee31f4

`git diff --numstat "$BASE_72_02" HEAD -- tox.ini`:
```
8	0	tox.ini
```

`git diff "$BASE_72_02" HEAD -- tox.ini`, verbatim:
```diff
diff --git a/tox.ini b/tox.ini
index 729e40cb..f6487c46 100644
--- a/tox.ini
+++ b/tox.ini
@@ -88,3 +88,11 @@ changedir = docs
 commands =
     sphinx-build -b html source _build/html
     sphinx-build -b typstpdf source _build/pdf
+
+[testenv:linkcheck]
+description = Check external links and anchors in the documentation (needs network)
+runner = uv-venv-lock-runner
+extras = docs
+changedir = docs
+commands =
+    sphinx-build -b linkcheck source _build/linkcheck
```

`sed -n 2p tox.ini`:
```
env_list = py312, py313, lint, type, cov, docs
```

`uv run tox list`, verbatim:
```
default environments:
py312     -> Run tests with pytest
py313     -> Run tests with pytest
lint      -> Run linting checks
type      -> Run type checking with mypy
cov       -> Run tests with coverage
docs      -> Build both HTML and PDF documentation

additional environments:
docs-html -> Build HTML documentation
docs-pdf  -> Build PDF documentation with typstpdf
linkcheck -> Check external links and anchors in the documentation (needs network)
```

`linkcheck` appears once under `additional environments:` and does not appear under
`default environments:`.

## Run 1

`rm -rf docs/_build/linkcheck` then `test ! -e docs/_build/linkcheck; echo "exit:$?"`:
```
exit:0
```

Command: `uv run tox -e linkcheck`, output to `$SCRATCH_72_02/p7202_run1.log`.

LINKCHECK_RUN_1_EXIT = 0

`output.json` copied to `$SCRATCH_72_02/p7202_run1_output.json` (95 lines).

Census, via `uv run python -c` over the JSON lines:

LINKCHECK_RUN_1_TOTAL = 95
LINKCHECK_RUN_1_WORKING = 95
LINKCHECK_RUN_1_UNIQUE_URIS = 95
LINKCHECK_RUN_1_STATUS_CENSUS = working:95
LINKCHECK_RUN_1_ANCHORED_URIS = 41

Non-`working` rows:
```
no non-working rows
```

Tail of the run log, last 5 lines. Console text is locale-dependent per `CLAUDE.md` § Locale — the
sandbox passes the host `LANG` through, so this is Japanese on this machine; the binding evidence
is the `output.json` census above, not this console text:
```
build succeeded, 3 warnings.

上記の出力結果、または _build/linkcheck /output.txt を見てエラーを確認してください
  linkcheck: OK (10.47=setup[0.11]+cmd[10.36] seconds)
  congratulations :) (10.49 seconds)
```

Run 1 meets SC#1 on its own: exit 0, total 95 equals working 95, at least 1 row. Task 2 records
the verdict.
