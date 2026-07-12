---
status: resolved
trigger: "DATA_START
Fix the FOURTEENTH pre-existing production fatal blocking GATE-02 (v0.6.0 milestone bar): codly package-API mismatch in code-block line numbering. On the real Sphinx doc/ corpus, -b typstpdf fails at typst compile with 'TypstError: unexpected argument: start' from codly(start: {lineno_start}) emitted by typsphinx/translator.py (~line 1319) for literalinclude/code-block with :linenos:. 20 occurrences across 4 files (development/tutorials/{autodoc_ext,extending_build,adding_domain,extending_syntax}.typ).
DATA_END"
created: 2026-07-12T12:12:14Z
updated: 2026-07-12T12:12:14Z
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "codly 1.3.0's codly() function has no `start` parameter; the correct parameter is `offset` (int, additive delta: displayed_number = line.number + offset). offset = linenostart - 1 makes the first displayed line equal Sphinx's linenostart. Sphinx's LiteralInclude directive ALWAYS populates highlight_args['linenostart'] (default 1) even without explicit :lineno-start:, so the fix must also guard against emitting a call for the linenostart==1 default case."
  confirming_evidence:
    - "codly/1.3.0/codly.typ full parameter list (lines 74-129) has no `start:` kwarg; has `offset` (int) and `offset-from`."
    - "codly/1.3.0/src/lib.typ lines 1521/1528/1533/1542 show `line.number + offset` used for the displayed number, highlight ranges, and reference format -- confirms additive-delta semantics, not a direct first-line-number."
    - "sphinx/directives/code.py: CodeBlock.run only sets linenostart when :lineno-start: is explicit (line 170-171); LiteralInclude.run ALWAYS sets it via reader.lineno_start, which defaults to 1 (line 211, 494) -- explains the exact 20-occurrence/4-file footprint (all literalinclude with plain :linenos:)."
  falsification_test: "If codly 1.3.0 actually still accepted `start:` (contradicting the corpus fatal), or if `offset` were a direct first-line-number rather than additive, the regression test's source-level assert (codly(offset: 4) for :lineno-start: 5) and PDF sentinel extraction would fail after the fix -- it didn't."
  fix_rationale: "Replacing `start:` with the correct `offset:` parameter and correct value transform addresses the API-mismatch root cause directly (not a workaround); tightening the guard to `lineno_start not in (None, 1)` addresses the literalinclude-default root cause directly (Sphinx populates a value that looks like real user intent but is just the always-present default)."
  blind_spots: "Did not verify codly's `offset-from` or any other codly 1.3.0 parameter beyond `offset`; did not check whether other @preview package versions (codly-languages, mitex, gentle-clues) have similar API drift (out of scope -- CLAUDE.md forbids touching version pins here). Did not exhaustively audit every code-block/literalinclude call site in the corpus beyond the reported 20 occurrences / 4 files."

hypothesis: CONFIRMED and FIXED. Corpus gate re-run (bounded, post-fix) shows GATE-02 progresses past the codly fatal entirely and now fails at a NEW, DISTINCT 15th fatal: `TypstError: unclosed delimiter` from `visit_block_quote`'s `quote[...]` emission (typsphinx/translator.py ~line 2131) -- a markup-mode/code-mode mismatch, NOT a codly issue. See Evidence below for the bounded root-cause investigation of this next fatal (not fixed in this pass, per bounded-discipline scope -- only the codly bug was authorized for this task).
test: (complete)
expecting: (complete)
next_action: none for bug #14 (resolved). For the newly-discovered 15th fatal (block_quote markup-mode leak), next investigation action would be: fix visit_block_quote/depart_block_quote in translator.py to emit code-mode content (e.g. `quote(body: [...])` or wrap the quote[...] body content in an explicit `#{...}` re-entry, or switch nested `par()/raw()/text()` calls to markup-safe form) so a lone markup-special character (underscore, asterisk, backtick, dollar) inside quoted prose can no longer be misparsed as an unclosed inline-emphasis/math span.

## Symptoms

expected: `-b typstpdf` on Sphinx's own doc/ corpus (development/tutorials/*) compiles to PDF with no fatal TypstCompilationError; code blocks with :linenos: (with or without explicit :lineno-start:) render line numbers starting at the correct value.
actual: typst.compile() raises `TypstError: unexpected argument: start` from the emitted `codly(start: N)\n` call -- codly 1.3.0 does not have a `start` parameter.
errors: |
  TypstError: unexpected argument: start
