# Phase 22: typstpdf Target-Name PDF Fix (Issue #117) - Research

**Researched:** 2026-07-21
**Domain:** Sphinx builder internals (`typsphinx/builder.py`) — output-filename derivation for a
custom Sphinx builder pair (`typst` / `typstpdf`)
**Confidence:** HIGH — every claim below is a direct code/tool measurement against this
repository, not external-library research. No web research was needed (per `<research_focus>`);
the one Sphinx-internals question (`get_target_uri()`) was answered by reading the installed
Sphinx 9.x source directly.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Scope of the rename**
- **D-01: Fix BOTH the `.typ` and the `.pdf` filename** — not the PDF alone. Rationale: the `.typ` side is equally broken and `docs/configuration.rst:43` already documents the target name as the output `.typ` filename, so a PDF-only fix would leave `index.typ` + `manual.pdf` — an incoherent pair that still contradicts the docs. Rejected: PDF-only (smaller diff, but preserves the documented-contract violation and creates a mismatched pair).
- **D-02: The fix targets the master-document write path only.** Documents NOT listed in `typst_documents` (toctree-included children) have no target name and keep being written as `docname + ".typ"` — unchanged. Only entries present in `typst_documents` get the target-name treatment.

**Target-name normalization**
- **D-03: Strip only a literal trailing `.typ`, then append the builder's suffix.** `'output.typ'` → stem `output` → `output.typ` / `output.pdf`; `'typsphinx'` (extension-less) → stem `typsphinx` → `typsphinx.typ` / `typsphinx.pdf`. Both forms occur in the real corpus and both MUST work.
- **D-04: Do NOT use `os.path.splitext`.** It would mangle a period-bearing stem (`'v1.2-manual'` → `'v1'`). Rejected explicitly for that reason. Extension-less target names are **valid input**, never a warning or an error — `docs/source/conf.py` itself uses one.

**Output location for nested docnames**
- **D-05: Rename the basename in place — the output file stays in the docname's own directory.** `('sub/index', 'manual.typ', …)` → `outdir/sub/manual.typ` and `outdir/sub/manual.pdf`, NOT `outdir/manual.typ`. Rationale: the translator emits child includes and image URIs relative to the master's **docname** location (`_compute_relative_include_path`, `translator.py:2928`, emitted at `:3428` as `include("<rel>.typ")`; `_compute_relative_image_path`, `:3043`). Moving the master's output elsewhere without rebasing those paths would invalidate them for `-b typst`. **Known limitation, deliberately accepted:** this keeps multi-master deliverables scattered across the output tree, and it does NOT fix the pre-existing `-b typstpdf` root mismatch (see `<deferred>`) — Phase 22 fixes the filename bug only and leaves the layout/rebasing question to a separate item. Owner-confirmed 2026-07-21. Rejected: collecting masters at the outdir root (correct end state, but requires rebasing relative-path computation in `translator.py` — a different bug from Issue #117).
- **D-06: A path-bearing target name is an explicitly GUARDED case — warn, then fall back to its basename.** `'sub/manual.typ'` → `logger.warning` ("a path is not supported in a `typst_documents` target name; emitting `manual.typ` next to the source document instead") → `manual` placed next to the docname. Rationale: honoring a user-supplied directory would re-introduce exactly the relative-path breakage D-05 avoids, but silently discarding the path leaves the user with output somewhere they did not ask for and no signal — the mismatch must be surfaced. A warning (not an error) keeps builds that currently "work" (the path is being ignored today anyway) from breaking, and users running `sphinx-build -W` still get a hard failure. Rejected: raising `ExtensionError` (breaks previously-building configs), and interpreting the target as an outdir-relative path (flexible, but pushes the relative-path recomputation problem into this phase, far beyond its scope).
- **D-07: The guard detects separators portably, and covers traversal and absolute forms.** Trigger on `/` **and** `os.sep`/`os.altsep` (so a Windows `sub\manual.typ` is caught on every platform), and treat `..` segments and absolute/drive-qualified targets as the same guarded case. `os.path.basename` alone is not a sufficient detector — detect first, warn, then reduce.

**Backward compatibility**
- **D-08: Clean break — no compatibility shim.** `index.typ` / `index.pdf` simply stop being emitted when a target name differs. No duplicate file, no copy, no symlink. Rationale: this is a bug fix restoring documented behavior; emitting both would leave permanent garbage with no defined removal point. Rejected: dual output (breaks nobody but never ends) and a deprecation-warning period (over-engineered for a documented-contract restoration).
- **D-09: The behavior change MUST be carried into the Phase 23 CHANGELOG `[0.6.2]` entry** as a user-visible output-filename change, not buried as an internal fix — users with CI referencing `build/pdf/index.pdf` need to see it. This is a hand-off obligation to Phase 23, not extra work here.

