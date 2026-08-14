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

---

## Baseline 4 — G-48-4, the pre-fix dead-link population in the built documentation PDF (plan 48-05)

**Captured:** 2026-08-14, against this plan's own provisioned worktree (`uv sync --extra dev
--extra docs` with `VIRTUAL_ENV`/`UV_PROJECT_ENVIRONMENT` unset — neither was set in this shell to
begin with, confirmed by `printenv VIRTUAL_ENV`/`printenv UV_PROJECT_ENVIRONMENT` both exiting 1
before `uv sync` ran). Isolation independently confirmed the same way prior plans in this phase
recorded it:

```
$ uv run python -c "import typsphinx, pathlib; print(pathlib.Path(typsphinx.__file__).resolve())"
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a09e1d2e4cf4b01c4/typsphinx/__init__.py
```

`git status --porcelain typsphinx/ tests/` printed nothing before, during, and after this task —
no emitter change exists anywhere in this section, per binding constraint #6.

### Build invocation — load-bearing, plan 48-07 re-runs the SAME one

**`uv run tox -e docs-pdf` was used** (the primary invocation named by the plan; `tox` ran
successfully in this worktree so the `sphinx-build` fallback was never needed). This is
`sphinx-build -b typstpdf source _build/pdf` run from `docs/`, per `tox.ini`
`[testenv:docs-pdf]`.

**Exit code:** 0 (`tox` reported `docs-pdf: OK (4.27=setup[0.14]+cmd[4.12] seconds)` /
`congratulations :)`). **Build tail (verbatim):**

```
typst: wrote 1 wrapper file(s) -- compile these: typsphinx.typ
Copying template assets...
Compiling 1 master document(s) to PDF...
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a09e1d2e4cf4b01c4/docs/_build/pdf/typsphinx.pdf
build succeeded, 5 warnings.
  docs-pdf: OK (4.27=setup[0.14]+cmd[4.12] seconds)
  congratulations :) (4.31 seconds)
```

Same "build succeeded, 5 warnings" outcome the UAT's own gap entry recorded (`48-UAT.md`
`measured_scope`), confirming this re-measurement started from the same baseline.

**Built PDF byte size:** 2,467,467 bytes (`stat -c '%s' docs/_build/pdf/typsphinx.pdf`).

### Enumeration snippet (verbatim, run via `uv run python <script>`)

```python
"""Task 1 enumeration snippet -- pasted verbatim into 48-RED-EVIDENCE.md.

Walks every /Link annotation in the built docs/_build/pdf/typsphinx.pdf,
buckets into three counters, filters the URI-action bucket to targets ending
in the typstpdf builder's out_suffix (".pdf"), and resolves each distinct
target the way `_resolve_xref_docname` does: join the citing document's
output-URI directory onto the target path, posixpath.normpath it, strip the
suffix -- then check membership in the documentation project's found_docs.
"""

import io
import posixpath
import re
from collections import Counter
from pathlib import Path

import pypdf

PDF_PATH = Path("docs/_build/pdf/typsphinx.pdf")
BUILD_DIR = Path("docs/_build/pdf")
OUT_SUFFIX = ".pdf"  # TypstPDFBuilder.out_suffix (typsphinx/builder.py:1245)

pdf_bytes = PDF_PATH.read_bytes()
reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))

dest_count = 0
uri_count = 0
other_count = 0
uri_targets: Counter[str] = Counter()

for page in reader.pages:
    annots = page.get("/Annots") or []
    for annot in annots:
        obj = annot.get_object()
        if obj.get("/Subtype") != "/Link":
            continue
        if obj.get("/Dest") is not None:
            dest_count += 1
            continue
        action = obj.get("/A")
        if action is not None:
            action_obj = action.get_object()
            if action_obj.get("/S") == "/URI":
                uri_count += 1
                uri_targets[str(action_obj.get("/URI"))] += 1
                continue
        other_count += 1

total = dest_count + uri_count + other_count
print(f"internal /Dest: {dest_count}   URI actions: {uri_count}   "
      f"other: {other_count}   ({total} total)")

