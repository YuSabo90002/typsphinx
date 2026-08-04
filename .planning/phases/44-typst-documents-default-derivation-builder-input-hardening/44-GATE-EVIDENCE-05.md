# Phase 44 Plan 05 — Gate Evidence 05

CR-01 gap closure. All output below was produced by commands run in this
plan's own execution session (worktree `agent-afea23cfd766dd160`), never
transcribed from a planning document.

## 1. Scope

44-VERIFICATION.md's `gaps:` frontmatter block scored two `missing:` items
against this phase's own goal ("a user who follows the Quick Start exactly
gets a PDF"), quoted verbatim:

1. `_resolve_output_stem` never checks a resolved stem's collision against
   `self.env.found_docs` or the reserved `_template` basename, so an
   ordinary project name that slugifies onto an existing docname silently
   destroys that document's output (`-b typst`, exit 0, no warning) or
   hard-fails the PDF compile (`-b typstpdf`, `TypstError: cyclic import`).
2. Neither collision kind (docname collision, `_template` clobber) is
   gate-tested on either path (derived-default, explicit `typst_documents`)
   — four real `sphinx-build` subprocess scenarios are missing entirely.

**WR-01** (the `None`-vs-empty-list warning wording at
`builder.py:929-941`) and **IN-01** (the vacuous `"Nothing to compile"`
assertion at `tests/test_default_typst_documents_gate.py:120`) are
explicitly **owner-excluded** from this plan (classified non-blocking by the
verifier) — recorded as deferred notes in § 7, not planned as work.

## 2. RED — derived-default docname collision

Both commands below were run against the unmodified `typsphinx/builder.py`
(no collision guard), before the guard was added.

### `pytest tests/test_typst_documents_collision_gate.py -q`

```
$ uv run python -m pytest tests/test_typst_documents_collision_gate.py -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-afea23cfd766dd160
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests/test_typst_documents_collision_gate.py FF                          [100%]

=================================== FAILURES ===================================
_ TestTypstDocumentsCollisionGate.test_derived_default_docname_collision_keeps_both_documents _
...
E       AssertionError: Expected index.typ (the degraded master fallback) on disk:
E         stdout: ...build succeeded.
E       assert False
E        +  where False = exists()
E        +    where exists = PosixPath('.../build/index.typ').exists

_ TestTypstDocumentsCollisionGate.test_derived_default_docname_collision_produces_pdf _
...
E       AssertionError: Expected a successful PDF build despite the docname collision:
E         stderr: Typst compilation failed at .../build/chapter1.typ: TypstError: cyclic import
E         ...
E       assert 2 == 0

=========================== short test summary info ============================
FAILED tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_derived_default_docname_collision_keeps_both_documents
FAILED tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_derived_default_docname_collision_produces_pdf
============================== 2 failed in 0.60s ===============================
```

Both new tests fail (RED), for exactly the mechanism CR-01 describes.

### Hand build — `-b typst`

```
$ uv run python -m sphinx -b typst tests/fixtures/derived_docname_collision_gate /tmp/gate05-red-typst
...
writing output... [chapter1] done
writing output... [index] done
build succeeded.

$ echo "EXIT=$?"
EXIT=0

$ ls /tmp/gate05-red-typst/*.typ
/tmp/gate05-red-typst/_template.typ
/tmp/gate05-red-typst/chapter1.typ

$ grep -c 'UNIQUE-CHAPTER-MARKER-XYZ' /tmp/gate05-red-typst/chapter1.typ
0
```

**Exit 0, `build succeeded`, no warning.** Only `chapter1.typ` is on disk —
it is the **index** master's own content (self-referential
`include("chapter1.typ")`); `chapter1.rst`'s own rendered body
(`UNIQUE-CHAPTER-MARKER-XYZ`) is not present anywhere (grep count 0).
`index.typ` never exists.

### Hand build — `-b typstpdf`

```
$ uv run python -m sphinx -b typstpdf tests/fixtures/derived_docname_collision_gate /tmp/gate05-red-typstpdf
...
writing output... [chapter1] done
writing output... [index] done
Compiling 1 master document(s) to PDF...
Typst compilation failed at /tmp/gate05-red-typstpdf/chapter1.typ: TypstError: cyclic import
ERROR: Failed to compile /tmp/gate05-red-typstpdf/chapter1.typ: Typst compilation failed: TypstError: cyclic import
...
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: cyclic import
Location: /tmp/gate05-red-typstpdf/chapter1.typ
Details: cyclic import
...

$ echo "EXIT=$?"
EXIT=2
```

