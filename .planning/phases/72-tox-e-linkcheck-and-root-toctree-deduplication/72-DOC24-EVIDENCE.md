# Phase 72 — DOC-24 Evidence (SC#2) and the D-07 todo note

## Head check and gate

- `date -u +%FT%TZ`: `2026-09-13T13:35:58Z`
- `pwd -P`: `/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aab9ec9556bbfe744`
- `test -f .git; echo "exit:$?"`: `exit:0`
- `grep -q typsphinx-fhs-run "$(command -v uv)"`: `SHIM_OK`
- Provisioning: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --python 3.13.13` — exit 0, installed 81 packages including `typsphinx==0.9.2` built from this worktree.

BASE_72_03 = 043949e7cb4233999d4d1db9683055e6f5ecbb83

SCRATCH_72_03 = /tmp/tmp.K00cCubXim

`grep -nx '\[testenv:linkcheck\]' tox.ini`:
```
92:[testenv:linkcheck]
```
The environment is present at `BASE_72_03` (72-02 already merged into this worktree's base). Gate passes — proceeding to name it on listing surfaces.

## Discovery

`git grep -n 'tox -e docs-pdf' -- ':!.planning'`:
```
.github/workflows/docs.yml:36:        run: uv run tox -e docs-pdf
CHANGELOG.md:921:  - Documentation builds now reproducible locally with `tox -e docs-html` or `tox -e docs-pdf`
CLAUDE.md:33:tox -e docs-pdf              # PDF via the typstpdf builder (dogfoods this extension)
README.md:262:uv run tox -e docs-pdf      # Build PDF documentation
docs/source/contributing.rst:124:   uv run tox -e docs-pdf      # Build PDF documentation
```

DOC24_GREP_HITS = 5

Supplementary `git grep -nE 'tox -e (lint|type|py312|docs-html|docs)( |$)' -- ':!.planning'`:
```
.github/workflows/ci.yml:70:        run: uv run tox -e lint
.github/workflows/ci.yml:91:        run: uv run tox -e type
.github/workflows/docs.yml:33:        run: uv run tox -e docs-html
CLAUDE.md:32:tox -e docs-html             # HTML via furo
README.md:258:uv run tox -e lint          # Run linters (black, ruff)
README.md:259:uv run tox -e type          # Run type checking (mypy)
README.md:260:uv run tox -e py312         # Run tests on Python 3.12
README.md:261:uv run tox -e docs-html     # Build HTML documentation
README.md:263:uv run tox -e docs          # Build both HTML and PDF docs
docs/source/contributing.rst:120:   uv run tox -e lint          # Black + Ruff
docs/source/contributing.rst:121:   uv run tox -e type          # Mypy type checking
docs/source/contributing.rst:122:   uv run tox -e py312         # Tests on Python 3.12
docs/source/contributing.rst:123:   uv run tox -e docs-html     # Build HTML documentation
docs/source/contributing.rst:125:   uv run tox -e docs          # Build both HTML and PDF
```

No file beyond the three named at planning time (`CLAUDE.md`, `README.md`, `docs/source/contributing.rst`) plus the two already-dispositioned non-listing hits (`.github/workflows/docs.yml`, `CHANGELOG.md`) appears in either grep — matches milestone invariant #4's expectation that the supplementary grep is discovery-only, not a source of new surfaces.

## CLAUDE.md

`git diff --numstat 043949e7cb4233999d4d1db9683055e6f5ecbb83 HEAD -- CLAUDE.md`:
```
1	0	CLAUDE.md
```

`git diff -U1 043949e7cb4233999d4d1db9683055e6f5ecbb83 HEAD -- CLAUDE.md`:
```diff
diff --git a/CLAUDE.md b/CLAUDE.md
index 17194349..b6b8b3c5 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -33,2 +33,3 @@ tox -e docs-html             # HTML via furo
 tox -e docs-pdf              # PDF via the typstpdf builder (dogfoods this extension)
+tox -e linkcheck             # Check external links and anchors (needs network; not run by plain tox)
 ```
```

`uv run python -c` column/ASCII check output: `CLAUDE_COMMENT_COLUMN = 29`

CLAUDE_COMMENT_COLUMN = 29

The three `#` columns (the new line and its two neighbours above) agree at column 29; the new line is pure ASCII and is the fenced block's last line before the closing fence.
