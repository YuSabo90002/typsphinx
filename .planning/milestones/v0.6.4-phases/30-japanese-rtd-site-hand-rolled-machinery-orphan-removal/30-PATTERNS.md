# Phase 30: Hand-Rolled Multi-Language Machinery & Orphan Removal - Pattern Map

**Mapped:** 2026-07-26
**Files analyzed:** 12 (touched/deleted), all pre-existing — no new files are created by this phase
**Analogs found:** 12 / 12 (this phase's own commit history supplies the pattern directly for the deletion tasks; the CI/config-edit tasks are precise line-anchor edits with no meaningful "analog" beyond the file's own surrounding context)

**Anchor verification note:** all line numbers below were re-read from the current tree this
session (commit `944de9c`), not copied from `30-CONTEXT.md`. `docs/source/conf.py` matched
`30-RESEARCH.md`'s anchors exactly (lines 67, 71-73, 76-82, 85-94). `tests/test_readthedocs_config.py`'s
docstring at lines ~288-297 is **already correct** (cites Phase 30.1 D-04/D-05, not the
superseded D-11) — do not write a task to "fix" it; only the four `html_context["language"]`
assertions (lines 304, 312, 320, 328) need repointing to `module._resolve_language()`.

## File Classification

| File | Role | Data Flow | Action | Closest Analog | Match Quality |
|------|------|-----------|--------|-----------------|----------------|
| `docs/build_multilang.py` | utility (build script) | file-I/O / batch | delete whole file | — (self-contained, no analog needed) | n/a |
| `docs/source/_templates/language-switcher.html` | component (Jinja template) | request-response (render-time) | delete whole file | — | n/a |
| `docs/source/_templates/page.html` | component (Jinja template) | request-response | delete whole file | — | n/a |
| `docs/source/_static/custom.css` | config/asset | n/a | delete whole file | — | n/a |
| `docs/source/conf.py` | config | transform (build config) | trim 4 blocks, keep seam | itself — before/after diff is the pattern | exact (self) |
| `docs/Makefile` | config (build orchestration) | batch | delete 3 targets + `.PHONY` entries | itself | exact (self) |
| `tox.ini` | config (task runner) | batch | delete `[testenv:docs-multilang]` section | `[testenv:docs-html]` / `[testenv:docs-pdf]` (surviving sibling sections show exact block shape) | exact |
| `.github/workflows/docs.yml` | CI pipeline (YAML) | event-driven (push/PR triggers) | rename one step, delete one step, repoint 3 paths | itself — surviving steps (`Upload PDF artifact`, `Upload PDF to Release`) show the untouched step shape | exact (self) |
| `docs/usage.rst` | documentation source | n/a (static content) | delete whole file | Phase 27's `docs/configuration.rst` deletion (commit `90801cf`) | exact — same orphan class |
| `docs/installation.rst` | documentation source | n/a | delete whole file | Phase 27's `docs/configuration.rst` deletion (commit `90801cf`) | exact — same orphan class |
| `tests/test_documentation_usage.py` | test (collateral) | n/a | delete whole file, same commit as subject | Phase 27's `tests/test_documentation_configuration.py` deletion (same commit `90801cf`) | exact |
| `tests/test_documentation_installation.py` | test (collateral) | n/a | delete whole file, same commit as subject | same as above | exact |
| `tests/test_readthedocs_config.py` | test (unit, module-load) | request-response (assert-only) | repoint 4 assertions, lines 304/312/320/328 | itself — surrounding `test_language_seam_precedence` structure | exact (self) |
| `docs/locale/ja/**` (13 `.po` + 13 `.mo`) | data (locale catalogs) | file-I/O | `git rm -r` whole directory | Phase 27's precedent of clean `git rm` + verify-green-after | exact — same deletion discipline, different asset class |

## Pattern Assignments

### Orphan-doc deletion pattern (`docs/usage.rst`, `docs/installation.rst` + collateral tests)

