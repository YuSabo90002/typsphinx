# Phase 48 — Evidence Log

Created by plan 48-01, Task 2, Step 0. Later plans APPEND new sections to this file — never
overwrite it.

## Body-mode measurement

**Purpose:** D-08 says D-07's exact Typst syntax is unmeasured. Two candidate body spellings
exist and only one preserves today's child-emission bytes:

- `[#{` … `}]` — a content block wrapping a code block. Children keep streaming in code mode
  exactly as today (`_in_markup_mode` stays False, `_in_link` stays True), so no other visitor's
  emission moves and the corpus-wide body bytes do not change. This is the planner's derived
  preference and was NOT yet measured before this section.
- `[` … `]` — the bare content block PROJECT.md/research measured with hand-written markup
  children. Choosing it forces children into markup mode, changing the emitted body of every
  cross-document reference in the corpus.

**Methodology (binding constraint #6 compliance):** every probe below is a throwaway, HAND-WRITTEN
`.typ` file exercising the Typst LANGUAGE, not output read off the new emitter — the guard code
does not exist yet in `typsphinx/translator.py` at the time these probes were compiled
(`git status --porcelain typsphinx/` prints nothing throughout this task). This measurement does
NOT violate binding constraint #6 (which forbids deriving expected TEST values from the new
emitter's output) — these probes derive the SYNTAX contract itself, before any test asserts
against it. Every probe was compiled via `typst.compile(path)` (typst-py 0.15.0, same installed
version confirmed in `48-RED-EVIDENCE.md`'s provenance header) from this plan's own provisioned
worktree venv, under `/tmp/claude-.../scratchpad/48-01-probes/` (outside the repository, per the
scratchpad convention).

**Every probe is wrapped inside a `#{ ... }` / `par({ ... })` code-mode context**, not placed as
bare top-level markup prose. This matters: a bare `[` at the top level of a `.typ` document is
MARKUP mode by default, where `[`/`]` are LITERAL bracket characters with no content-block effect
— an earlier draft of probes 4/5 made exactly this mistake (placed the own-anchor bracket at
top-level markup prose) and still compiled with the query finding the label, but for the WRONG
reason (the label attached to loose inline text, not to a real content-block value), which would
have been a false positive per Pitfall 2's warning about test artifacts that look like a real
guard validation but are not representative. The real translator emits this construct from INSIDE
a `par({ ... })` code block (confirmed by reading a real compiled fixture,
`tests/fixtures/citation_render_gate/`'s emitted `index.typ`:
`par({text("...") \n [#link(<label>, \n text("[Cross2019]"))#label("index:id4")] \n text(".")})`),
so every probe below reproduces that exact code-mode wrapping.

### Probe 1 — `[#{` with a translator-shaped code-mode body (`+`-joined `text()`/`raw()` chain)

**Source (verbatim):**
```typst
= Doc

#{
par({text("Some text before ")
context { let __tsx_body = [#{text("first ") + raw("code segment") + text(" last")}]; if query(<present-label>).len() > 0 { link(<present-label>, __tsx_body) } else { __tsx_body } }
text(" and text after.")})
}

= Target <present-label>
Target section.
```

**Compile result, target PRESENT:** `typst.compile()` succeeds (19,033 bytes). `pypdf`-extracted
text: `"Doc\nSome text before first code segment last and text after.\nTarget\nTarget section."` —
the guarded body renders inline exactly as the unguarded form would. 3 `/Link` annotation rects
were found, all with `/Dest` = `present-label` — Typst splits one logical link into multiple
`/Rect`s across the font-run boundary where `raw("code segment")` switches to monospace, which is
expected Typst PDF-emission behaviour, not a guard defect (every rect points at the SAME
destination).

**Compile result, target ABSENT** (same source with the `= Target <present-label>` heading
removed): `typst.compile()` still succeeds. `pypdf`-extracted text:
`"Doc\nSome text before first code segment last and text after."` — the reference's text still
renders, with **0** `/Link` annotations. No error either way.

### Probe 2 — `[#{` with an EMPTY body (the edge/empty case the guard must not turn into a syntax error)

**Source (verbatim):**
```typst
= Doc

#{
par({text("Some text before ")
context { let __tsx_body = [#{}]; if query(<present-label>).len() > 0 { link(<present-label>, __tsx_body) } else { __tsx_body } }
text(" and text after.")})
}

= Target <present-label>
Target section.
```

**Compile result:** `typst.compile()` succeeds (11,344 bytes). `pypdf`-extracted text:
`"Doc\nSome text before  and text after.\nTarget\nTarget section."` (note the double space where
the empty body contributed nothing). **0** `/Link` annotations — even with the target PRESENT, an
empty guarded body produces no visible link annotation, since there is no glyph content for Typst
to attach a clickable rect to. No error. Confirms the empty-body edge case does not become a
syntax error.

### Probe 3 — `[#{` with a body containing a nested `link("https://example.com", text("x"))`

**Source (verbatim):**
```typst
= Doc

#{
par({text("Some text before ")
context { let __tsx_body = [#{text("see ") + link("https://example.com", text("here"))}]; if query(<present-label>).len() > 0 { link(<present-label>, __tsx_body) } else { __tsx_body } }
text(" and text after.")})
}

= Target <present-label>
Target section.
```

**Compile result:** `typst.compile()` succeeds (12,125 bytes). `pypdf`-extracted text:
`"Doc\nSome text before see here and text after.\nTarget\nTarget section."`. 2 `/Link`
annotations — one for the OUTER guard link (`/Dest` = `present-label`) and one for the NESTED
external `link("https://example.com", ...)` — both compile cleanly nested inside the guarded body,
confirming arbitrary child markup (including another `link()` call) streams unchanged inside
`[#{ ... }]`.

### Probe 4 — the own-anchor combination (`_reference_own_anchor` bracket-wrap composed with the guard)

`visit_reference` emits a bare `[` and enters markup mode when `decision.eligible` is true, and
`depart_reference` closes with `#label("...")]` AFTER the link's closing `)`. Replacing that `)`
with the guard's close string changes the nesting; this combination was not among research's 34
compiled probes. D-09 makes `opens_wrapper` unconditional in 48-02, which is precisely what makes
a citation-derived CROSS-document reference simultaneously eligible for its own anchor and routed
through the guard, so this combination is not hypothetical.

**Source (verbatim):**
```typst
= Doc

#{
par({text("Some text before ")
[#context { let __tsx_body = [#{text("[Cited]")}]; if query(<present-label>).len() > 0 { link(<present-label>, __tsx_body) } else { __tsx_body } } #label("citing-anchor")]
text(" and text after.")})
}

#context [Query result: #query(<citing-anchor>).len()]

= Target <present-label>
Target section.
```

**Compile result, target PRESENT:** `typst.compile()` succeeds (12,676 bytes). `pypdf`-extracted
text: `"Doc\nSome text before [Cited]  and text after.\nQuery result: 1\nTarget\nTarget section."`
— **the query for `<citing-anchor>` finds exactly 1 match**, confirming the `#label(...)` attaches
to the outer bracketed content (the WHOLE `[#context {...} #label(...)]` construct), not merely to
loose inline text. 1 `/Link` annotation (`/Dest` = `present-label`), from the guard's positive
branch.

**Compile result, target ABSENT** (same source, `= Target <present-label>` heading removed):
`typst.compile()` still succeeds. `pypdf`-extracted text:
`"Doc\nSome text before [Cited]  and text after.\nQuery result: 1"` — **the own-anchor label STILL
attaches** (`Query result: 1`) even when the guard's target is absent and the guarded expression
degrades to plain text. This confirms the own-anchor and the guard's cross-document query are
INDEPENDENT: the anchor is same-document-derived (D-09's reasoning) and its attachment does not
depend on whether the guard's own target resolves. 0 `/Link` annotations (the guard degraded, as
expected).

### Probe 5 — the own-anchor combination with an empty body

**Source (verbatim):**
```typst
= Doc

#{
par({text("Some text before ")
[#context { let __tsx_body = [#{}]; if query(<present-label>).len() > 0 { link(<present-label>, __tsx_body) } else { __tsx_body } } #label("citing-anchor")]
text(" and text after.")})
}

#context [Query result: #query(<citing-anchor>).len()]

= Target <present-label>
Target section.
```

**Compile result, target PRESENT:** `typst.compile()` succeeds (12,131 bytes). `pypdf`-extracted
text: `"Doc\nSome text before   and text after.\nQuery result: 1\nTarget\nTarget section."` — the
own-anchor label still attaches (`Query result: 1`) even with an empty guarded body. 0 `/Link`
annotations (matching Probe 2's empty-body finding: no glyph content, so no clickable rect, even
though the guard's positive branch was taken).

### Adopted spelling

**All five cases (1, 2, 3, 4, 5) compiled successfully in BOTH the target-present and
target-absent configurations, with no `TypstError` in any of the ten compiles.** Per the plan's
own decision rule ("Adopt `[#{` if cases 1-3 and 5 compile; otherwise fall back to the bare `[`
form"), **`[#{` … `}]` is ADOPTED** as D-07/D-08's body-mode spelling — it preserves today's
code-mode child-emission bytes exactly (no other visitor's emission moves), and the own-anchor
composition (case 4/5) confirmed the `#label(...)` closing pair correctly attaches to the whole
bracketed construct regardless of the guard's own query outcome.

### Guard contract, fixed by this measurement

- Shared helper: `TypstTranslator._label_existence_guard(label, *, prefix="", code_mode_body=False)`,
  returning a `_LabelGuardStrings` `NamedTuple` with fields `open_str` and `close_str`.
- Bound identifier: `__tsx_body`.
- When `code_mode_body=True` (the ADOPTED spelling for all three D-07 sites — every site's
  existing children already stream in code mode): `open_str` ends with `= [#{` and `close_str`
  begins with `}];`.
- When `code_mode_body=False` (unused by this phase's three sites, but the parameter is kept for
  completeness/future callers whose children already stream in markup mode): `open_str` ends with
  `= [` and `close_str` begins with `];`.
- `close_str`'s conditional is one unbroken statement — `if query(<L>).len() > 0 {` never has a
  newline between the condition and its opening brace (Pitfall 1's `expected block` parse error).
- Own-anchor composition: when the caller has also opened the `_reference_own_anchor`
  bracket-wrap (`self.add_text("[")` + `self._in_markup_mode = True` in `visit_reference`), the
  `#label("…")]` closing pair lands AFTER `close_str`, OUTSIDE the `context { … }` block — exactly
  the shape Probe 4/5 compiled and verified query-findable.

**Fully substituted example** (label `target:xref-guard-target`, `code_mode_body=True`,
`prefix=""`):

```
open_str:  context { let __tsx_body = [#{
close_str: }]; if query(<target:xref-guard-target>).len() > 0 { link(<target:xref-guard-target>, __tsx_body) } else { __tsx_body } }
```
