# Phase 47 gap-closure plan 13 — Pre-Fix RED Evidence

**Captured:** 2026-08-12, against the unfixed tree (this plan's own worktree, before any
`typsphinx/builder.py` change — `git diff --name-only` prints nothing for `typsphinx/` throughout
Task 1, and `git status --short` shows only the three new test artifacts as untracked).
**Binding constraint #4 compliance:** every section below records the VERBATIM raw output of a
real `sphinx-build` subprocess against this plan's own two new fixtures, run inside this plan's own
provisioned worktree venv (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`, per
`CLAUDE.md`'s mandatory worktree-isolated execution protocol; isolation independently confirmed via
`uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"`
printing a path inside this worktree). Failure mode 1's `-b typst` symptom exits 0, so — per binding
constraint #4's amended definition of RED — its RED is a content-level measurement, never an exit
code. Failure mode 2 crashes with an uncaught `TypeError`, so its RED is the verbatim traceback.

This document does NOT touch `47-RED-EVIDENCE.md` or `47-GAP-RED-EVIDENCE.md`, which belong to the
already-executed plans 47-01..47-11 and stay byte-identical throughout this plan.

---

## Failure mode 1 — ghost entry's phantom-included subtree, silent dangling label

**Fixture:** `tests/fixtures/bld03_ghost_entry_xref_gate/` — `typst_documents = [("index",
"manual.typ", "Real Master", "Probe Author"), ("ghost",)]`. `index.rst` is the real master and
carries a `:ref:` to `ghost-child-label`, which `ghost.rst` (an `:orphan:` document with its own
`toctree` listing `ghost_child`) pulls in via `ghost_child.rst`.

### `-b typst`

**Command:** `uv run python -m sphinx -b typst tests/fixtures/bld03_ghost_entry_xref_gate /tmp/red2-d`

**Raw output:**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 3 件のソースファイル
環境データを更新中[新しい設定] 3 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 33%] ghost
ソースを読み込み中...[ 67%] ghost_child
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
WARNING: typst_documents entry 1 (('ghost',)) produces no wrapper file -- entry has no target element or a non-str docname
preparing documents... Template written to /tmp/red2-d/_template.typ
done
writing output... [ghost] done
writing output... [ghost_child] done
writing output... [index] done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
build succeeded, 1 warning.
```
Exit code: 0, 1 warning — but the warning only reports the `('ghost',)` entry's own inability to
produce a wrapper; it says nothing about the consequence measured below: `index`'s cross-reference
into `ghost`'s toctree closure is still judged "safe to link".

**Verbatim emitted `index.typ`:**
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
[#heading(depth: 1, {text("Real Master")}) <index:real-master>]

par({text("GHOST-XREF-INDEX-SENTINEL-FFF")})

par({text("See ")
link(<ghost_child:ghost-child-label>, 
text("Ghost Child Target Section"))
text(".")})


}
```

