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

## Surfaces

`git diff --numstat 043949e7cb4233999d4d1db9683055e6f5ecbb83 HEAD -- README.md`:
```
1	0	README.md
```

`git diff --numstat 043949e7cb4233999d4d1db9683055e6f5ecbb83 HEAD -- docs/source/contributing.rst`:
```
1	0	docs/source/contributing.rst
```

`git diff -U1` for README.md:
```diff
diff --git a/README.md b/README.md
index 8a262adc..8fe00311 100644
--- a/README.md
+++ b/README.md
@@ -263,2 +263,3 @@ uv run tox -e docs-pdf      # Build PDF documentation
 uv run tox -e docs          # Build both HTML and PDF docs
+uv run tox -e linkcheck     # Check external links and anchors (needs network; not run by plain tox)
 ```
```

`git diff -U1` for docs/source/contributing.rst:
```diff
diff --git a/docs/source/contributing.rst b/docs/source/contributing.rst
index bfc80ca8..87935a94 100644
--- a/docs/source/contributing.rst
+++ b/docs/source/contributing.rst
@@ -125,2 +125,3 @@ Tox provides the same commands used in CI, making it easy to reproduce issues lo
    uv run tox -e docs          # Build both HTML and PDF
+   uv run tox -e linkcheck     # Check external links and anchors (needs network; not run by plain tox)
```

`uv run python -c` column/ASCII check output:
```
README_COMMENT_COLUMN = 28
CONTRIBUTING_COMMENT_COLUMN = 31
```

README_COMMENT_COLUMN = 28

CONTRIBUTING_COMMENT_COLUMN = 31

Both new lines are directly after the neighbouring `… tox -e docs` line, column-aligned with their three neighbours above, ASCII, and the block's last line (a closing fence in README.md, a blank line in contributing.rst). The two byte-identical sync-hazard comment lines were re-checked and are unchanged:
- `docs/source/contributing.rst`: `   # Run all tox environments (tests, lint, type check, docs)` — present, unchanged.
- `CLAUDE.md`: `tox                          # env_list: py312, py313, lint, type, cov, docs` — present, unchanged.

## Dispositions

One row per hit of both the discovery grep and the supplementary grep, taken at `BASE_72_03`:

| File:line | Matched text | Disposition |
|-----------|--------------|--------------|
| `.github/workflows/docs.yml:36` | `run: uv run tox -e docs-pdf` | CI step that runs one environment; not a listing, and constraint 3 keeps workflow files out of the diff |
| `CHANGELOG.md:921` | `` - Documentation builds now reproducible locally with `tox -e docs-html` or `tox -e docs-pdf` `` | released CHANGELOG history bullet; not a listing |
| `CLAUDE.md:33` | `tox -e docs-pdf              # PDF via the typstpdf builder (dogfoods this extension)` | listing surface — linkcheck line added (CLAUDE.md) |
| `README.md:262` | `uv run tox -e docs-pdf      # Build PDF documentation` | listing surface — linkcheck line added (README.md) |
| `docs/source/contributing.rst:124` | `   uv run tox -e docs-pdf      # Build PDF documentation` | listing surface — linkcheck line added (docs/source/contributing.rst) |
| `.github/workflows/ci.yml:70` | `run: uv run tox -e lint` | CI step that runs one environment; not a listing, and constraint 3 keeps workflow files out of the diff |
| `.github/workflows/ci.yml:91` | `run: uv run tox -e type` | CI step that runs one environment; not a listing, and constraint 3 keeps workflow files out of the diff |
| `.github/workflows/docs.yml:33` | `run: uv run tox -e docs-html` | CI step that runs one environment; not a listing, and constraint 3 keeps workflow files out of the diff |
| `CLAUDE.md:32` | `tox -e docs-html             # HTML via furo` | already part of the CLAUDE.md listing surface, edited above |
| `README.md:258` | `uv run tox -e lint          # Run linters (black, ruff)` | already part of the README.md listing surface, edited above |
| `README.md:259` | `uv run tox -e type          # Run type checking (mypy)` | already part of the README.md listing surface, edited above |
| `README.md:260` | `uv run tox -e py312         # Run tests on Python 3.12` | already part of the README.md listing surface, edited above |
| `README.md:261` | `uv run tox -e docs-html     # Build HTML documentation` | already part of the README.md listing surface, edited above |
| `README.md:263` | `uv run tox -e docs          # Build both HTML and PDF docs` | already part of the README.md listing surface, edited above (this is the line the new line was inserted directly after) |
| `docs/source/contributing.rst:120` | `   uv run tox -e lint          # Black + Ruff` | already part of the contributing.rst listing surface, edited above |
| `docs/source/contributing.rst:121` | `   uv run tox -e type          # Mypy type checking` | already part of the contributing.rst listing surface, edited above |
| `docs/source/contributing.rst:122` | `   uv run tox -e py312         # Tests on Python 3.12` | already part of the contributing.rst listing surface, edited above |
| `docs/source/contributing.rst:123` | `   uv run tox -e docs-html     # Build HTML documentation` | already part of the contributing.rst listing surface, edited above |
| `docs/source/contributing.rst:125` | `   uv run tox -e docs          # Build both HTML and PDF` | already part of the contributing.rst listing surface, edited above (this is the line the new line was inserted directly after) |

