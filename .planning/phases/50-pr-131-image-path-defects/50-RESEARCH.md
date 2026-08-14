# Phase 50: PR #131 Image Path Defects - Research

**Researched:** 2026-08-14
**Domain:** Sphinx image post-processing / filesystem path resolution (`typsphinx/builder.py`)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**IMG-01 — how a converted image is rehomed**
- **D-01:** an absolute URI keeps today's rehome target unless a real source image occupies it.
  `_track_image()` computes `rel_uri` exactly as today, then probes the filesystem for the ordinary-
  image location that `rel_uri` would denote — the join of `srcdir` and `rel_uri`. If nothing is
  there, `rel_uri` is used unchanged. If something is there, the converted image is relocated per D-02
  instead.
- **D-02:** the collision escape hatch is a reserved top-level namespace (`_typst_converted/`), not a
  numeric suffix. Rejected alternative — Sphinx-style suffixing of the basename in the same directory
  — because the winner/loser assignment would then depend on document write order.
- **D-03:** the probe is against the filesystem, never against the accumulated dict. Deciding the
  collision from whether the key is already present in `self.images` reintroduces exactly the
  order-dependence D-02 rejects.
- **D-04:** relocation under D-02 is silent, and is not a warning-worthy event. The IMG-02 escape
  (D-06) does warn; that asymmetry is deliberate.

**IMG-02 — an absolute URI that is not under doctreedir**
- **D-05:** the escape is contained by relocating, not by dropping the image. The relocation target
  is the same reserved namespace D-02 uses. When the rehome result points outside `doctreedir` —
  detected as a leading parent-directory component — the image is tracked under the reserved
  namespace so that `copy_image_files()` still copies it, and every destination it writes lands under
  `outdir`. Rejected alternative — warn and abandon tracking.
- **D-06:** the IMG-02 relocation warns, because it is genuinely anomalous. All three of Sphinx's own
  image post-transforms write under the doctree image directory, so reaching this branch means a
  third-party extension placed an absolute URI somewhere unexpected.
- **D-07:** the cross-drive crash path is closed in the same guard. On Windows, `path.relpath` raises
  `ValueError` when the two paths sit on different drives; that exception is caught and routed into
  the same D-05 relocation.

**Verification obligations**
- **D-08:** the pre-fix RED for IMG-01 is an embedded-image assertion read out of the compiled PDF —
  the single compiled PDF embeds the SAME picture for both documents, and only one of the two files
  was copied into the output tree. `pypdf`/`pillow` are already dev dependencies.
- **D-09:** the two fixture images are discriminated by pixel dimensions, not by raw bytes (Typst
  re-encodes what it embeds).
- **D-10:** the IMG-01 fixture is one master wrapper over two content documents, producing one PDF.
- **D-11:** SC#3's two-build comparison is a one-time recorded measurement, not a new permanent test
  — over `docs/source` and every root under the test roots directory, plain Typst builder (no PDF
  compile needed).
- **D-12:** PR #131's own regression tests are a fixed point and must pass byte-unchanged — the
  emitted-path and copied-asset assertions in `tests/test_absolute_image_render_gate.py`, and the
  rehomed-uri assertion in `tests/test_builder.py`. If an implementation attempt requires editing any
  of them, that is evidence D-01 was violated — escalate to the owner rather than adjusting the
  expected string.

### Claude's Discretion

- The exact spelling of the reserved namespace directory. `_typst_converted/` is the default; a
  different reserved name may be proposed with a rationale, but it must be a single reserved
  top-level component.
- What happens if the reserved namespace path itself collides with a real source directory. A
  second-order guard is welcome but must not reintroduce order-dependence.
- Whether the two defects land as one commit or two, and whether one shared helper or two guards
  express D-01/D-05 in code.
- Whether a debug-level log records a D-02 relocation. D-04 forbids a warning, not a debug line.
- The concrete pixel dimensions and file names used in the D-09 fixture.

### Deferred Ideas (OUT OF SCOPE)

None — the owner declined discussion ("議論ポイント無し") and no new capability was raised. Nothing
here touches `write_doc()`'s composition shape, and content files staying docname-named means
`_compute_relative_image_path()` needs no change at all. This phase is independent of the v0.8.0
composition work (Phases 47-49) and must not pick up any of it.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| IMG-01 | A converted image rehomed to `images/<basename>` no longer collides with a real source image at `<srcdir>/images/<basename>` | Filesystem-probe collision detection (Pattern 1), reserved-namespace relocation (Pattern 3), D-12-pinned-test-preserving branch ordering (Code Examples), D-10 render-gate fixture design (Recommended Project Structure), D-08/D-09 embedded-image pixel-dimension extraction idiom (Code Examples) |
| IMG-02 | An absolute image URI outside `doctreedir` no longer causes `copy_image_files()` to write outside the output directory | Reuse of the existing `_escapes_outdir()` helper (Pattern 2), Windows cross-drive `ValueError` handling (D-07, Pitfall 4), Sphinx 9.1.0 ground-truth confirming stock post-transforms never reach this branch (State of the Art) |
</phase_requirements>

## Summary

This phase closes two defects filed against `TypstBuilder._track_image()`, the code PR #131 itself
introduced. Both are resolvable with in-repo measurement alone — no external library research was
needed, because the fix is a filesystem-probe change to code this project already owns, and every
primitive it needs (`os.path.relpath`, `os.path.isabs`, a filesystem `exists()` check) is stdlib.

**IMG-01** happens because `_track_image()` rehomes a converted image's absolute URI to
`images/<basename>` — the exact same source-root-relative key an ordinary image at
`<srcdir>/images/<basename>` already claims — and both tracking sites guard insertion with
`if <key> not in self.images`, so whichever document writes first wins and the loser is silently
never copied. **IMG-02** happens because `path.relpath(resolved_uri, self.doctreedir)` assumes the
absolute URI lives under `doctreedir`; when a third-party extension places it elsewhere, `relpath`
returns a `../`-prefixed path and `copy_image_files()`'s unconditional `path.join(self.outdir, imguri)`
follows it outside `outdir`.