**Numeric measurement that constitutes RED (exit code is unavailable here, per binding constraint
#4 — the build exits 0):**
```
$ grep -c 'link(<ghost_child:' /tmp/red2-d/index.typ
1
```
A real `link(<ghost_child:ghost-child-label>, ...)` Typst label link was emitted into the real
master's content file, pointing at a document (`ghost_child`) that is never physically
`#include()`d into `manual.typ` — the sole surviving wrapper.

### `-b typstpdf`

**Command:** `uv run python -m sphinx -b typstpdf tests/fixtures/bld03_ghost_entry_xref_gate /tmp/red2-d-pdf`

**Raw output (tail — the fatal and the surrounding traceback):**
```
WARNING: typst_documents entry 1 (('ghost',)) produces no wrapper file -- entry has no target element or a non-str docname
preparing documents... Template written to /tmp/red2-d-pdf/_template.typ
done
writing output... [ghost] done
writing output... [ghost_child] done
writing output... [index] done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
Compiling 2 master document(s) to PDF...
Typst compilation failed at /tmp/red2-d-pdf/manual.typ: TypstError: label `<ghost_child:ghost-child-label>` does not exist in the document
ERROR: Failed to compile /tmp/red2-d-pdf/manual.typ: Typst compilation failed: TypstError: label `<ghost_child:ghost-child-label>` does not exist in the document
Location: /tmp/red2-d-pdf/manual.typ
Details: label `<ghost_child:ghost-child-label>` does not exist in the document
WARNING: typst_documents entry ('ghost',) has no target element -- expected at least a (docname, target) pair

...

Traceback
=========

      File "typsphinx/builder.py", line 1492, in finish
        raise ExtensionError(
            f"typstpdf: {len(failures)} master document(s) failed: {summary}"
        )
    sphinx.errors.ExtensionError: typstpdf: 2 master document(s) failed: index: Typst compilation
    failed: TypstError: label `<ghost_child:ghost-child-label>` does not exist in the document
    Location: /tmp/red2-d-pdf/manual.typ
    Details: label `<ghost_child:ghost-child-label>` does not exist in the document; ghost:
    typst_documents entry ('ghost',) has no target element -- expected at least a (docname,
    target) pair
```
Exit code: 2 (non-zero) — this IS the exact fatal this mitigation exists to prevent, discovered
only at compile time, and it takes the well-formed sibling master's own PDF down with it:
```
$ ls /tmp/red2-d-pdf/*.pdf
ls: cannot access '/tmp/red2-d-pdf/*.pdf': No such file or directory
```
`manual.pdf` — the wrapper for the WELL-FORMED `index` entry — does not exist, even though `index`
itself has no defect of its own; the only reason it fails to compile is the dangling label the
phantom-included `ghost`/`ghost_child` subtree introduced.

**RED confirmed:**
- `test_ghost_entry_subtree_xref_degrades_typst` asserts `"link(<ghost_child:" not in scannable` —
  `False` (count 1 above), `AssertionError`, caught by `xfail(strict=True)`, reported `XFAIL`.
- `test_ghost_entry_no_dangling_label_typstpdf` asserts `"does not exist in the document" not in
  combined_output` — `False` (present verbatim above) — `AssertionError`, caught by
  `xfail(strict=True)`, reported `XFAIL`. (The same test's `manual.pdf` existence assertion also
  fails independently, since the file was never written.)
- `test_ghost_entry_excluded_from_master_include_set` (unit) asserts
  `builder._compute_master_included_docnames() == {"index"}` against a stub builder whose
  `toctree_includes = {"ghost": ["ghost_child"]}` — the pre-fix bare `if entry` filter returns
  `{"ghost", "ghost_child", "index"}` instead, `AssertionError`, caught by `xfail(strict=True)`,
  reported `XFAIL`.

<!-- planner-discipline-allow: link(<ghost_child: -->
<!-- planner-discipline-allow: does not exist in the document -->

---

## Failure mode 2 — non-hashable `entry[0]` crashes the BFS's `set` operations

**Fixture:** `tests/fixtures/bld03_unhashable_docname_gate/` — `typst_documents = [(["weird"],
"manual.typ", "Weird Master", "Probe Author"), ("index", "real.typ", "Real Master", "Probe
Author")]`. The FIRST entry's docname is a `list`, not a `str` — a plausible `conf.py` typo Sphinx
does not type-check.

### `-b typst`

**Command:** `uv run python -m sphinx -b typst tests/fixtures/bld03_unhashable_docname_gate /tmp/red2-e`

**Raw output (tail — the fatal traceback, quoted verbatim including the `builder.py` line
number):**
```
WARNING: typst_documents entry 0 ((['weird'], 'manual.typ', 'Weird Master', 'Probe Author')) produces no wrapper file -- entry has no target element or a non-str docname
preparing documents... Template written to /tmp/red2-e/_template.typ
done

...

Traceback
=========

      File "typsphinx/builder.py", line 276, in _compute_master_included_docnames
        if docname in included:
           ^^^^^^^^^^^^^^^^^^^
    TypeError: unhashable type: 'list'
```
Exit code: 2 (non-zero) — an UNCAUGHT interpreter traceback, not a named diagnostic. Note the
`_validate_output_path_collisions()` warning ABOVE the traceback already tolerates this same entry
gracefully (47-11's predicate-guarded validator) — the crash is entirely inside the fifth,
unguarded site, which runs immediately afterward in `write()`.

<!-- planner-discipline-allow: unhashable type -->

### `-b typstpdf`

**Command:** `uv run python -m sphinx -b typstpdf tests/fixtures/bld03_unhashable_docname_gate /tmp/red2-e-pdf`

**Raw output (tail):**
```
WARNING: typst_documents entry 0 ((['weird'], 'manual.typ', 'Weird Master', 'Probe Author')) produces no wrapper file -- entry has no target element or a non-str docname
preparing documents... Template written to /tmp/red2-e-pdf/_template.typ
done

...

Traceback
=========

      File "typsphinx/builder.py", line 276, in _compute_master_included_docnames
        if docname in included:
           ^^^^^^^^^^^^^^^^^^^
    TypeError: unhashable type: 'list'
```
Exit code: 2 (non-zero) — identical crash, because `_compute_master_included_docnames()` runs at
the top of the shared `write()` both builders call, well before `TypstPDFBuilder.finish()`'s own
existing non-str-docname diagnostic is ever reached.

**RED confirmed:**
- `test_unhashable_docname_skipped_gracefully_typst` asserts `result.returncode == 0` — actual `2`
  — `AssertionError`, caught by `xfail(strict=True)`, reported `XFAIL`.
- `test_unhashable_docname_reported_by_finish_typstpdf` asserts `"non-str docname" in
  combined_output` — absent (the crash preempts `finish()` entirely) — `AssertionError`, caught by
  `xfail(strict=True)`, reported `XFAIL`.
- `test_compute_master_included_docnames_tolerates_unhashable_docname` (unit) asserts the call
  returns `{"index"}` and raises nothing — it raises `TypeError: unhashable type: 'list'` instead,
  caught by `xfail(strict=True)`, reported `XFAIL`.

---

## Full-module raw pytest transcript (six xfail / two pass, zero xpass)

**Command:** `uv run pytest tests/test_master_include_set_predicate_gate.py -q -rxX`

**Raw output:**
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 8 items

tests/test_master_include_set_predicate_gate.py xxxxxx..                 [100%]

=========================== short test summary info ============================
XFAIL tests/test_master_include_set_predicate_gate.py::TestGhostEntryXrefRenderGate::test_ghost_entry_subtree_xref_degrades_typst
XFAIL tests/test_master_include_set_predicate_gate.py::TestGhostEntryXrefRenderGate::test_ghost_entry_no_dangling_label_typstpdf
XFAIL tests/test_master_include_set_predicate_gate.py::TestGhostEntryIncludeSetUnit::test_ghost_entry_excluded_from_master_include_set
XFAIL tests/test_master_include_set_predicate_gate.py::TestUnhashableDocnameRenderGate::test_unhashable_docname_skipped_gracefully_typst
XFAIL tests/test_master_include_set_predicate_gate.py::TestUnhashableDocnameRenderGate::test_unhashable_docname_reported_by_finish_typstpdf
XFAIL tests/test_master_include_set_predicate_gate.py::TestUnhashableDocnameIncludeSetUnit::test_compute_master_included_docnames_tolerates_unhashable_docname
========================= 2 passed, 6 xfailed in 2.57s =========================
```
Exit code: 0. Six `XFAIL`, two `passed`, zero `xpassed`, zero `failed`, zero `error` — the two green
invariance guards (`test_well_formed_masters_still_yield_full_toctree_closure`,
`test_empty_typst_documents_still_yields_empty_set`) already pass on the unfixed tree and are
asserted to keep passing after Task 2's filter change.

`git diff --name-only` prints nothing for `typsphinx/` throughout this task — confirmed again
immediately after this transcript. `tests/test_collision_predicate_completeness_gate.py` (the
sibling gap-closure plan 47-11's gate) still reports `11 passed`, unmodified.

## Post-fix GREEN

Captured after Task 2 landed: `_compute_master_included_docnames()`'s masters-comprehension now
filters via `_is_usable_typst_documents_entry(entry)` instead of the bare `if entry` truthiness
test, and both docstrings were corrected. Every command below is re-run verbatim against the same
two fixtures.

### Failure mode 1 — ghost entry, post-fix

**`-b typst`:** `uv run python -m sphinx -b typst tests/fixtures/bld03_ghost_entry_xref_gate /tmp/green2-d`

**Raw output (tail):**
```
WARNING: typst_documents entry 1 (('ghost',)) produces no wrapper file -- entry has no target element or a non-str docname
preparing documents... Template written to /tmp/green2-d/_template.typ
done
writing output... [ghost] done
writing output... [ghost_child] done
writing output... [index]WARNING: cross-reference to non-included document 'ghost_child' rendered as plain text (typstpdf includes only toctree-reachable documents): Ghost Child Target Section
 done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
build succeeded, 2 warnings.
```
Exit code: 0, now 2 warnings — the existing under-length-entry warning PLUS the existing
cross-document-degrade warning, both correctly naming the ghost-child consequence.

**Numeric measurement:**
```
$ grep -c 'link(<ghost_child:' /tmp/green2-d/index.typ
0
$ grep -c 'Ghost Child Target Section' /tmp/green2-d/index.typ
1
```
The dangling label link is gone; the reference's text still renders as plain inline content.

**`-b typstpdf`:** `uv run python -m sphinx -b typstpdf tests/fixtures/bld03_ghost_entry_xref_gate /tmp/green2-d-pdf`

**Raw output (tail):**
```
writing output... [index]WARNING: cross-reference to non-included document 'ghost_child' rendered as plain text (typstpdf includes only toctree-reachable documents): Ghost Child Target Section
 done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
Compiling 2 master document(s) to PDF...
Generated PDF: /tmp/green2-d-pdf/manual.pdf
WARNING: typst_documents entry ('ghost',) has no target element -- expected at least a (docname, target) pair

...

sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: ghost: typst_documents entry
('ghost',) has no target element -- expected at least a (docname, target) pair
```
Exit code: 2 (non-zero) — but now for the CORRECT reason (D-02's attempt-all-then-raise contract):
only the malformed `ghost` entry fails, with the intended `has no target element` diagnostic, and
NO `does not exist in the document` fatal appears anywhere. `manual.pdf` — the well-formed
`index`/`manual.typ` master — IS produced:
```
$ ls /tmp/green2-d-pdf/manual.pdf
/tmp/green2-d-pdf/manual.pdf
$ head -c4 /tmp/green2-d-pdf/manual.pdf
%PDF
```

### Failure mode 2 — unhashable docname, post-fix

**`-b typst`:** `uv run python -m sphinx -b typst tests/fixtures/bld03_unhashable_docname_gate /tmp/green2-e`

**Raw output (tail):**
```
WARNING: typst_documents entry 0 ((['weird'], 'manual.typ', 'Weird Master', 'Probe Author')) produces no wrapper file -- entry has no target element or a non-str docname
preparing documents... Template written to /tmp/green2-e/_template.typ
done
writing output... [index] done
typst: wrote 1 wrapper file(s) -- compile these: real.typ
build succeeded, 1 warning.
```
Exit code: 0. No traceback, no `TypeError`, no `unhashable type` anywhere — the graceful
warn-and-skip every other predicate-guarded site already guarantees now covers this fifth site
too. Both `index.typ` and `real.typ` exist.

**`-b typstpdf`:** already-covered by `finish()`'s existing non-str-docname branch, now reachable
for the first time because `_compute_master_included_docnames()` no longer crashes before
`finish()` runs -- `"non-str docname"` appears in the combined output, `TypeError` does not, and
`real.pdf` exists.

### Full-module raw pytest transcript (eight passed, zero xfail, zero xpass)

**Command:** `uv run pytest tests/test_master_include_set_predicate_gate.py -q -rxX`

**Raw output:**
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 8 items

tests/test_master_include_set_predicate_gate.py ........                 [100%]

============================== 8 passed in 2.49s ===============================
```

### Behavioural proof of the fix, independent of source text

```
$ uv run python -c "import types, typsphinx.builder as b; f=b.TypstBuilder._compute_master_included_docnames; o=type('X',(),{'config':types.SimpleNamespace(typst_documents=[('index','manual.typ','T','A'),('ghost',)]),'env':types.SimpleNamespace(toctree_includes={'ghost':['ghost_child']})})(); print(sorted(f(o)))"
['index']
$ uv run python -c "import types, typsphinx.builder as b; f=b.TypstBuilder._compute_master_included_docnames; o=type('X',(),{'config':types.SimpleNamespace(typst_documents=[(['weird'],'manual.typ','T','A'),('index','real.typ','T','A')]),'env':types.SimpleNamespace(toctree_includes={})})(); print(sorted(f(o)))"
['index']
$ uv run python -c "import inspect, typsphinx.builder as b; s=inspect.getsource(b.TypstBuilder._compute_master_included_docnames); print('_is_usable_typst_documents_entry' in s)"
True
$ uv run python -c "import typsphinx.builder as b; d=b._is_usable_typst_documents_entry.__doc__; print('FIVE' in d, '_compute_master_included_docnames' in d)"
True True
$ uv run python -c "import typsphinx.builder as b; print(b._is_usable_typst_documents_entry(()), b._is_usable_typst_documents_entry(('index',)), b._is_usable_typst_documents_entry((123,'t.typ')), b._is_usable_typst_documents_entry(('index','t.typ')))"
False False False True
```
The predicate's own input/output pairs are unchanged by its docstring correction.

### Full-suite and lint/type trio

```
$ uv run pytest -q
================= 1042 passed, 5 skipped in 210.12s (0:03:30) ==================
$ uv run black --check .
All done! (270 files unchanged)
$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```
`uv run ruff check .` could not run in this worktree -- a pre-existing, already-acknowledged
NixOS environment limitation (`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`;
STATE.md Deferred Items: "Does not block SC#3, which takes lint authority from CI"). Unrelated to
this plan's changes; CI's `lint` job is authoritative.

### Legacy regression modules, unmodified

```
$ uv run pytest tests/test_collision_predicate_completeness_gate.py tests/test_missing_and_malformed_master_gate.py tests/test_non_str_docname_gate.py tests/test_xref_orphan_degrade_render_gate.py tests/test_citation_degradation_gate.py -q
================= 31 passed in 7.23s =================
```
`git diff --stat` is empty for all five modules — the four already-wired sites' behaviour and the
existing degrade/citation gates all stay byte-for-byte, proving this plan's fifth-site fix did not
disturb any of BLD-02's, BLD-03's four already-wired sites', or GATE-02's existing contracts.
