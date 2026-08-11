# Phase 47: Two-Layer Output — Content/Wrapper Split, Target-as-Path, Collision Detection - Pattern Map

**Mapped:** 2026-08-11
**Files analyzed:** 8 (2 existing files being rewritten in place, 2 new test modules, 1 existing
test module whose expectations move, N new `tests/roots`/`tests/fixtures` fixture projects)
**Analogs found:** 8 / 8 (this phase modifies its own analogs — every "new" behavior has a same-file
predecessor pattern; no external file needed as a stand-in)

**Line-number drift check against `47-CONTEXT.md`'s `<canonical_refs>`:** all cited ranges were
re-read this session and match with only trivial drift:
- `writer.py:96-126` `_is_master_document()` — **exact match**.
- `writer.py:204-221` included-document preamble — the actual preamble body is `writer.py:208-218`
  (the `if not is_master:` guard starts at 204, `return` is at 221) — CONTEXT.md's range is the
  containing block, RESEARCH.md's `208-218` is the tighter, correct citation for the excerpt itself.
- `writer.py:24-73` `_resolve_entry_element()` — **exact match**.
- `writer.py:128-174` `_compute_template_import_path()` — **exact match**.
- `builder.py:156-288` `_resolve_output_stem()` — **exact match**; the `is_guarded` OR-expression
  CONTEXT.md cites at `:222-227` is confirmed at exactly that range (RESEARCH.md's `:217-227` is off
  by 5 lines — trust CONTEXT.md's `:222-227` here).
- `builder.py:290-323` `_directory_preserving_relpath()` — **exact match**.
- `builder.py:28-47` `_default_typst_documents()` — **exact match**.
- `builder.py:960-1069` `TypstPDFBuilder.finish()` — the method itself runs `960-1075` (7 lines
  longer than cited; the failures-list-then-`ExtensionError` shape CONTEXT.md cites at `:1007-1069`
  is confirmed, actual raise block is `:1070-1074`).
- Call sites `builder.py:578` and `builder.py:929` (`_resolve_output_stem` calls in the two
  `write_doc` bodies) — **exact match**.
- `tests/test_builder_output_stem.py:334` and `:352` — **exact match**, both are
  `test_resolve_output_stem_falls_back_on_*_collision`, asserting
  `builder._resolve_output_stem("index") == "index"`.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `typsphinx/writer.py` (rewrite: delete `_is_master_document`, generalize preamble, rewrite `#include()`-path computation, D-08 positional title/author) | writer/transform | request-response (docname → `.typ` string) | itself, pre-phase (`translate()`, `_compute_template_import_path()`) | exact — same file, same method, new logic |
| `typsphinx/builder.py` (rewrite: split content vs. wrapper write paths, new unified collision validator, OUT-01/OUT-02 disentangle) | builder/orchestrator | batch (build-wide) + CRUD (file writes) | itself, pre-phase (`_resolve_output_stem`, `write()`, `TypstPDFBuilder.finish()`) | exact — same file, same methods, new logic |
| New unified collision validator (method on `TypstBuilder`, e.g. `_validate_no_collisions()`) | validator/config-gate | batch (single pass over `typst_documents` + `found_docs`) | `TypstPDFBuilder.finish()`'s `failures`-list-then-one-`ExtensionError` shape (`builder.py:1007-1074`) | role-match — same aggregate-then-raise shape, one build stage earlier, on the base class |
| Wrapper `.typ` generation (template application + `#include()` of content) | writer/transform | request-response | Today's master-document path through `TypstWriter.translate()` (`writer.py:223-363`) + `TemplateEngine.render()` | exact — literally the surviving half of the current single-shape `translate()` |
| Content `.typ` generation (no template, D-06 preamble) | writer/transform | request-response | Today's included-document path through `TypstWriter.translate()` (`writer.py:204-221`) | exact — literally the surviving half, generalized to run unconditionally |
| Wrapper→content `#include()` path computation (new function, e.g. `compute_include_path()`) | utility | transform (pure path computation) | `_compute_template_import_path()` (`writer.py:128-174`) — as an ANTI-pattern to structurally avoid, per RESEARCH.md Pattern 2 | role-match, but explicitly NOT a copy target — see "New Utility: wrapper→content include path" below |
| `tests/test_two_layer_output_gate.py` (new) | test / integration gate | request-response (subprocess) + file-I/O | `tests/test_typst_documents_collision_gate.py` (subprocess pattern) + `tests/test_pdf_render_gate.py` (pypdf pattern) | role-match — both are real `sphinx-build` subprocess + real `typst.compile()` gates already in this repo |
| `tests/test_collision_validator_gate.py` (new) | test / integration gate | request-response (subprocess) + file-I/O | `tests/test_typst_documents_collision_gate.py` | exact — same subprocess-gate shape, inverted assertions (ExtensionError instead of warn-and-fallback) |
| `tests/test_typst_documents_collision_gate.py` (expectations invert) | test / integration gate | request-response (subprocess) | itself, pre-phase | exact — same file, same fixtures, assertions flip from `returncode == 0` to non-zero + `ExtensionError` |
| `tests/test_builder_output_stem.py` (expectations move at :334, :352; OUT-02 subset stays) | test / unit | request-response (in-process) | itself, pre-phase | exact — same file, two functions' assertions change, the three `is_guarded` escape-term tests are kept verbatim as regression tests |
| New `tests/roots/` or `tests/fixtures/` fixture projects (nested master, duplicate targets, self-collision, case-varied target, escaping targets) | fixture / config | file-I/O | `tests/fixtures/derived_docname_collision_gate/` (conf.py + minimal .rst pair) | exact — see "Fixture Convention" section below |

## Pattern Assignments

### `typsphinx/writer.py` — content/wrapper split

**Analog:** itself, pre-phase (`_is_master_document`, the `translate()` branch, `_compute_template_import_path`)

**Deleted pattern** (`writer.py:96-126`, MUST be gone per success criterion 1 — verified by
repo-wide grep):
```python
def _is_master_document(self, docname: str) -> bool:
    config = self.builder.config
    typst_documents = getattr(config, "typst_documents", [])
    for doc_tuple in typst_documents:
        if doc_tuple and doc_tuple[0] == docname:
            return True
    return False
```
Every call site of this method (currently one, in `translate()` at `writer.py:202`) must be
replaced by whatever new dispatch distinguishes "am I emitting a content file or a wrapper file for
this call" — CONTEXT.md's phase boundary implies this becomes two separate write operations per
entry rather than a single-docname boolean branch, so the replacement is architectural, not a
drop-in rename.

**D-06 preamble to generalize verbatim to EVERY content file** (`writer.py:208-218`, currently only
reached when `not is_master`):
```python
imports = []
imports.append("// Essential imports for included document")
imports.append('#import "@preview/codly:1.3.0": *')
imports.append('#import "@preview/codly-languages:0.1.10": *')
imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
imports.append('#import "@preview/gentle-clues:1.3.1": *')
imports.append("")
imports.append("// Initialize codly")
imports.append("#show: codly-init.with()")
imports.append("#codly(languages: codly-languages)")
imports.append("")

self.output = "\n".join(imports) + "\n" + body
```
Copy this block unchanged as the content-file's ENTIRE output shape (`self.output = "\n".join(imports) + "\n" + body`, no template, no docname-based `is_master` gate). Note the `@preview` versions
(`codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7`, `gentle-clues:1.3.1`) are pinned across
THREE files (see Shared Patterns → `@preview` version sync below) — do not hand-retype them, copy
this exact block.

**Wrapper's full template-application path to keep** (`writer.py:223-363`, today's `is_master`
branch): everything from `# For master documents, apply template` through the final
`template_engine.render(params, body, template_file=template_file)` call is the wrapper's shape,
essentially unchanged, EXCEPT:
- `docname` in this block currently refers to the single write target; for a wrapper it must become
  "the docname of the master document THIS ENTRY names" plus its own resolved output location for
  the include-path computation (see below).