Both defects are fixed by widening `_track_image()`'s absolute-URI branch with two filesystem-probe
checks, in this order: (1) does the rehomed path escape `doctreedir` (a leading `..` segment, or a
`ValueError` from `relpath` on a Windows cross-drive pair)? — if so, relocate under a reserved
namespace and warn (IMG-02, genuinely anomalous). (2) does a **real** file already exist at
`<srcdir>/<rehomed-path>`? — if so, relocate under the same reserved namespace, silently (IMG-01, an
ordinary and expected shape for any project using an image-conversion extension). Both checks are
against the filesystem, never against `self.images`' own accumulated keys, which is what keeps the
outcome independent of document write order (D-03).

`builder.py` already contains the exact escape-detection shape needed for IMG-02
(`_escapes_outdir()`, `typsphinx/builder.py:63-104`) — it is written for a different call site
(`typst_documents` target validation, OUT-02) but its core test (a leading `..` path segment) is
domain-agnostic string-shape logic and is safe to reuse directly on the rehomed `rel_uri`. `pypdf`
and `pillow` are already declared dev dependencies (`pyproject.toml:46-47`) and pypdf 6.14.2's
`page.images` property (confirmed by introspection this session) returns `ImageFile` objects
carrying a `.image` PIL handle — exactly what D-08/D-09's embedded-image pixel-dimension assertion
needs. No new package, no new `typst_*` config value, and no change to `writer.py`'s composition
shape or `_compute_relative_image_path()` are required.

**Primary recommendation:** widen `_track_image()`'s existing absolute-URI branch with two
filesystem-probe guards (escape-check first, then srcdir-collision-check), route both into the same
`_typst_converted/<rel_uri>` reserved namespace, warn only on the escape case, and leave
`copy_image_files()`'s destination computation (`path.join(self.outdir, imguri)`) completely
untouched — it already lands correctly for both defects once the tracked key never carries a leading
`..`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Image URI collision detection (IMG-01) | Backend / Builder | — | `TypstBuilder._track_image()` is a pure Sphinx-builder-tier concern; no browser, SSR, or CDN tier is involved in this project (it is a docs-to-PDF compiler, not a web app) |
| Outdir-escape containment (IMG-02) | Backend / Builder | — | Same tier and same method; `copy_image_files()`'s destination join is the only "write" boundary this phase touches |
| Compiled-PDF embedded-image assertion (D-08/D-09) | Test / Verification | Backend / Builder | The RED/GREEN proof reads pypdf-extracted image bytes out of a real `typst.compile()` artifact — a verification-tier concern layered on top of the builder-tier fix |

