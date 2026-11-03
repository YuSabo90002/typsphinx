# Final Review — typsphinx

Reviewed HEAD: ae1565f28a43b152c7599f7aed92d661b428e59f
Overall verdict: pass

## Success criteria

### SC1 — Package pin: `typsphinx/typst_deps.py` `DEFAULT_PACKAGES` names `@preview/codly:2.0.0`, and a `typst` build of `tests/roots/test-basic` writes `<outdir>/_typsphinx/deps.typ` whose codly import line is `@preview/codly:2.0.0` and whose `typsphinx-init` contains no 1.3-only call (`codly-init`, a state-setting `codly(` call) and no `show raw` rule that converts raw blocks to codly (E9: user-written raw blocks are left to Typst's ordinary rendering); `tests/test_preview_version_sync.py` passes with the spec literal appearing only in `typst_deps.py`.

- **Verdict**: met
- **Check**: `LC_ALL=C uv run sphinx-build -E -q -b typst tests/roots/test-basic <tmp>/tests_roots_test-basic` then `cat <tmp>/tests_roots_test-basic/_typsphinx/deps.typ`; `git grep -n '@preview/codly:' -- typsphinx`; project Verify ledger entry for ae1565f2
- **Observed**: build exit 0. deps.typ contains `#import "@preview/codly:2.0.0" as codly` and `#let typsphinx-init(body) = {` / `  show: codly.lang-set_(languages: codly-languages)` / `  body` / `}` — no `codly-init`, no state-setting `codly(` call, no `show raw` rule (E9 criterion edge: user raw blocks are left to Typst). `git grep` hits only `typsphinx/typst_deps.py:50` (docstring) and `:93` (`PreviewPackage(spec="@preview/codly:2.0.0", alias="codly")`). `tests/test_preview_version_sync.py` passed inside the project Verify run (1883 passed, 1 skipped, 0 failed).
- **Reference**: typsphinx/typst_deps.py:93; .project/build/verify-ledger.jsonl (commit ae1565f2); .project/review/final-gap-1.md
- **Finding**: none
- **Fix direction**: none

### SC2 — Code-mode emission (surface: generated content .typ files): in the content `.typ` files produced by `typst` builds of `tests/roots/test-basic`, `examples/basic`, `examples/advanced` and `docs/source`, every Sphinx code block (literal_block and doctest_block, including blocks inside captioned figures, list items, admonitions and table cells) is one `codly.new(raw(...), ...)` expression. Absence check over those same output files: `grep -rn '```'` and `grep -rnE '(^|[^.a-z-])codly\('` both return no match.

