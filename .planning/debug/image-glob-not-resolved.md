---
status: resolved
trigger: "Corpus gate fatal: TypstError: file not found (searched at <build>/_static/translation.*). .. figure:: /_static/translation.* at usage/advanced/intl.rst:12 emitted as image(\"../../_static/translation.*\", width: 100%) -- the literal .* glob is never resolved to a concrete file."
created: 2026-07-12T00:00:00
updated: 2026-07-12T00:00:00
---

## Current Focus

reasoning_checkpoint:
  hypothesis: "TypstBuilder.post_process_images (builder.py:139) does a bare `node.get(\"uri\", \"\")` read and never resolves `*`-glob image URIs to a concrete candidate file, unlike the base sphinx.builders.Builder.post_process_images which walks node['candidates'] (populated during the read phase by sphinx.environment.collectors.asset.ImageCollector) and picks the best match from self.supported_image_types, rewriting node['uri'] to the concrete resolved path. TypstBuilder declares no supported_image_types (empty list, from Builder base default), so even if the glob-resolution branch were reached it would never find a match. Result: for a `.. figure:: _static/translation.*` node, node['uri'] stays the literal glob string \"_static/translation.*\" all the way through visit_image (emits the glob into the .typ) and copy_image_files (tries to copy a nonexistent literal '.*' file)."
  confirming_evidence:
    - "Read sphinx/environment/collectors/asset.py ImageCollector.process_doc: for imguri.endswith('.*') it sets node['uri'] = rel_imgpath (still the glob string) and populates node['candidates'] with {mimetype: concrete_path} pairs discovered via glob() on disk -- it does NOT rewrite node['uri'] to a concrete file itself."
    - "Read sphinx/builders/__init__.py Builder.post_process_images: for '*' not in node['candidates'], iterates self.supported_image_types, picks first present candidate keyed by mimetype, and does node['uri'] = candidate -- this is the ONLY place a glob gets resolved to a concrete file."
    - "Read sphinx/builders/html/__init__.py and latex/__init__.py: both declare a concrete supported_image_types class list (html: svg+xml/png/gif/jpeg; latex: pdf/png/jpeg) and both call self.post_process_images(doctree) in write_doc-equivalent flow. TypstBuilder declares no supported_image_types override (inherits Builder's empty list) and its own post_process_images override never consults candidates at all."
    - "typsphinx/builder.py:139-160 TypstBuilder.post_process_images: confirmed bare `imguri = node.get('uri', '')`, no reference to node['candidates'] anywhere in the file."
  falsification_test: "If, after declaring supported_image_types and rewriting post_process_images to resolve node['candidates'] for glob URIs (mirroring base Builder logic), a fixture with `.. figure:: /_static/pic.*` where only pic.png exists still emits image(\"pic.*\", ...) into the .typ instead of image(\"pic.png\", ...), the hypothesis is wrong."
  fix_rationale: "Declare supported_image_types (Typst-embeddable mimetypes, SVG preferred like the HTML builder) and rewrite post_process_images to resolve glob candidates via node['candidates'], writing the resolved concrete path back into node['uri'] (so translator.visit_image emits the concrete path) AND into self.images (so copy_image_files copies the concrete file). Must gracefully fall back to the existing bare node.get('uri','') behavior when node has no 'candidates' key at all (hand-built doctrees in tests/test_builder.py construct nodes.image(uri=...) directly, bypassing Sphinx's ImageCollector environment pass -- those must keep working byte-identically)."
  blind_spots: "Two other textual '.*' matches exist in the corpus per the trigger description but are confirmed NOT live image directives (no matching asset / prose in code block) -- not chased. If a THIRD distinct fatal appears after this fix, it is out of scope per campaign discipline and must be reported separately, not chased into this session."

hypothesis: CONFIRMED (see reasoning_checkpoint) -- verified by reading both sphinx.environment.collectors.asset.ImageCollector and sphinx.builders.Builder.post_process_images, and typsphinx/builder.py's current override.
test: Add supported_image_types + rewrite post_process_images to resolve node['candidates'] for glob URIs, add fast offline regression fixture (glob figure where only one concrete file exists), verify emitted .typ has concrete path not '.*', verify existing test_builder.py hand-built-doctree tests still pass unmodified.
expecting: glob resolves to concrete file in both node['uri'] and self.images; non-glob URIs byte-unchanged; hand-built doctree tests (no candidates key) unaffected.
next_action: Apply the fix to typsphinx/builder.py, add tests/fixtures/glob_image_render_gate fixture + tests/test_glob_image_render_gate.py, run fast suite, lint, then re-run corpus gate.

## Symptoms

