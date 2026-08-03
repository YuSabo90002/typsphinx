# Phase 36: Shared-Emission Seam Cleanup - Pattern Map

**Mapped:** 2026-08-01
**Files analyzed:** 5 (2 new + 1 new dir, 2 modified)
**Analogs found:** 5 / 5

This phase is a pure in-repo refactor (D-01..D-07 already lock the shape). No new
architecture — this map exists to hand the planner exact copy-from-here excerpts for the
new test/fixture and the exact current bodies being decoupled, plus the evidence-file
skeleton. Nothing here proposes redesign; do not extract a shared helper (D-01).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `tests/test_desc_rubric_decoupling_render_gate.py` (NEW) | test (real-compile render gate) | request-response (subprocess → `.typ`/`.pdf` → assert) | `tests/test_desc_signature_concat_render_gate.py` (structure) + `tests/test_inline_math_after_text_render_gate.py` (mitex/native parameterisation, pypdf) | exact |
| `tests/fixtures/desc_rubric_decoupling_render_gate/conf.py` (NEW) | config (Sphinx project) | — | `tests/fixtures/rubric_option_concat_render_gate/conf.py` | exact |
| `tests/fixtures/desc_rubric_decoupling_render_gate/index.rst` (NEW) | fixture content | — | `tests/fixtures/desc_signature_siblings_render_gate/index.rst` + `tests/fixtures/rubric_option_concat_render_gate/index.rst` (combined) | exact |
| `typsphinx/translator.py` — `visit_desc_signature`/`depart_desc_signature` (MODIFIED) | translator node-handler | transform (doctree→text) | `visit_strong`/`depart_strong` (body to copy verbatim, D-01) | exact — this IS the source body |
| `typsphinx/translator.py` — `visit_rubric`/`depart_rubric` (MODIFIED) | translator node-handler | transform | `visit_strong`/`depart_strong` (body to copy verbatim, D-01) | exact — this IS the source body |
| `typsphinx/translator.py` — `visit_math_block` (MODIFIED, one line) | translator node-handler | transform | itself (one-line change only, D-06) | exact |
| `.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md` (NEW) | evidence artifact | — | `.planning/milestones/v0.6.5-phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md` | exact |

## Pattern Assignments

### `typsphinx/translator.py` — decoupling `visit_desc_signature`/`depart_desc_signature` and `visit_rubric`/`depart_rubric` (ADM-06, SC#1/SC#2)

**Source of truth to copy from — `visit_strong`/`depart_strong`, `typsphinx/translator.py:1203-1280`** (re-verified this session, line numbers current):

```python
def visit_strong(self, node: nodes.strong) -> None:
    # Add separator if in paragraph and not first node
    self._add_paragraph_separator()

    # If this strong is a sibling in a code-mode concat context (def-list
    # term / link body / desc parameter), + separate it and suppress that
    # context for the strong body (content mode, where an outer '+' would
    # leak). Otherwise fall back to the list-item newline separator.
    if not self._enter_inline_concat_element():
        if self.in_list_item and self.list_item_needs_separator:
            self.add_text("\n")

    # Temporarily disable paragraph state for children
    was_in_paragraph = self.in_paragraph
    self.in_paragraph = False

    # Save and reset list item separator for children (they're inside this element)
    was_list_item_needs_separator = self.list_item_needs_separator

    # Since strong({}) uses content block, treat it like list_item
    # Children need newline separators, not + operators
    was_in_list_item = self.in_list_item
    self.in_list_item = True
    self.list_item_needs_separator = False

    # Determine if we need # prefix (in markup mode)
    prefix = "#" if self._in_markup_mode else ""

    # Use strong({}) function with content block
    self.add_text(f"{prefix}strong({{")

    # Store state to restore in depart
    self._strong_was_in_paragraph = was_in_paragraph
    self._strong_was_in_list_item = was_in_list_item
    self._strong_was_list_item_needs_separator = was_list_item_needs_separator

def depart_strong(self, node: nodes.strong) -> None:
    # Close strong({}) function
    self.add_text("})")

    # Restore paragraph state
    if hasattr(self, "_strong_was_in_paragraph"):
        self.in_paragraph = self._strong_was_in_paragraph
        delattr(self, "_strong_was_in_paragraph")

    # Restore in_list_item state
    if hasattr(self, "_strong_was_in_list_item"):
        self.in_list_item = self._strong_was_in_list_item
        delattr(self, "_strong_was_in_list_item")

    # Restore and mark that next element needs separator
    if hasattr(self, "_strong_was_list_item_needs_separator"):
        # Restore previous state, then mark next element needs separator
        if self.in_list_item:
            self.list_item_needs_separator = True
        delattr(self, "_strong_was_list_item_needs_separator")

    # Restore the code-mode concat context suppressed for the strong body
    # and mark this strong as a sibling so the next term/link/desc
    # expression is + separated.
    self._exit_inline_concat_element()
```