reproduction: sphinx-build -b typstpdf <sphinx-doc-clone>/development/tutorials <out>; any literalinclude/code-block with :linenos: hits this because literalinclude always sets highlight_args['linenostart'] (defaults to 1).
started: pre-existing bug introduced whenever the codly package was bumped to (or pinned at) 1.3.0, or when Issue #31's :lineno-start: support was implemented against an older codly API that had a `start:` parameter (unconfirmed which came first -- not required for the fix, only the correct 1.3.0 API surface matters).

## Eliminated

(none yet)

## Evidence

- timestamp: 2026-07-12T12:12Z
  checked: ~/.cache/typst/packages/preview/codly/1.3.0/codly.typ (full file, `#let codly(...)` parameter list lines 74-129)
  found: No `start` parameter anywhere in the `codly()` (or `local()`) signature. Parameters present instead: `offset (int, function)` and `offset-from (none, label, function)`.
  implication: `codly(start: N)` is guaranteed to fail with "unexpected argument: start" against 1.3.0 -- confirms the reported TypstError mechanically.

- timestamp: 2026-07-12T12:12Z
  checked: ~/.cache/typst/packages/preview/codly/1.3.0/src/args.json (offset / offset-from entries)
  found: "offset": {"default": "0", "ty": ["int"], description: "The offset to apply to line numbers. This is purely cosmetic, only impacting the shown line numbers in the final output."}. "offset-from": {"default": "none", ...} (unrelated -- cross-block offset chaining, not needed here).
  implication: default offset is 0 (int), confirming an explicit `offset: 0` would be a semantic no-op matching default behavior (still consider omitting for cleanliness per fix requirement #2).

- timestamp: 2026-07-12T12:12Z
  checked: ~/.cache/typst/packages/preview/codly/1.3.0/src/lib.typ lines 869-895, 1521-1542
  found: |
    let offset = (__codly-args.offset.type_check)(if "offset" in extra { extra.offset } else { state("codly-offset", __codly-args.offset.default).get() })
    ...
    lines_to_number.push(line.number + offset)
    items.push(numbers-format(line.number + offset))
    reference-number-format(line.number + offset)
  implication: displayed line number = `line.number + offset`, where `line.number` is the 1-indexed line number WITHIN the raw block. So for the first line (line.number == 1) to display as Sphinx's `linenostart`, the correct transform is `offset = linenostart - 1`. This is NOT "offset is the first line number directly" -- it is an additive delta, confirming the prior debug pass's suspicion in the bug brief.

- timestamp: 2026-07-12T12:12Z
  checked: .venv/lib/python3.13/site-packages/sphinx/directives/code.py lines 146-171 (CodeBlock.run) and 460-494 (LiteralInclude.run + LiteralIncludeReader.__init__ line 211)
  found: |
    CodeBlock (`.. code-block::`): `extra_args['linenostart']` is ONLY set when `'lineno-start' in self.options` (line 170-171) -- plain `:linenos:` alone never sets highlight_args['linenostart'], so `highlight_args.get("linenostart")` is None for plain :linenos: code-block.
    LiteralInclude (`.. literalinclude::`): `extra_args['linenostart'] = reader.lineno_start` is ALWAYS assigned (line 494, unconditional), and `reader.lineno_start = self.options.get('lineno-start', 1)` (line 211) -- defaults to 1 even without explicit :lineno-start:.
  implication: This explains the 20-occurrence / 4-tutorial-file footprint precisely -- Sphinx's own tutorial docs use `.. literalinclude::` with plain `:linenos:` (no explicit :lineno-start:), which still populates `linenostart=1` in highlight_args, tripping the existing `if linenos and lineno_start is not None:` gate in translator.py and emitting the fatal `codly(start: 1)` even for the "default" case. The fix must guard on `lineno_start not in (None, 1)`, not just `is not None`, to satisfy fix requirement #2 (no spurious emission for the default case) AND to stop this exact 20-occurrence fatal (all default-start literalinclude blocks).

- timestamp: 2026-07-12T12:12Z
  checked: tests/test_translator.py lines 919-1008 (three existing tests: test_literal_block_with_lineno_start, test_literal_block_with_lineno_start_without_linenos, test_literal_block_with_lineno_start_and_emphasize)
  found: Two tests assert `"codly(start: 42)" in output` / `"codly(start: 100)" in output` -- both encode the old, now-incorrect emission and must be updated to assert `codly(offset: 41)` / `codly(offset: 99)` respectively. The third test (without_linenos) only asserts the negative (`"#codly(start:" not in output`) and needs no behavior change but should additionally assert no `offset:` leak either, for symmetry.
  implication: exactly the "update+name any test that encoded the old start: emission" fix requirement #3 callout.

- timestamp: 2026-07-12T12:17Z
  checked: ran new fast regression test (TestCodlyOffsetRenderGate) both pre-fix (git stash of translator.py) and post-fix
  found: Pre-fix -- the source-level assert fails, showing `codly(start: 5)` (explicit :lineno-start: block) AND `codly(start: 1)` (plain :linenos: literalinclude, confirming the linenostart=1-default mechanism) both leaked into the emitted .typ. Post-fix -- test passes; emitted .typ contains `codly(offset: 4)` for the explicit case and NO codly offset/start call for either plain-linenos case.
  implication: fix verified in both directions (fails pre-fix with the exact predicted mechanism, passes post-fix).

- timestamp: 2026-07-12T12:20Z
  checked: full fast suite (`--ignore=...4 known-bad integration files... -m "not slow"`), `tests/test_preview_version_sync.py`, `black --check`, `nix-shell ruff check`, `mypy typsphinx/`
  found: 416 passed (fast suite), 2/2 preview-version-sync tests green, black clean after one reformat of the new test file, ruff clean, mypy clean (no issues in 6 source files).
  implication: no regressions; ready to commit.

- timestamp: 2026-07-12T12:25Z
  checked: re-ran `pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s` against the cached Sphinx v9.1.0 doc/ corpus clone, post-fix
  found: The codly `start:`/API-mismatch fatal (bug #14) no longer occurs -- sphinx-build succeeds, all docs write output, image copy succeeds, and the build proceeds all the way to "Compiling 1 master document(s) to PDF...". It now fails at a NEW, DISTINCT fatal: `TypstError: unclosed delimiter` (no line/file info from typst-py's exception). Reproduced persistently via `sphinx-build -b typstpdf <corpus>/doc <scratch>/corpus_build` (bypassing pytest's tmp_path cleanup) to enable bisection.
  implication: bug #14 (codly) is fully resolved at the corpus scale -- GATE-02 is NOT yet green, blocked by a distinct 15th fatal, which is out of this task's authorized scope (codly only). Investigated it far enough to report precisely (see next entry), per the bounded-discipline instruction, without fixing it.

- timestamp: 2026-07-12T12:35Z
  checked: bisected the ~1300-line generated index.typ (whole corpus merged via nested Typst `include()` calls) by selectively disabling top-level `include(...)` calls, then recursively bisecting within development/index.typ -> development/html_themes/index.typ -> truncation-point bisection within that single 657-line file -> isolated to lines 443-460 (a `quote[...]` block-quote body) -> isolated further to a single `raw("_t")` call. Confirmed with a minimal standalone repro: `#{ quote[par({text("The ") raw("_t") text(" file suffix...")})]}` alone reproduces `TypstError: unclosed delimiter`; a control test with `#{ quote[Some text with a # character in it] }` reproduces a related-class error (`expected expression`) proving `quote[...]`'s body is parsed as TYPST MARKUP MODE, not code mode.
  found: |
    typsphinx/translator.py's visit_block_quote (line ~2131) emits `quote[` for a docutils block_quote WITHOUT an attribution child. `quote[...]` is Typst's "trailing content block" syntax -- its body is parsed in MARKUP mode. But the nested paragraph/inline content generated by the rest of the translator (`par({text(...)})`, `raw(...)`, `link(...)`, `emph({...})`) assumes it is ALREADY in Typst CODE mode (no `#` prefix needed) -- which is true almost everywhere else in the document (inside `#{ ... }` blocks), but is FALSE inside `quote[...]`'s markup-mode body. Because these calls are unprefixed, they are NOT invoked as functions inside quote[...] -- they become literal markup prose. Any single occurrence of a markup-special character within that "literal" text (a lone `_` from `raw("_t")` -- Sphinx's `_t` static-template file suffix -- opens Typst inline-emphasis `_..._`, which is never closed within the block) triggers `TypstError: unclosed delimiter`.
  implication: this is bug #15, structurally similar in class to bugs #1-14 (markup-mode/code-mode leak) but a NEW site (visit_block_quote, not literal_block/codly). NOT fixed in this task (bounded scope -- codly only, per task authorization). Reported precisely below.

## Resolution

root_cause: |
  typsphinx/translator.py's visit_literal_block emitted `codly(start: {lineno_start})` for :linenos: code blocks with a known Sphinx linenostart, but the pinned @preview/codly:1.3.0 package's codly() function has no `start` parameter -- it was renamed/redesigned to `offset` (int, additive delta from the raw block's 1-indexed line.number), with displayed number = `line.number + offset`. Additionally, the existing `is not None` guard was too loose: Sphinx's LiteralInclude directive unconditionally populates highlight_args['linenostart'] (defaulting to 1) even without an explicit :lineno-start: option, so plain `:linenos:` literalinclude blocks (the exact construct used 20x across 4 Sphinx tutorial docs) always emitted a spurious codly(start: 1) call, which is the fatal hit by the corpus gate.
fix: |
  Replaced `codly(start: {lineno_start})` with a guarded `codly(offset: {lineno_start - 1})`, only emitted when `lineno_start` is not None AND not 1 (i.e., only when it actually differs from codly's default of offset=0 / Sphinx's default of linenostart=1). This fixes both the API-mismatch fatal and, as a side effect of the correct default-case guard, ensures literalinclude's always-populated linenostart=1 no longer triggers a spurious codly() call.
verification: |
  New fast regression test (TestCodlyOffsetRenderGate) verified FAILS pre-fix (git stash of
  translator.py) with the exact source-level leak (`codly(start: 5)` and `codly(start: 1)`) and
  PASSES post-fix (`codly(offset: 4)`, no start:/spurious offset: emission). Full fast suite:
  416 passed, 0 failed (incl. tests/test_preview_version_sync.py 2/2 green, unaffected -- version
  pins untouched). black/ruff/mypy clean on all changed files. Corpus gate (slow, real network +
  cached clone): bug #14 (codly) no longer occurs -- sphinx-build succeeds through the entire
  corpus and reaches "Compiling 1 master document(s) to PDF..." before hitting a NEW, DISTINCT
  fatal (bug #15, block_quote markup-mode leak -- see below). GATE-02 is therefore NOT YET green
  overall, but bug #14 specifically is fully resolved and verified at corpus scale.
files_changed:
  - typsphinx/translator.py (commit 777229c)
  - tests/test_translator.py (commit b9463a5)
  - tests/fixtures/codly_offset_render_gate/conf.py (new, commit b9463a5)
  - tests/fixtures/codly_offset_render_gate/index.rst (new, commit b9463a5)
  - tests/fixtures/codly_offset_render_gate/included_snippet.py (new, commit b9463a5)
  - tests/test_pdf_render_gate.py (commit b9463a5)

next_fatal_bounded_report: |
  Bug #15 (NOT fixed -- out of this task's authorized scope, reported per bounded-discipline
  instruction):
  - File:line: typsphinx/translator.py:2131 (visit_block_quote, `self.add_text("quote[")`) and
    :2146 (depart_block_quote, closing `]`).
  - TypstError: "unclosed delimiter" (typst-py's TypstError carries no file/line info; isolated
    via manual bisection of the persisted corpus build output, not the raw exception).
  - Construct: a docutils block_quote (rST indented quote, no attribution) whose body contains
    inline content with a markup-special character occurring an odd number of times (confirmed
    trigger: a single literal underscore via `raw("_t")`, i.e. Sphinx's `_t` static-template file
    suffix rendered as a `:literal:`/code-span inside prose). visit_block_quote emits `quote[`,
    Typst's markup-mode "trailing content block" syntax; every other paragraph/inline visitor in
    the translator emits unprefixed code-mode calls (`par({text(...)})`, `raw(...)`, `link(...)`)
    that are only valid because they normally run inside an already-open `#{ ... }` code block --
    inside `quote[...]`'s markup-mode body those same calls are NOT invoked as functions, they
    become literal prose, and any lone `_`/`*`/backtick/`$` within that prose opens an
    inline-emphasis/raw/math span that's never closed.
  - One-line hypothesis: visit_block_quote/depart_block_quote need to emit code-mode-safe content
    (e.g. `quote(body: [...])` with an explicit re-entry to code mode via `#{...}` for the nested
    calls, or restructure to avoid the bracket "trailing content" form entirely) instead of the
    markup-mode `quote[...]` wrapper.
  - Occurrence/file count: confirmed reproducing in development/html_themes/index.typ (the first
    document the corpus compile reaches with this exact trigger). A corpus-wide scan of the
    already-generated .typ output found 10 files / 11 total `quote[` (no-attribution block_quote)
    occurrences; of those, at least 4 files (faq.typ, development/html_themes/index.typ, latex.typ,
    extdev/nodes.typ) contain a `raw("_...")` call inside a quote[...] block -- a plausible but
    NOT exhaustively verified trigger heuristic (the true trigger is ANY odd count of
    markup-special characters within a quote[...] body, not only underscore/raw()). True
    occurrence count requires a fix + full rebuild to confirm.