No file beyond the three named listing surfaces (`CLAUDE.md`, `README.md`, `docs/source/contributing.rst`) appears in either grep. No new listing surface was discovered.

DOC24_LISTING_SURFACES = 3

## Post-edit grep

`git grep -n 'tox -e linkcheck' -- ':!.planning'`:
```
CLAUDE.md:34:tox -e linkcheck             # Check external links and anchors (needs network; not run by plain tox)
README.md:264:uv run tox -e linkcheck     # Check external links and anchors (needs network; not run by plain tox)
docs/source/contributing.rst:126:   uv run tox -e linkcheck     # Check external links and anchors (needs network; not run by plain tox)
```

DOC24_LINKCHECK_LINES = 3

`git grep -n 'tox -e docs-pdf' -- ':!.planning'` (post-edit, same hit count as at discovery):
```
.github/workflows/docs.yml:36:        run: uv run tox -e docs-pdf
CHANGELOG.md:921:  - Documentation builds now reproducible locally with `tox -e docs-html` or `tox -e docs-pdf`
CLAUDE.md:33:tox -e docs-pdf              # PDF via the typstpdf builder (dogfoods this extension)
README.md:262:uv run tox -e docs-pdf      # Build PDF documentation
docs/source/contributing.rst:124:   uv run tox -e docs-pdf      # Build PDF documentation
```

DOC24_VERDICT = MET

## D-07 todo note

`git diff --numstat 043949e7cb4233999d4d1db9683055e6f5ecbb83 HEAD -- .planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md`:
```
6	0	.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md
```
0 removed. The base file (41 lines) is a byte-identical prefix of the new file: `head -n 41` of the current file hashes to `6a0aa371a5cccac3410ec9f12e8f9e8c190e35ab`, the same as `git rev-parse 043949e7cb4233999d4d1db9683055e6f5ecbb83:.planning/todos/pending/2026-07-22-add-sphinx-linkcheck-ci-job.md`.

`git ls-files .planning/todos/pending .planning/todos/completed | wc -l` before this task (at `BASE_72_03`): 60. After this task (current HEAD): 60. Unchanged — no todo was added, moved, or removed.

Appended text, verbatim (via `sed -n '/^## Status note (Phase 72, v0.9.5)$/,$p'`):
```markdown
## Status note (Phase 72, v0.9.5)

- `tox.ini` now has the `[testenv:linkcheck]` environment the first Solution bullet asks for. It runs `sphinx-build -b linkcheck source _build/linkcheck` from `docs/`, and it is not in `env_list` (Phase 72, QUA-13).
- The still-open part is the CI job that would run it. That is **QUA-08**, a Future requirement in `.planning/REQUIREMENTS.md`, deferred by the owner on 2026-09-13.
- A future pickup must plan a side PR to `main` from the start, because GitHub runs `schedule` only on the default branch and `workflow_dispatch` only for a workflow file on it (ROADMAP v0.9.5 constraint 4). v0.9.3 did the same for `dependabot.yml`, in PR #137.
```

D07_NOTE = appended
