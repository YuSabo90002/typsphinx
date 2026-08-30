# Phase 62: The `visit_image()` Separator Fix and Its Real-Compile Gate - Pattern Map

**Mapped:** 2026-08-30
**Files analyzed:** 4 (1 modified product file, 1 test module, 1 fixture directory bundle, 1 goldens sub-bundle)
**Analogs found:** 4 / 4 (all strong matches; one structural delta documented, no "no analog" file)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `typsphinx/translator.py` (`visit_image`/`depart_image`, non-`in_figure` branches only, `:4718-4783`) | translator emitter method | transform (docutils node → Typst text stream) | `typsphinx/translator.py` `visit_Text` (`:1775-1846`, specifically the `in_signature_text` triad at `:1826-1846`) — same-file, same-class sibling method | exact (same class, same triad mechanism, same file) |
| `tests/test_inline_image_separator_render_gate.py` | test (real-compile regression gate) | request-response (subprocess `sphinx-build` invocation → assert on stdout/stderr/filesystem) | `tests/test_paragraph_concat_render_gate.py` (skeleton) + `tests/test_abbr_pep_separator_render_gate.py` (multi-shape FAIL+PASS pairing) + `tests/test_desc_rubric_decoupling_render_gate.py` (golden-comparison leg) | exact for skeleton; role-match extension for the 18-master aggregate-error assertion shape (no existing gate has this shape) |
| `tests/fixtures/inline_image_separator_render_gate/` (conf.py + 26 `.rst` docs) | test fixture / config | CRUD (static Sphinx project, no runtime data flow) | `tests/fixtures/state_guard_three_master_gate/` (multi-master shape) | role-match (closest structural analog, but 3 masters/6 docs vs. this phase's 18 masters/26 docs — 6x scale-up, not a drop-in copy) |
| `tests/fixtures/inline_image_separator_render_gate/goldens/*.typ` (9 files) | test data (golden fixtures) | file-I/O (write-once at RED capture, read-compare at gate run) | `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` | exact (same golden-comparison idiom; that precedent is singular — this phase needs 9 goldens compared per-shape, not 1) |

## Pattern Assignments

### `typsphinx/translator.py` — `visit_image()` / `depart_image()` (non-`in_figure` branches)

**Analog:** `typsphinx/translator.py`, `visit_Text`'s `in_signature_text` branch (`:1826-1846`), which is itself explicitly documented in CONTEXT.md as "the exact triad shape to mirror" — same triad also appears verbatim at `_emit_signature_leaf_wrapper` (`:1775-1788`, quoted in RESEARCH.md's Code Examples).

**Current (pre-fix) state — the exact lines this phase touches** (`typsphinx/translator.py:4728-4756`, read this session):
```python
def visit_image(self, node: nodes.image) -> None:
    if not self.in_figure:
        self._emit_id_anchors(node)          # UNCHANGED — leave this call exactly here

    uri = node.get("uri", "")
    current_docname = getattr(self.builder, "current_docname", None)
    adjusted_uri = self._compute_relative_image_path(uri, current_docname)
    escaped_uri = escape_typst_string(adjusted_uri)

    if self.in_figure:
        self.add_text(f'  image("{escaped_uri}"')   # UNCHANGED branch — do not touch
    else:
        # No # prefix in code mode
        self.add_text(f'image("{escaped_uri}"')      # <- triad goes directly above this line
    ...
    self.add_text(")")

def depart_image(self, node: nodes.image) -> None:
    if not self.in_figure:
        self.add_text("\n\n")   # UNCHANGED text — INSERT the trailing mark ABOVE this line
```