**Verification (GATE-01)**
- **D-10: The gate is a real-compile test driven by `tests/roots/test-basic`,** which already declares `("index", "output.typ", …)`. Run `-b typstpdf` against it and assert `output.typ` and `output.pdf` exist with valid `%PDF` magic — and, to make the assert genuinely fail pre-fix, additionally assert `index.typ` / `index.pdf` are **absent**. Pre-fix the builder emits `index.*` and no `output.*`, so both halves fail. Rejected: a brand-new dedicated `tests/fixtures/` render-gate project (duplicates a root that already exercises the exact condition).
- **D-11: Existing tests that assert `index.typ` against `test-basic` must be updated to `output.typ`, not worked around.** They encode the buggy behavior; updating them is part of the fix. The planner must enumerate them (they are the `tests/roots/test-basic`-consuming subset, NOT all 238 `index.typ` occurrences) and confirm the 60 target==docname fixtures stay untouched.
- **D-12: `docs/source/conf.py` output moves to `typsphinx.typ` / `typsphinx.pdf`** — verify `tox -e docs-pdf` and the full-corpus gate (`tests/test_corpus_gate.py`) still pass, updating any hardcoded `index.typ` / `index.pdf` path in the docs-build or corpus-gate machinery. This is a required part of the phase, not a follow-up.