# Filter to URI targets ending in the builder's out_suffix.
suffix_targets = {u: c for u, c in uri_targets.items() if u.endswith(OUT_SUFFIX)}
suffix_total = sum(suffix_targets.values())
print(f"\nURI actions ending in '{OUT_SUFFIX}': {suffix_total} across "
      f"{len(suffix_targets)} distinct targets\n")
print(f"{'target':<45} count")
for target, count in sorted(suffix_targets.items()):
    print(f"{target:<45} {count}")

# -- Resolve each distinct target the way `_resolve_xref_docname` does. --
# found_docs: every content .typ file this build wrote, minus the shared
# wrapper (typsphinx.typ) and the shared template (_template.typ).
found_docs = set()
for typ_file in BUILD_DIR.rglob("*.typ"):
    rel = typ_file.relative_to(BUILD_DIR).as_posix()
    if rel in ("typsphinx.typ", "_template.typ"):
        continue
    found_docs.add(rel[: -len(".typ")])

print(f"\nfound_docs ({len(found_docs)}): {sorted(found_docs)}")


def get_target_uri(docname: str) -> str:
    """Mirror TypstPDFBuilder.get_target_uri: docname + out_suffix."""
    return docname + OUT_SUFFIX


def resolve(citing_docname: str, path_part: str) -> str:
    """Mirror `_resolve_xref_docname`'s inversion exactly."""
    current_uri = get_target_uri(citing_docname)
    base_dir = posixpath.dirname(current_uri)
    target_uri = posixpath.normpath(posixpath.join(base_dir, path_part))
    return target_uri[: -len(OUT_SUFFIX)]


# For each distinct target string, find which content .typ file(s) actually
# emit a `link("<target>", ` call citing it, so the resolution join uses the
# REAL citing docname's directory -- not an assumed one.
resolved_by_target: dict[str, set[str]] = {}
citations: dict[str, set[str]] = {}

for target in suffix_targets:
    pattern = re.compile(r'link\("' + re.escape(target) + r'",')
    resolved_docnames: set[str] = set()
    citing_docnames: set[str] = set()
    for typ_file in BUILD_DIR.rglob("*.typ"):
        rel = typ_file.relative_to(BUILD_DIR).as_posix()
        if rel in ("typsphinx.typ", "_template.typ"):
            continue
        text = typ_file.read_text(encoding="utf-8")
        if pattern.search(text):
            citing_docname = rel[: -len(".typ")]
            citing_docnames.add(citing_docname)
            resolved_docnames.add(resolve(citing_docname, target))
    resolved_by_target[target] = resolved_docnames
    citations[target] = citing_docnames

print("\ntarget -> citing docname(s) -> resolved docname(s) -> in found_docs?")
sub_a = []  # resolves onto a real document
sub_b = []  # does not
for target in sorted(suffix_targets):
    resolved = resolved_by_target[target]
    citing = citations[target]
    in_found = {r: (r in found_docs) for r in resolved}
    print(f"  {target!r}: citing={sorted(citing)!r} resolved={sorted(resolved)!r} "
          f"in_found_docs={in_found}")
    if resolved and all(in_found.values()):
        sub_a.append(target)
    else:
        sub_b.append(target)

print(f"\nSub-population A (resolves onto a real docname): {len(sub_a)} distinct "
      f"targets, {sum(suffix_targets[t] for t in sub_a)} annotations")
for t in sorted(sub_a):
    print(f"  {t}  x{suffix_targets[t]}")

print(f"\nSub-population B (does not resolve onto a real docname): {len(sub_b)} "
      f"distinct targets, {sum(suffix_targets[t] for t in sub_b)} annotations")
for t in sorted(sub_b):
    print(f"  {t}  x{suffix_targets[t]}")
```

### Enumeration output (verbatim)

```
internal /Dest: 37   URI actions: 465   other: 0   (502 total)

URI actions ending in '.pdf': 40 across 20 distinct targets

