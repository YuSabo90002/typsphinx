# Phase 49 Plan 02 -- Pre-Fix RED Evidence

**Captured:** 2026-08-14, against the unfixed tree (this plan's own worktree, before any
`typsphinx/` change -- `git status --porcelain typsphinx/` printed nothing throughout Task 2, and
`git status --short` showed only this file plus Task 1's already-committed fixture directories).

**Worktree provenance:**

```
$ uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a05871287a970fd02/typsphinx/__init__.py
```

-- a path inside THIS worktree, confirming `import typsphinx` binds to the unmodified worktree
copy, not the main checkout's editable install.

**Dependency versions read live this session** (`uv run python -c "import importlib.metadata as
m; print(m.version('typst')); print(m.version('sphinx')); print(m.version('pypdf'))"`):
`typst` `0.15.0`, `sphinx` `9.1.0`, `pypdf` `6.14.2` -- matching `49-EVIDENCE.md`'s own
live-verified readings, no drift.

**Binding constraint #4 compliance:** Failure mode 1's `-b typstpdf` build exits 0, so -- per
binding constraint #4's amended definition of RED -- its RED is a content-level `pypdf` count
measurement, never an exit code or a `TypstError`. Every transcript below is the VERBATIM raw
output of a real `sphinx-build` subprocess (`uv run python -m sphinx ...`) run inside this
worktree, or a real `typst.query()`/`pypdf.PdfReader.extract_text()` readback of the artifact that
build produced -- nothing here is hand-reconstructed or read off any future emitter (binding
constraint #6). Both fixtures used are the ones Task 1 of this plan committed
(`tests/fixtures/state_guard_two_master_gate/`, `tests/fixtures/state_guard_mirror_pair_gate/`),
unmodified.

---

## Failure mode 1 -- COMP-07, defect A, a non-fatal silent omission

**Fixture:** `tests/fixtures/state_guard_two_master_gate/` -- `typst_documents = [("index",
"manual.typ", ...), ("bmaster", "bmanual.typ", ...)]`. `index.rst` (master A) toctrees `zmid` then
`shared`; `zmid.rst` toctrees `shared`; `bmaster.rst` (master B, `:orphan:`) toctrees `shared`
directly. `shared.rst`'s body carries the marker `SHARED-CHAPTER-MARKER`, spelled to match the
2026-08-11 baseline recorded in `PROJECT.md` lines 74-78 verbatim.

**Command:** `uv run python -m sphinx -b typstpdf tests/fixtures/state_guard_two_master_gate
<tmp-build-dir>`

**Raw output (verbatim):**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typstpdf]: 更新された 6 件のソースファイル
環境データを更新中[新しい設定] 6 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 17%] bmaster
ソースを読み込み中...[ 33%] emptytoc
ソースを読み込み中...[ 50%] index
ソースを読み込み中...[ 67%] shared
ソースを読み込み中...[ 83%] sub/nested
ソースを読み込み中...[100%] zmid

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a05871287a970fd02/tests/fixtures/state_guard_two_master_gate/shared.rst: document is referenced in multiple toctrees: ['bmaster', 'index', 'zmid'], selecting: zmid <- shared
完了
preparing documents... Template written to <tmp-build-dir>/_template.typ
done
writing output... [bmaster] done
writing output... [emptytoc] done
writing output... [index] done
writing output... [shared] done
writing output... [sub/nested] done
writing output... [zmid] done
typst: wrote 2 wrapper file(s) -- compile these: bmanual.typ, manual.typ
Compiling 2 master document(s) to PDF...
Generated PDF: <tmp-build-dir>/manual.pdf
Generated PDF: <tmp-build-dir>/bmanual.pdf
build succeeded.
```
**Exit code: 0.** The only diagnostic is Sphinx's OWN `document is referenced in multiple
toctrees: [...], selecting: zmid <- shared` consistency message (`_check_toc_parents`,
`sphinx/environment/__init__.py:942-959`, per `PROJECT.md` lines 96-104 -- typsphinx's own
mechanism does not consult or port this message, and this transcript is the live confirmation that
Sphinx emits it independently of anything typsphinx does). There is no collision warning, no error,
and no other diagnostic.

**`pypdf`-extracted occurrence count of `SHARED-CHAPTER-MARKER`, each PDF read independently
(`pypdf.PdfReader(...).pages`, `extract_text()` joined and `.count()`-ed):**
```
manual.pdf   (master A / index)   : 0
bmanual.pdf  (master B / bmaster) : 1
```
**This matches the 2026-08-11 baseline recorded in `PROJECT.md` lines 74-78 exactly** (master A:
0, master B: 1, exit 0, no collision warning). No discrepancy to record.

**Mechanism, stated in prose because the transcript alone does not show it (verified by reading
the emitted `.typ` files directly, below):**

`index.typ`'s toctree context block emits `include("zmid.typ")` only -- there is no second, dark
`include("shared.typ")` line at all, because the current write-time ledger's emptiness check is a
hard `continue`, not a guarded-but-emitted line:
```
context {
  set heading(offset: heading.offset + 1)
  include("zmid.typ")
}
```
`zmid.typ`'s own context block is EMPTY -- no `include("shared.typ")` line either:
```
context {
  set heading(offset: heading.offset + 1)
}
```
`bmaster.typ`'s context block DOES carry `include("shared.typ")`:
```
context {
  set heading(offset: heading.offset + 1)
  include("shared.typ")
}
```
Sphinx writes content files in docname-sorted order (confirmed by the progress log above:
`bmaster` (17%), `emptytoc` (33%), `index` (50%), `shared` (67%), `sub/nested` (83%), `zmid`
(100%) -- alphabetical). `bmaster` sorts before both `index` and `zmid`, so `bmaster`'s own
toctree is TRANSLATED FIRST. When the translator visits `bmaster`'s single toctree entry
(`shared`), the build-scoped `_included_docnames` ledger does not yet contain `shared` -- it
claims it, emits the unconditional `include("shared.typ")`, and adds `"shared"` to the ledger.
When `index`'s own toctree is translated next (entries `zmid`, `shared` in that order), `zmid` is
not yet in the ledger -- claimed, `include("zmid.typ")` emitted. `shared` IS already in the ledger
(claimed by `bmaster` moments earlier) -- skipped entirely, no include line of any kind. When
`zmid`'s own toctree is translated last, its sole entry `shared` is ALSO already in the ledger --
skipped too.

**The decision is baked into the shared content file's *including parents* at write time by a
single build-scoped ledger, and the parent whose toctree is translated first wins the claim --
decided by docname sort order (`bmaster` < `index` alphabetically), not by any per-master
traversal semantics.** A build-scoped ledger cannot express a per-master answer, which is exactly
the decision this phase moves to compile time.

---

## Failure mode 2 -- COMP-09, the diamond, from the same fixture

Same build as Failure mode 1 (`<tmp-build-dir>` above).

**Directory listing proving exactly one shared content file exists on disk:**
```
$ find <tmp-build-dir> -maxdepth 2 -name '*.typ' | sort
<tmp-build-dir>/_template.typ
<tmp-build-dir>/bmanual.typ
<tmp-build-dir>/bmaster.typ
<tmp-build-dir>/emptytoc.typ
<tmp-build-dir>/index.typ
<tmp-build-dir>/manual.typ
<tmp-build-dir>/shared.typ
<tmp-build-dir>/sub/nested.typ
<tmp-build-dir>/zmid.typ
```
Exactly one `shared.typ` at the build root -- there is no second copy anywhere in the tree.

**Its SHA-256 digest (the same physical file both masters' compiles read from):**
```
$ sha256sum <tmp-build-dir>/shared.typ
672b5d2c7c86e73b12c503341e61477983317d7ac6fef08cb5f8a8f4dff012b5  <tmp-build-dir>/shared.typ
```

**`pypdf`-extracted occurrence count of the shared child's marker in each master's PDF (same
numbers as Failure mode 1, restated here for the diamond's own claim):**
```
manual.pdf   (master A / index)   : 0
bmanual.pdf  (master B / bmaster) : 1
```

**What these numbers prove pre-fix:** one physical file on disk (`shared.typ`, one SHA-256
digest) produces DIFFERENT per-master outcomes only in the trivial, degenerate sense that a
build-scoped ledger picks exactly ONE winner across the WHOLE build -- not because the mechanism
can express "included here, also included there, nested differently in each." The diamond shape
this fixture also carries (`shared` reachable via `bmaster` directly AND via `index -> zmid ->
shared`) demonstrates the SAME failure: only the parent whose toctree is translated first (here,
`bmaster`, alphabetically first) ever gets a live `include()`; every other parent that ALSO
legitimately reaches `shared` sees it silently vanish, with no guard, no dark line, no diagnostic.

**What they must become post-fix:** exactly ONE occurrence of `SHARED-CHAPTER-MARKER` in EACH of
`manual.pdf` and `bmanual.pdf`, both produced from the SAME on-disk `shared.typ` (verified again by
SHA-256 identity, since the content file is written once per docname regardless of which masters
reach it) -- the per-master difference expressed entirely through each wrapper's own published
`state`, not through two divergent content files.

---

## Failure mode 3 -- COMP-08, document-order interleaving, recorded as the CURRENT behaviour

Same build as Failure modes 1-2.

**`pypdf`-extracted text of `manual.pdf` (master A / index), verbatim, in full:**
```
Two Master Gate - Index
Probe Author
1.0.0
1
1
Contents
2 Index . . . [...page-number leaders omitted for length, unchanged content otherwise...] . . . 3
2.1 ZMid . . . [...] . . . 3
3 Indices and tables . . . [...] . . . 3
2
2 Index
PROSE-BEFORE-MARKER
2.1 ZMid
3 Indices and tables
PROSE-AFTER-MARKER
3
```
(The two omitted spans above are the outline/table-of-contents page-number leader dots
`typst`'s `#outline()` renders for each entry -- elided here only for transcript length; every
other character is verbatim `pypdf` output, unedited.)

