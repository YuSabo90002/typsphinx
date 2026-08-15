# Phase 50: PR #131 Image Path Defects - Context

**Gathered:** 2026-08-14
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase fixes the two defects the PR #131 review filed against the code PR #131 itself
introduced. Both live in `TypstBuilder._track_image()` and its consumer
`TypstBuilder.copy_image_files()`, and both are fixed together as one change:

- **IMG-01** — a converted image rehomed to `images/<basename>` collides, in `self.images`, with an
  ordinary source image genuinely at `<srcdir>/images/<basename>`. Both tracking sites guard with
  `if <key> not in self.images`, so whichever document is written first wins: the loser is never
  copied, both `.typ` files emit the identical `image("images/<basename>")` call, one document
  renders a completely different picture, and the build succeeds with no warning. This is also a
  **regression in failure mode** — the same project aborted loudly before PR #131 (Issue #130) and
  now renders the wrong picture silently.
- **IMG-02** — `path.relpath(resolved_uri, self.doctreedir)` assumes the absolute URI lives under
  `doctreedir`. When it does not, `relpath` returns a `../`-prefixed path, and
  `dest = path.join(self.outdir, imguri)` writes **outside** `outdir` — into the user's project tree
  in one measured shape, and back onto `src == dest` (Issue #130's original "are the same file"
  shape) in another.

**Explicitly out of scope.** Nothing here touches `write_doc()`'s composition shape, and content
files staying docname-named means `_compute_relative_image_path()` needs no change at all. This
phase is independent of the v0.8.0 composition work (Phases 47-49) and must not pick up any of it.

</domain>

<decisions>
## Implementation Decisions

**The owner declined a gray-area discussion for this phase** (answer: "議論ポイント無し"). The
decisions below were therefore taken by Claude from measurement, and are recorded here so
downstream agents implement them rather than re-derive or re-ask. They are all reversible unless
noted. Where a decision was genuinely close, the rejected alternatives and the measurement that
decided it are written down so a researcher can overturn one **with evidence**, not by preference.

### IMG-01 — how a converted image is rehomed

- **D-01: an absolute URI keeps today's rehome target unless a real source image occupies it.**
  `_track_image()` computes `rel_uri` exactly as today, then probes the
  filesystem for the ordinary-image location that `rel_uri` would denote — the join of `srcdir` and
  `rel_uri`. If nothing is there, `rel_uri` is used unchanged, so today's behavior and today's
  emitted path are preserved for every non-colliding project. If something is there, the converted
  image is relocated per D-02 instead.

- **D-02: the collision escape hatch is a reserved top-level namespace, not a numeric suffix.** A
  relocated converted image is tracked under `_typst_converted/` followed by the same relative path
  the rehome produced. Rejected alternative — Sphinx-style suffixing of the basename in the same
  directory — because the winner/loser assignment would then depend on document write order, making
  the emitted filename non-reproducible across builds.

- **D-03: the probe is against the filesystem, never against the accumulated dict.** Deciding the
  collision from whether the key is already present in `self.images` reintroduces exactly the
  order-dependence D-02 rejects, because the source image may be tracked after the converted one.
  The filesystem probe returns the same answer regardless of traversal order.

- **D-04: relocation under D-02 is silent, and is not a warning-worthy event.** A project that uses
  an image-conversion extension and keeps its assets in an `images/` directory is ordinary, not
  suspect; after the fix its output is correct, and a per-build warning would be noise. Sphinx's own
  de-collision of converted filenames is likewise silent. The IMG-02 escape (D-06) does warn, and
  that asymmetry is deliberate.

### IMG-02 — an absolute URI that is not under doctreedir

- **D-05: the escape is contained by relocating, not by dropping the image.**
  The relocation target is the same reserved namespace D-02 uses.
  When the rehome result points outside `doctreedir` — detected as a leading
  parent-directory component — the image is tracked under the reserved namespace so that
  `copy_image_files()` still copies it, and every destination it writes lands under `outdir`.
  Rejected alternative — warn and abandon tracking — because it converts a recoverable path defect
  into a missing image and a Typst compile fatal, and SC#2 asks for destinations under `outdir`,
  not for the image to disappear.

- **D-06: the IMG-02 relocation warns, because it is genuinely anomalous.** All three of Sphinx's
  own image post-transforms write under the doctree image directory, so reaching this branch means a
  third-party extension placed an absolute URI somewhere unexpected. The message names the URI and
  says the image could not be rehomed relative to the doctree directory and was relocated.

- **D-07: the cross-drive crash path is closed in the same guard.** On Windows, `path.relpath`
  raises `ValueError` when the two paths sit on different drives, which today would abort the build.
  That exception is caught and routed into the same D-05 relocation. Reachability is near-zero, but
  the guard is one clause in code this phase is already rewriting, and the milestone runs Windows
  CI lanes.

