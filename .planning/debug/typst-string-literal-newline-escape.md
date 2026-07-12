---
status: awaiting_human_verify
trigger: "Corpus gate fatal: TypstError: expected semicolon or line break. translator emits raw()/text() Typst string literals containing an UNESCAPED literal newline when inline-literal/text source wraps across a physical line (~31 occurrences across ≥6 generated files)."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## MISDIAGNOSIS CORRECTION (scientific finding)

The prior-pass premise (unescaped newline in raw()/text() causes the fatal) is
FALSE. Empirically, Typst 0.15.0 TOLERATES a raw newline inside a "..." string
literal (verified: `#let x = "a<newline>b"` compiles fine). The construct that
actually produces `expected semicolon or line break` is an UNESCAPED `"`
(closes the string early) OR two adjacent code-mode expressions with no
separator. Reverting the newline-escaping and recompiling the corpus produced
the IDENTICAL first fatal — proving the newline escape changes nothing about
the fatal.

REAL root cause of the second GATE-02 blocker: `visit_target` emitted a bare
code-mode `label("id")`. Two consecutive `target` nodes (e.g. the two anonymous
hyperlink targets `__ https://...` closing a `.. tip::`) produced
`label("id1")label("id2")` — adjacent expressions, a Typst syntax error
(usage/installation.typ:56:12). A bare label is also a raw label *value* that
"cannot join content with label" even singly, and an anchor directly followed
by a paragraph produced `]par(` (a second adjacency).

## Current Focus

reasoning_checkpoint:
  hypothesis: "translator.visit_literal (typsphinx/translator.py:807-815) emits `raw(\"<node.astext()>\")` but escapes ONLY backslash (810) and quote (811). It does NOT escape newline/CR/tab. When an inline literal's source text wraps across physical lines, node.astext() carries an embedded \\n. That raw literal newline lands inside the Typst \"...\" string, which cannot span physical lines → 'TypstError: expected semicolon or line break'. visit_Text (629) does NOT hit this because it applies the full 5-step escape (598-602). The fix class is: route both string-literal emissions through ONE shared escaper that always escapes backslash-first, then quote, newline, CR, tab."
  confirming_evidence:
    - "visit_literal (810-811) escapes backslash + quote only; visit_Text (598-602) escapes backslash+quote+newline+CR+tab. The two sites disagree; only the raw() site is missing newline escaping — exactly the failing construct."
    - "Corpus fatal examples are inline literals: latex.typ:351 raw(\"'extraclassoptions': <newline> 'openany'\"), changes/1.0.typ:359 raw(\":param type <newline> name: description\") — both wrapped inline literals whose node text carries \\n, emitted via visit_literal."
    - "Typst string literals \"...\" are single-physical-line; an embedded raw \\n is a syntax error, producing precisely 'expected semicolon or line break'."
  falsification_test: "If, after routing visit_literal through a full escaper (newline→\\n etc.), a tiny fixture with an inline literal containing an embedded newline STILL fails typst.compile with 'expected semicolon or line break', the hypothesis is wrong."
  fix_rationale: "Centralize into one _escape_typst_string(text) helper implementing the correct-order escape (backslash FIRST to avoid double-escaping, then quote, newline, CR, tab). Route BOTH visit_Text and visit_literal through it. visit_Text output is unchanged (its inline logic already matched the helper). visit_literal now also escapes newline/CR/tab → the raw literal newline becomes the two-char sequence \\n inside the Typst string, which renders as a literal newline in the raw content (correct semantics for a wrapped literal) AND is valid single-line Typst syntax. General across every raw()/text() emission, not the two example strings."
  blind_spots: "link(\"<refuri>\", ...) at 2381 and rect(text(\"[<node_label>...]\")) at 3113 are other \"...\" emissions, but refuri is a URL (no legit embedded newline; a stray quote/backslash would already be broken today) and node_label is a fixed internal vocabulary — neither is the wrapped-inline-literal class. Per scope discipline, if the corpus surfaces a DISTINCT link/label escaping fatal after this fix, report it, don't chase. Escaped-caption at 1080-1083 is markup [...] content, not a string literal — out of scope."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: add _escape_typst_string helper; route visit_Text + visit_literal; build tiny inline-literal-with-newline fixture via -b typstpdf; re-run corpus gate
