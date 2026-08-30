# Phase 62: The `visit_image()` Separator Fix and Its Real-Compile Gate - Research

**Researched:** 2026-08-30
**Domain:** Sphinx→Typst translator emitter defect (delta research — milestone-level research
already exists in `.planning/research/{SUMMARY,ARCHITECTURE,FEATURES,PITFALLS}.md`, written the
same day and read in full as input)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

The owner selected "おすすめ設定" — every decision below is Claude's measured recommendation,
accepted en bloc.

- **D-01: One fixture project, 26 documents, 18 masters.** `tests/fixtures/inline_image_separator_render_gate/`:
  `index.rst` (no-image root master, SC#1's blast-radius document), **16 FAIL documents** (one per
  `research/FEATURES.md` Q1 row, each its own master), **9 PASS documents** (one per Q2 row A–I,
  all toctree'd under one `pass_parent` document, the 18th master). `typst_documents` holds 18
  entries: `index` + 16 FAIL docs + `pass_parent`.
- **D-02: Per-shape attribution is obtainable only one-master-per-shape — measured.** A `typst.compile()`
  probe with three unseparated juxtapositions returned exactly ONE `expected semicolon or line
  break` message — `TypstError` carries no file/line/multiplicity. `TypstPDFBuilder.finish()`
  attempts every master, then raises ONE aggregate `ExtensionError` joining `f"{docname}: {err}"`
  per failure. One build against the unfixed tree yields one aggregate error naming **17** masters
  (`index` + 16 FAIL docs), each carrying the verbatim refusal, with docname supplying attribution.
- **D-03: `pass_parent` is a positive control inside the RED run.** Must come back green in the
  SAME RED build in which 17 others are red.
- **D-04: One RED build, transcribed verbatim, following Phase 59's choreography.** Restore
  `git checkout $PHASE_BASE_SHA -- typsphinx/translator.py`, run the gate, transcribe the aggregate
  `ExtensionError` verbatim, restore the fix, record `git status --porcelain` empty. Gate module
  greps positive for `typst.compile` / `TYPST_AVAILABLE`.
- **D-05: The evidence file is `62-RED-EVIDENCE.md`, never `62-VERIFICATION.md`** (reserved output
  name, clobbered at verify time). Follows `59-WINDOWS-URI-EVIDENCE.md`'s naming.
- **D-06: Byte-identity, not merely "compiles."** ROADMAP SC#3 says the 9 shapes "compile";
  `research/FEATURES.md` Q2 says byte-identical. Bind the stronger one.
- **D-07: The goldens come from the unfixed tree, captured during the RED run.** Commit the 9
  PASS documents' emitted **content** `.typ` files (never wrapper files — title/author/date, not
  stable test data) as goldens during D-04's restore window. Planning must first confirm content
  `.typ` output carries no build-volatile bytes; if it does, narrow the golden to the image-bearing
  region rather than abandoning byte-identity.
- **D-08: The triad's insertion point is decided by D-06's goldens, not by fiat.** Measured hazard:
  `_emit_id_anchors()` (`translator.py:1023-1028`) already emits `\n[#metadata(none) <id>]\n` and
  sets `list_item_needs_separator = True` when `in_list_item`. A triad placed *after* that call may
  double-separate an id-carrying image inside a list item. Placement is whichever keeps the 9
  goldens byte-identical — measure, don't argue.
- **D-09: Phase 62 does not touch `CHANGELOG.md`.** Follows v0.9.1's pattern (fix phases silent,
  release-prep authors every bullet).
- **D-10: Push at phase head, dispatch the authority CI run at phase end.** Push
  `gsd/v0.9.2-inline-image-blocker-fix-and-release` with `-u` in the phase's first plan.
- **D-11: Exactly one authority run, dispatched after the phase's last commit.**
  `gh workflow run CI --ref gsd/v0.9.2-inline-image-blocker-fix-and-release`, waited to completion,
  `windows-latest`/`macos-latest` named individually. `ruff`'s verdict from that run's `Run
  linters` step, never from this machine.
- **D-12: Expect the decoy `gsd/v0.9.2-milestone` to be re-created by the next commit helper.**
  Advance the canonical pointer before deleting it if it reappears.
- **D-13: Zero pre-existing test edits, measured.** `git diff --name-status` over this phase's own
  range scoped to `tests/` must show only `A` entries.

