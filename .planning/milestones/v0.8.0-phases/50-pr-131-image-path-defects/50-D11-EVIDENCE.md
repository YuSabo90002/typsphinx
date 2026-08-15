# Phase 50 Plan 02 — D-11 Two-Build Comparison Evidence

**Measured:** 2026-08-14, inside worktree `agent-a1eac8d92c79d4eee`, provisioned per
`CLAUDE.md`'s worktree-isolated-execution rules
(`unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT && uv sync --extra dev --extra docs`,
every command below run via `uv run`).

D-11: SC#3's two-build comparison is a one-time recorded measurement, not a standing
test. This document records both halves, the nondeterminism this measurement's first
attempt surfaced, the corrected methodology, and the final empty diff.

## `git rev-parse HEAD` at both halves

```
BEFORE (Task 1, plan 50-02, builder.py byte-unchanged): 670bf7d2 (parent 1ba754b3)
AFTER  (Task 3, plan 50-02, after the Task 2 fix):       cd75fa1d
```

## Commands run and exit codes

```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT && uv sync --extra dev --extra docs
exit: 0

# BEFORE (Task 1, before any typsphinx/builder.py edit)
$ uv run python -m sphinx -b typst docs/source /tmp/img50-before/docs-source
exit: 0
$ uv run python -m sphinx -b typst tests/roots/test-basic /tmp/img50-before/test-basic
exit: 0

# AFTER (Task 3, same worktree, same environment, after the Task 2 fix)
$ uv run python -m sphinx -b typst docs/source /tmp/img50-after/docs-source
exit: 0
$ uv run python -m sphinx -b typst tests/roots/test-basic /tmp/img50-after/test-basic
exit: 0
```

## Finding 1 (Task 1): `docs/source` has no live image reference at all

RESEARCH.md and the plan cite `docs/source/examples/basic.rst:128`
(`.. figure:: _static/diagram.png`) as "at least one ordinary `.. figure::`
reference ... that exercises `copy_image_files()`'s unchanged ordinary-image
path." Directly measured, this claim is **incorrect**: that line sits inside a
`.. code-block:: rst` fence (lines 123–133) — it is literal example prose shown
to documentation readers, never parsed by docutils as a real directive.
Confirmed two ways:

1. `find docs -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname
   "*.gif" -o -iname "*.svg" -o -iname "*.webp"` returns **zero** files anywhere
   under `docs/` — there is no image asset for a real figure to reference even if
   one existed.