target                                        count
../examples/advanced.pdf                      3
../examples/basic.pdf                         1
../genindex.pdf                               1
../py-modindex.pdf                            1
../user_guide/configuration.pdf               4
../user_guide/templates.pdf                   3
advanced.pdf                                  2
basic.pdf                                     1
builders.pdf                                  2
configuration.pdf                             5
contributing.pdf                              1
examples/index.pdf                            1
genindex.pdf                                  1
py-modindex.pdf                               1
quickstart.pdf                                1
search.pdf                                    1
templates.pdf                                 7
user_guide/builders.pdf                       1
user_guide/configuration.pdf                  2
user_guide/templates.pdf                      1

found_docs (13): ['api/index', 'changelog', 'contributing', 'examples/advanced', 'examples/basic', 'examples/index', 'index', 'installation', 'quickstart', 'user_guide/builders', 'user_guide/configuration', 'user_guide/index', 'user_guide/templates']

target -> citing docname(s) -> resolved docname(s) -> in found_docs?
  '../examples/advanced.pdf': citing=['user_guide/configuration', 'user_guide/templates'] resolved=['examples/advanced'] in_found_docs={'examples/advanced': True}
  '../examples/basic.pdf': citing=['user_guide/builders'] resolved=['examples/basic'] in_found_docs={'examples/basic': True}
  '../genindex.pdf': citing=['api/index'] resolved=['genindex'] in_found_docs={'genindex': False}
  '../py-modindex.pdf': citing=['api/index'] resolved=['py-modindex'] in_found_docs={'py-modindex': False}
  '../user_guide/configuration.pdf': citing=['api/index', 'examples/advanced', 'examples/basic'] resolved=['user_guide/configuration'] in_found_docs={'user_guide/configuration': True}
  '../user_guide/templates.pdf': citing=['examples/advanced', 'examples/basic'] resolved=['user_guide/templates'] in_found_docs={'user_guide/templates': True}
  'advanced.pdf': citing=['examples/basic', 'examples/index'] resolved=['examples/advanced'] in_found_docs={'examples/advanced': True}
  'basic.pdf': citing=['examples/index'] resolved=['examples/basic'] in_found_docs={'examples/basic': True}
  'builders.pdf': citing=['user_guide/configuration', 'user_guide/index'] resolved=['user_guide/builders'] in_found_docs={'user_guide/builders': True}
  'configuration.pdf': citing=['user_guide/builders', 'user_guide/index', 'user_guide/templates'] resolved=['user_guide/configuration'] in_found_docs={'user_guide/configuration': True}
  'contributing.pdf': citing=['changelog'] resolved=['contributing'] in_found_docs={'contributing': True}
  'examples/index.pdf': citing=['quickstart'] resolved=['examples/index'] in_found_docs={'examples/index': True}
  'genindex.pdf': citing=['index'] resolved=['genindex'] in_found_docs={'genindex': False}
  'py-modindex.pdf': citing=['index'] resolved=['py-modindex'] in_found_docs={'py-modindex': False}
  'quickstart.pdf': citing=['installation'] resolved=['quickstart'] in_found_docs={'quickstart': True}
  'search.pdf': citing=['index'] resolved=['search'] in_found_docs={'search': False}
  'templates.pdf': citing=['user_guide/builders', 'user_guide/configuration', 'user_guide/index'] resolved=['user_guide/templates'] in_found_docs={'user_guide/templates': True}
  'user_guide/builders.pdf': citing=['quickstart'] resolved=['user_guide/builders'] in_found_docs={'user_guide/builders': True}
  'user_guide/configuration.pdf': citing=['quickstart'] resolved=['user_guide/configuration'] in_found_docs={'user_guide/configuration': True}
  'user_guide/templates.pdf': citing=['quickstart'] resolved=['user_guide/templates'] in_found_docs={'user_guide/templates': True}