- D-08 requires `sphinx_metadata["project"]`/`["author"]` (`writer.py:271-279`) to stop calling
  `_resolve_entry_element(typst_documents_cfg, docname, 2/3, default)` (a docname first-match scan)
  and instead read `entry[2]`/`entry[3]` directly off the SPECIFIC `typst_documents` tuple this
  wrapper is being generated for (positional, not docname-matched) — this is a bypass of
  `_resolve_entry_element()` for the wrapper path specifically; `_resolve_entry_element()` itself
  (`writer.py:24-73`) can stay as dead code, be deleted, or be repurposed depending on the plan's
  Wave design, since D-08 only forbids USING its docname-matching behavior for wrappers, not its
  continued existence.
- `body` for a wrapper is no longer the wrapper's own translated doctree — it must be a
  `#include("<computed-path>")` statement (or equivalent) referencing the entry's content file, not
  the literal Typst body `TypstTranslator` emitted for that docname. This is the single largest
  structural change in this file.

**`_compute_template_import_path()` (`writer.py:128-174`) — reuse pattern, NOT reuse code:**
```python
depth = len(PurePosixPath(docname).parent.parts)
return "".join(["../"] * depth) + "_template.typ"
```
RESEARCH.md's Pattern 2/Common Pitfall 3 (measured this session with real `typst.compile()` runs)
establishes this depth-only counter does NOT generalize to wrapper→content paths — it silently
assumes (a) the importing file's resolved directory equals its docname's directory, and (b) the
imported file is always at the outdir root. Both are false once OUT-01 lets a wrapper's target be an
arbitrary path. Use the measured-correct replacement instead (see "New Utility" below). Do NOT copy
this function's body for the new include-path computation — copy only its DOCSTRING CONVENTION
(depth/path Examples block with `>>>` doctests) for whatever new function replaces it, and keep this
function itself for its own still-valid job (locating the outdir-root `_template.typ`, unchanged).