*(This project has no browser/SSR/CDN tiers — it is a Sphinx extension producing `.typ`/`.pdf` files,
not a served application. The table above is complete for this phase's scope.)*

## Package Legitimacy Audit

**No new packages are introduced by this phase.** `pypdf>=6.14,<7` and `pillow>=12.3,<13` are already
declared dev dependencies (`pyproject.toml:46-47`), added in an earlier milestone (ADM-04). Verified
installed and importable this session: `pypdf.__version__ == "6.14.2"`, and `typst.__version__ ==
"0.15.0"` (already a pinned runtime dependency, `pyproject.toml:30`). This section is otherwise N/A —
the Package Legitimacy Gate protocol is scoped to *new* package introductions and none occurs here.

## Standard Stack

No new stack. This phase edits one existing module (`typsphinx/builder.py`) using only Python's
`os.path` stdlib and the two already-present dev dependencies for the new render-gate test.

### Core (unchanged, cited for completeness)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `sphinx` | 9.1.0 (installed, pinned `>=9.1,<10`) | Provides the doctree, `env.doctreedir`, and the `ImageConverter`/`ImageDownloader`/`DataURIExtractor` post-transforms this phase's fix defends against | Already the project's runtime dependency |
| `typst-py` | 0.15.0 (installed, pinned `>=0.15.0,<0.16`) | Real-compile verification for the D-08/D-09 render gate | Already the project's runtime dependency |

### Supporting (dev-only, unchanged)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pypdf` | 6.14.2 (installed, pinned `>=6.14,<7`) | `PdfReader(...).pages[i].images` extracts embedded raster images from the compiled PDF as `ImageFile` objects (`.image` is a PIL handle) — this is the D-08/D-09 extraction mechanism | Compiled-PDF embedded-image assertions |
| `pillow` | (installed via pypdf's own PIL dependency + the project's own `pillow>=12.3,<13` dev pin) | `.image.size` on an extracted `ImageFile` gives `(width, height)` in pixels — the D-09 discriminator | Pixel-dimension comparison between the two fixture images |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Filesystem-probe collision detection (D-01/D-03) | Sphinx-style numeric-suffix de-collision inside `self.images` (the todo's rejected "Solution 2") | Rejected in CONTEXT.md's D-02: winner/loser assignment (and therefore the emitted suffix) would depend on document write order, making output non-reproducible across builds — the opposite of what a filesystem probe gives |
| `_escapes_outdir()` reuse for IMG-02 | A brand-new, image-specific escape-detection helper | Rejected below (see Architecture Patterns) — the existing helper's core test is domain-agnostic and reuse is strictly DRY-preferred per no known downside |
| pypdf `page.images` (D-08) | Render each page to PNG via `typst.compile(..., format="png")` and diff pixels directly (the pattern `test_admonition_greyscale_pipeline.py` already uses) | Rejected: that pattern proves a *rendered page* matches, not that *two named images* were both embedded and are distinguishable — D-09's dimension-discrimination requirement needs per-image extraction, which only pypdf's `page.images` gives |

**Installation:** None required — every dependency this phase touches is already declared.

**Version verification:** confirmed this session by direct interpreter introspection inside the
project's own `.venv` (`uv run python -c "import pypdf; print(pypdf.__version__)"` → `6.14.2`;
`uv run python -c "import sphinx; print(sphinx.__version__)"` → `9.1.0`; `uv run python -c "import
typst; print(typst.__version__)"` → `0.15.0`) — not training-data recollection.

## Architecture Patterns

### System Architecture Diagram

```
 doctree (post-transformed)
        │
        ▼
 TypstBuilder.post_process_images()          [unchanged]
        │  resolves node["candidates"] to one concrete URI
        ▼
 TypstBuilder._track_image(node, resolved_uri)     ◄── THIS PHASE
        │
        ├─ resolved_uri is NOT absolute (ordinary source image)
        │       └─► self.images[resolved_uri] = ""            [unchanged branch]
        │
        └─ resolved_uri IS absolute (converted/downloaded image)
                │
                ▼
          rel_uri = relpath(resolved_uri, doctreedir)   (catch ValueError, D-07)
                │
                ├─ escapes doctreedir? (_escapes_outdir(rel_uri), D-05)──yes─┐
                │         no                                                 │
                │         ▼                                                  │
                │  real file exists at srcdir/rel_uri? (D-01/D-03) ──yes─┐   │
                │         no                                             │   │
                │         ▼                                              ▼   ▼
                │   node["uri"] = rel_uri              node["uri"] = "_typst_converted/" + rel_uri
                │   self.images[rel_uri] = resolved_uri      self.images[key] = resolved_uri
                │   (today's behavior, D-12 pinned)     (D-04 silent for collision, D-06 WARN for escape)
                ▼
     ... write_doc() continues, .typ emits image(node["uri"]) ...
                │
                ▼
 TypstBuilder.copy_image_files()             [unchanged]
        for imguri, override_src in self.images.items():
            src  = override_src or path.join(srcdir, imguri)
            dest = path.join(outdir, imguri)     ◄── never escapes outdir now, because imguri
                                                       never carries a leading ".." (D-05 already
                                                       relocated it under the reserved namespace)
            shutil.copy2(src, dest)
```

### Recommended Project Structure

No new files or directories in `typsphinx/`. One new sibling test fixture directory:

```
tests/
├── test_absolute_image_render_gate.py       # existing — D-12 pinned, untouched
├── test_builder.py                            # existing — two D-12 pinned assertions, untouched
└── fixtures/
    ├── absolute_image_render_gate/             # existing — D-12 pinned, untouched
    └── <new-sibling-fixture>/                  # D-10 — see Code Examples
        ├── conf.py                             # FakeImageConverter post-transform (copied pattern)
        ├── index.rst                           # master, toctree'ing two children
        ├── converted_source.rst                # figures an SVG that "converts" to images/<colliding-name>.png
        ├── real_source.rst                     # figures the REAL srcdir image directly
        └── images/
            └── <colliding-name>.png            # the real source image, at the colliding location
```

### Pattern 1: Filesystem probe, not dict lookup (D-01/D-03)

**What:** Collision detection for IMG-01 must ask "does a real file exist at
`<srcdir>/<rehomed-path>`?" (`os.path.exists`), never "is `<rehomed-path>` already a key in
`self.images`?".

**When to use:** Any time the outcome must not depend on which document happens to be written
first. `write()` iterates `sorted(docnames)` (`typsphinx/builder.py:726`) — the source image and the
converted image can be tracked in either order depending on docname alphabetization, and a
`self.images`-membership check would let the *second* tracked one always relocate regardless of
which one is "really" the collider, producing a result that is at least *deterministic* but is
**not** equivalent to what the filesystem actually contains (e.g. if the converted image happens to
sort first, a `self.images` check would never detect the collision at all, since nothing is in the
dict yet when the converted image is tracked). A filesystem probe gives the same answer regardless of
traversal order — this is D-03's argument, verified structurally correct here: `os.path.exists()` has
no dependency on `self.images`' current contents.

**Example (verified against the installed `os.path`, stdlib):**
```python
# Source: Python stdlib os.path (verified: os.path.exists is a pure
# filesystem query with no dependency on any in-process dict state)
import os.path as path

def _real_source_image_exists(srcdir: str, rel_uri: str) -> bool:
    return path.isfile(path.join(srcdir, rel_uri))
```

### Pattern 2: Reuse `_escapes_outdir()` for the IMG-02 leading-`..` check (D-05)

**What:** `typsphinx/builder.py:63-104` already defines `_escapes_outdir(stem: str) -> bool`:

```python
# Source: typsphinx/builder.py:96-104 (verified: Read this session)
def _escapes_outdir(stem: str) -> bool:
    segments = stem.replace("\\", "/").split("/")
    return ".." in segments or posixpath.isabs(stem) or _is_drive_qualified(stem)
```

Its docstring (`typsphinx/builder.py:63-77`) frames it as a `typst_documents` target-stem guard
(OUT-02), but the function itself takes a plain `str` and returns a plain `bool` — it has no
dependency on `typst_documents`, entries, docnames, or anything OUT-02-specific. Called on the
rehomed `rel_uri` (already forward-slash-normalized by the existing `.replace(path.sep, "/")` at
`typsphinx/builder.py:868`), it correctly answers "does this path try to leave the directory it is
relative to" for the image case too — a `relpath()` result that escapes `doctreedir` is
string-shape-identical to a `typst_documents` target that escapes `outdir`: both are detected by a
leading `..` path segment. `posixpath.isabs(stem)` and `_is_drive_qualified(stem)` will structurally
never trigger for an image `rel_uri` (a `relpath()` return value is never absolute or drive-qualified
by construction), so reusing the function adds zero false-positive surface versus writing a
narrower, image-specific `".." in rel_uri.split("/")` check by hand.

**Recommendation: reuse `_escapes_outdir()` directly**, called as `_escapes_outdir(rel_uri)` inside
`_track_image()`. Reasons to prefer reuse over a new helper: (a) it is the single existing
source-of-truth for "does this relative path escape its base directory" in this module, and this
module's own `_collision_key()` docstring (`typsphinx/builder.py:414-492`) already establishes the
convention of consolidating a check used by more than one call site into one named function rather
than letting two call sites drift; (b) the function is a pure string-shape test with no
`typst_documents`-specific state threaded through it, so calling it from `_track_image()` introduces
no coupling to unrelated config; (c) it is already unit-tested (indirectly, via the OUT-02 gate) for
every shape this phase needs (`..` segment, leading `/`, drive letter). The one caveat to record for
the planner: if `_escapes_outdir()`'s contract is ever narrowed to something OUT-02-specific in a
later phase, this call site would need to be re-evaluated — a one-line comment at the new call site
noting the cross-domain reuse is worth adding.

### Pattern 3: The reserved namespace, and its collision-implausibility precedent (D-02, discretion item 2)

**What:** `_typst_converted/` (the filed todo's proposed name) is confirmed as the right choice, with
two independent precedents found this session, neither present in the todo:

1. **This project's own convention.** `typsphinx/builder.py:1086` already writes a reserved
   infrastructure file at the outdir root named `_template.typ` — a leading underscore already marks
   "this name is owned by typsphinx, not by the user's source tree" in this codebase.
2. **Sphinx's own convention.** The installed Sphinx 9.1.0 HTML builder reserves `_images` as its own
   image output directory (`sphinx/builders/html/__init__.py:165`: `self.imagedir = '_images'`) and
   `_static`/`_sources` follow the same leading-underscore pattern project-wide. A leading underscore
   at the top level of a Sphinx output/source tree is an established, widely-recognized reservation
   marker, not a typsphinx-only invention.

**Recommendation:** keep `_typst_converted/` unchanged from the todo's default. No rationale to
deviate — the leading underscore already carries meaning both to this codebase's own maintainers and
to anyone familiar with Sphinx's own `_static`/`_images` convention.

### Pattern 4: Second-order collision guard (D-05/discretion item 3)

**What:** if a real source directory *also* exists at `<srcdir>/_typst_converted/...`, relocating
under the reserved namespace does not actually escape the collision — a second, much rarer collision
is possible.

**Recommendation (discretionary, offered with rationale, not mandatory):** apply the *same* D-01
filesystem probe recursively — after computing the candidate `_typst_converted/<rel_uri>` key, probe
`path.isfile(path.join(srcdir, "_typst_converted", rel_uri))`. If that too is occupied, this is now a
double-improbable event: a project using an image-conversion extension AND happening to keep a real
source asset at the exact same relative path under a directory named after this project's own
reserved namespace. Two options that both respect D-03 (no order-dependence):

- **Minimal (recommended):** do nothing further — accept the residual, doubly-improbable collision as
  an unclosed edge, matching this project's own precedent of treating implausible compound
  collisions as out of scope until measured to actually occur (e.g. `_template.typ` itself has no
  runtime guard against a docname literally being `_template`). Document the limitation in the
  planner's chosen commit/PR description; do not add code for it.
- **If the planner wants a closed guard anyway:** disambiguate deterministically from the *content* of
  the collision, not from write order — e.g. append a short hash of `resolved_uri` (the true absolute
  source path) to the reserved-namespace key:
  `_typst_converted/<dirname>/<sha1(resolved_uri)[:8]>-<basename>`. This is a pure function of
  `resolved_uri` alone, so two independent builds of the same project produce the identical key
  regardless of traversal order — it does not reintroduce D-03's rejected order-dependence, because
  nothing about *when* the image is tracked feeds into the hash.

Given the compound-improbability, the **Minimal** option is the recommendation; the hashed fallback
is offered only if the planner's own risk tolerance differs.

### Anti-Patterns to Avoid

- **Checking `self.images` membership to detect the IMG-01 collision.** This is the exact defect
  D-02/D-03 close — see Pattern 1. Do not add a `if rel_uri in self.images and self.images[rel_uri]
  != resolved_uri:` branch; it silently depends on write order.
- **Warning on the IMG-01 relocation.** D-04 is explicit: an ordinary `images/` srcdir layout
  colliding with a converted image's rehome target is common and expected once an image-conversion
  extension is in use — warning here would be noise on every affected project's every build. Only the
  IMG-02 escape case warns (D-06), because it can only be reached via a non-standard third-party
  extension (verified this session — see State of the Art below).
- **Editing any of the three D-12-pinned assertions to make a new approach pass.** If an
  implementation attempt requires touching `tests/test_absolute_image_render_gate.py`'s emitted-path
  or copied-asset assertions, or `tests/test_builder.py`'s
  `test_post_process_images_rehomes_absolute_uri` rehomed-uri string, that is evidence D-01 was
  violated (the common, non-colliding case must resolve to the unchanged `rel_uri`) — escalate to the
  owner per CONTEXT.md's binding instruction, do not adjust the expected string.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| "Does this relative path try to escape its base directory" | A new image-specific `..`-segment scanner | The existing `_escapes_outdir()` (`typsphinx/builder.py:96-104`) | Same string-shape question, already correct and tested for every case this phase needs — see Pattern 2 |
| "Extract an embedded image from a compiled PDF" | A hand-rolled PDF-stream parser, or `pdftoppm`/`pdfimages` subprocess shelling | `pypdf.PdfReader(...).pages[i].images` (returns `ImageFile` with a `.image` PIL handle) | Already a dev dependency; `.image.size` gives exactly the `(width, height)` D-09 needs with zero new machinery |
| "Reproduce a real image-conversion post-transform for a test fixture, without an external converter binary" | A new fake-converter transform class | Copy `tests/fixtures/absolute_image_render_gate/conf.py`'s existing `FakeImageConverter` (`SphinxTransform` subclass, `default_priority = 200`) | Already proven correct against this exact mechanism (Issue #130's own render gate); D-10's sibling fixture needs the identical shape with a second content document added |

**Key insight:** every mechanism this phase needs — path-escape detection, PDF embedded-image
extraction, and fake-converter fixture construction — already exists somewhere in this repository or
its already-declared dependencies. The work is entirely "compose existing primitives correctly, with
a filesystem probe instead of a dict-order check," not "invent a new mechanism."

## Common Pitfalls

### Pitfall 1: Reading `_track_image()`'s absolute-URI branch as "the only place a collision can be
introduced"

**What goes wrong:** A fix that only guards the absolute-URI branch (where the converted image is
tracked) but does not consider that the *ordinary* branch (`self.images[resolved_uri] = ""` at
`typsphinx/builder.py:875-876`) already ran first for the real source image, silently succeeds either
way — **but only because the ordinary branch is genuinely unconditional and untouched.** The risk is
in the other direction: a planner might be tempted to also add a guard to the ordinary branch
("what if two ordinary images collide with each other") — that is a different, non-existent problem
(two ordinary images at the same source-relative path are the same physical file by construction) and
is out of this phase's two requirement IDs.

**Why it happens:** the two `if <key> not in self.images` guards look symmetric in the source, inviting
a symmetric fix.

**How to avoid:** confine the fix to the absolute-URI branch only, per D-01/D-05's own framing ("the
probe is against the filesystem location the rehome would target" — always the *converted* image's
candidate key, checked against a *real source* image, never the reverse).