**Exit 2**, hard failure — `TypstError: cyclic import` at `chapter1.typ`,
exactly reproducing 44-REVIEW.md's orchestrator re-measurement § C.

RED commit SHA: `87dd26333dcce32056bf9133e91fb60599e60c4e`
(`test(44-05): add failing collision gate for the derived-default docname
collision` — production code untouched, confirmed by
`git show --stat 87dd26333dcce32056bf9133e91fb60599e60c4e --name-only | grep -c '^typsphinx/'` → `0`).

## 3. GREEN — derived-default docname collision

After adding the collision guard to `_resolve_output_stem` in
`typsphinx/builder.py` (commit
`edca2de24f8f6077a6db8c719fb22080321ebdc8`,
`fix(44-05): reject a typst_documents target name colliding with a docname
or the reserved template`).

### `pytest tests/test_typst_documents_collision_gate.py -q`

```
$ uv run python -m pytest tests/test_typst_documents_collision_gate.py -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-afea23cfd766dd160
configfile: pyproject.toml
plugins: cov-7.1.0
collected 2 items

tests/test_typst_documents_collision_gate.py ..                          [100%]

============================== 2 passed in 0.56s ===============================
```

### Hand build — `-b typst`

```
$ uv run python -m sphinx -b typst tests/fixtures/derived_docname_collision_gate /tmp/gate05-green-typst
...
writing output... [chapter1] done
writing output... [index]WARNING: typst_documents target name 'chapter1.typ' for docname 'index' collides with an existing document or the reserved template file -- falling back to 'index'
 done
build succeeded, 1 warning.

$ echo "EXIT=$?"
EXIT=0

$ ls /tmp/gate05-green-typst/*.typ
/tmp/gate05-green-typst/_template.typ
/tmp/gate05-green-typst/chapter1.typ
/tmp/gate05-green-typst/index.typ

$ grep -c 'UNIQUE-CHAPTER-MARKER-XYZ' /tmp/gate05-green-typst/chapter1.typ
1
```

**Exit 0, both `.typ` files present.** `chapter1.typ` carries the chapter's
own body marker exactly once (no overwrite); `index.typ` is the degraded
master fallback; the console carries the collision WARNING (observed on
stdout, interleaved with the `writing output...` progress line — this
project's warnings are not consistently routed to stderr, so the gate
module asserts against `result.stdout + result.stderr`, a deliberate
divergence from the plan's stderr-only default noted here per Step 2's
own instruction).

### Hand build — `-b typstpdf`

```
$ uv run python -m sphinx -b typstpdf tests/fixtures/derived_docname_collision_gate /tmp/gate05-green-typstpdf
...
writing output... [chapter1] done
writing output... [index]WARNING: typst_documents target name 'chapter1.typ' for docname 'index' collides with an existing document or the reserved template file -- falling back to 'index'
 done
Compiling 1 master document(s) to PDF...
WARNING: typst_documents target name 'chapter1.typ' for docname 'index' collides with an existing document or the reserved template file -- falling back to 'index'
Generated PDF: /tmp/gate05-green-typstpdf/index.pdf
build succeeded, 2 warnings.

$ echo "EXIT=$?"
EXIT=0

$ ls /tmp/gate05-green-typstpdf/
_template.typ
chapter1.typ
index.pdf
index.typ

$ head -c4 /tmp/gate05-green-typstpdf/index.pdf
%PDF
```

**Exit 0, `index.pdf` present, first four bytes `%PDF`.** No `cyclic
import` text anywhere in the output. The collision warning fires **twice**
(once from `write_doc`, once from `finish`, since both call
`_resolve_output_stem`) — matching planning measurement 7's predicted
arity, consistent with the pre-existing D-06/D-07 warnings' behaviour.

### Acceptance-criteria commands (all measured this session)

- `uv run python -m pytest tests/test_typst_documents_collision_gate.py -q` → `2 passed`
- `sed -n '/def _resolve_output_stem/,/def _directory_preserving_relpath/p' typsphinx/builder.py | grep -c 'found_docs'` → `3`
- `sed -n '/def _resolve_output_stem/,/def _directory_preserving_relpath/p' typsphinx/builder.py | grep -c '_directory_preserving_relpath'` → `3`
- `grep -c 'collides with an existing document' typsphinx/builder.py` → `1`
- `grep -c 'typst_documents *=' tests/fixtures/derived_docname_collision_gate/conf.py` → `0`
- `grep -c 'Chapter 1' tests/fixtures/derived_docname_collision_gate/conf.py` → `3`
- `git log --oneline -2` →
  ```
  edca2de fix(44-05): reject a typst_documents target name colliding with a docname or the reserved template
  87dd263 test(44-05): add failing collision gate for the derived-default docname collision
  ```

