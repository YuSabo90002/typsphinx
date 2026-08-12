# Phase 48 Plan 01 — Pre-Fix RED Evidence

**Captured:** 2026-08-12, against the unfixed tree (this plan's own worktree, before any
`typsphinx/` change — `git status --porcelain typsphinx/` prints nothing throughout Task 1, and
`git status --short` shows only the three new fixture directories as untracked).

**Binding constraint #4 compliance:** every transcript below is the VERBATIM raw output of a real
`sphinx-build` subprocess run inside this plan's own provisioned worktree venv
(`uv sync --extra dev` with `VIRTUAL_ENV`/`UV_PROJECT_ENVIRONMENT` unset, per `CLAUDE.md`'s
mandatory worktree-isolated execution protocol). Isolation independently confirmed:

```
$ uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a6f36a8dcb0f9def8/typsphinx/__init__.py
```

— a path inside THIS worktree, confirming `import typsphinx` binds to the unmodified worktree
copy, not the main checkout's editable install.

Nothing in this document is derived from a hand-edited or reconstructed artifact (binding
constraint #6). Failure mode 1's evidence is a single, direct `sphinx-build -b typstpdf` run
against the committed fixture — no `typst.compile()` probe, no hand-assembled transcript.

---

## Failure mode 1 — XREF-03, the unguarded cross-document form (per-master divergence)

**Fixture:** `tests/fixtures/xref_per_master_guard_gate/` —
`typst_documents = [("index", "alpha.typ", "Alpha Master", "Probe Author"), ("bravo",
"bravo_master.typ", "Bravo Master", "Probe Author")]`, `extensions = ["typsphinx",
"sphinx.ext.autosectionlabel"]`. `index.rst` (master alpha) toctrees `target` and carries a
`:ref:` (via `autosectionlabel`) to `target.rst`'s single section, "Guarded Target Section".
`bravo.rst` (master bravo) is marked `:orphan:`, carries NO toctree of its own, and carries the
byte-identical `:ref:` sentence.

### Mechanism, stated before the transcript because the transcript alone does not show it

`_compute_master_included_docnames()` (`typsphinx/builder.py:257-322`) seeds its BFS from EVERY
master docname (`index` AND `bravo`) and returns the union of docnames reachable from SOME
compiled master. `target` is reachable only from `index`'s toctree, but because the set is a
UNION across masters, `target` still lands in the shared set that BOTH `index`'s and `bravo`'s
references are judged against. Both content files therefore take the non-degrade path and emit
the IDENTICAL real `link(<target:guarded-target-section>, ...)` — confirmed below, byte-identical.
Bravo's wrapper (`bravo_master.typ`), which physically `#include()`s only `bravo.typ` (never
`target.typ`), then fails to resolve that label at Typst compile time. The build-time union
cannot express a per-master answer — exactly the decision this phase moves to compile time.

**Verbatim emitted `index.typ` reference line** (from `uv run python -m sphinx -b typst
tests/fixtures/xref_per_master_guard_gate /tmp/permaster-typst`, exit 0, no warning):

```
par({text("See ")
link(<target:guarded-target-section>, 
text("Guarded Target Section"))
text(" for the guarded section.")})
```

**Verbatim emitted `bravo.typ` reference line, same build:**

```
par({text("See ")
link(<target:guarded-target-section>, 
text("Guarded Target Section"))
text(" for the guarded section.")})
```

The two content files AGREE at write time — both emit the exact same plain `link(...)` label
link, byte-for-byte. `bravo_master.typ`'s own `#include()` statement pulls in only `bravo.typ`:

```
#include("bravo.typ")
```

— `target.typ` is never mentioned in `bravo_master.typ`, so the label `<target:guarded-target-section>`
`bravo.typ` links to does not exist in `bravo_master.typ`'s compiled document.

### `-b typstpdf` — the direct build fatal

**Command:** `uv run python -m sphinx -b typstpdf tests/fixtures/xref_per_master_guard_gate
/tmp/permaster-pdf`

**Raw output (verbatim, full transcript against the committed fixture, nothing reconstructed):**

