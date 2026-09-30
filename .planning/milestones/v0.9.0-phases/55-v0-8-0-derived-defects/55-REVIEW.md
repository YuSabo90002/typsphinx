---
phase: 55-v0-8-0-derived-defects
reviewed: 2026-08-16T07:09:52Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - typsphinx/translator.py
  - typsphinx/builder.py
  - tests/test_builder.py
  - tests/test_include_edge_derivation_unit.py
  - tests/test_include_edge_separator_collision_gate.py
  - tests/test_label_existence_guard_unit.py
  - tests/test_sanitize_label_injectivity_unit.py
  - tests/test_xref_compile_time_guard_render_gate.py
  - tests/fixtures/xref_label_collision_guard_gate/conf.py
  - CHANGELOG.md
findings:
  critical: 1
  warning: 1
  info: 2
  total: 4
status: issues_found
---

# Phase 55: Code Review Report

**Reviewed:** 2026-08-16T07:09:52Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Reviewed the phase-55 diff (`18a2a60d..HEAD`) across `translator.py` (XREF-05,
BLD-07, BLD-08) and `builder.py` (BLD-09, IMG-03), plus the new/changed test
modules and the CHANGELOG entries describing all five fixes.

The two injectivity claims that are this phase's load-bearing property held
up under independent adversarial testing: I re-ran brute-force searches
against `_sanitize_label` (~6.7M strings over a hex/underscore/slash/quote
alphabet) and against `make_include_edge_key` (~13K triples over a
`#`/`>`/backslash/quote alphabet) outside the shipped test suite and found
zero collisions in either, corroborating the exhaustive round-trip proofs
already in `tests/test_sanitize_label_injectivity_unit.py` and
`tests/test_include_edge_separator_collision_gate.py`. The `_MAX_INCLUDE_CHAIN_DEPTH`
boundary arithmetic in `derive_master_edge_keys()` is exact (off-by-one
verified by hand against the three depth tests). BLD-08's tests exercise the
real boundary, not just a fixture, and would fail if the bound check or the
recursion shape were reverted.

However, BLD-09's widened `_is_absolute_image_uri()` gate — combined with
IMG-03's key construction in `_track_image()`'s escape branch — has a
concrete, reproducible consequence beyond the documented backslash-in-POSIX-
filename tradeoff: a Windows/UNC-shaped absolute image URI processed on a
POSIX build host now reaches the escape-relocation branch (as BLD-09
intends), but the relocation key is built from `path.basename(resolved_uri)`
on the *unnormalized* URI, which does not split on a literal backslash under
POSIX's `posixpath.basename()`. The resulting key embeds raw, unescaped
backslashes, and that key is later interpolated verbatim (no
`escape_typst_string()` call) into `visit_image()`'s `image("...")` call —
producing a `.typ` file that fails to compile. I reproduced this end-to-end,
including a real `typst.compile()` call that raises `path must not contain a
backslash`. Neither of the new BLD-09/IMG-03 tests renders the emitted body
or compiles it, so this regression is invisible to the current suite.

## Critical Issues

### CR-01: BLD-09's widened absolute-URI gate feeds an unescaped, backslash-laden filename into `image(...)`, breaking the Typst compile

**File:** `typsphinx/builder.py:1700-1704` (interacting with `typsphinx/builder.py:121-194` and `typsphinx/translator.py:4746-4749`)

**Issue:** In `_track_image()`'s escape branch (D-05/D-06, widened this phase
by BLD-09's `_is_absolute_image_uri()`), the relocation key is:

```python
digest = hashlib.sha1(resolved_uri.encode("utf-8")).hexdigest()[:8]
key = (
    f"{RESERVED_IMAGE_NAMESPACE}/{digest}-"
    f"{path.basename(resolved_uri)}"
)
```

