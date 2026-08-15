# Phase 47 Plan 01 — Pre-Fix RED Evidence

**Captured:** 2026-08-11, against the unfixed tree (this plan's own worktree, before any
`typsphinx/writer.py` or `typsphinx/builder.py` change — `git status --porcelain typsphinx/`
prints nothing throughout this plan).
**Binding constraint #4 compliance:** every section below records the VERBATIM raw output of a
real `sphinx-build` subprocess, a real `typst.compile()` call, and/or `pypdf` text extraction
against this plan's own fixtures — no claim here is inferred or copied from `47-RESEARCH.md`
without independent re-measurement this task, except where explicitly cited as a prior-session
citation (COMP-01/COMP-02/OUT-03's build is re-run fresh in this task).

Command environment for every capture below: `uv run python -m sphinx -b typst <fixture> <build_dir>`
and `uv run python3 -c "import typst; ..."` / `uv run python3 -c "import typst, pypdf; ..."`, run
inside this plan's own provisioned worktree venv (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv
sync --extra dev`, per `CLAUDE.md`'s mandatory worktree-isolated execution protocol).

---

## COMP-01 — Every document written as a docname-named content `.typ`, no template

**RED shape:** structural — the content file does not exist at all on the unfixed tree.

**Command:** `uv run python -m sphinx -b typst tests/fixtures/two_layer_root_master_gate <build_dir>`

**Raw output:**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 1 件のソースファイル
環境データを更新中[新しい設定] 1 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to <build_dir>/_template.typ
done
writing output... [index] done
build succeeded.
```
Exit code: 0.

**Emitted files:** `_template.typ`, `manual.typ` — **no `index.typ` exists**.

**Verbatim `manual.typ` content (the single, undivided file the unfixed tree writes for docname
`index`):**
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
  title: "Root Master Gate",
  authors: ("Probe Author",),
  date: "1.0.0",
  lang: "en",
)

#{
[#heading(depth: 1, {text("Root Master Gate")}) <index:root-master-gate>]

par({text("This is the root master gate document body. ROOT-BODY-MARKER-AAA")})


}
```

**RED confirmed:** `test_comp01_content_file_has_no_template` asserts `(build_dir /
"index.typ").exists()`, which is `False` on this tree — `AssertionError`, caught by
`xfail(strict=True)`, reported `XFAIL`.

---

## COMP-02 — Each `typst_documents` entry produces a wrapper `.typ` at its resolved target path

**RED shape:** structural — the wrapper file exists, but it is the SAME undivided file COMP-01's
section shows, with the body embedded directly rather than pulled in via `#include()`.

**Command/output:** identical build to COMP-01's section above (same fixture, same run).

**RED confirmed:** `test_comp02_wrapper_file_has_template_and_include` asserts `"#include(" in
content` against `manual.typ`'s content quoted above — `#include(` does not appear anywhere in
that file (there is nothing to include; the body is inlined). `AssertionError`, caught by
`xfail(strict=True)`, reported `XFAIL`.

---

## COMP-03 — B-1 closes: nested master-as-toctree-child builds without `file not found`

**RED shape: classic `TypstError`** (per binding constraint #4's amendment, this is the one
requirement in this plan whose RED IS a compile fatal, not a structural assertion).

**Command 1:** `uv run python -m sphinx -b typst tests/fixtures/two_layer_nested_master_gate <build_dir>`

**Raw output:**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 2 件のソースファイル
環境データを更新中[新しい設定] 2 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 50%] guide/index
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to <build_dir>/_template.typ
done
writing output... [guide/index]WARNING: a path is not supported in a typst_documents target name: 'manuals/guide.typ' -- using 'guide' instead
 done
writing output... [index] done
build succeeded, 1 warning.
```
Exit code: 0, 1 warning.

**Emitted files:** `_template.typ`, `outer.typ`, `guide/guide.typ` — note the SECOND entry's
target `manuals/guide.typ` was truncated+relocated to `guide/guide.typ`, NOT written at
`manuals/guide.typ` as OUT-01 requires post-fix.

**Verbatim `outer.typ` content:**
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
  title: "Outer Master",
  authors: ("Probe Author",),
  date: "1.0.0",
  lang: "en",
  toctree_maxdepth: none,
  toctree_numbered: false,
  toctree_caption: none,
)

#{
[#heading(depth: 1, {text("Outer Master")}) <index:outer-master>]

par({text("This is the outer master's own prose. OUTER-PROSE-MARKER")})

context {
  set heading(offset: heading.offset + 1)
  include("guide/index.typ")
}


}
```