**New Utility: wrapper→content include path** (no existing analog in this codebase — this is
genuinely new, per RESEARCH.md's own explicit "Don't Hand-Roll" entry):
```python
# RESEARCH.md's measured-correct form (this session's own posixpath.relpath
# cross-check against real typst.compile() results — see 47-RESEARCH.md
# "Common Pitfalls" #3 for the four independent fixture measurements this
# is derived from):
import posixpath

def compute_include_path(wrapper_relative_dir: str, content_relative_path: str) -> str:
    """wrapper_relative_dir: dirname of the wrapper's own OUTPUT path,
    relative to outdir root ('' for outdir root itself).
    content_relative_path: the content file's own path, relative to outdir
    root, e.g. 'guide/index.typ'.
    Typst #include() resolves relative to the INCLUDING file's own
    directory (measured empirically, not from docs) -- this is a genuine
    two-endpoint relpath, not a depth-only "../" counter.
    """
    start = wrapper_relative_dir or "."
    return posixpath.relpath(content_relative_path, start=start)
```
This is a `posixpath.relpath`-based two-endpoint computation, structurally distinct from
`_compute_template_import_path()`'s one-endpoint depth counter. Do not name it to look like a minor
variant of the old function — RESEARCH.md is explicit that reusing the old function's SHAPE (not
just its code) for this job is the literal root cause of the B-1 defect this phase closes.

---

### `typsphinx/builder.py` — content path, wrapper path, unified collision validator

**Analog:** itself, pre-phase (`_resolve_output_stem`, `_directory_preserving_relpath`, `write()`,
both `write_doc` bodies, `TypstPDFBuilder.finish()`)

**Content path — becomes unconditional, no resolver call** (new pattern per RESEARCH.md
"Code Examples"; today's near-equivalent no-op path is `_resolve_output_stem()`'s
`if not entry_found: return docname` branch at `builder.py:199-203`):
```python
# Every docname's content file, unconditionally (COMP-01/OUT-03):
content_path = path.normpath(path.join(self.outdir, docname + ".typ"))
```
This REPLACES the current universal `stem = self._resolve_output_stem(docname)` call
(`builder.py:578` in `TypstBuilder.write_doc`, `builder.py:929` in `TypstPDFBuilder.write_doc`) for
the content-file half of each write — the content path is now a pure function of `docname`, with
`_resolve_output_stem()` no longer consulted for it at all.