### Claude's Discretion

Planning may refine the fixture's internal file names and the exact golden-comparison helper
shape; it may **not** weaken D-06 (byte-identity), D-09 (no CHANGELOG in this phase), or D-13
(zero test edits) without returning to the owner.

### Deferred Ideas (OUT OF SCOPE)

- A cheap string-level (non-compiling) regression test alongside the real-compile gate — not built,
  the real compile is the authority.
- A doc-comment in `visit_image()` cross-referencing `visit_Text`'s triad by name — fold in if it
  costs nothing, not a requirement.
- Auditing the other thirteen inline constructs, refactoring the separator machinery,
  `:scale:`/`:align:` support, figure/legend styling, a from-scratch line-boundary predicate — all
  binding **Out of Scope** per REQUIREMENTS.md.
- MSG-06, REL-04, QUA-10, NUM-01, CI-01 (reviewed todos, not folded — see NUM-01 fixture-hazard
  finding below, which is the one with direct bearing on this phase's fixture design).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| IMG-08 | Image node preceded by sibling content emits a separator before `image(` across the 16 measured failing shapes | Architecture Patterns (triad mechanism), Code Examples, D-08 delta finding (insertion-point measurement) |
| IMG-09 | `-b typstpdf` produces a PDF for every master, including the image-free root | Common Pitfalls #2 (blast radius via `#include()`), D-05 delta finding (aggregate-error shape) |
| IMG-10 | Fix routes through the existing triad only, `in_figure` branch untouched, zero pre-existing test edits | Architecture Patterns, Don't Hand-Roll, D-08 delta finding |
| TEST-05 | One regression gate module binding 16 FAIL + 9 PASS shapes on a real `typst.compile()`, RED-first | Validation Architecture, Code Examples (gate skeleton), D-04/D-07 delta findings |
</phase_requirements>

## Summary

The milestone-level research (`FEATURES.md`, `ARCHITECTURE.md`, `PITFALLS.md`, `SUMMARY.md`,
2026-08-30) already measured the defect exhaustively and is not repeated here. This document
closes the seven concrete gaps CONTEXT.md left open for planning, each answered by reading the
actual code this session and, where cheap, by a real emission/compile probe — never by reasoning
alone.

**The two load-bearing new findings, in order of planning impact:**　

1. **D-07's precondition holds, with one real caveat.** Content `.typ` output is byte-stable across
   two consecutive builds on this machine (measured `diff` clean) and carries no timestamp,
   absolute path, or ordering nondeterminism. But the write path (`builder.py:2072`, `:2139`) is a
   bare `open(path, "w", encoding="utf-8")` with no `newline=""` — on `windows-latest` this
   translates `\n` → `\r\n` at write time. The golden-comparison gate MUST read both the golden and
   the freshly-built file via `Path.read_text(encoding="utf-8")` (universal-newline text mode),
   never `.read_bytes()`, or the Windows CI lane will report a spurious mismatch that has nothing to
   do with the fix. No narrowing to an image-bearing region is needed — the whole content file is
   safe to golden.

2. **D-08's placement question is answered, and the "hazard" is real but harmless, and does not
   touch the measured goldens.** A real emission probe (monkey-patched `TypstTranslator`, actual
   docutils nodes, actual `.typ` output diffed) confirms: placing the triad immediately before the
   `image(` call — i.e. leaving `_emit_id_anchors()`'s existing call site at the top of
   `visit_image()` completely untouched, which is also the minimum-diff choice and the one the
   milestone `ARCHITECTURE.md` already recommends — produces exactly **one** redundant-but-harmless
   blank line for an id-carrying image inside a list item (a shape combination absent from all 9
   measured PASS goldens; shape E, the only id-carrying golden, is standalone/top-level, never in a
   list item). A probe build of shape E's exact fixture (`.. _mytarget:` + `.. image::`, no list, no
   figure) with the fix applied is **byte-identical** to the pre-fix output (`BYTE IDENTICAL: True`,
   measured). Reordering the call (triad-before-anchor) does not eliminate the redundancy — it only
   relocates it to before the anchor line instead — because neither `_emit_id_anchors()` nor the
   triad ever clears `list_item_needs_separator` before the other reads it. **Recommendation: do not
   reorder; insert the triad at the architecture-recommended site.**