**Ordered marker offsets within the BODY portion (after the outline), read directly from the
string above:** `PROSE-BEFORE-MARKER` at the position immediately after the "2 Index" body
heading, then `2.1 ZMid` (the ZMid section heading, entered via the toctree's own
`include("zmid.typ")`), then `3 Indices and tables` (index's own trailing section, part of
`index.rst`'s OWN body, unrelated to the toctree mechanism), then `PROSE-AFTER-MARKER`.

**This is an INVARIANCE baseline, not a RED.** The current emitter already emits `include()` at
the toctree's own position inside `index.typ` (see Failure mode 1's `index.typ` excerpt above),
strictly BEFORE the "Indices and tables" heading and `PROSE-AFTER-MARKER` line that follow it in
`index.rst`'s own source order. The observable pre-fix ordering (`PROSE-BEFORE-MARKER` < `ZMid`
section < `Indices and tables` heading < `PROSE-AFTER-MARKER`) already holds exactly as `49-CONTEXT.md`'s "rejected flattened design" discussion says it must -- a flattened wrapper-side
include graph (the alternative design PROJECT.md measured and rejected) would have broken this by
moving every include to the wrapper, ahead of the trailing section; the state-guarded design this
phase implements keeps the include at the toctree's own position and therefore does not regress
this property. `SHARED-CHAPTER-MARKER` does not appear in this transcript at all (Failure mode 1's
own 0-count), so the FULL four-marker sequence the post-fix gate will assert (`PROSE-BEFORE` <
`ZMid` body < `Shared` body < `PROSE-AFTER`) cannot be observed on the unfixed tree -- only the
subset that IS currently reachable (`PROSE-BEFORE` < `ZMid` < `Indices-and-tables` < `PROSE-AFTER`)
is measured here, and it is already correct. This section is recorded as an **invariance**
baseline: the property must not regress once `shared` starts appearing in `manual.pdf` too.