**Wrapper path — `_resolve_output_stem()`'s surviving terms, OUT-01/OUT-02 disentangled:**
The `is_guarded` OR-expression (`builder.py:222-227`, four terms) is the single load-bearing site to
split:
```python
is_guarded = (
    any(sep in stem for sep in separators)   # <- OUT-01 REVERSES this term only
    or ".." in segments                       # <- OUT-02 KEEPS this term
    or path.isabs(stem)                       # <- OUT-02 KEEPS this term
    or is_drive_qualified                     # <- OUT-02 KEEPS this term
)
```
Copy the surrounding function's STRUCTURE (docstring conventions, the `entry_found` guard-loop at
`builder.py:191-203`, the D-04 `.typ`-suffix-stripping rule at `builder.py:205-209`) but split this
boolean into `escapes_outdir` (the three OUT-02 terms only) — still routes to the existing
fallback-to-basename-with-warning block (`builder.py:228-249`, unchanged) — while the
separator-membership term becomes a no-op: a bare separator-bearing, non-escaping stem is now the
literal relative wrapper path, joined under `outdir` unmodified. Per RESEARCH.md Pitfall 4, this is
the single highest-risk regression site in the whole rewrite — a test asserting "any `/` in a target
name warns and truncates" still passing after the change is itself a bug signal.

**CR-01 collision block to DELETE** (`builder.py:264-283`, the entire warning-and-fallback shape) —
D-03 explicitly replaces this in-function collision check with the new unified pre-write validator;
do not port its logic forward, only its comment's explanation of WHY the comparison must be made on
the directory-qualified effective path (still true for whatever collision-map key the new validator
builds for a wrapper entry).

**Unified collision validator — analog is `TypstPDFBuilder.finish()`'s failures-list shape**
(`builder.py:1007-1074`), relocated to `TypstBuilder`, run BEFORE any write (D-02), and covering ALL
of D-03's four collision kinds in one map:
```python
# Source: typsphinx/builder.py:1007-1074 (TypstPDFBuilder.finish, current
# shape) -- the aggregate-failures-then-one-ExtensionError pattern D-02
# mirrors one build stage earlier, on the BASE builder so both TypstBuilder
# and TypstPDFBuilder inherit identical behaviour (Claude's Discretion note
# in 47-CONTEXT.md).
failures: List[Tuple[str, str]] = []

for doc_tuple in typst_documents:
    if not doc_tuple:
        logger.warning(f"Malformed typst_documents entry: {doc_tuple!r}")
        failures.append((repr(doc_tuple), "malformed typst_documents entry"))
        continue
    docname = doc_tuple[0]
    if not isinstance(docname, str):
        message = (
            f"typst_documents entry has a non-str docname: "
            f"{docname!r} -- expected a str"
        )
        logger.warning(message)
        failures.append((repr(docname), message))
        continue
    # ... per-entry work here (in finish()'s case: resolve stem, compile,
    # write; in the new validator's case: compute this entry's PHYSICAL
    # wrapper path and add it -- casefold()-normalized per D-05 -- to a
    # single logical-file-to-physical-path map, checking for a duplicate
    # key on every insertion including the reserved "_template" and every
    # docname's own content path) ...

if failures:
    summary = "; ".join(f"{docname}: {err}" for docname, err in failures)
    raise ExtensionError(
        f"typstpdf: {len(failures)} master document(s) failed: {summary}"
    )
```
Key differences the new validator must apply, per D-01/D-02/D-03/D-05 (these are NOT present in the
`finish()` analog and must be added, not copied):
- Runs BEFORE any `write_doc()` call (D-02) — likely inserted into `write()`
  (`builder.py:384-444`) immediately after `self.master_included_docnames = ...`
  (`builder.py:428`) and before the `for docname in sorted(docnames):` write loop
  (`builder.py:432`), or as an explicit call from `prepare_writing()` (`builder.py:368-382`).
  Exact placement is Claude's Discretion per CONTEXT.md, constrained only by "before write" + "one
  code path shared by both builders" + "`TypstBuilder` owns it".