expecting: fixture compiles to %PDF with no 'expected semicolon or line break'; corpus advances past the 31 raw()/text() newline fatals
next_action: Add helper, edit visit_Text (597-602) and visit_literal (810-811) to call it, add regression test + unit test, run fast suite + lint + corpus gate.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal TypstCompilationError; inline literals whose source wraps across lines emit valid Typst string literals.
actual: "Typst compilation failed: TypstError: expected semicolon or line break" — translator emits raw(\"...\")/text(\"...\") string literals containing an unescaped literal newline. ~31 occurrences across ≥6 generated files.
errors: "TypstError: expected semicolon or line break"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate, after the asset-copy fix (c671e8b) unblocked the compile path.

## Eliminated

## Evidence

- timestamp: initial
  checked: grep for all Typst string-literal emission sites and escaping in translator.py
  found: Two arbitrary-node-text string emitters. visit_Text (629) `text("{content}")` with full 5-step escape (598-602). visit_literal (815) `raw("{content}")` with ONLY backslash+quote escape (810-811). Other "..." sites (link refuri 2381, node_label 3113) are non-wrapped-literal classes.
  implication: visit_literal is missing newline/CR/tab escaping → the exact failing class. Fix = centralize + apply full escape to raw().

- timestamp: initial
  checked: grep existing test assertions on raw()/text() output
  found: tests assert only simple forms: raw("code"), raw("code_reference"), raw("print()"), text("Code: "). None contain newline/quote/backslash, so none encode the OLD unescaped behavior.
  implication: Routing both sites through the helper is a no-op for visit_Text and safe for the existing raw() tests; no expectation needs updating.

## Evidence (investigation this session)

- timestamp: verify-premise
  checked: Compiled isolated `raw("a<newline>b")` and `#let x="a<newline>b"` via typst.compile (typst 0.15.0)
  found: BOTH compile to %PDF. Raw newlines inside Typst string literals are TOLERATED. An unescaped `"` (`"a"b"`) is what yields `expected semicolon or line break`.
  implication: The prior-pass "unescaped newline" root cause is a misdiagnosis. Newline escaping does not fix the fatal.

- timestamp: corpus-first-fatal
  checked: Built the cached corpus via -b typst, compiled master index.typ directly, WITH and WITHOUT the newline-escape change
  found: IDENTICAL first fatal both ways: usage/installation.typ:56:12 `label("id1")label("id2")` → expected semicolon or line break.
  implication: Real blocker = adjacent bare label() from visit_target, NOT string escaping.

- timestamp: fix-design
  checked: Tested candidate anchor forms via typst.compile in the faithful tip({par({...}) <anchor> <anchor>}) context
  found: bare `label()` fails (adjacent syntax error; single "cannot join content with label"). `\n[#metadata(none) <id>]\n` (metadata markup block, matching visit_title extra-id anchors) compiles singly, consecutively, after-text, before-par, and stays reachable via link(<id>).
  implication: Fix visit_target to emit the metadata-label markup anchor wrapped in newlines.

- timestamp: fix-applied
  checked: Rebuilt+recompiled corpus after the visit_target fix; ran fast suite + new render gate both directions
  found: installation.typ label fatals GONE. tests/test_target_label_render_gate.py FAILS pre-fix (exact fatal), PASSES post-fix. Fast suite 396 passed / 15 deselected. black/ruff/mypy clean.
  implication: Label fix confirmed and regression-locked.

- timestamp: corpus-next-fatal
  checked: Re-ran the slow corpus gate with the label fix
  found: GATE-02 still RED on a DISTINCT class: tutorial/getting-started.typ:127:147 `TypstError: expected comma` — `terms.item(raw("make.bat")text(" and ")raw("Makefile"), ...)`: definition-list term inline nodes juxtaposed with no `+`.
  implication: Adjacent-label class fixed. Next blocker is a separate def-list-term `+`-concatenation bug → STOP per scope discipline (fix_requirements #4).

## Resolution

root_cause: (SECOND GATE-02 fatal) visit_target emitted a bare code-mode `label("id")`. Two consecutive target nodes → `label("id1")label("id2")` (adjacent expressions, Typst syntax error "expected semicolon or line break", usage/installation.typ:56:12); a bare label also "cannot join content with label" even singly; an anchor followed by a paragraph produced `]par(`. The prior-pass "unescaped newline in raw()/text()" premise was a MISDIAGNOSIS — Typst 0.15 tolerates raw newlines in strings, and reverting the newline escape reproduces the identical fatal.
fix: (primary) visit_target now emits `\n[#metadata(none) <id>]\n` — a metadata-carrying markup anchor wrapped in newlines, matching visit_title extra-id anchors: genuine content with the label attached, valid singly/consecutively, reachable via link(<id>). (hardening, requested) Centralized string-literal escaping into escape_typst_string(text) (backslash-first, then quote/newline/CR/tab); visit_Text and visit_literal both route through it, so raw() escapes newline/CR/tab consistently with text(). NOT the fatal fix.
verification: tests/test_target_label_render_gate.py passes with fix, fails pre-fix with the exact fatal (both directions via revert). escape_typst_string unit tests pass. Fast suite 396 passed / 15 deselected (updated test_target_label_generation expectation from bare label("my-label") to [#metadata(none) <my-label>]). black/ruff/mypy clean. Corpus gate advanced past the label fatal; now RED on the DISTINCT terms.item `expected comma` fatal (getting-started.typ:127) — reported, not fixed (bounded scope).
files_changed: [typsphinx/translator.py, tests/test_translator.py, tests/test_typst_string_escape_gate.py, tests/test_target_label_render_gate.py, tests/fixtures/target_label_render_gate/conf.py, tests/fixtures/target_label_render_gate/index.rst]