`path.basename()` is `posixpath.basename()` on a POSIX build host (the
project's own primary dev/CI platform per `CLAUDE.md`'s NixOS guidance), and
`posixpath.basename()` only splits on `/`. Before this phase, a
backslash-containing absolute URI (Windows driveless-absolute or UNC shape)
was never classified as absolute on POSIX at all — `path.isabs()` (=
`posixpath.isabs()`) returned `False` for it — so this branch was
unreachable for that shape. BLD-09's `_is_absolute_image_uri()` deliberately
widens detection to catch exactly this shape (per its own docstring and per
`tests/test_builder.py::test_post_process_images_driveless_absolute_uri_reaches_rehome_branch`
/ `test_post_process_images_unc_absolute_uri_reaches_rehome_branch`), so this
branch is now reachable for it. Once reached, `path.basename(resolved_uri)`
returns the **entire original URI** (since it contains no `/`), backslashes
and all, and that raw text becomes part of `self.images`'s key. That key
flows into `node["uri"]`, and from there into `visit_image()` at
`typsphinx/translator.py:4746-4749`:

```python
adjusted_uri = self._compute_relative_image_path(uri, current_docname)
...
self.add_text(f'image("{adjusted_uri}"')
```

with **no `escape_typst_string()` call** — unlike every other user-controlled
string this phase's own two other fixes (XREF-05, BLD-07) are careful to
route through an escaping/injectivity-preserving transform before emission.

I reproduced this concretely:

```
$ .venv/bin/python - <<'EOF'
... (drive a docutils doc through TypstTranslator with
     uri="_typst_converted/70c5653b-\\typsphinx_test_55_03_server\share\chart.png",
     the exact shape _track_image() produces for the UNC test fixture)
EOF
'#{\n...\nimage("_typst_converted/70c5653b-\\typsphinx_test_55_03_server\share\chart.png")\n\n}\n'

$ echo '#image("_typst_converted/70c5653b-\\typsphinx_test_55_03_server\share\chart.png")' > probe.typ
$ python -c "import typst; typst.compile('probe.typ', output='probe.pdf')"
COMPILE ERROR: path must not contain a backslash
```