- The map is over EVERY docname's content path (`outdir/<docname>.typ`, unconditional) UNION every
  `typst_documents` entry's wrapper path UNION the literal `"_template"` — not just
  `typst_documents` entries as `TypstPDFBuilder.finish()`'s loop does.
- Every key comparison is `.casefold()`-normalized on BOTH sides (D-05) — `finish()`'s analog has no
  such normalization; this is new logic, not a copy.
- Two entries naming the SAME docname with DIFFERENT targets are explicitly allowed (D-04) — the
  validator must ask "do two logical files (a content file and N wrapper files) want ONE physical
  path", never "is this docname repeated".
- On any collision: NO output file is written at all (D-02) — unlike `finish()`, which still writes
  every entry that did NOT fail. The validator must raise before ANY `write_doc()` runs, not after
  attempting all of them.

**`_directory_preserving_relpath()` (`builder.py:290-323`) — deprecated for wrapper placement, kept
for content placement:** RESEARCH.md's "State of the Art" table marks this function's
directory-FORCING role (its entire purpose under D-05/Phase 44) as reversed by OUT-01 for wrappers.
Do not call it when computing a wrapper's path. Its directory-preservation SHAPE (a docname's own
directory is unconditionally where ITS CONTENT FILE goes) may still describe the content-path rule,
but the content path per the "Code Examples" analog above needs no call to this function at all — it
is `path.join(self.outdir, docname + ".typ")` directly, since a docname already carries its own
`/`-separated directory.

---

### `tests/test_two_layer_output_gate.py` (new)

**Analogs:** `tests/test_typst_documents_collision_gate.py` (subprocess-invocation idiom) +
`tests/test_pdf_render_gate.py` (pypdf-extraction idiom)