**Warning signs:** a diff that touches the `if resolved_uri not in self.images: self.images[resolved_uri]
= ""` line (`typsphinx/builder.py:875-876`) is almost certainly out of scope.

### Pitfall 2: Assuming `relpath()`'s escape shape is always a single `../` prefix

**What goes wrong:** The todo's own measured table (`.planning/todos/pending/2026-08-10-track-image-
rehome-escapes-outdir-for-non-doctreedir-abs-uri.md`) shows a case with **three** leading `../../../`
segments (`/tmp/generated/chart.png` relative to a `doctreedir` several levels deep). A check that
only looks for a *single* leading `..` (e.g. `rel_uri.startswith("..")` without splitting on `/`)
would still work for this case too since `"..".startswith("..")` covers any repeat count — but a
check that looks for `.. ` *anywhere in the string* rather than as a path *segment* could
false-positive on a legitimately named directory containing literal dots (e.g. `images/v1..2/`).
`_escapes_outdir()` already gets this right (splits on `/` first, checks segment membership, not
substring), which is a second reason to reuse it (Pattern 2) rather than hand-write a narrower
check.

**Why it happens:** `path.relpath()`'s escape shape is proportional to directory nesting depth, not
fixed at one `../`.

**How to avoid:** reuse `_escapes_outdir()`, which already handles arbitrary-depth escapes correctly
via segment splitting.

**Warning signs:** a regex or substring check against `"../"` rather than a segment-based check.

### Pitfall 3: `pypdf`'s `page.images` ordering is not guaranteed to match doctree order

**What goes wrong:** D-10's fixture produces one PDF containing two images (one converted stand-in,
one real source image, deliberately different pixel dimensions per D-09). A test that asserts
`page.images[0].image.size == <converted-dims>` and `page.images[1].image.size == <source-dims>` by
positional index is fragile — pypdf's extraction order follows the PDF's internal XObject
enumeration order, which is a function of Typst's own PDF-writer internals, not necessarily the
doctree's visual top-to-bottom order.

**Why it happens:** PDF embedded-resource ordering is an implementation detail of the PDF writer, not
part of the PDF content stream's visual layout.

**How to avoid:** assert on the **set** of extracted `(width, height)` pairs across all pages (e.g. `{
img.image.size for page in reader.pages for img in page.images }`), matching D-10's own framing:
"that list holds one picture, or the same picture twice" (pre-fix RED) vs. "two distinctly-sized
pictures" (post-fix GREEN) — a set/count comparison, not a positional one.

**Warning signs:** `page.images[N]` indexed by a fixed literal `N` in a new test.

### Pitfall 4: Forgetting the `path.relpath()` `ValueError` (D-07) has to wrap the *entire* absolute-URI branch, not just the new guard logic

**What goes wrong:** `rel_uri = path.relpath(resolved_uri, self.doctreedir)` is the very first
statement of today's absolute-URI branch (`typsphinx/builder.py:868`). If the new escape-guard logic
is inserted *after* this line without wrapping the `relpath()` call itself in a `try/except
ValueError`, the Windows cross-drive crash (D-07) is never actually closed — it still raises before
any new guard code runs.

**Why it happens:** it is easy to read D-05/D-06/D-07 as three sequential guards added *after* the
existing rehome computation, when D-07 specifically requires catching an exception thrown *during*
that computation.

**How to avoid:** wrap the `path.relpath(...)` call itself in `try: ... except ValueError: <treat as
IMG-02 escape>`, matching the todo's own framing ("捕捉しておくと Windows のクラッシュ経路も塞げる" —
catch it so the Windows crash path is also closed) and D-07's "routed into the same D-05 relocation."

**Warning signs:** a `try/except` block that starts after `rel_uri = path.relpath(...)` rather than
around it.

## Code Examples

### `_track_image()`'s absolute-URI branch, with both guards composed (illustrative — not literal
plan text; the planner owns the final shape and whether the two guards are one shared helper or two)

```python
# Source: typsphinx/builder.py:840-876 (verified: Read this session), extended per
# D-01/D-03/D-05/D-06/D-07. RESERVED_IMAGE_NAMESPACE = "_typst_converted" per D-02.
def _track_image(self, node: nodes.image, resolved_uri: str) -> None:
    if path.isabs(resolved_uri):
        try:
            rel_uri = path.relpath(resolved_uri, self.doctreedir).replace(path.sep, "/")
        except ValueError:
            # D-07: Windows cross-drive relpath() crash -- treat identically
            # to an escape (there is no meaningful doctreedir-relative path
            # to compute at all).
            rel_uri = None

        if rel_uri is None or _escapes_outdir(rel_uri):
            # D-05/D-06: rehome result points outside doctreedir (or could
            # not be computed at all) -- relocate under the reserved
            # namespace and WARN, because reaching this branch means a
            # third-party extension placed an absolute URI somewhere none
            # of Sphinx's own post-transforms ever do.
            fallback_source = rel_uri if rel_uri is not None else resolved_uri
            key = f"{RESERVED_IMAGE_NAMESPACE}/{posixpath.basename(fallback_source)}"
            logger.warning(
                f"could not rehome image URI {resolved_uri!r} relative to "
                "the doctree directory -- relocated to a reserved namespace"
            )
        elif path.isfile(path.join(self.srcdir, rel_uri)):
            # D-01/D-03/D-04: a REAL source image already occupies the
            # target this rehome would produce -- relocate under the same
            # reserved namespace, SILENTLY (an ordinary, expected shape for
            # any project combining an images/ srcdir layout with an
            # image-conversion extension).
            key = f"{RESERVED_IMAGE_NAMESPACE}/{rel_uri}"
        else:
            # D-01: no collision -- today's behavior and today's emitted
            # path are preserved unchanged. This is the branch the three
            # D-12-pinned test assertions all exercise.
            key = rel_uri

        node["uri"] = key
        if key not in self.images:
            self.images[key] = resolved_uri
        return

    # Store empty string as value to be compatible with parent class type
    if resolved_uri not in self.images:
        self.images[resolved_uri] = ""
