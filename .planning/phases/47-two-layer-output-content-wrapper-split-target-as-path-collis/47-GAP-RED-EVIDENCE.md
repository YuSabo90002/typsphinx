# Phase 47 gap-closure plan 11 — Pre-Fix RED Evidence

**Captured:** 2026-08-12, against the unfixed tree (this plan's own worktree, before any
`typsphinx/builder.py` change — `git diff --name-only -- typsphinx/` prints nothing throughout
Task 1).
**Binding constraint #4 compliance:** every section below records the VERBATIM raw output of a
real `sphinx-build` subprocess against this plan's own three new fixtures, run inside this plan's
own provisioned worktree venv (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev`,
per `CLAUDE.md`'s mandatory worktree-isolated execution protocol). All three shapes exit 0 on the
unfixed tree, so — per binding constraint #4's amended definition of RED — each section's RED is a
content-level or template-symbol measurement, never an exit code.

This document does NOT touch `47-RED-EVIDENCE.md`, which belongs to the executed plans 47-01..47-10
and stays byte-identical throughout this plan.

---

## BLD-02 — path shape: `./manual.typ` vs `manual.typ`

**Fixture:** `tests/fixtures/bld02_path_shape_collision_gate/` — `typst_documents = [("index",
"./manual.typ", "Index Master", "Probe Author"), ("other", "manual.typ", "Other Master", "Probe
Author")]`.

**Command:** `uv run python -m sphinx -b typst tests/fixtures/bld02_path_shape_collision_gate /tmp/red-a`

**Raw output:**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 2 件のソースファイル
環境データを更新中[新しい設定] 2 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 50%] index
ソースを読み込み中...[100%] other

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to /tmp/red-a/_template.typ
done
writing output... [index] done
writing output... [other] done
typst: wrote 2 wrapper file(s) -- compile these: ./manual.typ, manual.typ
build succeeded.
```
Exit code: 0. No collision warning anywhere — and the D-07 report itself claims TWO wrapper files
were written (`./manual.typ, manual.typ`), which is already misleading: only one physical file
exists.

**Emitted files:** `_template.typ`, `index.typ`, `other.typ`, `manual.typ` — the content/wrapper
split from Phase 47 means `index.typ`/`other.typ` (content) exist unconditionally, but only ONE
physical `manual.typ` (wrapper) exists on disk:
```
$ find /tmp/red-a -name '*.typ' | sort
/tmp/red-a/_template.typ
/tmp/red-a/index.typ
/tmp/red-a/manual.typ
/tmp/red-a/other.typ
$ find /tmp/red-a -name 'manual.typ' | wc -l
1
```

**Verbatim surviving `manual.typ` content — carries `title: "Other Master"` (the SECOND entry's
title, "T2"-shaped) and `#include("other.typ")`; the FIRST entry's (`index`) wrapper is gone with
no error and no warning:**
```typst
// Essential package imports
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()
#codly(languages: codly-languages)

#import "_template.typ": project

#show: project.with(
  title: "Other Master",
  authors: ("Probe Author",),
  date: "1.0.0",
  lang: "en",
)

#include("other.typ")
```

**Marker survival counts against `manual.typ` (both are `0` because content lives in `index.typ`/
`other.typ`, not inline in the wrapper — the wrapper's `#include()` target is what proves which
master's wrapper survived):**
```
$ grep -c PATHSHAPE-INDEX-MARKER-AAA /tmp/red-a/manual.typ
0
$ grep -c PATHSHAPE-OTHER-MARKER-BBB /tmp/red-a/manual.typ
0
$ grep 'title:' /tmp/red-a/manual.typ
  title: "Other Master",
```
`index.typ` (the FIRST entry's content file) still exists on disk with `PATHSHAPE-INDEX-MARKER-AAA`
intact, but it is never `#include()`d by ANY surviving wrapper — its content is unreachable from any
compiled master, the same "index entry's wrapper is gone" symptom the objective describes.

**RED confirmed:** `test_bld02_path_shape_duplicate_rejected_typst` asserts `result.returncode !=
0` against the exit-0 output above — `AssertionError`, caught by `xfail(strict=True)`, reported
`XFAIL`. The `-b typstpdf` counterpart (`test_bld02_path_shape_duplicate_rejected_typstpdf`) was
also measured this task: exit 0, `Generated PDF: /tmp/red-a-pdf/manual.pdf` (produced from
whichever entry's wrapper survived the silent overwrite) — same RED shape.

---

## BLD-02 — reserved-infrastructure-file clobber: `./_template.typ`

**Fixture:** `tests/fixtures/bld02_template_clobber_gate/` — `typst_documents = [("index",
"./_template.typ", "Clobber Master", "Probe Author")]`.

**Command:** `uv run python -m sphinx -b typst tests/fixtures/bld02_template_clobber_gate /tmp/red-b`

**Raw output:**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 1 件のソースファイル
環境データを更新中[新しい設定] 1 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to /tmp/red-b/_template.typ
done
writing output... [index] done
typst: wrote 1 wrapper file(s) -- compile these: ./_template.typ
build succeeded.
```
Exit code: 0. No warning at all — the D-07 report even names `./_template.typ` as a "wrapper file",
oblivious that it is the reserved infrastructure file.

**Emitted files:** `_template.typ`, `index.typ` — the wrapper physically overwrote the template
that every content/wrapper file's `#import "_template.typ": project` line depends on:
```
$ find /tmp/red-b -name '*.typ' | sort
/tmp/red-b/_template.typ
/tmp/red-b/index.typ
```

**Verbatim written `_template.typ` — no longer a template at all, but the wrapper body:**
```typst
// Essential package imports
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()
#codly(languages: codly-languages)

#import "_template.typ": project

#show: project.with(
  title: "Clobber Master",
  authors: ("Probe Author",),
  date: "1.0.0",
  lang: "en",
)

#include("index.typ")
```
Note this file even self-imports `"_template.typ": project` — a symbol that no longer exists in the
file since the file's own content overwrote it.

**Numeric measurement:**
```
$ grep -c '^#let project' /tmp/red-b/_template.typ
0
```
Every content and wrapper file in the tree imports the `project` symbol that this defect deletes.

**RED confirmed:** `test_bld02_dot_slash_template_clobber_rejected_typst` asserts `result.returncode
!= 0` against the exit-0 output above — `AssertionError`, caught by `xfail(strict=True)`, reported
`XFAIL`. The `-b typstpdf` counterpart
(`test_bld02_dot_slash_template_clobber_rejected_typstpdf`) was also measured this task: exit 0,
`_template.typ` destroyed before compilation — same RED shape.

---

## BLD-03 — under-length entry destroys its own docname's content

**Fixture:** `tests/fixtures/bld03_under_length_entry_gate/` — `typst_documents = [("index",),
("other", "manual.typ", "Other Master", "Probe Author")]`.

**Command:** `uv run python -m sphinx -b typst tests/fixtures/bld03_under_length_entry_gate /tmp/red-c`

**Raw output:**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 2 件のソースファイル
環境データを更新中[新しい設定] 2 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 50%] index
ソースを読み込み中...[100%] other

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to /tmp/red-c/_template.typ
done
writing output... [index]WARNING: empty typst_documents target name for docname 'index' -- falling back to 'index'
 done
writing output... [other] done
WARNING: empty typst_documents target name for docname 'index' -- falling back to 'index'
typst: wrote 2 wrapper file(s) -- compile these: index.typ, manual.typ
build succeeded, 2 warnings.
```
Exit code: 0, 2 warnings — but neither warning states "produces no wrapper file"; both are the
existing generic "empty typst_documents target name" fallback message, emitted because
`_resolve_target_stem()` receives a `None` target (the 1-tuple has no element `[1]`) and falls back
to the docname itself as the stem — which is precisely how the wrapper collides with the content
file.

**Emitted files:** `_template.typ`, `index.typ`, `manual.typ`, `other.typ`:
```
$ find /tmp/red-c -name '*.typ' | sort
/tmp/red-c/_template.typ
/tmp/red-c/index.typ
/tmp/red-c/manual.typ
/tmp/red-c/other.typ
```
`index.typ` is written TWICE during the same build: first as the docname's own content file, then
overwritten by the under-length entry's self-referential wrapper.

**Verbatim final `index.typ` content — a self-including wrapper, not `index`'s own content:**
```typst
// Essential package imports
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": mi, mitex
#import "@preview/gentle-clues:1.3.1": *

#show: codly-init.with()
#codly(languages: codly-languages)

#import "_template.typ": project

#show: project.with(
  title: "Under Length Entry Gate",
  authors: ("Probe Author",),
  date: "1.0.0",
  lang: "en",
)

#include("index.typ")
```

**Numeric measurement — the content sentinel is completely gone:**
```
$ grep -c UNDERLENGTH-CONTENT-SENTINEL-CCC /tmp/red-c/index.typ
0
```

**`-b typstpdf` counterpart, measured separately (`/tmp/red-c-pdf`):**
```
$ uv run python -m sphinx -b typstpdf tests/fixtures/bld03_under_length_entry_gate /tmp/red-c-pdf
[... same write-phase warnings as above ...]
typst: wrote 2 wrapper file(s) -- compile these: index.typ, manual.typ
Compiling 2 master document(s) to PDF...
WARNING: empty typst_documents target name for docname 'index' -- falling back to 'index'
Typst compilation failed at /tmp/red-c-pdf/index.typ: TypstError: cyclic import
ERROR: Failed to compile /tmp/red-c-pdf/index.typ: Typst compilation failed: TypstError: cyclic import
Generated PDF: /tmp/red-c-pdf/manual.pdf
[...]
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation
failed: TypstError: cyclic import
```
Exit code: 2 (non-zero). Note the failure IS reported, but with the wrong shape: a Typst compiler
`cyclic import` message discovered only at compile time (`index.typ` imports itself via
`#include("index.typ")`), never the intended `finish()`-level "has no target element" diagnostic —
`finish()` never learns the entry is under-length; it only discovers, downstream, that the file the
under-length entry silently aliased onto `index.typ` is a self-import. `manual.pdf` (the
well-formed `other` entry) IS still produced, so D-02's attempt-all-then-raise contract survives
even in this pre-fix state.

**RED confirmed:**
- `test_bld03_under_length_entry_preserves_content_typst` asserts `UNDERLENGTH-CONTENT-SENTINEL-CCC
  in index.typ` — `False` (count 0 above), `AssertionError`, caught by `xfail(strict=True)`,
  reported `XFAIL`.
- `test_bld03_under_length_entry_not_named_in_wrapper_report_typst` asserts `"wrote 1 wrapper
  file(s)"` and `"compile these: manual.typ"` in the combined output — the actual output reads
  `"wrote 2 wrapper file(s) -- compile these: index.typ, manual.typ"`, `AssertionError`, caught by
  `xfail(strict=True)`, reported `XFAIL`.
- `test_bld03_under_length_entry_reported_by_finish_typstpdf` asserts `"has no target element"` in
  the combined output — the actual output contains `"TypstError: cyclic import"` instead,
  `AssertionError`, caught by `xfail(strict=True)`, reported `XFAIL`.

---

## Full-module raw pytest transcript (nine xfail / two pass, zero xpass)

**Command:** `uv run pytest tests/test_collision_predicate_completeness_gate.py -q -rxX`

**Raw output:**
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>
configfile: pyproject.toml
plugins: cov-7.1.0
collected 11 items

tests/test_collision_predicate_completeness_gate.py xxxxxxxx..x          [100%]

=========================== short test summary info ============================
XFAIL tests/test_collision_predicate_completeness_gate.py::TestBld02PathShapeCollisionGate::test_bld02_path_shape_duplicate_rejected_typst
XFAIL tests/test_collision_predicate_completeness_gate.py::TestBld02PathShapeCollisionGate::test_bld02_path_shape_duplicate_rejected_typstpdf
XFAIL tests/test_collision_predicate_completeness_gate.py::TestBld02TemplateClobberGate::test_bld02_dot_slash_template_clobber_rejected_typst
XFAIL tests/test_collision_predicate_completeness_gate.py::TestBld02TemplateClobberGate::test_bld02_dot_slash_template_clobber_rejected_typstpdf
XFAIL tests/test_collision_predicate_completeness_gate.py::TestBld03UnderLengthEntryGate::test_bld03_under_length_entry_preserves_content_typst
XFAIL tests/test_collision_predicate_completeness_gate.py::TestBld03UnderLengthEntryGate::test_bld03_under_length_entry_not_named_in_wrapper_report_typst
XFAIL tests/test_collision_predicate_completeness_gate.py::TestBld03UnderLengthEntryGate::test_bld03_under_length_entry_reported_by_finish_typstpdf
XFAIL tests/test_collision_predicate_completeness_gate.py::TestCollisionKeyPathShapeUnit::test_collision_key_normalizes_path_shape
XFAIL tests/test_collision_predicate_completeness_gate.py::TestIsUsableTypstDocumentsEntryUnit::test_is_usable_typst_documents_entry_predicate
========================= 2 passed, 9 xfailed in 4.29s =========================
```
Exit code: 0. Nine `XFAIL`, two `passed`, zero `xpassed`, zero `failed`, zero `error` — the two
green invariance guards
(`test_collision_key_still_folds_case_and_ignores_unicode_normalization`,
`test_collision_key_does_not_collapse_leading_parent_traversal`) already pass on the unfixed tree
and are asserted to keep passing after Task 2's normalization change.

---

## Post-fix GREEN

Captured after Task 2 (`_collision_key()` gains `posixpath.normpath()`) and Task 3
(`_is_usable_typst_documents_entry()` single-sourced across all four wrapper-path-resolving
sites) both landed. Every command below is re-run verbatim against the same three fixtures.

### BLD-02 — path shape, post-fix

**Command:** `uv run python -m sphinx -b typst tests/fixtures/bld02_path_shape_collision_gate /tmp/green-a`

**Raw output (tail):**
```
sphinx.errors.ExtensionError: typst: 1 output path collision(s): 'manual.typ': typst_documents
entry 0 (docname 'index', target './manual.typ') and typst_documents entry 1 (docname 'other',
target 'manual.typ') both resolve to the same output path 'manual.typ'
```
Exit code: 2 (non-zero). `find /tmp/green-a -name '*.typ' | wc -l` → `0`. Both docnames (`index`,
`other`) and both targets are named in the single `ExtensionError`.

**`-b typstpdf` counterpart** (`/tmp/green-a-pdf`): same `ExtensionError`, same message, exit
non-zero — one shared validator, both builders.

### BLD-02 — reserved-infrastructure-file clobber, post-fix

**Command:** `uv run python -m sphinx -b typst tests/fixtures/bld02_template_clobber_gate /tmp/green-b`

**Raw output (tail):**
```
sphinx.errors.ExtensionError: typst: 1 output path collision(s): './_template.typ': the reserved
_template.typ infrastructure file and typst_documents entry 0 (docname 'index', target
'./_template.typ') both resolve to the same output path './_template.typ'
```
Exit code: 2 (non-zero). `_template` is named. No `.typ` file is written at all — the reserved
file is never even created, let alone clobbered.

**`-b typstpdf` counterpart** (`/tmp/green-b-pdf`): same `ExtensionError`, same message, exit
non-zero.

### BLD-03 — under-length entry, post-fix

**Command:** `uv run python -m sphinx -b typst tests/fixtures/bld03_under_length_entry_gate /tmp/green-c`

**Raw output:**
```
Sphinx v9.1.0 を実行中
[... unchanged read-phase lines ...]
WARNING: typst_documents entry 0 (('index',)) produces no wrapper file -- entry has no target element or a non-str docname
preparing documents... Template written to /tmp/green-c/_template.typ
done
writing output... [index] done
writing output... [other] done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
build succeeded, 1 warning.
```
Exit code: 0, 1 warning — now the intended `produces no wrapper file` diagnostic, not the generic
`empty typst_documents target name` fallback message.

**Numeric measurement — the content sentinel now survives intact:**
```
$ grep -c UNDERLENGTH-CONTENT-SENTINEL-CCC /tmp/green-c/index.typ
1
$ grep -c '#show: project.with(' /tmp/green-c/index.typ
0
```
`index.typ` stays a plain content file (no template-application marker); the D-07 report now
correctly names exactly one wrapper (`manual.typ`), never `index.typ`.

**`-b typstpdf` counterpart:**
```
$ uv run python -m sphinx -b typstpdf tests/fixtures/bld03_under_length_entry_gate /tmp/green-c-pdf
[...]
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: typst_documents entry
('index',) has no target element -- expected at least a (docname, target) pair
```
Exit code non-zero. `has no target element` and `master document(s) failed` are both present;
`ls /tmp/green-c-pdf/*.pdf` → `manual.pdf` exists — D-02's attempt-all-then-raise contract holds:
the well-formed `other` entry still gets its PDF even though the build overall fails.

### Full-suite and lint/type trio

```
$ uv run pytest -q
================= 1038 passed, 5 skipped in 219.94s (0:03:39) ==================
$ uv run black --check .
All done! (267 files unchanged)
$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```
`uv run ruff check .` could not run in this worktree -- a pre-existing, already-acknowledged
NixOS environment limitation (`.planning/todos/pending/2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md`;
STATE.md Deferred Items: "Does not block SC#3, which takes lint authority from CI"). Unrelated to
this plan's changes; CI's `lint` job is authoritative.

### Legacy regression modules, unmodified except one stale assertion

`tests/test_missing_and_malformed_master_gate.py` and `tests/test_non_str_docname_gate.py` pass
unmodified (`git diff --stat` empty for both), proving the two exact legacy messages
(`"(): malformed typst_documents entry"`, `"typst_documents entry has a non-str docname"`) and the
exact failure count (`"2 master document(s) failed"`) all survive byte-for-byte.

`tests/test_pdf_generation.py` required one deviation: its
`test_builder_appends_failure_for_malformed_entry_but_not_short_entry` test asserted the EXACT
pre-fix behavior BLD-03 reverses -- that a 1-element entry "is NOT malformed" and "must still
compile" by falling its stem back to the docname. That is precisely the silent-fallback defect
this plan closes (the write-phase equivalent is what destroys the docname's own content file), so
the test was renamed to `test_builder_appends_failure_for_malformed_entry_and_short_entry` and its
assertions updated to the corrected, locked BLD-03 contract: both entries now fail (`"2 master
document(s) failed"`), the second with `"has no target element"`, and `valid.pdf` is no longer
produced. See `47-11-SUMMARY.md`'s Deviations section for the full account.