**Subprocess invocation** (copy verbatim per-module — this repo's convention is each gate module
carries its OWN copy rather than importing a sibling's, per
`test_typst_documents_collision_gate.py:46-58`'s own docstring):
```python
import subprocess
import sys
from pathlib import Path

def _run_sphinx_build(source_dir: Path, build_dir: Path, builder: str) -> subprocess.CompletedProcess:
    """Invoked as `sys.executable -m sphinx` (never `uv run sphinx-build`,
    never a resolved `sphinx-build` binary) so the exact interpreter/venv
    running this test is reused, sidestepping the documented NixOS-sandbox
    PATH-shadowing hazard. Every gate module in this suite carries its own
    copy of this helper rather than importing a sibling module's."""
    return subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", builder, str(source_dir), str(build_dir)],
        capture_output=True,
        text=True,
    )
```

**Availability guards** (copy verbatim, `test_typst_documents_collision_gate.py:24-29` +
`test_pdf_render_gate.py:32-44`):
```python
try:
    import typst  # noqa: F401
    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
```
Then `@pytest.mark.skipif(not (TYPST_AVAILABLE and PYPDF_AVAILABLE), reason=...)` at class level, per
`test_pdf_render_gate.py:267-270`.

**COMP-03 (B-1) real-`TypstError` RED assertion** — this phase's pre-fix RED baseline is the exact
string RESEARCH.md measured this session:
```
TypstError('file not found (searched at .../guide/index.typ)')
```
Assert this string is ABSENT (or that the compile SUCCEEDS) post-fix; assert it IS present pre-fix
if a red/green pair is written into the same test run (binding constraint #4).

**COMP-04 (B-2) structural `pypdf`-text RED assertion** — class-scoped compile-once fixture, mirror
`admonition_render_gate_pdf_text` (`test_pdf_render_gate.py:194-264`):
```python
@pytest.fixture(scope="class")
def some_fixture_pdf_text(tmp_path_factory):
    source_dir = Path(__file__).parent / "fixtures" / "<new_fixture_name>"
    build_dir = tmp_path_factory.mktemp("<new_fixture_name>") / "_build"
    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-b", "typst", str(source_dir), str(build_dir)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"sphinx-build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    wrapper_typ = build_dir / "<wrapper-file>.typ"  # NOT index.typ unconditionally --
    # this phase's wrapper path is the compile target, not the docname-named file
    assert wrapper_typ.exists()

    pdf_output = build_dir / "<wrapper-file>.pdf"
    typst.compile(str(wrapper_typ), output=str(pdf_output))
    assert pdf_output.exists() and pdf_output.stat().st_size > 0
    with open(pdf_output, "rb") as f:
        assert f.read(4) == b"%PDF"

    reader = pypdf.PdfReader(str(pdf_output))
    return "\n".join(page.extract_text() for page in reader.pages)
```
Then assert the per-page structural claim RESEARCH.md's Pitfall 2 measured: a second title-page-shaped
block (an author line + isolated page number) and a second `"Contents"` heading appear BETWEEN the
outer document's own prose and the nested document's own body marker, pre-fix; assert neither appears
post-fix. This is a `pypdf.PdfReader(...).extract_text()` structural check, NOT a `.typ` source-text
regex — RESEARCH.md's "Don't Hand-Roll" table is explicit this distinction is load-bearing (a `.typ`
source diff cannot prove what the COMPILED document contains).

---

### `tests/test_collision_validator_gate.py` (new)

**Analog:** `tests/test_typst_documents_collision_gate.py` (structure, fixture-per-scenario
organization, `COLLISION_WARNING_SUBSTRING`-style constant — but repurposed for the OPPOSITE outcome)

Structure to copy (class docstring, one fixture-directory constant per scenario, one test method per
scenario, both `-b typst` and `-b typstpdf` variants where the old module has them):
```python
FIXTURES_DIR = Path(__file__).parent / "fixtures"
BLD02_DUPLICATE_TARGET_FIXTURE_DIR = FIXTURES_DIR / "bld02_duplicate_target_gate"
BLD03_SELF_COLLISION_FIXTURE_DIR = FIXTURES_DIR / "bld03_self_collision_gate"
BLD04_CASE_COLLISION_FIXTURE_DIR = FIXTURES_DIR / "bld04_case_collision_gate"

COLLISION_ERROR_SUBSTRING = "..."  # whatever the new ExtensionError names -- exact wording
                                    # is Claude's Discretion per 47-CONTEXT.md
```
Inverted assertion shape (contrast with the OLD module's `returncode == 0` + warning-substring
pattern at `test_typst_documents_collision_gate.py:96-129`):
```python
def test_bld02_duplicate_target_is_rejected(self, tmp_path):
    build_dir = tmp_path / "build"
    result = _run_sphinx_build(BLD02_DUPLICATE_TARGET_FIXTURE_DIR, build_dir, "typst")

    assert result.returncode != 0, (
        f"Expected the build to FAIL on a duplicate-target collision (D-01/D-02/D-03):\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    combined_output = result.stdout + result.stderr
    assert "ExtensionError" in combined_output
    assert COLLISION_ERROR_SUBSTRING in combined_output

    # D-02: no output file at all when any collision is found.
    assert not any(build_dir.iterdir()) if build_dir.exists() else True
```
BLD-04 (case-insensitivity) needs an ADDITIONAL unit-level assertion alongside the subprocess gate,
per RESEARCH.md's Validation Architecture table ("Structural RED at the unit level... since Linux CI
cannot observe the physical collision") — assert the comparison function itself folds case, e.g.
`assert some_comparison_fn("Manual.typ", "manual.typ")` returns a collision-equal result, independent
of any real filesystem behavior.

---

### `tests/test_typst_documents_collision_gate.py` (expectations invert, in place)

**Analog:** itself. Every one of its 5 test methods currently asserts the OLD warn-and-fallback
contract; each must invert to assert `ExtensionError` + non-zero exit + no output written. Concrete
example of the exact inversion (from `test_derived_default_docname_collision_keeps_both_documents`,
`test_typst_documents_collision_gate.py:83-129`):
```python
# BEFORE (current, to invert):
assert result.returncode == 0, (...)
index_typ = build_dir / "index.typ"
chapter1_typ = build_dir / "chapter1.typ"
assert index_typ.exists(), (...)
assert chapter1_typ.exists(), (...)
...
assert COLLISION_WARNING_SUBSTRING in combined_output, (...)

# AFTER (D-01/D-02/D-03 shape):
assert result.returncode != 0, (...)
assert not index_typ.exists(), (...)      # D-02: no file written on collision
assert not chapter1_typ.exists(), (...)
combined_output = result.stdout + result.stderr
assert "ExtensionError" in combined_output, (...)
```
The `COLLISION_WARNING_SUBSTRING = "collides with an existing document"` module constant
(`test_typst_documents_collision_gate.py:43`) should be renamed/repurposed to whatever the new
`ExtensionError`'s message substring is, per whatever wording the implementation plan chooses.

---

### `tests/test_builder_output_stem.py` (expectations move at specific lines, OUT-02 subset kept)

**Analog:** itself. `:334` and `:352` (verified this session, both exact):
```python
def test_resolve_output_stem_falls_back_on_docname_collision(temp_sphinx_app):
    ...
    builder.env = types.SimpleNamespace(found_docs={"index", "chapter1"})
    builder.config.typst_documents = [("index", "chapter1.typ", "T", "A")]
    assert builder._resolve_output_stem("index") == "index"   # <- INVERTS: this is now a
                                                                 #    collision the validator
                                                                 #    catches BEFORE write,
                                                                 #    not a per-call fallback

def test_resolve_output_stem_falls_back_on_reserved_template_name(temp_sphinx_app):
    ...
    builder.config.typst_documents = [("index", "_template.typ", "T", "A")]
    assert builder._resolve_output_stem("index") == "index"   # <- SAME inversion
```
Both currently assert the per-call warn-and-fallback contract CR-01 implements; D-03 moves this
entire responsibility to the new unified validator, so these two specific assertions either move
into the NEW `tests/test_collision_validator_gate.py` module (testing the validator directly) or are
deleted here and replaced with a test that `_resolve_output_stem()` (rewritten, wrapper-path-only) no
longer performs ANY collision check at all — the exact split is a planning decision, not fixed by
this pattern map.

**OUT-02 escape-term tests to KEEP as regression tests, unchanged** — every test currently exercising
`".." in segments`, `path.isabs(stem)`, or `is_drive_qualified` must keep passing verbatim after
OUT-01's split (per RESEARCH.md Pitfall 4's own warning sign: such a test STILL passing is confirming
evidence, not staleness).

