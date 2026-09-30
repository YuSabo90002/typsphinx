# Phase 49 Plan 03 — Shapes Pre-Fix RED / Baseline Evidence

**Captured:** 2026-08-14, against the unfixed tree (this plan's own worktree, before any
`typsphinx/` change — `git status --porcelain typsphinx/` prints nothing throughout Task 1 and
Task 2).

**Worktree provenance:** `typsphinx` package path resolved via `uv run python -c "import
typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"` →
`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aba9a064385780508/typsphinx/__init__.py`
— this plan's own worktree copy, not the main checkout. Dependency versions read live this
session: `typst` `0.15.0`, `sphinx` `9.1.0`, `pypdf` `6.14.2` — all match `49-EVIDENCE.md`'s own
live-verified readings, no drift.

**Purpose of recording every fixture's FULL Sphinx warning list, not just the warnings the
section cares about:** this phase must not silently remove a diagnostic Sphinx already emits
today. The only way to detect a silently-removed diagnostic after the emitter lands is to have
the full before-list on record, so `tests/test_state_guard_shapes_gate.py`'s "no lost
diagnostics" test can assert every warning recorded here is still present post-fix.

**Reproduction command shape (identical for every section unless noted):**
```
uv run python -m sphinx -b typst    tests/fixtures/<fixture> <build-dir-typst>
uv run python -m sphinx -b typstpdf tests/fixtures/<fixture> <build-dir-typstpdf>
```
Invoked as `sys.executable -m sphinx` (matching `tests/test_pdf_render_gate.py`'s
`_run_sphinx_build_typst` convention) — no dependency on `uv` PATH resolution inside the
subprocess.

---

## Section 1 — `state_guard_self_and_url_gate` (D-03/D-10, the phase's one classic-TypstError RED)

**`-b typst`:**
```
uv run python -m sphinx -b typst tests/fixtures/state_guard_self_and_url_gate /tmp/evidence-self-and-url-typst
```

**Raw output (verbatim, full):**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 2 件のソースファイル
環境データを更新中[新しい設定] 2 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 50%] child
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aba9a064385780508/tests/fixtures/state_guard_self_and_url_gate/child.rst: document is referenced in multiple toctrees: ['index', 'index'], selecting: index <- child
完了
preparing documents... Template written to /tmp/evidence-self-and-url-typst/_template.typ
done
writing output... [child] done
writing output... [index] done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
build succeeded, 1 warning.
```
**Full warning list (this fixture's baseline for "no lost diagnostics"):**
- `index.rst:4: WARNING: toctree で重複したエントリが見つかりました: child [toc.duplicate_entry]`
  (Sphinx's own `duplicated entry found in toctree: child`, localized to `ja`)

Exit code: 0, 1 warning. The markup build succeeds — the fatal is at PDF-compile time only.

**Verbatim emitted `index.typ` content file — the mechanism, made visible:**
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
[#heading(depth: 1, {text("Index")}) <index:index>]

context {
  set heading(offset: heading.offset + 1)
  include("self.typ")
  include("https://example.com.typ")
  include("child.typ")
}


}
```
The current `entries`-iterating emitter unconditionally emits THREE `include()` calls: the two
that derive from `self` and the external URL (neither file exists on disk — D-03's fix moves the
emission side onto `includefiles`, which never contains either) and one deduped `include("child.typ")`
(the duplicate `child` entry only produces ONE call because the current build-scoped
`_included_docnames` ledger collapses it — D-04's future occurrence-indexed keys replace this
write-time ledger with two static compile-time guards, only one of which is ever live).

**`-b typstpdf`:**
```
uv run python -m sphinx -b typstpdf tests/fixtures/state_guard_self_and_url_gate /tmp/evidence-self-and-url-typstpdf
```

