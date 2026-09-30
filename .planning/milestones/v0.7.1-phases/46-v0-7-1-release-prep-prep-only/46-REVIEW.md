---
phase: 46-v0-7-1-release-prep-prep-only
reviewed: 2026-08-11T00:00:00Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - CHANGELOG.md
  - README.md
  - docs/source/changelog.rst
  - pyproject.toml
  - tests/fixtures/absolute_image_render_gate/_static/converted_stand_in.png
  - tests/fixtures/absolute_image_render_gate/_static/diagram.svg
  - tests/fixtures/absolute_image_render_gate/conf.py
  - tests/fixtures/absolute_image_render_gate/index.rst
  - tests/test_absolute_image_render_gate.py
  - tests/test_builder.py
  - tests/test_changelog_page_gate.py
  - tests/test_docs_contract_claims_gate.py
  - tests/test_toolchain_config_gate.py
  - typsphinx/builder.py
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 46: Code Review Report

**Reviewed:** 2026-08-11
**Depth:** standard
**Files Reviewed:** 13 (+ 1 excluded as a generated artifact, see Scope note)
**Status:** issues_found

## Scope note

Per the phase's own scope note, this diff has two distinct owners:

- **Phase 46's own edits** — `CHANGELOG.md`, `docs/source/changelog.rst`, `pyproject.toml`
  (version bump only), `README.md`, and small edits to three pre-existing gate modules
  (`tests/test_docs_contract_claims_gate.py`, `tests/test_toolchain_config_gate.py`,
  `tests/test_changelog_page_gate.py`).
- **Merged-in via `origin/main` (PR #131, Issue #130, @christianwehe)** — `typsphinx/builder.py`
  (the `_track_image()` helper and its two call sites), `tests/test_builder.py` (two new
  tests), `tests/test_absolute_image_render_gate.py`, and the
  `tests/fixtures/absolute_image_render_gate/` fixture tree. These are reviewed as
  newly-integrated code and each finding below is labelled with its owning change set.

`uv.lock` (239KB) was excluded from scope as a generated artifact, per the workflow's
`files` list (it was not included there).

I verified the diff against the stated `diff_base` with `git diff --stat` /
`git diff -- <file>` for every file below before reviewing, to confirm exactly which
lines belong to Phase 46 vs. the PR #131 merge, and cross-checked several factual claims
(`make_filename_from_project`, Sphinx's real `ImageConverter`/`ImageDownloader`
`imagedir` property, the CI OS matrix) against the installed Sphinx 9.1 source and
`.github/workflows/ci.yml` rather than trusting the prose.

## Summary

Phase 46's own diff (CHANGELOG, README, changelog.rst migration guide, version bump, and
the three gate-module edits) is accurate on every claim I could mechanically verify:
`make_filename_from_project("Quickstart Default Gate")` really does produce
`quickstartdefaultgate` as the CHANGELOG's worked example states, the version/date/links
are internally consistent, and the two `raise ... from e` fixes in
`test_toolchain_config_gate.py` are genuine (if small) quality improvements. No blockers
found in Phase 46's own edits.

The merged-in PR #131 fix (`typsphinx/builder.py`'s `_track_image()`) correctly solves
the specific "are the same file" / "file not found" bug it targets, and the new
`test_absolute_image_render_gate.py` real-compile gate is a solid, well-reasoned
regression test. However, the fix introduces an un-guarded path-collision hazard between
a rehomed converted/downloaded image and an ordinary user image that happens to share the
same `doctreedir`-relative path string — this can silently substitute the wrong image
content with no warning and is not covered by any test. See WR-01/WR-02 below.

The release-prep gate modules also have two minor, pre-existing quality gaps that Phase
46 touched but did not resolve: a stale exclusion rationale in
`test_docs_contract_claims_gate.py` (WR-03) and a comment/data mismatch in
`test_changelog_page_gate.py` (IN-02) that Phase 46's edit updated the numbers on without
correcting the underlying inaccuracy.

## Warnings

### WR-01: Rehomed absolute image path can silently collide with an unrelated ordinary image, swapping content with no warning

**File:** `typsphinx/builder.py:522-558` (`_track_image`), `typsphinx/builder.py:677-713`
(`copy_image_files`) — **owner: PR #131 merge, newly-integrated code**

**Issue:** `_track_image()` rehomes an absolute image URI (from
`ImageConverter`/`ImageDownloader`) to a path relative to `self.doctreedir`, e.g.
`"images/diagram.png"`, and records the true absolute source only the *first* time that
relative key is seen:

```python
if path.isabs(resolved_uri):
    rel_uri = path.relpath(resolved_uri, self.doctreedir).replace(path.sep, "/")
    node["uri"] = rel_uri
    if rel_uri not in self.images:
        self.images[rel_uri] = resolved_uri
    return
```