## Fixture Convention (`tests/fixtures/` vs. `tests/roots/`)

**`tests/roots/`** holds exactly ONE project today: `tests/roots/test-basic` — CLAUDE.md's own
"Tests" section names this as the `rootdir` fixture's target, consumed via
`sphinx.testing.fixtures`' `rootdir`/`app` machinery for lower-level, non-subprocess integration
tests (doctree-level, not full-build).

**`tests/fixtures/`** is the established convention for REAL-`sphinx-build`-subprocess gate fixtures
— every existing collision/render-gate module (`test_typst_documents_collision_gate.py`,
`test_pdf_render_gate.py`, and this phase's own `test_default_typst_documents_gate.py` analog) points
`FIXTURES_DIR = Path(__file__).parent / "fixtures"` at a per-scenario subdirectory containing a
minimal `conf.py` + a small number of `.rst` files with distinctive marker strings (e.g.
`UNIQUE-CHAPTER-MARKER-XYZ`, confirmed at `tests/fixtures/derived_docname_collision_gate/`). This is
the convention this phase's five new fixture projects (nested master, duplicate targets,
self-collision, case-varied target, escaping targets) should follow — one new subdirectory per
scenario under `tests/fixtures/`, named descriptively (e.g. `bld02_duplicate_target_gate/`,
matching the existing `derived_docname_collision_gate` / `explicit_template_collision_gate` naming
pattern of `<scenario>_<mechanism>_gate`), each with its own `conf.py` carrying a load-bearing-facts
docstring comment (copy this convention verbatim — see
`tests/fixtures/derived_docname_collision_gate/conf.py:1-15` for the exact style: a comment
enumerating exactly which config values are load-bearing and why renaming them breaks the fixture).

