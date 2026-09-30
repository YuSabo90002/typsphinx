---
created: 2026-08-06T22:39:26.922Z
title: Review PR #131 — rehome absolute image URIs from ImageConverter/ImageDownloader
area: builder, tests
severity: major
files:
  - typsphinx/builder.py
  - tests/test_builder.py
  - tests/test_absolute_image_render_gate.py
  - tests/fixtures/absolute_image_render_gate/
  - CHANGELOG.md
---

## Problem

PR #131 (https://github.com/YuSabo90002/typsphinx/pull/131) is an **external
contribution** from @christianwehe, opened 2026-08-05, fixing issue #130. As of
2026-08-07 it has **zero reviews and zero comments** — nobody has looked at it.
State: OPEN, not a draft, `mergeable: MERGEABLE`, `fix/issue-130-absolute-image-uri`
→ `main`, +440/−10 across 8 files.

**The bug it claims to fix:** Sphinx's `ImageConverter` / `ImageDownloader`
post-transforms rewrite an image node's `uri` to an *absolute* filesystem path
under `<doctreedir>/images/...` for any image needing conversion (e.g.
`sphinxcontrib.rsvgconverter`, `sphinx.ext.imgconverter`) or download — unlike
ordinary images, which stay source-root-relative. `copy_image_files()` joined
that absolute uri onto both `srcdir` and `outdir` with `os.path.join()`, which
silently discards the first argument once the second is absolute — collapsing
src and dest onto the identical path ("are the same file") and copying nothing.
The translator then prepended a bogus `../..` depth prefix onto the still-absolute
uri, producing a garbled path that aborted the Typst compile with "file not found".

**The claimed fix:** `post_process_images()` rehomes an absolute resolved uri to
a doctreedir-relative path via a new `_track_image()` helper and tracks the true
absolute source location separately; `copy_image_files()` uses that tracked
location as the real copy source when present. The author reports reproducing it
end-to-end with a new real-compile render-gate fixture
(`tests/fixtures/absolute_image_render_gate/`) that simulates Sphinx's
image-converter mechanism without depending on an external converter binary —
confirmed RED against the unfixed builder, GREEN after the fix.

This matters because the underlying defect makes any converted/downloaded image
break the PDF build with no workaround, and because leaving a first-time external
contributor's PR unreviewed is its own cost.

## Solution

Review the PR. Specific things worth checking rather than taking the description
at face value:

1. **Verify the RED claim independently.** Per the standing rule that executor /
   contributor "I proved it RED" claims get re-measured: check out the branch,
   revert only `typsphinx/builder.py` to `main`'s version, and confirm
   `tests/test_absolute_image_render_gate.py` actually fails with the reported
   symptom — not merely fails for some other reason (missing fixture, import
   error, environment). Then confirm GREEN with the fix restored.
2. **Run the full suite on the branch**, not just the new test. Note that the
   NixOS sandbox has ~45 known environmental integration failures — compare
   against a `main` baseline run rather than reading absolute counts.
3. **Review `_track_image()`'s data structure and lifetime** — where the
   "true absolute source location" is stored, whether it survives parallel
   builds / incremental rebuilds, and whether the doctreedir-relative rehome
   interacts correctly with the translator's `../..` depth-prefix logic for
   *nested* documents (the fixture may only cover a flat/root-level doc).
4. **Check interaction with the other open image/master-document todos** — in
   particular whether the per-build image bookkeeping has the same per-build-not-
   per-master flaw as the include-dedup ledger
   (see `2026-08-05-shared-document-silently-dropped-from-all-but-first-master.md`).
5. **CHANGELOG entry** — confirm it lands under Unreleased and matches the
   project's entry style.
6. Decide: approve/merge, request changes, or take over. If commenting on the
   contributor's PR, write in English, read the whole thread first, keep it
   terse, and avoid phrasing that reads as blaming them.