The rehomed namespace (`"images/<basename>"`) is not guaranteed disjoint from the
namespace ordinary, non-absolute, srcdir-relative image URIs already occupy — real
Sphinx post-transforms (`ImageConverter`, `ImageDownloader`, third-party subclasses like
`sphinxcontrib.rsvgconverter`) all place converted output under
`env.doctreedir / "images"` (verified against the installed Sphinx 9.1
`sphinx/transforms/post_transforms/images.py`), and "images/" is also an extremely
common convention for a project's own hand-written `.. image:: images/foo.png`
references.

If a document in the same build references an ordinary image at
`images/diagram.png` (relative to `srcdir`) **and**, separately, an SVG that converts to
the same relative path `images/diagram.png` under `doctreedir`, whichever `_track_image`
/ `post_process_images` call happens first wins the `self.images["images/diagram.png"]`
entry; the second image's own real source is silently discarded:

- If the *converted* image is tracked first (`self.images["images/diagram.png"] =
  "<abs path to converted file>"`), the later *ordinary* image's own bare-URI branch
  (`if resolved_uri not in self.images: self.images[resolved_uri] = ""`) is a no-op
  because the key already exists — so `copy_image_files()` copies the **converted**
  file's bytes to `outdir/images/diagram.png`, and the ordinary image's `#image(...)`
  call in the emitted `.typ` (which still points at the same relative path) silently
  renders the wrong picture. No warning, no error, no test coverage of this path.
- The reverse ordering has the analogous effect on the converted image.

**Fix:** Detect the collision and warn (at minimum) rather than silently keeping
whichever mapping was inserted first, e.g.:

```python
if path.isabs(resolved_uri):
    rel_uri = path.relpath(resolved_uri, self.doctreedir).replace(path.sep, "/")
    node["uri"] = rel_uri
    existing = self.images.get(rel_uri)
    if existing is not None and existing != resolved_uri:
        logger.warning(
            f"image path collision: {rel_uri!r} is claimed by both "
            f"{existing!r} and {resolved_uri!r} -- the second image will "
            "not be copied correctly"
        )
    if rel_uri not in self.images:
        self.images[rel_uri] = resolved_uri
    return
```

Better still, rehome converted/downloaded images into a namespace that cannot collide
with an ordinary srcdir-relative path at all (e.g. prefix with a reserved marker such as
`_typsphinx_converted/images/...`), since `"images/"` is exactly the directory name a
real project is likely to already use.

### WR-02: `_track_image` trusts `resolved_uri` is always nested under `self.doctreedir` with no defensive check

**File:** `typsphinx/builder.py:549-551` — **owner: PR #131 merge, newly-integrated code**

**Issue:** `path.relpath(resolved_uri, self.doctreedir)` is computed unconditionally for
any absolute `resolved_uri`, with no check that the result stays inside `doctreedir` (no
`..` segments) or that the two paths even share a drive/root. I confirmed against the
installed Sphinx 9.1 source that all three built-in post-transforms
(`ImageConverter`, `ImageDownloader`, `DataURIExtractor`) and their documented
`imagedir` property always nest under `env.doctreedir / "images"`, so this is not
reachable today through any currently-known converter. But nothing in this code
enforces that invariant — a third-party post-transform that writes an absolute path
*outside* `doctreedir` (not impossible; `BaseImageConverter.imagedir` is an overridable
property) would silently produce a `../../..`-laden relative path (reproducing the exact
class of bug this fix was written to close, just shaped differently) or, on Windows CI
(which this project actively runs per `ci.yml`'s `windows-latest` matrix entry), a raw
`ValueError` from `os.path.relpath` if the two paths are on different drives, crashing
the build with an unhandled traceback instead of a Sphinx-style warning.

**Fix:** Guard the relpath result before using it:

```python
if path.isabs(resolved_uri):
    try:
        rel_uri = path.relpath(resolved_uri, self.doctreedir)
    except ValueError as e:
        logger.warning(f"cannot resolve image path {resolved_uri!r}: {e}")
        return
    rel_uri = rel_uri.replace(path.sep, "/")
    if rel_uri.startswith("..") or path.isabs(rel_uri):
        logger.warning(
            f"converted/downloaded image {resolved_uri!r} lies outside "
            f"the doctree directory; skipping"
        )
        return
    ...
```

### WR-03: `docs/source/changelog.rst`'s exclusion from the docs-contract-claims gate no longer describes what it actually exempts

**File:** `tests/test_docs_contract_claims_gate.py:142-148`; the exempted content is
`docs/source/changelog.rst:89-93` — **owner: Phase 46's own diff added the exempted
prose; the exclusion mechanism itself is pre-existing (Phase 45.1)**

**Issue:** `EXCLUDED_CLAIM_PAGES["docs/source/changelog.rst"]` justifies exempting the
whole page from the automated two-way lang-route-scope agreement check with:

> "A historical release-note migration guide (documenting the 0.5.x -> 0.6.x
> `typst_elements` allowlist change at the time it shipped), not a live claim about the
> current build's behaviour."