### Claude's Discretion
- **Where the name-derivation lives** — a small shared helper on `TypstBuilder` (e.g. resolving docname → output stem via a `typst_documents` lookup) reused by `TypstBuilder.write_doc`, `TypstPDFBuilder.write_doc`, and `TypstPDFBuilder.finish` is the obvious shape, but the planner settles the exact factoring. The invariant is that all three sites agree, so `finish()` can never look for a `.typ` the write path did not produce.
- **Unit tests for the normalization rule** — the compile gate (D-10) is the required floor; adding table-driven unit tests for the D-03/D-04/D-06 stem cases (extension present/absent, period-bearing stem, path separator) is allowed and encouraged, but not mandated.
- **Duplicate / colliding target names** (two entries resolving to the same output file, or a target colliding with an included child's `docname.typ`) — not raised in discussion and not present in the corpus. Planner may add a defensive warning if it costs nothing; do not build validation machinery for it.

### Deferred Ideas (OUT OF SCOPE)
- **`get_target_uri()` semantics for renamed masters** — if cross-document link resolution turns out not to depend on it, leave it docname-based and note the reasoning; a deliberate redesign of Typst-side cross-document URIs is out of scope here. **RESOLVED by this research — see "Research Question 1" below: it depends on `get_target_uri()` as an internal round-trip identity, and MUST stay docname-based. Do not touch `builder.py:142-153`.**
- **Duplicate / colliding target-name validation** — no corpus case exists; a defensive warning is optional, validation machinery is deferred.
- **Interpreting the target name as an outdir-relative path** (`'sub/manual.typ'` placing the file under `outdir/sub/`) — rejected (D-06). Revisit only alongside a real solution to relative include/image path recomputation.
- **Master-output layout + the `-b typst` / `-b typstpdf` root mismatch + dead `typst_output_dir`** — captured in full at `.planning/todos/pending/2026-07-21-master-output-layout-and-dead-typst-output-dir.md`. Owner's call (2026-07-21): not in Phase 22. D-05 stands.
- **Backlog 999.3/999.4 (`typst_package` path broken end-to-end)** — separate backlog item, separate surface, not this phase.
- **Read the Docs hosting migration** — unrelated docs-infrastructure todo.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PDF-01 | `sphinx-build -b typstpdf` names the compiled PDF after the `typst_documents` target name (`manual.pdf`), not the source docname (`index.pdf`); `TypstPDFBuilder.finish()` derives the output name from the target tuple. Per D-01, this phase widens delivery to the `.typ` filename too (a strict superset of the written requirement). | Architecture Patterns (shared-helper factoring across the 3 write sites), Common Pitfalls (get_target_uri trap, corpus-gate gap), Code Examples (exact current code at each site), Validation Architecture (GATE-01 shape + the newly-found corpus-gate assertion that must also move) |
</phase_requirements>

## Summary

CONTEXT.md already measured the root cause precisely (three write/read sites in `builder.py`, all
docname-based; `doc_tuple[1]` read nowhere) and locked the normalization rule (D-01..D-12). This
research answers the five questions CONTEXT.md explicitly left open for the planner, all via direct
codebase/Sphinx-source measurement:

1. **`get_target_uri()` must NOT change.** It has exactly one consumer in this codebase
   (`translator.py:3279`, inside `_resolve_xref_docname`), which uses it as a **round-trip
   identity** to recover a cross-referenced document's DOCNAME from a Sphinx-computed `refuri`.
   Sphinx itself computes that `refuri` via `Builder.get_relative_uri(from_, to)` →
   `relative_uri(get_target_uri(from_), get_target_uri(to))` (verified by reading
   `sphinx/builders/__init__.py` and `sphinx/util/nodes.py:make_refnode` in the installed Sphinx
   9.x). Because typsphinx's own label namespacing (`_namespace_label`, `translator.py:3202`) is
   **permanently keyed on source docname** — never on the output filename — changing
   `get_target_uri()` to reflect a renamed master's target name would desynchronize the recovered
   "docname" from the actual label namespace, breaking every cross-document link into or out of a
   renamed master with a Typst `"label ... does not exist"` compile fatal. Leave
   `builder.py:142-153` byte-unchanged.

2. **Exact D-11 test-surface enumeration, done.** Of the 5 modules CONTEXT.md named plus a
   corpus-wide sweep of every `typst_documents = [...]` literal in the repo: **none of the 5 named
   modules actually consume `tests/roots/test-basic`.** They all construct their own conf.py
   (inline string or `temp_sphinx_app`'s empty-config fixture) with either no `typst_documents` at
   all or an identity mapping (`target-stem == docname`). D-11's premise ("determine which
   modules consume test-basic") resolves to **zero** — no existing unit-test module needs an
   assertion update. The `output.typ`/`output.pdf` assertions land entirely in the **new** GATE-01
   test (D-10), which is the only consumer of `test-basic` for this behavior.

3. **A THIRD blast-radius entry, not in CONTEXT.md's table, found by code sweep:**
   `tests/test_corpus_gate.py` dynamically writes `typst_documents = [('index', 'sphinx-corpus',
   …)]` into a cloned Sphinx `doc/` tree (`wire_typsphinx_into_corpus_conf`), then asserts
   `outdir / "index.pdf"` — this is presently PASSING BY BUG (its own comment says so: "docname-based
   naming (builder.py:544/560), never the typst_documents 'target' field"). After this phase's fix
   the compiled file moves to `sphinx-corpus.pdf`, and this assertion (line 330) will break unless
   updated. This was invisible to a static grep for `typst_documents = \[` in `.py`/`conf.py`
   files because it is embedded as an f-string write inside a Python function, not a literal
   config assignment — flagging it explicitly here.

4. **`docs/source/conf.py`'s CI/build machinery is already glob-safe** — `tox -e docs-pdf` just
   runs `sphinx-build -b typstpdf source _build/pdf` (no filename assumption), and
   `.github/workflows/docs.yml` copies/uploads/releases via `docs/_build/pdf/*.pdf` globs
   throughout. **No CI change needed.** The real D-12 surface is narrower than "CI machinery": it
   is `tests/test_corpus_gate.py` (item 3 above) plus one stale prose example in
   `docs/source/user_guide/builders.rst` (a self-contradictory doc example found during this
   research — see Common Pitfalls).

5. **The three write/read sites and the GATE-01 fixture shape are confirmed verbatim** against
   current `builder.py` (lines 329, 646, 703-725) and `tests/test_desc_signature_concat_render_gate.py`
   respectively — see Code Examples.

**Primary recommendation:** Add one private helper, `TypstBuilder._resolve_output_stem(docname) ->
str`, that looks up `docname` in `self.config.typst_documents`, applies D-03/D-04/D-06/D-07
normalization, and falls back to `docname` itself when no entry matches (D-02). Call it from all
three write/read sites (`TypstBuilder.write_doc`, `TypstPDFBuilder.write_doc`,
`TypstPDFBuilder.finish`). Do not touch `get_target_uri()`. Update
`tests/test_corpus_gate.py::TestCorpusRenderGate.test_corpus_compiles_with_no_fatal_error` (assert
`sphinx-corpus.pdf`, not `index.pdf`) as a required D-12 companion change alongside the
`docs/source/conf.py` verification.

## Architectural Responsibility Map

This is a Sphinx builder extension, not a client/server web app — "tiers" below are adapted to the
translate → build → verify pipeline this codebase actually has.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Output-filename derivation (docname → target stem) | Builder (write/finish path, `builder.py`) | — | The only place a `typst_documents` target is a candidate write-path input; translator and writer never see it |
| Cross-document link/label resolution | Translator (`translator.py`) | Builder (`get_target_uri`, read-only, unchanged) | Labels are namespaced by SOURCE DOCNAME, permanently — filename renames must NOT leak into this layer |
| Master-vs-included branching | Writer (`writer.py:_is_master_document`) | — | Keyed on `doc_tuple[0]` (docname), by design (D-02); must stay untouched |
| PDF compilation (content → bytes) | `pdf.py` (`compile_typst_to_pdf`) | — | Filename-agnostic (`content`, `root_dir` only); confirmed no change needed |
| Regression verification | Tests (`tests/roots/test-basic` + new GATE-01 test) | Docs build (`docs/source/conf.py` via `tox -e docs-pdf`) | Both are consumers of the fix, not implementers of it |

## Standard Stack

No new dependencies. This phase is a same-file (`typsphinx/builder.py`) internal refactor plus a
new pytest module; it uses only the stdlib (`os.path`, `pathlib`) already imported in `builder.py`,
and the existing test stack (`pytest`, `sphinx.testing`, `typst` via `typst-py`, already declared).

**Installation:** none required.

**Version verification:** N/A — no packages added or bumped. Milestone invariant (zero new
runtime deps, no `@preview` bump) holds trivially since every edit lands in `builder.py` and
`tests/`.

## Package Legitimacy Audit

**Not applicable.** This phase installs zero new packages (confirmed: D-01..D-12 scope every edit
to `typsphinx/builder.py` plus test/doc consumer updates; no `pyproject.toml` dependency edit is
in scope). The Package Legitimacy Gate is skipped.

## Architecture Patterns

### System Flow (write-path only; unaffected stages omitted)

```
sphinx-build -b typst|typstpdf
        │
        ▼
Builder.write()  (builder.py:171)
        │  loops docnames, calls write_doc(docname, doctree) per doc
        ▼
TypstBuilder.write_doc / TypstPDFBuilder.write_doc
        │
        ├─► [NEW] self._resolve_output_stem(docname)
        │        │
        │        ├─ docname found in self.config.typst_documents? ──yes──► normalize target
        │        │        (strip trailing ".typ" only; guard path-bearing names -> basename + warn)
        │        │
        │        └─ not found (included child, D-02) ─────────────────────► stem = docname
        │
        ▼
destination = outdir / (stem + out_suffix)   <- was: outdir / (docname + out_suffix)
        │
        ▼
writer.translate() -> write .typ content to `destination`
        (TypstPDFBuilder additionally writes only .typ here; .pdf comes later)

TypstPDFBuilder.finish()  (builder.py:675)
        │  loops self.config.typst_documents entries (doc_tuple)
        ▼
        stem = self._resolve_output_stem(doc_tuple[0])   <- SAME helper, same result as write_doc
        │
        ├─► typ_file = outdir / (stem + ".typ")   <- read back what write_doc actually wrote
        ├─► compile_typst_to_pdf(content, root_dir=outdir)   <- pdf.py, unchanged, filename-agnostic
        └─► pdf_file = outdir / (stem + ".pdf")   <- write

--- UNCHANGED, must not be touched ---
get_target_uri(docname) = docname + out_suffix   (builder.py:142)
        │  consumed ONLY by translator.py:3279 (_resolve_xref_docname), a pure math
        │  round-trip against Sphinx's own refuri computation -- see Common Pitfalls #1.
        ▼
_namespace_label(docname, id)   (translator.py:3202) -- ALWAYS keyed on source docname,
        never on output filename, for every label definition and reference in the corpus.
```

### Recommended Factoring

```
typsphinx/
└── builder.py
    ├── class TypstBuilder
    │   ├── _resolve_output_stem(self, docname: str) -> str   # NEW, shared helper
    │   ├── write_doc(...)                                     # calls the helper
    │   └── get_target_uri(...)                                # UNCHANGED
    └── class TypstPDFBuilder(TypstBuilder)
        ├── write_doc(...)                                     # calls the (inherited) helper
        └── finish(...)                                        # calls the helper for BOTH
                                                                 # the .typ read-back and the
                                                                 # .pdf write, from the same call
```

Putting `_resolve_output_stem` on `TypstBuilder` (not `TypstPDFBuilder`) means `TypstBuilder`'s own
`write_doc` (the plain `-b typst` builder) and `TypstPDFBuilder`'s `write_doc`/`finish` (via
inheritance) all call the identical method — the "cannot look for a `.typ` the write path did not
produce" invariant CONTEXT.md's `<code_context>` names is enforced by construction (one function,
three call sites, no duplicated normalization logic to drift apart).

### Pattern: Guarded normalization (D-03/D-04/D-06/D-07)

```python
# Source: this repository, typsphinx/builder.py (existing code) +
# CONTEXT.md D-03/D-04/D-06/D-07 (locked decisions this pattern must satisfy)
import os

def _resolve_output_stem(self, docname: str) -> str:
    typst_documents = getattr(self.config, "typst_documents", []) or []
    target = None
    for doc_tuple in typst_documents:
        if doc_tuple and doc_tuple[0] == docname:
            target = doc_tuple[1]
            break
    if target is None:
        # D-02: no typst_documents entry (included child) -> unchanged behavior.
        return docname

    # D-03/D-04: strip ONLY a literal trailing ".typ"; os.path.splitext is
    # explicitly forbidden (would mangle "v1.2-manual" -> "v1").
    stem = target[:-4] if target.endswith(".typ") else target

    # D-06/D-07: guard path-bearing target names (portable separator + traversal
    # + absolute/drive-qualified detection) -- warn, then reduce to the basename.
    has_separator = "/" in stem or (os.sep in stem) or (
        os.altsep is not None and os.altsep in stem
    )
    is_traversal_or_absolute = (
        ".." in stem.split("/") or os.path.isabs(stem)
        # a Windows drive-qualified relative form (e.g. "C:manual") is also
        # caught by os.path.isabs on Windows; os.sep/os.altsep splitting
        # above already catches "sub\\manual" on every platform.
    )
    if has_separator or is_traversal_or_absolute:
        basename = os.path.basename(stem.replace("\\", "/"))
        logger.warning(
            f"a path is not supported in a typst_documents target name "
            f"({target!r}); emitting {basename}.typ / {basename}.pdf "
            f"next to the source document instead"
        )
        stem = basename

    return stem
```

This is illustrative of the shape the locked decisions require, not a final implementation the
planner must copy verbatim — the planner/executor should verify edge cases (e.g. an empty stem
after stripping) against the project's own test style.

### Anti-Patterns to Avoid
- **Do not change `get_target_uri()`.** It is tempting to "fix" it symmetrically with the write
  path, but it is a pure internal identity consumed by `_resolve_xref_docname`'s round-trip math —
  changing it desyncs the recovered docname from `_namespace_label`'s docname-keyed namespace and
  breaks cross-document links into/out of any renamed master. See Common Pitfalls #1.
- **Do not use `os.path.splitext()` for stem extraction** — explicitly rejected by D-04 (mangles
  period-bearing stems like `v1.2-manual`).
- **Do not duplicate the normalization logic** across the three call sites — `finish()` reading
  back a `.typ` file that `write_doc()` named differently (because the two sites computed the stem
  independently and drifted) is exactly the failure mode CONTEXT.md's `<code_context>` warns
  against ("the invariant is that all three sites agree").

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Stripping a known suffix from a filename | A general "parse any extension" helper (`os.path.splitext`) | A literal `str.endswith(".typ")` + slice (as required by D-03/D-04) | The general case actively breaks on period-bearing stems; this problem has exactly one known suffix to strip (`.typ`), so the general tool is the wrong tool |
| Detecting a path-bearing string portably | Manual `if "/" in x` only | `os.sep`/`os.altsep` + explicit `..`/absolute checks per D-07 | `os.path.basename` alone silently passes through backslash-separated Windows paths and `..` traversal on POSIX; D-07 already enumerates the exact checks needed — don't re-derive them ad hoc |

**Key insight:** this phase is deliberately narrow (four D-locked normalization rules, one shared
helper, three call sites) — resist the urge to generalize the target-name resolution into a
broader "output path planner" abstraction; D-05's known-limitation note and the deferred
master-output-layout item confirm that broader problem is explicitly out of scope here.

## Common Pitfalls

### Pitfall 1: "Fixing" `get_target_uri()` in sympathy with the write-path rename
**What goes wrong:** A developer sees `get_target_uri()` still returns `docname + self.out_suffix`
after the write path has been changed to honor the target name, assumes this is an oversight, and
"completes" the fix by making `get_target_uri()` target-name-aware too.
**Why it happens:** `get_target_uri()` LOOKS like exactly the kind of code this phase should touch
(it computes an output-adjacent URI from a docname) — CONTEXT.md itself flags it as an open
question, inviting a "just fix it too" instinct.
**How to avoid:** `get_target_uri()` has one consumer (`translator.py:3279`), used purely as a
round-trip identity to recover a DOCNAME from a Sphinx-internal `refuri` (Sphinx computes that
refuri via `get_relative_uri(from_, to)` = `relative_uri(get_target_uri(from_),
get_target_uri(to))` — both endpoints go through the SAME function). Since every label definition
and reference in the translator is namespaced by DOCNAME (`_namespace_label`, never by output
filename), changing `get_target_uri()`'s docname-to-target mapping desynchronizes the recovered
value from the label namespace. Concretely: a cross-reference INTO or OUT OF a renamed master
would resolve to a label like `<manual:some-anchor>` when the actual emitted label is
`<index:some-anchor>` (still docname-keyed) — Typst then fails to compile with `"label
<manual:some-anchor> does not exist"`. Leave `builder.py:142-153` byte-unchanged.
**Warning signs:** Any diff touching `get_target_uri()`; any new test asserting `get_target_uri()`
returns a target-name-based string; a corpus-gate or GATE-01 fatal reading `"label ... does not
exist"` after an otherwise-correct-looking filename fix.

### Pitfall 2: Trusting CONTEXT.md's 2-entry blast-radius table as exhaustive
**What goes wrong:** Treating `tests/roots/test-basic/conf.py` and `docs/source/conf.py` as the
ONLY two `target != docname` corpus entries (per CONTEXT.md's `<domain>` table) and shipping
without touching `tests/test_corpus_gate.py`.
**Why it happens:** CONTEXT.md's measurement was (reasonably) a static grep for `typst_documents =
[...]` literals across `.py`/`conf.py` files. `tests/test_corpus_gate.py`'s entry
(`typst_documents = [('index', 'sphinx-corpus', …)]`) is constructed dynamically inside
`wire_typsphinx_into_corpus_conf()` as an f-string appended to a cloned corpus's `conf.py` at test
runtime — a static grep for the assignment pattern in the typsphinx repo's own files still finds
the *string literal* (it's grep-able, confirmed above), but the test's own PDF-path assertion
(`outdir / "index.pdf"`, line 330) is the thing that actually breaks, and it's easy to miss because
this test is `@pytest.mark.slow` and network-dependent (skipped without network / outside the
`tests/roots` sweep most contributors mentally run).
**How to avoid:** Update `tests/test_corpus_gate.py::TestCorpusRenderGate.test_corpus_compiles_with_no_fatal_error`
line 330 from `outdir / "index.pdf"` to `outdir / "sphinx-corpus.pdf"` (and update its own inline
comment at lines 324-326, which currently documents the pre-fix docname-based behavior as
intentional — it will be stale and misleading post-fix). Run this test locally with network access
before considering D-12 satisfied; it is not covered by the fast test suite.
**Warning signs:** `pytest -m slow` (or a direct `pytest tests/test_corpus_gate.py -k
TestCorpusRenderGate`, with network + `~/.cache/typsphinx-corpus-gate` populated) failing after
the fix lands with "No index.pdf produced" even though the build actually succeeded and produced
`sphinx-corpus.pdf`.

### Pitfall 3: Assuming the 5 CONTEXT.md-named test modules need assertion updates
**What goes wrong:** Pre-emptively editing `tests/test_builder.py`,
`tests/test_builder_requirement13.py`, `tests/test_integration_nested_toctree.py`,
`tests/test_config_template_mapping.py`, `tests/test_config_toctree_defaults.py` to expect a
different filename, because CONTEXT.md's D-11 names them as "the `index.typ`-asserting modules"
requiring investigation.
**Why it happens:** D-11's wording ("must be updated to `output.typ`, not worked around") reads as
an instruction to edit these files; it is actually an instruction to *investigate and update only
the subset that turns out to need it*.
**How to avoid:** This research already did the investigation (see Summary #2): none of these 5
modules use `tests/roots/test-basic`. Each builds its own `conf.py` (inline string or
`temp_sphinx_app`'s fixture) with either no `typst_documents` at all, or `typst_documents =
[('index', 'index', ...)]` (identity mapping). Under the new normalization rule, an identity
mapping strips to stem `"index"` — byte-identical to today's docname-based output. **These 5
modules require zero test-assertion changes.** Confirm this with `pytest
tests/test_builder.py tests/test_builder_requirement13.py tests/test_integration_nested_toctree.py
tests/test_config_template_mapping.py tests/test_config_toctree_defaults.py` staying green,
unmodified, after the fix — a red result here means the fix's D-02 "no entry -> docname" fallback
or identity-mapping normalization has a bug, not that these tests were wrong.

### Pitfall 4: The stale `docs/source/user_guide/builders.rst` example (found during this research, not in CONTEXT.md)
**What goes wrong:** `docs/source/user_guide/builders.rst:106-112` documents a
`typst_documents` example with `("index", "main", …)` and `("api", "api-ref", …)`, but the same
page's nearby CLI walkthroughs (lines 61, 147, 161) hardcode `index.typ`/`index.pdf` as if the
example config were never applied — a self-contradiction that is currently invisible because the
pre-fix bug makes `index.pdf` the ACTUAL output regardless of the documented target name. After
this fix, a user following that exact example would find `main.pdf`, not `index.pdf`, making the
walkthrough text actively wrong.
**Why it happens:** The page was written before Issue #117 was known/fixed; the target-name
example and the manual-compile walkthrough were never cross-checked against real builder output.
**How to avoid:** Not a locked decision (CONTEXT.md's `<canonical_refs>` cites only
`docs/configuration.rst:38-60` as the "published contract"), so this is a planner judgment call,
not a mandate. Recommend a small doc-hygiene pass on `docs/source/user_guide/builders.rst` lines
61/147/161 to either (a) match the target-name example's actual output names, or (b) drop the
target-name example in favor of the default identity mapping the walkthrough already assumes. Flag
for the planner rather than silently expanding phase scope.
**Warning signs:** A user issue reporting "the docs say my PDF should be named X but I got Y" after
v0.6.2 ships.

## Code Examples

### The three write/read sites, exact current state (verified against `builder.py` on this branch)

```python
# Source: typsphinx/builder.py:329 -- TypstBuilder.write_doc (the `typst` builder)
destination = path.join(self.outdir, docname + self.out_suffix)

# Source: typsphinx/builder.py:646 -- TypstPDFBuilder.write_doc (the `typstpdf` builder, .typ half)
typ_destination = path.join(self.outdir, docname + ".typ")

# Source: typsphinx/builder.py:703-725 -- TypstPDFBuilder.finish (the `typstpdf` builder, .pdf half)
for doc_tuple in typst_documents:
    # doc_tuple format: (sourcename, targetname, title, author)
    docname = doc_tuple[0]                                    # [1] (targetname) is read NOWHERE
    typ_file = path.join(self.outdir, docname + ".typ")       # <-- read-back site
    ...
    pdf_bytes = compile_typst_to_pdf(typst_content, root_dir=self.outdir)
    pdf_file = path.join(self.outdir, docname + ".pdf")       # <-- write site
```

```python
# Source: typsphinx/builder.py:142-153 -- get_target_uri, UNCHANGED by this phase
def get_target_uri(self, docname: str, typ: str | None = None) -> str:
    return docname + self.out_suffix
```

### The single consumer of `get_target_uri()`, and why it must stay docname-based

```python
# Source: typsphinx/translator.py:3240-3283 -- _resolve_xref_docname (verified verbatim)
def _resolve_xref_docname(self, refuri: str) -> Tuple[str, str] | None:
    ...
    current = self._current_docname()
    ...
    current_uri = self.builder.get_target_uri(current)   # <-- the ONLY call site in the repo
    base_dir = posixpath.dirname(current_uri)
    target_uri = posixpath.normpath(posixpath.join(base_dir, path_part))
    target_docname = target_uri[: -len(suffix)]           # recovered docname, used to namespace
    return target_docname, anchor                          # the label: _namespace_label(target_docname, anchor)
```

```python
# Source: installed Sphinx 9.x, sphinx/builders/__init__.py -- Builder.get_relative_uri
# (confirms refuri is computed by Sphinx via get_target_uri on BOTH endpoints)
def get_relative_uri(self, from_: str, to: str, typ: str | None = None) -> str:
    return relative_uri(
        self.get_target_uri(from_),
        self.get_target_uri(to, typ),
    )

# Source: installed Sphinx 9.x, sphinx/util/nodes.py -- make_refnode
# (confirms this is how domains build the `reference` node's refuri that
# _resolve_xref_docname above later parses)
node['refuri'] = builder.get_relative_uri(fromdocname, todocname) + '#' + targetid
```

```python
# Source: typsphinx/translator.py:3202 -- _namespace_label, confirms labels are ALWAYS
# keyed on source docname, never on output filename (why get_target_uri's VALUE doesn't
# need to match the real output name -- only its ROUND-TRIP CONSISTENCY matters)
def _namespace_label(self, docname: str | None, raw_id: str) -> str:
    """... every DEFINITION site prefixes the SOURCE docname; every REFERENCE site
    recomputes the SAME namespace from its target's docname ..."""
```

### GATE-01 fixture shape to follow verbatim (from `tests/test_desc_signature_concat_render_gate.py`)

```python
# Source: tests/test_desc_signature_concat_render_gate.py (existing pattern, reused for D-10)
def _run_sphinx_build_typstpdf(source_dir: Path, build_dir: Path) -> subprocess.CompletedProcess:
    """Invoked as `sys.executable -m sphinx` (never `uv run sphinx-build`) so the
    exact interpreter/venv running this test is reused, sidestepping the documented
    NixOS-sandbox PATH-shadowing hazard."""
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf", str(source_dir), str(build_dir)],
        capture_output=True, text=True,
    )

# ... build, then:
assert result.returncode == 0, ...
pdf_output = temp_build_dir / "index.pdf"     # <-- for GATE-01, this becomes "output.pdf"
assert pdf_output.exists(), ...
assert pdf_output.stat().st_size > 0, "PDF file is empty"
with open(pdf_output, "rb") as f:
    magic = f.read(4)
    assert magic == b"%PDF", "Generated file is not a valid PDF"
```

For D-10, point `source_dir` at `tests/roots/test-basic` (already declares `("index", "output.typ",
…)` at `conf.py:12-14`), and additionally assert `(temp_build_dir / "index.typ").exists() is
False` and `(temp_build_dir / "index.pdf").exists() is False` — CONTEXT.md's explicit "fails
against the pre-fix builder on both counts" requirement (D-10).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml` `[tool.pytest.ini_options]`) |
| Config file | `pyproject.toml` (existing — no Wave 0 gap) |
| Quick run command | `uv run pytest tests/test_builder.py tests/test_config.py -q` |
| Full suite command | `uv run pytest` (excludes nothing by default; `pytest -m "not slow"` skips the network-dependent corpus gate) |