2. A real `-b typst` build of `docs/source` (Task 1's BEFORE build) produces zero
   image files anywhere in the output tree (`find <build-dir> -iname "*.png" -o
   ...` empty).

Per Task 1's own acceptance criterion ("if no image destination appears at all,
STOP ... that must be reported rather than silently accepted"), this is recorded
here rather than silently treated as satisfying an ordinary-image-destination
proof. **Consequence for D-11:** the `docs/source` half of this measurement is,
like `tests/roots/test-basic`, a **structural control** (proving the non-image
`.typ` output is untouched), not an image-destination proof. The
image-destination claim SC#1/D-01 make is independently and directly proven by
the two D-12-pinned render gates instead (`tests/test_absolute_image_render_gate.py`,
`tests/test_converted_image_collision_render_gate.py`), which drive real
`-b typstpdf` builds with real images and assert the exact emitted path and
copied-asset byte content — stronger evidence than a hash-manifest diff would
have given even had the docs figure been live.

## Finding 2 (Task 3): the naive `find`-over-everything manifest is not reproducible

The literal command sequence in `50-VALIDATION.md`/`50-RESEARCH.md` walks
`find <build-dir> -type f`, which sweeps up Sphinx's own `.doctrees/` read-phase
cache alongside the builder's actual `.typ`/image output. The first BEFORE/AFTER
comparison (unfiltered) was **not** empty:

```
$ diff /tmp/img50-before-manifest.txt /tmp/img50-after-manifest.txt
2d1
< 0b6ddd28a6382d3eab8024d06c4f2dde110d353dec44c1834cce1d04bdf0c846  test-basic/.doctrees/environment.pickle
5d3
< 295e75234ea3ff7f90b0570164b82491e34ed63dfc74ddc32a35c8bbce1ac5a5  docs-source/.doctrees/environment.pickle
23a22
> 98a836433c9b9b18d35f801e6fa57fd40d7f2bf8cf57f915a2dde4b5ec231fa3  docs-source/.doctrees/environment.pickle
25a25,26
> b327dac19f46f16c53dc1897466613368c1e21418273ab1e108564a42c0fec34  docs-source/.doctrees/changelog.doctree
> b39c57dfef0593530b95e78a12b9bd71e2a45b3a15c94b2059e4ade20fec9988  test-basic/.doctrees/environment.pickle
34d34
< ec37a6aaaac2b741e739d59f7543f2ac47a70ad57f124f850183686e680ff101  docs-source/.doctrees/changelog.doctree
exit: 1
```

Per the plan's own instruction ("do not rationalize it ... must be re-taken with
that source of nondeterminism identified in writing"), this was investigated
rather than accepted or dismissed. **Every** differing line is under a
`.doctrees/` path (confirmed: `diff ... | grep -v '.doctrees/'` leaves only diff
structural markers, no content). Classified by direct experiment — a THIRD build
of `docs/source`, with the *identical, already-fixed* code, into a fresh
directory:

```
$ uv run python -m sphinx -b typst docs/source /tmp/img50-after2/docs-source
exit: 0
$ sha256sum /tmp/img50-after/docs-source/.doctrees/environment.pickle \
            /tmp/img50-after2/docs-source/.doctrees/environment.pickle
98a836433c9b9b18d35f801e6fa57fd40d7f2bf8cf57f915a2dde4b5ec231fa3  /tmp/img50-after/docs-source/.doctrees/environment.pickle
47a4ba2ff447f0800a98ffb5772a0a8eaab67a21ca3a8ae12cbbefd1da0641e0  /tmp/img50-after2/docs-source/.doctrees/environment.pickle
$ sha256sum /tmp/img50-after/docs-source/.doctrees/changelog.doctree \
            /tmp/img50-after2/docs-source/.doctrees/changelog.doctree
b327dac19f46f16c53dc1897466613368c1e21418273ab1e108564a42c0fec34  /tmp/img50-after/docs-source/.doctrees/changelog.doctree
9a4b0484d3cf8e208e7b0f2042b4ff6b4a83e82392486ad0c10f814060a6b310  /tmp/img50-after2/docs-source/.doctrees/changelog.doctree
```

Both files differ **between two builds of the byte-identical fixed code**,
proving conclusively that `.doctrees/environment.pickle` and `.doctrees/*.doctree`
are inherently non-reproducible across separate build directories (Sphinx's own
read-phase pickle cache — not part of what `TypstBuilder` writes as its
"destination" output; `env.pickle`/`.doctree` files are produced by
`sphinx.environment.BuildEnvironment`, unrelated to `TypstBuilder._track_image()`
or any other code this phase touches). This is a measurement-methodology
artifact, not an SC#3 regression: no `.typ` file, no image file, and no
added/removed non-cache file appeared in the unfiltered diff at all.

**Corrected methodology:** exclude the `.doctrees/` subtree
(`find <build-dir> -type f -not -path '*/.doctrees/*'`) — this is the one
amendment to `50-VALIDATION.md`'s literal command sequence, made necessary by a
measured fact the validation strategy could not have anticipated (Sphinx's own
cache format is non-reproducible across build directories, independent of any
code this phase touches). `50-D11-BEFORE-MANIFEST.txt` and
`50-D11-AFTER-MANIFEST.txt` in this directory both use the corrected,
`.doctrees/`-excluded methodology consistently.

## Final comparison (corrected methodology)

```
$ find /tmp/img50-before -type f -not -path '*/.doctrees/*' -exec sha256sum {} \; \
    | sed 's#/tmp/img50-before/##' | sort > /tmp/img50-before-manifest.txt
$ find /tmp/img50-after -type f -not -path '*/.doctrees/*' -exec sha256sum {} \; \
    | sed 's#/tmp/img50-after/##' | sort > /tmp/img50-after-manifest.txt
$ diff /tmp/img50-before-manifest.txt /tmp/img50-after-manifest.txt
(empty)
exit: 0
```

18 lines in each manifest — every `.typ` file `-b typst` wrote for `docs/source`
(17 files) and `tests/roots/test-basic` (1 file, `output.typ`, plus each
directory's own `_template.typ`), zero image entries in either (consistent with
Finding 1: neither project tree contains a real image asset). Both manifests are
committed byte-identical to this diff's inputs: `50-D11-BEFORE-MANIFEST.txt`,
`50-D11-AFTER-MANIFEST.txt`.

## Reading, tied to SC#3

SC#3 ("The two D-11 manifests are byte-identical") is **met** on the corrected,
reproducible methodology: every `.typ` file `TypstBuilder` writes for an ordinary
project with no absolute-URI image at all is byte-for-byte unchanged across the
IMG-01/IMG-02 fix. This is the weakest of the three SC criteria to prove via this
mechanism specifically *because* neither available project tree contains a real
image (Finding 1) — the stronger, image-bearing claims (SC#1, SC#2, and D-01's
"the common case is unchanged" precondition D-12 depends on) are proven directly
by the D-10 collision render gate and the two D-12-pinned regression tests
(`tests/test_absolute_image_render_gate.py`,
`tests/test_builder.py::test_post_process_images_rehomes_absolute_uri`), both of
which exercise real images through a real `-b typstpdf` compile and pass with
zero edits after the Task 2 fix.

No new `.py` file was created by this measurement anywhere in the repository —
D-11 is a one-time recorded measurement, not a standing pytest module, per its
own definition.