**Command 2 (direct `typst.compile()` transcript):**
```python
import typst
typst.compile("<build_dir>/outer.typ", root="<build_dir>")
```

**Raw output (the classic `TypstError`, verbatim):**
```
COMPILE FAILED: TypstError: file not found (searched at <build_dir>/guide/index.typ)
```

**Root cause, confirmed by direct comparison:** `outer.typ`'s `include("guide/index.typ")` names
a file that does not physically exist — `guide/guide.typ` exists instead (the truncated,
relocated stem), never `guide/index.typ`.

**RED confirmed:** `test_comp03_b1_nested_master_compiles` calls `typst.compile(str(wrapper_typ),
root=str(build_dir))` inside a `try`/`except`; the `except` branch's two `assert ... not in
message` checks both PASS (the strings ARE present, so `"file not found" not in message` is
`False` → `AssertionError`), which is itself caught by `xfail(strict=True)`, reported `XFAIL`.

---

## COMP-04 — B-2 closes: included master no longer re-expands template mid-body

**RED shape: structural `pypdf`-text assertion, NOT a `TypstError`** — B-2 is a
compiles-fine-but-wrong-output defect, per binding constraint #4's amendment and open question #3
(closed in `47-RESEARCH.md`).

**On `two_layer_nested_master_gate` exactly as configured, B-1 (above) blocks the compile before
B-2 can be independently observed** — `typst.compile("outer.typ", root=build_dir)` raises the
COMP-03 `TypstError` before any PDF is produced. B-2's own effect is isolated below by temporarily
copying the misplaced file to the path the wrapper expects (`guide/guide.typ` →
`guide/index.typ`), the SAME workaround `47-RESEARCH.md` Pitfall 2 used, re-run independently this
task against this plan's OWN fixture (not copied from that prior session's fixture).

**Command:**
```python
import typst, pypdf
typst.compile("<build_dir_b2>/outer.typ", output="<build_dir_b2>/outer.pdf", root="<build_dir_b2>")
reader = pypdf.PdfReader("<build_dir_b2>/outer.pdf")
for i, page in enumerate(reader.pages):
    print(f"--- page {i} ---")
    print(page.extract_text())