```

### D-08/D-09 embedded-image pixel-dimension extraction idiom (new pattern this phase introduces)

```python
# Source: pypdf 6.14.2's ImageFile dataclass (verified: introspected via
# `inspect.getsource(pypdf._page.ImageFile)` this session -- .image is
# Optional[PIL.Image.Image], .data is bytes, .name is str). Combined with
# the repository's existing pypdf-extraction idiom
# (tests/test_pdf_render_gate.py:265-266's
# `reader = pypdf.PdfReader(str(pdf_output))`).
import pypdf

reader = pypdf.PdfReader(str(pdf_output))
extracted_sizes = {
    image_file.image.size  # (width, height) in pixels
    for page in reader.pages
    for image_file in page.images
    if image_file.image is not None
}

# Pre-fix RED (D-10): only one distinct size present (or the images list is
# shorter than expected) -- one of the two source assets was never copied,
# or both documents embed the SAME picture.
# Post-fix GREEN: both fixture-chosen pixel dimensions (D-09) are present.
assert extracted_sizes == {CONVERTED_STANDIN_DIMS, REAL_SOURCE_DIMS}
```

### The existing structural + pypdf render-gate idiom to copy (D-08's "structural .typ assertion
combined with pypdf extraction")

```python
# Source: tests/test_pdf_render_gate.py:244-266 (verified: Read this
# session) -- the repository's established two-half pattern: (1) a
# structural assertion over the emitted .typ BEFORE compiling, (2) a real
# typst.compile() + pypdf extraction AFTER.
result = subprocess.run(
    [sys.executable, "-m", "sphinx", "-b", "typst", str(source_dir), str(build_dir)],
    capture_output=True, text=True,
)
assert result.returncode == 0, f"sphinx-build failed:\n{result.stdout}\n{result.stderr}"