```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typstpdf]: 更新された 3 件のソースファイル
環境データを更新中[新しい設定] 3 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 33%] bravo
ソースを読み込み中...[ 67%] index
ソースを読み込み中...[100%] target

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to /tmp/permaster-pdf/_template.typ
done
writing output... [bravo] done
writing output... [index] done
writing output... [target] done
typst: wrote 2 wrapper file(s) -- compile these: alpha.typ, bravo_master.typ
Compiling 2 master document(s) to PDF...
Generated PDF: /tmp/permaster-pdf/alpha.pdf
Typst compilation failed at /tmp/permaster-pdf/bravo_master.typ: TypstError: label `<target:guarded-target-section>` does not exist in the document
ERROR: Failed to compile /tmp/permaster-pdf/bravo_master.typ: Typst compilation failed: TypstError: label `<target:guarded-target-section>` does not exist in the document
Location: /tmp/permaster-pdf/bravo_master.typ
Details: label `<target:guarded-target-section>` does not exist in the document

...

Traceback
=========

      File "typsphinx/builder.py", line 1490, in finish
        raise ExtensionError(
            f"typstpdf: {len(failures)} master document(s) failed: {summary}"
        )
    sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: bravo: Typst compilation
    failed: TypstError: label `<target:guarded-target-section>` does not exist in the document
    Location: /tmp/permaster-pdf/bravo_master.typ
    Details: label `<target:guarded-target-section>` does not exist in the document
```

Exit code: 2 (non-zero). Every byte shown came from the unmodified, committed fixture build — no
`typst.compile()` call, no hand-edited reconstruction appears anywhere in this section.

**Note:** `alpha.pdf` (the well-formed sibling master reaching `target` legitimately through its
own toctree) DID compile: `Generated PDF: /tmp/permaster-pdf/alpha.pdf` appears in the transcript
above, BEFORE the fatal. The failure is isolated to `bravo_master.typ`.

**Conclusion:** the build-time union cannot express a per-master answer, which is exactly the
decision this phase moves to compile time.

<!-- planner-discipline-allow: does not exist in the document -->

---

## Failure mode 2 — D-05, citation reference inside a captioned code block

**Fixture:** `tests/fixtures/citation_caption_dangling_label_gate/` — single well-formed entry
`[("index", "manual.typ", "Citation Caption Gate", "Probe Author")]`. `index.rst` carries a
`code-block` directive whose `:caption:` option contains `[Smith2020]_`, with the citation
definition `.. [Smith2020] Smith et al. *A Paper*. 2020.` in the same document.

### `-b typst` — clean success, zero warnings

**Command:** `uv run python -m sphinx -b typst tests/fixtures/citation_caption_dangling_label_gate
/tmp/citcap-typst`

**Raw output (verbatim):**

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
preparing documents... Template written to /tmp/citcap-typst/_template.typ
done
writing output... [index] done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
build succeeded.
```

Exit code: 0. Zero warnings — this defect is entirely invisible until Typst compiles the output.

**Verbatim emitted `index.typ` (the caption's citing reference renders as plain `[Smith2020]`
text, while the citation definition's back-reference marker links to an anchor that was never
attached anywhere):**

```
figure(caption: [See [Smith2020] for the reference implementation.])[
#codly(number-format: none)
```python
print("hello world")
```
]

grid(
  columns: (auto, 1fr),
  column-gutter: 6pt,
  row-gutter: 9pt,
[#{text("[") + link(<index:id1>, text("Smith2020")) + text("]")} <index:smith2020>], {par({text("Smith et al. ")
emph({text("A Paper")})
text(". 2020.")})

},
)
```

The caption's `[Smith2020]` is plain text (no `link(...)`) — `visit_caption`'s `SkipNode`
(`translator.py:2670-2671`) prevented `visit_reference` from ever running on the citing node, so
no `<index:id1>` anchor was attached. But `link(<index:id1>, ...)` was still emitted in the
citation-definition grid row, because `_find_citing_reference`'s `document.findall(nodes.reference)`
scan finds the citing node structurally regardless of whether the live walker ever reached it.

### `-b typstpdf` — the fatal

**Command:** `uv run python -m sphinx -b typstpdf tests/fixtures/citation_caption_dangling_label_gate
/tmp/citcap-pdf`

**Raw output (verbatim):**

```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typstpdf]: 更新された 1 件のソースファイル
環境データを更新中[新しい設定] 1 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to /tmp/citcap-pdf/_template.typ
done
writing output... [index] done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
Compiling 1 master document(s) to PDF...
Typst compilation failed at /tmp/citcap-pdf/manual.typ: TypstError: label `<index:id1>` does not exist in the document
ERROR: Failed to compile /tmp/citcap-pdf/manual.typ: Typst compilation failed: TypstError: label `<index:id1>` does not exist in the document
Location: /tmp/citcap-pdf/manual.typ
Details: label `<index:id1>` does not exist in the document

...

Traceback
=========

      File "typsphinx/builder.py", line 1490, in finish
        raise ExtensionError(
            f"typstpdf: {len(failures)} master document(s) failed: {summary}"
        )
    sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation
    failed: TypstError: label `<index:id1>` does not exist in the document
    Location: /tmp/citcap-pdf/manual.typ
    Details: label `<index:id1>` does not exist in the document