So the exact chain BLD-09's own new tests exercise
(`test_post_process_images_unc_absolute_uri_reaches_rehome_branch`,
`test_post_process_images_driveless_absolute_uri_reaches_rehome_branch`) —
if carried one step further into an actual document render and Typst
compile, which neither test does — fails the build outright. This is a
regression class BLD-09 specifically creates reachability for on the
project's own primary platform (POSIX): before this phase such a URI simply
wasn't detected as absolute and took a different (also imperfect, but
pre-existing and out of this phase's scope) path; after this phase it is
correctly detected as absolute per SC#4, but the very code this phase
touches (IMG-03's key-construction line) hands it forward unescaped and
un-normalized into a Typst string literal, turning a previously-silent
mis-detection into a hard, deterministic build failure for any project whose
image-providing extension emits a backslash-containing absolute URI while
building on Linux/macOS CI — exactly the "Windows-authored input validated
on POSIX CI" scenario this same phase's `_is_drive_qualified()`/
`_escapes_outdir()` precedent is designed to protect against, not break.

This is not the previously-filed, out-of-scope `_escapes_outdir()` gap
(`.planning/todos/pending/2026-08-16-escapes-outdir-isabs-not-backslash-normalized.md`)
— that todo is about `_escapes_outdir()`'s own absolute-detection predicate
being non-normalized; this finding is about the *escape branch's key
construction* embedding an unescaped, unnormalized basename into emitted
Typst source, a different code path with a worse, concretely-reproduced
consequence (a hard compile failure, not merely a missed detection).

**Fix:** At minimum, normalize backslashes before taking the basename in the
escape branch, consistent with the module's existing D-05
platform-independence idiom used elsewhere in this same file
(`_is_absolute_image_uri()`, `_escapes_outdir()`):

```python
digest = hashlib.sha1(resolved_uri.encode("utf-8")).hexdigest()[:8]
safe_basename = path.basename(resolved_uri.replace("\\", "/"))
key = f"{RESERVED_IMAGE_NAMESPACE}/{digest}-{safe_basename}"
```

That alone still leaves a general gap: any character that is meaningful
inside a Typst string literal (`\`, `"`) surviving into `node["uri"]` from
*any* branch (not just the escape branch) reaches `visit_image()`
unescaped. The more complete fix is for `visit_image()` (or
`_compute_relative_image_path()`) to route `adjusted_uri` through
`escape_typst_string()` before interpolating it into `image("...")`,
matching the pattern this phase's own XREF-05/BLD-07 fixes establish for
every other emission site that inserts translator-controlled text into a
Typst string literal. Also add a regression test that renders (not just
tracks) a driveless/UNC-shaped image URI through `TypstTranslator` and
asserts the emitted `image("...")` argument contains no unescaped
backslash (or, better, actually calls `typst.compile()` on the result, the
way `tests/test_include_edge_separator_collision_gate.py` and
`tests/test_xref_compile_time_guard_render_gate.py` already do for their
own phase-55 fixes) — the current BLD-09 tests stop one layer short of
proving the fix is safe end-to-end.

## Warnings

### WR-01: IMG-03's digest+basename key has no length bound and can exceed common filesystem filename limits

**File:** `typsphinx/builder.py:1700-1704`

**Issue:** The relocated filename is `{digest8}-{basename}` where `digest8`
is a fixed 9-byte prefix (`"70c5653b-"` shape) and `basename` is
`path.basename(resolved_uri)` with no length cap. Most POSIX filesystems
(ext4, APFS) and NTFS impose a 255-byte/char limit per path component. A
pathological but realistic case — an image URI whose final path segment is
already close to that limit (e.g. a long slug generated by another tool, or,
per CR-01 above, a basename that is actually the *entire* unsplit absolute
URI because it contains no `/`) — will now exceed the limit once the 9-byte
prefix is added, where the pre-IMG-03 basename-only key would not have. This
is a build-time `OSError` (`ENAMETOOLONG`) at `copy_image_files()` time
rather than a compile-time failure, so it surfaces later and is harder to
diagnose than CR-01.

**Fix:** Either cap the basename portion (e.g. truncate to a safe length
before appending, keeping the digest as the collision-avoidance anchor since
truncation on its own reintroduces the pre-IMG-03 collision risk this phase
just closed), or at minimum note the limit in the escape-branch's own
warning message so a user hitting it has a diagnosable trail back to the
oversized source URI.

## Info

### IN-01: `_is_absolute_image_uri`'s own docstring overstates its "exactly two lines" claim

**File:** `typsphinx/builder.py:181-191`

**Issue:** The docstring's `Note:` section states the name
`_is_absolute_image_uri` appears "on exactly two lines of this file (the
definition and the single gate call site inside `_track_image()`)". In fact
it appears on three lines: the definition (`builder.py:121`), a prose mention
inside `_track_image()`'s own docstring (`builder.py:1634`), and the call
site (`builder.py:1653`). Harmless (the prose mention doesn't create a second
derivation point), but the stated acceptance-criteria count is now
inaccurate and could mislead a future reader auditing for duplicate
derivation points via a naive grep-count.

**Fix:** Reword the `Note:` to "the definition, one prose mention in
`_track_image()`'s own docstring, and the single call site" or drop the
specific count and just assert "no doctest block, to keep the call site
singular."

### IN-02: CHANGELOG's BLD-09 entry attributes the fix to "Python 3.13" without the platform qualifier that makes it true

**File:** `CHANGELOG.md:63-67`

**Issue:** "An absolute image URI written by a third-party extension in the
driveless Windows shape (or the UNC shape) now reaches the relocate-and-warn
path on Python 3.13, where it was previously left untouched" reads as if the
pre-fix gap were Python-version-scoped. In fact, per the pre-fix code
(`path.isabs(resolved_uri)`, OS-native), this shape was **always** left
untouched on POSIX regardless of Python version (`posixpath.isabs()` never
treated a backslash-leading string as absolute on any Python version), and
was only version-sensitive on Windows (CPython 3.13's narrowed
`ntpath.isabs()`, per the code's own detailed comment at
`builder.py:128-136`). A reader skimming only the CHANGELOG could conclude
the gap was Windows+3.13-only and therefore irrelevant to their POSIX build,
which is the opposite of the actual, more consequential case (see CR-01).

**Fix:** Add "on Windows" before "Python 3.13", and note the POSIX case was
always affected too, e.g.: "...now reaches the relocate-and-warn path
identically on every platform and Python version; on Windows under Python
3.13 specifically, this shape was previously left untouched (`ntpath.isabs()`
narrowed there); on POSIX it was always left untouched, regardless of
Python version."

---

_Reviewed: 2026-08-16T07:09:52Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

---

## Orchestrator addendum — CR-01 re-measured (execute-phase, 2026-08-16)

CR-01's **mechanism is confirmed**; its **"regression introduced by Phase 55"
framing is not**. Both halves were re-measured independently by the
execute-phase orchestrator on the merged tree, not taken from the reviewer's
report.

### Confirmed

1. `_track_image()`'s escape branch derives its key with
   `path.basename(resolved_uri)` on the **un-normalized** URI. On a POSIX
   build host `path.basename` is `posixpath.basename`, which does not split
   on `\`, so the whole URI becomes the "basename". Measured on the merged
   tree:

   | shape | absolute? | escape branch | key contains `\` |
   |---|---|---|---|
   | unc | True | True | **yes** |
   | driveless-absolute | True | True | **yes** |
   | drive-qualified | True | True | **yes** |
   | posix-absolute | True | True | no |
   | ordinary-relative | False | — | — |

2. `visit_image()` emits `image("{adjusted_uri}")` with no
   `escape_typst_string()` call, and Typst rejects the result:

   ```
   $ printf '#image("_typst_converted/70c5653b-\\\\typsphinx_test_55_03_server\\share\\chart.png")\n' > probe.typ
   $ python -c "import typst; typst.compile('probe.typ', output='probe.pdf')"
   COMPILE ERROR: TypstError path must not contain a backslash
   ```

### Corrected

CR-01 states this turns "a previously-silent mis-detection into a hard,
deterministic build failure". It does not — the build already failed, with the
same Typst error, on the pre-fix tree. Measured by running the **pre-fix**
`builder.py` (from `40b92fc6`) and the merged one side by side against the same
UNC URI:

```
PRE-FIX  node['uri'] = '\\typsphinx_test_55_03_server\share\chart.png'
POST-FIX node['uri'] = '_typst_converted/70c5653b-\\typsphinx_test_55_03_server\share\chart.png'
```

Pre-fix, the URI was not classified as absolute on POSIX, fell through to the
final `self.images[resolved_uri] = ""`, and reached `image(...)` with its
backslashes intact — the identical `path must not contain a backslash` failure.
The `path.basename()` call in the escape branch is also itself pre-existing
(`40b92fc6:typsphinx/builder.py:1589` — `key = f"{RESERVED_IMAGE_NAMESPACE}/{path.basename(resolved_uri)}"`);
IMG-03 added the digest prefix ahead of it and did not change its
normalization.

So Phase 55 neither introduced nor fixed this. What it changed for this input
class is that the emitted path now carries the reserved namespace and a digest,
and a `could not rehome image URI` warning is now logged where previously there
was silence.

### Severity as re-rated

**Warning, not blocker, for Phase 55's own gates.** It is a real, reproducible
defect in a line this phase edited, and it should be fixed — but it is
pre-existing, it does not regress any prior behaviour, and it does not falsify
SC#4 (classification) or SC#5 (key distinctness), both of which are met. It
belongs in the same follow-up lane as the already-filed sibling gap
`.planning/todos/pending/2026-08-16-escapes-outdir-isabs-not-backslash-normalized.md`,
which it sits directly adjacent to. Owner decides fix-now vs. todo.

The one-line shape of the fix, for whoever takes it:

```python
safe_basename = path.basename(resolved_uri.replace("\\", "/"))
key = f"{RESERVED_IMAGE_NAMESPACE}/{digest}-{safe_basename}"
```

Note this alone does not make the emitted path safe in general — WR-01's
length bound and the absence of any escaping at the `image("...")` emission
site both remain open.