**Analog:** commit `90801cf` — "docs(27-01): delete orphan configuration.rst + its collateral test"

This is the load-bearing precedent for Phase 30's biggest risk (milestone invariant #5: "delete
collateral tests in the same commit as their subjects, or pytest goes red").

**Commit shape to copy** (`git show 90801cf --stat`):
```
 docs/configuration.rst                    | 489 ------------------------------
 tests/test_documentation_configuration.py | 155 ----------
 2 files changed, 644 deletions(-)
```
i.e. exactly two files deleted, zero files added, zero files modified, in one atomic commit.

**Commit message shape to copy** (verbatim structure, adapt content):
```
docs(27-01): delete orphan configuration.rst + its collateral test

- git rm docs/configuration.rst (489-line orphan, no conf.py in its
  tree, never built; wrong package name sphinxcontrib.typst at lines
  20/299/449)
- git rm tests/test_documentation_configuration.py (11 functions
  hard-assert the orphan exists; deleting one without the other
  turns pytest red — RESEARCH Pitfall 1)
- Salvage-nothing decision: content superseded by
  docs/source/user_guide/configuration.rst; wrong package name;
  typst_elements example uses phantom mainfont/monofont keys the
  CONF-04 allowlist rejects (D-05)
- Sibling doc-existence tests (test_documentation_usage.py,
  test_documentation_installation.py) verified green, untouched
```
Adapt for Phase 30: cite D-11 (no `usage`/`installation` docname under `docs/source/`, 606-line
and 213-line orphans, unreferenced by any toctree), note `docs/source/installation.rst` (76
lines, toctree-live) is the untouched sibling this time, exactly as the Phase 27 commit noted
`test_documentation_usage.py`/`test_documentation_installation.py` were the untouched siblings
then.

**Verification discipline to copy:** run the full `pytest` suite *after* the deletion commit
lands (not just the touched test files) — this is what the Phase 27 commit message means by
"verified green" and what ROADMAP SC#4 requires here. `RESEARCH Pitfall 1` cross-reference in
the old message maps to this phase's Pitfall 2 (`docs/locale/` omission) as the analogous "don't
trust the checklist, re-derive" caution.

---

### `docs/locale/ja/` bulk deletion (D-06 catalog relocation cleanup, PD-01)

