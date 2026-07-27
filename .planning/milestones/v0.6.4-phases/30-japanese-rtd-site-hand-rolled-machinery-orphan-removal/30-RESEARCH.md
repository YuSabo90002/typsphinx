# Phase 30: Hand-Rolled Multi-Language Machinery & Orphan Removal - Research

**Researched:** 2026-07-26
**Domain:** Deletion/refactor of hand-rolled Sphinx multi-language build tooling, CI workflow surgery, orphan-doc removal — no new technology, no new dependency. Every finding below is a direct measurement of the current tree (`git rev-parse HEAD` = `944de9c`, working tree clean at research time), not a general best-practices lookup.
**Confidence:** HIGH — all claims are `[VERIFIED: <local measurement>]` against the live repository; nothing in this phase requires external library research.

## Summary

This phase deletes, not adds. There is no new stack to select — the "standard stack" for this
phase is "grep, git rm, and the existing test suite." The research effort here was spent
re-measuring the current tree against `30-CONTEXT.md`'s decisions and the ROADMAP's success
criteria, because both explicitly warn that the CONTEXT.md measurements predate Phase 30.1's
execution and must not be trusted blindly (milestone invariant #4, and the phase's own
"Current-tree note").

Two re-measurements changed the plan's shape from what CONTEXT.md assumed:

1. **A fresh repo-wide grep for `html_static_path` finds MORE false positives than CONTEXT.md's
   two documented ones.** `examples/basic/conf.py:25`, `examples/advanced/conf.py:30`,
   `tests/fixtures/static_asset_copy_render_gate/conf.py:25,27`, and
   `tests/fixtures/glob_image_render_gate/conf.py:29,31` all contain the literal string
   `html_static_path` and are wholly unrelated to the language switcher. CONTEXT.md's own
   "Multilang token grep" measurement (`<specifics>`) never actually grepped for this token — it
   was added to SC#1's token list later, as a Claude's-discretion decision, without a fresh
   repo-wide grep to back it. **SC#1's grep must be scoped to `docs/source/conf.py`'s instance
   only** (or the false-positive exclusion list expanded to include these four files) — a literal
   "zero hits anywhere in the repo" reading of SC#1 would demand deleting `html_static_path` from
   two bundled example projects and two unrelated test fixtures, which is out of scope and would
   break them.
2. **`docs/locale/ja/` (26 git-tracked files: 13 `.po` + 13 `.mo`, force-added despite the
   `.gitignore`'s blanket `*.mo` rule) still needs an explicit deletion task in this phase.** It
   is not named in the phase's five ROADMAP success criteria, but `STATE.md`'s Phase 30.1
   carry-forward (PD-01) is unambiguous: *"`docs/locale/ja/`'s deletion belongs to Phase 30 ...
   delete here in Phase 30."* Empirically confirmed safe: deleting `docs/locale/` entirely and
   rebuilding `docs-html` for English succeeds with the same 2 pre-existing warnings as the
   baseline (measured this session, see Common Pitfalls). The planner must add this as an explicit
   task even though the ROADMAP SC bullets don't spell it out by name.

Everything else in `30-CONTEXT.md` checked out exactly as measured: token locations, line
anchors (with the current tree's `conf.py` reordered slightly by Phase 30.1's font-config
addition — new anchors below), the two known false positives, and the fact that
`test_readthedocs_config.py`'s no-language-flag docstring **is already fixed** (see Pitfall 4 —
one less task than `30-CONTEXT.md` implied).

**Primary recommendation:** Treat this as a pure deletion + line-anchor-precise-edit phase. Do the
fresh repo-wide grep from this document (not from `30-CONTEXT.md`) as the SC#1 gate, delete
`docs/locale/` explicitly, and budget one manual-merge step for the deletion guard.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Language switching UX | CDN / Static (RTD flyout, external) | — | Read the Docs' own flyout replaces the in-repo switcher; nothing in this repo implements it after this phase |
| Multi-language HTML build | Build Tooling / Task Runner (`tox`, `docs.yml`) | — | `docs-html`/`docs-pdf` tox envs already build a single-language tree; RTD's per-project builds (Phase 30.1) replace the multilang orchestration |
| `conf.py` language resolution | Documentation Source (Sphinx config) | — | `_resolve_language()` / `language` assignment stay — this is Phase 29's seam, explicitly out of scope for deletion |
| Locale catalog storage | Database / Storage (git-tracked `.po`/`.mo` as flat files) | — | `docs/locale/ja/` is source-controlled data, not code; its removal is a data-migration-style deletion (already copied to `typsphinx-doc-translations`, Phase 30.1), not a code refactor |
| CI publish pipeline | CI/CD (`docs.yml`) | CDN / Static (GitHub Pages) | `docs.yml` orchestrates the build and the `peaceiris/actions-gh-pages` publish step; this phase repoints paths only, does not touch the `gh-pages` branch itself (Phase 32) |
| Orphan doc removal | Documentation Source | Test Suite (hard-asserting tests) | `docs/usage.rst` / `docs/installation.rst` and their test files are deleted together — a documentation-content concern with a test-suite collateral |