```

**Raw output (compile succeeds; per-page transcript verbatim, U+200B stripped):**
```
COMPILE SUCCEEDED
--- page 0 ---
Outer Master
Probe Author
1.0.0
1
--- page 1 ---
1
Contents
2 Outer Master . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
2.2 Guide Section . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
2
--- page 2 ---
2 Outer Master
This is the outer master's own prose. OUTER-PROSE-MARKER
3
--- page 3 ---
Nested Master
Probe Author
1.0.0
4
--- page 4 ---
2.1 Contents
Contents
2 Outer Master . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
2.2 Guide Section . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
5
--- page 5 ---
2.2 Guide Section
This is the nested master's own body. GUIDE-BODY-MARKER
6
```

**States in prose: the compile SUCCEEDED — this is the structural, not classic-`TypstError`, RED
shape** binding constraint #4 requires for COMP-04. Six pages total. Pages 3–4 (a full second
title page reading `Nested Master` / `Probe Author` / an isolated page number, plus a full second
outline headed `2.1 Contents`) sit between the outer document's own prose (page 2,
`OUTER-PROSE-MARKER`) and the nested document's own content (page 5, `GUIDE-BODY-MARKER`) — the
exact "mid-body re-expansion" defect description. Substring counts against the joined text:
`OUTER-PROSE-MARKER` present, `GUIDE-BODY-MARKER` present, `"Nested Master"` present exactly once
(page 3 only — the fixture's `guide/index.rst` heading is deliberately the DIFFERENT string
`"Guide Section"`, so this one occurrence is unambiguously the second title page, not the section's
own heading), `"Contents"` present three times (page 1's own outline heading once, page 4's
mid-body outline contributing two: its `"2.1 Contents"` section heading and its own `"Contents"`
title line).

**RED confirmed (on the actual test fixture, via the shared class-scoped fixture, not the
temporary B-1 workaround above):** `test_comp04_b2_no_mid_body_template_reexpansion`'s
class-scoped `nested_master_outer_pdf_text` fixture calls `typst.compile()` directly on
`two_layer_nested_master_gate`'s real `outer.typ` (no workaround applied in the test itself) —
this raises COMP-03's `TypstError` inside fixture setup. Verified empirically this task: a
class-scoped fixture raising during setup is still caught correctly by a dependent
`xfail(strict=True)` test — pytest reports `XFAIL`, not a bare `error` (confirmed with a minimal
throwaway probe: `1 xfailed` / `2 xfailed` for one and two dependent tests respectively, exit code
0 both times).

---

## OUT-03 — Content files stay docname-derived regardless of wrapper placement

**RED shape:** structural — no docname-derived content file exists for either docname on the
unfixed tree.

**Command/output:** identical build to COMP-03's Command 1 above (same fixture, same run).

**Emitted `.typ` files:** `outer.typ`, `guide/guide.typ` — **neither `index.typ` nor
`guide/index.typ` exists.** The second entry's target `manuals/guide.typ` was not honored as a
path at all (OUT-01's reversal has not landed); it was truncated to the basename `guide` and
FORCE-RELOCATED into the docname's own directory (`guide/`) by the surviving Phase 44
`_directory_preserving_relpath()` logic, giving `guide/guide.typ` — neither the pre-fix nor the
post-fix expected wrapper path (`manuals/guide.typ`).

**RED confirmed:** `test_out03_content_files_stay_docname_derived` asserts `(build_dir /
"index.typ").exists()` — `False`, `AssertionError`, caught by `xfail(strict=True)`, reported
`XFAIL`.

---

## Full-module raw pytest transcript (all five requirements + the unit edge test, one run)

**Command:** `uv run pytest tests/test_two_layer_output_gate.py -v`

**Raw output:**
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- <venv>/bin/python
cachedir: .pytest_cache
rootdir: <worktree>
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 6 items

tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_comp01_content_file_has_no_template XFAIL [ 16%]
tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_comp02_wrapper_file_has_template_and_include XFAIL [ 33%]
tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_out03_content_files_stay_docname_derived XFAIL [ 50%]
tests/test_two_layer_output_gate.py::TestTwoLayerOutputGate::test_comp03_b1_nested_master_compiles XFAIL [ 66%]
tests/test_two_layer_output_gate.py::TestTwoLayerOutputGatePdf::test_comp04_b2_no_mid_body_template_reexpansion XFAIL [ 83%]
tests/test_two_layer_output_gate.py::TestComputeContentIncludePath::test_compute_content_include_path_is_a_pure_two_endpoint_relpath XFAIL [100%]

============================== 6 xfailed in 2.25s ==============================
```
Exit code: 0. Every test `XFAIL` — no `xpassed`, no `failed`, no `error`.

---

## BLD-02 — Duplicate targets detected, not silently dropped

**RED shape:** structural — exit 0, no collision warning anywhere, the first entry's body silently
overwritten.

**Command:** `uv run python -m sphinx -b typst tests/fixtures/bld02_duplicate_target_gate <build_dir>`

**Raw output:**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 2 件のソースファイル
環境データを更新中[新しい設定] 2 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 50%] index
ソースを読み込み中...[100%] other

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to <build_dir>/_template.typ
done
writing output... [index] done
writing output... [other] done
build succeeded.
```
Exit code: 0, no warning at all.

**Emitted files:** `_template.typ`, `manual.typ` — no `index.typ` or `other.typ` (single-file
per-docname model, both resolve to the SAME stem `manual`).

**Marker survival counts against the surviving `manual.typ`:**
```
$ grep -c INDEX-MASTER-MARKER-AAA <build_dir>/manual.typ
0
$ grep -c OTHER-MASTER-MARKER-BBB <build_dir>/manual.typ
1
```
The first entry's (`index`) body is completely gone — silently dropped by the sorted-order write
loop (`"index"` written first, `"other"` written second, overwriting).

**Verbatim surviving `manual.typ` content:**
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

#{
[#heading(depth: 1, {text("Other Master")}) <other:other-master>]

par({text("This is the other master's own body. OTHER-MASTER-MARKER-BBB")})


}
```