**Analog:** same Phase 27 commit's `git rm` discipline, applied to a directory instead of two
files — `git rm -r docs/locale/` (26 tracked files: 13 `.po` + 13 `.mo`, several force-added past
`.gitignore`'s `*.mo` rule per Pitfall 2).

**Empirical safety check already performed** (30-RESEARCH.md, cite in the commit/verification
record rather than re-deriving): temporarily removing `docs/locale/` and running
`sphinx-build -b html docs/source <tmp>` with no env vars succeeds, `build succeeded, 2 warnings`
— identical warning count to baseline. No new warning introduced by the directory's absence.

---

### `docs/source/conf.py` trim (switcher-only blocks, seam untouched)

**Analog:** the file itself — before/after block boundaries, current tree read this session:

**Blocks to DELETE** (verbatim current text, lines 66-94):
```python
html_static_path = ["_static"]                      # line 67 -- DELETE

# Add custom CSS for language switcher                # lines 70-73 -- DELETE (comment + block)
html_css_files = [
    "custom.css",
]

# Language switcher configuration                      # lines 75-82 -- DELETE (comment + block)
html_context = {
    "language": language,
    "languages": [
        ("en", "English"),
        ("ja", "日本語"),
    ],
}

# Add language switcher to sidebar                      # lines 84-94 -- DELETE (comment + block)
html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "language-switcher.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
    ]
}
```

**Lines that MUST survive byte-for-byte** (do not touch, per anti-pattern list):
- Lines 51-56 — `_resolve_language()` / `language = _resolve_language()` (Phase 29 seam, shared with the ja translations repo's own `conf.py` copy)
- Lines 58-61 — `locale_dirs` / `gettext_*` (harmless no-op locally once `docs/locale/` is gone; shared byte-for-byte with translations repo)
- Lines 66 (`html_theme = "furo"`) and 68 (`html_title = ...`) — the two `html_*` lines that are NOT switcher-related, sit between the deleted blocks
- Lines 96-139 — the entire `typst_documents`/`typst_use_mitex`/`typst_template`/`derive_typst_lang` block (Phase 30.1's font-config territory, unrelated)

**Resulting surviving `-- Options for HTML output --` section:**
```python
html_theme = "furo"
html_title = f"{project} {release}"

# -- Options for typst/typstpdf output ---------------------------------------
```

---

### `docs/Makefile` trim (D-12, D-13)

**Analog:** the file itself, lines 15/17-32/34-43 vs. surviving lines 1-14 + 45-48.

**Delete:**
```makefile
.PHONY: help Makefile gettext locale-init locale-update html-ja multilang serve-multilang
# (replace with:) .PHONY: help Makefile

# Internationalization (i18n) targets
gettext:
	@$(SPHINXBUILD) -M gettext "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "Build finished. The message catalogs are in $(BUILDDIR)/gettext."

locale-init:
	sphinx-intl update -p $(BUILDDIR)/gettext -l ja
	@echo "Locale initialized. Translation files are in locale/ja/LC_MESSAGES/."

locale-update:
	sphinx-intl update -p $(BUILDDIR)/gettext -l ja
	@echo "Locale updated. Translation files are in locale/ja/LC_MESSAGES/."

html-ja:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html-ja" -D language=ja $(SPHINXOPTS) $(O)
	@echo "Build finished. The Japanese HTML pages are in $(BUILDDIR)/html-ja."

# Multi-language build for GitHub Pages
multilang:
	python build_multilang.py
	@echo "Multi-language build complete. Output in $(BUILDDIR)/multilang/"

# Serve multi-language docs locally
serve-multilang: multilang
	@echo "Starting local server at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	cd $(BUILDDIR)/multilang && python -m http.server 8000
```

**Surviving file in full** (verify against this after edit):
```makefile
# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
```

---

### `tox.ini` trim

**Analog:** the surviving `[testenv:docs-html]` (lines 53-60) / `[testenv:docs-pdf]` (lines
62-69) sections show the exact block shape that stays; `[testenv:docs-multilang]` (lines 78-84)
is the block to delete whole, including its blank-line separator from the preceding `[testenv:docs]`
section:
```ini
[testenv:docs-multilang]
description = Build multi-language HTML documentation (English + Japanese)
runner = uv-venv-lock-runner
extras = docs
changedir = docs
commands =
    python build_multilang.py
```
`[testenv:docs]` (lines 69-76, the combined HTML+PDF env) is untouched — it is not in the
deletion set and does not reference `build_multilang.py`.

---

### `.github/workflows/docs.yml` surgery (D-14)

**Analog:** the file itself — surviving steps (`Upload PDF artifact` lines 51-55, `Upload PDF to
Release` lines 65-71) show the untouched step shape/indentation to match.

**Current (lines 34-49, 62), read this session:**
```yaml
      - name: Build multi-language HTML documentation
        run: uv run tox -e docs-multilang

      - name: Build PDF documentation (English only)
        run: uv run tox -e docs-pdf

      - name: Copy PDF to multi-language build (English version)
        run: |
          mkdir -p docs/_build/multilang/en
          cp docs/_build/pdf/*.pdf docs/_build/multilang/en/

      - name: Upload HTML artifact
        uses: actions/upload-artifact@v7
        with:
          name: documentation-html
          path: docs/_build/multilang
      ...
          publish_dir: ./docs/_build/multilang
```

**After (per D-14 — repoint, do not delete the deploy step itself; that is Phase 32's CI-04):**
```yaml
      - name: Build HTML documentation
        run: uv run tox -e docs-html

      - name: Build PDF documentation (English only)
        run: uv run tox -e docs-pdf

      - name: Upload HTML artifact
        uses: actions/upload-artifact@v7
        with:
          name: documentation-html
          path: docs/_build/html
      ...
          publish_dir: ./docs/_build/html
```
The `Copy PDF to multi-language build` step is deleted entirely (no replacement — the PDF now
only exists via its own separate `Upload PDF artifact` / `Upload PDF to Release` steps, both
verbatim-unchanged). `permissions:` block (lines 10-13) and both trigger blocks (lines 3-8) are
untouched.

---

### `tests/test_readthedocs_config.py` repointing (SC#4, Claude's discretion item)

**Analog:** the file itself — `test_language_seam_precedence` (starts at line 288), all four
occurrences at lines 304, 312, 320, 328 share the identical line shape.

**Current (×4, lines 304/312/320/328):**
```python
    assert module.html_context["language"] == module.language
```

**After (×4) — assert the resolver/assignment relationship directly since `html_context` no
longer exists in `conf.py`:**
```python
    assert module._resolve_language() == module.language
```

**Docstring note:** the paragraph at lines ~292-296 currently reads *"A final wiring assertion
checks that `html_context["language"]` reads the same resolved value..."* — this needs updating
to describe the new assertion shape (re-call `_resolve_language()` directly), but the
**PDF-no-language-flag docstring at lines ~261-266 is already correct** (already cites Phase
30.1 D-04/D-05, not the superseded D-11) — do not write a task to touch it; confirm-only.

---

## Shared Patterns

### Deletion-commit discipline (applies to all `git rm` tasks in this phase)
**Source:** commit `90801cf` (Phase 27)
**Apply to:** `docs/usage.rst` + `tests/test_documentation_usage.py`,
`docs/installation.rst` + `tests/test_documentation_installation.py`, `docs/locale/ja/**`,
`docs/build_multilang.py`, `docs/source/_templates/{language-switcher,page}.html`,
`docs/source/_static/custom.css`
- One atomic commit per logical deletion unit (subject file + its hard-asserting test together, per milestone invariant #5)
- Commit message states: what's deleted, why (measured fact, not assumption), which sibling file/test was checked and confirmed untouched
- Full `pytest` run *after* the commit, not just the touched test files, as the actual proof (ROADMAP SC#4's "a green build proves nothing about content" caveat notwithstanding — this is about deletion, not content)

### Repo-wide grep as verification gate, not a committed script
**Source:** `30-RESEARCH.md` Pitfall 1 + Wave 0 Gaps; consistent with this project's D-03
(sibling Phase 30.1 decision) "commit no comparison script (unreachable-from-CI gates look like
they never run)"
**Apply to:** SC#1's switcher-token grep, SC#3's orphan-reference grep
- Run by hand, paste exact command + output into the verification record
- Scope `html_static_path` to `docs/source/conf.py`'s single instance (Pitfall 1) — do not treat `examples/basic/conf.py:25`, `examples/advanced/conf.py:30`, `tests/fixtures/static_asset_copy_render_gate/conf.py:25,27`, `tests/fixtures/glob_image_render_gate/conf.py:29,31` as violations
- Known-good false positives that must survive: `tests/fixtures/confval_field_body_render_gate/index.rst:15`, `tests/test_readthedocs_config.py`'s (repointed) `html_context`-derived assertions

## No Analog Found

None. Every touched/deleted file either has a direct prior-phase deletion precedent (Phase 27,
commit `90801cf`) or is self-analogous (the edit is a precise trim against the file's own
surrounding untouched context, verified against the current tree this session).

## Metadata

**Analog search scope:** full git history (`git log --oneline --all`), current-tree reads of
`docs/source/conf.py`, `docs/Makefile`, `tox.ini`, `.github/workflows/docs.yml`,
`tests/test_readthedocs_config.py`
**Files scanned:** 7 read in full this session + 1 historical commit diff (`90801cf`)
**Pattern extraction date:** 2026-07-26