## 4. RED — reserved-template clobber and the explicit-entry path

Three new fixtures added (`derived_template_collision_gate`,
`explicit_docname_collision_gate`, `explicit_template_collision_gate`), three
new subprocess tests added to `test_typst_documents_collision_gate.py`, and
three new unit tests added to `test_builder_output_stem.py` (test file
diffs committed separately; production code untouched at this point).

### Revert procedure

```
$ git cat-file -e 87dd26333dcce32056bf9133e91fb60599e60c4e && echo "SHA reachable: OK"
SHA reachable: OK

$ git checkout 87dd26333dcce32056bf9133e91fb60599e60c4e -- typsphinx/builder.py

$ grep -c 'collides with an existing document' typsphinx/builder.py
0
```

The guard is confirmed absent (grep count `0`).

### `pytest tests/test_typst_documents_collision_gate.py tests/test_builder_output_stem.py -q`

```
$ uv run python -m pytest tests/test_typst_documents_collision_gate.py tests/test_builder_output_stem.py -q
collected 32 items

tests/test_typst_documents_collision_gate.py FFFFF                       [ 15%]
tests/test_builder_output_stem.py ........................FF.            [100%]

=========================== short test summary info ============================
FAILED tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_derived_default_docname_collision_keeps_both_documents
FAILED tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_derived_default_docname_collision_produces_pdf
FAILED tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_derived_default_template_collision_preserves_shared_template
FAILED tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_explicit_target_docname_collision_keeps_both_documents
FAILED tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_explicit_target_template_collision_preserves_shared_template
FAILED tests/test_builder_output_stem.py::test_resolve_output_stem_falls_back_on_docname_collision
FAILED tests/test_builder_output_stem.py::test_resolve_output_stem_falls_back_on_reserved_template_name
7 failed, 25 passed in 1.47s
```

All seven new tests fail (the two subprocess tests from Task 1 are a free
re-proof, already established RED in § 2, and are not counted again here
since they were not re-collected against a fresh checkout state distinct
from § 2). `test_resolve_output_stem_tolerates_env_without_found_docs`
passes even against the pre-fix code (the 25 passing count includes it) --
correctly, since pre-fix `_resolve_output_stem` performs no `found_docs`
lookup at all, so there is nothing for that regression guard to catch yet.
This is the expected shape: the guard's ABSENCE is exactly what the other
two collision unit tests catch (`assert 'chapter1' == 'index'` and
`assert '_template' == 'index'`, both actual observed failures pasted
above verbatim).

### Hand measurement — `derived_template_collision_gate`

```
$ uv run python -m sphinx -b typst tests/fixtures/derived_template_collision_gate /tmp/gate05-red-derived-template
...
build succeeded.

$ echo "EXIT=$?"
EXIT=0

$ ls -l /tmp/gate05-red-derived-template/_template.typ
-rw-r--r-- 1 yuta users 528  8月  4 16:52 /tmp/gate05-red-derived-template/_template.typ

$ grep -c '^#let project' /tmp/gate05-red-derived-template/_template.typ
0
```

**Divergence from the planner's table, recorded plainly:** planning
measurement 8 (44-REVIEW.md's orchestrator re-measurement § D) recorded
`460 bytes` pre-fix for `_template.typ`, measured against a different
fixture (`project = "_Template"` with a `CHAPTERBODY`-marker body). This
plan's own fixture (`DERIVED-TEMPLATE-COLLISION-BODY` marker, different
body text length) measures `528 bytes` instead. The MEASURED value here
(528 bytes, `#let project` count 0) is what stands for this fixture; the
byte-count divergence is expected (different source body text) and does
not affect the pass/fail semantics -- both measurements agree on the load-
bearing fact: **the `#let project` definition is destroyed** (count 0 in
both).

### Hand measurement — `explicit_template_collision_gate`

```
$ uv run python -m sphinx -b typst tests/fixtures/explicit_template_collision_gate /tmp/gate05-red-explicit-template
...
build succeeded.

$ echo "EXIT=$?"
EXIT=0

$ ls -l /tmp/gate05-red-explicit-template/_template.typ
-rw-r--r-- 1 yuta users 578  8月  4 16:52 /tmp/gate05-red-explicit-template/_template.typ

$ grep -c '^#let project' /tmp/gate05-red-explicit-template/_template.typ
0
```

Same result: `#let project` destroyed (count 0) via the explicit-entry path.

### Restore procedure and proof

```
$ git checkout HEAD -- typsphinx/builder.py

$ git status --porcelain typsphinx/builder.py
(no output)

$ grep -c 'collides with an existing document' typsphinx/builder.py
1
```

