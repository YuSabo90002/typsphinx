# Phase 50 Plan 01 — IMG-01 Pre-Fix RED Evidence

**Measured:** 2026-08-14, inside the worktree provisioned per `CLAUDE.md`'s
worktree-isolated-execution rules (`unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT
&& uv sync --extra dev`, every command below run via `uv run`).

Per ROADMAP binding constraint #4 (GATE-01's non-fatal amendment) and
`50-CONTEXT.md`'s D-08, "does not compile" is NOT an available RED for
IMG-01 — the defect compiles fine both before and after the fix. This
document records the D-08 embedded-image RED instead: read out of the
single compiled `master.pdf`, before any line of `typsphinx/builder.py`
changes.

## Commands run and exit codes

```
$ git rev-parse HEAD
9180620c8a3a400d46ce1f3cbb826280c4ae6d7c

$ sha256sum typsphinx/builder.py tests/test_converted_image_collision_render_gate.py
455f36415acb31440fed75b768df1617df2babd83000248a847df4501ef7ea2a  typsphinx/builder.py
6fe5691ae30f7ac57ac8ad35fa921c8aea8b46967029bfd71411fb39b5732eea  tests/test_converted_image_collision_render_gate.py

$ git diff --stat -- typsphinx/builder.py
(empty — typsphinx/builder.py is byte-unchanged at measurement time)

$ uv run pytest tests/test_converted_image_collision_render_gate.py --runxfail -v
exit code: 1

$ uv run pytest tests/test_converted_image_collision_render_gate.py --runxfail -q
exit code: 1
```

## Verbatim `--runxfail` transcript (`-v`)

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a415ab32d2aa77b0c/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a415ab32d2aa77b0c
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 3 items

tests/test_converted_image_collision_render_gate.py::TestConvertedImageCollisionRenderGate::test_typstpdf_build_succeeds_without_image_warnings PASSED [ 33%]
tests/test_converted_image_collision_render_gate.py::TestConvertedImageCollisionRenderGate::test_content_documents_emit_distinct_image_paths FAILED [ 66%]
tests/test_converted_image_collision_render_gate.py::TestConvertedImageCollisionRenderGate::test_pdf_embeds_both_distinctly_sized_images FAILED [100%]

=================================== FAILURES ===================================
_ TestConvertedImageCollisionRenderGate.test_content_documents_emit_distinct_image_paths _

