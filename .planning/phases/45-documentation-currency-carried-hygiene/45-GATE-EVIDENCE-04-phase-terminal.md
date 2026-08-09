# Phase 45 Plan 04 — Terminal Phase Gate Evidence

Measured against the whole phase's tree (all four plans merged: 45-01, 45-02, 45-03, 45-04),
worktree branch `worktree-agent-a0f6ee46c1444712b`.

**Final HEAD SHA:** `255c2e04285718cee06566fc75e92a22ba5a95c5` (after Task 2's commit; Task 3
adds only this evidence file, which does not change any tested behaviour).

**Environment:** provisioned with both `dev` and `docs` extras
(`uv sync --extra dev --extra docs`), per the upstream-context instruction — this is what lets
`tests/test_changelog_page_gate.py` actually RUN rather than SKIP (myst-parser present).

## SC#1 — README Quick Start matches real Quick Start behaviour (DOC-11)

Discharged by Plan 45-03. Cited here for completeness of the phase-wide gate:
`tests/test_quickstart_docs_gate.py` (`TestQuickstartFirstPdfGate`,
`TestPublishedQuickstartTextMatchesBuild`) — both classes pass in the full-suite run below.

## SC#2 — Published changelog page carries every release, both docs builders build it clean (DOC-12)

Discharged by Plans 45-01/45-02. Cited here: `tests/test_changelog_page_gate.py`
(`TestPublishedChangelogPageDelegates`, `TestChangelogPageContentCoverage`,
`TestChangelogIncludeCompilesToPdf`) — all pass in the full-suite run below, **not skipped**
(myst-parser is present via the `docs` extra). Delta counts re-confirmed against the final tree
below (§ Docs-build delta re-confirmation): `changelog_attributable_warning_count = 0`, neither
`html_warning_count` (1) nor `pdf_warning_count` (1) exceeds the
`45-GATE-EVIDENCE-01-docs-build-baseline.md` baseline (1 and 1 respectively).

## SC#3 — `derive_typst_lang()` emits its rejection warning from exactly one site (QUA-02)

Discharged by this plan's Task 1. Structural scan (bounded to the function body, docstrings and
comment lines stripped): exactly 1 `logger.warning(` call site. Both pinning surfaces —
`tests/test_template_engine.py::TestDeriveTypstLang` (18 tests) and
`tests/test_typst_lang_gate.py` (18 tests, real-build corpus) — green both before and after the
refactor (39/39 both times). The rendered message for a rejected input (`derive_typst_lang("abcd")`)
was captured character-for-character before and after and found byte-identical:

```
typsphinx: could not derive a Typst 'lang' from Sphinx 'language' = 'abcd' -- omitting 'lang' (falling back to the template's own default).
```

`tests/test_preview_version_sync.py` (3 tests) also green, confirming the four `@preview`
version declarations in `typsphinx/template_engine.py` were undisturbed by the refactor.

## SC#4 — `.planning/PROJECT.md` contains zero unterminated `<!--` (QUA-03)

Discharged by this plan's Task 2, recorded in full in
`45-GATE-EVIDENCE-04-qua03-comment-scan.md`: a fence- and backtick-aware opener-stack scan finds
34 openers, 34 closers, zero residual (unterminated) openers. Three self-checks pass (same-line
pair neutrality, zero-opener-input safety, LIFO/ascending-order residual pairing). The D-08
bisect finding is recorded there: commit `43a2a78` (Phase 41 plan 03, decision D-13) deliberately
and attributedly closed the two openers the source todo named — not incidentally, correcting
`45-CONTEXT.md`'s D-07 phrasing.

## SC#5 — Full suite + lint/type trio green, `typsphinx/` change confined to QUA-02's refactor

### Full pytest suite

```
uv run pytest
...
================== 952 passed, 1 skipped in 190.23s (0:03:10) ==================
```

The one skip:

```
SKIPPED [1] tests/test_corpus_gate.py:529: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
```

This is the expected, standing env-gated skip (unrelated to this phase; `TYPSPHINX_CORPUS_REPORT`
opts into an on-demand corpus report and is deliberately not set in normal runs) — it is not
attempted to be made to run per the upstream-context instruction.

