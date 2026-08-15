# Phase 48: Compile-Time Cross-Reference Guard - Research

**Researched:** 2026-08-12
**Domain:** Typst compile-time label existence guard (`context`/`query`) replacing a build-time Python
boolean; Sphinx `pending_xref` resolution pipeline; Typst code/markup mode grammar for a streaming
open/close emission contract.
**Confidence:** HIGH — every load-bearing claim in this document was verified this session either by
reading the cited source lines (translator.py, builder.py, Sphinx's own `post_transforms/__init__.py`)
or by a real `typst.compile()` / `sphinx-build` invocation. No claim in the Standard Stack, Architecture
Patterns, or Common Pitfalls sections rests on training-data memory alone.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** The build-time degrade warning is deleted outright, with no diagnostic replacement.
- **D-02:** A degraded reference renders as exactly the same visible text as the linked form, with no
  visual marking.
- **D-03:** Every gate whose assertion flips direction has its new expected value written down in a
  standalone phase artifact, derived from the fixture's `conf.py` and `.rst` alone, **before** the new
  emitter is run.
- **D-04:** `visit_pending_xref` is brought under the guard, not merely rewired — closes open question
  #1: it is a fourth independent degradation site. If a RED cannot be constructed, follow the Phase 40.1
  D-01 precedent: enumerate every plausible source shape and record why the topology is unconstructible.
- **D-05:** Citation back-references are guarded, and the reason SC#4 does not exempt them is recorded
  explicitly — their presence depends on `visit_reference` having actually run on the citing node, which
  is not guaranteed for same-document anchors in general (the captioned-code-block route).
- **D-06:** Same-document anchors outside the citation back-reference case keep their unguarded form,
  asserted explicitly, per SC#4.
- **D-07:** The shared guard helper returns an **open string and a close string**, and the reference body
  keeps streaming between them exactly as it does today.
- **D-08:** The exact Typst syntax of D-07's shape is treated as **unmeasured** and must be verified
  against a real `typst.compile()` during research before any plan depends on it.
- **D-09:** Removing `degrade_xref_to_text` makes `opens_wrapper` unconditional, and the resulting
  citation back-reference marker appearing where none appeared before is accepted as an intended
  behaviour fix.
- **D-10:** The four unit tests bound directly to the deleted function are removed with it; the three
  end-to-end tests in the same file survive unchanged.
- **D-11:** The compile-time cost thresholds are written down **before** the measurement is taken, in
  three tiers (<+20% record only; +20%-100% record as finding + file improvement todo; >+100% escalate
  to a blocker attached to Phase 49's scope).

### Claude's Discretion

- Where the shared helper lives and what it is named, as long as D-07's open/close contract holds and
  all three emission sites consume it.
- The exact identifier used for the `let`-bound body in D-07's emitted Typst (the `__b` in the sketch is
  illustrative, not fixed).
- Whether the pre-fix RED for XREF-03 is expressed as an `xfail(strict=True)` recording (the Phase 47
  gap-closure convention) or as a separately-committed evidence transcript.
- The exact wording of any message text that changes.
- Whether the four deleted unit tests' file is removed entirely or kept holding only its three surviving
  end-to-end tests.

### Deferred Ideas (OUT OF SCOPE)

- **Replacing `query(<L>)` with a `state("inc", ())` lookup** — only becomes possible once Phase 49
  introduces the state-published include set. Filed as the named remediation path for D-11's top tier,
  not as work for this phase.
- Composition semantics, the per-master include graph, `state`-guarded includes, `:numref:` divergence
  (Phase 49); the PR #131 image defects (Phase 50); documenting the two-layer output shape (Phase 51).

</user_constraints>

## Summary

This phase replaces one build-time Python boolean (`degrade_xref_to_text`, derived from
`builder.master_included_docnames`) with a Typst **compile-time** guard evaluated per compiled wrapper,
using `context { if query(<label>).len() > 0 { link(<label>, body) } else { body } }`. The mechanism
was already measured working in its simplest form (a literal string body) before this phase; this
research closes the two things that measurement did NOT cover and that D-08 flagged as load-bearing
risk: (1) whether the specific **`let`-bound streaming open/close split** D-07 requires actually
compiles, given the translator's `visit_*`/`depart_*` streaming pattern, and (2) whether the guard still
produces a real, `pypdf`-readable PDF link annotation in the positive case and a clean silent degrade
(zero annotations, zero errors) in the negative case. Both are now empirically confirmed, with one
correction to the sketch in `48-CONTEXT.md`: **the `if <condition>` and its opening `{` must not be
separated by a bare newline** — Typst's parser does not look across a newline for a deferred block, and
raises `expected block` if you split them the way the CONTEXT sketch's illustrative formatting does.
Every other part of the sketch (the `;` separator, the `let`-bound identifier, nesting arbitrary markup
inside the bound body, using the guard as a plain value expression in a non-streaming site) compiles and
behaves exactly as measured.

Separately, this research closes open question #1 (`translator.py:4291`'s nature, D-04) and
independently re-derives D-05's citation-caption route by direct construction: a real `sphinx-build`
against a `[Cite]_` inside a `code-block` `:caption:` reproduces the exact fatal PROJECT.md predicts
(`label <index:id1> does not exist in the document`), confirming D-05's claim is not merely plausible
but currently reachable. D-04's `pending_xref` site, by contrast, could not be reached through any of
the four plausible unresolved-reference shapes tested against a real Sphinx 9.1.0 build — Sphinx's
`ReferencesResolver` post-transform unconditionally replaces every `pending_xref` node before the writer
ever runs, confirming the Phase 40.1 D-01 precedent applies here too.

**Primary recommendation:** Implement a single shared guard helper returning `(open_str, close_str)`
per D-07's contract, with the close string's `if`/`{` kept on one unbroken statement (never split across
a bare newline the way the CONTEXT sketch illustrates it — see Common Pitfalls). Route all three sites
(`visit_reference`'s cross-document branch, `visit_citation`'s backref loop, `visit_pending_xref`/
`depart_pending_xref`) through it. Treat D-04's `translator.py:4291` site as unconstructible-RED by the
Phase 40.1 precedent (still bring it under the guard defensively per D-04's own instruction — "brought
under the guard, not merely rewired" — but do not spend planning effort inventing a RED fixture for it).

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-------------------|
| XREF-03 | A cross-document reference whose target label is absent from the compiling master degrades to plain text at compile time instead of aborting the compile | The corrected D-08 guard shape (Architecture Patterns Pattern 1) is verified end-to-end with `pypdf` readback: positive case yields a real `/Link` annotation, negative case yields zero annotations and a successful compile. Common Pitfall 1 documents the one syntax correction needed relative to the CONTEXT.md sketch |
| XREF-04 | Every label-reference emission site routes through one shared guard, and `master_included_docnames` is removed | All three sites' current code was read this session (`visit_reference` cross-document branch, `visit_citation` backref loop, `visit_pending_xref`/`depart_pending_xref`) and the guard's usage as both a streaming open/close pair (Pattern 1) and a bare value expression (Pattern 1's second example, Pitfall 3) is verified compiling. D-04's open question #1 is closed (Pitfall 4 — unconstructible RED, confirmed empirically against a real Sphinx 9.1.0 build across four unresolved-reference shapes). D-05's citation-caption route is confirmed as a currently-reachable real fatal (Pitfall 5, reproduced with a verbatim `TypstError` transcript) |

</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Cross-document label-existence decision | Typst compile pass (`context`/`query`) | — | The information ("is this label present in THIS compiled wrapper's document graph") genuinely does not exist until Typst has resolved which documents are `#include()`d into this specific compile — a Python-side union across all masters cannot know which master is asking (this phase's whole premise) |
| Reference-body emission (streaming markup) | `TypstTranslator` (translator.py) | — | `visit_*`/`depart_*` node handlers own converting docutils nodes to Typst source text; the guard is a change to WHAT text they emit, not a new tier |
| Shared guard-string derivation | `TypstTranslator` (one new helper method) | — | Per D-07, one method returns `(open, close)`; all three emission sites are translator methods, so the helper lives in the same module/class, not in `builder.py` |
| Build-time include-set bookkeeping (deleted) | `TypstBuilder` (builder.py) | — | `master_included_docnames`/`_compute_master_included_docnames()` are pure Python builder state with no consumer left after this phase — tier ownership moves entirely to Typst compile time |
| Test/gate verification of degrade behaviour | pytest + real `typst.compile()` via `typst-py` | Sphinx subprocess build | Per the project's standing GATE-01 bar, correctness is proven by compiling and reading back a real PDF (`pypdf`), not by asserting on emitted `.typ` string content alone |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `typst` (typst-py) | `0.15.0` [VERIFIED: `importlib.metadata.version("typst")`, this session] | Compiles `.typ` -> PDF; `context`/`query` are its own stdlib primitives, no new dependency | Already the project's sole PDF-compile dependency (`pyproject.toml: "typst>=0.15.0,<0.16"` [VERIFIED: pyproject.toml, this session]); zero new runtime dependencies is a standing invariant (binding constraint #7) |
| `sphinx` | `9.1.0` [VERIFIED: `sphinx.__version__`, this session] | Doctree resolution; `ReferencesResolver` post-transform is the mechanism D-04's empirical question turns on | Already the project's core dependency |

### Supporting
No new libraries. This phase adds zero runtime dependencies (binding constraint #7 — no new `@preview`
package, no new `typst_*` config value) and zero new dev/test dependencies (`pypdf` is already used by
`tests/test_pdf_render_gate.py` for the identical link-annotation-readback pattern this phase's SC#1
needs).

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `context`/`query` compile-time guard | Keep the build-time Python boolean, re-scoped per master | Measured and rejected in the milestone's own PROJECT.md (not this phase's research to re-derive): cannot serve the Phase 49 diamond-include case where the same content file needs a different degrade answer per master from one write of the file |
| `query(<label>).len() > 0` | `state("inc", ()).get()` lookup against Phase 49's include-set state | Not available yet — Phase 49 introduces the state-publishing wrapper. D-11 names this as the top-tier cost-regression remediation, explicitly deferred (see Deferred Ideas in 48-CONTEXT.md) |

**Installation:** No new packages. No `npm install`/`pip install` step is part of this phase's changes.

**Version verification:** `typst-py` and `sphinx` versions confirmed live this session via
`importlib.metadata.version("typst")` and `sphinx.__version__` against the project's own `.venv` — both
match the versions already recorded in `PROJECT.md`/`pyproject.toml`. No drift since the 2026-08-11
measurement.

## Package Legitimacy Audit

Not applicable — this phase adds no new packages of any kind (no new PyPI dependency, no new `@preview`
package). `typst`/`sphinx` are pre-existing project dependencies, already audited in prior milestones.

## Architecture Patterns

### System Architecture Diagram

```
docutils doctree (per docname)
        |
        v
TypstTranslator.visit_reference / visit_citation / visit_pending_xref
        |
        |  BEFORE this phase: consult builder.master_included_docnames
        |  (Python boolean, computed once at write() time, unioned
        |  across ALL masters -- cannot know which master is asking)
        |
        |  AFTER this phase: emit an UNCONDITIONAL guarded expression;
        |  defer the existence decision to Typst itself
        v
  {prefix}context { let __b = [ ...streamed child markup... ]
    ; if query(<label>).len() > 0 { link(<label>, __b) } else { __b } }
        |
        v
  .typ content file (docname-named, written once, referenced by N wrappers)
        |
        v
  per-wrapper #include() (Phase 47's two-layer split; Phase 49's per-master graph)
        |
        v
  typst.compile() -- Typst's OWN multi-pass layout resolves query(<label>)
  against WHATEVER this specific wrapper actually included
        |
        +-- label present in this compile  --> real link() annotation
        |
        +-- label absent from this compile --> plain body, no annotation,
                                                 compile still succeeds
```

A reader can trace SC#1's primary use case end to end: a reference's body is written to disk exactly
ONCE (in the docname-named content file), and the SAME bytes produce a link in one master's PDF and
plain text in another's, because the branch decision moves from "baked into the file at write time" to
"resolved by Typst separately for each wrapper that includes the file."

### Recommended Project Structure

No new files/directories. This phase's changes are localized to two existing modules:

```
typsphinx/
├── translator.py   # new shared guard helper; 3 call sites updated; degrade_xref_to_text field removed
└── builder.py       # _compute_master_included_docnames() + master_included_docnames attribute deleted
```

### Pattern 1: Shared open/close guard helper (D-07's contract)

**What:** One translator method that, given a label string, returns a `(open_str, close_str)` pair. The
caller emits `open_str`, then streams the reference's body (whatever child markup the translator would
have emitted anyway), then emits `close_str`.

**When to use:** At all three label-reference emission sites — `visit_reference`'s cross-document
branch, `visit_citation`'s backref-loop label expression, `visit_pending_xref`/`depart_pending_xref`.

**Example — the corrected D-08 shape** (verified this session, typst-py 0.15.0; the CONTEXT.md sketch's
line break between `if <cond>` and `{` does NOT compile — see Common Pitfalls Pitfall 1):

```typst
// Source: verified this session via typst.compile() against typst-py 0.15.0
// open string (emitted by visit_*):
#context { let __b = [
// ... streamed child markup goes here, unchanged from today's emission ...
]; if query(<the-label>).len() > 0 { link(<the-label>, __b) } else { __b } }
// ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ close string
// (depart_* emits everything from `];` onward)
```

Verified this session:
- Real transcript, positive case (target present): `typst.compile()` succeeds, `pypdf` reports **1**
  `/Link` annotation with `/Dest` = the label.
- Real transcript, negative case (target absent anywhere in the document): `typst.compile()` succeeds,
  `pypdf` reports **0** annotations on the page — the body renders as plain content, no error.
- Verified with **nested markup inside the `let`-bound body**: emphasis, a nested external `link()`,
  a `footnote[...]`, and `raw("code")` all compile cleanly inside `[...]` between the open and close
  strings, matching D-07's "arbitrary child markup streams unchanged" requirement.
- Verified the guard used as a **bare value expression** (not streamed, computed once) — the shape
  `visit_citation`'s backref loop needs, e.g. `text("[") + context { if query(<L>).len() > 0
  { link(<L>, __b) } else { __b } } + text("]")` used directly as a `grid(...)` function-call
  argument — compiles with no outer parentheses required.

### Pattern 2: Mode-transition prefix (`{prefix}context`)

**What:** `visit_reference` already computes `prefix = "#" if self._in_markup_mode else ""` before
emitting `link(...)`. The guard's open string must use the SAME prefix rule, since `context` is a
code-mode keyword exactly like `link`.

**When to use:** Any of the three sites where the surrounding mode is ambiguous (`visit_reference`,
which switches). `visit_pending_xref` currently hardcodes `#link(<label>)[` with no `prefix` variable at
all — verify at implementation time whether that hardcoding is itself already a latent bug (it assumes
markup mode unconditionally) or whether `visit_pending_xref` is only ever reached from markup-mode
contexts in practice; this phase's D-04 finding (see Common Pitfalls Pitfall 4) suggests this code path
is unreachable in normal builds, which may make the question moot.

**Verified this session:** `context` used WITHOUT a `#` prefix inside an already-code-mode block
(`#{ ... }`, or as a bare argument inside `#grid(...)`) compiles correctly — confirming the existing
`prefix` computation pattern generalizes to the guard with no new mode-detection logic needed.

### Anti-Patterns to Avoid

- **Splitting `if <condition>` from its opening `{` across a bare newline:** Typst's parser does not
  defer looking for the block across a newline boundary; this is a hard parse error (`expected block`),
  not a style preference. See Common Pitfalls Pitfall 1 for the full transcript.
- **Interpolating the body into both the `if` and `else` branches instead of `let`-binding it once:**
  D-07 explicitly rejects this (doubles the body on disk, risks duplicate labels/footnotes if the body
  itself contains a label-bearing element). The `let`-bound single-write form is the only one this
  research validated end to end.
- **A boolean-only guard helper** (Phase 40.1 D-06 precedent, cited in D-07): returning `bool` and
  leaving each site to build its own `context`/`query`/`link` expression would leave the Typst-syntax
  derivation itself un-unified even after this phase, reproducing the drift class Phase 40.1 closed for
  the anchor-eligibility judgement. Return the strings themselves.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Deciding whether a cross-document link target exists | A second Python-side include-graph traversal scoped "per master" | Typst's own `context`/`query` against whatever `#include()`s are actually active in this compile | Measured impossible to serve correctly from Python for the diamond-include case (PROJECT.md, not re-derived here) — the information doesn't exist until Typst itself has resolved the include graph for THIS wrapper |
| Label uniqueness across documents | A second label-derivation helper for guarded sites | `_namespace_label(docname, raw_id)` (`translator.py:4579`) [VERIFIED: translator.py:4579-4599, this session] | Already the project's single source of truth (D-13); a guarded site computing its own namespacing would risk byte-mismatching the anchor the target document actually emits |
| Detecting whether a reference resolves cross-document | A parallel refuri parser | `_resolve_xref_docname(refuri)` (survives untouched per CONTEXT.md) | Still a correct BUILD-TIME question ("what docname/anchor does this refuri encode") — only the SAFETY question (does that anchor exist in this compile) moves to compile time |

**Key insight:** This phase is explicitly about NOT hand-rolling a second Python-side answer to a
question Typst can now answer correctly and per-compile — the entire phase goal is deleting the
hand-rolled mechanism (`master_included_docnames`), not adding a new one.

## Common Pitfalls

### Pitfall 1: `if <condition>` split from its block across a newline is a hard parse error

**What goes wrong:** `TypstError: expected block`.

**Why it happens:** Verified this session by direct minimization. Typst's parser requires the `{` that
opens an `if`'s body to appear on the same unbroken statement as the `if <condition>` — a newline
between them is NOT treated as insignificant whitespace the way it is inside, e.g., a plain
`let x = 5\nif x > 0 { ... }` two-statement sequence (which DOES work, verified). The failure is
specific to splitting a single `if`/`else` STATEMENT's condition from its own block:

```typst
// FAILS -- TypstError: expected block
if query(<L>).len() > 0
  { link(<L>, __b) } else { __b }

// WORKS -- condition and its `{` on one unbroken line
if query(<L>).len() > 0 { link(<L>, __b) } else { __b }
```

This directly contradicts the illustrative line-wrapping in `48-CONTEXT.md`'s D-07/D-08 sketch
(`if query(<onlyx:onlyx-label>).len() > 0\n    { link(...) } else { __b } }`), which was explicitly
flagged there as "a sketch to verify, not measured fact." **The plan must NOT reproduce that exact line
break in the generated `.typ` output** — the translator's close-string literal must keep `if
query(<L>).len() > 0 {` unbroken, even though the surrounding `.typ` file can still have newlines
elsewhere (verified: a `;` separator between the `let` and the `if`, or a bare newline there instead,
both work fine, AS LONG AS the `if`'s own condition and block stay together).

**How to avoid:** When constructing the close-string literal in Python, do not insert `\n` between
`query(<L>).len() > 0` and its `{`. A single-line close string (or one broken only after `{link(...)}`
or after `else`) is safe — every variant tested where the break fell BEFORE the first `{` failed.

**Warning signs:** `TypstError: expected block` with no other context — this is the signature error for
this exact mistake; it will surface at `typst.compile()` time, not at Python string-construction time,
so a plan that generates the guard string via multi-line Python triple-quoted literals must audit the
exact bytes it produces.

### Pitfall 2: An invalid `{...}` code-block-as-content-cell test artifact looks identical to a real guard failure

**What goes wrong:** During this session's own verification, wrapping a citation-style grid cell's body
argument in `{Body text.}` (bare curly braces around prose) produced `TypstError: expected semicolon or
line break` — which LOOKS like a guard-expression problem (it appeared only when combined with
`context`/`query` in the same call) but was actually an unrelated, pre-existing Typst syntax error: `{...}`
is a CODE block, not a content block, and `Body text.` is not valid Typst code inside one.

**Why it happens:** The real translator's `visit_citation`/`depart_citation` DOES emit a bare `{` ...
`}` for the body cell (`self.add_text("{")`, matching content walked via the normal visitor chain, which
emits markup-mode constructs like `#raw(...)`/`par({...})` INSIDE that code block) — so a naive test
literal using plain prose inside `{}` is not representative and will falsely implicate the guard.

**How to avoid:** When constructing isolated `.typ` test fixtures for the guard (as opposed to running
the real translator), use `[...]` (a content block) for any body argument standing in for
translator-emitted markup, never bare prose inside `{...}`.

**Warning signs:** `expected semicolon or line break` appearing ONLY when the guard expression is
combined with a specific surrounding call shape, but not when the guard is tested in isolation — check
whether the surrounding shape itself (not the guard) is malformed Typst before concluding the guard is
at fault.

### Pitfall 3: `visit_citation`'s backref loop does not stream — the guard is a value expression there, not an open/close pair around a live child walk

**What goes wrong:** Assuming all three D-07 sites consume the guard identically (open string, then
walk children, then close string) would be wrong for the citation site. `visit_citation`'s
`label_body`/`label_expr` construction (translator.py:3272-3284) already fully computes
`label_content`/`backref_targets` as Python strings BEFORE any `add_text()` call — there is no live
child-streaming happening at the point the guard applies. D-07's contract still works here (open + body
+ close, concatenated as one Python string, rather than interleaved with real `walkabout()` calls) — but
a plan or executor expecting literal `visit_*`/`depart_*` symmetry at this site will be confused.

**How to avoid:** Treat D-07's helper as returning strings usable EITHER by streaming (the two
`visit_reference`/`visit_pending_xref` sites) OR by direct Python string concatenation around an
already-fully-computed body (the `visit_citation` site) — verified both usages compile.

**Warning signs:** Trying to make `visit_citation` open/close symmetric with `visit_reference` when its
existing code structure (buffer-swap idiom, `_find_citing_reference` loop) has no natural "depart" point
for a citing site's own guard — it doesn't need one; the guard wraps the whole computed expression at
once.

### Pitfall 4: `pending_xref` (D-04's site) is very likely unreachable from any real Sphinx build

**What goes wrong:** Assuming a RED fixture can be constructed for `translator.py:4262-4303` the same
way it can for `visit_reference`'s degrade branch.

**Why it happens:** Verified this session by reading Sphinx 9.1.0's `ReferencesResolver`
(`sphinx/transforms/post_transforms/__init__.py:62-93`) — a `SphinxPostTransform` with EMPTY
`builders`/`formats` class tuples, meaning `is_supported()` returns `True` unconditionally for every
builder including `typst`/`typstpdf`. Its `run()` method iterates every `pending_xref` node in the
document and calls `node.replace_self(new_nodes)` UNCONDITIONALLY — `new_nodes` falls back to the
node's own `contnode` (its first child, deep-copied) even when resolution fails completely. This means
**no `pending_xref` node can survive to reach the writer** in a normal build.

Confirmed empirically this session: a real `sphinx-build -b typst` against a fixture containing an
unresolvable `:ref:`, an unresolvable `:doc:`, an unresolvable `:any:`, and an unknown custom role all
produced plain-text or `raw()`-wrapped fallback output in the emitted `.typ` — with the corresponding
Sphinx WARNING for each (`undefined label`, `unknown document`, `'any' 参照先が見つかりません`) — and
NONE of them produced the `visit_pending_xref` fallback's distinctive `#link(<label>)[...]` pattern. The
unknown-role case instead surfaced as docutils' own `problematic` node (`WARNING: unknown node type:
<problematic ...>`), an entirely different code path, not `pending_xref` at all.

**How to avoid:** Follow D-04's own instruction and the Phase 40.1 D-01 precedent: record this as an
UNCONSTRUCTIBLE RED, with the enumerated source shapes and why each resolves before the writer, rather
than spending planning/execution time hunting for a fixture that (on this evidence) cannot exist through
the normal pipeline. Still bring the site under the guard defensively (D-04 requires this regardless of
reachability — "brought under the guard, not merely rewired"), since it is dead code only through the
NORMAL pipeline; a future Sphinx version or an unusual extension interaction is not ruled out by this
session's four-shape sample.

**Warning signs:** None expected at runtime — this pitfall is about not WASTING planning effort trying
to construct an impossible RED, not about a runtime hazard.

### Pitfall 5: D-05's citation-caption route is not merely plausible — it is a currently reachable real fatal, reproduced this session

**What goes wrong:** A `[Cite]_` reference inside a `code-block`'s `:caption:` option renders as plain
`[Smith2020]` text in the caption (because `visit_caption` raises `SkipNode` when
`in_captioned_code_block`, `translator.py:2670-2671`, before `visit_reference` ever runs on the citing
node) — but the citation DEFINITION's back-reference loop (`_find_citing_reference`,
`translator.py:3006`, scanning `self.document.findall(nodes.reference)`) still FINDS that citing node in
the doctree (SkipNode only stops the WALKER, it does not remove the node), judges it `eligible` via
`_reference_anchor_decision`, and emits `link(<label>, ...)` targeting an anchor that was never attached
anywhere.

**Verified this session, real transcript:** A minimal Sphinx project with exactly this shape
(`code-block` `:caption:` containing `[Smith2020]_`, defined by `.. [Smith2020] Smith et al. 2020.`)
built cleanly through `-b typst` with `build succeeded` and no warnings — the defect is entirely
invisible until Typst compiles the output — and `typst.compile()` on the resulting `.typ` failed with:

```
TypstError: label `<index:id1>` does not exist in the document
```

— the exact error shape PROJECT.md predicts for this defect class, with the specific label ID differing
only because docutils assigns `id1`/`id2` etc. per-document rather than the semantic name.

**Why it happens:** Two independent traversal mechanisms disagree about whether a node is "in" the
document: the WALKER (`walkabout`, which `SkipNode` interrupts) and a raw `findall()` scan (which does
not check reachability from the root via the walker's traversal rules, only structural presence in the
tree).

**How to avoid:** This is exactly the case D-05 says needs guarding despite SC#4's same-document
exemption — because the citation back-reference's OWN presence in the compiled output is NOT
guaranteed the way an ordinary same-document anchor's is (content files are included wholesale, but a
`SkipNode` inside `visit_caption` prunes this specific anchor's emission even though the file IS
included). Route this site through the shared guard per D-05.

**Warning signs:** Any future defect where one traversal mechanism (`document.findall`) disagrees with
another (the live `walkabout` chain) about node reachability is worth auditing the same way — this is
the second occurrence of the pattern (the first was WR-01's `only`-tag-pruned citing site, Phase 40.1).

## Code Examples

### Full realistic guard round-trip, positive and negative, with nested markup (verified this session)

```typst
// Source: verified via typst.compile() this session, typst-py 0.15.0.
// Positive case (target section exists in this compile):
= Doc

Some text before #context { let __b = [text with _emphasis_ and #link("https://example.com")[a link] and a #footnote[note body] and #raw("code")]; if query(<present-label>).len() > 0 { link(<present-label>, __b) } else { __b } } and text after.

= Target <present-label>
Target section.
```

Result: compiles successfully; `pypdf` confirms a real `/Link` annotation with `/Dest` = `present-label`
when the `= Target <present-label>` heading is present, and confirms zero annotations for the guarded
span when that heading (and therefore the label) is removed from the same document — compile still
succeeds in both cases.

### Guard as a value expression (for the non-streaming citation site)

```typst
// Source: verified via typst.compile() this session.
#grid(
  columns: (auto, 1fr),
  text("[") + context { if query(<cite-target>).len() > 0 { link(<cite-target>, [1]) } else { [1] } } + text("]"), [Body text.],
)
```

No outer parentheses are required around the `text(...) + context {...} + text(...)` chain even when
used directly as a multi-line function-call argument — verified after eliminating an unrelated test
artifact (Pitfall 2).

### The `pending_xref` degradation-pipeline evidence (for D-04)

```
$ sphinx-build -b typst source build
...
WARNING: undefined label: 'nonexistent-label-xyz' [ref.ref]
WARNING: unknown document: 'nonexistent-doc-xyz' [ref.doc]
WARNING: 'any' 参照先が見つかりません: nonexistent-any-xyz [ref.any]
WARNING: unknown node type: <problematic ids="id2" ...>:unknownrole:`nonexistent-custom-xyz`</problematic>
build succeeded, 5 warnings.
```

Emitted `.typ` for all four unresolved shapes: plain text (`:ref:`, `:doc:`), `raw("...")`-wrapped text
(`:any:`, via its `literal` contnode), or the unrelated `unknown node type` fallback (unknown role) —
none matches `visit_pending_xref`'s `#link(<label>)[...]` fallback pattern, confirming that code path
was not exercised by any of these four shapes.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| `builder.master_included_docnames` (a Python `set[str]`, unioned across ALL masters, computed once in `write()`) | `context { query(<label>) }` evaluated by Typst per compiled wrapper | This phase | The degrade decision becomes correct per-master instead of being an approximation that cannot distinguish which master is asking |
| Reference degradation logged via `logger.warning` at build time (`translator.py:4995-5001`) | No diagnostic replacement (D-01) | This phase | The one case that warning uniquely covered (an explicitly `:orphan:`-marked target) loses build-time visibility; Sphinx's own `unknown document`/`document isn't included in any toctree` warnings continue to cover the other cases unchanged |

**Deprecated/outdated:**
- `_compute_master_included_docnames()` and its `write()` call site — deleted in this phase, per SC#3.
- `_ReferenceAnchorDecision.degrade_xref_to_text` field — deleted in this phase, per D-09.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `let`-bound identifier name (`__b` in every example above) will not collide with any Typst-reserved identifier or a name already bound in the surrounding scope — this session tested only the illustrative `__b` name, not the exact identifier the implementation will choose | Architecture Patterns / Code Examples | Low — Claude's Discretion in `48-CONTEXT.md` already leaves this identifier unfixed; any sufficiently unique name (already the pattern's convention, double-underscore prefix) avoids collision |
| A2 | `pending_xref` is unreachable from ANY Sphinx extension interaction, not just the four shapes tested this session (`:ref:`, `:doc:`, `:any:`, unknown role) — a third-party extension emitting its own unresolved `pending_xref` after `ReferencesResolver` runs was not tested | Common Pitfalls Pitfall 4 | Low-Medium — if wrong, the "unconstructible RED" conclusion for D-04 would need revisiting; mitigated by D-04's own instruction to bring the site under the guard regardless of reachability, so behavior is correct either way even if the RED-construction conclusion changes |
| A3 | The full-corpus baseline of ~29 seconds (measured twice: 28.93s and 28.56s pytest-reported) is representative of this specific machine/session and may not transfer directly to CI hardware — D-11's thresholds are relative percentages, so this matters only for the ABSOLUTE numbers recorded, not the tiering logic | Environment Availability / D-11 cost measurement | Low — D-11's methodology is explicitly "one-off manual before/after record," so a different absolute baseline on a different machine does not invalidate the tiering approach, only requires re-measuring "before" on whatever machine measures "after" |

**If this table is empty:** N/A — three low/low-medium-risk assumptions recorded above; none blocks
planning.

## Open Questions

All five research priorities named in the phase brief were closed by direct measurement this session
(D-08's syntax, D-04's RED constructibility, D-11's baseline, D-05's route). No open questions remain
that block planning.

1. **Whether `visit_pending_xref`'s hardcoded `#` prefix (no `prefix` variable, unlike `visit_reference`)
   is itself a latent defect independent of this phase's guard work.**
   - What we know: the current code always emits `#link(<label>)[` regardless of surrounding mode.
   - What's unclear: whether this path is ever reached in markup mode only, or whether the hardcoding
     is already wrong in some code-mode context — moot if Pitfall 4's unreachability conclusion holds,
     since the site may never execute in a real build.
   - Recommendation: note this in the plan as a "verify at implementation, do not fix speculatively"
     item — out of this phase's stated scope (D-04 says "brought under the guard, not merely rewired,"
     not "audited for unrelated mode bugs").

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|----------|
| `typst` (typst-py) | Guard compile verification, all GATE-01 fixtures | ✓ | 0.15.0 [VERIFIED, this session] | — |
| `sphinx` | Real-build reproduction fixtures (D-04, D-05) | ✓ | 9.1.0 [VERIFIED, this session] | — |
| `pypdf` | Reading back link annotations from compiled PDFs | ✓ (already a test dependency, used in `tests/test_pdf_render_gate.py`) | not separately queried this session; already proven working via this session's own annotation-readback tests | — |
| Cached Sphinx `doc/` corpus (`~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0/`) | D-11's baseline measurement, `tests/test_corpus_gate.py` | ✓ | commit-pinned to `v9.1.0` tag, already cloned | Re-clones automatically if cache absent (`get_or_clone_corpus`) |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** None — everything this phase needs was already present and
working in the project's `.venv` this session.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 [VERIFIED: `pytest --version` output captured this session's `test_corpus_gate.py` run header] |
| Config file | `pyproject.toml` (`configfile: pyproject.toml`, confirmed in this session's pytest header) |
| Quick run command | `uv run pytest -m "not slow"` |
| Full suite command | `uv run pytest` (includes `-m slow` corpus/render-gate tests) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| XREF-03 | A reference to an absent target degrades to plain text; compile succeeds | integration (real `typst.compile()` + `pypdf` readback) | `uv run pytest tests/test_xref_orphan_degrade_render_gate.py -x` | ✅ (existing gate — its PREMISE moves from build-time to compile-time per `48-CONTEXT.md`'s "Tests this phase changes" list; content will change, file exists) |
| XREF-03 | Pre-fix RED recorded before the new emitter runs (binding constraint #6/#4) | integration | New fixture per Claude's Discretion (xfail(strict=True) or separate RED-EVIDENCE.md, per `48-CONTEXT.md`) | ❌ Wave 0 — new RED-evidence artifact needed |
| XREF-04 | Every label-reference site routes through the shared guard; grep for `master_included_docnames` returns nothing | structural (repo-wide grep) + unit | `grep -rn master_included_docnames typsphinx/` (must be empty) | N/A — a grep assertion, likely embedded in a new or existing test |
| XREF-04 | The four unit tests bound to `_compute_master_included_docnames()` are removed; three end-to-end tests survive | unit | `uv run pytest tests/test_master_include_set_predicate_gate.py -x` | ✅ (existing file, lines 103/129/165/196/227/260/288/319 confirmed present this session — matches D-10's line-level claims exactly) |
| XREF-04 (D-05) | Citation back-reference inside a captioned code-block compiles without a dangling-label fatal | integration (real `typst.compile()`) | New fixture — reproduced this session as a real RED (`label <index:id1> does not exist in the document`) | ❌ Wave 0 — this session's reproduction transcript is available as the pre-fix RED evidence; needs to become a committed fixture |
| XREF-04 (D-04) | `visit_pending_xref`/`depart_pending_xref` route through the guard | unit | `uv run pytest tests/test_translator.py -k pending_xref -x` (existing tests at lines 1973, 2001) | ✅ (existing coverage, unit-level only — no real-compile gate exists yet per `48-CONTEXT.md`'s own note) |
| D-11 | Full-corpus `-b typstpdf` compile time recorded before and after | manual measurement (not an automated assertion — `test_corpus_gate.py` carries no timing instrumentation, confirmed this session) | `time uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow` | ✅ (existing gate, used for this session's "before" measurement) |

### Sampling Rate
- **Per task commit:** `uv run pytest -m "not slow"` (fast suite; excludes the corpus gate)
- **Per wave merge:** `uv run pytest` (full suite including the corpus gate) plus a manual
  `time uv run pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow`
  run for D-11's "after" number once the guard lands
- **Phase gate:** Full suite green before `/gsd-verify-work`; D-11's tiered cost decision (recorded
  BEFORE the after-measurement, per D-11's own instruction) applied to the recorded before/after pair

### Wave 0 Gaps
- [ ] A committed pre-fix RED-evidence artifact for XREF-03's guarded-degrade behaviour (the fixture
  that currently exercises `tests/test_xref_orphan_degrade_render_gate.py`'s premise needs its
  expected-values-first artifact per D-03, mirroring `47-EXPECTED-STRUCTURE.md`)
- [ ] A committed fixture reproducing D-05's citation-in-caption fatal (this session's manual
  reproduction — `label <index:id1> does not exist in the document` — is not yet a committed test
  asset; it needs to become one as the pre-fix RED, per binding constraint #4)
- [ ] `tests/test_master_include_set_predicate_gate.py::TestBld03GhostEntryXref::test_ghost_entry_subtree_xref_degrades_typst`
  (line 103) needs its NEW expected value written down before the new emitter runs, per D-03 — this is
  the one assertion in that file that flips direction (asserts degrade-to-text today; must assert a
  guarded `link()` after)
- [ ] `tests/test_citation_degradation_gate.py`'s case (iii) at line 1007 (`_wr03_case_refuri_excluded_document`)
  needs its new expected value written down before the new emitter runs, per D-09/D-03 — `opens_wrapper`
  becomes unconditional, so a citation marker that previously did not appear now does

*(No framework install needed — pytest, typst-py, pypdf, and Sphinx are all already installed and
working in `.venv`.)*

## Security Domain

Not applicable to this phase. This is a compile-time correctness/degradation-behaviour change to a
document-generation pipeline with no authentication, session, network-input-validation, or cryptographic
surface. `security_enforcement` is not toggled off explicitly in `.planning/config.json`, but the ASVS
categories (V2 Authentication, V3 Session Management, V4 Access Control, V6 Cryptography) are all
structurally inapplicable to a local Sphinx/Typst document-build tool with no user-facing network
service. V5 Input Validation is already covered by the project's existing `escape_typst_string`/
`_sanitize_label` machinery (unchanged by this phase; the guard reuses `_namespace_label`, which already
routes through `_sanitize_label`).

## Sources

### Primary (HIGH confidence — verified this session by direct tool invocation)
- `typst.compile()` (typst-py 0.15.0) — 34 distinct `.typ` fixtures compiled this session to isolate the
  exact D-08 guard syntax, its failure modes, and its `pypdf`-verified annotation behaviour (positive
  and negative cases, streaming and value-expression usages, nested markup).
- `sphinx-build -b typst` (Sphinx 9.1.0) — two real project builds this session: one reproducing D-04's
  four unresolved-reference shapes, one reproducing D-05's citation-in-caption fatal end to end through
  `typst.compile()`.
- `/home/yuta/Documents/typsphinx/.venv/lib/python3.13/site-packages/sphinx/transforms/post_transforms/__init__.py`
  lines 40-249 — read directly this session; `ReferencesResolver.run()`'s unconditional
  `node.replace_self()` fallback is the mechanism behind D-04's conclusion.
- `typsphinx/translator.py` lines 33-103 (`_ReferenceAnchorDecision`), 2620-2703 (`visit_caption`/
  `depart_caption`), 3011-3330 (`_reference_anchor_decision`, `visit_citation`), 4230-4310
  (`visit_pending_xref`/`depart_pending_xref`), 4570-4600 (`_namespace_label`), 4900-5030
  (`visit_reference`'s cross-document branch) — all read directly this session; every line number cited
  in `48-CONTEXT.md`'s canonical_refs was cross-checked against the actual file and found to match
  exactly (e.g. the `logger.warning` at 4995-5001, the four test line numbers in
  `tests/test_master_include_set_predicate_gate.py`).
- `typsphinx/builder.py` — `grep -n` this session confirmed `_compute_master_included_docnames` (line
  257), `master_included_docnames` attribute (line 255), and the `write()` call site (line 758) all
  match `48-CONTEXT.md`'s canonical_refs exactly.
- `tests/test_corpus_gate.py` — read directly this session (lines 1-380); confirmed it carries no timing
  instrumentation and the exact invocation shape used for D-11's baseline measurement.

### Secondary (MEDIUM confidence)
- `.planning/PROJECT.md` lines 45-165 — the milestone-level design record, cross-checked against this
  session's own independent re-derivation rather than taken as given (the D-07/D-08 sketch specifically
  was re-verified and found to need one correction).

### Tertiary (LOW confidence)
- None used. Every claim in this document traces to either a file this session read directly or a
  command this session ran directly.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies, both existing dependencies' versions verified live.
- Architecture: HIGH — the guard's exact working Typst syntax was compiled and read back via `pypdf`
  this session, not inferred from documentation.
- Pitfalls: HIGH — all five pitfalls are transcribed from real `TypstError`/build transcripts produced
  this session, not anticipated from general Typst knowledge.

**Research date:** 2026-08-12
**Valid until:** Tied to `typst-py>=0.15.0,<0.16` and Sphinx 9.1.0 — re-verify the guard syntax if either
pin changes (Typst's own parser grammar is the load-bearing dependency here, more than either Python
package's version number). No fixed day-count expiry; re-verify on any `typst-py` major/minor bump.
