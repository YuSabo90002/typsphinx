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

<!-- gsd:write-continue -->