**Reconciling this count against the two reference baselines the orchestrator measured on the
merged main tree at this plan's base (`4a15c739`):**

| Extras provisioned | Passed | Skipped |
|---|---|---|
| `dev` only | 948 | 5 |
| `dev` + `docs` (this run) | 952 | 1 |

The delta (948→952 passed, 5→1 skipped) is exactly the four
`tests/test_changelog_page_gate.py` classes converting from SKIP (myst-parser absent) to PASS
(myst-parser present via the `docs` extra) — confirmed by name: `TestPublishedChangelogPageDelegates`,
`TestChangelogPageContentCoverage`, `TestChangelogIncludeCompilesToPdf`'s three tests collapse
from 4 skips to 4 passes at the plan-count granularity above (952 - 948 = 4). This run
provisioned **both** extras, so the changelog gate **ran** (not skipped) — the terminal green
gate actually exercises the phase's new gates rather than silently skipping them, per the
upstream-context instruction.

### Lint / type trio

```
uv run black --check .
All done! ✨ 🍰 ✨
243 files would be left unchanged.

uv run ruff check .
All checks passed!

uv run mypy typsphinx/
Success: no issues found in 6 source files
```

All three exit 0.

### `typsphinx/` scope diff against the phase baseline

`baseline_sha` (from `45-GATE-EVIDENCE-01-docs-build-baseline.md`): `8c74b853f81eaac0c9233a9628928528d16f2d18`

```
$ git diff --name-only 8c74b853f81eaac0c9233a9628928528d16f2d18 HEAD -- typsphinx/
typsphinx/template_engine.py
```

Exactly one file — no other path under `typsphinx/` changed anywhere in the phase. Full diff of
that file, verbatim:

```diff
diff --git a/typsphinx/template_engine.py b/typsphinx/template_engine.py
index 7b9ed04..123ecee 100644
--- a/typsphinx/template_engine.py
+++ b/typsphinx/template_engine.py
@@ -128,19 +128,16 @@ def derive_typst_lang(sphinx_language: str | None) -> str | None:
         A lowercase 2-3-letter ASCII Typst ``lang`` code, or ``None`` if no
         such code could be derived.
     """
-    if not isinstance(sphinx_language, str) or not sphinx_language:
-        logger.warning(
-            f"typsphinx: could not derive a Typst 'lang' from Sphinx "
-            f"'language' = {sphinx_language!r} -- omitting 'lang' (falling "
-            f"back to the template's own default)."
-        )
-        return None
-
-    head = re.split(r"[_\-@]", sphinx_language, maxsplit=1)[0].lower()
-
-    if re.fullmatch(r"[a-z]{2,3}", head):
-        return head
-
+    if isinstance(sphinx_language, str) and sphinx_language:
+        head = re.split(r"[_\-@]", sphinx_language, maxsplit=1)[0].lower()
+        if re.fullmatch(r"[a-z]{2,3}", head):
+            return head
+
+    # QUA-02: both rejection paths above (non-str/None/empty input, and a
+    # well-formed-length-but-non-ASCII-alpha head) fall through to this
+    # single tail call rather than each carrying its own copy -- the two
+    # reasons are deliberately NOT distinguished in the wording, since
+    # doing so would change build output and fail SC#3's byte-identity bar.
     logger.warning(
         f"typsphinx: could not derive a Typst 'lang' from Sphinx "
         f"'language' = {sphinx_language!r} -- omitting 'lang' (falling "
```

The single hunk falls entirely inside `derive_typst_lang()`'s span (the docstring return block
at line 128 through the tail `logger.warning`/`return None` at line ~149) — no line outside that
function is touched. **No SC#5 scope violation.**

### Docs-build delta re-confirmation (final tree)

Both real builds re-run against the final tree (fresh output directories, no `-W`/`-q`/`-n`,
same method as `45-GATE-EVIDENCE-01-docs-build-baseline.md` and
`45-GATE-EVIDENCE-02-docs-build-clean.md`):