index_typ = build_dir / "index.typ"
assert index_typ.exists()
typ_source = index_typ.read_text()
# ... structural assertion over typ_source here (e.g. two DIFFERENT
# image(...) calls, per SC#1's "identical path" pre-fix RED) ...

wrapper_typ = build_dir / "master.typ"  # Phase 47: only wrappers compile
pdf_output = build_dir / "master.pdf"
typst.compile(str(wrapper_typ), output=str(pdf_output))

assert pdf_output.exists() and pdf_output.stat().st_size > 0
with open(pdf_output, "rb") as f:
    assert f.read(4) == b"%PDF"

reader = pypdf.PdfReader(str(pdf_output))
# ... embedded-image extraction (see idiom above) or full_text = "\n".join(
#     page.extract_text() for page in reader.pages) for a text-based gate ...
```

## State of the Art

| Old Approach (pre-PR-131) | Current Approach (PR #131, pre-Phase-50) | Post-Phase-50 | Impact |
|--------------|------------------|------------------|--------|
| Absolute converted-image URI used unmodified in `os.path.join(srcdir_or_outdir, uri)` | Same absolute URI rehomed to `doctreedir`-relative `images/<basename>`, tracked with dict-order-dependent `not in` guard | Same rehome, but gated by two filesystem probes before the key is finalized | Pre-PR-131: `os.path.join` silently discards its first arg once `uri` is absolute → `src == dest`, build **aborts loudly** (Issue #130). PR #131: build succeeds but **silently drops one image** on a collision, and can **write outside `outdir`** on an escape. Phase 50: both silent-failure shapes close without reintroducing the loud-abort regression |

**Deprecated/outdated:** none — this phase does not remove any capability, only widens one method's
guard logic.

**Sphinx 9.1.0 ground truth (verified this session by reading the installed source, per requirement
#6):**

- `BaseImageConverter.imagedir` returns `self.env.doctreedir / 'images'`
  (`sphinx/transforms/post_transforms/images.py:46-48`, exact source:
  `return self.env.doctreedir / 'images'`) — this is why the IMG-01 collision key is `images/<basename>`.
- `DataURIExtractor.handle()` writes under an `embeded` subdirectory of that same directory
  (`sphinx/transforms/post_transforms/images.py:147,149`: `ensuredir(self.imagedir / 'embeded')` then
  `path = self.imagedir / 'embeded' / (digest + ext)`) — note the upstream misspelling "embeded" is
  verbatim in the installed Sphinx source, not a transcription error in this document.
- `ImageConverter.handle()` takes its output filename from `self.env.images[srcpath][1]`
  (`sphinx/transforms/post_transforms/images.py:267`) and registers its own destination via
  `self.env.images.add_file(...)` (`sphinx/transforms/post_transforms/images.py:281`).
  `env.images` is a `sphinx.util._files.FilenameUniqDict`
  (`sphinx/util/_files.py:14-41`, verified: `Read` this session), whose `add_file()` de-collides two
  identically-named destinations by appending a numeric suffix drawn from an internal `_existing` set
  (`sphinx/util/_files.py:36-38`: `while unique_name in self._existing: i += 1; unique_name =
  f'{base}{i}{ext}'`) — **confirming converted-vs-converted collisions are already closed by Sphinx
  itself**, before `_track_image()` ever sees the URI. This phase's D-01 probe therefore only ever
  needs to consider converted-vs-source, matching CONTEXT.md's framing exactly.
- All three of Sphinx's own image post-transforms (`ImageDownloader`, `DataURIExtractor`,
  `ImageConverter`) write under `self.imagedir` (`<doctreedir>/images`) or its `embeded/` subdirectory
  — never outside `doctreedir`. This corroborates the todos' own "到達性は低い" (low reachability)
  framing for IMG-02: reaching that branch through stock Sphinx alone is not possible; it requires a
  third-party extension that writes an absolute URI somewhere else, which is exactly why D-06 treats
  it as "genuinely anomalous" and warns, in contrast to D-04's silent IMG-01 relocation.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The second-order reserved-namespace collision guard (Pattern 4) is safe to leave unguarded (Minimal option) given its compound improbability | Architecture Patterns, Pattern 4 | If a real project genuinely hits this double collision, the same silent-loser failure mode IMG-01 fixes would recur one level down — low likelihood, explicitly flagged as discretionary in CONTEXT.md, and the hashed fallback is offered as a documented alternative |

**All other claims in this research were verified this session** — either by `Read`-ing the source
file directly (`typsphinx/builder.py`, the installed Sphinx 9.1.0 source, the two todo files, the
pinned test files, `pyproject.toml`), or by interpreter introspection inside the project's own `.venv`
(`pypdf.__version__`, `pypdf._page.ImageFile`'s dataclass fields, `sphinx.__version__`,
`typst.__version__`). No package name, API shape, or file/line claim in this document is drawn from
training-data recollection alone.

## Open Questions (RESOLVED)

None outstanding. All seven items CONTEXT.md's "Claude's Discretion" / "the researcher should
measure this" list handed to this research were closed by direct measurement above:

1. **`builder.py`'s existing escape-detection helper** — `_escapes_outdir()`
   (`typsphinx/builder.py:63-104`), reuse recommended (Pattern 2).
2. **Reserved namespace spelling** — `_typst_converted/` confirmed, with two independent precedents
   found (Pattern 3).
3. **Second-order collision guard** — Minimal (no guard) recommended, hashed fallback offered
   (Pattern 4); logged as A1 above since it is a judgment call, not a measured fact.
4. **pypdf/pillow embedded-image extraction pattern** — no prior test in this repo combines pypdf
   embedded-image extraction (`page.images`) with Pillow; the closest existing pattern
   (`tests/test_admonition_greyscale_pipeline.py`) extracts from a rendered PNG, not a compiled PDF's
   embedded XObjects. This phase introduces the `page.images` idiom fresh (Code Examples), while
   reusing the repository's established structural-assertion + `typst.compile()` + `pypdf.PdfReader`
   scaffolding verbatim from `tests/test_pdf_render_gate.py:244-266`. `pypdf`/`pillow` confirmed as
   dev dependencies (`pyproject.toml:46-47`).
5. **D-10 fixture shape** — worked out concretely in Recommended Project Structure and Pattern 3
   (`FakeImageConverter` copied from `tests/fixtures/absolute_image_render_gate/conf.py`, extended
   with a second content document and a real colliding source image).
6. **Sphinx 9.1.0 ground truth** — verified with file:line citations in State of the Art.
7. **D-11 two-build comparison mechanics** — see Validation Architecture below.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `typst-py` | D-08/D-09/D-10 render-gate compile step | ✓ | 0.15.0 | — |
| `pypdf` | D-08/D-09 embedded-image extraction | ✓ | 6.14.2 | — |
| `pillow` | D-09 pixel-dimension access via `ImageFile.image.size` | ✓ (transitively via pypdf's own PIL usage, and the project's own `pillow>=12.3,<13` dev pin) | 12.x | — |
| NixOS sandbox `sys.executable -m sphinx` invocation | D-10/D-11 subprocess builds | ✓ (standing project convention, `CLAUDE.md`) | — | — |

**Missing dependencies with no fallback:** none.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (config in `pyproject.toml`, per `CLAUDE.md`) |
| Config file | `pyproject.toml` |
| Quick run command | `uv run pytest tests/test_builder.py tests/test_absolute_image_render_gate.py -x` |
| Full suite command | `uv run pytest` (or `uv run pytest --cov=typsphinx --cov-report=term-missing`) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| IMG-01 | Rehomed converted image no longer collides with a real source image of the same basename; both copied, both documents render their own picture | render-gate (structural `.typ` + pypdf embedded-image extraction) | `uv run pytest tests/test_<new-sibling-fixture>_gate.py -x` | ❌ Wave 0 — new sibling fixture (D-10) |
| IMG-01 (unit) | `_track_image()` relocates on filesystem collision, silently | unit | `uv run pytest tests/test_builder.py -k rehome -x` | ❌ Wave 0 — new unit test(s); existing `test_post_process_images_rehomes_absolute_uri` stays pinned (D-12), a NEW test covers the collision branch |
| IMG-02 | Absolute URI outside `doctreedir` never escapes `outdir`; every written destination lands inside `outdir` | unit + render-gate | `uv run pytest tests/test_builder.py -k escape -x` | ❌ Wave 0 — new unit test(s) for the escape branch and the D-07 `ValueError` catch |
| SC#3 (no collateral change) | Two-build byte-identical destination comparison over `docs/source` and `tests/roots/test-basic` | one-time recorded measurement, NOT a standing test (D-11) | see D-11 mechanics below | N/A — not a pytest file |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_builder.py tests/test_absolute_image_render_gate.py -x`
- **Per wave merge:** `uv run pytest`
- **Phase gate:** Full suite green, plus `black --check .` / `ruff check .` / `mypy typsphinx/`
  (matching CI exactly, per `CLAUDE.md`), before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] New sibling fixture directory under `tests/fixtures/` for D-10 (name TBD by the planner; must
      not reuse or mutate `tests/fixtures/absolute_image_render_gate/`, per D-12) — `conf.py` with a
      `FakeImageConverter` post-transform copied from the existing fixture's pattern, `index.rst` as
      master toctree'ing two content documents, one real source image at the colliding location, two
      distinctly-dimensioned PNGs (D-09).