## User Constraints

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-11:** `docs/usage.rst` is deleted whole — nothing is salvaged (606 lines, no `usage`
  docname exists under `docs/source/`, referenced by no toctree). `docs/installation.rst`
  (213 lines, root orphan) goes the same way; `docs/source/installation.rst` (76 lines,
  toctree-live) is untouched. Milestone invariant #5: `tests/test_documentation_usage.py` and
  `tests/test_documentation_installation.py` are deleted in the *same commit* as their subjects.
- **D-12:** `docs/Makefile`'s `gettext` / `locale-init` / `locale-update` move to the translations
  repository. All three targets leave `docs/Makefile`.
- **D-13:** `docs/Makefile:31-33`'s `html-ja` target is deleted (once `docs/locale/ja/` leaves
  this repository, `-D language=ja` finds no catalogs and renders 100% English silently).
- **D-14:** `docs.yml`'s gh-pages deploy step is repointed, not removed: change
  `publish_dir: ./docs/_build/multilang` → `./docs/_build/html`. Deleting the step itself is
  Phase 32's work (CI-04).
- **`custom.css` (Claude's discretion, exercised):** all 7 rules in `custom.css` are
  `.language-switcher` selectors and `_static/` contains nothing else — delete `custom.css`,
  `conf.py`'s `html_css_files`, and `html_static_path` (an empty, untracked `_static/` with
  `html_static_path` still pointing at it makes Sphinx warn).
- **D-15:** The work splits into Phase 30 (this phase: I18N-02, DOC-08 — machinery + orphan
  removal) and Phase 30.1 (translations repo + Japanese site: I18N-01, I18N-03 — **already
  complete**, UAT passed). Ordering constraint: Phase 30's deletions must not run ahead of Phase
  30.1's replacement being confirmed working — **satisfied**: Phase 30.1 is complete and its
  Japanese site has been observed serving (STATE.md).
- **PD-01 (STATE.md carry-forward, not in ROADMAP SC list):** `docs/locale/ja/`'s deletion
  belongs to Phase 30 — Phase 30.1 copied the catalogs to `typsphinx-doc-translations` but did
  not delete the local copies; do not "fix" by regenerating here, delete here.

### Claude's Discretion

- SC#1's grep pass/fail rule — two measured false positives (`confval_field_body_render_gate`
  fixture, `test_readthedocs_config.py`'s `html_context` assertions) must survive.
  **Research finding: this list is incomplete against the current tree — see Pitfall 1.**
- Exact shape/wiring is not applicable here (no new repo being created in this phase).
- Whether Furo's default sidebar (restored once `html_sidebars` is removed) needs any further
  `conf.py` adjustment. **Research finding: see Pitfall 3 — it does, if the ad widget is
  unwanted, but SC#2 mandates full deletion of the key regardless.**

### Deferred Ideas (OUT OF SCOPE)

