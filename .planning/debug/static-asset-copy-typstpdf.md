---
status: resolved
trigger: "Corpus gate fatal: TypstError: file not found (searched at <build>/_static/python-logo.png). Referenced static asset not copied into typstpdf output tree."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "TypstPDFBuilder.write_doc (builder.py:483) overrides the base write_doc but omits the self.post_process_images(doctree) call the parent makes (builder.py:189). So during a typstpdf build self.images is never populated; copy_image_files() early-returns on the empty dict; referenced image/static assets (e.g. _static/python-logo.png) are never copied into outdir; typst.compile() in finish() then fails 'file not found'."
  confirming_evidence:
    - "Minimal figure+_static fixture: `-b typst` logs 'Copying 1 image file(s)...' and _static/python-logo.png lands in outdir; PDF-equivalent .typ compiles."
    - "Same fixture, `-b typstpdf`: NO 'Copying image file(s)' log line at all; _static/ dir absent from outdir; identical 'TypstError: file not found (searched at .../_build/_static/python-logo.png)' — a byte-for-byte match to the corpus fatal."
    - "finish() (via super().finish()) calls copy_image_files()+copy_template_assets(), proving the builder INTENDS to copy tracked images — but write_doc never registered any, so the dict is empty."
  falsification_test: "If, after adding self.post_process_images(doctree) to TypstPDFBuilder.write_doc, the typstpdf build still fails to copy _static/python-logo.png, the hypothesis is wrong."
  fix_rationale: "The parent already has a proven image-tracking → copy pipeline (post_process_images + copy_image_files) that the `-b typst` builder uses successfully. The PDF builder's write_doc override simply forgot the tracking call. Restoring that single call makes the PDF builder track images identically, fixing the whole class (any figure/image node, including _static/* assets), not just python-logo.png. It reuses existing machinery, restructures nothing."
  blind_spots: "Assets referenced by the emitted .typ but NOT via a docutils image node (e.g. a raw typst include, or a template/theme asset) would not be caught by post_process_images. Mitigation: the only thing emitting image('_static/…') in the .typ is translator.visit_image (image nodes). Per scope-discipline, rebuild corpus after fix; if a DIFFERENT non-image-node asset fatal surfaces, STOP and report."

hypothesis: CONFIRMED (see reasoning_checkpoint)
test: add post_process_images to TypstPDFBuilder.write_doc; rebuild fixture + corpus
expecting: _static asset copied, PDF produced, corpus python-logo fatal gone
next_action: Apply the one-line fix, add fast regression test, rebuild fixture + corpus, run fast suite + lint.

## Symptoms

expected: Sphinx doc/ corpus compiles through -b typstpdf with no fatal TypstCompilationError; referenced static assets (_static/python-logo.png) resolve at compile time.
actual: Typst compilation failed: TypstError: file not found (searched at <build>/_static/python-logo.png). The emitted master .typ references _static/python-logo.png but the file is never copied into the Typst output tree.
errors: "TypstError: file not found (searched at .../_build/_static/python-logo.png)"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
started: Pre-existing bug surfaced by Phase 15 corpus gate.

## Eliminated

## Evidence

- timestamp: initial
  checked: grep python-logo across corpus doc/
  found: Referenced via ".. figure:: _static/python-logo.png" in doc/index.rst:89. File exists at doc/_static/python-logo.png. conf.py has html_static_path=['_static'] but no html_logo. So it is a GENUINE docutils image node uri "_static/python-logo.png", NOT a theme/html_logo-only asset.
  implication: copy_image_files() SHOULD resolve srcdir/_static/python-logo.png → outdir/_static/python-logo.png IF the image were tracked in self.images.

- timestamp: initial
  checked: builder.py TypstBuilder.write_doc (162) vs TypstPDFBuilder.write_doc (483)
  found: TypstBuilder.write_doc calls self.post_process_images(doctree) at line 189. TypstPDFBuilder.write_doc OVERRIDES write_doc and does NOT call post_process_images. copy_image_files() early-returns "if not self.images".
  implication: For the typstpdf builder, images are never tracked, so nothing is copied. This is the likely root cause (not a theme/substitution walk gap).

## Evidence (continued)

- timestamp: fix-applied
  checked: Rebuilt minimal figure+_static fixture with -b typstpdf after adding post_process_images to TypstPDFBuilder.write_doc
  found: "Copying 1 image file(s)..." now logs; _static/python-logo.png lands in outdir; "Generated PDF"; %PDF magic bytes. The file-not-found fatal is gone.
  implication: Root cause confirmed and fixed.

- timestamp: regression-test
  checked: New tests/test_static_asset_copy_gate.py built via -b typstpdf, both directions
  found: PASSES with fix; FAILS without fix with the exact "file not found (searched at .../_build/_static/python-logo.png)" fatal (verified via git stash).
  implication: Deterministic offline regression test proves the fix and reproduces the corpus bug.

- timestamp: corpus-gate
  checked: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s
  found: python-logo.png "file not found" fatal RESOLVED (real 187KB python-logo.png now copied into corpus outdir). Full corpus now translates and progresses through the entire tree. A DIFFERENT, unrelated fatal now surfaces: "TypstError: expected semicolon or line break" — translator emits raw("...")/text("...") Typst string literals containing an UNESCAPED literal newline whenever an inline literal's source text wraps across a line (31 occurrences across ≥6 generated files, e.g. latex.typ:351 raw("'extraclassoptions': <newline> 'openany'")).
  implication: Asset-copy root cause is fully fixed. The next fatal is a separate translator.py escaping bug, NOT an asset-copy issue → STOP per scope-discipline (fix_requirements #4). GATE-02 not yet fully green; blocked by the distinct translator fatal.

## Resolution

root_cause: TypstPDFBuilder.write_doc() (builder.py) overrode TypstBuilder.write_doc() but omitted its self.post_process_images(doctree) call. During a typstpdf build self.images therefore stayed empty; copy_image_files() (called from finish() via super().finish()) early-returns on the empty dict; any image/static asset referenced by an image node (e.g. a `.. figure:: _static/python-logo.png`) was never copied into the output tree; typst.compile() in finish() then aborted with "file not found". The `-b typst` builder was unaffected because its write_doc DID call post_process_images.
fix: Added self.post_process_images(doctree) to TypstPDFBuilder.write_doc (one call, mirroring the parent), so the typstpdf builder tracks image nodes and copy_image_files() copies them. General across all image-node-referenced assets, not python-logo.png-specific; reuses existing machinery; no restructuring.
verification: Minimal fixture builds to %PDF with asset copied; new tests/test_static_asset_copy_gate.py passes with fix and fails without (both directions); fast suite 390 passed; black/ruff/mypy clean; real corpus now copies python-logo.png and the file-not-found fatal is gone. GATE-02 not fully green — a DISTINCT unrelated translator fatal (unescaped newline in raw()/text() string literals) now blocks full corpus compile; reported per scope-discipline, not fixed.
files_changed: [typsphinx/builder.py, tests/test_static_asset_copy_gate.py, tests/fixtures/static_asset_copy_render_gate/conf.py, tests/fixtures/static_asset_copy_render_gate/index.rst, tests/fixtures/static_asset_copy_render_gate/_static/python-logo.png]
