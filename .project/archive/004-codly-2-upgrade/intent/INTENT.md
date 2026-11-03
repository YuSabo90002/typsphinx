# Intent — typsphinx

Lane: standard   <!-- RESEARCH items remain (codly 2.0 API semantics for offset/highlighted/figure kind, codly-languages compatibility, raw() string escaping) and the work spans package pin, translator emission, templates, docs and examples -->

Review panel: off

Finding skeptics: off

Surfaces: generated content .typ files, typstpdf PDF output, docs user guide templates page (docs/source/user_guide/templates.rst)

## Summary

typsphinx pins Typst Universe `@preview/codly:1.3.0`; codly 2.0.0 (published 2026-10-14, requires Typst >= 0.15) replaces the 1.3 state-mutating API (`codly-init`, `codly(...)` config calls consumed by the next raw block) with a constructor `codly.new(body, ..fields)` and scoped `codly.set_` / `codly.lang-set_` show rules. This milestone moves typsphinx to codly 2.0.0: the `DEFAULT_PACKAGES` pin and `typsphinx-init` are rewritten for the 2.0 API, and every Sphinx code block is emitted as one pure code-mode `codly.new(raw("...", ...), ...)` expression instead of a markup ``` fence preceded by `codly(...)` config calls — removing the last exception to typsphinx's code-mode `.typ` output. Sphinx code-block options (line numbers on/off, start line, emphasized lines, language) must still be reflected, while the visual design follows codly 2.0's new defaults. The change to the `/_typsphinx/deps.typ` export contract is accepted as a breaking change and documented with a migration note. The milestone also carries three doc-audit rulings on the examples. Release work (version bump, PyPI publish) is out of scope.

## Problem

- codly 1.3.0 is superseded by 2.0.0; typsphinx stays on the old line and its generated code depends on the 1.3-only state API (`codly(number-format: none)`, `codly(offset: N)`, `codly(highlights: (...))` emitted before each block at `typsphinx/translator.py:2521-2570`).
- Code blocks are the one place where generated `.typ` files leave code style: a ``` markup fence, with mode-dependent `#` prefixes (`codly_prefix`, list-item `{`/`#{` wrappers, `translator.py:2480-2521`) that have caused past markup/code-mode leak defects (FID-12, the codly-range corpus bug).
- Doc-audit queue: `examples/charged-ieee/README.md` claims both approaches produce identical output, but approach1's PDF title is "Paper Title" because its `typst_template_function["params"]` omits `title`; `examples/advanced/README.md` says seealso renders as `#info` (code renders `#tip`) and shows inline math as `#mi(...)` (output has no `#`).

## Users

typsphinx users building Typst/PDF output from Sphinx projects (code blocks are in nearly every technical document); users who write custom templates importing `/_typsphinx/deps.typ`; the maintainer.

## Success criteria

