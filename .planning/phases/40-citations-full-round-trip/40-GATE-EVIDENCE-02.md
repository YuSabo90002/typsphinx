# Phase 40, Plan 02 — GATE-01 Evidence (Shipped-Sample RED)

**Recorded against commit:** `4f79c6f` (`docs(40-02): correct ROADMAP Phase 40 SC#3 to D-08's
same-document scope`), built directly on `1f643f0` (`fix(40-02): restore charged-ieee citation
syntax verbatim`), itself built on `ccb37b2` (`docs(40): create phase plan`), the phase-start
commit. `typsphinx/` is byte-identical across `ccb37b2`, `1f643f0`, and `4f79c6f`:

```
$ git diff --stat -- typsphinx/ tests/ ccb37b2e7099386462968177cf500a196db67c07..HEAD
(empty -- no output)
```

so all three commits equally qualify as "the untouched translator" this evidence is recorded
against. This plan touches only `examples/` and `.planning/`. No file under `typsphinx/` or
`tests/` is modified.

---

## 1. The restoration proof (D-11/D-12)

```
$ git hash-object examples/charged-ieee/approach1/source/index.rst
82831eb092b9f52cba8b1247b95f7e148f499bb2

$ git hash-object examples/charged-ieee/approach2/source/index.rst
82831eb092b9f52cba8b1247b95f7e148f499bb2

$ diff examples/charged-ieee/approach1/source/index.rst examples/charged-ieee/approach2/source/index.rst
(empty -- diff exits 0, no output)

$ git diff --stat ccb37b2e7099386462968177cf500a196db67c07..HEAD -- examples/
 examples/charged-ieee/approach1/source/index.rst | 15 ++++++++-------
 examples/charged-ieee/approach2/source/index.rst | 15 ++++++++-------
 2 files changed, 16 insertions(+), 14 deletions(-)
```

Both files hash to the pre-removal blob `82831eb092b9f52cba8b1247b95f7e148f499bb2`, `diff` between
them produces no output, and exactly two files under `examples/` are touched by this plan's
commits. This is what D-11's verbatim-restore claim and D-12's byte-identity claim reduce to: the
restore was a literal write of the pre-removal blob into both paths (`git cat-file -p <blob> >
<path>`), not a hand-edit or reverse-patch, so no VGGNet/ResNet/EfficientNet entries were added
even though those papers are already named in the sample's prose (D-11 rejected exactly that
expansion). Both top-of-file "no citations" RST comment blocks (the five-line block each removal
commit added, worded slightly differently between `approach1` and `approach2`) disappeared as a
direct consequence of restoring the pre-removal blob -- neither file's restoration required a
separate hand-edit to delete a comment block, because the blob never contained either one.

---

## 2. `tests/test_examples_charged_ieee_gate.py` — verbatim RED

Command: `uv run pytest tests/test_examples_charged_ieee_gate.py -v`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a71fff256315460ee
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 2 items

tests/test_examples_charged_ieee_gate.py::TestChargedIeeeExamplesGate::test_approach1_package_alone_sample_builds_and_compiles FAILED [ 50%]
tests/test_examples_charged_ieee_gate.py::TestChargedIeeeExamplesGate::test_approach2_custom_template_sample_actually_uses_package FAILED [100%]

=================================== FAILURES ===================================
_ TestChargedIeeeExamplesGate.test_approach1_package_alone_sample_builds_and_compiles _

self = <test_examples_charged_ieee_gate.TestChargedIeeeExamplesGate object at 0x7bd032922c10>
tmp_path = PosixPath('/tmp/pytest-of-yuta/pytest-542/test_approach1_package_alone_s0')

    def test_approach1_package_alone_sample_builds_and_compiles(self, tmp_path):
        build_dir = tmp_path / "approach1_build"
        result = _run_sphinx_build(APPROACH1_DIR, APPROACH1_DIR / "source", build_dir)