### Verification obligations

- **D-08: the pre-fix RED for IMG-01 is an embedded-image assertion read out of the compiled PDF.**
  Binding constraint #4 forbids treating "GATE-01 fixture" as a checkbox for a compiles-fine defect:
  the RED assertion must be written down before implementation. For IMG-01 the RED is that the
  single compiled PDF embeds the **same** picture for both documents, and that only one of the two
  files was copied into the output tree. `pypdf` and `pillow` are already dev dependencies, so no
  new dependency is needed.

- **D-09: the two fixture images are discriminated by pixel dimensions, not by raw bytes.** Typst
  re-encodes what it embeds, so a byte comparison against the source PNG is not a stable assertion.
  Giving the source image and the converted stand-in different pixel dimensions makes the extracted
  images self-identifying. Pixel-content comparison via pillow is the fallback if a dimension
  collision is ever forced.

- **D-10: the IMG-01 fixture is one master wrapper over two content documents, producing one PDF.**
  Since Phase 47 only wrappers compile to PDF, and a single PDF whose extracted-image list must
  contain two distinctly-sized pictures is a stronger and cheaper assertion than two PDFs each
  checked in isolation. The RED shape falls straight out of it — pre-fix, that list holds one
  picture, or the same picture twice.

- **D-11: SC#3's two-build comparison is a one-time recorded measurement.**
  It does not become a new permanent test.
  The success criterion asks for byte-identical destinations measured across the change; it
  does not ask for a standing test, and the repository already carries a full-corpus gate. The
  comparison runs the plain Typst builder — destinations are what is compared, so no PDF compile is
  needed — over the project docs source tree and over every root under the test roots directory, and
  the before/after file trees are recorded as phase evidence.

- **D-12: PR #131's own regression tests are a fixed point and must pass byte-unchanged.** Three
  assertions couple to the current rehome target: the emitted-path and copied-asset assertions in
  the absolute-image render gate, and the rehomed-uri assertion in the builder unit tests. D-01 was
  chosen so that all three keep passing without edit. **If an implementation attempt requires
  editing any of them, that is evidence D-01 was violated — escalate to the owner rather than
  adjusting the expected string.** Binding constraint #6 (no laundered gates) governs.

### Claude's Discretion

- The exact spelling of the reserved namespace directory. `_typst_converted/` is the name the
  filed todo proposed and is the default; a researcher may propose a different reserved name with a
  rationale, but it must be a single reserved top-level component so that a second-order collision
  with a real source directory is implausible.
- What happens if the reserved namespace path *itself* collides with a real source directory. A
  second-order guard is welcome but must not reintroduce order-dependence.
- Whether the two defects land as one commit or two, and whether one shared helper or two guards
  express D-01/D-05 in code. They are one change conceptually; the split is a planning choice.
- Whether a debug-level log records a D-02 relocation. D-04 forbids a warning, not a debug line.
- The concrete pixel dimensions and file names used in the D-09 fixture.

### Folded Todos

Both folded todos ARE this phase — they are the two filed defects, matched at score 0.9 each:

- `.planning/todos/pending/2026-08-10-rehomed-converted-image-collides-with-srcdir-images-dir.md` —
  IMG-01. Carries the 2026-08-10 probe measurement (73-byte real source image vs 68-byte converted
  image; `Copying 1 image file(s)` when two exist; both `.typ` files emitting the identical path;
  build succeeded with no warning) and the two candidate solutions D-01/D-02 chose between.
- `.planning/todos/pending/2026-08-10-track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri.md`
  — IMG-02. Carries the measured rehome table for three absolute URIs, showing one destination
  landing in the user's project tree and one collapsing back onto `src == dest`, plus the Windows
  cross-drive `ValueError` note D-07 acts on.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and standing constraints
- `.planning/ROADMAP.md` — the Phase 50 section (goal, the three success criteria, the dependency on
  Phase 49) and the "Binding constraints this roadmap is built on" list. Constraint #4 (GATE-01 with
  its non-fatal amendment) and constraint #6 (no laundered gates) both bind this phase directly.
- `.planning/REQUIREMENTS.md` — IMG-01 and IMG-02 statements, and the requirement-to-phase table.
- `.planning/PROJECT.md` — Constraints and Key Decisions sections; the milestone invariants
  (zero new runtime dependencies, four `@preview` packages, no new `typst_*` config value) apply
  unchanged here.

### The filed defects
- `.planning/todos/pending/2026-08-10-rehomed-converted-image-collides-with-srcdir-images-dir.md`
- `.planning/todos/pending/2026-08-10-track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri.md`

### Code this phase changes
- `typsphinx/builder.py` — `TypstBuilder._track_image()` is the single site both defects live in;
  `TypstBuilder.copy_image_files()` consumes the tracked key and the stashed override source and is
  where the destination is computed. `TypstBuilder.post_process_images()` is the caller and needs no
  change.