**RED confirmed:** `test_bld02_duplicate_target_rejected_typst` asserts `result.returncode != 0`
against the exit-0 output above — `AssertionError`, caught by `xfail(strict=True)`, reported
`XFAIL`. The `-b typstpdf` counterpart (`test_bld02_duplicate_target_rejected_typstpdf`) was also
measured this task: exit 0, `Generated PDF: <build_dir>/manual.pdf` (produced from whichever
entry survived the silent overwrite) — same RED shape, same assertion failure.

---

## BLD-03 — Wrapper target colliding with a content file's own path detected

**RED shape:** structural — exit 0, no warning, the exact D-01 self-collision configuration
building successfully.

**Command:** `uv run python -m sphinx -b typst tests/fixtures/bld03_self_collision_gate <build_dir>`

**Raw output:**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 1 件のソースファイル
環境データを更新中[新しい設定] 1 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to <build_dir>/_template.typ
done
writing output... [index] done
build succeeded.
```
Exit code: 0, no warning at all.

**Emitted files:** `_template.typ`, `index.typ` — a single, fully-templated file, containing
`SELF-COLLISION-BODY-MARKER`.

**RED confirmed:** `test_bld03_self_collision_rejected_typst` asserts `result.returncode != 0`
against the exit-0 output above — `AssertionError`, caught by `xfail(strict=True)`, reported
`XFAIL`. The `-b typstpdf` counterpart (`test_bld03_self_collision_rejected_typstpdf`) was also
measured this task: exit 0, `Generated PDF: <build_dir>/index.pdf` — same RED shape.

---

## BLD-04 — Collision detection behaves identically on case-insensitive filesystems

**RED shape:** structural at the unit level (the comparison function does not exist yet, let alone
fold case) — the physical-collision consequence is unobservable on Linux CI, confirmed directly
this task.

**Fixture design note (Rule 1 fix applied this task):** the fixture's `index.rst` originally
toctree-included `manual`, which reproduced an UNRELATED confound — since `manual`'s own
`typst_documents` target (`Manual.typ`) differs from the toctree's docname-derived include
(`manual.typ`), this accidentally triggered B-1's `file not found` failure on `-b typstpdf`,
masking the case-collision defect behind a different one. The toctree link was removed (accepting
the harmless "document isn't included in any toctree" warning) so BLD-04's own defect is isolated
cleanly on both builders. See the fixture's own `conf.py` comment for the full account.

**Command 1 (`-b typst`, corrected fixture):**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 2 件のソースファイル
環境データを更新中[新しい設定] 2 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 50%] index
ソースを読み込み中...[100%] manual

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... <fixture>/manual.rst: WARNING: ドキュメントはどの toctree にも含まれていません [toc.not_included]
完了
preparing documents... Template written to <build_dir>/_template.typ
done
writing output... [index] done
writing output... [manual] done
build succeeded, 1 warning.
```
Exit code: 0. The one warning is the harmless orphan-document notice, unrelated to BLD-04.

**Emitted files:** `_template.typ`, `index-wrapper.typ`, `Manual.typ` — **two DISTINCT files**
(`index-wrapper.typ` and `Manual.typ`) coexist on this Linux, case-sensitive filesystem. States in
prose: on a case-insensitive filesystem (Windows, default macOS APFS), `Manual.typ` (the second
entry's target) and `manual.typ` (docname `manual`'s own content path, once COMP-01 makes content
files unconditional) would be the SAME physical path — the physical collision consequence is
therefore observable ONLY on the Windows/macOS CI lanes, never on Linux, confirming the gap this
requirement closes is real and structurally invisible to a Linux-only local run.

**Command 2 (`-b typstpdf`, corrected fixture):** exit 0, `build succeeded, 1 warning`,
`Generated PDF: <build_dir>/index-wrapper.pdf` and `Generated PDF: <build_dir>/Manual.pdf` — both
builders share the same undetected gap.