```

Exit code: 2 (non-zero). `does not exist in the document` — the exact fatal PROJECT.md predicts
for this defect class.

**Conclusion:** the `-b typst` half exiting 0 with zero warnings is the reason this defect is
invisible until the Typst compile — the two-traversal-mechanism disagreement (walker vs.
`findall`) produces no Sphinx-level diagnostic at all.

<!-- planner-discipline-allow: does not exist in the document -->

---

## D-04 — enumerated impossibility argument (open question #1)

Not a transcript-of-a-failure section: an argument, per the Phase 40.1 D-01 precedent.

`visit_pending_xref`/`depart_pending_xref` (`typsphinx/translator.py:4262-4303`) is a best-effort
fallback for a `pending_xref` node that survives all the way to the writer. Sphinx 9.1.0's
`ReferencesResolver` post-transform
(`.venv/lib/python3.13/site-packages/sphinx/transforms/post_transforms/__init__.py:62-93`, the
exact installed version this worktree runs) makes that essentially impossible in a normal build:

```python
class SphinxPostTransform(SphinxTransform):
    builders: tuple[str, ...] = ()
    formats: tuple[str, ...] = ()

    def apply(self, **kwargs: Any) -> None:
        if self.is_supported():
            self.run(**kwargs)

    def is_supported(self) -> bool:
        if self.builders and self.env._builder_cls.name not in self.builders:
            return False
        return not self.formats or self.env._builder_cls.format in self.formats


class ReferencesResolver(SphinxPostTransform):
    """Resolves cross-references on doctrees."""

    default_priority: ClassVar[int] = 10

    def run(self, **kwargs: Any) -> None:
        for node in self.document.findall(addnodes.pending_xref):
            ...
            new_node = self._resolve_pending_xref(node, contnode)
            if new_node:
                new_nodes: list[Node] = [new_node]
            else:
                new_nodes = [contnode]
                ...
            node.replace_self(new_nodes)
```

`SphinxPostTransform.builders`/`.formats` are EMPTY tuples on the base class, and
`ReferencesResolver` never overrides them, so `is_supported()` is unconditionally `True` for
every builder — including `typst` and `typstpdf`. `run()` then iterates every `pending_xref` node
in the document and calls `node.replace_self(new_nodes)` UNCONDITIONALLY: `new_nodes` falls back
to `contnode` (a deep copy of the node's own first child) even when `_resolve_pending_xref`
returns `None` (resolution failed completely). **No `pending_xref` node can survive to reach the
writer through this transform**, for any resolution outcome.

**Four plausible source shapes, per research's own reproduction this session** (an unresolvable
`:ref:`, an unresolvable `:doc:`, an unresolvable `:any:`, and an unknown role), with the verbatim
transcript `48-RESEARCH.md` recorded:

```
$ sphinx-build -b typst source build
...
WARNING: undefined label: 'nonexistent-label-xyz' [ref.ref]
WARNING: unknown document: 'nonexistent-doc-xyz' [ref.doc]
WARNING: 'any' 参照先が見つかりません: nonexistent-any-xyz [ref.any]
WARNING: unknown node type: <problematic ids="id2" ...>:unknownrole:`nonexistent-custom-xyz`</problematic>
build succeeded, 5 warnings.
```

Emitted `.typ` for all four shapes: plain text (`:ref:`, `:doc:`), `raw("...")`-wrapped text
(`:any:`, via its `literal` contnode), or the unrelated `unknown node type` docutils `problematic`
fallback (unknown role) — NONE matches `visit_pending_xref`'s distinctive `#link(<label>)[...]`
fallback pattern. Each of the four shapes produces a Sphinx WARNING and a plain-text or
`raw()`-wrapped output, never a surviving `pending_xref`.

**Conclusion, stated explicitly:** no `pending_xref` node survives to the writer through the
normal pipeline. The RED for D-04's site is therefore **unconstructible**, not merely
un-reproduced — the topology of `ReferencesResolver.run()` makes it structurally impossible for
any of the four measured shapes to reach `visit_pending_xref`. Per D-04, the site is still brought
under the guard as defence in depth regardless of this conclusion. Research assumption A2 is
recorded here verbatim as the argument's own stated limit: *"`pending_xref` is unreachable from
ANY Sphinx extension interaction, not just the four shapes tested this session... a third-party
extension emitting its own unresolved `pending_xref` after `ReferencesResolver` runs was not
tested."* That limit stands — this argument covers the normal pipeline, not every conceivable
extension interaction.

---

## Baseline 3 — the label-collision fixture's pre-fix behaviour