D-01: copy this body **twice**, once into a new self-contained
`visit_desc_signature`/`depart_desc_signature` open/close pair and once into
`visit_rubric`/`depart_rubric` — do not factor into a shared helper. D-03 permits pruning
provably-unreachable branches (see RESEARCH.md's "Provably unreachable branches" list:
`_add_paragraph_separator()`'s body, the `#` markup-mode prefix, and
`_enter_inline_concat_element()`'s `ctx`-not-`None` branch are all dead code when entered
from `desc_signature`/`rubric` — safe to prune OR keep verbatim, implementer's call) but
the **live** branches (`in_list_item`/`list_item_needs_separator` leading-check and the
save/restore dance around `strong({`/`})`) must stay, byte-identically.

**Current call sites being replaced — `visit_desc_signature`/`depart_desc_signature`, `typsphinx/translator.py:4664-4722`** (re-verified, unchanged from RESEARCH.md's cited lines):

```python
def visit_desc_signature(self, node: addnodes.desc_signature) -> None:
    if not self._is_first_desc_signature:
        self._emit_forced_break("linebreak()")
    self._is_first_desc_signature = False
    # Create a dummy strong node and use its visitor logic
    dummy_strong = nodes.strong()
    self.visit_strong(dummy_strong)                    # ← delegation point to REMOVE,
                                                         #   replace with the copied-in body
    # Reset per signature (DESC-02): each desc_signature starts fresh,
    # so consecutive signatures don't carry over a stray linebreak().
    self._is_first_desc_signature_line = True

def depart_desc_signature(self, node: addnodes.desc_signature) -> None:
    # Use strong's depart logic
    dummy_strong = nodes.strong()
    self.depart_strong(dummy_strong)                   # ← delegation point to REMOVE
    docname = self._current_docname()
    seen_labels: set[str] = set()
    for node_id in node.get("ids", []):
        label_id = self._namespace_label(docname, node_id)
        if label_id in seen_labels:
            continue
        seen_labels.add(label_id)
        self.body.append(f"\n[#metadata(none) <{label_id}>]")
    self.body.append("\n")
```

**IMPORTANT — hand-rolled anchor loop stays verbatim, do NOT swap for `_emit_id_anchors`**
(RESEARCH.md Anti-Pattern): the loop above omits a trailing `\n` after each `]` that
`_emit_id_anchors` would add — swapping changes bytes.

**Current call sites being replaced — `visit_rubric`/`depart_rubric`, `typsphinx/translator.py:5034-5076`** (re-verified, unchanged from RESEARCH.md's cited lines):

```python
def visit_rubric(self, node: nodes.rubric) -> None:
    self._emit_id_anchors(node)         # BEFORE the delegation; propagated-target anchor
    self.body.append("\n")              # unconditional extra newline, ALWAYS
    dummy_strong = nodes.strong()
    self.visit_strong(dummy_strong)     # ← delegation point to REMOVE

def depart_rubric(self, node: nodes.rubric) -> None:
    dummy_strong = nodes.strong()
    self.depart_strong(dummy_strong)    # ← delegation point to REMOVE
    self.add_text("\n")                 # required after the copied-in "})" — no trailing
                                         # separator of its own
    self._emit_forced_break("linebreak()")   # FID-04's unconditional trailing linebreak()
```

**Hazard specific to `rubric` (do NOT "clean up" while copying, RESEARCH.md Pitfall 2):** a
rubric with a propagated target inside a list item emits **two** blank lines (not one)
between the anchor and `strong({` — three separate pieces of code (`_emit_id_anchors`'s
internal consume-then-reset, `visit_rubric`'s own unconditional `"\n"`, and the copied-in
leading check) all fire against the same still-`True` flag. D-01 requires reproducing this
exactly; it looks like an obvious bug but fixing it here violates SC#2.

**`visit_literal_strong`/`depart_literal_strong`, `typsphinx/translator.py:5138-5148` — DO NOT TOUCH, but SC#1's grep must tolerate it:**

```python
def visit_literal_strong(self, node: nodes.inline) -> None:
    """Visit a literal_strong node (bold literal text in field lists)."""
    dummy_strong = nodes.strong()
    self.visit_strong(dummy_strong)

def depart_literal_strong(self, node: nodes.inline) -> None:
    """Depart a literal_strong node."""
    dummy_strong = nodes.strong()
    self.depart_strong(dummy_strong)
```

This is a THIRD `dummy_strong = nodes.strong()` delegation pair, out of scope (FLD-03,
Phase 38's territory), not named in CONTEXT.md's decision text. `grep -n "dummy_strong =
nodes.strong()" typsphinx/translator.py` currently returns **6 hits** (lines 4684, 4693 =
desc_signature; 5047, 5065 = rubric; 5141, 5147 = literal_strong). Post-decoupling the
correct count is **2 hits**, both inside `visit_literal_strong`/`depart_literal_strong` —
write SC#1's verification scoped to function context (count == 2 AND both remaining hits
are inside `literal_strong`'s two methods by line-proximity/AST check), not a bare
count-drops-to-zero assertion.

---

### `typsphinx/translator.py` — `visit_math_block` one-line fix (MATH-02, SC#3)

**Current defective trailing bookkeeping, `typsphinx/translator.py:4087-4088`** (re-verified, line numbers unchanged from RESEARCH.md):

```python
        # Mark that content was added so the next list-item sibling
        # (visit_paragraph's _emit_forced_break, a nested list, another
        # block) newline-separates from this equation. The extra newline
        # this produces on top of the existing "\n\n" is cosmetic in Typst
        # code mode; consistency with the shared protocol is what prevents
        # the next sibling from juxtaposing.
        if self.in_list_item:
            self.list_item_needs_separator = True
```

**The fix (D-06) — change only the token `True` → `False` on this one line:**

```python
        if self.in_list_item:
            self.list_item_needs_separator = False
```

Do not touch the LEADING check at `translator.py:4054-4055` (`if self.in_list_item and
self.list_item_needs_separator: self.add_text("\n")`) — it is pre-existing, harmless,
out of MATH-02's stated scope (RESEARCH.md Pitfall 3). Do not touch `_emit_id_anchors`'s
own body (RESEARCH.md blast-radius table) — MATH-02 only touches code that *calls* it.

---

### `tests/test_desc_rubric_decoupling_render_gate.py` (NEW) — SC#1 grep test + SC#2 byte-identity test

**Analog for module docstring/skip-guard/subprocess-invocation shape — `tests/test_desc_signature_concat_render_gate.py:1-101`:**

```python
import re
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
def desc_signature_concat_render_gate_dir():
    """Return the path to the desc_signature_concat_render_gate fixture project."""
    return Path(__file__).parent / "fixtures" / "desc_signature_concat_render_gate"


@pytest.fixture
def temp_build_dir(tmp_path):
    """Provide a temporary directory for build output."""
    return tmp_path / "_build"


def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path
) -> subprocess.CompletedProcess:
    """
    Run ``sphinx-build -b typstpdf`` as a subprocess and return the completed
    process (stdout/stderr captured as text).

    Invoked as ``sys.executable -m sphinx`` (never ``uv run sphinx-build``) so
    the exact interpreter/venv running this test is reused, sidestepping the
    documented NixOS-sandbox PATH-shadowing hazard.
    """
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typstpdf", str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )
```

Note: SC#2 itself only needs `-b typst` (no compile) per RESEARCH.md, but Open Question 2
recommends also driving `-b typstpdf` for a cheap "still compiles" sanity check — mirror
`_run_sphinx_build_typstpdf`'s signature above for the compile leg, and add a second
plain-`-b typst` invocation (or reuse `TypstBuilder` directly) for the byte-diff leg.
`writer.py`'s `translate()` is irrelevant here — this is a black-box subprocess/CLI test
like every other render gate in this repo, not a unit test against the translator class.

**Analog for mitex/native parameterisation and pypdf extraction —
`tests/test_inline_math_after_text_render_gate.py:62-98` (extra_args plumbing) and the
`pypdf.PdfReader` idiom used at that file's PDF-assertion section:**

```python
def _run_sphinx_build_typstpdf(
    source_dir: Path, build_dir: Path, extra_args: tuple = ()
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable, "-m", "sphinx", "-b", "typstpdf",
            *extra_args,
            str(source_dir), str(build_dir),
        ],
        capture_output=True,
        text=True,
    )

# Usage:
# result = _run_sphinx_build_typstpdf(fixture_dir, temp_build_dir, extra_args=("-D", "typst_use_mitex=0"))
```

```python
import pypdf
reader = pypdf.PdfReader(str(pdf_output))
full_text = "\n".join(page.extract_text() for page in reader.pages)
```

(This phase's new test does not need mitex/native parameterisation itself — SC#2's
fixture has no math content — but reuse the same `extra_args` plumbing shape if a
`-b typstpdf` compile-sanity leg is added, and the `pypdf` idiom is the project's
standard PDF-text-extraction pattern if any assertion needs it.)

**Structural/token-count assertion style to reuse for SC#1's grep test and SC#2's
byte-diff test — `tests/test_desc_signature_concat_render_gate.py:255-264`
(`typ_text.count("linebreak()")`) is the closest existing "assert an exact count of a
token in the emitted `.typ`" pattern**:

```python
linebreak_count = typ_text.count("linebreak()")
assert linebreak_count == 2, (
    "Expected exactly 2 linebreak() tokens ... — found "
    f"{linebreak_count}. ...\n{typ_text}"
)
```

Apply the same shape to SC#1 (`grep`-equivalent via `subprocess.run(["grep", "-n",
"dummy_strong = nodes.strong()", "typsphinx/translator.py"], ...)` or a pure-Python
`re.findall` over the file, expecting exactly 2 hits both inside
`literal_strong`'s methods) and to SC#2 (full-string `==` between a captured
pre-decoupling golden `.typ` and the post-decoupling rebuild — see Byte-identity proof
mechanics below).

**Golden-snapshot / byte-identity pattern — NEW to this repo (RESEARCH.md confirms zero
existing `golden`/`snapshot`/`difflib`/full-file-equality pattern in `tests/`).** No
analog file to copy from; use plain string equality:

```python
golden_typ = (Path(__file__).parent / "fixtures"
              / "desc_rubric_decoupling_render_gate" / "golden.typ").read_text(encoding="utf-8")
# ... run sphinx-build -b typst against the fixture into temp_build_dir ...
actual_typ = (temp_build_dir / "index.typ").read_text(encoding="utf-8")
assert actual_typ == golden_typ, (
    "Decoupling changed emitted bytes -- SC#2 violated:\n"
    + "\n".join(difflib.unified_diff(
        golden_typ.splitlines(), actual_typ.splitlines(), lineterm=""
    ))
)
```

Capture `golden.typ` by running the real pre-decoupling `sphinx-build -b typst` against
the new fixture ONCE (before the decoupling code lands) and committing the output
verbatim — this doubles as both the permanent regression test asset AND (via `diff`) the
`36-GATE-EVIDENCE.md` recorded-diff evidence D-07/SC#2 require.

---

### `tests/fixtures/desc_rubric_decoupling_render_gate/conf.py` (NEW)

**Analog — `tests/fixtures/rubric_option_concat_render_gate/conf.py`** (copy verbatim, rename project/title):

```python
"""Sphinx config for the desc/rubric decoupling render-gate fixture (Phase 36, SC#2)."""

project = "Desc Rubric Decoupling Render Gate"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

typst_documents = [
    ("index", "index", "Desc Rubric Decoupling Render Gate", "typsphinx tests"),
]
```

No `intersphinx`, no domain config needed — matches `desc_sig_space_render_gate` and
`rubric_option_concat_render_gate`'s own minimal-conf style (RESEARCH.md Open Question 1
recommendation).

### `tests/fixtures/desc_rubric_decoupling_render_gate/index.rst` (NEW)

**Analogs — combine constructs from `tests/fixtures/desc_signature_siblings_render_gate/index.rst`
(signatures + siblings) and `tests/fixtures/rubric_option_concat_render_gate/index.rst`
(rubric incl. Options-style) + inline bold as a regression control.** RESEARCH.md's Code
Examples section already sketches the exact combined shape (verified against the real
Sphinx `doc/` corpus — `.. rubric:: Options` + `.. option::` is a real, recurring
construct, not synthetic):

```rst
Desc Rubric Decoupling Render Gate
====================================

This fixture combines a signature, sibling signatures, a rubric styled like
autodoc's ".. rubric:: Options" construct, and plain bold markup -- the four
constructs Phase 36's SC#2 names -- into one file, to prove the desc_signature/
rubric decoupling produces byte-identical .typ output.

.. py:function:: connect(host, port, timeout=30)

   Connect to *host*.

.. py:function:: connect(host, port, timeout=30)
   :noindex:

This is a paragraph with **bold text** for the regression control.

.. rubric:: Options

.. option:: --sep

   If specified, separate source and build directories.
```

---

### `.planning/phases/36-shared-emission-seam-cleanup/36-GATE-EVIDENCE.md` (NEW)

**Analog — `.planning/milestones/v0.6.5-phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md`**
(immediately preceding phase, same milestone, same "GATE-01 redefined" situation).

**Heading structure to reuse, substituting a diff pair for the decoupling half (no
compile-fatal RED exists there, per D-04) and keeping the classic RED→GREEN pair for the
MATH-02 half:**

```markdown
# Phase 36 GATE-01 Evidence: Decoupling Diff + MATH-02 RED -> GREEN Record

## Pre-decoupling baseline (SC#2, D-07)
- Commit measured / Date / Commands (real `sphinx-build -b typst` against the new fixture)
### Verbatim captured .typ (or pointer to the committed golden.typ)

## Post-decoupling diff (SC#1, SC#2, D-03)
- Commit measured / Date / Commands (identical build, post-decoupling-commit)
### Diff result (empty diff == SC#2 proof)
### SC#1 grep result (6 hits -> 2 hits, both inside literal_strong)

## RED — pre-fix run (SC#3, D-04, D-06)
### Verbatim structural-assertion failure output (two blank lines after math, .typ-level)

## GREEN — post-fix run (SC#3, D-04, D-06)
### Verbatim passing output (one blank line after math)
### PDF text-invariance guard result (extracted text unchanged across the fix, per D-04)

## Diff scope
(git diff --stat between the pre-decoupling and final commit)

## Regression sweep — suite, lint, invariants
(full-suite command + result table, black/ruff/mypy exit codes, milestone invariant checks)

## Regression sweep — corpus gate and docs dogfooding
(uv run pytest tests/test_corpus_gate.py -q -m slow, SC#4)

## Phase verdict
(table: criterion | marker | evidence, one row per ROADMAP SC, mirroring 34-GATE-EVIDENCE.md's closing table)
```

Follow 34-GATE-EVIDENCE.md's convention throughout: every claim backed by a verbatim
command + verbatim output block (not paraphrase), named commit SHAs for RED/GREEN
boundaries, and a final verdict table with one row per ROADMAP success criterion.

## Shared Patterns

### Worktree-isolated execution (applies to every plan/wave in this phase)
**Source:** `CLAUDE.md` § "Worktree-isolated execution"
**Apply to:** all executor waves.
```bash
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
uv run pytest ...   # run ALL subsequent commands via `uv run`
```
Plus the NixOS `uv`/`ruff` binary-symlink shim documented in RESEARCH.md's SC#4 section
(`for t in uv ruff; do ln -sf "$(command -v $t)" ".venv/bin/$t"; done`), retired-but-still
worth applying defensively per fresh worktree.

### `sys.executable -m sphinx`, never bare `sphinx-build`
**Source:** every existing render-gate test file (`_run_sphinx_build_typstpdf` helper,
duplicated per-file by convention — see excerpts above).
**Apply to:** the new `tests/test_desc_rubric_decoupling_render_gate.py`.

### Real-compile skip guard
**Source:** every render-gate test file's `try: import typst ... TYPST_AVAILABLE` +
`@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` on the test class.
**Apply to:** the new test file, even for the `-b typst`-only byte-diff leg (typst-py
availability is still assumed by the compile-sanity leg if added).

## No Analog Found

None — every file in this phase's scope has a strong analog (the existing render-gate
suite, Phase 34's evidence file, and the translator's own current code being copied).

## Metadata

**Analog search scope:** `tests/test_desc_signature_*.py`, `tests/test_rubric_*.py`,
`tests/test_inline_math_after_text_render_gate.py`, `tests/fixtures/desc_signature_*`,
`tests/fixtures/rubric_*`, `typsphinx/translator.py` (targeted line ranges), and
`.planning/milestones/v0.6.5-phases/34-inline-math-after-text-separator-fix/34-GATE-EVIDENCE.md`.
**Files scanned:** 9 (5 test files, 3 fixture files, 1 evidence file) + `translator.py`
(6 targeted, non-overlapping reads).
**Pattern extraction date:** 2026-08-01
</content>