**Primary recommendation:** plan the fix as the architecture research already specifies (triad
inserted verbatim before the `image(` call in the non-`in_figure` branch, `depart_image()` gets the
matching trailing mark), plan the gate as an **extension** of the two-precedent skeleton
(`test_paragraph_concat_render_gate.py` + `test_abbr_pep_separator_render_gate.py`) but note the
one structural delta this fixture introduces that neither precedent has: 18 independently
configured masters compiled in **one** `sphinx-build -b typstpdf` invocation, not one master per
gate module — the assertion shape must read the aggregate `ExtensionError` text for the 16+1 FAIL
docnames and independently confirm `pass_parent`'s own `.pdf` exists on disk (its success is never
named in the exception, only in the build's `Generated PDF: ...` log line).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Separator emission (`visit_image`/`depart_image`) | Core library — docutils→Typst translator | — | Pure in-process string emission, no I/O, no external service |
| Real-compile regression gate | Test infrastructure | Core library (imports `typst`) | Drives the same `sphinx-build -b typstpdf` subprocess path production users exercise |
| RED-evidence capture (D-04) | Test infrastructure / process | Version control (git checkout/restore) | Git-mediated restore-measure-restore choreography, not a runtime concern |
| Milestone branch push + CI dispatch (SC#5) | Build/CI tier | — | GitHub Actions workflow dispatch, outside the Python process entirely |

This phase has no browser, server, or database tier — it is a single-process Python library
emitting text, plus test/CI process orchestration around it.

## Standard Stack

### Core

No new packages. Every dependency (`typst-py`, `sphinx`, `docutils`, the four `@preview` Typst
Universe packages) is unchanged per REQUIREMENTS.md's binding Out of Scope table ("All verified
current against PyPI and Typst Universe on 2026-08-30 and already matching this repo's pins... This
is a blocker-fix-and-release round, not an ecosystem round"). Confirmed still true this session:

| Library | Version (pinned) | Purpose | Why unchanged |
|---------|------|---------|--------------|
| `typst-py` | as pinned in `pyproject.toml` | Real `typst.compile()` gate + PDF compilation | `[VERIFIED: typsphinx/.venv/lib/python3.13/site-packages/typst/__init__.py exists, imports cleanly this session]` |
| `pypdf` | as pinned (dev extra) | Extracted-text adjacency asserts (optional, per `test_abbr_pep_separator_render_gate.py`'s `PYPDF_AVAILABLE` pattern) | `[VERIFIED: import pypdf succeeded this session]` |

### Supporting

None new. `gh` CLI (`2.98.0`, confirmed on `$PATH` this session — `[VERIFIED: gh --version this session]`)
is required for D-11's CI dispatch, already a standing project dependency (used at every prior
milestone close).

### Alternatives Considered

Not applicable — no new library decision exists in this phase; the fix reuses existing in-repo
mechanisms exclusively (REQUIREMENTS.md IMG-10, binding).

**Installation:** none required.

## Package Legitimacy Audit

**Not applicable.** This phase installs zero external packages — REQUIREMENTS.md's Out of Scope
table explicitly excludes bumping `typst-py`/`sphinx`/`docutils`/the four `@preview` packages from
this milestone. No package-legitimacy check was run because there is nothing to check.

## Architecture Patterns

### System Architecture Diagram

```
rST source (mid-paragraph image node)
        │
        ▼
  docutils doctree walk
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│ TypstTranslator.visit_image() / depart_image()             │
│  (typsphinx/translator.py:4718-4783)                       │
│                                                              │
│  if not in_figure:                                          │
│    _emit_id_anchors(node)   ← existing, UNCHANGED           │
│    ...compute escaped_uri...                                │
│    ┌─────────────────────────────────────────────────┐     │
│    │ NEW: the triad (mirrors visit_Text, :1775-1846)   │     │
│    │  _add_paragraph_separator()                       │     │
│    │  if not _emit_inline_concat_separator():          │     │
│    │    if in_list_item and list_item_needs_separator: │     │
│    │      add_text("\n")                               │     │
│    └─────────────────────────────────────────────────┘     │
│    add_text(f'image("{escaped_uri}"...)')                   │
│    ┌─────────────────────────────────────────────────┐     │
│    │ NEW (depart_image, before existing "\n\n"):        │     │
│    │  if not _mark_inline_concat_content():             │     │
│    │    if in_list_item: list_item_needs_separator=True │     │
│    └─────────────────────────────────────────────────┘     │
│  else (in_figure): UNCHANGED, no triad                      │
└───────────────────────────────────────────────────────────┘
        │
        ▼
  emitted .typ (content document, one #{...} code-mode block)
        │
        ├──► #include()'d by every wrapper that transitively reaches it
        ▼
  TypstPDFBuilder.finish() (typsphinx/builder.py:2505-2642)
    for each of 18 configured masters:
      compile_typst_file_to_pdf(wrapper.typ) ── typst.compile() ──► .pdf
      (failure ⇒ appended to `failures`, loop CONTINUES to next master)
    if failures: raise ONE aggregate ExtensionError
        │
        ▼
  Real-compile regression gate (pytest, subprocess sys.executable -m sphinx)
    asserts: returncode==0, no "Typst compilation failed" in stderr,
    all 18 wrapper .pdf files exist + start with %PDF,
    9 content .typ files == committed golden (via read_text(), not bytes)
```

### Recommended Project Structure

```
tests/
├── fixtures/
│   └── inline_image_separator_render_gate/
│       ├── conf.py                    # 18-entry typst_documents (D-01)
│       ├── index.rst                  # no-image root master
│       ├── fail_01_sub_mid_sentence.rst   ... fail_16_*.rst   (16 FAIL masters)
│       ├── pass_parent.rst            # toctree of the 9 PASS docs, the 18th master
│       ├── pass_a_standalone_image.rst ... pass_i_bare_image_first_in_list_item.rst
│       └── goldens/                   # D-07: committed content .typ, captured pre-fix
│           ├── pass_a_standalone_image.typ
│           ├── ...
│           └── pass_i_bare_image_first_in_list_item.typ
└── test_inline_image_separator_render_gate.py   # TEST-05's one gate module
```

### Pattern 1: The separator triad (verbatim reuse, no new helper)

**What:** `_add_paragraph_separator()` + `_emit_inline_concat_separator()` +
`in_list_item`/`list_item_needs_separator` — already used by `visit_Text`, `visit_literal`,
`visit_math`, `visit_footnote_reference`, `visit_reference`.
**When to use:** Immediately before any code-mode expression emission that can follow a sibling.
**Example (canonical call shape, read this session):**
```python
# Source: typsphinx/translator.py:1775-1788 (_emit_signature_leaf_wrapper,
# the exact triad shape to mirror) — verbatim, confirmed by direct read
self._add_paragraph_separator()
if not self._emit_inline_concat_separator():
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")

# ...emit the node's own content here...

if not self._mark_inline_concat_content():
    if self.in_list_item:
        self.list_item_needs_separator = True
```

### Pattern 2: `_emit_id_anchors()` already owns its own list-item separator (do not duplicate its intent)

**What:** `_emit_id_anchors()` (`translator.py:945-1029`, read in full this session) independently
implements `if self.in_list_item and self.list_item_needs_separator: self.add_text("\n")` before
emitting `\n[#metadata(none) <id>]\n`, and sets `list_item_needs_separator = True` after — its own
private instance of the SAME pattern the triad implements, run once per id it anchors.
**When it matters:** an image node that both carries a propagated id AND sits inside a list item
after prior content triggers BOTH checks (measured, see Code Examples below) — this is provably
cosmetic (an extra blank line, never a syntax break) and does not touch any of the 9 measured
goldens (none combine id + list-item).
**Example — the exact lines in `visit_image()` this phase touches, read this session:**
```python
# Source: typsphinx/translator.py:4728-4756 (visit_image, current/pre-fix state)
if not self.in_figure:
    self._emit_id_anchors(node)          # UNCHANGED — leave this call exactly here

uri = node.get("uri", "")
current_docname = getattr(self.builder, "current_docname", None)
adjusted_uri = self._compute_relative_image_path(uri, current_docname)
escaped_uri = escape_typst_string(adjusted_uri)

if self.in_figure:
    self.add_text(f'  image("{escaped_uri}"')   # UNCHANGED branch
else:
    # INSERT the triad here, immediately before this add_text call:
    self.add_text(f'image("{escaped_uri}"')      # <- triad goes directly above this line
```
```python
# Source: typsphinx/translator.py:4774-4783 (depart_image, current/pre-fix state)
def depart_image(self, node: nodes.image) -> None:
    if not self.in_figure:
        self.add_text("\n\n")   # UNCHANGED — INSERT the trailing mark ABOVE this line
```

### Anti-Patterns to Avoid

- **Reordering `_emit_id_anchors(node)` relative to the triad:** measured this session (two probe
  variants) — swapping the call order does not remove the redundant blank line, it only relocates
  it earlier (before the anchor instead of before `image(`), because neither routine clears
  `list_item_needs_separator` before the other reads it. Not worth the diff; leave the existing call
  site untouched.
- **Inventing a `self.body`-inspecting "already at a line boundary" predicate:** already rejected in
  `ARCHITECTURE.md` Q2/Q3 and confirmed absent from the codebase by `grep`; REQUIREMENTS.md's Out of
  Scope table forbids it explicitly.
- **Comparing goldens with `.read_bytes()`:** will spuriously fail on `windows-latest` due to the
  `\n`→`\r\n` write-time translation this session confirmed at `builder.py:2072`/`:2139` — always
  `.read_text(encoding="utf-8")`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Leading-separator detection before `image(` | A new `self.body`-inspecting boundary predicate | The existing triad (`_add_paragraph_separator`/`_emit_inline_concat_separator`/`in_list_item` check) | Already proven correct for 5 other emitters; a parallel mechanism would duplicate `add_text()`'s own `table_cell_content`-vs-`body` routing decision at the call site — explicitly warned against in the file's own comments |
| Real-compile regression gate scaffolding | A bespoke subprocess/PDF-magic-byte harness | `_run_sphinx_build_typstpdf()` idiom from `test_paragraph_concat_render_gate.py` | 56 existing `tests/test_*_render_gate.py` modules already share this exact skeleton; TEST-05 is a new instance, not a new pattern |
| RED-first evidence choreography | A one-off ad hoc "I reverted the file and it failed" claim | Phase 59's `git checkout $PHASE_BASE_SHA -- <file>` / re-run / restore / `git status --porcelain` empty pattern, recorded in `<phase>-RED-EVIDENCE.md` | Already proven, already the project's own established antidote to Pitfall 2 (tautological gate) |

**Key insight:** every mechanism this phase needs already exists in this repository, proven at
least once before. The work is composition (apply the triad to one more call site, extend a
proven gate skeleton to 18 masters), not invention.

## Common Pitfalls

Full ranked catalogue with repo-incident citations is in `.planning/research/PITFALLS.md`
(12 pitfalls, not repeated verbatim here). The phase-critical subset, with this session's
confirmation:

### Pitfall 1: A gate that asserts only on the emitted string cannot see this defect

**What goes wrong:** The nine pre-existing `test_translator.py` image unit tests
(lines 1706–3918) never call `typst.compile()` — confirmed still true this session (no new image
test added since the milestone research was written). A new gate that only inspects
`translator.body` would pass on the SAME broken output that fooled these nine tests.
**Prevention:** the new gate module MUST grep-positive for `typst.compile`/`TYPST_AVAILABLE`
(D-04's own explicit acceptance criterion).

### Pitfall 2: The aggregate `ExtensionError` never names a successful master

**What goes wrong (new finding, this session):** `TypstPDFBuilder.finish()`'s `failures` list
(`builder.py:2552`) only ever receives FAILED docnames; a master that compiles successfully is
logged via `logger.info(f"Generated PDF: {pdf_file}")` (`builder.py:2632`) and never appears in the
final `raise ExtensionError(...)` text at all (`builder.py:2638-2642`, quoted verbatim below). An
evidence procedure that only parses the exception text will never observe `pass_parent`'s success.
**Prevention:** D-04's evidence capture must ALSO assert `pass_parent`'s wrapper `.pdf` exists on
disk (the loop continues past individual failures — the `try/except: failures.append(...); continue`
shape at `builder.py:2619-2636` guarantees every master is attempted regardless of earlier
failures) and that the captured stdout contains its `Generated PDF: ...` line.

### Pitfall 3: Windows write-mode newline translation threatens the D-07 goldens

**What goes wrong (new finding, this session):** `builder.py:2072`/`:2139` write content/wrapper
`.typ` files via bare `open(path, "w", encoding="utf-8")` — no `newline=""`. On `windows-latest`
this silently converts `\n` to `\r\n` at write time. A golden-comparison test using
`Path.read_bytes()` (or any binary compare) will spuriously fail on the Windows CI lane even when
the fix is byte-for-byte correct.
**Prevention:** compare via `Path.read_text(encoding="utf-8")` for BOTH the committed golden and the
freshly-built file (Python's text-mode read normalizes `\r\n`→`\n` on input regardless of platform,
so this is the correct comparison, not merely a workaround).

### Pitfall 4 (from milestone PITFALLS.md, reconfirmed applicable): `ruff` unrunnable in a fresh worktree

`nix run nixpkgs#ruff -- check .` or a linked CI run's `Run linters` step is the lint authority per
D-11 — not local `black`/`mypy` alone.

## Code Examples

### Emission probe — the redundant-but-harmless blank line (this session, real `TypstTranslator`, real docutils nodes)

Probe fixture: `- First paragraph text.\n\n  .. _mytarget:\n\n  .. image:: images/img.png` (id-carrying
image inside a list item, preceded by a sibling paragraph — NOT one of the 25 fixture documents,
constructed specifically to stress-test D-08's hazard). Recommended placement (triad immediately
before the `image(` add_text call, `_emit_id_anchors()` untouched):

```
list({
parbreak()

text("First paragraph text.")


[#metadata(none) <index:mytarget>]

image("images/img.png")


})
```

One blank line appears between `]` and `image(` — `_emit_id_anchors()`'s own trailing `\n` plus the
triad's own list-item check both fire against the same still-`True` `list_item_needs_separator`
flag. Confirmed cosmetic-only (compiles; per `PITFALLS.md` Part 2's own direct `typst.compile()`
measurement that a bare newline between complete top-level statements is pure whitespace). Reordering
the call (triad-before-anchor) produces the same redundancy, relocated earlier:

```
text("First paragraph text.")



[#metadata(none) <index:mytarget>]
image("images/img.png")
```

(two blank lines before the anchor instead of one before the image — strictly worse, not better).

### Byte-identity confirmation — shape E (the only id-carrying golden) is unaffected

```
# Source: this session's scratch probe, real Sphinx build via typsphinx.translator.TypstTranslator,
# fixture: `.. _mytarget:\n\n.. image:: images/img.png` (standalone, top-level, no list, no figure)
BYTE IDENTICAL: True
```

### Aggregate `ExtensionError` — exact format the RED transcription must reproduce

```python
# Source: typsphinx/builder.py:2638-2642 (TypstPDFBuilder.finish(), read this session)
if failures:
    summary = "; ".join(f"{docname}: {err}" for docname, err in failures)
    raise ExtensionError(
        f"typstpdf: {len(failures)} master document(s) failed: {summary}"
    )
```

The join separator is literally `"; "` (semicolon-space), and the wrapping message is
`"typstpdf: {N} master document(s) failed: {summary}"` — D-04's transcription must match this exact
shape, not a paraphrase.

### Gate skeleton to extend — exact reusable pieces (read in full this session)

```python
# Source: tests/test_paragraph_concat_render_gate.py:56-79 — the subprocess helper, reusable verbatim
def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf", str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )
```

```python
# Source: tests/test_paragraph_concat_render_gate.py:82-85 — the TYPST_AVAILABLE skip guard
@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the paragraph-concat render gate",
)
```

**Structural delta this phase's gate must add, absent from both precedents:** both
`test_paragraph_concat_render_gate.py` and `test_abbr_pep_separator_render_gate.py` compile
exactly ONE master per fixture (`index.typ` → `master.pdf`). This phase's fixture configures 18
masters compiled in a SINGLE `sphinx-build -b typstpdf` invocation (D-01/D-02). The new gate must
therefore, after one `_run_sphinx_build_typstpdf()` call:
1. Assert the 17 FAIL docnames (`index` + 16 fail_*) all appear in `result.stderr`'s aggregate
   error text, each paired with the verbatim `expected semicolon or line break` refusal.
2. Assert NONE of the 17 FAIL masters' `.pdf` wrapper files exist in the build dir.
3. Assert `pass_parent`'s wrapper `.pdf` DOES exist, is non-empty, and starts with `%PDF` — the
   positive control (D-03), observed via the filesystem, not via the exception text (Pitfall 2
   above).

## State of the Art

Not applicable — this is an internal single-repository bugfix with no external ecosystem-facing
API surface change; `research/SUMMARY.md`'s own "no bump needed" conclusion still holds, reconfirmed
this session (no stack element checked).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The 18-master fixture's `sphinx-build -b typstpdf` wall-clock extrapolates linearly from the 3-master/6-doc probe (~0.44s) and the 1-master/1-doc baseline (~0.31s) to roughly 1-2s for 18 masters/26 docs. Not independently re-measured at the full 18-master scale (no such fixture exists yet to time). | 18-master fixture cost (Validation Architecture) | If the real build is materially slower (e.g. due to 16 distinct image-copy operations or per-fixture parsing overhead this small extrapolation didn't include), the gate may need `@pytest.mark.slow`; low risk since even a 5-10x miss stays well under any "slow" threshold used elsewhere in this suite |

**All other findings in this document are `[VERIFIED]` — confirmed by direct file read or a live
measurement taken this session** (probe builds, `diff`, `typst.compile()`, `git rev-parse`
precedent reads). No package-name or external-fact claims were made.

## Open Questions

All seven questions CONTEXT.md posed to planning are answered in the Summary and inline sections
above; none remain open. The one item carried to the Assumptions Log (A1) is a magnitude estimate,
not a blocking unknown — the direction (fast, no `slow` marker needed) is unambiguous from the
measurement.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst-py` | Real-compile gate (TEST-05), PDF compilation | ✓ | pinned per `pyproject.toml`, imports cleanly | — |
| `pypdf` | Optional extracted-text assert (dev extra, mirrors `test_abbr_pep_separator_render_gate.py`) | ✓ | pinned, imports cleanly | Gate can omit the pypdf-based test class if unavailable — the compile-gate class alone still satisfies TEST-05 |
| `gh` CLI | D-11's CI dispatch | ✓ | 2.98.0 | — |
| `uv` | Worktree provisioning (CLAUDE.md, mandatory) | ✓ | in use throughout this session | — |
| `ruff` (local) | Lint | ✗ (known NixOS hazard, per project memory/PITFALLS.md Pitfall 4) | — | CI's `Run linters` step is the lint authority (D-11); do not attempt local `ruff` |

No missing dependency blocks this phase.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`, `addopts = "-v --strict-markers"`, `markers = ["slow: ..."]`) |
| Config file | `pyproject.toml` (existing) |
| Quick run command | `uv run pytest tests/test_inline_image_separator_render_gate.py -q` |
| Full suite command | `uv run pytest -q` (matches CI; `pytest -m "not slow"` is the documented fast path, not needed here per A1) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| IMG-08 | Separator emitted before `image(` for all 16 FAIL shapes | real-compile integration | `uv run pytest tests/test_inline_image_separator_render_gate.py -k fail -q` | ❌ Wave 0 (new module + fixture) |
| IMG-09 | Every one of 18 masters (incl. image-free `index`) produces a `.pdf` post-fix | real-compile integration | `uv run pytest tests/test_inline_image_separator_render_gate.py -k full_matrix -q` | ❌ Wave 0 |
| IMG-10 | `in_figure` branch untouched; zero pre-existing test edits | structural/grep assertion (part of the plan's own verification, not a pytest test) | `git diff --name-status $PHASE_BASE_SHA..HEAD -- tests/` shows only `A`; `grep -n 'endswith("\\n")\|rstrip().endswith\|\[-1:\]' typsphinx/translator.py` returns nothing | N/A (process check) |
| TEST-05 | RED-first, real-compile gate binding 16 FAIL + 9 PASS | real-compile integration + evidence file | gate module itself; `62-RED-EVIDENCE.md` transcription | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `uv run pytest tests/test_inline_image_separator_render_gate.py -q`
- **Per wave merge:** `uv run pytest -q` (full suite, matches CI)
- **Phase gate:** Full suite green before `/gsd-verify-work`, PLUS the RED-evidence choreography
  (D-04) executed at least once regardless of wave structure — this is a phase-level, not
  per-wave, obligation, since it requires a temporary restore of `typsphinx/translator.py` to the
  phase base SHA.

### Wave 0 Gaps

- [ ] `tests/fixtures/inline_image_separator_render_gate/` — the 26-document, 18-master fixture
      (D-01); zero existing fixture matches this shape (closest precedent,
      `state_guard_three_master_gate/`, has 3 masters/6 docs — this phase's fixture is 6x larger)
- [ ] `tests/test_inline_image_separator_render_gate.py` — the one gate module (TEST-05)
- [ ] `tests/fixtures/inline_image_separator_render_gate/goldens/*.typ` — the 9 committed content
      goldens (D-07), captured during the RED window per D-04's choreography
- [ ] `62-RED-EVIDENCE.md` — the phase's evidence file (D-05)

*(Framework itself needs no install — pytest, typst-py, pypdf all already present.)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No | No auth surface in this phase |
| V3 Session Management | No | N/A |
| V4 Access Control | No | N/A |
| V5 Input Validation | Partial — reused, not introduced | `escape_typst_string()` (existing, `typsphinx/translator.py`) is REUSED unmodified for the image URI at the escaping call site this phase does not touch (`escaped_uri` computed identically pre- and post-fix); the fix itself only changes WHERE a separator is inserted relative to an already-escaped string, never how escaping is performed |
| V6 Cryptography | No | N/A |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Typst code-mode string-literal injection via an unescaped image URI | Tampering | Already mitigated (IMG-05, v0.9.1) via `escape_typst_string()`; this phase's fix runs strictly before the already-escaped string is emitted and does not alter the escaping call — no new injection surface is opened by inserting a separator |

This phase introduces no new external input path, no new file I/O beyond what the existing
translator/builder already perform, and no new network/service dependency. The security-relevant
surface (image URI escaping) is unmodified.

## Sources

### Primary (HIGH confidence — direct file reads this session)

- `typsphinx/translator.py:933-1029` (`_add_paragraph_separator`, `_emit_id_anchors`) — read in full
- `typsphinx/translator.py:1630-1846` (`_CONCAT_CONTEXTS` through `visit_Text`) — read in full
- `typsphinx/translator.py:4700-4790` (`visit_image`/`depart_image`/`visit_target` boundary) — read
  in full
- `typsphinx/builder.py:2490-2650` (`TypstPDFBuilder.finish()`) — read in full
- `tests/test_paragraph_concat_render_gate.py` — read in full
- `tests/test_abbr_pep_separator_render_gate.py` — read in full
- `tests/fixtures/state_guard_three_master_gate/conf.py` and directory listing — read
- `.planning/milestones/v0.9.1-phases/59-.../59-WINDOWS-URI-EVIDENCE.md` — read (partial, first
  ~908 lines, covering the `PHASE_BASE_SHA` precedent and the zero-test-edit measurement pattern)
- `.planning/todos/pending/2026-08-14-numref-number-diverges-per-master-and-vanishes-for-non-root-only-figures.md` — read in full
- `pyproject.toml` (pytest markers section) — read
- Live probe builds this session (scratchpad, never touching the repo tree): id+list-item emission
  probe (two variants), shape-E byte-identity probe, content-`.typ` build-twice-and-diff probe,
  3-master and 1-master `sphinx-build -b typstpdf` timing probes, `gh`/`typst`/`pypdf` availability
  checks

### Secondary (MEDIUM confidence)

- `.planning/research/{SUMMARY,ARCHITECTURE,FEATURES,PITFALLS}.md` — milestone-level research,
  read in full as required input, not independently re-verified line-by-line in this pass (already
  HIGH confidence per their own metadata, dated the same day)
- `.planning/phases/62-.../62-CONTEXT.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md` —
  read as required input

### Tertiary (LOW confidence)

None — every claim in this document is either a direct read or a live measurement.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies, confirmed present this session
- Architecture: HIGH — triad mechanism already established by milestone research; this session's
  delta (insertion-point measurement, aggregate-error shape, newline write-mode hazard) is all
  direct-read or live-probe confirmed
- Pitfalls: HIGH — milestone `PITFALLS.md` plus three new findings this session (aggregate-error
  attribution gap, Windows newline-translation hazard, id+list-item redundant-separator behavior),
  all measured

**Research date:** 2026-08-30
**Valid until:** 7 days (fast-moving milestone phase; re-verify if `typsphinx/translator.py` or
`typsphinx/builder.py` changes before planning is consumed)