Sub-population A (resolves onto a real docname): 15 distinct targets, 35 annotations
  ../examples/advanced.pdf  x3
  ../examples/basic.pdf  x1
  ../user_guide/configuration.pdf  x4
  ../user_guide/templates.pdf  x3
  advanced.pdf  x2
  basic.pdf  x1
  builders.pdf  x2
  configuration.pdf  x5
  contributing.pdf  x1
  examples/index.pdf  x1
  quickstart.pdf  x1
  templates.pdf  x7
  user_guide/builders.pdf  x1
  user_guide/configuration.pdf  x2
  user_guide/templates.pdf  x1

Sub-population B (does not resolve onto a real docname): 5 distinct targets, 5 annotations
  ../genindex.pdf  x1
  ../py-modindex.pdf  x1
  genindex.pdf  x1
  py-modindex.pdf  x1
  search.pdf  x1
```

### Sub-population split, stated explicitly

**Resolution rule** (mirrors `_resolve_xref_docname`, `typsphinx/translator.py:4786-4829`): for
each distinct URI-action target ending in the builder's `out_suffix` (`.pdf`), find the content
`.typ` file(s) that actually emit `link("<target>", ` for it (the REAL citing docname, not an
assumed one), compute `current_uri = citing_docname + ".pdf"`, `base_dir =
posixpath.dirname(current_uri)`, `target_uri = posixpath.normpath(posixpath.join(base_dir,
path_part))`, then strip the suffix to get the resolved docname. A target counts as
**sub-population A** when every citing occurrence resolves onto a docname present in
`found_docs`; **sub-population B** otherwise.

- **Sub-population A** (resolves onto a real document): **15 distinct targets, 35 annotations**.
- **Sub-population B** (does not resolve — Sphinx's generated `genindex` / `py-modindex` /
  `search` pages, which the Typst output never produces): **5 distinct targets, 5 annotations** —
  `genindex.pdf` (cited from `index`), `py-modindex.pdf` (cited from `index`), `search.pdf` (cited
  from `index`), `../genindex.pdf` (cited from `api/index`), `../py-modindex.pdf` (cited from
  `api/index`).

**Re-derivation against the UAT's own figure:** `48-UAT.md`'s gap entry `G-48-4` states sub-population
B as **"4 of the 40" in its `truth`/`reason` prose, but its own `measured_scope` field already
corrected this to 5** ("5 of the 40 have no PDF equivalent at all... (Corrected during gap
planning — this entry first said 4, miscounting the `../` forms against the enumeration above,
which lists all five at 1 occurrence each)"). This re-measurement's own independent count —
**5** — agrees with the UAT's own corrected `measured_scope` figure, not its stale outer
`truth`/`reason` wording. No new divergence is introduced here; the UAT document already carries
its own correction, and this baseline confirms that corrected number (5) by direct re-enumeration
on this worktree rather than by copying it forward.

### Quickstart "What's Next?" page — anchored to the originally reported symptom

`48-UAT.md`'s `measured_scope` quotes four `/A` URI actions on PDF page 6 (the Quickstart "What's
Next?" section the owner reported clicking): `user_guide/configuration.pdf`,
`user_guide/builders.pdf`, `user_guide/templates.pdf`, `examples/index.pdf`. Re-run against this
worktree's rebuilt PDF (verbatim page-scan output, restricted to those four target strings):

```
Page 5: ['user_guide/configuration.pdf']
Page 6: ['examples/index.pdf', 'user_guide/builders.pdf', 'user_guide/configuration.pdf', 'user_guide/templates.pdf']
```

Page 6 carries all four target strings the owner's report and the UAT's transcript name,
confirming this baseline is anchored to the reported symptom and not only to the aggregate count
above. (Page 5 also carries one `user_guide/configuration.pdf` annotation from a different citing
sentence — outside the scope of the reported symptom, not a discrepancy.)

**Conclusion:** the pre-fix dead-link population is 40 annotations across 20 distinct `.pdf`-suffixed
URI-action targets, split 35/5 between sub-population A (real documents, unconditionally closed by
this gap's fix) and sub-population B (the 5 Sphinx-generated-page references with no Typst
counterpart, whose policy is decided at this plan's checkpoint task).
