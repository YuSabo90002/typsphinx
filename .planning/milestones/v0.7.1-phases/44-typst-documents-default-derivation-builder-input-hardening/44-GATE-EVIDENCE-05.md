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

## 6. Regression boundary and phase gate

### Repo-wide pre-existing collision re-measurement

Re-measured (not trusted from the planner's table) with a script that walks
every non-`.venv` `conf.py`, statically parses (via `ast`) each
`typst_documents` assignment's literal `(docname, target, ...)` entries,
computes the effective outdir-relative path the same way
`_resolve_output_stem` + `_directory_preserving_relpath` do (suffix strip,
D-06/D-07 path-guard basename reduction, directory-qualification against
the docname), and reports any whose effective path equals a sibling
document's docname or `_template`, against the sibling `.rst`/`.md` files
in that fixture's own directory.

```
$ uv run python <scan-script>
conf.py files scanned (non-.venv): 111
conf.py files mentioning typst_documents: 111
conf.py files with a parseable typst_documents assignment: 108
unparseable/non-literal entries: 1
  - (tests/fixtures/non_str_docname_gate/conf.py, "non-literal entry (None, 'manual.typ')")
COLLISIONS FOUND: 2
  - (tests/fixtures/explicit_docname_collision_gate/conf.py, 'index', 'chapter1.typ', 'chapter1')
  - (tests/fixtures/explicit_template_collision_gate/conf.py, 'index', '_template.typ', '_template')
```

**Divergence from the planner's table, stated plainly:** planning
measurement 5 recorded "0 collisions" for the pre-existing repo. This
re-measurement's raw count is **2, not 0** — but both hits are
`explicit_docname_collision_gate/conf.py` and
`explicit_template_collision_gate/conf.py`, the two fixtures **this very
plan created in Task 2**, whose entire purpose is to collide by design (the
explicit-`typst_documents` half of CR-01's coverage). Excluding this plan's
own deliberately-colliding gate fixtures, the re-measured count over every
OTHER conf.py in the repo (106 of the 108 parseable files) is **0**,
confirming the planner's measurement for the pre-existing tree. This is not
a real pre-existing defect — it is the two new tests behaving exactly as
designed. The 3 non-parseable mentions (`derived_docname_collision_gate`,
`derived_template_collision_gate`, `default_typst_documents_gate`) are the
fixtures whose conf.py mentions "typst_documents" only in a header comment
(no assignment at all, by design — they exercise the derived default,
which this static scan cannot see since it never appears literally in
conf.py). The 1 unparseable entry
(`tests/fixtures/non_str_docname_gate/conf.py`) is BLD-01's own
deliberately-malformed fixture — its second `typst_documents` entry uses
the integer literal `123` as a docname, which this scan's `str`-only
literal filter correctly excludes rather than mis-comparing.

### `uv run python -m pytest -q` (full suite)

**Worktree provisioning note:** this worktree's `.venv/bin/uv` and
`.venv/bin/ruff` are generic-linux ELF wheels that NixOS cannot exec
directly (exit 127) -- the documented NixOS-sandbox shim
(`ln -sf <nix-store uv> .venv/bin/uv`, `ln -sf <main-tree's own
patchelf'd ruff> .venv/bin/ruff`) was re-applied this session, matching
`44-GATE-EVIDENCE-01.md` § 6(b) and `44-GATE-EVIDENCE-04.md` § 5. Without
it, 45 tests in `tests/test_integration_{multi_doc,nested_toctree}.py`
fail with pre-existing environmental noise (subprocess `uv run
sphinx-build` calls that cannot exec) -- observed once this session before
the shim was applied, confirmed unrelated to this plan's diff, and not
recorded as a defect here.

```
$ .venv/bin/uv --version
uv 0.11.25 (x86_64-unknown-linux-gnu)
$ .venv/bin/ruff --version
ruff 0.15.20

$ uv run python -m pytest -q
================== 863 passed, 1 skipped in 78.99s (0:01:18) ===================
```

**Exit status: 0.** `863 passed, 1 skipped` is **greater than or equal to**
the `855 passed, 1 skipped` baseline recorded in `44-GATE-EVIDENCE-04.md`
§ 5, by **exactly 8** -- the number of tests this plan added (2 subprocess
tests in Task 1 + 3 subprocess tests + 3 unit tests in Task 2 = 8). No
divergence.

### Slow corpus gate, selected and green

This repository configures no `-m` filter anywhere (`pyproject.toml`
`addopts = "-v --strict-markers"`, no `markers`-based deselection; every
`tox.ini` environment calls plain `pytest {posargs:tests/}`; CI invokes
tox environments, never `pytest -m` directly) — confirmed again this
session:

```
$ grep -n "addopts\|markers" pyproject.toml
79:addopts = "-v --strict-markers"
80:markers = [
```

So the full-suite run above genuinely includes the slow corpus gate,
proven by name:

```
$ uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -q
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-afea23cfd766dd160
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests/test_corpus_gate.py .                                              [100%]

============================== 1 passed in 13.90s ===============================
```

### Lint and type gate

```
$ uv run black --check .
All done! ✨ 🍰 ✨
230 files would be left unchanged.
```
**Exit status: 0.**

```
$ uv run ruff check .
All checks passed!
```
**Exit status: 0.**

```
$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```
**Exit status: 0.**

**Deviation recorded:** `black --check .` initially failed
(`would reformat tests/test_typst_documents_collision_gate.py`) — a
line-wrap the multi-line constant assignment I added in Task 2 exceeded
the 88-column limit. Auto-fixed under Rule 1 (directly caused by this
plan's own diff, surfaced by this task's own `<verify>` step): ran `uv run
black tests/test_typst_documents_collision_gate.py`, re-ran `black
--check .` to confirm clean, and committed the reformat separately
(`style(44-05): black-format DERIVED_TEMPLATE_COLLISION_FIXTURE_DIR
line-wrap`) before this section was written. No behavior change; the
collision gate tests were re-run and still pass (`5 passed`) after the
reformat.

### Manifests and typing-import prohibition

```
$ git diff --stat 7ad417e6d16a0b3891023f2b85db677ede02e24f..HEAD -- pyproject.toml uv.lock
(no output)
```

**Empty diff — no new runtime dependency.**

```
$ grep -c 'from typing import List, Set, Tuple' typsphinx/builder.py
1
```

The `List`/`Set`/`Tuple` typing imports at the top of `typsphinx/builder.py`
are untouched by this plan's diff:

```
$ git diff 7ad417e6d16a0b3891023f2b85db677ede02e24f..HEAD -- typsphinx/builder.py | head -20
diff --git a/typsphinx/builder.py b/typsphinx/builder.py
...
@@ -178,7 +178,13 @@ class TypstBuilder(Builder):
             ``logger.warning`` is emitted and a safe fallback is returned
             instead -- ``path.basename`` of the offending stem for a
             path-bearing target (D-06/D-07), or the docname itself for a
-            degenerate target (edge: empty).
+            degenerate target (edge: empty). When the resolved stem's
...
```

Only the docstring and the new guard branch (further down the diff) are
touched — line 13's `from typing import List, Set, Tuple` never appears in
either side of the diff.

No test was skipped, `xfail`-ed, deselected, or weakened anywhere in this
plan's diff — confirmed by grepping the diff itself:

```
$ git diff 7ad417e6d16a0b3891023f2b85db677ede02e24f..HEAD -- tests/ | grep -E '^\+.*(pytest\.mark\.skip|pytest\.mark\.xfail|pytest\.skip\()' | grep -v skipif
(no output)
```

## 7. Gap-closure verdict and deferred notes

| # | `missing:` item (44-VERIFICATION.md, verbatim) | Evidence | Status |
|---|--------------------------------------------------|----------|--------|
| 1 | `_resolve_output_stem` never checks a resolved stem's collision against `self.env.found_docs` or the reserved `_template` basename, so an ordinary project name that slugifies onto an existing docname silently destroys that document's output (`-b typst`, exit 0, no warning) or hard-fails the PDF compile (`-b typstpdf`, `TypstError: cyclic import`). | § 2-3 (RED/GREEN, derived-default docname collision); § 4-5 (RED/GREEN, derived-default template collision, explicit docname collision, explicit template collision); guard implemented at `typsphinx/builder.py::_resolve_output_stem`. Test node ids: `tests/test_typst_documents_collision_gate.py::TestTypstDocumentsCollisionGate::test_derived_default_docname_collision_keeps_both_documents`, `::test_derived_default_docname_collision_produces_pdf`, `::test_derived_default_template_collision_preserves_shared_template`; unit tests `tests/test_builder_output_stem.py::test_resolve_output_stem_falls_back_on_docname_collision`, `::test_resolve_output_stem_falls_back_on_reserved_template_name`, `::test_resolve_output_stem_tolerates_env_without_found_docs`. | **GAP CLOSED** |
| 2 | Neither collision kind (docname collision, `_template` clobber) is gate-tested on either path (derived-default, explicit `typst_documents`) — four real `sphinx-build` subprocess scenarios are missing entirely. | § 5's scenario-to-test-node-id table: all four scenarios (derived-docname, derived-template, explicit-docname, explicit-template) covered by real `sphinx-build` subprocess tests in `tests/test_typst_documents_collision_gate.py` (5 tests total, one scenario has both a `-b typst` and a `-b typstpdf` variant). Node ids: `test_derived_default_docname_collision_keeps_both_documents`, `test_derived_default_docname_collision_produces_pdf`, `test_derived_default_template_collision_preserves_shared_template`, `test_explicit_target_docname_collision_keeps_both_documents`, `test_explicit_target_template_collision_preserves_shared_template`. | **GAP CLOSED** |

**What the fix costs.** In the collision case the derived master is
written as `index.typ` (or `index.pdf`), not `<project>.typ` — a
deliberate degradation away from SC#1's promised filename shape, traded
for not destroying a real document or the shared template infrastructure.
SC#1's own evidence (`44-GATE-EVIDENCE-01.md`) is unaffected: its fixture
(`default_typst_documents_gate`, `project = "Quickstart Default Gate"`) is
collision-free by construction and was re-measured green in this plan's
own full-suite run (§ 6, `863 passed`).

**Deferred notes, recorded not planned:**

- **WR-01** (the `None`-vs-empty-list warning wording at
  `builder.py:929-941`) — owner-excluded from this plan per the objective's
  explicit scope statement. Classified non-blocking by the verifier.
- **IN-01** (the vacuous `"Nothing to compile"` assertion in
  `tests/test_default_typst_documents_gate.py:120-123`) — owner-excluded
  from this plan per the objective's explicit scope statement. Classified
  non-blocking by the verifier.
- **Master-vs-master target collision** (two explicit `typst_documents`
  entries naming the SAME target as each other) — planning measurement 8
  noted this is a different mechanism (neither stem is in `found_docs`,
  since neither target is itself a docname), so this plan's guard does not
  fire on it. Not required by either of 44-VERIFICATION.md's `missing:`
  items; recorded here as a deferred observation, not a gap.
