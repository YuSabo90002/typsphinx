# Phase 34: Inline Math After Text — Separator Fix - Research

**Researched:** 2026-07-28
**Domain:** `typsphinx/translator.py` inline-node emission — Typst code-mode statement/expression
separator protocol
**Confidence:** HIGH (root cause and fix pattern empirically reproduced and measured; no external
library research needed — this is a pure codebase-internal logic bug)

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|--------------------|
| MATH-01 | A paragraph where inline math immediately follows text builds through `typstpdf` without a Typst compile error — the emitted `.typ` carries a valid separator between the preceding text emission and the `mi(...)` / `$...$` call. Covers both the mitex default path and the native path. Pinned by a real `typst.compile()` GATE-01 regression fixture proven fail-pre-fix. | Root cause measured (visit_math's non-participation in the concat-context and list-item separator protocols — see Summary/Architecture Patterns); exact fix shape specified (mirror `visit_literal`, one fix point covers both mitex and native branches, see Code Examples); GATE-01 fixture guidance specified (Validation Architecture, Wave 0 Gaps); regression coverage for existing math tests confirmed at green baseline (23/23) |
</phase_requirements>

## Summary

The backlog's own hypothesis ("`translator.py` math/Text visit ordering" in a plain paragraph) is
**empirically false** — confirmed by direct reproduction. A plain top-level paragraph with inline
math immediately after text, including the no-intervening-space form (`text\ :math:`x`\ text`),
**already compiles and renders correctly today**. `visit_math`'s call to `_add_paragraph_separator()`
(`translator.py:3936-3954`) is sufficient there.

The real defect is a **scope gap**: `visit_math` (and structurally, `visit_math_block`) never
participates in the OTHER two separator protocols every other leaf inline node handler
(`visit_Text`, `visit_literal`, `visit_emphasis`, `visit_strong`, `visit_reference`) already
implements — the code-mode inline-concat-context protocol (`_emit_inline_concat_separator` /
`_mark_inline_concat_content`, used inside definition-list terms, link bodies, desc parameters,
collapsed-inline field bodies, and block-quote attributions) and the list-item separator protocol
(`self.in_list_item and self.list_item_needs_separator`). `_add_paragraph_separator()` is a no-op
in every one of these contexts (`self.in_paragraph` is deliberately `False` there — see
`visit_paragraph`'s list-item branch, `translator.py:791-794`), so when math is emitted immediately
after another expression in one of these five contexts, the two Typst expressions land on the page
with **zero characters between them** — e.g. `text("Text before math ")mi(`E=mc^2`)` — which Typst's
parser rejects with `expected comma` (inside a function-argument context like a term/link body) or
`expected semicolon or line break` (inside a `list.item({...})` content block). This is empirically
reproduced below on **both the mitex and native paths** (the branch selection happens after the
separator code, so one fix point covers `mi(...)`/`$...$` identically) and in **list items** (the
single most likely real-world shape of "a paragraph with math after text" — a list item's first
paragraph is unwrapped from `par({...})`, exactly the condition under which
`_add_paragraph_separator()` goes silent) and in a **definition-list term**.

**Primary recommendation:** Rewrite `visit_math` (`translator.py:3936`) to follow the exact
separator-participation pattern already used by `visit_literal` (`translator.py:1282`, the closest
structural analog — both are leaf inline nodes with a single emission and `raise nodes.SkipNode`):
keep the existing `_add_paragraph_separator()` call, then gate on
`if not self._emit_inline_concat_separator(): if self.in_list_item and
self.list_item_needs_separator: self.add_text("\n")` before emitting the `mi(...)`/`$...$` content,
and set `if not self._mark_inline_concat_content(): if self.in_list_item:
self.list_item_needs_separator = True` after emitting the content (and its optional label anchor)
but before `raise nodes.SkipNode`. No new helper is needed — the five-context concat machinery and
the list-item flag already exist and are shared with every other inline visitor.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| reST inline-math parsing (`:math:` role → `nodes.math`) | docutils/Sphinx parser | — | Upstream; unmodified by this phase |
| Typst statement/expression separator emission | `TypstTranslator` (`translator.py`) | — | The bug and the fix both live entirely here — no other layer participates in separator decisions |
| Typst compile-time syntax validation | `typst-py` (`pdf.py` wrapper) | — | Read-only signal for this phase: the regression fixture asserts on `typst.compile()`'s pass/fail, never modifies compile behavior |
| PDF text-content fidelity check | `pypdf` (test-only) | — | Verification tooling only, not shipped code |

## Standard Stack

No new libraries. This phase is a pure logic fix inside `typsphinx/translator.py` using helpers
that already exist in the codebase (`_emit_inline_concat_separator`, `_mark_inline_concat_content`,
`self.list_item_needs_separator`). Test-side dependencies (`typst-py`, `pypdf`) are already
installed dev dependencies used by every other GATE-01 render-gate test in this repo.

### Core (already present, no version changes)
| Library | Version (verified installed) | Purpose | Why Standard |
|---------|-------------------------------|---------|---------------|
| `typst` (typst-py) | 0.15.0 [VERIFIED: `uv run python -c "import typst; print(typst.__version__)"`] | Compiles emitted `.typ` → PDF; used directly by the GATE-01 fixture and by `TypstPDFBuilder.finish()` | Already the project's sole PDF-compile mechanism (`pdf.py`) |
| `pypdf` | 6.14.2 [VERIFIED: `uv run python -c "import pypdf; print(pypdf.__version__)"`] | Extracts PDF text for the SC#3 content-fidelity assertion | Already used by every render-gate test in `tests/` (e.g. `test_wide_table_render_gate.py`) |

### Alternatives Considered
None — no new packages are needed or appropriate. The milestone invariant is "zero new runtime
dependencies."

**Installation:** None required — no `pyproject.toml`/`uv.lock` change for this phase.

## Package Legitimacy Audit

**Not applicable.** This phase installs zero new packages (milestone invariant, `.planning/STATE.md`
"Milestone invariants (every phase)": *zero new runtime dependencies*). `typst-py` and `pypdf` are
pre-existing dev dependencies already pinned in `pyproject.toml`/`uv.lock` and used across the
existing render-gate test suite.

## Architecture Patterns

### System / Data-Flow Diagram

```
reST source (.rst)
   │  docutils parse (Sphinx)
   ▼
doctree  ──►  nodes.paragraph
                 │
                 ├─ nodes.Text ("Text before math ")
                 │     └─ visit_Text: _add_paragraph_separator() [no-op outside par()/in_paragraph]
                 │                  → _emit_inline_concat_separator() [+ if concat ctx active]
                 │                  → OR list-item newline check
                 │                  → emits text("...")
                 │                  → _mark_inline_concat_content() OR list_item_needs_separator=True
                 │
                 ├─ nodes.math ("E=mc^2")
                 │     └─ visit_math (CURRENT, BUGGY):
                 │            _add_paragraph_separator()  ◄── ONLY this call
                 │            emits mi(`...`) / $...$      ◄── no concat/list-item participation
                 │            raise SkipNode                ◄── separator flags never updated
                 │
                 └─ nodes.Text (" text after.")
                       └─ visit_Text: sees STALE list_item_needs_separator from the
                          PRECEDING Text node (math never touched it) → separator logic
                          is now internally inconsistent, producing the exact glued
                          Typst source shown in "Common Pitfalls" below.

Emitted .typ (buggy, inside a list.item / term / link / field-body / attribution context)
   │
   ▼
typst.compile()  ──►  FATAL: "expected comma" / "expected semicolon or line break"
                       (TypstCompilationError, aborts sphinx-build -b typstpdf)
```

### Recommended Fix Shape (mirrors `visit_literal`, `translator.py:1282-1352`)

```python
# Source: typsphinx/translator.py, visit_literal (existing, PROVEN pattern) — adapt 1:1 for visit_math
def visit_math(self, node: nodes.math) -> None:
    # Add separator if in paragraph and not first node (existing, unchanged — this
    # is the piece that already makes plain top-level paragraphs work correctly).
    self._add_paragraph_separator()

    # Add separator before the math expression, mirroring visit_literal /
    # visit_Text: in a code-mode concat context (def-list term / link body /
    # desc parameter / collapsed-inline field body / attribution), + separate;
    # otherwise, inside a list item, use the shared newline-separator flag.
    if not self._emit_inline_concat_separator():
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

    # ... existing math_content / is_typst_native / use_mitex branch, UNCHANGED ...
    # ... existing label-anchor emission, UNCHANGED ...

    # Mark that content was added, so the next sibling is + / newline separated.
    if not self._mark_inline_concat_content():
        if self.in_list_item:
            self.list_item_needs_separator = True

    raise nodes.SkipNode
```

This is a **minimal, surgical, precedent-matching** change: it does not introduce any new helper,
does not touch the mitex/native branch logic, and reuses the exact same two guard expressions
(`if not self._emit_inline_concat_separator(): ...` / `if not self._mark_inline_concat_content(): ...`)
already present verbatim in `visit_Text` (`translator.py:1060-1080`) and `visit_literal`
(`translator.py:1299-1301`, `:1349-1351`).

### Anti-Patterns to Avoid
- **Don't fix only the mitex branch or only the native branch.** Both branches sit downstream of
  the SAME separator code at the top of `visit_math` — one correct fix point covers SC#2
  automatically. A plan that duplicates the separator logic per-branch is unnecessary and risks the
  two branches drifting.
- **Don't "fix" by inserting a hard-coded `"\n"` or `" "` unconditionally before `mi(...)`.** That
  reproduces the exact double-separator / stray-newline bug class this codebase's concat-context
  machinery was built to prevent (see `_add_paragraph_separator`'s own docstring warning and the
  `_CONCAT_CONTEXTS` precedence-ordered tuple, `translator.py:928-934`) — it would silently break
  the ALREADY-WORKING plain-paragraph case (verified below) by inserting a redundant separator when
  `_add_paragraph_separator()` already handled it, and would emit a wrong (` + `-less or
  double-`\n`) separator inside the five concat contexts.
- **Don't assume the backlog's "math/Text visit ordering" framing.** Node visitation order is
  correct; the defect is `visit_math`'s non-participation in two separator PROTOCOLS that exist
  independently of visit order.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Deciding whether the next inline expression needs `+`, `\n`, or nothing | A new math-specific separator heuristic | The existing `_emit_inline_concat_separator()` / `_mark_inline_concat_content()` pair and `self.list_item_needs_separator` flag (both already shared across 5+ other inline visitors) | Single source of truth (`translator.py:900-999` docstring: "the ONE place that decides which concat context is active"); duplicating this logic in `visit_math` would create a second, divergent copy that future concat-context additions (there are already 5) would not automatically cover |

**Key insight:** This bug class is already "solved" in this codebase for every OTHER inline leaf
node. The fix is not new design — it's applying the existing, tested pattern to the one visitor that
was written before (or independently of) that pattern's introduction and never retrofitted.

## Common Pitfalls

### Pitfall 1: Believing the plain-paragraph case is broken (it is not)
**What goes wrong:** A plan that starts by "fixing" `visit_math`'s `_add_paragraph_separator()` call
for the plain top-level-paragraph case wastes effort on a path that already works, and risks
introducing a regression (double separator) in the one case that was fine.
**Why it happens:** The backlog title and ROADMAP phrasing both say "paragraph... immediately
following text," which reads as "any paragraph," but the actual failure requires a paragraph whose
`par({...})` wrapping is SKIPPED — i.e., a list item's paragraph (`visit_paragraph`'s
`self.in_list_item` branch never sets `self.in_paragraph = True`) — or a doctree position that never
was a `paragraph` at all (definition-list term, link body, desc parameter, collapsed-inline field
body, attribution).
**How to avoid:** Reproduce empirically before touching code (already done in this research —
see Verification Evidence below). Do not add any separator logic gated on `self.in_paragraph`.
**Warning signs:** A regression fixture that only tests a bare top-level `paragraph` with math after
text will pass on BOTH the buggy and fixed translator — it proves nothing (violates the "fail-pre-fix"
GATE-01 bar, SC#4). The fixture MUST target a list item (or one of the four other concat contexts).

### Pitfall 2: `visit_math_block` has the identical defect class, but is arguably out of MATH-01's stated scope
**What goes wrong:** `.. math::` (display math) inside a list item ALSO fails to compile today
(measured below: `expected semicolon or line break`), for the exact same root cause
(`visit_math_block` never checks/sets `list_item_needs_separator`). The backlog title is scoped
specifically to `#mi()` (inline math); MATH-01's SC#2 also names only the inline forms
(`mi(...)`/`$...$`). But SC#5 says "math in list items... stay green," which could be read as
requiring this too.
**Why it happens:** `visit_math_block` is a structurally separate node handler from `visit_math` —
fixing one does not fix the other.
**How to avoid:** Flag this explicitly for the discuss/plan step (see Open Questions below) rather
than silently expanding scope OR silently leaving a known-red case unfixed. This is a genuinely new
finding not previously captured anywhere in `.planning/` — confirmed by grepping
`.planning/todos/pending/` for "math" (no hits).
**Warning signs:** If a plan's SC#5 verification step tests block math inside a list item and it was
never in scope, either the test will unexpectedly fail (scope was implicitly expanded) or the test
will be silently omitted (leaving a known defect undocumented).

### Pitfall 3: Testing `visit_math` in isolation (as the existing 3 math test modules do) cannot catch this bug
**What goes wrong:** `tests/test_math_mitex.py` / `test_math_native.py` / `test_math_fallback.py`
call `translator.visit_math(math_node)` directly on a bare/fresh translator with no surrounding
paragraph, list item, or concat context pushed — so `self.in_list_item` is always `False` and no
concat context is ever active in these tests. They will pass identically before and after this fix
(confirmed: 23/23 pass today) and do not exercise the separator-protocol code path at all.
**Why it happens:** They were written as pure node-conversion unit tests (Task 6.2-6.5), not
context-sensitive emission tests.
**How to avoid:** The GATE-01 regression fixture (a real `sphinx-build -b typstpdf` → `typst.compile()`
run against a `.rst` fixture with a real list item) is REQUIRED — a translator-level unit test alone
cannot prove or disprove this defect.
**Warning signs:** A plan whose only new test is `translator.visit_math(...)`-based will not move
GATE-01's needle.

## Code Examples

### Verified (this session) BUGGY emission — definition-list term, mitex path
```
// Source: reproduced via sphinx-build -b typst against a scratch fixture (this session)
// reST: "Term :math:`E=mc^2`\n   Definition body text."
terms(separator: linebreak(), terms.item(text("Term ")mi(`E=mc^2`), {par({text("Definition body text.")})}))
```
`typst.compile()` on this file raises: `expected comma` [VERIFIED: local `typst.compile()` call,
typst 0.15.0].

### Verified (this session) BUGGY emission — bullet list item, mitex path
```
// Source: reproduced via sphinx-build -b typst against a scratch fixture (this session)
// reST: "- Text before math :math:`E=mc^2` text after."
list({
parbreak()

text("Text before math ")mi(`E=mc^2`)
text(" text after.")
})
```
`typst.compile()` on this file raises: `expected semicolon or line break` [VERIFIED: local
`typst.compile()` call, typst 0.15.0].

### Verified (this session) BUGGY emission — bullet list item, `.. math::` block (Pitfall 2, likely out of stated scope)
```
// reST: "- Text before block math.\n\n  .. math::\n\n     E = mc^2\n\n  Text after block math."
list({
parbreak()

text("Text before block math.")mitex(`E = mc^2`)


parbreak()

text("Text after block math.")
})
```
`typst.compile()` on this file raises: `expected semicolon or line break` [VERIFIED: local
`typst.compile()` call, typst 0.15.0].

### Verified (this session) WORKING emission — plain top-level paragraph, both with and without the backslash-escaped no-space form
```
// reST:
// "With space before math: :math:`E=mc^2` after.
//
// No space where\ :math:`E=mc^2`\ immediately follows."
par({text("With space before math: ")
mi(`E=mc^2`)
text(" after.")})

par({text("No space where")
mi(`E=mc^2`)
text("immediately follows.")})
```
`sphinx-build -b typstpdf` succeeds; extracted PDF text (`pypdf`) reads: `"With space before math:
𝐸 = 𝑚𝑐2 after."` and `"No space where𝐸 = 𝑚𝑐2immediately follows."` — prose and math both present,
adjacent as authored, no dropped words [VERIFIED: local `sphinx-build`/`typst.compile()`/`pypdf`
run, this session].

### Existing proven pattern to copy (`visit_literal`, unchanged by this phase)
```python
# Source: typsphinx/translator.py:1282-1352 (existing code, cited for the fix's shape)
def visit_literal(self, node: nodes.literal) -> None:
    self._add_paragraph_separator()
    if not self._emit_inline_concat_separator():
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")
    # ... content-specific emission ...
    self.add_text(f'raw("{escaped_code}")')
    if not self._mark_inline_concat_content():
        if self.in_list_item:
            self.list_item_needs_separator = True
    raise nodes.SkipNode
```

## State of the Art

| Old Approach (current `visit_math`) | Current/Recommended Approach | When Changed | Impact |
|--------------------------------------|-------------------------------|---------------|--------|
| Only `_add_paragraph_separator()` before emission; no post-emission bookkeeping | Full 3-protocol participation (paragraph / concat-context / list-item), matching `visit_literal` | This phase | Inline math becomes compilable in list items, def-list terms, link bodies, collapsed-inline field bodies, and block-quote attributions — the same 5 contexts every other inline node already supports |

**Deprecated/outdated:** None — no Typst/mitex/Sphinx API changes involved. This is purely an
internal consistency fix.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The reported backlog 999.1 repro was most likely a list item or field-body context (not a bare top-level paragraph), since bare top-level paragraphs are measured to already work | Summary, Pitfall 1 | If the actual original repro differs from all 5 contexts identified here, the fixture built from this research might not match the exact backlog trigger — though the fix is general enough (all 5 contexts share one root cause and one fix point) that any concat-context or list-item repro should be equally valid evidence for SC#1/SC#4 |
| A2 | `visit_math_block` (display math) sharing the identical defect class is OUT of MATH-01's literal scope (backlog title says "before `#mi()`"; SC#2 names only inline forms) | Pitfall 2 | If the milestone owner intends "math in list items" (SC#5) to cover display math too, a plan that fixes only `visit_math` will leave a known-red case (block math in a list item) unaddressed; needs an explicit scope decision (see Open Questions) |

## Open Questions

1. **Should `visit_math_block` (display math / `.. math::`) receive the identical list-item-separator
   fix in this same phase, or be filed as a new, separately-scoped backlog item?**
   - What we know: It has the exact same root cause and is currently broken in exactly the same
     shape (measured this session: `expected semicolon or line break` for `.. math::` inside a
     bullet list item). The fix would be structurally analogous (add
     `if self.in_list_item and self.list_item_needs_separator: self.add_text("\n")` before emission,
     and set the flag after) but is NOT identical code (math_block is a block-level, not
     inline-concat-context, node — it never participates in the 5 concat contexts, only the
     list-item case applies).
   - What's unclear: Whether the milestone owner's "minimal hotfix scope" intent (STATE.md: "the
     owner wants 999.1 fixed and released promptly") extends to a closely-related but distinct bug
     discovered during research, or whether that violates the "nothing else enters this milestone"
     invariant.
   - Recommendation: Surface this explicitly to the user/planner. Given the shared root cause, tiny
     additional diff, and that SC#5 already names "math in list items" as protected surface, leaning
     toward including it — but this is a scope decision, not a research one, and should be confirmed
     (e.g., via `/gsd-discuss-phase` or explicit owner sign-off) before the plan commits to one or
     the other. If descoped, file a new backlog item so it is not silently lost.

2. **Which of the 5 concat contexts (term / link / desc_parameter / field_body / attribution) plus
   list items should the GATE-01 regression fixture cover?**
   - What we know: List items are almost certainly the most common real-world trigger (any bullet
     point mixing prose and math). Collapsed-inline field bodies are the second most likely
     (`:field: prose :math:`x` more` — very common in Sphinx docstring-style field lists; this
     project already has `test_confval_field_body_render_gate.py` for the analogous `strong()` case).
     Definition-list terms were reproduced directly this session.
   - What's unclear: Whether the plan should ship one fixture (list item, matching SC#1's "paragraph"
     framing most directly) or multiple (covering all 5 concat contexts + list items, for full
     regression coverage of the actual code change).
   - Recommendation: At minimum, one list-item-based fixture (satisfies SC#1/SC#2/SC#3/SC#4 directly
     against the literal "999.1 shape"). Since the SAME code change touches the shared
     `_emit_inline_concat_separator`/`_mark_inline_concat_content` call sites, a second fixture
     covering one concat context (term or field_body) would meaningfully raise confidence for a
     one-line-diff-sized fix, without materially expanding the phase.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst` (typst-py) | GATE-01 fixture, existing `TypstPDFBuilder.finish()` | ✓ | 0.15.0 | — |
| `pypdf` | GATE-01 fixture text-extraction assertions (SC#3) | ✓ | 6.14.2 | — |
| `sphinx-build` (`sys.executable -m sphinx`) | All fixture builds | ✓ | Sphinx 9.1.0 (via `uv run`) | Always invoke as `sys.executable -m sphinx`, never bare `sphinx-build` / `uv run sphinx-build` — the compiled-binary shim fails under the NixOS sandbox (project memory: "NixOS sandbox test env") |

**Missing dependencies:** None.

**NixOS sandbox caveat (project memory, confirmed applicable):** `uv run <compiled-binary>` (e.g.
`uv run sphinx-build`) fails in this environment; this session's reproduction used
`uv run sphinx-build` successfully via `uv --project <repo> run sphinx-build ...` from OUTSIDE the
scratch working directory (module invocation resolves correctly through the project's own
console-script entry point in this instance) — but the existing render-gate test convention (see
`tests/test_wide_table_render_gate.py:81-104`, `_run_sphinx_build_typstpdf`) deliberately invokes
`[sys.executable, "-m", "sphinx", "-b", ...]` as a subprocess specifically to sidestep this hazard.
**The new GATE-01 fixture MUST follow this same `sys.executable -m sphinx` subprocess convention**,
not a bare `sphinx-build` invocation. Per project memory, ~45 integration tests fail purely
environmentally on this NixOS sandbox for reasons unrelated to code correctness — a plan's
verification step should run the SPECIFIC new/modified test files plus the 3 existing math modules
plus the fast (`-m "not slow"`) suite, and treat any pre-existing unrelated NixOS-only failures as
known noise rather than blocking, distinguishing them from real regressions.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 [VERIFIED: `uv run pytest --version` output header this session] |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["tests"]`) |
| Quick run command | `uv run pytest tests/test_math_mitex.py tests/test_math_native.py tests/test_math_fallback.py -q` (0.04s, 23/23 passing baseline, measured this session) |
| Full suite command | `uv run pytest` (matches CLAUDE.md; excludes nothing by default — `slow`-marked tests run unless `-m "not slow"` is passed) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MATH-01 (SC#1, SC#2, SC#3, SC#4) | Inline math immediately after text, in a context where `_add_paragraph_separator()` is a no-op (list item at minimum), compiles on both mitex and native paths and renders prose+math adjacent with no drop | real-compile GATE-01 fixture | `uv run pytest tests/test_inline_math_after_text_render_gate.py -q` (new file; exact name TBD by planner, follow `test_<topic>_render_gate.py` convention seen across 20+ existing files) | ❌ Wave 0 — must be created, and its RED-before-fix run captured per SC#4 |
| MATH-01 (SC#5, non-regression) | Existing math node-conversion unit tests, math in tables/captions, full pytest suite | unit + full suite | `uv run pytest tests/test_math_mitex.py tests/test_math_native.py tests/test_math_fallback.py -q` then `uv run pytest -q` | ✅ (all 3 modules exist, 23/23 passing baseline measured this session) |
| MATH-01 (SC#5, full-corpus gate) | `-b typstpdf` regression gate over Sphinx's own `doc/` tree stays fatal-free | slow / integration | `uv run pytest tests/test_corpus_gate.py -q -m slow` (network-dependent; skips gracefully if corpus unavailable, per its own docstring D-05) | ✅ (existing, `test_corpus_gate.py`) |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_math_mitex.py tests/test_math_native.py tests/test_math_fallback.py tests/test_inline_math_after_text_render_gate.py -q`
- **Per wave merge:** `uv run pytest` (full suite, matches CLAUDE.md)
- **Phase gate:** Full suite green before `/gsd-verify-work`, plus the RED-then-GREEN GATE-01 evidence captured per SC#4, plus (time permitting / if in scope) a live re-run of the full-corpus `-b typstpdf` gate per SC#5's explicit mention of it.

### Wave 0 Gaps
- [ ] `tests/test_inline_math_after_text_render_gate.py` (exact name TBD by planner) — covers MATH-01
  SC#1-SC#4, built on a `.rst` fixture with a bullet list item mixing prose and `:math:` inline
  content (and optionally a second concat-context fixture per Open Question 2). Follow the
  `_run_sphinx_build_typstpdf` subprocess-invocation idiom from `tests/test_wide_table_render_gate.py`
  (never bare `sphinx-build`, per the NixOS caveat above) and the `pypdf` text-extraction /
  collision-absence assertion idiom from the same file for SC#3.
- [ ] The fail-pre-fix (RED) run itself is not a file gap, but a **required evidence artifact**
  (SC#4): run the new fixture against the unmodified translator, capture the verbatim
  `TypstCompilationError` (or the fixture's own assertion failure showing the compile error), THEN
  apply the fix and re-run GREEN.

*No framework-install gap: pytest, typst-py, and pypdf are all already installed dev dependencies.*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | No auth surface in this project or this phase |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | Marginal | Inline math content (`node.astext()`) is emitted into a Typst backtick-raw-string (`mi(`...`)`) or a `$...$` math-mode span. This phase does not change escaping/validation of that content — it only changes WHERE a separator character is inserted around the already-existing emission. No new user-controlled string reaches an unescaped context as a result of this fix. |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Untrusted reST/LaTeX math content injecting Typst code-mode syntax (e.g. a crafted `:math:` body breaking out of the backtick-raw-string or `$...$` span) | Tampering | Out of scope for this phase — pre-existing behavior, unchanged by this fix. `mi(`...`)` uses Typst's own raw-string/backtick literal (mitex parses the LaTeX content itself; a backtick inside the math source is the one edge case, already pre-existing and not touched here). This phase's diff is strictly the separator characters surrounding the call, not the call's argument construction. |

## Sources

### Primary (HIGH confidence — direct empirical measurement, this session)
- Local reproduction via `sphinx-build -b typst` / `sphinx-build -b typstpdf` / `typst.compile()`
  against 5 scratch `.rst` fixtures (plain paragraph with/without backslash-escaped no-space math;
  definition-list term; bullet list item with inline math; bullet list item with block math) —
  verbatim Typst compile errors captured for each failing case, verbatim `pypdf`-extracted PDF text
  captured for the working case.
- `typsphinx/translator.py` — direct reading of `visit_math` (3936-3992), `visit_math_block`
  (3994-4053), `visit_Text` (1018-1082), `visit_literal` (1282-1354), `visit_paragraph` (763-800),
  `_add_paragraph_separator` (319-330), the concat-context helper block (900-999,
  `_CONCAT_CONTEXTS` at 928-934), `visit_term`/`depart_term` (1992-2033), `visit_field_body`
  (4944-4973), `visit_reference` (link-body concat activation, 3696-3786), `visit_attribution`
  (2839-2879).
- Existing test suite: `tests/test_math_mitex.py`, `tests/test_math_native.py`,
  `tests/test_math_fallback.py` (read + executed, 23/23 passing baseline), `tests/test_corpus_gate.py`
  (read, for the slow full-corpus gate's invocation convention), `tests/test_wide_table_render_gate.py`
  (read, as the GATE-01 fixture-authoring template).
- `docutils.nodes.math.__mro__` — confirmed `nodes.math` is a subclass of `nodes.Inline`, executed
  this session, which is why `visit_field_body`'s `all_inline` check (already-existing code) also
  activates its concat context for inline math field bodies.

### Secondary (MEDIUM confidence)
- None used — no external documentation lookups were needed for this phase; the defect and fix are
  entirely internal to this codebase and were resolved by direct measurement.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Root cause: HIGH — reproduced with verbatim compile errors in 3 distinct contexts (term, list
  item x2)
- Fix shape: HIGH — directly mirrors an existing, tested, in-codebase pattern (`visit_literal`) used
  identically by 4+ other inline visitors
- Scope boundary (visit_math_block / which contexts to fixture): MEDIUM — technically sound but
  requires an explicit scope decision from the user/planner (see Open Questions); not purely a
  research question

**Research date:** 2026-07-28
**Valid until:** No expiry driver — this is a static internal-code finding, not a moving external
dependency; re-verify only if `translator.py`'s separator machinery is refactored before this phase
executes.