Per CLAUDE.md's worktree-isolation mandate, every command above runs via `uv run` inside the
executor's own worktree (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` first).

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PDF-01 | `sphinx-build -b typstpdf` against `typst_documents = [('index', 'output.typ', …)]` emits `output.typ`+`output.pdf`, NOT `index.typ`/`index.pdf` | integration (real `typst.compile()`) | `uv run pytest tests/test_<new-gate-name>.py -q` (real-compile, D-10 shape above, driven by `tests/roots/test-basic`) | ❌ Wave 0 — new GATE-01 module needed |
| PDF-01 (regression guard) | The 5 CONTEXT.md-named modules + the 60-entry identity-mapping fixture corpus stay byte-identical | unit/integration (existing) | `uv run pytest tests/test_builder.py tests/test_builder_requirement13.py tests/test_integration_nested_toctree.py tests/test_config_template_mapping.py tests/test_config_toctree_defaults.py -q` | ✅ existing, unmodified |
| D-12 | `docs/source/conf.py`'s own dogfood build emits `typsphinx.typ`/`typsphinx.pdf` | integration (real docs build) | `tox -e docs-pdf` (from repo root; or `cd docs && uv run sphinx-build -b typstpdf source _build/pdf`) | ✅ existing tox env, no new file |
| D-12 (corpus-gate companion, found in this research) | `tests/test_corpus_gate.py` GATE-02 assertion moves from `index.pdf` to `sphinx-corpus.pdf` | integration (slow, network) | `uv run pytest tests/test_corpus_gate.py -k TestCorpusRenderGate -m slow -q` | ✅ existing file — **1-line assertion edit required, see Common Pitfalls #2** |
| get_target_uri non-regression | Cross-document references into/out of a renamed master still resolve (no `"label ... does not exist"` fatal) | integration (real `typst.compile()`) | Cover via a `typst_documents` entry with `target != docname` AND a cross-doc `:ref:`/`:doc:` in the same GATE-01 fixture, or a dedicated small fixture — planner's call | ❌ Wave 0 — not covered by any existing fixture (all current `target != docname` fixtures are single-document, no cross-reference exercised) |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_builder.py tests/test_<new-gate-name>.py -q`
- **Per wave merge:** `uv run pytest -m "not slow"` (fast suite, includes the new GATE-01 module and the 5 named regression modules; excludes the network-dependent corpus gate)
- **Phase gate:** `uv run pytest` (full suite including `-m slow` corpus gate, network required) + `tox -e docs-pdf` green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] New test module (name TBD by planner, e.g. `tests/test_target_name_render_gate.py`) — covers PDF-01 per the D-10 gate shape (Code Examples section above), driven by `tests/roots/test-basic`
- [ ] Cross-document-reference-into-renamed-master fixture — no existing fixture exercises `target != docname` together with a cross-doc reference; needed to give the `get_target_uri` non-regression claim (Common Pitfalls #1) an automated, real-compile proof rather than resting on code-reading alone
- [ ] `tests/test_corpus_gate.py` line-330 assertion update (`index.pdf` → `sphinx-corpus.pdf`) — not a new file, but a required edit surfaced by this research, easy to miss because the test is `@pytest.mark.slow`

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| — | (none) | — | Every claim in this document was verified directly against this repository's source (`builder.py`, `writer.py`, `translator.py`, `tests/`, `docs/`, `tox.ini`, `.github/workflows/docs.yml`) or the installed Sphinx 9.x package source in `.venv/lib/python3.13/site-packages/sphinx/`. No `[ASSUMED]` claims. |

**This table is empty:** All claims in this research were verified by direct tool/code
inspection — no user confirmation needed.

## Open Questions

1. **Should `docs/source/user_guide/builders.rst` be corrected in this phase or a follow-up?**
   - What we know: it contains a self-contradictory example (Common Pitfalls #4) that becomes
     actively misleading, not just inaccurate, once this fix ships.
   - What's unclear: CONTEXT.md's canonical-refs only names `docs/configuration.rst` as the
     contract this phase restores; `builders.rst` wasn't in scope during discussion.
   - Recommendation: small, low-risk addition to this phase's task list (3-line prose fix); if the
     planner prefers to keep the phase strictly to `builder.py` + tests, defer to a docs-hygiene
     quick-task instead — either is defensible, flagging for a decision rather than assuming.

2. **Should the cross-document-reference-into-renamed-master case get its own fixture, or is
   code-level reasoning (Pitfall 1) sufficient proof?**
   - What we know: the `get_target_uri()` round-trip argument is airtight by direct source reading
     (Sphinx's `make_refnode`/`get_relative_uri` + typsphinx's `_resolve_xref_docname` +
     `_namespace_label`), and D-02/D-05 mean the common case (a renamed master, referenced FROM one
     of its own toctree children) is exercised by every multi-doc fixture already in the corpus
     (e.g. `tests/fixtures/integration_nested_toctree`) as long as its `typst_documents` gets a
     `target != docname` entry added.
   - What's unclear: whether "reasoning proof" meets this project's GATE-01 standing bar ("every
     node-handler change ships or extends a real `typst.compile()` regression fixture" — Phase 22
     is a builder change, not a node-handler change, but the spirit likely still applies to a
     cross-reference-affecting change).
   - Recommendation: cheapest option is extending an EXISTING multi-doc fixture's `conf.py`
     (e.g. one of the `integration_*` fixtures) to use a non-identity target name rather than
     building a new one — this exercises the real round-trip with near-zero new fixture cost.

## Sources

### Primary (HIGH confidence — direct repository/installed-package inspection)
- `typsphinx/builder.py` (this repo, current branch) — the three write/read sites, `get_target_uri`, `finish()`
- `typsphinx/writer.py` (this repo) — `_is_master_document`, confirming D-02's docname-keyed branch
- `typsphinx/translator.py` (this repo) — `_resolve_xref_docname` (:3240), `_namespace_label` (:3202), `visit_reference` (:3446)
- `.venv/lib/python3.13/site-packages/sphinx/builders/__init__.py` — `Builder.get_relative_uri` (installed Sphinx 9.x, matches `pyproject.toml`'s `sphinx>=9.1,<10` pin)
- `.venv/lib/python3.13/site-packages/sphinx/util/nodes.py` — `make_refnode`
- `tests/conftest.py`, `tests/test_builder.py`, `tests/test_builder_requirement13.py`, `tests/test_integration_nested_toctree.py`, `tests/test_config_template_mapping.py`, `tests/test_config_toctree_defaults.py`, `tests/test_config.py`, `tests/test_pdf_generation.py`, `tests/test_corpus_gate.py`, `tests/test_desc_signature_concat_render_gate.py` — full-text read + grep sweep for `typst_documents` literals and `index.typ`/`index.pdf` assertions
- `tests/fixtures/integration_*/conf.py`, `tests/roots/test-basic/conf.py`, `docs/source/conf.py` — every `typst_documents` entry in the corpus, individually checked for target==docname vs. target!=docname
- `tox.ini`, `.github/workflows/docs.yml` — docs-build/CI filename-hardcoding sweep (none found beyond globs)
- `docs/source/quickstart.rst`, `docs/source/user_guide/builders.rst`, `docs/source/changelog.rst` — prose sweep for `index.typ`/`index.pdf` references

### Secondary (MEDIUM confidence)
- none — no external/web sources were consulted (research_focus explicitly deprioritized web
  research in favor of codebase measurement, and no gap required it)

### Tertiary (LOW confidence)
- none

## Metadata

**Confidence breakdown:**
- Standard stack: N/A — no new stack (no packages added)
- Architecture (write-site factoring, get_target_uri conclusion): HIGH — verified against this repo's source and the installed Sphinx package source, not training-data recollection
- Test-surface enumeration (D-11/D-12): HIGH — every `typst_documents` literal in the repo was mechanically swept and individually classified target==docname vs. target!=docname
- Pitfalls: HIGH — each pitfall traces to a specific file:line measurement, not a hypothesized failure mode

**Research date:** 2026-07-21
**Valid until:** Stable until `typsphinx/builder.py`, `typsphinx/translator.py`, or the installed
Sphinx major version changes — no external time-based decay (internal-code research, not
ecosystem/library research). Re-verify the `get_target_uri()` consumer count if Sphinx's pin in
`pyproject.toml` (`sphinx>=9.1,<10`) is ever widened past `<10`.