```
uv run sphinx-build -b html docs/source docs/_build/html-terminal
```
Exit code: 0. `build succeeded, 3 warnings.` One literal `WARNING:` line (the same pre-existing,
out-of-fence `visit_toctree` docstring defect in `typsphinx/translator.py` the baseline recorded —
unrelated to this phase, unrelated to `template_engine.py`):
```
typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:15: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```
Two `ERROR:`-severity docutils lines (not counted in `html_warning_count`, identical to baseline):
```
typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: ERROR: Unexpected indentation. [docutils]
typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:20: ERROR: Unexpected indentation. [docutils]
```
No line mentions `changelog`.

```
uv run sphinx-build -b typstpdf docs/source docs/_build/pdf-terminal
```
Exit code: 0. `build succeeded, 3 warnings.` Same single `WARNING:` line, same two `ERROR:` lines,
no `changelog`-mentioning line. `Generated PDF: .../docs/_build/pdf-terminal/typsphinx.pdf` —
confirmed a valid PDF (`%PDF-` magic header, 2,289,525 bytes).

| Metric | Baseline (45-GATE-EVIDENCE-01) | Final tree (this evidence) | Delta |
|---|---|---|---|
| `html_warning_count` | 1 | 1 | 0 |
| `pdf_warning_count` | 1 | 1 | 0 |
| `changelog_attributable_warning_count` | 0 | 0 | 0 |

Both totals equal (not exceeding) baseline; `changelog_attributable_warning_count` stays 0 — the
phase's own bar is met exactly, with headroom. (`docs/_build/` is gitignored; the scratch output
directories used for this measurement were removed afterward — `git status --porcelain -- docs/_build`
is empty.)

## Environment note (recorded per prior plans' precedent, not a repository change)

This worktree's `uv sync`-installed `.venv/bin/ruff` and `.venv/bin/uv` are generic-linux
dynamically-linked ELFs the NixOS host cannot execute directly
(`Could not start dynamically linked executable`) — the same class of environment hazard plans
45-01 and 45-02 recorded for their own fresh worktrees. Resolved identically: symlinked
Nix-store binaries (`ruff` 0.15.14, within this repo's `ruff>=0.15,<0.16` pin; `uv` 0.11.25, the
ambient shell's own resolved `uv`) over `.venv/bin/ruff` and `.venv/bin/uv`. Local, gitignored
`.venv/` change only — no repository file touched, and this fix was necessary for the 45
subprocess-based integration tests (which invoke `["uv", "run", "sphinx-build", ...]`) to pass
rather than fail on an unrelated environment defect.

## Carried to the milestone close

- **`ja` catalogue regeneration owed in `typsphinx-doc-translations`.** Every line the changelog
  include newly surfaces (`CHANGELOG.md`'s full content, rendered on both `en` and `ja` builds
  since `docs/source/changelog.rst` is shared byte-for-byte between the `typsphinx` and
  `typsphinx-doc-translations` repositories) renders untranslated on the `ja` site until the
  separate `typsphinx-doc-translations` repository's gettext catalogs are regenerated. Recorded
  identically in `45-GATE-EVIDENCE-01-include-shape.md` and
  `45-GATE-EVIDENCE-02-docs-build-clean.md`; out of this repository's scope; flag at the
  milestone close.

- **RESEARCH.md's two open questions — measured answers** (from `45-GATE-EVIDENCE-01-include-shape.md`):
  (a) the included fragment's heading depth nests sanely under Phase 44.1's relative
  `depth:`/`offset:` mechanism combined with a real `-b typstpdf` compile — confirmed via a
  strictly consecutive H1→H2→H3 sequence in the HTML render and a clean PDF compile with zero
  changelog-attributable warnings; (b) CommonMark's shortcut-reference resolution of the
  bracketed version headings against `CHANGELOG.md`'s own tail link-definition block renders as
  working linked headings (e.g. the `0.7.0` heading links to its GitHub release tag) — confirmed
  in the rendered HTML, no fallback needed.

- **RTD.** `.readthedocs.yaml`'s `python.install` step already syncs the `docs` extra
  (`method: uv` / `command: sync` / `extras: [docs]`), so `myst-parser` is picked up automatically
  by the next RTD build with no RTD-side configuration change needed (recorded in
  `45-GATE-EVIDENCE-01-include-shape.md`).