**B-1's nested-master fixture specifically** needs a docname whose target basename DIFFERS from its
docname (per CONTEXT.md's "Specific Ideas": "the exact way B-1 could be reintroduced one level up"),
e.g. a `typst_documents` entry `("guide/index", "manuals/guide.typ", ...)` nested under an outer
master's toctree — this is a new shape not present in any current fixture and must be hand-built, not
copied from an existing one.

## Shared Patterns

### `@preview` package version sync (three-site hazard — unaffected by this phase, but every content
file now carries it unconditionally)
**Source:** `typsphinx/writer.py:210-213` (imports), `typsphinx/template_engine.py`, `templates/base.typ`
**Apply to:** every content-file emission path (D-06 makes what was previously an
included-documents-only concern apply to EVERY docname unconditionally)
```python
imports.append('#import "@preview/codly:1.3.0": *')
imports.append('#import "@preview/codly-languages:0.1.10": *')
imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
imports.append('#import "@preview/gentle-clues:1.3.1": *')
```
`tests/test_preview_version_sync.py` asserts all three sites agree — CLAUDE.md flags this as the
project's one hazard where bumping a version requires touching three files, or CI fails. This
phase's own RESEARCH.md flags the same test module as needing re-verification once content files
carry this preamble unconditionally (it should still pass unchanged, but must be re-run).

### Aggregate-failures-then-single-`ExtensionError` (D-02's borrowed shape)
**Source:** `typsphinx/builder.py:1007-1074` (`TypstPDFBuilder.finish()`)
**Apply to:** the new unified collision validator on `TypstBuilder`
```python
failures: List[Tuple[str, str]] = []
for entry in ...:
    if <malformed or colliding>:
        logger.warning(message)
        failures.append((key, message))
        continue
if failures:
    summary = "; ".join(f"{k}: {err}" for k, err in failures)
    raise ExtensionError(f"typst: {len(failures)} collision(s) found: {summary}")
```
One pass, every offending entry enumerated in the single raised error (D-02), relocated to run BEFORE
any write and on the base `TypstBuilder` class so `TypstPDFBuilder` inherits it rather than
re-implementing it (Claude's Discretion note in CONTEXT.md).

### `casefold()`-normalized comparison, every platform, no exceptions (D-05)
**Source:** no existing analog — this is new logic the validator must apply on both sides of every
map-key comparison.
**Apply to:** every collision-map key lookup/insertion in the new validator.
```python
key = physical_path.casefold()  # comparison only -- the WRITTEN filename keeps the user's
                                 # exact bytes (builder.py:285-288's existing no-normalization
                                 # rule on the write side is unaffected)
```

### Real `sphinx-build` subprocess + `sys.executable -m sphinx` invocation
**Source:** `tests/test_typst_documents_collision_gate.py:46-71`, duplicated (by convention) in
`tests/test_pdf_render_gate.py:150-191`
**Apply to:** both new test modules (`test_two_layer_output_gate.py`,
`test_collision_validator_gate.py`)
Copy this helper verbatim into EACH new module — this repo's established convention is NOT to share
it via import.

## No Analog Found

None — every file this phase touches is a rewrite of a file this session read in full, and every new
test module has at least one directly-applicable analog already in `tests/`.

## Metadata

**Analog search scope:** `typsphinx/writer.py`, `typsphinx/builder.py` (both read in full),
`tests/test_typst_documents_collision_gate.py` (read in full), `tests/test_pdf_render_gate.py`
(read in full), `tests/test_builder_output_stem.py` (targeted read, lines 280-380),
`tests/fixtures/derived_docname_collision_gate/conf.py` (read in full), `tests/roots/` (listed)
**Files scanned:** 6 read in full/targeted, 1 directory listing
**Pattern extraction date:** 2026-08-11