**Fixture:** `tests/fixtures/xref_label_collision_guard_gate/` — single well-formed entry
`[("index", "manual.typ", "Collision Gate", "Probe Author")]`. `index.rst` toctrees `a_u2f_b`
ONLY and carries `:ref:`nested-target``, which Sphinx resolves to `a/b.rst`'s explicit
`.. _nested-target:` label (the ONLY document defining that label as a Sphinx `std` domain label
— `a_u2f_b.rst`'s "Nested Target" section has a matching docutils auto id but no explicit target,
so it never registers as a `:ref:`-resolvable label itself). `a/b.rst` is marked `:orphan:` and is
in no toctree.

Not a fatal: this fixture's pre-fix behaviour is the EXISTING correct degrade (the reference's
real target, `a/b`, is outside `master_included_docnames`).

### `-b typstpdf`

**Command:** `uv run python -m sphinx -b typstpdf tests/fixtures/xref_label_collision_guard_gate
/tmp/collision-pdf`

**Raw output (verbatim, `-b typst` run shown; `-b typstpdf` behaves identically except it also
compiles to PDF):**

```
Sphinx v9.1.0 を実行中
翻訳カタログをロードしています [en]... 完了
出力先ディレクトリを作成しています... 完了
ビルド中 [mo]: 更新された 0 件のpoファイル
出力中...
ビルド中 [typst]: 更新された 3 件のソースファイル
環境データを更新中[新しい設定] 3 件追加, 0 件更新, 0 件削除
ソースを読み込み中...[ 33%] a/b
ソースを読み込み中...[ 67%] a_u2f_b
ソースを読み込み中...[100%] index

更新されたファイルを探しています... 見つかりませんでした
環境データを保存中... 完了
整合性をチェック中... 完了
preparing documents... Template written to /tmp/collision-typst/_template.typ
done
writing output... [a/b] done
writing output... [a_u2f_b] done
writing output... [index]WARNING: cross-reference to non-included document 'a/b' rendered as plain text (typstpdf includes only toctree-reachable documents): Alpha Nested Section
 done
typst: wrote 1 wrapper file(s) -- compile these: manual.typ
build succeeded, 1 warning.
```

Exit code: 0, clean. Expected: a clean exit with the build-time degrade warning naming `a/b`,
because `a/b` is outside the union.

**Emitted `index.typ` reference line — plain text, no label link:**

```
par({text("See ")

text("Alpha Nested Section")
text(" for the nested section.")})
```

**Collision measured to really exist in the emitted bytes:**

```
$ grep -c '<a_u2f_b:nested-target>' /tmp/collision-typst/a_u2f_b.typ /tmp/collision-typst/a/b.typ
/tmp/collision-typst/a_u2f_b.typ:1
/tmp/collision-typst/a/b.typ:1
```

Both `a_u2f_b.typ` (the DECOY, whose auto section id `nested-target`, namespaced with docname
`a_u2f_b`, sanitizes to `a_u2f_b:nested-target`) and `a/b.typ` (the ABSENT partner, whose explicit
label `nested-target`, namespaced with docname `a/b`, sanitizes via `_sanitize_label`'s `/` →
`_u2f_` transform to the SAME string `a_u2f_b:nested-target`) carry the identical label token.

**What changes post-fix (stated, not yet implemented):** the guard's `query(<a_u2f_b:nested-target>)`
will find the DECOY's identically-spelled label — present in the compiled master via `index`'s
toctree — and therefore link, so a reference whose real target (`a/b`) is absent will render as a
working link to the WRONG section. This is the one new false-negative class this phase
introduces, measured here rather than argued: the guard asks "does a label with this spelling
exist in this compile," not "does the document I meant exist."

<!-- planner-discipline-allow: link(<ghost_child: -->

---

## Summary

| Failure mode | Pre-fix outcome | Post-fix (this plan's expectation, derived in 48-EXPECTED-STRUCTURE.md) |
|---|---|---|
| 1 — per-master divergence (SC#1) | `bravo_master.typ` compile FATALS (`does not exist in the document`); `alpha.pdf` compiles fine | Both masters compile; bravo's guard finds no label and degrades, alpha's finds one and links |
| 2 — citation-in-caption (D-05) | `-b typst` clean, `-b typstpdf` FATALS (`does not exist in the document`) | Both builders succeed; the caption citing site degrades gracefully |
| D-04 — `pending_xref` | Unconstructible RED (site unreachable via normal pipeline) | Guarded defensively regardless (defence in depth) |
| Baseline 3 — label collision | Correctly degrades today (target outside union) | Post-fix: an ACCEPTED false-negative — links to the decoy instead of degrading |