---

## Failure mode 4 -- COMP-10, the mirror pair, recorded as the CURRENT resolved heading levels

**Fixture:** `tests/fixtures/state_guard_mirror_pair_gate/` -- `root_doc = "xmastera"`,
`typst_documents = [("xmastera", "mastera.typ", ...), ("xmasterb", "masterb.typ", ...),
("soloist", "solomaster.typ", ...)]`. `xmastera.rst` (master A) toctrees `zmid` then `shared`;
`xmasterb.rst` (master B, `:orphan:`) toctrees `shared` then `zmid` -- the MIRRORED order;
`zmid.rst` toctrees `shared`; `soloist.rst` (`:orphan:`) carries no toctree at all.

**Command:** `uv run python -m sphinx -b typst tests/fixtures/state_guard_mirror_pair_gate
<tmp-build-dir>`

**Raw output (verbatim):**
```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 5 件のソースファイル
環境データを更新中[新しい設定] 5 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 20%] shared
ソースを読み込み中...[ 40%] soloist
ソースを読み込み中...[ 60%] xmastera
ソースを読み込み中...[ 80%] xmasterb
ソースを読み込み中...[100%] zmid

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a05871287a970fd02/tests/fixtures/state_guard_mirror_pair_gate/shared.rst: document is referenced in multiple toctrees: ['xmastera', 'xmasterb', 'zmid'], selecting: zmid <- shared
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a05871287a970fd02/tests/fixtures/state_guard_mirror_pair_gate/zmid.rst: document is referenced in multiple toctrees: ['xmastera', 'xmasterb'], selecting: xmasterb <- zmid
完了
preparing documents... Template written to <tmp-build-dir>/_template.typ
done
writing output... [shared] done
writing output... [soloist] done
writing output... [xmastera] done
writing output... [xmasterb] done
writing output... [zmid] done
typst: wrote 3 wrapper file(s) -- compile these: mastera.typ, masterb.typ, solomaster.typ
build succeeded.
```
**Exit code: 0.** Again, only Sphinx's own `document is referenced in multiple toctrees`
consistency messages (twice this time -- once for `shared`, once for `zmid` itself, since
`xmasterb`'s own direct `shared` entry and `xmastera`'s `zmid` entry both compete for `zmid` and
`shared` respectively across the two masters' toctrees). No error, no collision warning.

**`typst.query(..., "heading", field="level", root=<tmp-build-dir>)` result for each wrapper,
verbatim:**
```
mastera.typ   levels: [1, 1, 1, 2, 2]
masterb.typ   levels: [1, 1, 1]
solomaster.typ levels: [1, 1, 1]
```

**Outline (level, title) readback for `mastera.typ`, confirming which heading sits at which
level** (`typst.query(..., "heading", root=<tmp-build-dir>)`, body text extracted per element):
```
[(1, ''), (1, 'Contents'), (1, 'XMasterA'), (2, 'ZMid'), (2, 'Shared')]
```
and for `masterb.typ`:
```
[(1, ''), (1, 'Contents'), (1, 'XMasterB')]
```

**Mechanism (verified by reading the emitted `.typ` files directly):** content files are written
in docname-sorted order (`shared`, `soloist`, `xmastera`, `xmasterb`, `zmid` -- confirmed by the
progress log above). `xmastera`'s toctree is translated BEFORE `xmasterb`'s. `xmastera.typ`'s
context block therefore carries BOTH entries as unconditional, SIBLING includes at the SAME
offset (both claimed on first encounter, within the SAME toctree scope -- the current mechanism
does not recurse into `zmid`'s own toctree before moving to `xmastera`'s next entry):
```
context {
  set heading(offset: heading.offset + 1)
  include("zmid.typ")
  include("shared.typ")
}
```
This is why `Shared` resolves at level 2 (a DIRECT sibling of `ZMid`) rather than level 3 (nested
UNDER `ZMid`) -- the write-time mechanism has no per-parent DFS-recursion step; both of
`xmastera`'s own toctree entries are simply emitted unconditionally, one after another, in the
SAME scope. When `xmasterb`'s own toctree is translated next, BOTH of its entries (`shared`,
`zmid`) are ALREADY in the build-scoped ledger (claimed by `xmastera` moments earlier) -- so
`xmasterb.typ`'s context block is completely EMPTY:
```
context {
  set heading(offset: heading.offset + 1)
}
```
`masterb.typ`'s resolved level sequence (`[1, 1, 1]`, i.e. only the template's own headings plus
`XMasterB` itself) confirms `xmasterb` sees NO shared child at all -- shorter than the post-fix
expectation, exactly as `49-02-PLAN.md`'s own `<read_first>` note anticipated ("under the current
build-scoped ledger the second master may see no shared child at all, so its sequence may be
shorter than the post-fix expectation -- record what is observed, not what would be tidy").