The production file is provably restored: no pending diff, and the guard
is back.

## 5. GREEN — all four scenarios plus the unit-level edge tests

### `pytest tests/test_typst_documents_collision_gate.py tests/test_builder_output_stem.py -q`

```
$ uv run python -m pytest tests/test_typst_documents_collision_gate.py tests/test_builder_output_stem.py -q
collected 32 items

tests/test_typst_documents_collision_gate.py .....                       [ 15%]
tests/test_builder_output_stem.py ...........................            [100%]

============================== 32 passed in 1.47s ==============================
```

All 32 tests pass (5 subprocess collision gates + 27 unit stem tests, 24
pre-existing + 3 new).

### Hand measurement — `derived_template_collision_gate` (GREEN)

```
$ uv run python -m sphinx -b typst tests/fixtures/derived_template_collision_gate /tmp/gate05-green-derived-template
...
writing output... [index]WARNING: typst_documents target name '_template.typ' for docname 'index' collides with an existing document or the reserved template file -- falling back to 'index'
 done
build succeeded, 1 warning.

$ echo "EXIT=$?"
EXIT=0

$ ls -l /tmp/gate05-green-derived-template/_template.typ
-rw-r--r-- 1 yuta users 2438  8月  4 16:52 /tmp/gate05-green-derived-template/_template.typ

$ grep -c '^#let project' /tmp/gate05-green-derived-template/_template.typ
1

$ ls /tmp/gate05-green-derived-template/index.typ
/tmp/gate05-green-derived-template/index.typ
```

`_template.typ` restored to its full 2438-byte content (matching
44-GATE-EVIDENCE-01.md's GREEN measurement of the same file), `#let
project` count 1, `index.typ` present as the degraded fallback.

### Hand measurement — `explicit_template_collision_gate` (GREEN)

```
$ uv run python -m sphinx -b typst tests/fixtures/explicit_template_collision_gate /tmp/gate05-green-explicit-template
...
writing output... [index]WARNING: typst_documents target name '_template.typ' for docname 'index' collides with an existing document or the reserved template file -- falling back to 'index'
 done
build succeeded, 1 warning.

$ echo "EXIT=$?"
EXIT=0

$ ls -l /tmp/gate05-green-explicit-template/_template.typ
-rw-r--r-- 1 yuta users 2438  8月  4 16:52 /tmp/gate05-green-explicit-template/_template.typ

$ grep -c '^#let project' /tmp/gate05-green-explicit-template/_template.typ
1

$ ls /tmp/gate05-green-explicit-template/index.typ
/tmp/gate05-green-explicit-template/index.typ
```

Same result via the explicit-entry path: `#let project` restored, `index.typ`
present.

### Acceptance-criteria commands (all measured this session)

- `uv run python -m pytest tests/test_typst_documents_collision_gate.py tests/test_builder_output_stem.py -q` → `32 passed`
- `uv run python -m pytest tests/test_typst_documents_collision_gate.py --collect-only -q` → `5 tests collected`
- `git status --porcelain typsphinx/builder.py` → (no output)
- `grep -c 'collides with an existing document' typsphinx/builder.py` → `1`
- `grep -c '_Template' tests/fixtures/derived_template_collision_gate/conf.py` → `3`
- `grep -c 'chapter1.typ' tests/fixtures/explicit_docname_collision_gate/conf.py` → `2`
- `grep -c '_template.typ' tests/fixtures/explicit_template_collision_gate/conf.py` → `4`
- `grep -c 'test_resolve_output_stem_tolerates_env_without_found_docs' tests/test_builder_output_stem.py` → `1`

### Scenario-to-test-node-id mapping

| # | Scenario | Test node id |
|---|----------|--------------|
| 1 | Derived-default docname collision | `tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_derived_default_docname_collision_keeps_both_documents` (and its `-b typstpdf` counterpart `test_derived_default_docname_collision_produces_pdf`) |
| 2 | Derived-default reserved-template clobber | `tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_derived_default_template_collision_preserves_shared_template` |
| 3 | Explicit `typst_documents` docname collision | `tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_explicit_target_docname_collision_keeps_both_documents` |
| 4 | Explicit `typst_documents` reserved-template clobber | `tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_explicit_target_template_collision_preserves_shared_template` |

Unit-level edge coverage (all in `tests/test_builder_output_stem.py`):
`test_resolve_output_stem_falls_back_on_docname_collision`,
`test_resolve_output_stem_falls_back_on_reserved_template_name`,
`test_resolve_output_stem_tolerates_env_without_found_docs`.

<!-- gsd:write-continue -->