- [ ] New test module (or extension of `tests/test_absolute_image_render_gate.py`'s sibling —
      planner's choice) driving the D-10 fixture through `-b typstpdf`, asserting the structural
      pre-fix RED (one copied file, or two identical `image(...)` calls) and the post-fix GREEN
      (`extracted_sizes == {dims_a, dims_b}`, per the Code Examples idiom above).
- [ ] New unit test(s) in `tests/test_builder.py` for `_track_image()`'s two new branches
      (srcdir-collision relocation, escape relocation + warning, D-07's `ValueError` catch) —
      additive; the two existing D-12-pinned tests in this file must NOT be edited.
- [ ] D-11's one-time before/after manifest recording is NOT a pytest file — see mechanics below.

### D-11 Two-Build Comparison Mechanics (one-time recorded measurement, not a standing test)

Respecting `CLAUDE.md`'s NixOS constraint (`sys.executable -m sphinx`, never a bare `sphinx-build`,
always `uv run` inside the provisioned worktree):

```bash
# 1. BEFORE any code change (first task of the plan, run inside the
#    provisioned worktree, before touching typsphinx/builder.py):
env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev
uv run python -m sphinx -b typst docs/source /tmp/img50-before/docs-source
uv run python -m sphinx -b typst tests/roots/test-basic /tmp/img50-before/test-basic
find /tmp/img50-before -type f -exec sha256sum {} \; \
  | sed 's#/tmp/img50-before/##' | sort > /tmp/img50-before-manifest.txt

# 2. Implement the IMG-01/IMG-02 fix.

# 3. AFTER the fix (same worktree, same environment):
uv run python -m sphinx -b typst docs/source /tmp/img50-after/docs-source
uv run python -m sphinx -b typst tests/roots/test-basic /tmp/img50-after/test-basic
find /tmp/img50-after -type f -exec sha256sum {} \; \
  | sed 's#/tmp/img50-after/##' | sort > /tmp/img50-after-manifest.txt

# 4. Compare -- expect ZERO diff (byte-identical destinations, SC#3):
diff /tmp/img50-before-manifest.txt /tmp/img50-after-manifest.txt
```

`docs/source` is confirmed (this session) to contain at least one ordinary `.. figure::` reference
(`docs/source/examples/basic.rst:128`, `_static/diagram.png`) that exercises `copy_image_files()`'s
unchanged ordinary-image path. `tests/roots/test-basic` is the repository's only root under
`tests/roots/` (confirmed this session: `ls tests/roots/` → `test-basic` alone) and contains no image
references at all, so its manifest comparison is a lighter-weight structural control (proving the
non-image `.typ` output is untouched) rather than an image-destination proof — both are worth running
per D-11's literal instruction ("over the project docs source tree and over every root under the test
roots directory"). `-b typst` (not `-b typstpdf`) is correct per D-11: "destinations are what is
compared, so no PDF compile is needed." Record the `diff` output (expected empty) plus both manifest
files as phase evidence — this is a one-time recorded measurement, not a new pytest module.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | The IMG-02 fix IS an input-validation/path-traversal-containment control: an absolute image URI supplied by a third-party Sphinx extension (untrusted relative to this builder's own assumptions) must never cause a write outside `outdir`. `_escapes_outdir()`'s reuse (Pattern 2) is the validation mechanism |
| V12 File and Resources | yes | `copy_image_files()`'s `shutil.copy2(src, dest)` is a file-write operation whose destination must stay contained within `outdir` — exactly what D-05's relocation guarantees before any copy is attempted |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via a `../`-prefixed relative path escaping an intended output root (IMG-02) | Tampering / Information Disclosure (a write outside `outdir` could overwrite an unrelated file in the user's project tree) | Detect the escape shape before ever computing a destination path (D-05's relocation, reusing `_escapes_outdir()`), never after — the existing `_validate_output_path_collisions()` method (`typsphinx/builder.py:494-605`) is this project's own established precedent for "validate before any write occurs" |
| Windows cross-drive `ValueError` crash treated as a denial-of-service surface (D-07) | Denial of Service (an unhandled exception aborts the entire build) | Catch the specific `ValueError` `os.path.relpath` raises for a cross-drive pair and route it into the same contained-relocation path, rather than letting it propagate uncaught |

This phase does not touch authentication, session management, or cryptography (V2/V3/V6 N/A — this
is a local, offline Sphinx builder with no network or credential surface).

## Sources

### Primary (HIGH confidence — verified this session via `Read` or direct interpreter introspection)
- `typsphinx/builder.py` (full file, this session) — `_track_image()`, `copy_image_files()`,
  `_escapes_outdir()`, `_is_drive_qualified()`, `_collision_key()`, `_validate_output_path_collisions()`
- `sphinx/transforms/post_transforms/images.py` (installed Sphinx 9.1.0, this session) —
  `BaseImageConverter.imagedir`, `DataURIExtractor.handle()`, `ImageConverter.handle()`
- `sphinx/util/_files.py` (installed Sphinx 9.1.0, this session) — `FilenameUniqDict.add_file()`
- `sphinx/builders/html/__init__.py` (installed Sphinx 9.1.0, this session) — `self.imagedir = '_images'`
  precedent
- `tests/test_absolute_image_render_gate.py`, `tests/fixtures/absolute_image_render_gate/conf.py`,
  `tests/fixtures/absolute_image_render_gate/index.rst` (this session) — the fixture pattern to copy
  for D-10
- `tests/test_builder.py:392-459` (this session) — the two D-12-pinned assertions
- `tests/test_pdf_render_gate.py:244-266` (this session) — the established structural + pypdf
  extraction idiom
- `tests/test_admonition_greyscale_pipeline.py` (this session) — confirmed as a DIFFERENT pattern
  (PNG-render, not PDF-embedded-image extraction), not directly reusable for D-08/D-09
- `pyproject.toml:27-48` (this session) — dependency pins, including `pypdf>=6.14,<7` and
  `pillow>=12.3,<13`
- Interpreter introspection this session (`uv run python -c "..."`) — `pypdf.__version__` = 6.14.2,
  `sphinx.__version__` = 9.1.0, `typst.__version__` = 0.15.0, and `pypdf._page.ImageFile`'s dataclass
  source (`data`, `image`, `indirect_reference`, `is_inline`, `is_displayed`, `name`, `replace`)
- `.planning/todos/pending/2026-08-10-rehomed-converted-image-collides-with-srcdir-images-dir.md` and
  `.planning/todos/pending/2026-08-10-track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri.md`
  (this session) — the original measured probe data (73-byte source / 68-byte converted image;
  `Copying 1 image file(s)`; the three-case `relpath` escape table)
- `.planning/ROADMAP.md:345-410` (this session) — binding constraints #4 (GATE-01 non-fatal
  amendment) and #6 (no laundered gates), #7 (zero new runtime deps)
- `.planning/phases/50-pr-131-image-path-defects/50-CONTEXT.md` (this session) — the locked D-01
  through D-12 decisions this research measures against, not re-derives

### Secondary (MEDIUM confidence)
- None — every claim in this document traces to a Primary source above.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH — no new packages; every version verified by interpreter introspection this
  session, not recollection.
- Architecture: HIGH — every code pattern traces to a file:line citation read this session; the fix
  shape is a direct, verified consequence of D-01 through D-12 (already locked in CONTEXT.md) plus
  the measured existing helper (`_escapes_outdir()`).
- Pitfalls: HIGH — Pitfalls 1, 2, and 4 are derived directly from reading the exact code this phase
  edits; Pitfall 3 (pypdf `page.images` ordering) is a reasoned caution about a newly-introduced
  extraction idiom, flagged accordingly rather than presented as a measured failure.

**Research date:** 2026-08-14
**Valid until:** 30 days (stable, code-only domain; no external ecosystem drift risk — the only
version-sensitive claims are pinned dev/runtime dependencies already locked in `pyproject.toml`)