**RED confirmed (subprocess half):** `test_bld04_case_collision_rejected_typst` and
`test_bld04_case_collision_rejected_typstpdf` both assert `result.returncode != 0` against the
exit-0 outputs above — `AssertionError`, caught by `xfail(strict=True)`, reported `XFAIL`.

**RED confirmed (unit half, the load-bearing one since Linux cannot observe the physical
overwrite):** `test_collision_key_folds_case_but_not_unicode_normalization` accesses
`TypstBuilder._collision_key` — verified this task that the attribute does not exist on the
unfixed tree:
```
$ uv run python3 -c "from typsphinx.builder import TypstBuilder; TypstBuilder._collision_key"
AttributeError: type object 'TypstBuilder' has no attribute '_collision_key'
```
`AttributeError`, caught by `xfail(strict=True, raises=AttributeError)`, reported `XFAIL`.

---

## Full-module raw pytest transcript (BLD-02, BLD-03, BLD-04, both builders + the unit edge test)

**Command:** `uv run pytest tests/test_collision_validator_gate.py -v`

**Raw output:**
```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- <venv>/bin/python
cachedir: .pytest_cache
rootdir: <worktree>
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 7 items

tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld02_duplicate_target_rejected_typst XFAIL [ 14%]
tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld02_duplicate_target_rejected_typstpdf XFAIL [ 28%]
tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld03_self_collision_rejected_typst XFAIL [ 42%]
tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld03_self_collision_rejected_typstpdf XFAIL [ 57%]
tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld04_case_collision_rejected_typst XFAIL [ 71%]
tests/test_collision_validator_gate.py::TestCollisionValidatorGate::test_bld04_case_collision_rejected_typstpdf XFAIL [ 85%]
tests/test_collision_validator_gate.py::TestCollisionKeyUnit::test_collision_key_folds_case_but_not_unicode_normalization XFAIL [100%]

============================== 7 xfailed in 3.65s ==============================
```
Exit code: 0. Every test `XFAIL` — no `xpassed`, no `failed`, no `error`.

**Combined run (both new gate modules together):**
```
$ uv run pytest tests/test_two_layer_output_gate.py tests/test_collision_validator_gate.py -q
tests/test_two_layer_output_gate.py xxxxxx                               [ 46%]
tests/test_collision_validator_gate.py xxxxxxx                           [100%]

============================= 13 xfailed in 5.97s ==============================
```
Exit code: 0.

---

## A3: second path-rejection site search

**Plan 47-03, Task 3.** RESEARCH.md's Assumptions-Log A3 records that a repo-wide grep for a
SECOND, independent path-rejection site (beyond the `is_guarded`/`_escapes_outdir` boolean at
`builder.py`) was never exhaustively run, and that a missed site would let an escaping
`typst_documents` target slip past OUT-02 undetected. Closed here by measurement: a real grep
over `typsphinx/` for each of the seven named patterns, captured against the tree as it stood
after Task 1 and Task 2 of this plan landed (both already-committed).