`solomaster.typ`'s resolved level sequence (`[1, 1, 1]`) confirms the no-nesting control: `soloist`
carries no toctree at all (`env.toctree_includes.get("soloist", [])` is empty, so `visit_toctree`
never fires for it), and its own heading resolves at level 1 with no ancestor offset applied --
this observation is UNCHANGED by the phase 49 fix (a master with nothing to nest resolves at the
top level regardless of the mechanism), so this half of Failure mode 4 is an **invariance**
baseline, not a RED.

**Comparison against `49-EXPECTED-STRUCTURE.md`'s hand-derived post-fix sequences:**

| Master | Post-fix expected | Pre-fix observed | Match? |
|---|---|---|---|
| `xmastera` | `[1, 2, 3]` (`XMasterA`, `ZMid` nested at 2, `Shared` nested under `ZMid` at 3) | `[1, 1, 1, 2, 2]` (template headings + `XMasterA` at 1, `ZMid` AND `Shared` both direct siblings at 2) | **DIVERGES** -- `Shared` sits at level 2 (direct), not level 3 (nested under `ZMid`) |
| `xmasterb` | `[1, 2, 2]` (`XMasterB` at 1, `Shared` direct at 2, `zmid` direct-and-empty also at 2) | `[1, 1, 1]` (template headings + `XMasterB` at 1 only -- no `Shared`, no `ZMid` heading at all) | **DIVERGES** -- shorter: `xmasterb` sees neither child, not "both children present at level 2" |
| `soloist` | resolves at top level (no ancestor offset) | resolves at top level (no ancestor offset; `[1, 1, 1]`) | **MATCHES** (invariance) |