>       assert result.returncode == 0, (
            f"sphinx-build failed for examples/charged-ieee/approach1:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
E       AssertionError: sphinx-build failed for examples/charged-ieee/approach1:
E         stdout: Sphinx v9.1.0 を実行中
E         翻訳カタログをロードしています [en]... 完了
E         出力先ディレクトリを作成しています... 完了
E         ビルド中 [mo]: 更新された 0 件のpoファイル
E         出力中...
E         ビルド中 [typstpdf]: 更新された 1 件のソースファイル
E         環境データを更新中[新しい設定] 1 件追加, 0 件更新, 0 件削除
E         ソースを読み込み中...[100%] index
E
E         更新されたファイルを探しています... 見つかりませんでした
E         環境データを保存中... 完了
E         整合性をチェック中... 完了
E         preparing documents... done
E         writing output... [index] done
E         Compiling 1 master document(s) to PDF...
E
E         stderr: WARNING: unknown node type: <citation backrefs="id1" docname="index" ids="krizhevsky2012" names="krizhevsky2012"><label support_smartquotes="0">Krizhevsky2012</label><paragraph>Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012).
E         ImageNet classification with deep convolutional neural networks.
E         <emphasis>Advances in neural information processing systems</emphasis>, 25.</paragraph></citation>
E         WARNING: unknown node type: <label support_smartquotes="0">Krizhevsky2012</label>
E         Typst compilation failed at /tmp/pytest-of-yuta/pytest-542/test_approach1_package_alone_s0/approach1_build/paper.typ: TypstError: expected semicolon or line break
E         ERROR: Failed to compile /tmp/pytest-of-yuta/pytest-542/test_approach1_package_alone_s0/approach1_build/paper.typ: Typst compilation failed: TypstError: expected semicolon or line break
E         Location: /tmp/pytest-of-yuta/pytest-542/test_approach1_package_alone_s0/approach1_build/paper.typ
E         Details: expected semicolon or line break
E
E         Extension error!
E
E         sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: expected semicolon or line break
E
E       assert 2 == 0
E        +  where 2 = CompletedProcess(...).returncode

tests/test_examples_charged_ieee_gate.py:158: AssertionError
_ TestChargedIeeeExamplesGate.test_approach2_custom_template_sample_actually_uses_package _

self = <test_examples_charged_ieee_gate.TestChargedIeeeExamplesGate object at 0x7bd032922fd0>
tmp_path = PosixPath('/tmp/pytest-of-yuta/pytest-542/test_approach2_custom_template0')

    def test_approach2_custom_template_sample_actually_uses_package(self, tmp_path):
        build_dir = tmp_path / "approach2_build"
        result = _run_sphinx_build(APPROACH2_DIR, APPROACH2_DIR / "source", build_dir)
>       assert result.returncode == 0, (
            f"sphinx-build failed for examples/charged-ieee/approach2:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
E       AssertionError: sphinx-build failed for examples/charged-ieee/approach2:
E         stdout: Sphinx v9.1.0 を実行中
E         翻訳カタログをロードしています [en]... 完了
E         出力先ディレクトリを作成しています... 完了
E         ビルド中 [mo]: 更新された 0 件のpoファイル
E         出力中...
E         ビルド中 [typstpdf]: 更新された 1 件のソースファイル
E         環境データを更新中[新しい設定] 1 件追加, 0 件更新, 0 件削除
E         ソースを読み込み中...[100%] index
E
E         更新されたファイルを探しています... 見つかりませんでした
E         環境データを保存中... 完了
E         整合性をチェック中... 完了
E         preparing documents... Template written to /tmp/pytest-of-yuta/pytest-542/test_approach2_custom_template0/approach2_build/_template.typ
E         done
E         writing output... [index] done
E         Copying template assets...
E         Compiling 1 master document(s) to PDF...
E
E         stderr: WARNING: unknown node type: <citation backrefs="id1" docname="index" ids="krizhevsky2012" names="krizhevsky2012"><label support_smartquotes="0">Krizhevsky2012</label><paragraph>Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012).
E         ImageNet classification with deep convolutional neural networks.
E         <emphasis>Advances in neural information processing systems</emphasis>, 25.</paragraph></citation>
E         WARNING: unknown node type: <label support_smartquotes="0">Krizhevsky2012</label>
E         Typst compilation failed at /tmp/pytest-of-yuta/pytest-542/test_approach2_custom_template0/approach2_build/paper.typ: TypstError: expected semicolon or line break
E         ERROR: Failed to compile /tmp/pytest-of-yuta/pytest-542/test_approach2_custom_template0/approach2_build/paper.typ: Typst compilation failed: TypstError: expected semicolon or line break
E         Location: /tmp/pytest-of-yuta/pytest-542/test_approach2_custom_template0/approach2_build/paper.typ
E         Details: expected semicolon or line break
E
E         Extension error!
E
E         sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed: index: Typst compilation failed: TypstError: expected semicolon or line break
E
E       assert 2 == 0
E        +  where 2 = CompletedProcess(...).returncode