**Raw output (verbatim, the fatal and surrounding traceback):**
```
Sphinx v9.1.0 を実行中
...
整合性をチェック中... /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aba9a064385780508/tests/fixtures/state_guard_self_and_url_gate/child.rst: document is referenced in multiple toctrees: ['index', 'index'], selecting: index <- child
完了
preparing documents... Template written to /tmp/evidence-self-and-url-typstpdf/_template.typ
done
writing output... [child] done
writing output... [index] done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
Compiling 1 master document(s) to PDF...
Typst compilation failed at /tmp/evidence-self-and-url-typstpdf/manual.typ: TypstError: file not found (searched at /tmp/evidence-self-and-url-typstpdf/self.typ)
ERROR: Failed to compile /tmp/evidence-self-and-url-typstpdf/manual.typ: Typst compilation failed: TypstError: file not found (searched at /tmp/evidence-self-and-url-typstpdf/self.typ)
Location: /tmp/evidence-self-and-url-typstpdf/manual.typ
Details: file not found (searched at /tmp/evidence-self-and-url-typstpdf/self.typ)

Extension error!
...
Traceback
=========

      File "typsphinx/builder.py", line 1390, in finish
        raise ExtensionError(
            f"typstpdf: {len(failures)} master document(s) failed: {summary}"
        )
    sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation
    failed: TypstError: file not found (searched at /tmp/evidence-self-and-url-typstpdf/self.typ)
    Location: /tmp/evidence-self-and-url-typstpdf/manual.typ
    Details: file not found (searched at /tmp/evidence-self-and-url-typstpdf/self.typ)
```
Exit code: 2 (non-zero). No PDF is produced — `manual.pdf` does not exist.

**RED confirmed:** post-fix, `test_state_guard_shapes_gate.py`'s self-and-URL test asserts the
PDF build exits 0, no emitted include derives from `self` or the external URL, and the child's
marker appears exactly once — every one of these is currently false on the unfixed tree, and the
test is recorded `xfail(strict=True, reason="... 49-04 ...")` per this transcript.

<!-- planner-discipline-allow: file not found -->

---

## Section 2 — `state_guard_cycle_gate` (D-06, an ADDITIONAL classic-TypstError RED discovered by
measurement — not the phase's named "one classic RED", which is Section 1's self/URL fixture per
D-10, but a second, distinct pre-existing compile fatal this fixture's own real-compile transcript
surfaced)

**`-b typst`:**
```
uv run python -m sphinx -b typst tests/fixtures/state_guard_cycle_gate /tmp/evidence-cycle-typst
```

**Raw output (verbatim, full):**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 2 件のソースファイル
環境データを更新中[新しい設定] 2 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 50%] alpha
ソースを読み込み中...[100%] beta

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to /tmp/evidence-cycle-typst/_template.typ
done
writing output... [alpha] done
writing output... [beta] done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
build succeeded.
```
**Full warning list:** none. Exit code: 0. Unlike Section 1, Sphinx's own `parse_content` raises
no diagnostic for a genuine mutual toctree pair (this is not a duplicate-entry or nonexisting-
document case — both `alpha` and `beta` are perfectly well-formed documents).

**Verbatim emitted include lines (the mechanism, made visible):**
```
$ grep -n 'include(' alpha.typ beta.typ
beta.typ:17:  include("alpha.typ")
alpha.typ:17:  include("beta.typ")
```
The current emitter has NO cycle guard of any kind (it has no traversal concept at all — it
processes each document's own toctree entries independently, per-document, at write time). Both
directions of the cycle are emitted unconditionally: `alpha.typ` includes `beta.typ`, AND
`beta.typ` includes `alpha.typ` back — a genuine mutual `#include()` pair.

**`-b typstpdf`:**
```
uv run python -m sphinx -b typstpdf tests/fixtures/state_guard_cycle_gate /tmp/evidence-cycle-typstpdf
```

**Raw output (verbatim, the fatal):**
```
...
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
Compiling 1 master document(s) to PDF...
Typst compilation failed at /tmp/evidence-cycle-typstpdf/manual.typ: TypstError: maximum show rule depth exceeded
ERROR: Failed to compile /tmp/evidence-cycle-typstpdf/manual.typ: Typst compilation failed: TypstError: maximum show rule depth exceeded
Location: /tmp/evidence-cycle-typstpdf/manual.typ
Details: maximum show rule depth exceeded
...
    sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: alpha: Typst compilation
    failed: TypstError: maximum show rule depth exceeded
```
Exit code: 2 (non-zero). No PDF is produced. Typst's own recursion-depth guard trips on the mutual
`#include()` pair — a DIFFERENT Typst-level failure signature than Section 1's `file not found`,
but equally a real, verbatim, classic `TypstError`.