### Tests that must NOT move (D-12)
- `tests/test_absolute_image_render_gate.py` — PR #131's own Issue #130 render gate. Asserts the
  emitted `image("images/diagram.png")` call and the copied asset location.
- `tests/test_builder.py` — `test_post_process_images_rehomes_absolute_uri` asserts the rehomed uri
  string; `test_copy_image_files_uses_override_source_for_absolute_uri` sets its key by hand and is
  namespace-agnostic.
- `tests/fixtures/absolute_image_render_gate/` — the existing fixture, including the custom
  post-transform in its `conf.py` that reproduces Sphinx's converter mechanism without requiring an
  external converter binary. Extending this fixture family is the cheapest route to the D-10
  fixture; **mutating it in place is not**, because D-12 pins its current assertions.

### Sphinx sources the behavior mirrors (read, do not guess)
- `sphinx/transforms/post_transforms/images.py` in the installed Sphinx 9.1.0. Measured
  2026-08-14: `BaseImageConverter.imagedir` returns the doctree directory joined with `images` —
  this is why the IMG-01 collision key is `images/<basename>`. `DataURIExtractor.handle()` writes
  under an `embeded` subdirectory of that same directory. `ImageConverter.handle()` takes its output
  filename from the environment's image registry, which already de-collides converted images
  **against each other** — so converted-vs-converted is not a case this phase must handle, and the
  D-01 probe only ever has to consider converted-vs-source.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `pypdf` and `pillow` are already declared dev dependencies, so D-08/D-09's embedded-image
  extraction adds no dependency. The repository has an established render-gate shape combining a
  structural assertion over the emitted `.typ` with a `pypdf` extraction from the compiled PDF;
  several existing render gates follow it and are the pattern to copy.
- `tests/fixtures/absolute_image_render_gate/conf.py` already registers a custom post-transform that
  reproduces Sphinx's converter mechanism (rewriting the image uri to an absolute path under the
  doctree image directory) without depending on an external converter binary. The D-10 fixture needs
  exactly this mechanism plus one real source image at the colliding location.
- Test subprocess builds in this repository invoke Sphinx as `sys.executable -m sphinx`, never
  through a console-script shim — this sidesteps the documented NixOS PATH-shadowing hazard and must
  be preserved in any new fixture test.

### Established Patterns
- `self.images` maps a tracked key to either the empty string (ordinary source-relative image, copy
  source derived from `srcdir`) or the true absolute location (rehomed image, used as an override
  copy source). Both defects are consequences of that key being derived without checking what else
  can claim it; the value convention itself is sound and stays.
- Both tracking paths guard insertion with a not-in-dict check, which is what silently discards the
  loser today. Whatever replaces it must stay idempotent for the genuinely-same-image case.

### Integration Points
- `copy_image_files()` computes its destination by joining `outdir` with the tracked key, so the
  key **is** the destination path. Any change to how the key is chosen changes where the file lands
  and what the translator emits — which is exactly why D-01 keeps the key unchanged in the common
  case, and why D-12 can hold.
- `builder.py` already contains an output-path collision validator and helpers that reason about
  paths escaping the output directory; the researcher should check whether the parent-directory
  detection D-05 needs already exists there before writing a new one.

</code_context>

<specifics>
## Specific Ideas

- The owner's framing of IMG-01 in the filed todo is that the interesting property is not the
  collision but the **failure-mode regression**: "うるさく失敗する" became "黙って間違った画像を
  出す". The fix is only complete when the silent-wrong-output shape is provably gone, which is why
  SC#1 and D-08 insist the proof is read out of the compiled PDF rather than out of the copy list.
- The two defects are to be treated as one change to one function, per both todos' closing note —
  not as two independently-scheduled fixes.

</specifics>

<deferred>
## Deferred Ideas

None — the owner declined discussion and no new capability was raised.

### Reviewed Todos (not folded)

The todo matcher returned six further pending todos at score 0.6. All are keyword coincidences with
no relation to image path handling, and none is folded:

- `2026-08-04-release-create-job-missing-uv-verify-end-to-end.md` — release automation; belongs to
  the milestone's release phase, not here.
- `2026-08-11-ruff-generic-linux-elf-unrunnable-on-nixos.md` — local toolchain environment.
- `2026-08-12-label-collision-false-negative-in-compile-time-xref-guard.md` — translator, Phase 48
  territory.
- `2026-08-14-include-edge-key-separators-unescaped-two-edges-can-collide.md` — translator, Phase 49
  territory.
- Remaining lower-scored matches likewise unrelated to `_track_image()`.

</deferred>

---

*Phase: 50-PR #131 Image Path Defects*
*Context gathered: 2026-08-14*