**Commands and raw output** (`uv run` inside this plan's own provisioned worktree venv, per
`CLAUDE.md`'s mandatory worktree-isolated execution protocol; run from the repo root):

```
$ grep -rn "os\.sep" typsphinx/
typsphinx/builder.py:75:    ``os.sep``/``os.altsep``) is what makes a Windows-authored
typsphinx/builder.py:77:    ``os.sep`` is ``"/"`` and ``os.altsep`` is ``None``.
```
Both hits are prose inside `_escapes_outdir()`'s own docstring, explaining why it does NOT use
`os.sep`/`os.altsep` (it splits on the literal characters `/` and `\` instead, which is what makes
a Windows-authored separator detectable on POSIX). No second site.

```
$ grep -rn "os\.altsep" typsphinx/
typsphinx/builder.py:75:    ``os.sep``/``os.altsep``) is what makes a Windows-authored
typsphinx/builder.py:77:    ``os.sep`` is ``"/"`` and ``os.altsep`` is ``None``.
```
Same two docstring lines as above. No second site.

```
$ grep -rn "isabs" typsphinx/
typsphinx/builder.py:97:    return ".." in segments or path.isabs(stem) or _is_drive_qualified(stem)
typsphinx/builder.py:664:        if path.isabs(resolved_uri):
```
Line 97 is `_escapes_outdir()`'s own existing OUT-02 rule -- not a second site. Line 664 is inside
`_track_image()`, and operates on `resolved_uri` -- a Sphinx-resolved IMAGE URI from
`node["candidates"]`, never a `typst_documents` target string. It decides whether an image path
needs rehoming relative to `doctreedir` (Issue #130's fix), a disjoint input domain from a
`typst_documents` target. It cannot accept or reject a target string because a target string is
never passed to it. Per this task's own scope fence ("image path rehoming is Phase 50's scope,
IMG-01/IMG-02, and must not be picked up opportunistically"), this hit is recorded and left alone.

```
$ grep -rn "normpath" typsphinx/
typsphinx/builder.py:692:        return path.normpath(path.join(self.outdir, docname + ".typ"))
typsphinx/builder.py:760:            wrapper_destination = path.normpath(
typsphinx/builder.py:1186:            typ_file = path.normpath(path.join(self.outdir, wrapper_relpath + ".typ"))
typsphinx/builder.py:1208:                pdf_file = path.normpath(
typsphinx/translator.py:4658:        target_uri = posixpath.normpath(posixpath.join(base_dir, path_part))
```
`builder.py:692`/`760`/`1186`/`1208` all call `normpath` on a path built from a docname or a
value `_resolve_output_stem()`/`_wrapper_output_relpath()` has ALREADY resolved (and, for a
path-bearing target, already run through OUT-02's `_escapes_outdir()` gate) -- pure filesystem
string normalization (collapsing `./`, redundant separators) after the accept/reject decision has
already been made, not a second decision site. `translator.py:4658` is inside
`_resolve_xref_docname()`, joining a Sphinx-computed cross-reference `refuri` fragment -- an
internal, Sphinx-generated relative path between two already-known document URIs, never a
`typst_documents` target string. No second site.

```
$ grep -rn "relpath" typsphinx/ | grep -v "^typsphinx/builder.py:[0-9]*: *#"
typsphinx/writer.py:31:    This is a genuine two-endpoint ``posixpath.relpath`` computation, NOT
typsphinx/writer.py:61:    return posixpath.relpath(content_relative_path, start=start)
typsphinx/builder.py:265:            ``_directory_preserving_relpath()``, which force-relocates
typsphinx/builder.py:368:        effective = self._directory_preserving_relpath(docname, stem)
typsphinx/builder.py:385:    def _directory_preserving_relpath(self, docname: str, stem: str) -> str:
typsphinx/builder.py:550:        wrapper_relpaths = sorted(
typsphinx/builder.py:551:            self._wrapper_output_relpath(entry) + ".typ"
typsphinx/builder.py:555:        if wrapper_relpaths:
typsphinx/builder.py:557:                f"typst: wrote {len(wrapper_relpaths)} wrapper file(s) -- "
typsphinx/builder.py:558:                f"compile these: {', '.join(wrapper_relpaths)}"
typsphinx/builder.py:665:            rel_uri = path.relpath(resolved_uri, self.doctreedir).replace(path.sep, "/")
typsphinx/builder.py:682:        ``_directory_preserving_relpath()`` call. Every docname gets a
typsphinx/builder.py:694:    def _wrapper_output_relpath(self, entry: tuple) -> str:
typsphinx/builder.py:700:        ``_directory_preserving_relpath()``'s Phase 44 D-05 relocation
typsphinx/builder.py:759:            wrapper_relpath = self._wrapper_output_relpath(entry)
typsphinx/builder.py:761:                path.join(self.outdir, wrapper_relpath + ".typ")
typsphinx/builder.py:764:            wrapper_relative_dir = posixpath.dirname(wrapper_relpath)
typsphinx/builder.py:979:                rel_path = path.relpath(src_file, src_dir)
typsphinx/builder.py:1051:        rel_path = path.relpath(src_path, self.srcdir)
typsphinx/builder.py:1185:            wrapper_relpath = self._wrapper_output_relpath(doc_tuple)
typsphinx/builder.py:1186:            typ_file = path.normpath(path.join(self.outdir, wrapper_relpath + ".typ"))
typsphinx/builder.py:1209:                    path.join(self.outdir, wrapper_relpath + ".pdf")
typsphinx/translator.py:4986:            # Resolved CROSS-document reference (`<relpath><out_suffix>#anchor`).
```
`writer.py:61` (`compute_content_include_path()`) computes a wrapper-to-content `#include()`
path between two ALREADY-RESOLVED locations -- neither endpoint is a raw `typst_documents`
target, and it does not gate acceptance of anything (Pattern 2, `47-RESEARCH.md`).
`_directory_preserving_relpath()` (`builder.py:265`/`368`/`385`/`682`/`700`) is called only
AFTER `_resolve_output_stem()` has already resolved (and, for a path-bearing target, already
escape-gated) the stem -- it re-prefixes an already-accepted stem with a docname's own directory
for the CR-01 collision comparison (D-01/47-02's own acknowledged pre-OUT-01-shaped limitation,
47-09's territory) and, separately, for content-path placement; it never independently
decides whether a target is accepted or rejected. `builder.py:665` is the same `_track_image()`
image-rehoming site already covered under `isabs` above. `builder.py:979`/`1051`
(`_copy_template_directory()`/`_copy_single_asset()`) compute a relative path between two
ALREADY-TRUSTED, already-existing filesystem locations under `srcdir` for template-asset
copying -- never a `typst_documents` target string. `translator.py:4986` is a comment inside
cross-reference emission, describing the SAME Sphinx-computed `refuri` shape already covered
under `normpath` above. No second site.

```
$ grep -rn "basename" typsphinx/
typsphinx/writer.py:233:        basename.
typsphinx/writer.py:264:            ever collide with or impersonate the reserved basename.
typsphinx/builder.py:36:    two-character drive prefix before taking the fallback basename) call
typsphinx/builder.py:72:    escape-shaped terms below still fall back to a basename.
typsphinx/builder.py:254:            safe fallback is returned instead -- ``path.basename`` of the
typsphinx/builder.py:259:            ``_template`` basename (CR-01), a ``logger.warning`` is
typsphinx/builder.py:310:                fallback = path.basename(fallback_source)
typsphinx/builder.py:312:                    # The path guard's own fallback (a basename) is itself
typsphinx/builder.py:330:            elif "/" in stem and not path.basename(stem).strip():
typsphinx/builder.py:333:                # its basename -- is itself empty (a trailing
typsphinx/builder.py:362:        #     basename is a root-level equality test, not a basename test;
typsphinx/builder.py:388:        ``_resolve_output_stem`` returns only a basename-safe stem (D-06/
typsphinx/builder.py:389:        D-07 already reduced any path-bearing target to its basename), so a
typsphinx/builder.py:417:            return posixpath.join(directory, posixpath.basename(stem))
```
Every `path.basename`/`posixpath.basename` call (`builder.py:254`, `310`, `330`, `417`) executes
INSIDE `_resolve_output_stem()`, downstream of `_escapes_outdir()`'s already-made decision (the
first two compute the OUT-02 escape fallback; the third, added by this plan's Task 1, computes the
OUT-01 empty-trailing-segment fallback; the fourth, inside `_directory_preserving_relpath()`,
composes an already-resolved stem with a docname directory for the CR-01 comparison). None of
these independently decides whether a target string is accepted or rejected -- they only ever run
on a stem `_escapes_outdir()` has already classified, or compute a DIFFERENT thing entirely
(the CR-01 comparison path). `writer.py:233`/`264` are prose, not code. No second site.

```
$ grep -rn "isalpha()" typsphinx/
typsphinx/builder.py:38:    stem[0].isalpha() and stem[1] == ":"`` check independently -- see
typsphinx/builder.py:60:    return len(stem) >= 2 and stem[0].isalpha() and stem[1] == ":"
typsphinx/template_engine.py:97:    ``len(head) in (2, 3) and head.isalpha()``, because Python's
typsphinx/template_engine.py:98:    ``str.isalpha()`` is Unicode-aware and answers True for CJK/Cyrillic code
```
`builder.py:60` is the ONE place the drive-letter detection idiom is now defined (see "Fix applied"
below). `template_engine.py:97`/`98` are prose inside `derive_typst_lang()`'s docstring, discussing
Sphinx `language`-config-code ASCII validation -- a wholly different string domain (a 2-3-letter
locale code, not a filesystem target), and explicitly NOT using this idiom (the docstring explains
why `str.isalpha()` alone was rejected there, for an unrelated reason: Unicode-awareness over CJK
code points). No second site.

**Finding: the drive-letter detection idiom WAS duplicated (not independently divergent) --
routed through one helper.** Before this task, `is_drive_qualified = len(stem) >= 2 and
stem[0].isalpha() and stem[1] == ":"` was written twice in `typsphinx/builder.py`: once inside
`_escapes_outdir()` (the actual accept/reject decision) and once again, verbatim, inline inside
`_resolve_output_stem()` (used only downstream, to decide whether to strip a two-character drive
prefix before taking the escape fallback's basename -- never itself gating acceptance, since it
only ran inside the branch `_escapes_outdir(stem)` had already returned `True` for). This was
literal code duplication, not two independently-diverging DECISION sites -- the two copies could
never disagree, because the second copy's result was never used to accept or reject anything, only
to slice a string after the first copy (inside `_escapes_outdir`) had already rejected it. Still,
per this task's own `<done>` criterion ("OUT-02 has exactly one rule in exactly one place"),
having the SAME string-shape test written twice in one module was worth closing outright rather
than leaving as a latent duplication risk for a future edit to accidentally diverge.

**Fix applied:** extracted the shared predicate into a new module-level `_is_drive_qualified(stem)`
function (`typsphinx/builder.py`, with its own doctest examples), and both `_escapes_outdir()` and
`_resolve_output_stem()` now call it instead of each computing the check inline. This is a pure
refactor -- no behavior change; every existing `_resolve_output_stem`/`_escapes_outdir` test
(`tests/test_builder_output_stem.py`, `tests/test_out02_escape_target_gate.py`) still passes
unchanged after the extraction, proving the two call sites already agreed on all three escape
shapes before the refactor and continue to agree after it. No new unit test was added purely for
"the two sites agree" (per the task's own conditional instruction, that test is only required when
a second INDEPENDENT rejection site is found and routed through `_escapes_outdir` -- this was a
downstream duplicate of the SAME site's own computation, not a second site), but the full existing
regression suite (`tests/test_builder_output_stem.py tests/test_out02_escape_target_gate.py
tests/test_two_layer_output_gate.py`, 41 tests) re-passing after the extraction is direct evidence
the refactor preserved behavior.

**Conclusion: no second, independent path-rejection site exists for a `typst_documents` target
string.** Every `os.sep`/`os.altsep`/`isabs`/`normpath`/`relpath`/`basename`/drive-letter-idiom hit
in `typsphinx/` either (a) lives inside `_escapes_outdir()`/`_resolve_output_stem()` themselves,
downstream of the one accept/reject decision `_escapes_outdir()` makes, or (b) operates in a
disjoint input domain that never receives a raw `typst_documents` target string -- image URIs
(`_track_image()`, Issue #130's rehoming), Sphinx-computed cross-reference `refuri` fragments
(`_resolve_xref_docname()`), or already-trusted filesystem paths under `srcdir`/`doctreedir`
(template-asset copying). RESEARCH.md's Assumptions-Log A3 is closed by this measurement: the
`is_guarded`/`_escapes_outdir` boolean at `builder.py` was, and remains after this task, the
complete and only place a `typst_documents` target string is accepted or rejected -- and after
this task's extraction, its one remaining internal duplication (the drive-letter idiom) is also
gone.

Per this task's own scope fence, image path rehoming (`_track_image()`/`copy_image_files()`) was
identified above and explicitly left untouched -- it is Phase 50's scope (IMG-01/IMG-02), not
picked up opportunistically here. `git diff --stat` for this task's own change touches only
`typsphinx/builder.py` (the `_is_drive_qualified()` extraction) and confirms no hunk touches a
`_track_image` or `copy_image_files` body.