expected: Sphinx doc/ corpus compiles end-to-end through -b typstpdf with no fatal TypstCompilationError; a `.. figure:: /_static/translation.*` glob resolves to the concrete asset file present under _static/.
actual: typst.compile() fails with "TypstError: file not found (searched at <build>/_static/translation.*)". usage/advanced/intl.typ:25 emits image("../../_static/translation.*", width: 100%) -- the literal glob string, never resolved to a concrete filename.
errors: "TypstError: file not found (searched at <build>/_static/translation.*)"
reproduction: uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate -m slow -v -s (real Sphinx doc/ corpus, post bug #1-#12 fixes)
started: Pre-existing bug surfaced by Phase 15 corpus gate, 13th fatal in the fix-forward campaign (first builder.py fatal after 12 translator.py fatals).

## Eliminated

## Evidence

- timestamp: initial
  checked: typsphinx/builder.py TypstBuilder.post_process_images (line 139-160)
  found: Bare `imguri = node.get("uri", "")` read, no consultation of node['candidates'], no supported_image_types class attribute declared anywhere in builder.py.
  implication: Glob URIs (`.*`) are never resolved; the literal glob string flows through to both self.images tracking and (unmodified) node['uri'] read by translator.visit_image.

- timestamp: initial
  checked: sphinx/environment/collectors/asset.py ImageCollector.process_doc + collect_candidates (read phase, EnvironmentCollector, runs for ALL builders identically)
  found: For a glob uri ending in ".*", node['uri'] is set to the relative-to-srcdir glob path (still contains the literal '.*') and node['candidates'] is populated as {mimetype: concrete_relative_path} via an on-disk glob() scan. For a non-glob uri, node['candidates']['*'] = node['uri'] (the already-resolved concrete path) -- no glob-resolution needed for that case.
  implication: The read phase alone never produces a concrete uri for glob images; resolution is entirely the responsibility of the builder's post_process_images (called during write/translate phase), consulting node['candidates'] against the builder's supported_image_types.

- timestamp: initial
  checked: sphinx/builders/__init__.py Builder.post_process_images (base) + sphinx/builders/html/__init__.py and latex/__init__.py supported_image_types declarations
  found: Base method iterates self.supported_image_types in order, uses the first mimetype present in node['candidates'], sets node['uri'] = candidate. HTML declares ['image/svg+xml','image/png','image/gif','image/jpeg']; LaTeX declares ['application/pdf','image/png','image/jpeg']. Base method hard-indexes node['candidates'] (KeyError if absent) and tracks self.images[candidate] = self.env.images[candidate][1] (HTML's flat-dir uniquename scheme) -- not directly reusable as-is for typsphinx's srcdir-structure-preserving self.images[uri] = "" scheme, and would break the hand-built-doctree unit tests in tests/test_builder.py that never set 'candidates'.
  implication: Must replicate the base's glob-candidate-resolution logic (not call it directly), keep it read via node.get("candidates") with a graceful fallback to legacy behavior when absent, and keep typsphinx's own self.images[resolved_uri] = "" tracking scheme unchanged.

## Resolution

root_cause: TypstBuilder.post_process_images() (typsphinx/builder.py) never consults docutils image nodes' `candidates` dict (populated during Sphinx's read-phase ImageCollector for every builder) and TypstBuilder declares no `supported_image_types`. For a `*`-glob image URI (e.g. `.. figure:: _static/translation.*`), Sphinx's read phase leaves `node['uri']` as the literal unresolved glob string and instead records the concrete on-disk candidates in `node['candidates']` keyed by mimetype -- resolving that to a single concrete file is the BUILDER's job (mirroring sphinx.builders.Builder.post_process_images, done by html/latex builders via their own supported_image_types + candidate-picking loop), a step TypstBuilder's override never performed. The unresolved glob then flows unchanged into both translator.visit_image (emitted into the .typ as image("..._static/translation.*", ...)) and copy_image_files (tries to copy a literal, nonexistent "translation.*" file) -- so typst.compile() fails "file not found".
fix: Declared TypstBuilder.supported_image_types = ["image/svg+xml", "image/png", "image/gif", "image/jpeg"] (mirrors the HTML builder's preference order; Typst's image() function embeds all four). Rewrote post_process_images() to consult node["candidates"]: "?" (non-local URI) is skipped; "*" (already-resolved single candidate -- the non-glob case) is tracked byte-unchanged; otherwise (a genuine glob) the first mimetype present in supported_image_types is picked and node["uri"] is rewritten to that concrete path (so both visit_image and copy_image_files see the resolved file) -- no match degrades gracefully with a warning, no crash. Doctrees with no "candidates" key at all (hand-built doctrees in tests/test_builder.py that bypass Sphinx's ImageCollector) fall back to the original bare node.get("uri","") tracking, unchanged.
verification: New tests/test_glob_image_render_gate.py (fixture: .. figure:: /_static/pic.* where only pic.png exists) confirmed FAILS pre-fix with the exact "file not found (searched at .../_static/pic.*)" fatal (git stash verified) and PASSES post-fix: emitted .typ contains image("_static/pic.png") not image("_static/pic.*"), pic.png copied into output tree, index.pdf is real %PDF. Full fast suite (incl. all 21 hand-built-doctree tests in test_builder.py, unaffected) 414 passed, 15 deselected. black/ruff/mypy clean. Corpus gate re-run: the "file not found (searched at .../_static/translation.*)" fatal is GONE -- corpus now progresses past it. A DIFFERENT, distinct fatal now surfaces: "TypstError: unexpected argument: start" from codly(start: N) (translator.py:1319) -- codly 1.3.0 (the pinned @preview version) has no `start` parameter (renamed to `offset`/`offset-from` in this API version), a package-API-mismatch bug in code-block line-numbering, NOT an image-handling issue. 20 occurrences across 4 files (development/tutorials/{autodoc_ext,extending_build,adding_domain,extending_syntax}.typ), all from :linenos: literalinclude code-blocks where Sphinx computes highlight_args['linenostart']. STOPPED per scope-discipline -- reported as the 14th fatal, not fixed in this session.
files_changed: [typsphinx/builder.py, tests/test_glob_image_render_gate.py, tests/fixtures/glob_image_render_gate/conf.py, tests/fixtures/glob_image_render_gate/index.rst, tests/fixtures/glob_image_render_gate/_static/pic.png]
