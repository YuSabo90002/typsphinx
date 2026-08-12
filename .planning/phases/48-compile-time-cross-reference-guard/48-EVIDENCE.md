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

## D-11 compile-time cost

**Purpose:** measure what the compile-time guard actually costs at full-corpus scale, against
thresholds fixed **before** this measurement was taken, so a measured regression cannot be
rationalised after the fact.

### D-11's three tiers, quoted verbatim from `48-CONTEXT.md` (fixed at discussion time, 2026-08-12,
before any measurement in this section)

> under `+20%` the number is recorded and nothing else happens; between `+20%` and `+100%` it is
> recorded as an explicit finding in the phase evidence and an improvement todo is filed; above
> `+100%` it is escalated to a blocker attached to Phase 49's scope.

And the realistic remediation path if the top tier were hit, also quoted verbatim: "replace
`query(<L>).len() > 0` with a lookup against Phase 49's `state("inc", ())` include set once that
exists — abandoning the design is not available, since binding constraint #1 makes Phase 49
depend on the guard."

These were fixed at discussion time, before any measurement — the reading order above (tiers
first, number below) is itself the evidence that they were not renegotiated after the fact.

### Pre-fix baseline, quoted verbatim from `48-VALIDATION.md`'s "Test Infrastructure" table

> `tests/test_corpus_gate.py` full-corpus `-b typstpdf` → **28.93s / 28.56s** (D-11 "before"
> baseline)

Per `48-RESEARCH.md` assumption A3, these absolute numbers are specific to the measuring machine
— the after-number below was taken on the **same machine** (this worktree, provisioned per
`CLAUDE.md`'s `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` +
`uv run` protocol) so the ratio between before and after means something; the tiering logic
itself is relative (a percentage), not tied to any absolute wall-clock figure.

### After-measurement — two raw transcripts, `time uv run pytest tests/test_corpus_gate.py -m slow`
(the exact invocation `48-VALIDATION.md`'s "D-11 'after' measurement" row names)

**Run 1:**

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae7d93eaa5ed0d932/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae7d93eaa5ed0d932
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 5 items / 3 deselected / 2 selected

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 50%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3...) [100%]

================= 1 passed, 1 skipped, 3 deselected in 28.92s ==================

real	0m29.483s
user	0m27.747s
sys	0m1.582s
```

**Run 2:**

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae7d93eaa5ed0d932/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-ae7d93eaa5ed0d932
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 5 items / 3 deselected / 2 selected

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 50%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3...) [100%]

================= 1 passed, 1 skipped, 3 deselected in 27.21s ==================

real	0m27.567s
user	0m26.401s
sys	0m1.485s
```

`test_empty_url_before_after` SKIPs (env-gated behind `TYPSPHINX_CORPUS_REPORT=1`, unrelated to
D-11) in both runs — the pytest-reported duration line (`28.92s` / `27.21s`) is the corpus
render gate's own wall-clock time, matching the invocation the baseline was itself taken with.

### Arithmetic

- Pre-fix baseline mean: `(28.93 + 28.56) / 2 = 28.745s`
- After-guard mean: `(28.92 + 27.21) / 2 = 28.065s`
- Delta: `28.065 - 28.745 = -0.680s`
- Percentage change: `-0.680 / 28.745 * 100 = -2.37%`

The measured change is **-2.37%** — the corpus build is very slightly FASTER after the guard
landed than the pre-fix baseline, well within measurement noise for a ~28s wall-clock subprocess
build (network/disk/scheduler jitter dwarfs a single-digit-percent difference here). This falls in
the **bottom tier** (under `+20%`).

### Tier applied

**Bottom tier: record only.** The guard's corpus-scale cost is not a material regression — it is,
if anything, indistinguishable from noise around zero. No todo is filed and no `STATE.md` blocker
is added, exactly as the bottom tier's own instruction says: "record only." No sentence naming a
Phase 49 coupling is required here — that obligation is scoped to the middle and top tiers only,
neither of which was reached.

### Verification that no timing instrumentation was added

```
$ git diff --stat tests/test_corpus_gate.py
(no output)
$ grep -Ec 'assert.*(elapsed|duration|time\.)' tests/test_corpus_gate.py
0
```

`tests/test_corpus_gate.py` still carries no timing instrumentation and no wall-clock assertion —
this measurement is the one-off manual record D-11 specifies, not a permanent, CI-flaky assertion.