tests/test_examples_charged_ieee_gate.py:206: AssertionError
=========================== short test summary info ============================
FAILED tests/test_examples_charged_ieee_gate.py::TestChargedIeeeExamplesGate::test_approach1_package_alone_sample_builds_and_compiles - AssertionError: sphinx-build failed for examples/charged-ieee/approach1: ...
FAILED tests/test_examples_charged_ieee_gate.py::TestChargedIeeeExamplesGate::test_approach2_custom_template_sample_actually_uses_package - AssertionError: sphinx-build failed for examples/charged-ieee/approach2: ...
============================== 2 failed in 1.05s ===============================
```

**Failing-assertion → what it checks:**

Each test method's FIRST assertion is `assert result.returncode == 0` (line 158 for `approach1`,
line 206 for `approach2`), immediately after invoking `sphinx-build -b typstpdf`. Because both
builds exit non-zero (`returncode == 2`), pytest raises at that first assertion and neither test
function reaches any assertion after it -- the zero-warning helper (`_assert_no_warnings`), the
`paper.typ`/`paper.pdf` existence and non-empty-PDF checks, the package-import/authors-array
content assertions, and (for `approach2`) the shared-template provenance assertions (positive
`@preview/charged-ieee:0.1.4` import, negative default-header-marker absence, by-name master
import) are all downstream of the exit-code assertion and never execute on this RED run. The
failure text itself, captured in `stderr` inside the assertion message, names a non-zero
`sphinx-build` exit (`returncode=2`) whose cause is a build warning followed by a Typst compile
fatal -- not a Python exception and not a missing-file error:

- `WARNING: unknown node type: <citation ...>` -- the translator has no `visit_citation` handler.
- `WARNING: unknown node type: <label ...>` -- the translator has no `visit_label` handler.
- `Typst compilation failed ... TypstError: expected semicolon or line break` -- the two adjacent,
  un-separated expressions the unknown-node fallback emits are invalid Typst syntax, so
  `typst.compile()` itself rejects the generated `.typ`.
- `sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed` -- `TypstPDFBuilder.finish()`
  (Phase 22.1 D-04) surfaces the compile failure as a non-zero `sphinx-build` exit rather than
  silently swallowing it, which is exactly what `assert result.returncode == 0` is designed to
  catch.

---

## 3. Verbatim unknown-node warning + compile-fatal text (from a real build)

Reproduced from `approach1`'s captured `stderr` above (identical in shape for `approach2`, only the
`tmp_path` differs):

```
WARNING: unknown node type: <citation backrefs="id1" docname="index" ids="krizhevsky2012" names="krizhevsky2012"><label support_smartquotes="0">Krizhevsky2012</label><paragraph>Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012).
ImageNet classification with deep convolutional neural networks.
<emphasis>Advances in neural information processing systems</emphasis>, 25.</paragraph></citation>
WARNING: unknown node type: <label support_smartquotes="0">Krizhevsky2012</label>
Typst compilation failed at .../approach1_build/paper.typ: TypstError: expected semicolon or line break
ERROR: Failed to compile .../approach1_build/paper.typ: Typst compilation failed: TypstError: expected semicolon or line break
```

The two unknown-node warnings this phase's Plan 03 handlers remove are the `citation` node itself
(carrying the docutils-resolved `backrefs="id1"` and `ids="krizhevsky2012"` attributes D-13's
label-routing will consume) and the nested `label` child node. The compile fatal that follows
(`TypstError: expected semicolon or line break`) is the direct consequence of the unknown-node
fallback emitting the citation's and label's contents as two adjacent expressions with no
separator between them -- exactly the defect PROJECT.md's citation-support section and
`40-RESEARCH.md` describe as the reason `translator.py` currently contains zero citation handlers.

---

## 4. Executed-versus-skipped statement

```
$ python3 -c "import typst; print(typst.__version__)"
0.15.0
```

`typst-py` (`typst==0.15.0`) is installed in this worktree's `.venv` (see the `uv sync --extra dev`
provisioning output), so `tests/test_examples_charged_ieee_gate.py`'s module-level
`TYPST_AVAILABLE` guard (`tests/test_examples_charged_ieee_gate.py:48-53`) evaluates `True`, and
the class-level `@pytest.mark.skipif(not TYPST_AVAILABLE, ...)` (line 132) does NOT fire. Both
`test_approach1_package_alone_sample_builds_and_compiles` and
`test_approach2_custom_template_sample_actually_uses_package` genuinely EXECUTED on this run --
the collection summary reads `collected 2 items` and the result summary reads `2 failed`, never `2
skipped` or `1 passed, 1 skipped`. A skip would have produced no build at all and would not be
evidence of anything; this run is a real subprocess invocation of `sphinx-build -b typstpdf`
against the restored shipped sample, reaching an actual Typst compile attempt and a real
`TypstError`.

---

## 5. Module re-run, never edited

```
$ git diff --stat -- tests/
(empty -- no output)
```

`tests/test_examples_charged_ieee_gate.py` is byte-identical to its state before this plan started
(and to its state at the D-12 plan, `22.2-06-PLAN.md`, that wrote it). No skip marker, no `xfail`,
and no assertion change were added to make this RED convenient to read. The same module, with the
same eleven assertions per test method, is what plan 40-04 will re-run unchanged after 40-03 lands
the `visit_citation`/`visit_label`/`visit_citation_reference` handlers -- so the RED recorded here
and the GREEN 40-04 records are directly comparable: any difference in which assertion fails (or
whether any fails at all) is attributable entirely to the translator change, not to a change in
what is being checked.

---

## 6. D-11 accepted cost, restated

The restored sample carries exactly one citation definition (`Krizhevsky2012`) and exactly one
citing reference to it, in a single document. This is D-11's accepted cost, stated at decision time
and restated here so a later reader does not mistake the sample's narrowness for an oversight in
this plan's own coverage: with one entry and one citing site, the restored sample exercises ONLY
D-03's single-back-reference shape (one citation definition, one back-reference marker). Neither
the multi-marker back-reference shape (a definition cited from more than one location, e.g. an
`(1,2)`-style marker list) nor D-05's widest-label alignment (multiple definitions of differing
label width in one run, requiring the hanging indent to align to the widest) is visible anywhere in
this shipped sample. Both of those shapes are proven instead by this phase's own purpose-built
fixture, `tests/fixtures/citation_render_gate/` (plan 40-01), which is what carries the full
eleven-scenario coverage this plan's two-file, one-citation restoration cannot.

---

## 7. Success criteria cross-check

- Both sample files hash to `82831eb092b9f52cba8b1247b95f7e148f499bb2` and `diff` between them is
  empty -- confirmed in §1.
- `uv run pytest tests/test_examples_charged_ieee_gate.py -v` is RED for a build reason, and the
  module itself is unmodified -- confirmed in §2 and §5.
- `git diff --stat -- typsphinx/ tests/` is empty for this plan's commits -- confirmed at the top
  of this file and in §5.