self = <test_converted_image_collision_render_gate.TestConvertedImageCollisionRenderGate object at 0x71b8eb977d90>
converted_image_collision_render_gate_dir = PosixPath('/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a415ab32d2aa77b0c/tests/fixtures/converted_image_collision_render_gate')
temp_build_dir = PosixPath('/tmp/pytest-of-yuta/pytest-1087/test_content_documents_emit_di0/_build')

    @pytest.mark.xfail(strict=True, reason=_RED_REASON_STRUCTURAL)
    def test_content_documents_emit_distinct_image_paths(
        self, converted_image_collision_render_gate_dir, temp_build_dir
    ):
        """
        STRUCTURAL RED (D-08): ``real_source.typ`` must reference the
        unchanged ``images/chart.png`` key (D-01: the common, non-
        colliding-target-would-be case is unchanged -- but here a REAL
        collision exists, so the real source image keeps the plain key and
        the converted image is the one relocated), while
        ``converted_source.typ`` must reference the D-02 reserved
        namespace ``_typst_converted/images/chart.png`` instead. The two
        emitted image arguments must differ from each other.
        """
        result = _run_sphinx_build_typstpdf(
            converted_image_collision_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx build (typstpdf) failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    
        converted_typ = temp_build_dir / "converted_source.typ"
        real_typ = temp_build_dir / "real_source.typ"
        assert converted_typ.exists(), "converted_source.typ was not emitted"
        assert real_typ.exists(), "real_source.typ was not emitted"
    
        converted_text = converted_typ.read_text(encoding="utf-8")
        real_text = real_typ.read_text(encoding="utf-8")
    
        assert 'image("images/chart.png")' in real_text, (
            "Expected real_source.typ to keep the unchanged "
            f"images/chart.png key:\n{real_text}"
        )
>       assert 'image("_typst_converted/images/chart.png")' in converted_text, (
            "Expected converted_source.typ to reference the D-02 reserved "
            f"namespace after relocation:\n{converted_text}"
        )
E       AssertionError: Expected converted_source.typ to reference the D-02 reserved namespace after relocation:
E         // Essential imports for included document
E         #import "@preview/codly:1.3.0": *
E         #import "@preview/codly-languages:0.1.10": *
E         #import "@preview/mitex:0.2.7": mi, mitex
E         #import "@preview/gentle-clues:1.3.1": *
E         
E         // Initialize codly
E         #show: codly-init.with()
E         #codly(languages: codly-languages)
E         
E         #{
E         [#metadata(none) <converted_source:__tsx-doc__>]
E         [#heading(depth: 1, {text("Converted Source")}) <converted_source:converted-source>]
E         
E         par({text("This document’s figure references an SVG. A custom post-transform (registered in ")
E         raw("conf.py")
E         text(") “converts” it to an ABSOLUTE path under ")
E         raw("<doctreedir>/images/chart.png")
E         text(" – reproducing exactly what Sphinx’s real ")
E         raw("ImageConverter")
E         text("/")
E         raw("ImageDownloader")
E         text(" post-transforms do for any image that needs conversion or download.")})
E         
E         [#figure(
E           image("images/chart.png"),
E           caption: {text("A figure whose URI is rewritten to an absolute path by the fixture’s fake image converter, landing at the same basename an ordinary source image already occupies.")}
E         ) <converted_source:id1>]
E         
E         
E         }
E         
E       assert 'image("_typst_converted/images/chart.png")' in '// Essential imports for included document\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1.10": *\n#import "@preview/mitex:0.2.7": mi, mitex\n#import "@preview/gentle-clues:1.3.1": *\n\n// Initialize codly\n#show: codly-init.with()\n#codly(languages: codly-languages)\n\n#{\n[#metadata(none) <converted_source:__tsx-doc__>]\n[#heading(depth: 1, {text("Converted Source")}) <converted_source:converted-source>]\n\npar({text("This document’s figure references an SVG. A custom post-transform (registered in ")\nraw("conf.py")\ntext(") “converts” it to an ABSOLUTE path under ")\nraw("<doctreedir>/images/chart.png")\ntext(" – reproducing exactly what Sphinx’s real ")\nraw("ImageConverter")\ntext("/")\nraw("ImageDownloader")\ntext(" post-transforms do for any image that needs conversion or download.")})\n\n[#figure(\n  image("images/chart.png"),\n  caption: {text("A figure whose URI is rewritten to an absolute path by the fixture’s fake image converter, landing at the same basename an ordinary source image already occupies.")}\n) <converted_source:id1>]\n\n\n}\n'

tests/test_converted_image_collision_render_gate.py:215: AssertionError
_ TestConvertedImageCollisionRenderGate.test_pdf_embeds_both_distinctly_sized_images _

self = <test_converted_image_collision_render_gate.TestConvertedImageCollisionRenderGate object at 0x71b8eb97b820>
converted_image_collision_render_gate_dir = PosixPath('/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a415ab32d2aa77b0c/tests/fixtures/converted_image_collision_render_gate')
temp_build_dir = PosixPath('/tmp/pytest-of-yuta/pytest-1087/test_pdf_embeds_both_distinctl0/_build')

    @pytest.mark.skipif(
        not PYPDF_AVAILABLE,
        reason="pypdf is required for the embedded-image extraction assert",
    )
    @pytest.mark.xfail(strict=True, reason=_RED_REASON_EMBEDDED)
    def test_pdf_embeds_both_distinctly_sized_images(
        self, converted_image_collision_render_gate_dir, temp_build_dir
    ):
        """
        EMBEDDED-IMAGE RED (D-08/D-09): open ``master.pdf`` with
        ``pypdf.PdfReader`` and build the SET of ``image_file.image.size``
        pairs over every page and every entry of ``page.images`` (never by
        positional index -- pypdf's extraction order follows Typst's own
        PDF XObject enumeration, not doctree order). That set must equal
        ``{(40, 24), (16, 64)}`` -- both distinctly-sized pictures
        genuinely embedded. Also requires
        ``<build>/_typst_converted/images/chart.png`` to exist and
        ``<build>/images/chart.png`` to be byte-identical to the fixture's
        own ``images/chart.png`` -- proof that the REAL source image, not
        the converted stand-in, is the file that ends up at the ordinary
        location.
        """
        result = _run_sphinx_build_typstpdf(
            converted_image_collision_render_gate_dir, temp_build_dir
        )
        assert result.returncode == 0, (
            f"sphinx build (typstpdf) failed:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    
        pdf_output = temp_build_dir / "master.pdf"
        assert pdf_output.exists(), (
            "master.pdf was not produced:\n" f"stderr: {result.stderr}"
        )
    
        reader = pypdf.PdfReader(str(pdf_output))
        extracted_sizes = {
            image_file.image.size
            for page in reader.pages
            for image_file in page.images
            if image_file.image is not None
        }
    
>       assert extracted_sizes == {(40, 24), (16, 64)}, (
            "Expected both distinctly-sized pictures to be embedded in "
            f"master.pdf; observed sizes: {extracted_sizes}"
        )
E       AssertionError: Expected both distinctly-sized pictures to be embedded in master.pdf; observed sizes: {(16, 64)}
E       assert {(16, 64)} == {(16, 64), (40, 24)}
E         
E         Extra items in the right set:
E         (40, 24)
E         
E         Full diff:
E           {
E               (
E                   16,
E                   64,
E               ),
E         -     (
E         -         40,
E         -         24,
E         -     ),
E           }

tests/test_converted_image_collision_render_gate.py:269: AssertionError
=========================== short test summary info ============================
FAILED tests/test_converted_image_collision_render_gate.py::TestConvertedImageCollisionRenderGate::test_content_documents_emit_distinct_image_paths - AssertionError: Expected converted_source.typ to reference the D-02 reserved namespace after relocation:
  // Essential imports for included document
  #import "@preview/codly:1.3.0": *
  #import "@preview/codly-languages:0.1.10": *
  #import "@preview/mitex:0.2.7": mi, mitex
  #import "@preview/gentle-clues:1.3.1": *
  
  // Initialize codly
  #show: codly-init.with()
  #codly(languages: codly-languages)
  
  #{
  [#metadata(none) <converted_source:__tsx-doc__>]
  [#heading(depth: 1, {text("Converted Source")}) <converted_source:converted-source>]
  
  par({text("This document’s figure references an SVG. A custom post-transform (registered in ")
  raw("conf.py")
  text(") “converts” it to an ABSOLUTE path under ")
  raw("<doctreedir>/images/chart.png")
  text(" – reproducing exactly what Sphinx’s real ")
  raw("ImageConverter")
  text("/")
  raw("ImageDownloader")
  text(" post-transforms do for any image that needs conversion or download.")})
  
  [#figure(
    image("images/chart.png"),
    caption: {text("A figure whose URI is rewritten to an absolute path by the fixture’s fake image converter, landing at the same basename an ordinary source image already occupies.")}
  ) <converted_source:id1>]
  
  
  }
  
assert 'image("_typst_converted/images/chart.png")' in '// Essential imports for included document\n#import "@preview/codly:1.3.0": *\n#import "@preview/codly-languages:0.1....verter, landing at the same basename an ordinary source image already occupies.")}\n) <converted_source:id1>]\n\n\n}\n'
FAILED tests/test_converted_image_collision_render_gate.py::TestConvertedImageCollisionRenderGate::test_pdf_embeds_both_distinctly_sized_images - AssertionError: Expected both distinctly-sized pictures to be embedded in master.pdf; observed sizes: {(16, 64)}
assert {(16, 64)} == {(16, 64), (40, 24)}
  
  Extra items in the right set:
  (40, 24)
  Use -v to get more diff

========================= 2 failed, 1 passed in 0.99s ==========================
```

## Measurement integrity check

Both failures are `AssertionError`s raised from the test module's own
assertions after a **successful** `sphinx-build -b typstpdf` subprocess run
(`result.returncode == 0` passed in both tests, unasserted-on above because
it never fired) and a **successful** `pypdf.PdfReader` open (the reader
constructed and both `page.images` iterations completed without raising).
Neither failure is:

- an `ImportError` — `typst` and `pypdf` both imported cleanly
  (`TYPST_AVAILABLE`/`PYPDF_AVAILABLE` were both `True`; neither
  `@pytest.mark.skipif` fired),
- a fixture-resolution error — `converted_image_collision_render_gate_dir`
  and `temp_build_dir` both resolved and the fixture project built,
- a non-zero `sphinx-build` return code — both tests' internal
  `result.returncode == 0` assertion passed silently (never appears in the
  failure output above, confirming it did not fire), nor
- a `pypdf` read error — `pypdf.PdfReader(str(pdf_output))` succeeded and
  `page.images` enumerated without exception; the failure is purely in the
  size-SET comparison this test asserts.

This is the expected IMG-01 symptom, not a broken measurement: the
structural test's own control test
(`test_typstpdf_build_succeeds_without_image_warnings`) is the written proof
the build compiles fine; the two `xfail(strict=True)` tests fail on the
exact collision behavior D-08 predicts.

## What the transcript shows

- **Extracted-image size set (D-08):** pre-fix, `{(16, 64)}` — a
  **single-element set**, confirming the compiled `master.pdf` embeds only
  ONE distinct picture across both documents, not two.
- **Which file landed at `<build>/images/chart.png`:** the CONVERTED
  stand-in (16x64, matching `_static/converted_chart_stand_in.png` exactly
  — confirmed by a separate `cmp` this session: `cmp
  /tmp/img50-red-tree/images/chart.png
  tests/fixtures/converted_image_collision_render_gate/_static/converted_chart_stand_in.png`
  reported no difference). The REAL source image (40x24,
  `tests/fixtures/converted_image_collision_render_gate/images/chart.png`)
  was never copied into the output tree — a direct `cmp` against the
  output-tree file differs starting at byte 20.
- **`_typst_converted/` absence:** confirmed absent from the pre-fix output
  tree entirely (`find /tmp/img50-red-tree -iname '*typst_converted*'`
  returned no matches, over a full `-b typstpdf` build of the same
  fixture).

## Observed vs. predicted write-order outcome

`write()` iterates `sorted(docnames)` (`typsphinx/builder.py:726`), so
`converted_source` is tracked before `real_source` alphabetically, and the
CONVERTED stand-in is predicted to be the winner that occupies
`images/chart.png`. **Observed matches predicted**: the extracted PDF
embeds only the `(16, 64)` converted-stand-in dimensions, and the
output-tree `images/chart.png` byte-matches the converted stand-in fixture
asset, not the real source image. No disagreement between observation and
prediction to record.