**Reading:** this is a genuine RED, in the amended sense of binding constraint #4 (a real compile
fatal, not merely a structural assertion) — but it is NOT the fixture D-10 names as "the phase's
one classic-TypstError RED" (that framing is specific to Section 1's `self`/external-URL fixture,
which is this phase's own GATE-01 obligation). This is an unplanned-but-measured additional
finding: the cycle case ALSO fails today, for a different mechanistic reason (unconditional mutual
inclusion, with no traversal/cycle-detection concept at all in the current write-time emitter,
versus Section 1's iteration over the wrong list). Recorded here in full per binding constraint
#6 (measured, not guessed) — `test_state_guard_shapes_gate.py`'s cycle test is ALSO recorded
`xfail(strict=True)` against this transcript, in addition to the self/URL test.

<!-- planner-discipline-allow: maximum show rule depth exceeded -->

---

## Section 3 — `state_guard_selfref_gate` (D-06, an INVARIANCE baseline)

**`-b typst`:**
```
uv run python -m sphinx -b typst tests/fixtures/state_guard_selfref_gate /tmp/evidence-selfref-typst
```

**Raw output (verbatim, full):**
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
preparing documents... Template written to /tmp/evidence-selfref-typst/_template.typ
done
writing output... [index] done
writing output... [other] done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
build succeeded, 1 warning.
```
**Full warning list:**
- `index.rst:4: WARNING: toctree に存在しないドキュメントへの参照が含まれています 'index'
  [toc.not_readable]` (Sphinx's own "toctree contains reference to nonexisting document 'index'",
  localized to `ja` — the self-reference filtering diagnostic, per Sphinx's own pre-loop
  `all_docnames.remove(current_docname)`)

**`-b typstpdf`:** exits 0. `manual.pdf` produced.

**Verbatim `pypdf`-extracted PDF text (marker occurrence count):**
```
Self Reference Gate
Probe Author
1.0.0
1
1
Contents
2 Index ... 3
2.1 Other ... 3
2
2 Index
2.1 Other
OTHER-BODY-MARKER
3
```
`OTHER-BODY-MARKER` appears exactly ONCE. No duplicate `Index` heading anywhere.

**Reading:** this is an INVARIANCE baseline, not a RED. Sphinx's own `parse_content` already
filters the literal self-reference out of BOTH `entries` and `includefiles` before the current
emitter's `entries`-iterating loop ever sees it (this is the SAME mechanism D-03's fix targets,
but this particular exclusion happens upstream of the `entries`/`includefiles` divergence, so the
current tree already produces the post-fix-decided outcome). `test_state_guard_shapes_gate.py`'s
self-reference test therefore need not be `xfail` — it is recorded as an invariance guard the
emitter must keep passing, not a RED it must newly satisfy.

---

## Section 4 — `state_guard_glob_gate` (D-06, an INVARIANCE baseline)

**`-b typst`:**
```
uv run python -m sphinx -b typst tests/fixtures/state_guard_glob_gate /tmp/evidence-glob-typst
```

**Raw output (verbatim, full):**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 4 件のソースファイル
環境データを更新中[新しい設定] 4 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 25%] guide/alpha
ソースを読み込み中...[ 50%] guide/mike
ソースを読み込み中...[ 75%] guide/zulu
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to /tmp/evidence-glob-typst/_template.typ
done
writing output... [guide/alpha] done
writing output... [guide/mike] done
writing output... [guide/zulu] done
writing output... [index] done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
build succeeded.
```
**Full warning list:** none.

**`-b typstpdf`:** exits 0. `manual.pdf` produced.

**Verbatim `pypdf`-extracted PDF text (marker order proof):**
```
Glob Gate
Probe Author
1.0.0
1
1
Contents
2 Index ... 3
2.1 Alpha ... 3
2.2 Mike ... 3
2.3 Zulu ... 3
2
2 Index
2.1 Alpha
ALPHA-BODY-MARKER
2.2 Mike
MIKE-BODY-MARKER
2.3 Zulu
ZULU-BODY-MARKER
3
```
Alpha, then Mike, then Zulu — the SORTED docname order, not the `zulu, alpha, mike`
authoring/file-creation order. Every marker appears exactly once.

**Reading:** an INVARIANCE baseline. `sphinx/directives/other.py:109-129` expands the `:glob:`
pattern at PARSE time into `sorted(patfilter(...))`, appended to BOTH `entries` and
`includefiles` — the current `entries`-iterating emitter already sees the sorted order, so no
special-case handling is needed anywhere in the new mechanism, exactly as the Degenerate-shape
outcome table predicts. `test_state_guard_shapes_gate.py`'s glob test is recorded as an
invariance guard, not `xfail`.

---

## Section 5 — `state_guard_orphan_ref_gate` (D-06, an INVARIANCE baseline — Phase 48's own
mechanism, not this phase's)

**`-b typst`:**
```
uv run python -m sphinx -b typst tests/fixtures/state_guard_orphan_ref_gate /tmp/evidence-orphan-typst
```

**Raw output (verbatim, full):**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 2 件のソースファイル
環境データを更新中[新しい設定] 2 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 50%] index
ソースを読み込み中...[100%] orphan_doc

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to /tmp/evidence-orphan-typst/_template.typ
done
writing output... [index] done
writing output... [orphan_doc] done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
build succeeded.
```
**Full warning list:** none. (No "document is not in any toctree" warning either — Sphinx does
not warn on `:orphan:`-marked documents excluded from every toctree by design.)

**Content-file check — `index.typ` carries no toctree-emission block at all:**
```
$ grep -n 'context\|include(' index.typ
16:context { let __tsx_body = [#{
```
That single `context` match is Phase 48's OWN compile-time cross-reference guard construct
(unrelated to `visit_toctree`'s emission block) — `index.rst` has no `.. toctree::` directive at
all, so there is no toctree-emission `context { ... }` block of the kind this phase's mechanism
touches.

**`-b typstpdf`:** exits 0. `manual.pdf` produced.

**Verbatim `pypdf`-extracted PDF text:**
```
Orphan Reference Gate
Probe Author
1.0.0
1
1 Contents
Contents
2 Index ... 3
2
2 Index
See Orphan Section.
3
```
`ORPHAN-BODY-MARKER` is ABSENT. The `:ref:`orphan-target-label`` reference degrades to plain text
("See Orphan Section.") rather than a working label link, and the compile succeeds with no fatal.

**Reading:** an INVARIANCE baseline for THIS phase — the degradation is Phase 48's existing
compile-time `query(<label>).len() > 0` guard, already correctly firing on the unfixed tree, since
`orphan_doc` is in no `env.toctree_includes[...]` value reachable from `index` regardless of
which emitter mechanism (write-time ledger vs. compile-time state guard) is in use.
`test_state_guard_shapes_gate.py`'s orphan test asserts this behaviour is UNCHANGED, not newly
achieved.

---

## Section 6 — `state_guard_three_master_gate` (SC#2/COMP-09, a NON-FATAL content-drop RED —
defect A/the diamond reproduced live across three masters)

**`-b typst`:**
```
uv run python -m sphinx -b typst tests/fixtures/state_guard_three_master_gate /tmp/evidence-3m-typst
```

**Raw output (verbatim, full):**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 6 件のソースファイル
環境データを更新中[新しい設定] 6 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 17%] common_a
ソースを読み込み中...[ 33%] common_b
ソースを読み込み中...[ 50%] m1
ソースを読み込み中...[ 67%] m2
ソースを読み込み中...[ 83%] m3
ソースを読み込み中...[100%] mid

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aba9a064385780508/tests/fixtures/state_guard_three_master_gate/common_a.rst: document is referenced in multiple toctrees: ['m1', 'm2'], selecting: m2 <- common_a
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aba9a064385780508/tests/fixtures/state_guard_three_master_gate/common_b.rst: document is referenced in multiple toctrees: ['m2', 'm3', 'mid'], selecting: mid <- common_b
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-aba9a064385780508/tests/fixtures/state_guard_three_master_gate/mid.rst: document is referenced in multiple toctrees: ['m1', 'm3'], selecting: m3 <- mid
完了
preparing documents... Template written to /tmp/evidence-3m-typst/_template.typ
done
writing output... [common_a] done
writing output... [common_b] done
writing output... [m1] done
writing output... [m2] done
writing output... [m3] done
writing output... [mid] done
typst: wrote 3 wrapper file(s) -- compile these: manual1.typ, manual2.typ, manual3.typ
build succeeded.
```
**Full warning list (INFO-level "selecting" notices, PROJECT.md's own explicit non-portable
`_check_toc_parents` lexicographic tiebreak — recorded verbatim, per the instruction NOT to port
this message's own semantics into this phase's own mechanism):**
- `common_a.rst: document is referenced in multiple toctrees: ['m1', 'm2'], selecting: m2 <- common_a`
- `common_b.rst: document is referenced in multiple toctrees: ['m2', 'm3', 'mid'], selecting: mid <- common_b`
- `mid.rst: document is referenced in multiple toctrees: ['m1', 'm3'], selecting: m3 <- mid`

Exit code: 0. These are Sphinx's own environment-level "which toctree parent claims this
document" notices — governing HTML/LaTeX-style single-parent trees, not this phase's own DFS
edge-set derivation (which is per-master, not global).

**`-b typstpdf`:** exits 0. All three PDFs (`manual1.pdf`, `manual2.pdf`, `manual3.pdf`) are
produced — no compile fatal.

**Verbatim emitted include lines (the mechanism, made visible — the SAME build-scoped ledger
Section 1 already exposed, now shown dropping content SILENTLY across three masters):**
```
$ grep -n 'include(' m1.typ m2.typ m3.typ mid.typ
m1.typ:17:  include("mid.typ")
m1.typ:18:  include("common_a.typ")
m2.typ:17:  include("common_b.typ")
$ grep -n 'context' mid.typ m3.typ
mid.typ:15:context {
m3.typ:15:context {
```
`m2.typ`'s own `common_a` entry produces NO include line at all (silently dropped — `common_a`
was already claimed by the write-time ledger when `m1` was translated first, in alphabetical
write order `common_a, common_b, m1, m2, m3, mid`). `mid.typ`'s own `common_b` entry ALSO produces
no include line (claimed by `m2`'s translation, which ran before `mid`'s in write order).
`m3.typ`'s toctree (`[common_b, mid]`) produces NO includes at all — BOTH of its own listed
children were already claimed elsewhere by write time.

**Verbatim `pypdf`-extracted PDF text, all three masters (per-marker occurrence proof):**

`manual1.pdf` (M1) — `common_a` renders correctly under M1's own direct toctree position, but
`mid`'s section is completely EMPTY (its own child `common_b` never got an include emitted):
```
Three Master Gate — M1
Probe Author
1.0.0
1
1
Contents
2 M1 ... 3
2.1 Mid ... 3
2.2 Common A ... 3
2
2 M1
2.1 Mid
2.2 Common A
COMMON-A-MARKER
3
```
`manual2.pdf` (M2) — only `common_b` renders; `common_a` is ENTIRELY ABSENT (no heading, no
marker — its toctree entry was silently dropped at write time):
```
Three Master Gate — M2
Probe Author
1.0.0
1
1
Contents
2 M2 ... 3
2.1 Common B ... 3
2
2 M2
2.1 Common B
COMMON-B-MARKER
3
```
`manual3.pdf` (M3) — NEITHER `common_b` NOR `mid` renders at all, not even an empty heading (both
of M3's own toctree entries were already claimed by earlier-written masters):
```
Three Master Gate — M3
Probe Author
1.0.0
1
1
Contents
2 M3 ... 3
2
2 M3
3
```

**Numeric summary:** `COMMON-A-MARKER` appears in `manual1.pdf` only (1 of 3 masters that toctree
it — M2's own copy is silently dropped). `COMMON-B-MARKER` appears in `manual2.pdf` only (1 of 3
masters that toctree it — M1's `mid`-nested copy and M3's own direct copy are BOTH silently
dropped). Every marker's expected post-fix count, per the Fixture specification's hand-derived
edge sets, is exactly ONE PER MASTER (3 total occurrences of `COMMON-B-MARKER` across the three
PDFs, one per master's own PDF) — the pre-fix tree currently delivers only 1 of the 3 required
occurrences for `COMMON-B-MARKER` and only 1 of the 2 required occurrences for `COMMON-A-MARKER`.

**Reading:** this is a real, silent, NON-FATAL content-drop RED — defect A / the diamond,
reproduced live across three independent masters rather than the two-master case PROJECT.md
originally measured. It demonstrates, with a real compile, why a build-scoped ledger cannot serve
more than one master: whichever master's translation happens to run first (in this case, simple
alphabetical write order) silently wins every shared child, and every OTHER master's own,
otherwise-correct toctree entry for that same child is dropped with ZERO warning and ZERO
compile-time signal. `test_state_guard_shapes_gate.py`'s three-master test is recorded
`xfail(strict=True, reason="... 49-04 ...")` against this exact transcript.

---

## Section 7 — `state_guard_substring_key_gate` (COMP-06, an INVARIANCE baseline at the FIXTURE
level — the array-vs-string semantics hazard is proven separately, at the SYNTAX level, by
`49-EVIDENCE.md` Probe 5/Probe 6, since this phase's own state-guard mechanism does not exist yet)

**`-b typst`:**
```
uv run python -m sphinx -b typst tests/fixtures/state_guard_substring_key_gate /tmp/evidence-substr-typst
```

**Raw output (verbatim, full):**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 3 件のソースファイル
環境データを更新中[新しい設定] 3 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 33%] guide
ソースを読み込み中...[ 67%] guideext
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... /home/yuta/Documents/typsphinx/.claude/worktrees/agent-aba9a064385780508/tests/fixtures/state_guard_substring_key_gate/guide.rst: document is referenced in multiple toctrees: ['guideext', 'index'], selecting: index <- guide
完了
preparing documents... Template written to /tmp/evidence-substr-typst/_template.typ
done
writing output... [guide] done
writing output... [guideext] done
writing output... [index] done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
build succeeded.
```
**Full warning list (an INFO-level "selecting" notice, same class as Section 6's — recorded
verbatim, not ported):**
- `guide.rst: document is referenced in multiple toctrees: ['guideext', 'index'], selecting: index <- guide`

Exit code: 0.

**Verbatim emitted include lines (the mechanism, made visible):**
```
$ grep -n 'include(' index.typ guideext.typ
guideext.typ:17:  include("guide.typ")
index.typ:17:  include("guideext.typ")
```
`index.typ`'s OWN second toctree entry (`guide`) produces NO include line — silently dropped by
the write-time ledger, because `guideext.rst` was written FIRST (alphabetical write order
`guide, guideext, index`) and already claimed `guide` when ITS OWN toctree was translated.

**`-b typstpdf`:** exits 0. `manual.pdf` produced.

**Verbatim `pypdf`-extracted PDF text:**
```
Substring Key Gate
Probe Author
1.0.0
1
1
Contents
2 Index ... 3
2.1 GuideExt ... 3
2
2 Index
2.1 GuideExt
2.1.1 Guide
GUIDE-SUBSTRING-MARKER
GUIDEEXT-SUBSTRING-MARKER
3
```
`GUIDE-SUBSTRING-MARKER` appears exactly ONCE, nested under `GuideExt` (at the deeper heading
level), never at `Index`'s own direct position — visually IDENTICAL to the post-fix decided
outcome.

**Reading:** an INVARIANCE baseline at the FIXTURE level. In this SPECIFIC single-master
scenario, the current write-time ledger's dedup (whichever document's translation runs first
claims the child) happens to coincide with the post-fix DFS's first-encounter-wins rule (whichever
PARENT is listed/recursed-into first in the MASTER's own traversal claims the child) — both
produce the SAME visible result here, because there is only one master and the write order
happens to process `guideext` (which itself toctrees `guide`) before `index`'s own second entry
for `guide` is considered. This coincidence is exactly why the array-vs-string SEMANTICS hazard
this fixture is built to detect cannot be exercised at the fixture/PDF level pre-fix — the hazard
only exists once the state-guard MECHANISM (a real Typst array, testable for the omitted-trailing-
comma degradation) is in place. That mechanism-level proof is `49-EVIDENCE.md` Probe 5 (the
degradation, recorded) and Probe 6 (the correct dark-guard semantics, recorded) — both already
closed at the SYNTAX level in plan 49-01, against this phase's own decided key spellings.
`test_state_guard_shapes_gate.py`'s substring test is recorded `xfail(strict=True)` not because
the PRE-FIX PDF differs (it does not), but because the test's OWN assertions read the published
edge-key ARRAY directly (a construct that does not exist until 49-04's emitter lands) — the PDF-
level marker-count assertion is an invariance guard within the same test, and only the array-
membership assertions are the true xfail surface.

---

## What this evidence licenses

- **Section 1 (`state_guard_self_and_url_gate`) is a RED** — a real, verbatim, classic
  `TypstError: file not found` compile fatal. This is D-10's explicitly named "phase's one classic
  RED"; binding constraint #4's non-fatal amendment does not apply to it.
- **Section 2 (`state_guard_cycle_gate`) is a RED** — an ADDITIONAL, unplanned-but-measured
  classic `TypstError: maximum show rule depth exceeded` compile fatal, discovered by real
  measurement rather than assumed. It is NOT the fixture D-10 names as the phase's "one" classic
  RED (that naming is specific to Section 1); it is recorded here in full because binding
  constraint #6 requires every claim to be measured, and the cycle case's true pre-fix behaviour
  turned out to differ from a passing assumption.
- **Section 3 (`state_guard_selfref_gate`) is an INVARIANCE BASELINE** — Sphinx's own upstream
  self-reference filtering already produces the post-fix-decided outcome today; no fix is needed
  for this specific shape, only a non-regression guard.
- **Section 4 (`state_guard_glob_gate`) is an INVARIANCE BASELINE** — Sphinx's own parse-time
  sorted glob expansion already produces the post-fix-decided outcome today.
- **Section 5 (`state_guard_orphan_ref_gate`) is an INVARIANCE BASELINE** — Phase 48's existing
  compile-time cross-reference guard, unrelated to this phase's own mechanism, already produces
  the correct degradation today.
- **Section 6 (`state_guard_three_master_gate`) is a NON-FATAL RED** — a real, silent,
  zero-warning content-drop defect (defect A / the diamond), reproduced live across three
  independent masters with a real compile. This is the SC#2/COMP-09 coverage obligation's own
  pre-fix baseline.
- **Section 7 (`state_guard_substring_key_gate`) is an INVARIANCE BASELINE at the fixture/PDF
  level** — the array-vs-string semantics hazard this fixture is built to detect can only manifest
  once the state-guard array mechanism exists (49-04); it is already proven at the SYNTAX level by
  `49-EVIDENCE.md` Probes 5/6. This fixture's own PDF-level assertions do not change post-fix; only
  its array-membership assertions (impossible to write against a mechanism that does not exist yet)
  are the true xfail surface.

Every Sphinx warning/notice recorded in Sections 1-7 above is this phase's OWN "no lost
diagnostics" baseline — `test_state_guard_shapes_gate.py`'s backstop truth asserts every one of
these strings is STILL present in the captured warning list after 49-04's emitter lands, so a
silently-removed diagnostic becomes a test failure rather than an invisible regression.