**Canonical triad call shape to mirror verbatim** (`typsphinx/translator.py:1826-1846`, `visit_Text`'s `in_signature_text` branch):
```python
self._add_paragraph_separator()
if not self._emit_inline_concat_separator():
    if self.in_list_item and self.list_item_needs_separator:
        self.add_text("\n")

sig_prefix = "#" if self._in_markup_mode else ""
self.add_text(f'{sig_prefix}raw("{sig_text_content}")')

if not self._mark_inline_concat_content():
    if self.in_list_item:
        self.list_item_needs_separator = True
```

**The three helpers the triad calls** (all pre-existing, none new):
- `_add_paragraph_separator()` (`:933-943`) — emits `"\n"` when `self.in_paragraph and self.paragraph_has_content`, then sets `paragraph_has_content = True`.
- `_emit_inline_concat_separator()` (`:1651-1664`) — checks `self._inline_concat_context()` (desc-parameter / link / term / field-body / attribution); emits `" + "` if that context already holds a sibling; returns `True` iff any such context is active (in which case the caller must NOT also do the list-item newline check).
- `_mark_inline_concat_content()` (`:1666-1676`) — the trailing counterpart: sets the active concat context's has-content flag; returns `True` iff a context is active.

**Insertion point per D-08 (measured, do not reorder):** leave `_emit_id_anchors(node)`'s existing call site completely untouched at the top of `visit_image()`; insert the triad's leading half immediately before `self.add_text(f'image("{escaped_uri}"')` in the `else` branch only, and the trailing half in `depart_image()` immediately before the existing `self.add_text("\n\n")`, also `else`-branch only. RESEARCH.md's own emission probe (byte-identity confirmed) validates this exact placement against all 9 PASS goldens.

**Do not touch:** the `if self.in_figure:` branches in both methods (SC#3). Grep obligations after the edit (repo-wide, per CONTEXT.md's "Specific Ideas"): `endswith("\n")`, `rstrip().endswith`, `[-1:]` must all still return nothing in `typsphinx/translator.py`.

---

### `tests/test_inline_image_separator_render_gate.py`

**Analogs:** `tests/test_paragraph_concat_render_gate.py` (skeleton, reuse verbatim), `tests/test_abbr_pep_separator_render_gate.py` (multi-shape structure), `tests/test_desc_rubric_decoupling_render_gate.py` (golden-comparison leg, exact-string-equality idiom).

**Module-level skip guard + subprocess helper — copy verbatim** (`tests/test_paragraph_concat_render_gate.py:32-79`):
```python
import subprocess
import sys
from pathlib import Path

import pytest

try:
    import typst  # noqa: F401

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


@pytest.fixture
def paragraph_concat_render_gate_dir():
    return Path(__file__).parent / "fixtures" / "paragraph_concat_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``) so
    the exact interpreter/venv running this test is reused, sidestepping the
    documented NixOS-sandbox PATH-shadowing hazard.
    """
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf", str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )


@pytest.mark.skipif(
    not TYPST_AVAILABLE,
    reason="typst-py is required for the inline-image-separator render gate",
)
class TestInlineImageSeparatorRenderGate:
    ...
```
Rename the fixture-dir fixture to `inline_image_separator_render_gate_dir` pointing at `Path(__file__).parent / "fixtures" / "inline_image_separator_render_gate"`.

**Boilerplate returncode/stderr asserts — copy verbatim from either precedent** (e.g. `tests/test_paragraph_concat_render_gate.py:112-121`):
```python
assert result.returncode == 0, (
    f"sphinx-build -b typstpdf failed:\n"
    f"stdout: {result.stdout}\nstderr: {result.stderr}"
)
assert "Typst compilation failed" not in result.stderr, (
    "TypstPDFBuilder.finish() logged a compilation failure:\n"
    f"stderr: {result.stderr}"
)
```
**This exact pair is what MUST be asserted differently for the RED-first FAIL leg** — for the FAIL-shape assertion the gate wants the OPPOSITE (`returncode != 0` and the aggregate error text present) on the unfixed tree, and `returncode == 0` / no failure text only after the fix. Structure the test class with (at minimum) one test method asserting the full green matrix post-fix; RED capture itself is a manual, out-of-pytest choreography (see `62-RED-EVIDENCE.md` pattern below), not a permanently-red assertion baked into the suite.

**PDF magic-byte check — copy verbatim** (`tests/test_paragraph_concat_render_gate.py:153-158`, also present identically in the abbr-pep gate):
```python
assert pdf_output.stat().st_size > 0, "PDF file is empty"
with open(pdf_output, "rb") as f:
    magic = f.read(4)
    assert magic == b"%PDF", "Generated file is not a valid PDF"
```

**Golden-comparison leg — copy structure from `tests/test_desc_rubric_decoupling_render_gate.py:273-318`** (the one existing precedent of a committed `.typ` compared for exact equality against emitted output):
```python
typ_output = temp_build_dir / "index.typ"
assert typ_output.exists(), "index.typ was not emitted"
actual_typ = typ_output.read_text(encoding="utf-8")

golden_path = desc_rubric_decoupling_render_gate_dir / "golden.typ"
golden_typ = golden_path.read_text(encoding="utf-8")

assert actual_typ == golden_typ, (
    "Emitted .typ differs from the committed golden -- byte-identity "
    "requirement is violated:\n"
    + "\n".join(
        difflib.unified_diff(
            golden_typ.splitlines(),
            actual_typ.splitlines(),
            fromfile="golden.typ",
            tofile="actual index.typ",
            lineterm="",
        )
    )
)
```
**Structural delta from this single-golden precedent:** this phase needs 9 goldens, one per PASS shape, so this pattern must be driven in a loop or 9 parametrized cases — `desc_rubric_decoupling_render_gate` compares exactly one `index.typ` against one `golden.typ`; this gate compares 9 distinct content `.typ` outputs (each under `goldens/<pass-shape-name>.typ`) against 9 distinct committed goldens. Per D-07/Pitfall 3 (RESEARCH.md), read BOTH sides via `Path.read_text(encoding="utf-8")` — never `.read_bytes()` — because `builder.py:2072`/`:2139` write with a bare `open(path, "w", encoding="utf-8")` (no `newline=""`), so `windows-latest` CI produces `\r\n` at write time and a binary compare would spuriously fail there. `desc_rubric_decoupling_render_gate`'s own golden comparison already uses `.read_text()` (not bytes) — this is itself supporting precedent, not just RESEARCH.md's reasoning.

**The genuinely new piece — no existing gate has this shape (say so plainly, per instructions):** both `test_paragraph_concat_render_gate.py` and `test_abbr_pep_separator_render_gate.py` compile exactly ONE master per fixture. This gate's fixture (D-01) configures **18** masters compiled in a SINGLE `sphinx-build -b typstpdf` invocation. The exact aggregate-error format to assert against (`typsphinx/builder.py:2638-2642`, read this session):
```python
if failures:
    summary = "; ".join(f"{docname}: {err}" for docname, err in failures)
    raise ExtensionError(
        f"typstpdf: {len(failures)} master document(s) failed: {summary}"
    )
```
The join separator is literally `"; "`; the wrapping message is `"typstpdf: {N} master document(s) failed: {summary}"`. Post-fix, this aggregate error never appears at all (`returncode == 0`, no `"Typst compilation failed"` in stderr — the existing precedent asserts). No existing test asserts against a multi-docname `"; "`-joined `ExtensionError` body; the planner should treat the assertion helper that parses/confirms individual docnames within that joined string as new code, composed only from string operations, not copied from a prior test.

Also new (Pitfall 2, RESEARCH.md): asserting `pass_parent`'s `.pdf` exists on disk is REQUIRED because a successful master is never named in the exception text at all — only logged via `logger.info(f"Generated PDF: {pdf_file}")` (`builder.py:2632`), which the existing precedents' `pdf_output.exists()` + magic-byte pattern already covers verbatim (see above); no new mechanism needed there, just apply the existing check to `pass_parent`'s wrapper output specifically.

---

### `tests/fixtures/inline_image_separator_render_gate/` (conf.py + 26 `.rst` docs)

**Analog:** `tests/fixtures/state_guard_three_master_gate/conf.py` — the closest existing multi-master shape.

**conf.py shape to extend** (`tests/fixtures/state_guard_three_master_gate/conf.py`, read in full):
```python
project = "Three Master Gate"
author = "Probe Author"
release = "1.0.0"
copyright = "2026, Probe Author"

extensions = ["typsphinx"]

root_doc = "m1"

typst_documents = [
    ("m1", "manual1.typ", "Three Master Gate — M1", "Probe Author"),
    ("m2", "manual2.typ", "Three Master Gate — M2", "Probe Author"),
    ("m3", "manual3.typ", "Three Master Gate — M3", "Probe Author"),
]
```
This precedent's directory (`common_a.rst`, `common_b.rst`, `conf.py`, `m1.rst`, `m2.rst`, `m3.rst`, `mid.rst` — 3 masters, 6 documents, with deliberately varied toctree entry orders so a shared child is claimed by a different parent per master) is the shape to extend, not copy: this phase's fixture needs **18** `typst_documents` tuples (`index` + 16 `fail_*` docs, each its own master + `pass_parent`) and **26** `.rst` files (`index.rst`, 16 `fail_NN_*.rst`, `pass_parent.rst` toctree'ing 9 `pass_*.rst` children) — a 6x scale-up in both master count and document count, and a materially different toctree shape (the precedent shares children across masters to test traversal independence; this fixture's masters are almost entirely disjoint one-doc-each, except `pass_parent`'s own 9 children which are NOT shared with any other master). RESEARCH.md's recommended structure (already normative, restated here for the analog cross-reference):
```
tests/fixtures/inline_image_separator_render_gate/
├── conf.py                              # 18-entry typst_documents (D-01)
├── index.rst                            # no-image root master (image-free, SC#1's blast-radius doc)
├── fail_01_sub_mid_sentence.rst  ...  fail_16_*.rst   (16 FAIL masters, one per FEATURES.md Q1 row)
├── pass_parent.rst                      # toctree of the 9 PASS docs, the 18th master
├── pass_a_standalone_image.rst  ...  pass_i_bare_image_first_in_list_item.rst
└── goldens/
    ├── pass_a_standalone_image.typ
    ├── ...
    └── pass_i_bare_image_first_in_list_item.typ
```
`state_guard_three_master_gate/conf.py`'s comment-block style (a long top-of-file docstring-as-comment naming the phase/plan, the load-bearing properties, and what NOT to touch) is worth mirroring in the new `conf.py` — it is this repo's established convention for fixture provenance, distinct from a Python module docstring since `conf.py` is executed by Sphinx, not imported as a test module.

---

### `tests/fixtures/inline_image_separator_render_gate/goldens/*.typ` (9 files)

**Analog:** `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` (single committed content golden, compared with exact `str` equality).

**Golden file shape** (`tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ:1-16`, read this session — this IS a content file, not a wrapper, confirmed by its leading `@preview` import block and lack of any `#import` template/title/author/date machinery):
```typst
// Essential imports for included document
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

// Initialize codly
#show: codly-init.with()
#codly(languages: codly-languages)

#{
[#metadata(none) <index:__tsx-doc__>]
[#heading(depth: 1, {text("...")}) <index:...>]

par({text("...")})
...
```
Every included (non-master) content file carries this same leading `@preview`-import preamble (per `writer.py`'s `_is_master_document()` branching, described in CLAUDE.md) — this is a general property of ALL 9 goldens the new fixture will capture, not something specific to the `desc_rubric_decoupling` fixture's content. Confirm each captured golden begins with this same 9-line block before committing it.

**This precedent is singular (worth stating plainly per instructions):** it is the only existing test in the repo that commits a `.typ` file as test data and compares emitted output against it byte-for-byte. No prior test commits MULTIPLE goldens for one gate module — the 9-golden loop/parametrization this phase needs (see the test-module section above) is new composition of an existing single-golden idiom, not a copy of an existing multi-golden pattern.

## Shared Patterns

### The separator triad (already driven ~15+ times in `translator.py`)
**Source:** `typsphinx/translator.py:933-943` (`_add_paragraph_separator`), `:1651-1676` (`_emit_inline_concat_separator`/`_mark_inline_concat_content`), `in_list_item`/`list_item_needs_separator` instance attributes.
**Apply to:** `visit_image()`/`depart_image()`'s non-`in_figure` branches only — this is the ONLY product-code pattern this phase applies; no new helper method is created (IMG-10, binding).

### `_emit_id_anchors()`'s own private separator instance — do not conflate with the triad
**Source:** `typsphinx/translator.py:1023-1028` (trailing half: `\n[#metadata(none) <id>]\n` emission + `list_item_needs_separator = True`).
**Apply to:** read-only awareness for the planner — this call site (`visit_image`'s existing `self._emit_id_anchors(node)`, left untouched) independently implements the SAME `in_list_item`/`list_item_needs_separator` check pattern the triad implements, once per anchored id. Their interaction produces one harmless redundant blank line for the single id+list-item shape combination absent from all 9 PASS goldens (measured, RESEARCH.md D-08 finding) — not a bug to fix, not a reason to reorder the calls.

### Render-gate skeleton (56 existing `tests/test_*_render_gate.py` modules)
**Source:** `tests/test_paragraph_concat_render_gate.py:32-79` (imports, `TYPST_AVAILABLE` guard, `_run_sphinx_build_typstpdf`).
**Apply to:** `tests/test_inline_image_separator_render_gate.py`, verbatim for the skeleton, extended (not copied) for the 18-master aggregate-error assertion.

### Golden byte-comparison via `read_text(encoding="utf-8")`, never `.read_bytes()`
**Source:** `tests/test_desc_rubric_decoupling_render_gate.py:299-301` (`golden_path.read_text(encoding="utf-8")` / `typ_output.read_text(encoding="utf-8")`); root cause documented in `typsphinx/builder.py:2072`/`:2139` (bare `open(path, "w", encoding="utf-8")`, no `newline=""`).
**Apply to:** all 9 golden comparisons in the new gate module — a `.read_bytes()` compare will spuriously fail on `windows-latest` CI (D-11 names Windows explicitly) even when the fix is correct.

### RED-first evidence choreography
**Source:** `.planning/milestones/v0.9.1-phases/59-path-shape-predicate-and-image-uri-correctness/59-WINDOWS-URI-EVIDENCE.md` (format: `## Phase base SHA` with `git rev-parse HEAD` transcript, per-shape `### <ID>` sections each with `#### RED (pre-fix, ...)` naming the exact restore command `git checkout $PHASE_BASE_SHA -- <file>`, the exact pytest command run, the WHOLE verbatim output including the pytest header/failure tracebacks/summary line, followed by a `git diff --stat -- <file>` empty-output confirmation that the restore was real).
**Apply to:** `62-RED-EVIDENCE.md` (not `62-VERIFICATION.md` — D-05, reserved name). Structure: `## Phase base SHA` section, then one RED-capture section transcribing the aggregate `ExtensionError`'s full text (17 `docname: expected semicolon or line break` pairs + `pass_parent`'s green build confirmed via its `.pdf` existing on disk and the `Generated PDF: ...` log line in stdout), then the restore-to-fix + `git status --porcelain` empty confirmation. Also the choreography window during which the 9 golden `.typ` files are captured (D-07) — copy each PASS document's emitted content `.typ` from the RED build's `_build` output into `tests/fixtures/inline_image_separator_render_gate/goldens/` before restoring the fix.

## No Analog Found

None. Every file this phase creates or modifies has at least a role-match analog in the existing codebase (see Match Quality column above); the two "role-match" (not "exact") entries — the 18-master fixture and the multi-golden loop — are documented above as scale-ups/compositions of existing singular idioms, not files with zero precedent.

## Metadata

**Analog search scope:** `typsphinx/translator.py` (full file, targeted reads), `typsphinx/builder.py:2600-2650`, `tests/test_paragraph_concat_render_gate.py` (full), `tests/test_abbr_pep_separator_render_gate.py` (full), `tests/test_desc_rubric_decoupling_render_gate.py:270-330`, `tests/fixtures/state_guard_three_master_gate/conf.py` + directory listing, `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ:1-20`, `.planning/milestones/v0.9.1-phases/59-.../59-WINDOWS-URI-EVIDENCE.md:1-80`.
**Files scanned:** 4 primary analogs read in full/near-full, plus 2 targeted-section reads (`translator.py`, `builder.py`), plus one repo-wide `find`/`grep` sweep confirming `desc_rubric_decoupling_render_gate` is the sole existing golden-comparison precedent.
**Pattern extraction date:** 2026-08-30