- Raising ja catalog coverage above 24.3% — separate future work.
- Retiring D-07's two-repository tagging — revisit after a release or two.
- RTD Default Version / branch flips — Phase 33 handoff.
- PR preview builds (RTD-05) — Future.
- Browser-language auto-redirect at the documentation root — accepted loss, not reimplemented.
- README / `pyproject.toml` / About URL rewrites, repo-wide link guard — Phase 31.
- GitHub Pages teardown (disabling Pages, deleting `gh-pages` branch) — Phase 32.
- Version bump and CHANGELOG — Phase 33.
- **No `typsphinx/` runtime code change at all** (milestone invariant #3).
</user_constraints>

## Phase Requirements

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| I18N-02 | Hand-rolled multi-language publishing machinery gone; RTD flyout is the only switcher | Full token inventory below (Code Examples, Common Pitfalls); confirmed all 8 SC#1 tokens' current locations; confirmed `docs/locale/` deletion is also required by STATE.md PD-01 though absent from the SC bullet text |
| DOC-08 | `docs/usage.rst` / `docs/installation.rst` orphan pair resolved, tests green after | Confirmed zero toctree reachability, zero external references outside the two hard-asserting test files and `CHANGELOG.md`; confirmed `docs/source/installation.rst` is a distinct, untouched, toctree-live file |
</phase_requirements>

## Standard Stack

Not applicable in the conventional sense — no new library is installed. The "stack" for this
phase is entirely tools already in the repo:

| Tool | Version (measured) | Purpose | Why Standard |
|------|---------------------|---------|---------------|
| `git rm` / manual `Edit` | (n/a) | Delete files, edit surviving files | No package needed |
| `grep -rn` (repo-wide) | GNU grep, system | SC#1's verification gate | Exactly what the ROADMAP SC asks for |
| `pytest` | 9.1.1 [VERIFIED: `uv run pytest` output, this session] | Full-suite green-after-deletion proof (DOC-08 SC#3) | Already the project's test runner |
| `tox` (`docs-html`, `docs-pdf` envs) | tox 4.56+/tox-uv 1.35 [CITED: tox.ini] | Green-build gates (SC#5) | Already the project's docs-build entry point |
| `sphinx-build` | Sphinx 9.1.0 [VERIFIED: sphinx-build --version, this session] | Underlying HTML/PDF build | Unchanged by this phase |

**No `npm install` / `pip install` / `cargo add` of any kind is needed for this phase.**

## Package Legitimacy Audit

Not applicable — this phase installs no packages, adds no dependency, and touches no
`pyproject.toml` dependency list. (One adjacent observation, not an action item: `sphinx-intl>=2.0`
in the `docs` extra becomes unused by any local task once `docs/Makefile`'s `locale-init` /
`locale-update` targets leave per D-12 — see Open Questions. This is not a legitimacy concern,
just a potential future cleanup.)

## Architecture Patterns

### System Architecture Diagram

```
   git push to main / tag push
            |
            v
   .github/workflows/docs.yml (build-docs job)
            |
            +--> Setup Python 3.12, install uv, `uv sync --extra dev --extra docs`
            |
            +--> [BEFORE] tox -e docs-multilang --> build_multilang.py
            |               |                          |
            |               |                          +--> sphinx-build -b html (en, SPHINX_LANGUAGE=en)
            |               |                          +--> sphinx-build -b html (ja, SPHINX_LANGUAGE=ja)
            |               |                          +--> writes docs/_build/multilang/{en,ja}/ + redirect index.html
            |               |
            |               v
            |    [AFTER, this phase] tox -e docs-html --> sphinx-build -b html source _build/html
            |               (single English tree; docs/source/conf.py's language=_resolve_language()
            |                still resolves "en" locally / via READTHEDOCS_LANGUAGE on RTD)
            |
            +--> tox -e docs-pdf --> sphinx-build -b typstpdf --> docs/_build/pdf/*.pdf
            |
            +--> [BEFORE] mkdir + cp PDF into docs/_build/multilang/en/
            |    [AFTER, this phase] step deleted entirely (D-14) -- PDF stays only as its own
            |                        separate upload-artifact + Release attachment
            |
            +--> Upload HTML artifact: docs/_build/multilang --> [AFTER] docs/_build/html
            +--> Upload PDF artifact: docs/_build/pdf/*.pdf (unchanged)
            |
            +--> peaceiris/actions-gh-pages (push to main only)
            |         publish_dir: ./docs/_build/multilang --> [AFTER] ./docs/_build/html
            |         (still deploys to gh-pages branch -- that branch/feature is Phase 32's to remove)
            |
            +--> softprops/action-gh-release (tag push only, unchanged)

   Separately, docs/source/conf.py (shared byte-for-byte with typsphinx-doc-translations' ja
   project, per Phase 30.1):
       _resolve_language() / language = ...        <- STAYS (Phase 29 seam, both RTD projects depend on it)
       locale_dirs / gettext_* config               <- STAYS (harmless no-op for English when
                                                         docs/locale/ is absent locally; still needed
                                                         by the ja translations repo's own copy of
                                                         this file, which points at ITS OWN locale/)
       html_static_path / html_css_files / html_context / html_sidebars   <- DELETED (this phase)
       typst_documents / typst_use_mitex / typst_template / derive_typst_lang(...)  <- STAYS (Phase 30.1's
                                                         unrelated font-config addition; do not touch)
```

### Recommended Task Grouping

Not a new project structure (nothing is being scaffolded) — group tasks by blast radius instead:

1. **CI + task-runner surgery** (no runtime behavior change until next `main` push):
   `tox.ini` (`[testenv:docs-multilang]` removed), `.github/workflows/docs.yml` (step
   rename/removal/path repoints), `docs/Makefile` (6 targets removed).
2. **Switcher asset + conf.py surgery**: delete `build_multilang.py`,
   `_templates/{language-switcher,page}.html`, `_static/custom.css`; edit `conf.py`'s 4
   switcher-only blocks; leave the language-resolution and Typst blocks untouched.
3. **`docs/locale/` removal** (PD-01 — not in the ROADMAP SC list but required by STATE.md):
   `git rm -r docs/locale/` (26 tracked files).
4. **Orphan doc pair + collateral tests, single commit** (milestone invariant #5):
   `docs/usage.rst`, `docs/installation.rst`, `tests/test_documentation_usage.py`,
   `tests/test_documentation_installation.py`.
5. **`test_readthedocs_config.py` repair** (repointed, not deleted — SC#4): the 4
   `html_context["language"]` assertions.
6. **Full-suite + docs-build verification, fresh grep as the gate** (SC#1, SC#3, SC#5).

### Anti-Patterns to Avoid

- **Trusting `30-CONTEXT.md`'s grep list as the final word.** It predates Phase 30.1's execution
  and its own text says so. Re-run the grep from this document (or fresher) immediately before
  the deletion commit.
- **Deleting `html_static_path` wherever the string appears.** It is a generic Sphinx confval
  name that legitimately exists in `examples/basic/conf.py`, `examples/advanced/conf.py`, and two
  test fixtures for reasons unrelated to the language switcher. Only `docs/source/conf.py:67`'s
  instance is in scope.
- **Leaving `docs/locale/` in the tree "because the SC list didn't mention it."** STATE.md's PD-01
  is explicit and was written specifically to prevent this omission.
- **Touching `docs/source/conf.py`'s `locale_dirs` / `gettext_*` block.** That block is unrelated
  to the switcher and is shared byte-for-byte with the ja translations repo's own `conf.py` copy
  (Phase 30.1) — deleting it here would not affect the ja project (different file) but would be
  needless scope creep and diverge from the intentionally-shared file.
- **Touching the `typst_template` / `derive_typst_lang` block (conf.py lines ~104–139).** This
  is Phase 30.1's font-config gap-closure work, added after `30-CONTEXT.md`'s line-anchor
  measurements — completely unrelated to the switcher and must survive byte-for-byte.

## Don't Hand-Roll

Not applicable — this phase removes hand-rolled code, it does not add any. There is no
"don't-hand-roll" library substitution here; the whole point is that RTD's own flyout (already
proven working in Phase 30.1) replaces the custom `build_multilang.py` + Furo sidebar override.

**Key insight:** the thing this phase deletes *was* the hand-rolled solution to a problem
(multi-language Sphinx docs) that Read the Docs solves natively via separate per-language
projects + its flyout — which is exactly why Phase 30.1 exists and this phase is safe to run
after it.

## Common Pitfalls

### Pitfall 1: SC#1's `html_static_path` grep token is broader than the SC's own exclusion list

**What goes wrong:** Running a literal repo-wide grep for `html_static_path` and treating every
hit as a violation would flag `examples/basic/conf.py:25`, `examples/advanced/conf.py:30`,
`tests/fixtures/static_asset_copy_render_gate/conf.py:25,27`, and
`tests/fixtures/glob_image_render_gate/conf.py:29,31` — none of which relate to the language
switcher.

**Why it happens:** SC#1's token list was assembled partly from `30-CONTEXT.md`'s "Multilang
token grep" measurement (which never actually grepped for `html_static_path`) and partly from a
later Claude's-discretion decision (delete `html_static_path` from `docs/source/conf.py`
specifically, alongside `custom.css`). The generic confval name was never re-checked against the
whole repo before landing in the SC wording.

**How to avoid:** Scope the SC#1 verification either to (a) `docs/source/conf.py` specifically
for the `html_static_path` token (grep the file, not the repo, for that one token), or (b) add
the four files above to the exclusion list explicitly, the same way the confval fixture and
`test_readthedocs_config.py` are excluded. Recommendation: (a) is simpler and matches the intent
— the SC's real concern is "no *switcher-related* `html_static_path` reference survives," not
"the string never appears in the repo."

**Warning signs:** A verification script that does `grep -rn html_static_path .` and expects zero
hits will find 6 non-switcher-related lines and incorrectly fail the phase.

**Measured (this session), repo-wide grep excluding `.git`/`.planning`/`CHANGELOG.md`:**
```
docs/build_multilang.py:86        (sessionStorage — different token, shown for completeness)
tox.ini:78,84                     (docs-multilang)
docs/source/_static/custom.css    (7 hits, whole file deleted)
docs/source/_templates/language-switcher.html:2
docs/Makefile:15,30,31,32,36,40
docs/source/_templates/page.html:8
docs/source/conf.py:67,72,76,85,90
examples/basic/conf.py:25                                    <- FALSE POSITIVE (html_static_path)
examples/advanced/conf.py:30                                  <- FALSE POSITIVE (html_static_path)
tests/test_readthedocs_config.py:294,304,312,320,328          <- KNOWN false positive (repaired, not deleted)
tests/fixtures/static_asset_copy_render_gate/conf.py:25,27     <- FALSE POSITIVE (html_static_path)
tests/fixtures/confval_field_body_render_gate/index.rst:15     <- KNOWN false positive (must survive)
tests/fixtures/glob_image_render_gate/conf.py:29,31            <- FALSE POSITIVE (html_static_path)
.github/workflows/docs.yml:35
```

### Pitfall 2: `docs/locale/` is not in the ROADMAP SC bullets but is required by STATE.md

**What goes wrong:** Planning strictly off the five ROADMAP success criteria (as reproduced in
this phase's brief) would leave `docs/locale/ja/`'s 26 git-tracked files (13 `.po` + 13 `.mo`,
several force-added past the `.gitignore`'s `*.mo` rule) in the tree after this phase, orphaned
now that `docs/Makefile`'s `locale-init`/`locale-update` (the only things that maintained them
locally) are gone.

**Why it happens:** `30-CONTEXT.md`'s discussion pre-dates the D-15 phase split and focused on
the *machinery*, not the catalog *data*; the catalog-relocation decision (D-06) technically
belongs to Phase 30.1, which executed it by *copying* the catalogs into
`typsphinx-doc-translations` — but never deleted the local copies. STATE.md's carry-forward
(PD-01) closes that gap explicitly.

**How to avoid:** Add an explicit task: `git rm -r docs/locale/` in the same wave as the
Makefile/`conf.py` surgery. Empirically confirmed safe (measured this session): temporarily
removing `docs/locale/` and running `sphinx-build -b html docs/source <tmp>` with no env vars set
(i.e., English, the RTD-parent-project default) succeeds — `build succeeded, 2 warnings` — the
exact same 2 pre-existing warnings (`visit_toctree` docstring indentation) as the baseline. No
new warning or error is introduced by the directory's absence.

**Warning signs:** `git status` after "completing" this phase still shows `docs/locale/` tracked;
a verifier grepping for `html-ja`/Makefile targets passes while the actual catalog files remain.

### Pitfall 3: Deleting `html_sidebars` restores MORE than "no switcher" — it restores Furo's ad widget too

**What goes wrong:** SC#2 requires `html_sidebars` to be gone from `conf.py` entirely (not
replaced with a filtered list). Once it's gone, Sphinx falls back to the Furo theme's own
built-in default, which is (measured from the installed `furo` package's `theme.conf`):
`sidebar/brand.html, sidebar/search.html, sidebar/scroll-start.html, sidebar/navigation.html,
sidebar/ethical-ads.html, sidebar/scroll-end.html, sidebar/variant-selector.html`. The *current*
custom list in `conf.py` (with `language-switcher.html` swapped in) is:
`sidebar/brand.html, sidebar/search.html, sidebar/scroll-start.html, language-switcher.html,
sidebar/navigation.html, sidebar/scroll-end.html` — it never included `ethical-ads.html` or
`variant-selector.html`. Deleting the key doesn't just remove the switcher — it silently
reintroduces Furo's "ethical ads" sidebar widget and the light/dark variant selector, neither of
which the project has ever shipped.

**Why it happens:** the project's custom `html_sidebars` was written against an older Furo
version and only ever explicitly listed a subset; the omission of `ethical-ads.html` was
presumably deliberate (or simply an artifact of when it was written) but was never a documented
decision either way.

**How to avoid:** This is not a blocker — SC#2's wording ("gone") is a locked decision, not
something to solve around. Flag it as an accepted, documented side effect in the phase's
verification record (similar to the browser-redirect accepted loss already documented) rather
than silently reintroducing ads without comment. If the owner wants to suppress the ad widget,
Furo's own `[options]` `announcement`/other keys don't cover this — the only way to keep
`ethical-ads.html` out while still deleting `html_sidebars` per SC#2 is a documented follow-up,
out of scope for this phase.

**Warning signs:** A UAT screenshot of the rebuilt docs shows an unexpected "This website relies
on ads..." widget or a variant-selector control that wasn't there before, and the reviewer isn't
sure whether that's a regression or expected.

### Pitfall 4: One item in SC#4 is *already done* — don't re-do it

**What goes wrong:** `30-CONTEXT.md`'s D-05 and the phase's own SC#4 both describe amending the
PDF no-language-flag assertion's docstring in `tests/test_readthedocs_config.py` because it
allegedly still cites "not a step toward the deferred Japanese PDF (D-11)". **Measured this
session: the current docstring (lines ~261–266) already reads** *"the Japanese PDF ships from a
different manifest in the typsphinx-doc-translations repository (Phase 30.1 D-04/D-05)"* — the
superseded D-11 rationale is already gone. This was evidently fixed during Phase 30.1's own
edits to this file (or was never actually stale by the time `30-CONTEXT.md` was written, despite
its description).

**Why it happens:** `30-CONTEXT.md` was written before Phase 30.1 executed; Phase 30.1 executed
and, as a side effect of its own PDF/language work, touched this docstring.

**How to avoid:** Verify the current docstring text before writing a task to "fix" it. Only the
four `html_context["language"]` assertions (lines 304, 312, 320, 328) and the docstring
paragraph that *describes* that assertion (lines ~288–297, which still says "A final wiring
assertion checks that `html_context["language"]` reads the same resolved value") genuinely need
repointing.

**Warning signs:** A task titled "amend docstring per D-05" with no diff to show for it, or a
diff that touches text that was already correct.

## Code Examples

### `conf.py` surgery (current tree, lines as measured this session)

```python
# docs/source/conf.py -- lines 63-95 currently read (KEEP the -- Options for HTML output --
# heading and html_theme; DELETE everything from html_static_path through the html_sidebars dict)

html_theme = "furo"
html_static_path = ["_static"]                      # <- DELETE (Claude's discretion, custom.css cleanup)
html_title = f"{project} {release}"

# Add custom CSS for language switcher
html_css_files = [                                   # <- DELETE (comment + block)
    "custom.css",
]

# Language switcher configuration
html_context = {                                     # <- DELETE (comment + block)
    "language": language,
    "languages": [
        ("en", "English"),
        ("ja", "日本語"),
    ],
}

# Add language switcher to sidebar
html_sidebars = {                                    # <- DELETE (comment + block) -- see Pitfall 3
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "language-switcher.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
    ]
}

# -- Options for typst/typstpdf output ---------------------------------------
# ^ everything from here down (typst_documents, typst_use_mitex, typst_template,
#   derive_typst_lang(...)) is UNTOUCHED -- Phase 30.1 territory, not this phase's.
```

Lines that MUST NOT move: 51–56 (`_resolve_language()` / `language = _resolve_language()`) and
58–61 (`locale_dirs` / `gettext_*`) stay exactly as-is — the former is Phase 29's cross-project
seam, the latter is shared byte-for-byte with the ja translations repo's own `conf.py` copy and
harmlessly no-ops locally once `docs/locale/` is gone (measured, see Pitfall 2).

### `test_readthedocs_config.py` repointing (SC#4)

```python
# Current (4 occurrences, lines 304/312/320/328):
    assert module.html_context["language"] == module.language

# Repointed -- html_context no longer exists in conf.py, so assert the resolver/assignment
# relationship directly instead of via the deleted dict:
    assert module._resolve_language() == module.language
```

And the docstring paragraph (lines ~293–296) describing the check:

```python
    # Before:
    # A final wiring assertion checks that `html_context["language"]` reads the same resolved
    # value -- this is what catches a helper that exists but is never called by the `language`
    # assignment.

    # After:
    # A final assertion re-calls `_resolve_language()` and checks it still matches `language` --
    # this is what catches a helper that exists but is never called by the `language` assignment
    # (I18N-02 deleted html_context itself; the wiring it used to prove is now proven directly).
```

### `docs.yml` surgery (SC#5, D-14)

```yaml
# Before (lines 34-49, 62):
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

# After:
      - name: Build HTML documentation
        run: uv run tox -e docs-html
      - name: Build PDF documentation (English only)
        run: uv run tox -e docs-pdf
      # (PDF-copy-into-multilang step deleted entirely)
      - name: Upload HTML artifact
        uses: actions/upload-artifact@v7
        with:
          name: documentation-html
          path: docs/_build/html
      ...
          publish_dir: ./docs/_build/html
```

The PDF upload-artifact step and `softprops/action-gh-release` step (unchanged, lines 51-71) both
stay verbatim.

### `docs/Makefile` surgery (D-12, D-13)

```makefile
# Delete lines 15 (.PHONY list), 17-32 (gettext/locale-init/locale-update/html-ja),
# 34-43 (multilang/serve-multilang comments + targets). Surviving file is just:

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
```

### `tox.ini` surgery

```ini
# Delete the entire [testenv:docs-multilang] section (lines 78-84). docs-html (53-60) and
# docs-pdf (62-69) survive unchanged -- they are this phase's green-build gates (SC#5).
```

## State of the Art

Not applicable — no external ecosystem drift is relevant to a pure-deletion phase. The one
relevant "current approach" fact: **RTD Addons (search, flyout) have been enabled by default
platform-wide since 2024-10-07** and need no `conf.py` wiring [CITED: REQUIREMENTS.md Out of
Scope table, already verified in an earlier phase] — this is precisely why the hand-rolled
switcher this phase deletes is no longer needed.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `sphinx-intl>=2.0` in `pyproject.toml`'s `docs` extra becomes unused once D-12's Makefile targets leave, but is out of scope to remove this phase | Package Legitimacy Audit / Open Questions | Low — an unused dev-time dependency, no functional impact, easy to clean up in a later phase if the owner wants |
| A2 | The four newly-found `html_static_path` false positives were not intentionally excluded by the owner (vs. a considered "leave them, they're fine" decision already made) | Pitfall 1 | Low — worst case the planner asks the owner to confirm the exclusion, costing one clarifying round |

**Both entries are LOW risk and process-only** — no claim here concerns correctness of the
deletion itself, only scope-boundary bookkeeping. All substantive claims in this document are
`[VERIFIED: local measurement]`.

## Open Questions

1. **Should `sphinx-intl>=2.0` be removed from `pyproject.toml`'s `docs` extra?**
   - What we know: it's only invoked by `docs/Makefile`'s `locale-init`/`locale-update` targets,
     which D-12 removes from this repo (they move to `typsphinx-doc-translations`).
   - What's unclear: whether leaving an unused-but-harmless dependency in the `docs` extra is
     acceptable, or whether "the machinery is gone" (I18N-02) should extend to this line.
   - Recommendation: leave it — SC#2's `conf.py`-confinement clause and the "Files this phase
     touches" list in `30-CONTEXT.md` never mention `pyproject.toml`, and removing a dependency
     line is a different risk class (could silently affect an unrelated future doc-translation
     tool need) than deleting dead template/CSS files. Flag as a fast-follow todo instead.

2. **Does the owner want Furo's default `ethical-ads.html` / `variant-selector.html` sidebar
   entries to appear once `html_sidebars` is deleted (Pitfall 3)?**
   - What we know: SC#2 mandates the key be gone entirely; Furo's true upstream default includes
     those two entries, which the project's custom list never had.
   - What's unclear: whether this was ever a deliberate choice to omit, or coincidental.
   - Recommendation: document the resulting sidebar diff in the phase's verification record as an
     explicit, observed, accepted side effect (not silently absorbed) — the same treatment given
     to the browser-redirect accepted loss elsewhere in this milestone.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `uv` | all commands (worktree isolation, `uv run`) | ✓ | 0.11.25 | — |
| `pytest` (via `uv run`) | full-suite green proof | ✓ | 9.1.1 | — |
| `sphinx-build` (via `uv run`) | `docs-html`/`docs-pdf` gates | ✓ | Sphinx 9.1.0 | — |
| `tox` / `tox-uv` | `docs-html`/`docs-pdf` tox envs | ✓ | pinned in `tox.ini` (`tox-uv~=1.35`) | — |
| `git` | deletion + worktree/merge workflow | ✓ | system | — |
| GNU `grep` | SC#1's repo-wide token verification | ✓ | system | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none — this phase needs nothing beyond what the repo
already provisions via `uv sync --extra dev --extra docs`.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 [VERIFIED: `uv run pytest` this session], config in `pyproject.toml` |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["tests"]`) |
| Quick run command | `uv run pytest tests/test_readthedocs_config.py -q` |
| Full suite command | `uv run pytest` (per CLAUDE.md's worktree-isolated execution mode) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| I18N-02 | No live reference to any of the 9 SC#1 tokens (scoped per Pitfall 1) | structural / grep-based | `grep -rn --exclude-dir=.git --exclude-dir=.planning --exclude=CHANGELOG.md -iE '<token-list>' .` | ❌ Wave 0 — no committed script exists; run by hand per the phase's own precedent (D-03 of this phase's sibling decisions: "commit no comparison script") |
| I18N-02 | `conf.py`'s switcher-only lines gone, `_resolve_language()`/`language` byte-unchanged | unit (module load) | `uv run pytest tests/test_readthedocs_config.py::test_language_seam_precedence -q` | ✅ (repointed, not new) |
| DOC-08 | Orphan pair + collateral tests deleted same commit, full suite green after | full suite | `uv run pytest -q` | ✅ (existing suite; the two test files are removed as part of this phase, not added) |
| I18N-02 / DOC-08 | `docs-html` / `docs-pdf` still green post-deletion | integration | `uv run tox -e docs-html && uv run tox -e docs-pdf` | ✅ |

### Sampling Rate

- **Per task commit:** `uv run pytest tests/test_readthedocs_config.py -q` (fast, targets the one
  repointed test file) plus a manual repo-wide grep after the switcher-deletion task.
- **Per wave merge:** full `uv run pytest -q` and both `tox -e docs-html` / `tox -e docs-pdf`.
- **Phase gate:** full suite green + fresh grep clean (Pitfall 1's scoped version) + an observed
  `docs.yml` CI run green, before `/gsd-verify-work`.

### Wave 0 Gaps

- No committed script for the SC#1 repo-wide grep — by design (this phase's own precedent from
  the sibling Phase 30.1 decisions: a committed comparison/grep script would look like a gate
  that never runs in CI, since nothing in `docs.yml` invokes it). Run it by hand, paste the exact
  command and output into the verification record.
- **Recommended, optional addition:** a small permanent regression test (e.g.
  `tests/test_no_multilang_machinery.py`) that greps the repo for the switcher-specific tokens
  (excluding `html_static_path`, which is out of scope per Pitfall 1) and fails if any reappear —
  mirroring the project's existing `test_preview_version_sync.py` pattern of "guard the invariant
  permanently, not just at deletion time." Not required by any SC, but consistent with the
  project's established defect-prevention style (dead-config sweep pattern, STATE.md).

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | This phase touches no auth surface |
| V3 Session Management | No — but see note | `docs/build_multilang.py`'s deleted redirect page used browser `sessionStorage` (client-side, non-sensitive, a UX flag only — not a security session) |
| V4 Access Control | No | N/A |
| V5 Input Validation | Marginal | The grep-based SC#1 verification is a text-matching script, not user input handling — no injection surface |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| CI workflow file (`docs.yml`) edited to change a `publish_dir` / artifact path | Tampering (low severity) | Standard code review of the diff; no secrets or permissions are touched by this phase's edits (permissions block unchanged) |
| Deleting a client-side script (`build_multilang.py`'s `sessionStorage`/`navigator.language` redirect) | N/A | No security implication — pure UX regression, already accepted (browser-language auto-redirect loss, documented in CONTEXT.md `<deferred>`) |

This phase has essentially no security surface. It removes client-side JS (session-storage flag,
non-sensitive) and edits CI YAML for path/step bookkeeping only — no permissions, secrets, or
auth-adjacent code is touched.

## Sources

### Primary (HIGH confidence — all local measurement, this session)
- `docs/source/conf.py` (154 lines) — read in full, current line anchors confirmed
- `docs/Makefile`, `tox.ini`, `.github/workflows/docs.yml` — read in full
- `docs/build_multilang.py`, `docs/source/_templates/{language-switcher,page}.html`,
  `docs/source/_static/custom.css` — read in full
- `tests/test_readthedocs_config.py` (328 lines) — read in full, confirmed Pitfall 4's finding
- `tests/test_documentation_usage.py`, `tests/test_documentation_installation.py` — read in full
- `docs/usage.rst`, `docs/installation.rst`, `docs/source/installation.rst` — spot-checked,
  toctree-reachability cross-checked against `docs/source/index.rst`
- `tests/fixtures/confval_field_body_render_gate/index.rst` — confirmed false-positive shape
- Repo-wide `grep -rn` (this session) — the authoritative SC#1 input, superseding
  `30-CONTEXT.md`'s pre-Phase-30.1 grep
- `uv run --extra docs sphinx-build -b html docs/source <tmp>` with `docs/locale/` temporarily
  removed (this session) — empirical proof for Pitfall 2, repo left clean afterward
  (`git status --short` verified empty)
- Installed `furo` package's `theme.conf` (`.venv/lib/python3.13/site-packages/furo/theme.conf`)
  — the source for Pitfall 3's default-sidebar-list finding
- `.planning/phases/30-.../30-CONTEXT.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md` —
  read in full for this research

### Secondary (MEDIUM confidence)
- None — no external documentation lookup was needed for this phase.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: N/A — no new stack; existing tools only
- Architecture (deletion scope, line anchors): HIGH — every claim measured against the live tree
  this session
- Pitfalls: HIGH — all four are direct measurements, not inferred risk

**Research date:** 2026-07-26
**Valid until:** Effectively immediately-perishable — this research is a snapshot of the current
tree state and is only valid until the next commit lands (any further edits to `conf.py`,
`docs.yml`, `docs/Makefile`, or `tests/test_readthedocs_config.py` invalidate the line anchors
above). Re-verify anchors immediately before executing tasks if any time has passed since this
research.