---

## What this evidence licenses

Per ROADMAP binding constraint #4's non-fatal amendment, each of this phase's closed defects now
has its pre-fix RED assertion named and captured, verbatim, before implementation starts:

- **Failure mode 1 (COMP-07, defect A) is a RED**: the `pypdf`-extracted 0/1 marker-count split
  matches the 2026-08-11 baseline exactly, and the mechanism (build-scoped ledger, docname-sort-
  order winner) is confirmed by direct inspection of the emitted `.typ` files.
- **Failure mode 2 (COMP-09, the diamond) is a RED**: the SAME on-disk `shared.typ` (one SHA-256
  digest) produces a 0/1 split rather than a 1/1 split, because the build-scoped ledger picks
  exactly one winner across the whole build rather than one winner PER MASTER.
- **Failure mode 3 (COMP-08, interleaving) is an INVARIANCE baseline**, not a RED: the currently
  observable ordering (`PROSE-BEFORE` < `ZMid` < `Indices-and-tables` < `PROSE-AFTER`) already
  holds correctly on the unfixed tree, and must not regress once `Shared` starts appearing in
  `manual.pdf` too.
- **Failure mode 4 (COMP-10, the mirror pair) is a RED for both `xmastera` and `xmasterb`**
  (resolved level sequences diverge from the post-fix hand-derivation in both directions -- one
  too shallow, one entirely missing its shared children) **and an INVARIANCE baseline for
  `soloist`** (the no-nesting control already resolves correctly and must continue to).

Every transcript above is raw captured output from a real `sphinx-build` subprocess or a real
`typst.query()`/`pypdf` readback of the artifact that subprocess produced -- no value in this
document was hand-reconstructed.