- **Verdict**: met
- **Surface**: generated content .typ files
- **Check**: Walkthrough performed in the sidecar: `LC_ALL=C uv run sphinx-build -E -q -b typst <project> <tmp>/<name>` for the four projects (all exit 0); content files = 21 `.typ` outside `_typsphinx/`/`_template/` excluding the wrappers output.typ, basic-example.typ, advanced-example.typ, typsphinx.typ; `grep -rn '```' <content files>`; `grep -rnoE '(^|[^.a-z-])codly\(' <content files>`; opened examples_basic/index.typ and examples_advanced/{index,chapter1,chapter2}.typ; `LC_ALL=C uv run pytest tests/test_codly2_output_gate.py tests/test_codly2_render_gate.py -rs -q`
- **Observed**: empty state: test-basic content has 0 `codly.new(raw(`. Success state: examples/basic 3, examples/advanced 10, docs/source 141 code-mode `codly.new(raw(` expressions, each at line start with no `#`, no fence and no `{`/`#{` wrapper, e.g. `codly.new(raw("sphinx-quickstart", block: true, lang: "bash"), number-enabled: false)`; a code block inside the `tip(` admonition (chapter2.typ:277) is the same single expression. Error state not present: the fence grep returned no match (rc=1); the `codly(` grep returned only `docs_source/changelog.typ:3322` `raw("{ codly(...) }")` and `:5128` `raw("#codly(number-format: none)")`, inline literals quoting CHANGELOG.md:946 and :1356 verbatim — exactly the C5 exemption (released history; C5's 912/1322 shifted by the new Unreleased entry, content identical). Captioned figure and table-cell contexts are absent from the four projects; the output gate adds the codly2_render_gate fixture and asserts the union covers {captioned figure, list item, admonition, table cell} and per-document counts equal the doctree literal_block+doctest_block counts. Gate run: 34 passed, no skips. Held-out E2: `test_codly2_render_gate.py` encoding tests passed in that run (and in the T002 Verify, 34 passed); the fixture PDF text shows `enc_quote = "dq" 'sq'`, `enc_backslash = "a\\b\n"`, `enc_tick = `one` and ```three``` and ````four````, `enc_hash = #let x = $m$ # $`, `enc_cjk = "日本語" "😀"`, and the tabbed line rendered with leading whitespace and trailing spaces kept. Held-out E3: the empty-block and single-line tests passed; the rendered page 4 shows the empty block as one empty codly row with a Python badge between EMPTYBEFOREMARK and EMPTYAFTERMARK and `singleblk` as one badged row.
- **Reference**: tests/test_codly2_output_gate.py; tests/test_codly2_render_gate.py; .project/intent/INTENT.md C5; .project/review/wave-1.cycle1.md (T002/AC1-AC3, AC7, AC8)
- **Finding**: none
- **Fix direction**: none

### SC3 — Options reflected (surface: typstpdf PDF output): in the PDF built by `typstpdf` from a fixture covering each option, a block without `:linenos:` shows no line numbers; a block with `:linenos:` shows line numbers starting at 1; `:lineno-start: N` makes the first displayed number N; `:emphasize-lines:` highlights exactly the named lines (including when combined with `:lineno-start:`); and a block with a language shows codly 2.0's language badge. Visual styling (colors, radius, badge look) is codly 2.0's default, not a recreation of 1.3's look.

- **Verdict**: met
- **Surface**: typstpdf PDF output
- **Check**: Walkthrough performed: `LC_ALL=C uv run sphinx-build -E -b typstpdf tests/fixtures/codly2_render_gate <tmp>/fixpdf` ("build succeeded, 1 warning"), pypdf text of master.pdf, `typst.compile(master.typ, format="png", ppi=100)` and visual inspection of pages 3-4; `LC_ALL=C uv run pytest tests/test_codly2_render_gate.py -rs` (in the 34-passed run, no skips)
- **Observed**: page 3: `nolnblk` shows no numbers; `numonblk` 1,2,3; `tenstartblk` 10,11,12; `emphblk` (no linenos) highlights only row 2; E5 criterion edge: `comboblk` (`:lineno-start: 10`, `:emphasize-lines: 2`) highlights only the row displayed as 11. Held-out E4: `onestartblk` starts at 1 (the gate's `lineno-start 1 emits no offset` test passed), `zerostartblk` starts at 0, `bigstartblk` at 1000. Held-out E6: `dedupeblk` (`2-4,4,6`) highlights rows 2,3,4,6 once each in codly 2.0's multi-colour palette, rows 1,5,7 plain; `rangeblk` logged "WARNING: line number spec is out of range(1-3): '2,9'", the build still succeeded and row 2 is highlighted. Every language block carries codly 2.0's "Python" badge with icon, zebra rows, default radius — no 1.3 look. Held-out E7 (page 4): `nolangblk` (default) and `nonelangblk` (none) render as codly blocks with no badge; the doctest block shows the Python badge. Error state (non-zero exit, missing number/highlight/badge) not observed.
- **Reference**: tests/fixtures/codly2_render_gate/index.rst; tests/test_codly2_render_gate.py; .project/review/wave-1.cycle1.md (T002/AC4, AC5, AC9-AC11)
- **Finding**: none
- **Fix direction**: none

### SC4 — Captioned code blocks: a `code-block` with `:caption:` and `:name:` still renders as a numbered listing-kind figure with its caption (numbered in the listing sequence, separate from image figures), and a `:ref:`/`:numref:` to its name resolves in the PDF.

- **Verdict**: met
- **Surface**: typstpdf PDF output
- **Check**: Walkthrough step 4 on the same fixture PDF: pypdf text and page-4 render; pypdf `/Annots` of page 4; `test_listings_and_figure_are_numbered_separately` and `test_numref_and_ref_resolve` in the 34-passed gate run
- **Observed**: page 4 reads "Listing 1: Capone first listing", then "Figure 1: Figcap image figure", then "Listing 2: Cap ]br #x $m$" — E8 criterion edge: captioned code blocks are numbered in the listing sequence, separate from the image figure sequence. "Reference by number: NUMREFSENT 1. Reference by name: Cap ]br #x $m$." Page 4 carries two internal `/Link` annotations whose `/Dest` is an `/XYZ` position on the same page (the listing), so both references resolve and link.
- **Reference**: tests/test_codly2_render_gate.py; .project/review/wave-1.cycle1.md (T002/AC6)
- **Finding**: none
- **Fix direction**: none

### SC5 — Builds compile: `typstpdf` builds of `examples/basic`, `examples/advanced`, both `examples/charged-ieee` approaches, and the project docs (`tox -e docs-pdf`) complete without error.

- **Verdict**: met
- **Check**: `LC_ALL=C uv run sphinx-build -E -q -b typstpdf` of examples/basic, examples/advanced, docs/source, and `-c examples/charged-ieee/<approach> examples/charged-ieee/<approach>/source` for approach1 and approach2; recorded T003 Verify (`tox -e docs-pdf`)
- **Observed**: all five reviewer builds exit 0 and wrote basic-example.pdf, advanced-example.pdf, typsphinx.pdf, approach1/paper.pdf, approach2/paper.pdf. (A first charged-ieee attempt without `-c` failed only because the reviewer pointed srcdir at the directory holding conf.py rather than `source/`; rerun with the documented layout succeeded.) The T003 Verify recorded `tox -e docs-pdf`: "build succeeded." and "docs-pdf: OK"; `test_examples_typstpdf_gate.py` and `test_examples_charged_ieee_gate.py` passed again in the project Verify.
- **Reference**: .project/tasks/T003-*.md Log; .project/review/wave-1.cycle1.md (T003/AC1); .project/build/verify-ledger.jsonl (ae1565f2)
- **Finding**: none
- **Fix direction**: none

### SC6 — Contract docs (surface: docs user guide templates page): `docs/source/user_guide/templates.rst` lists the names `/_typsphinx/deps.typ` exports for codly 2.0 and describes what `typsphinx-init` now sets up; `CHANGELOG.md` `## [Unreleased]` records the codly 2.0.0 upgrade as a breaking change with a migration note for templates that imported `codly`/`codly-init` from deps.typ, and states that raw blocks written by users (custom templates, `.. raw:: typst`) are no longer rendered through codly by `typsphinx-init` (E9).

- **Verdict**: met
- **Surface**: docs user guide templates page (docs/source/user_guide/templates.rst)
- **Check**: Walkthrough performed: `LC_ALL=C uv run sphinx-build -E -q -b html docs/source <tmp>/html` (exit 0), opened `<tmp>/html/user_guide/templates.html` and read the deps.typ contract section as text; compared with the test-basic `_typsphinx/deps.typ`; read `CHANGELOG.md` `## [Unreleased]`
- **Observed**: export table row: "codly 2.0.0 codly, imported as a module (codly.new, codly.set_, codly.lang-set_, …)"; no `codly-init` export. The typsphinx-init paragraph: registers codly-languages "through show: codly.lang-set_(languages: codly-languages)", "installs no rule that turns raw blocks into codly blocks", user raw blocks (template or `.. raw:: typst`) "left to Typst's own rendering" — matches the generated deps.typ byte for byte. "Migrating from codly 1.3." note: remove `#show: codly-init.with()`, replace state-style `codly` calls with `#show: codly.set_(...)` or `#codly.new(raw(...), ...)`, `typst_dependencies` must import `as codly`. CHANGELOG Unreleased `### Changed`: "**Breaking: codly is upgraded from 1.3.0 to 2.0.0**" with "Migration for template authors" and "Raw blocks written by users are no longer rendered through codly" (E9). Judgment prohibition N1: judged against its Detail, the CHANGELOG breaking-change entry plus the templates.rst migration note disclose the removal of `codly-init`/state-style `codly` to template users, so templates are not broken silently.
- **Reference**: docs/source/user_guide/templates.rst:150-198; CHANGELOG.md `## [Unreleased]` (Breaking codly entry); .project/review/wave-1.cycle1.md (T001/AC6)
- **Finding**: none
- **Fix direction**: none

### SC7 — charged-ieee fix-code: the PDF built from `examples/charged-ieee` approach1 has the project title (not "Paper Title") as its paper title, so the README's identical-output claim holds.

- **Verdict**: met
- **Check**: `LC_ALL=C uv run sphinx-build -E -q -b typstpdf -c examples/charged-ieee/approach1 examples/charged-ieee/approach1/source <tmp>` (and approach2), then pypdf page-1 text
- **Observed**: approach1 page 1 begins "Machine Learning Applications in Computer | Vision | John Doe | Computer Science | Massachusetts Institute of Technology"; "Paper Title" absent. approach2 page 1 begins identically. approach1/conf.py:67 has `"title": project,`.
- **Reference**: examples/charged-ieee/approach1/conf.py:67; tests/test_examples_charged_ieee_gate.py
- **Finding**: none
- **Fix direction**: none

### SC8 — advanced README fix-doc: `examples/advanced/README.md` states that seealso renders through `#tip` and shows the inline-math form the translator actually emits.

- **Verdict**: met
- **Check**: `grep -n -i 'seealso\|#tip\|mi(' examples/advanced/README.md`; grep of `mi(` in the examples/advanced `-b typst` output; `grep -n -A3 'def visit_seealso' typsphinx/translator.py`; `LC_ALL=C uv run pytest -k 'advanced_readme_inline_math_form_is_emitted or advanced_seealso_renders_through_tip' tests/`
- **Observed**: README:207 "See also section (rendered through #tip[] with a \"See also\" title)"; README:138 shows ``mi(`E = mc^2`)`` with no `#`. The built output emits inline math as `mi(`...`)` with no `#` (e.g. chapter1.typ:16 ``mi(`a^2 + b^2 = c^2`)``); translator.py:6244 `visit_seealso` "converts to #tip[]". The two README gates: 2 passed.
- **Reference**: examples/advanced/README.md:138,207; tests/test_examples_typstpdf_gate.py
- **Finding**: none
- **Fix direction**: none

### SC9 — On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.

- **Verdict**: met
- **Check**: none (project Verify not re-run; cited recorded output of `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/` at ae1565f2)
- **Observed**: ledger execution exit_code 0: "1883 passed, 1 skipped in 215.21s" (skip: pre-existing `test_corpus_gate.py::test_empty_url_before_after`), "398 files would be left unchanged.", "All checks passed!", "Success: no issues found in 10 source files".
- **Reference**: .project/build/verify-ledger.jsonl (commit ae1565f28a43b152c7599f7aed92d661b428e59f); .project/review/final-gap-1.md (Gap verdict: pass)
- **Finding**: none
- **Fix direction**: none
