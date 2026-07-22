---
phase: 20-signature-token-spacing-cluster-b
reviewed: 2026-07-20T21:00:00Z
depth: deep
files_reviewed: 8
files_reviewed_list:
  - typsphinx/translator.py
  - tests/test_desc_sig_space_render_gate.py
  - tests/fixtures/desc_sig_space_render_gate/conf.py
  - tests/fixtures/desc_sig_space_render_gate/index.rst
  - tests/test_confval_field_spacing_render_gate.py
  - tests/fixtures/confval_field_spacing_render_gate/conf.py
  - tests/fixtures/confval_field_spacing_render_gate/index.rst
  - tests/test_field_list_in_list_item_render_gate.py
findings:
  critical: 1
  warning: 1
  info: 0
  total: 2
status: issues_found
---

# Phase 20: Code Review Report

**Reviewed:** 2026-07-20T21:00:00Z
**Depth:** deep
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed the four Phase 20 commits (206aa32, 9c4b087, 68ca123, 5691d61) on
`gsd/v0.6.2-rendering-fidelity-round-2`: the `desc_sig_space` → `pass`/`pass`
fix (FID-07/FID-08) and the field-list colon-space + inter-field separator
fix (FID-09), plus their four new/updated render-gate tests.

**Plan 20-01 (`desc_sig_space` pass/pass) is sound.** `desc_sig_space` always
carries exactly one `Text(" ")` child (`sphinx.addnodes.desc_sig_space.__init__`
defaults `text=' '`, and every call site across `sphinx/domains/{python,javascript}`
uses either the no-arg or default-text form — confirmed by grepping the
installed Sphinx package), so removing the `SkipNode` short-circuit is safe:
`visit_Text` now owns the emission uniformly, matching the four sibling
`desc_sig_*` handlers. Confirmed no `list_item_needs_separator` regression by
building a `py:class` signature nested inside a bullet-list item (not
previously gate-tested) — compiles and paginates correctly. Full fast suite
(487 tests), `black --check`, `ruff check`, and `mypy` all pass.