1. Package pin: `typsphinx/typst_deps.py` `DEFAULT_PACKAGES` names `@preview/codly:2.0.0`, and a `typst` build of `tests/roots/test-basic` writes `<outdir>/_typsphinx/deps.typ` whose codly import line is `@preview/codly:2.0.0` and whose `typsphinx-init` contains no 1.3-only call (`codly-init`, a state-setting `codly(` call) and no `show raw` rule that converts raw blocks to codly (E9: user-written raw blocks are left to Typst's ordinary rendering); `tests/test_preview_version_sync.py` passes with the spec literal appearing only in `typst_deps.py`.
2. Code-mode emission (surface: generated content .typ files): in the content `.typ` files produced by `typst` builds of `tests/roots/test-basic`, `examples/basic`, `examples/advanced` and `docs/source`, every Sphinx code block (literal_block and doctest_block, including blocks inside captioned figures, list items, admonitions and table cells) is one `codly.new(raw(...), ...)` expression. Absence check over those same output files: `grep -rn '```'` and `grep -rnE '(^|[^.a-z-])codly\('` both return no match.
3. Options reflected (surface: typstpdf PDF output): in the PDF built by `typstpdf` from a fixture covering each option, a block without `:linenos:` shows no line numbers; a block with `:linenos:` shows line numbers starting at 1; `:lineno-start: N` makes the first displayed number N; `:emphasize-lines:` highlights exactly the named lines (including when combined with `:lineno-start:`); and a block with a language shows codly 2.0's language badge. Visual styling (colors, radius, badge look) is codly 2.0's default, not a recreation of 1.3's look.
4. Captioned code blocks: a `code-block` with `:caption:` and `:name:` still renders as a numbered listing-kind figure with its caption (numbered in the listing sequence, separate from image figures), and a `:ref:`/`:numref:` to its name resolves in the PDF.
5. Builds compile: `typstpdf` builds of `examples/basic`, `examples/advanced`, both `examples/charged-ieee` approaches, and the project docs (`tox -e docs-pdf`) complete without error.
6. Contract docs (surface: docs user guide templates page): `docs/source/user_guide/templates.rst` lists the names `/_typsphinx/deps.typ` exports for codly 2.0 and describes what `typsphinx-init` now sets up; `CHANGELOG.md` `## [Unreleased]` records the codly 2.0.0 upgrade as a breaking change with a migration note for templates that imported `codly`/`codly-init` from deps.typ, and states that raw blocks written by users (custom templates, `.. raw:: typst`) are no longer rendered through codly by `typsphinx-init` (E9).
7. charged-ieee fix-code: the PDF built from `examples/charged-ieee` approach1 has the project title (not "Paper Title") as its paper title, so the README's identical-output claim holds.
8. advanced README fix-doc: `examples/advanced/README.md` states that seealso renders through `#tip` and shows the inline-math form the translator actually emits.
9. On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean.

## Edge coverage

| Edge | Criterion | Category | Disposition | Detail |
|------|-----------|----------|-------------|--------|
| E1 | SC1 | boundary | dismissed | a fixed literal pin `@preview/codly:2.0.0`; no range or threshold beyond the exact version string SC1 states |
| E2 | SC2 | encoding | held-out | code content containing `"`, `\`, backticks (including ``` runs), `#`, `$`, tabs, non-ASCII (CJK, emoji) and trailing whitespace round-trips byte-identical into the raw() string — per C4: the string literal emitted in the content `.typ` decodes to the source text byte-for-byte (tabs, trailing whitespace included), and the compiled PDF text equals the source text with each tab compared as rendered whitespace |
| E3 | SC2 | empty | held-out | an empty code block and a single-line block both compile and render as a codly block |
| E4 | SC3 | boundary | held-out | `:lineno-start: 1` emits no offset; `:lineno-start: 0` and large values (e.g. 1000) render the stated first number |
| E5 | SC3 | boundary | criterion SC3 | with `:lineno-start: 10` and `:emphasize-lines: 2`, the highlighted line is the 2nd source line (displayed as 11), matching Sphinx/HTML semantics |
| E6 | SC3 | adjacency | held-out | `:emphasize-lines: 2-4,4,6` highlights lines 2,3,4,6 once each; out-of-range line numbers follow Sphinx's own warning behavior and do not break compilation |
| E7 | SC3 | empty | held-out | a block with no language (and `highlight_language` none) renders as a codly block with no badge; doctest_block keeps the `python` language |
| E8 | SC4 | ordering | criterion SC4 | a captioned code block remains a listing-kind figure (numbered in the listing sequence, not the image/figure sequence) |
| E9 | SC1 | idempotency | criterion SC1 | user ruled E9 out: typsphinx does not convert user-written raw blocks (custom templates, `.. raw:: typst`); `typsphinx-init` installs no `show raw...: codly.new` rule, only typsphinx's explicit `codly.new` calls render through codly |
| E10 | SC5 | none | dismissed | fixed set of named example/doc projects; pass/fail compile, no data shape |
| E11 | SC6 | none | dismissed | static documentation text |
| E12 | SC7 | none | dismissed | one fixed example project; the title is the project's configured title |
| E13 | SC8 | none | dismissed | static documentation text |
| E14 | SC9 | none | dismissed | whole-repository command results on one HEAD |

## Prohibitions

| Prohibition | Criterion | Must not | Disposition | Detail |
|-------------|-----------|----------|-------------|--------|
| N1 | SC6 | silently break user templates that import `codly`/`codly-init` from deps.typ without telling them | criterion SC6 | the CHANGELOG breaking-change entry and templates.rst migration note are the disclosure |
| N2 | SC1 | none | dismissed | build-output or documentation internals; no values, safety, privacy or fairness item applies beyond the N1 disclosure |
| N3 | SC2 | none | dismissed | build-output or documentation internals; no values, safety, privacy or fairness item applies beyond the N1 disclosure |
| N4 | SC3 | none | dismissed | build-output or documentation internals; no values, safety, privacy or fairness item applies beyond the N1 disclosure |
| N5 | SC4 | none | dismissed | build-output or documentation internals; no values, safety, privacy or fairness item applies beyond the N1 disclosure |
| N6 | SC5 | none | dismissed | build-output or documentation internals; no values, safety, privacy or fairness item applies beyond the N1 disclosure |
| N7 | SC7 | none | dismissed | build-output or documentation internals; no values, safety, privacy or fairness item applies beyond the N1 disclosure |
| N8 | SC8 | none | dismissed | build-output or documentation internals; no values, safety, privacy or fairness item applies beyond the N1 disclosure |
| N9 | SC9 | none | dismissed | build-output or documentation internals; no values, safety, privacy or fairness item applies beyond the N1 disclosure |

## Scope: in

- Bump `DEFAULT_PACKAGES` codly spec to 2.0.0 and rewrite `typsphinx-init` for the 2.0 API (languages via `codly.lang-set_`).
- `typsphinx-init` installs no global raw→codly show rule (E9 ruling).
- Re-emit every code block as a code-mode `codly.new(raw("...", lang: ..., block: true), ...)` expression; map `:linenos:` → `number-enabled`, `:lineno-start:` → `offset`, `:emphasize-lines:` → `highlighted`; remove the fence and the mode-dependent `#`/`#{` wrappers for code blocks.
- Captioned code blocks keep figure, caption, numbering and label.
- codly-languages: verify compatibility with codly 2.0 and bump if required (C1 ruling 3a).
- Update the bundled `templates/base.typ`, `docs/source/_typst/`, `examples/` templates and test fixtures/render gates that encode 1.3 output.
- Docs: templates.rst export contract + migration note; CHANGELOG Unreleased breaking-change entry.
- Doc-audit rulings: charged-ieee approach1 `title` param (fix-code); advanced README seealso and inline-math claims (fix-doc).

## Scope: out (vetoes)

- A 1.3-compatibility shim that keeps `codly-init` / state-style `codly(...)` working — user ruled 1a: accept the breaking change.
- Recreating codly 1.3's visual look — "2.0で刷新された標準の見た目は反映されるべきだ".
- Version bump, CHANGELOG release section, tag, PyPI publish — user ruled 4a: release is a later milestone.
- Converting user-written raw blocks (templates, `.. raw:: typst`) to codly — E9 ruling "E9はしないべきだと考える".
- Bumping the other `@preview` packages (mitex, gentle-clues, diagraph) unless codly 2.0 forces it.
- Do not break: the `@preview` single-source rule (specs only in `typst_deps.py`), the `/_typsphinx/deps.typ` import path and `typsphinx-init` name, and code-mode output everywhere else.

## Constraints

- Python >= 3.12, builtin generics; black/ruff line 88; mypy clean (CLAUDE.md).
- Typst via typst-py `>=0.15.0,<0.16` (codly 2.0 requires Typst >= 0.15).
- `@preview` versions live only in `typsphinx/typst_deps.py` (`tests/test_preview_version_sync.py`).
- Integration by pull request (STATE `integration: pull-request`); CI runs ubuntu/windows/macos × py312/py313, so tests must stay OS-neutral.
- Test Verify for docs-touching work needs `--extra dev --extra docs` installed (17 docs gates skip otherwise).

## Current state (brownfield only)

- **What exists**: typsphinx 0.9.8, Sphinx builder → writer → translator; `typst_deps.py` single-sources five `@preview` specs and generates `_typsphinx/deps.typ` with `typsphinx-init` (`show: codly-init.with()` + `codly(languages: codly-languages)`); `translator.visit_literal_block` emits per-block `codly(...)` config calls then a ``` fence (`translator.py:2439-2605`). Full suite green (1812 passed, 18 skipped) at 46a72b5f.
- **Must not break**: `/_typsphinx/deps.typ` path and `typsphinx-init` name; `@preview` single source; captioned code-block figures and references; OS-neutral tests.
- **Doc-vs-code rulings**: queue #1 charged-ieee identical-output → fix-code; queue #2 advanced README seealso `#info` → fix-doc; queue #3 advanced README inline math `#mi` → fix-doc.
- **Ground truth**: `.project/research/evidence-codebase.md`, `.project/research/DOCS-AUDIT.md`

## Risks

- codly 2.0 semantics may differ from Sphinx's: `offset` vs first displayed number, `highlighted` uses displayed numbers (migration guide), so emphasize-lines with lineno-start may shift.
- Wrapping in `codly.new(...)` may change how `figure()` detects the listing kind (raw vs other content), changing caption supplement and numbering.
- Escaping arbitrary code text into a Typst string literal for `raw(...)` (backslashes, quotes, non-ASCII) — previously the fence carried it verbatim.
- codly-languages 0.1.10 may lack the `name` field codly 2.0 now requires per language.
- codly 2.0 is two weeks old; defects in it may surface in typst-py 0.15 compilation.

## Open questions

- [RESEARCH] Exact codly 2.0 field names/semantics for line numbers off, start number (`offset` value for `:lineno-start: N`), and whole-line highlights relative to offset.
- [RESEARCH] Does `figure(codly.new(raw(...)), caption: ...)` keep `kind: raw` auto-detection, or must typsphinx pass `kind: raw`? (User expects it works — codly 2.0 docs show captioned listings; captioned blocks get no SC2 exception either way.)
- [RESEARCH] Is codly-languages 0.1.10 compatible with codly 2.0, and which version is current?
- [RESEARCH] Which names should deps.typ export (`import "@preview/codly:2.0.0" as codly` vs `*`)?

## Corrections

- C1 2026-11-03: "1a 2オプションが反映されることは重視すべきだが2.0で刷新された標準の見た目は反映されるべきだ。3a 4a 5-1 fix-code 5-2 fix-doc 5-3 fix-doc"
- C2 2026-11-03: "プラスアルファとして、本プロジェクトによって生成されるtypファイルは、typstのコードスタイル(マークアップスタイルで出力されないの意)で出力されるが、従来、codlyはraw関数の絡みでこれの例外となっていた。今回からはcodly.new関数によって完全なコードスタイルとして定義できるようになったため今回はこれの刷新もするべきだと考えている"
- C3 2026-11-03: "E2-E8は推奨通り。E9はしないべきだと考える。N1 推奨どおり。SC2はcodly2.0のページにて例に挙られているためそもそもキャプション付きブロックは正常に表示されるであろうと考える"
- C4 2026-11-03: "Q1 a、Q2 a" — decide checkpoint: E2 re-worded (Typst renders tabs as spaces in PDF text; byte-identity is checked on the emitted `.typ` string, PDF text compares tabs as whitespace); emphasize-lines keep codly 2.0's default multi-colour palette.
- C5 2026-11-03: "C5 a、承認して build 開始" — plan checkpoint: the SC2 `codly(` absence check over docs/source output exempts exactly the inline `raw("...")` literals in `changelog.typ` whose decoded text occurs verbatim in CHANGELOG.md (released history at CHANGELOG.md lines 912 and 1322); every other match fails SC2 (T002 AC3).
