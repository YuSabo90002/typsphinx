---
phase: 50-pr-131-image-path-defects
reviewed: 2026-08-14T00:00:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - typsphinx/builder.py
  - tests/test_builder.py
  - tests/test_converted_image_collision_render_gate.py
  - tests/fixtures/converted_image_collision_render_gate/conf.py
  - tests/fixtures/converted_image_collision_render_gate/index.rst
  - tests/fixtures/converted_image_collision_render_gate/converted_source.rst
  - tests/fixtures/converted_image_collision_render_gate/real_source.rst
findings:
  critical: 1
  warning: 1
  info: 1
  total: 3
status: issues_found
---

# Phase 50: Code Review Report

**Reviewed:** 2026-08-14T00:00:00Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the phase's actual production diff (`typsphinx/builder.py`'s
`_track_image()` absolute-URI branch plus the new `RESERVED_IMAGE_NAMESPACE`
constant) against `git diff 2ccbbd3af86487a025ceb8be15f14b665d8c9d08..HEAD`,
and the accompanying unit tests (`tests/test_builder.py`) and real-compile
regression gate (`tests/test_converted_image_collision_render_gate.py` +
its fixture tree).

The headline fix — routing a rehomed-and-colliding converted image under
`_typst_converted/<rel_uri>` via a filesystem probe (`path.isfile`) rather
than a `self.images`-membership check — is sound and correctly closes the
write-order-dependence hazard its own docstring calls out (probing the
filesystem, not the accumulated dict, is exactly what makes the outcome
independent of `sorted(docnames)` traversal order). `copy_image_files()`
correctly contains every relocated destination under `outdir` (the
namespace constant and every fallback component — `path.basename()`,
suffix-stripped `rel_uri` gated by `_escapes_outdir()` — are guaranteed
free of `..`/absolute shape before they ever reach the dict), and
intermediate directories are created via the pre-existing `ensuredir()`
call. `_escapes_outdir()`'s reuse across the `typst_documents`-stem and
image-path domains is safe: it is a pure string-shape predicate with no
threaded state, and every edge case asked about in the review scope note
(a bare `".."`, an embedded `".."` not just a leading one, an
absolute-looking result, a drive-qualified result) is handled correctly.
The `path.isfile(path.join(self.srcdir, rel_uri))` probe cannot escape
`srcdir`, because the escape branch is evaluated and short-circuits first.
The new unit tests are not tautological — they assert concrete relocated
keys, exact warning counts/text, and (in the real-compile gate) pixel
dimensions extracted from the actually-compiled PDF via `pypdf`, which is
strong pinning for a defect whose entire failure mode is "silently renders
the wrong picture."

One real defect was found: the **escape branch discards directory context**
that the **collision branch preserves**, opening a second, unaddressed
collision surface *inside* the very namespace this phase introduced to
fix the first one. See CR-01.

## Critical Issues

### CR-01: Escape-branch relocation key uses only the basename, so two different escaping images with the same filename silently collide inside `_typst_converted/`

**File:** `typsphinx/builder.py:938` (collision branch for comparison: `typsphinx/builder.py:951`)

**Issue:**

The two Phase 50 relocation branches key their `_typst_converted/`
destination differently:

```python
938  key = f"{RESERVED_IMAGE_NAMESPACE}/{path.basename(resolved_uri)}"   # escape branch
...
951  key = f"{RESERVED_IMAGE_NAMESPACE}/{rel_uri}"                        # collision branch
```

The collision branch (line 951) preserves the *full* `rel_uri` (directory
structure and basename), so two converted images that would have rehomed
to different `images/...` paths still get different relocated keys. The
escape branch (line 938) throws away everything except
`path.basename(resolved_uri)` — the directory the escaping absolute URI
originally lived under is discarded entirely.

Concrete failure scenario: a third-party extension (or two independent
extensions) rewrites two *different* image nodes' URIs to two absolute
paths outside `doctreedir`, e.g.:

- `abs_uri_1 = "/opt/ext-cache/setA/chart.png"` (real bytes: picture A)
- `abs_uri_2 = "/opt/ext-cache/setB/chart.png"` (real bytes: picture B)

Both trip `_escapes_outdir()` (the `path.relpath()` result necessarily
contains a `..` segment to reach a directory outside `doctreedir`), so
both compute the *same* key, `"_typst_converted/chart.png"`. Per-image,
line 958's `node["uri"] = key` is assigned unconditionally, but line 959's
`if key not in self.images: self.images[key] = resolved_uri` only wins
for whichever image `write()`'s `sorted(docnames)` traversal reaches
first. The second document's `.typ` output ends up with
`image("_typst_converted/chart.png")` too, and `copy_image_files()` only
ever copies `abs_uri_1`'s bytes to that destination — the second
document silently renders picture A's content under a caption/context
that describes picture B, with no diagnostic beyond the two individually
correct-looking "could not rehome image URI ... -- relocated to
'_typst_converted/chart.png'" warnings (which read as two independent,
successful relocations, not as a same-key collision between them).