**Plan 20-02 (field colon-space + inter-field separator) has a real
regression that the phase's own tests do not catch.** `depart_field_name`'s
colon-space fix is correct and low-risk. `depart_field`'s new
sibling-guarded `text("  ")` separator, however, is unconditional on
*any* following field sibling — it does not check whether the field it
just closed used the "collapsed inline" field-body form (the one narrow
case the new fixtures exercise) or the far more common paragraph-wrapped
field-body form. For a paragraph-wrapped body the separator lands as an
orphaned `text("  ")` statement *between* the closed `par({...})` block and
the next field's `strong(`, which Typst renders as a literal two-space
indent glued to the front of the next field's label — not as a
same-line boundary between adjacent values (the only case the pinned
`"Type: int (a number)  Default: 42"` SC#3 string covers). See CR-01 for
reproduction, including via the phase's own committed fixture.

## Critical Issues

### CR-01: Inter-field double-space separator corrupts every paragraph-wrapped field list (common case), not just the targeted inline-collapsed confval repro

**File:** `typsphinx/translator.py:4671-4683`

**Issue:** `depart_field` unconditionally emits `\ntext("  ")\n` whenever
`node.next_node(descend=False, siblings=True)` finds a following field
sibling — regardless of whether the field it just closed rendered its body
inline (same code-mode run, no block wrapper) or as a block (`par({...})`,
a list, etc., via the normal, non-collapsed docutils path). The fix was
validated only against the collapsed-inline-body form (see
`tests/fixtures/confval_field_spacing_render_gate/index.rst`, whose own
docstring says the fixture deliberately reproduces "the docutils
'directive option list' [no-blank-line] form... which collapses each field
body's children to bare inline nodes... (no wrapping `paragraph`)"). Any
other field-body shape — a one-line field value written with a blank line
before it, a multi-word field value that docutils wraps in a `paragraph`,
or a `:param:`/`:type:`/`:returns:`/`:rtype:` docstring-style field list
(Sphinx's most common field-list rendering pattern) — is *not* collapsed,
and the separator lands in the wrong place.

Concretely reproduced three ways:

1. A synthetic `:param x: ... :type x: ... :param y: ... :returns: ... :rtype: ...`
   field list (the canonical autodoc parameter-list shape) renders
   (pypdf-extracted PDF text):
   ```
   param x:
   the x value
     type x:
   int
     param y:
   the y value
     type y:
   int
     returns:
   the sum
     rtype:
   int
   ```
   Every field after the first gets a stray leading two-space indent
   glued to its label (`  type x:`, `  param y:`, `  returns:`, `  rtype:`).
   Confirmed pre-fix (commit `68ca123~1`) does **not** exhibit this
   artifact — this is a genuine regression introduced by 68ca123, not a
   pre-existing issue.

2. The phase's own committed fixture,
   `tests/fixtures/field_list_in_list_item_render_gate/index.rst`, has a
   top-level two-field list (`:Author: Test Author` / `:Version: 1.0.0`),
   both paragraph-wrapped. Building it emits:
   ```
   strong(text("Author") + text(": "))
   par({text("Test Author")})

   text("  ")
   strong(text("Version") + text(": "))
   par({text("1.0.0")})
   ```
   and the compiled PDF's extracted text reads
   `"Author: \nTest Author\n  Version: \n1.0.0"` — the same stray
   `"  Version:"` artifact. `tests/test_field_list_in_list_item_render_gate.py`
   only asserts on the `Author` field's rendering (line 171); it never
   asserts on `Version`, so this exact defect is present in a file this
   phase's own commit touched (68ca123 updated this test's `Author`
   assertion) and shipped unnoticed.

3. A two-field list with a `bullet_list` body on the first field followed
   by a simple second field reproduces the same misplaced separator.

**Fix:** Only emit the inter-field separator when the field that was just
closed rendered its body in the collapsed-inline form (i.e., mirror the
`_in_field_body`/all-inline state `visit_field_body`/`depart_field_body`
already track). For a block-wrapped body, `depart_field_body`'s existing
`self.body.append("\n")` plus the next field's `strong(` on a fresh
statement is already sufficient separation — the extra `text("  ")` token
should not be emitted there. For example, capture the just-closed field's
mode before `depart_field_body` restores the parent state:

```python
def depart_field_body(self, node: nodes.field_body) -> None:
    # Remember whether THIS field body was collapsed-inline, for
    # depart_field's separator decision, before popping back to the
    # parent's saved state.
    self._last_field_body_was_inline = self._in_field_body
    self._in_field_body, self._field_body_has_content = self._field_body_stack.pop()
    self.body.append("\n")

def depart_field(self, node: nodes.field) -> None:
    if (
        getattr(self, "_last_field_body_was_inline", False)
        and node.next_node(descend=False, siblings=True)
    ):
        self.body.append('\ntext("  ")\n')
```

Add a paragraph-wrapped / block-body multi-field regression case to the
new or existing render-gate suite (e.g., assert on the fixture's own
`Version` field, or add a `:param:`/`:type:` style fixture) so this class
of regression is caught going forward.

## Warnings

### WR-01: New test coverage exercises only the inline-collapsed field-body path, missing the far more common block-wrapped case

**File:** `tests/test_confval_field_spacing_render_gate.py`, `tests/fixtures/confval_field_spacing_render_gate/index.rst`, `tests/test_field_list_in_list_item_render_gate.py`

**Issue:** Both the new GATE-01 fixture (confval, no-blank-line,
inline-collapsed field bodies) and the updated assertion in
`test_field_list_in_list_item_render_gate.py` (which only checks the
`Author` field, not the co-located `Version` field in the same fixture)
validate a narrower shape than the one `depart_field`'s unconditional fix
actually touches. This gap is exactly what let CR-01 ship: the fixture
that would have caught it (`field_list_in_list_item_render_gate/index.rst`)
was already present and already had a second field (`Version`) available,
but no assertion was added for it.

**Fix:** Add a positive/negative assertion pair for the `Version` field in
`test_field_list_in_list_item_render_gate.py` (e.g. assert
`'par({text("Test Author")})\nstrong(text("Version")'` — no intervening
`text("  ")` — rather than the buggy `'par({text("Test Author")})\n\n\n\ntext("  ")\nstrong(text("Version")'`
shape), and/or add a dedicated paragraph-wrapped-field-body render gate
alongside the inline-collapsed one, so both field-body shapes are covered
by the regression suite.

---

## Verification performed

- `black --check`, `ruff check`, `mypy typsphinx/` — all pass on the
  changed files.
- `pytest tests/ -m "not slow" -q` — 487 passed, 0 failed (includes all
  four new/updated Phase 20 tests).
- Confirmed `desc_sig_space` always has exactly one `Text(" ")` child
  across every Sphinx built-in call site (python/javascript domains) —
  the `pass`/`pass` reduction cannot under- or over-emit for those
  domains.
- Confirmed no injection/escaping concern: the only new emitted literals
  (`": "`, `"  "`) are fixed ASCII constants, never derived from
  user/document content; `visit_Text`'s existing `escape_typst_string()`
  call path is untouched.
- Confirmed the `@preview` version-sync surface (`writer.py`,
  `template_engine.py`, `templates/base.typ`) and `pyproject.toml` are
  untouched by all four commits.
- Reproduced CR-01 three independent ways (synthetic `:param:`/`:type:`
  docstring list, the phase's own `field_list_in_list_item_render_gate`
  fixture's untested `Version` field, and a bullet-list-bodied field
  followed by a plain field), and confirmed via `git show 68ca123~1` that
  the artifact is absent pre-fix (i.e., a genuine regression, not
  pre-existing).

---

_Reviewed: 2026-07-20T21:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