That rationale describes an *older* migration paragraph on the same page. Phase 46 added
a brand-new "Migrating from 0.7.0 to 0.7.1" section to `docs/source/changelog.rst` that
makes its own, present-tense `lang` route-scope claim:

> "The auto-derived `lang` reaches every non-`typst_package` template route -- an
> explicit `typst_template` and a `<srcdir>/base.typ` shadow now both receive it, same as
> the bundled default."

This paragraph independently satisfies every criterion `_claim_sentences()` checks
(contains a `DERIVATION_TOKENS` word — "auto-derived" — a `ROUTE_TOKEN_TO_ROUTES` token —
`typst_template`/`base.typ`/`typst_package` — and the literal `` ``lang`` `` token), so
it *is* a live, current-release claim about the shipped route-scope predicate, not
historical framing — yet it is silently exempted from
`TestLangRouteScopeClaimsMatchShippedPredicate`'s two-way agreement check by the same
blanket page-level exclusion, whose comment doesn't mention it. The claim happens to be
accurate today (I traced it against `configuration.rst`'s equivalent, reviewed claim),
so this is not a live defect, but it means the newest, most likely-to-drift prose on that
page has no automated protection if a future code change alters `lang` route scope again
without updating this migration section.

**Fix:** Either narrow the exclusion to the specific historical paragraph (rather than
the whole page) so new migration-guide sections default to being caught by
`test_discovered_minus_excluded_equals_reviewed` and must be explicitly reviewed, or
update `EXCLUDED_CLAIM_PAGES`'s reason string to explicitly acknowledge and justify
exempting the "Migrating from 0.7.0 to 0.7.1" section too (documenting *why* a
present-tense migration-guide claim about the current release is considered exempt).

## Info

### IN-01: `WITHHOLDING_TOKENS` constant is dead code

**File:** `tests/test_docs_contract_claims_gate.py:185-193` — **owner: pre-existing
(Phase 45.1), untouched by Phase 46's diff**

**Issue:** `WITHHOLDING_TOKENS` (`"withheld"`, `"never"`, `"except"`, `"does not apply"`,
`"do not apply"`, `"not apply"`, `"only when"`) is defined but never referenced anywhere
else in the module — `grep -n "WITHHOLDING_TOKENS"` finds only the definition.
`_classify_sentence()` instead hardcodes its own inline regexes for "except", "not
apply", and "withheld" (correctly, verified by tracing both the real
`configuration.rst` prose and the `PRE_FIX_FALSE_CLAIM`/`known_good` fixtures through the
classifier). This isn't a functional bug — the real docs corpus happens to be covered by
the hardcoded regexes — but the unused constant is misleading: editing it (e.g. adding a
new withholding phrase like `"only when"`, which is already listed but not actually
wired up) would have zero effect on the classifier's behavior.

**Fix:** Either wire `WITHHOLDING_TOKENS` into `_classify_sentence()`'s matching logic,
or remove the unused constant to avoid the false impression that it drives detection.

### IN-02: `RELEASE_VERSIONS` range comment doesn't match the tuple's actual contents

**File:** `tests/test_changelog_page_gate.py:47-49` — **owner: pre-existing inaccuracy
carried forward by Phase 46's edit** (the comment already said "0.4.4 through 0.7.0"
before this diff; Phase 46's change updated the count/end-version to "13" / "0.7.1" but
did not fix the pre-existing start-version discrepancy)

**Issue:** The comment reads:

```python
# The 13 releases the published page was frozen without (0.4.4 through 0.7.1,
# inclusive) -- shared by both the HTML and PDF content-coverage assertions
```

but `RELEASE_VERSIONS` actually starts at `"0.4.1"`, not `"0.4.4"` — the tuple is
`(0.4.1, 0.4.2, 0.4.3, 0.4.4, 0.5.0, 0.6.0, ..., 0.7.1)`, 13 entries total. This also
disagrees with `CHANGELOG.md`'s own 0.7.1 entry, which states the published page was
"frozen at 0.4.0 for two years" (implying every release from 0.4.1 onward, matching the
tuple, was missing) — not frozen at 0.4.3/starting its gap at 0.4.4. A maintainer reading
only the comment could wrongly conclude 0.4.1–0.4.3 aren't covered by this gate's
assertions, when they are.

**Fix:** Correct the comment to "0.4.1 through 0.7.1, inclusive" (or derive the range
description from `RELEASE_VERSIONS[0]`/`RELEASE_VERSIONS[-1]` so it can't drift from the
data again).

---

_Reviewed: 2026-08-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