This is the same failure shape (a filesystem-agnostic, dict-order-
dependent `self.images` key collision) IMG-01 itself was — and which this
very phase closed for the collision branch, using exactly the technique
(carry full `rel_uri`, not just a basename) that would also close it here.
The escape branch does not use the D-02 filesystem-probe technique either
(there is nothing meaningful to probe, since the URI is genuinely outside
`srcdir`/`doctreedir`), so the fix cannot be "probe before relocating" —
it must instead preserve enough of the original path to keep two
different escaping sources from colliding.

**Fix:** Derive the escape-branch key from more than the basename, e.g.
hash or otherwise disambiguate on the original absolute directory instead
of discarding it, or emit an *additional* warning (or raise) when a
second image is about to relocate onto an already-claimed
`_typst_converted/` key so the collision is at least visible rather than
silent:

```python
if escaped:
    key = f"{RESERVED_IMAGE_NAMESPACE}/{path.basename(resolved_uri)}"
    if key in self.images and self.images[key] != resolved_uri:
        logger.warning(
            f"image URI {resolved_uri!r} relocated to {key!r} collides "
            f"with a previously relocated image at the same path -- "
            f"only one of these two files will be copied"
        )
    logger.warning(
        f"could not rehome image URI {resolved_uri!r} relative "
        f"to the doctree directory -- relocated to {key!r}"
    )
```

(A full fix would disambiguate the key itself, e.g. incorporating a hash
of the source directory, rather than merely upgrading the diagnostic —
the above is the minimum change that stops the failure from being
*silent*.)

## Warnings

### WR-01: Relocation targets are never probed against a pre-existing genuine file already living under `_typst_converted/`

**File:** `typsphinx/builder.py:943-956`

**Issue:** The D-01 collision probe (line 943,
`path.isfile(path.join(self.srcdir, rel_uri))`) checks whether the
*un-relocated* target collides with a real source image, and relocates
under `_typst_converted/` when it does. But nothing probes whether the
*relocated* destination itself — `path.join(self.srcdir,
RESERVED_IMAGE_NAMESPACE, rel_uri)` — already holds a genuine user file.
If a project happens to have real source content literally at
`<srcdir>/_typst_converted/images/chart.png` (nothing in Sphinx or this
extension prevents a user from creating such a directory; `_static` is a
directly analogous, commonly-populated underscore-prefixed directory in
ordinary Sphinx projects), a converted image relocated to that same key
would silently claim the same `self.images` entry the genuine file would
also claim if it were ever tracked as an ordinary image, via the exact
same "first write wins" `if key not in self.images` pattern this phase's
own D-01 probe was written to defeat one level up. This is a narrower
version of CR-01, gated by the reserved-namespace naming convention
holding in practice (which is a soft, documentation-level guarantee, not
an enforced one).

**Fix:** Either explicitly reject/warn when a real file already exists at
the *relocated* path (mirroring the D-01 probe one level down:
`path.isfile(path.join(self.srcdir, RESERVED_IMAGE_NAMESPACE, rel_uri))`),
or document explicitly that `_typst_converted/` is a reserved namespace
users must not populate (parallel to how Sphinx documents `_static` as
user-owned but e.g. `_build`/output directories as tool-owned).

## Info

### IN-01: `try` block scope is wider than what can actually raise

**File:** `typsphinx/builder.py:911-929`

**Issue:** The `try`/`except ValueError` wraps both `path.relpath()`
*and* `_escapes_outdir(rel_uri)`:

```python
try:
    rel_uri = path.relpath(resolved_uri, self.doctreedir).replace(
        path.sep, "/"
    )
    escaped = _escapes_outdir(rel_uri)
except ValueError:
    rel_uri = ""
    escaped = True
```

`_escapes_outdir()`'s body (`typsphinx/builder.py:104-112`) is a pure
string operation (`.replace()`, `.split()`, `in`, `posixpath.isabs()`,
the ASCII-shape check in `_is_drive_qualified()`) that cannot raise
`ValueError` for any `str` input, so in practice this is not a live bug —
but the comment at line 915-922 documents this as an intentional "cross-
domain reuse" of a helper whose contract could, in principle, change.
Were `_escapes_outdir()` ever extended to do something that *can* raise
`ValueError` for an unrelated reason (e.g. stricter validation), that
exception would be silently misclassified here as "Windows cross-drive
relpath failure" rather than propagating or being handled on its own
merits, because the `except` clause cannot distinguish which of the two
calls raised.

**Fix:** Narrow the `try` to wrap only the `path.relpath()` call:

```python
try:
    rel_uri = path.relpath(resolved_uri, self.doctreedir).replace(
        path.sep, "/"
    )
except ValueError:
    rel_uri = ""
    escaped = True
else:
    escaped = _escapes_outdir(rel_uri)
```

---

_Reviewed: 2026-08-14T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
