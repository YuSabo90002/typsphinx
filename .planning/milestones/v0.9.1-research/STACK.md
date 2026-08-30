# Stack Research

**Domain:** Windows path-shape correctness in an existing Python/Sphinx extension (bug-fix milestone, no new deps)
**Researched:** 2026-08-27
**Confidence:** HIGH (a, c, d — verified by direct CPython source diff / live measurement / existing test read); MEDIUM (b — filesystem limits verified via multiple independent web sources but not directly measured on all three CI filesystems)

## Scope discipline

This milestone (v0.9.1) adds **zero new runtime dependencies**. Every recommendation below is either
an existing stdlib module already imported in this codebase, or a small hand-rolled function living
next to the existing hand-rolled predicates (`_is_drive_qualified`, `_is_absolute_image_uri`,
`_escapes_outdir`) in `typsphinx/builder.py`. Nothing here should be read as "add package X" — the
answer to every sub-question is "use what's already in the stdlib, correctly, and reuse the idiom
this file already established."

## (a) Path-shape predicates: which stdlib API is the authority

**Answer: none of the four alone. The authority is the composite idiom already in this file —
backslash-normalize the string, then `posixpath.isabs(normalized) or _is_drive_qualified(normalized)`
— not `ntpath`, not `os.path`, not `pathlib.PureWindowsPath`.** This is not a new recommendation; it
is the pattern `_is_absolute_image_uri()` (`builder.py:121-194`) and `_escapes_outdir()`
(`builder.py:197-238`) already implement, and `_resolve_target_stem()` (`builder.py:662`) already
reuses the same `.replace("\\", "/")` normalization. `_track_image()`'s basename fix (b/c below) must
route through the *same* normalized string these two already compute, not re-derive it a fourth time
— `builder.py` has this exact idiom at three separate lines (193, 230, 662) already; a fourth
hand-rolled copy at line 1772 would be the kind of drift `_is_drive_qualified()`'s own docstring
explicitly calls out having fixed once already (A47-03/A3).

**Why none of the four single-module options is sufficient, measured against the five named shapes**
(verified live: `python3 --version` → 3.13.13, this repo's own interpreter; second column verified by
diffing CPython's own `Lib/ntpath.py` between the `v3.12.8` and `v3.13.13` tags on GitHub):

| shape | literal | `posixpath.isabs` | `ntpath.isabs` (3.13) | `ntpath.isabs` (3.12, from source diff) | `os.path.isabs` (this POSIX host) | `PureWindowsPath.is_absolute()` |
|---|---|---|---|---|---|---|
| POSIX-absolute | `/a/b` | **True** | False | False | True | False |
| driveless-absolute (Win) | `\a\b` | False | **False** | **True** | False | False |
| drive-qualified | `C:\a\b` | False | **True** | True | False | **True** |
| drive-relative | `C:a` | False | False | False | False | False |
| UNC | `\\server\share\x` | False | **True** | True | False | **True** |
| ordinary-relative | `a/b` | False | False | False | False | False |

- `posixpath.isabs()` alone only catches the POSIX-absolute shape. It never understands drive letters
  or UNC — this is exactly why `_is_drive_qualified()` exists as a *second*, independent predicate
  next to it, not a replacement for it.
- `ntpath.isabs()` (and `os.path.isabs()` on an actual Windows host, since `os.path` *is* `ntpath`
  there) is **not** platform-independent across CPython versions on the identical shape. Verified by
  diffing `Lib/ntpath.py`:
  - **3.12.8** (`https://github.com/python/cpython/blob/v3.12.8/Lib/ntpath.py`):
    `if s.startswith(sep) or s.startswith(colon_sep, 1): return True` — a lone leading backslash
    alone (`sep`) is enough → driveless-absolute is `True`.
  - **3.13.13** (`https://github.com/python/cpython/blob/v3.13.13/Lib/ntpath.py`):
    `return s.startswith(colon_sep, 1) or s.startswith(double_sep)` — the single-`sep`-alone branch
    was **removed**; only a colon-drive or a *double* leading separator counts → driveless-absolute is
    now `False`.
  - This exact narrowing is documented in the CPython 3.13 stdlib docs for `os.path.isabs()`
    (`https://docs.python.org/3/library/os.path.html#os.path.isabs`): *"Changed in version 3.13: On
    Windows, returns `False` if the given path starts with exactly one (back)slash."* — this is the
    "one such narrowing" this project already hit (`_is_absolute_image_uri()`'s own docstring cites
    it; confirmed here against the primary source, not just re-reading that docstring).
  - Consequence for this milestone: **never gate any of these three fixes on `ntpath.isabs()` /
    `os.path.isabs()` directly** — its answer for the driveless-absolute shape depends on which
    CPython minor version is running the *build*, not on which OS. That is strictly worse than the
    existing `posixpath.isabs`-doesn't-know-about-drives gap, because it is silent and time-dependent
    rather than a fixed, documented limitation.
- `pathlib.PureWindowsPath` / `PurePosixPath` are genuinely host-OS-independent (confirmed live:
  `PureWindowsPath("C:\\a\\b").is_absolute()` returns `True` when run on this Linux host, exactly as
  it would on Windows — these classes parse a *named* flavor regardless of the interpreter's host
  OS). But `PureWindowsPath.is_absolute()` requires **both** a drive and a root, so it already
  returned `False` for the driveless-absolute shape *before* 3.13 too (unlike `ntpath.isabs()`,
  which only caught up to that stricter definition in 3.13) — so it does not, by itself, catch every
  shape this milestone needs to widen against either. Using it would mean adding a *second*
  absolute-path predicate with its own different edge-case boundary, on top of the `posixpath` one
  already used for `_escapes_outdir()`'s POSIX-absolute case — two predicates with two different
  drive-relative/UNC boundaries is a worse, not better, foundation than one hand-composed
  string-shape function reused everywhere.

**Conclusion for (a):** keep `posixpath` + `_is_drive_qualified()` (the existing hand-rolled
predicate) as the two primitives, backslash-normalize first, and treat that composite — not any
single stdlib module — as this module's one authority for "is this path-shape absolute," exactly as
`_is_absolute_image_uri()`'s docstring already states. The only actionable stdlib-selection decision
this milestone still has to make is at `_escapes_outdir()` (`builder.py:238`), which computes
`segments` from the normalized string but still applies `posixpath.isabs(stem)` /
`_is_drive_qualified(stem)` to the **raw** `stem` (the exact bug named in the milestone context) —
the fix is mechanical: apply both predicates to the same normalized string `segments` was built from,
matching `_is_absolute_image_uri()`'s own body one-for-one.

## (b) Bounding a filename component's length portably

**There is no portable stdlib constant usable at write time across all three CI platforms.**
`os.pathconf()` and `os.statvfs()` are the only stdlib-exposed way to *ask the filesystem* for its
`NAME_MAX`, and both are documented `Availability: Unix` only
(`https://docs.python.org/3/library/os.html#os.pathconf`) — verified live on this host:
`hasattr(os, "pathconf")` is `True` here (Linux) and `os.pathconf(".", "PC_NAME_MAX")` returns `255`,
but neither attribute exists in CPython's Windows build at all, so a `windows-latest` CI job would
raise `AttributeError` before ever reaching the filesystem question. This rules out querying the
limit at runtime as a cross-platform solution for the `windows-latest`-inclusive acceptance bar
(binding constraint #6) — any fix that calls `os.pathconf` unconditionally must branch on
`hasattr(os, "pathconf")` or platform, which is exactly the kind of OS-native branching this module's
other predicates deliberately avoid.

**Actual limits** (verified against independent sources; MEDIUM confidence — not measured directly
against a live ext4/APFS/NTFS volume in this sandbox):
- **ext4:** `NAME_MAX = 255`, counted in **bytes** of the UTF-8-encoded name, applies to a single
  path **component** (one directory entry), not the whole path. A pure-ASCII name can be 255
  characters; a name built from 4-byte code points caps out far shorter.
- **APFS (macOS):** also 255, counted in bytes of the UTF-8 encoding, per-component (same shape as
  ext4 for this purpose, despite Apple's own marketing copy sometimes saying "255 characters").
- **NTFS (Windows):** 255, but counted in **UTF-16 code units**, per-component. NTFS itself supports
  much longer *total* paths (up to 32,767 UTF-16 units) but the classic Win32 `MAX_PATH` (260 total
  characters) ceiling still applies unless the application opts into long-path support — a
  **separate, whole-path** constraint this milestone's defect does not need to solve (the reported
  `ENAMETOOLONG` is a component-length symptom from a single long basename, not a deep directory
  tree).

**Recommendation:** hardcode a conservative constant, not a filesystem query — mirroring how
`RESERVED_IMAGE_NAMESPACE` and `_EXCLUDED_BUNDLE_*` are already hardcoded module-level constants in
this same file rather than probed at runtime. A single `_MAX_BASENAME_BYTES = 255` (matching ext4/
APFS exactly, and safely under NTFS's 255-UTF-16-unit limit since ASCII/Latin basenames — the
realistic shape of a Sphinx source tree's image filenames — take 1 UTF-16 unit per UTF-8 byte)
applied by:
1. Encoding the candidate basename to UTF-8 (`.encode("utf-8")`), never counting `len()` on the `str`
   directly — the byte count, not the character count, is what ext4/APFS actually enforce.
2. Truncating the byte string to fit within `_MAX_BASENAME_BYTES` **after** reserving room for the
   `{sha1[:8]}-` prefix (the digest is the collision anchor per the milestone's own constraint 3 — it
   must never be the part that gets cut).
3. Decoding back with `errors="ignore"` (or an explicit boundary-safe trim) so truncation never splits
   a multi-byte UTF-8 sequence and produces an invalid filename.

No new dependency: `str.encode()` / `bytes` slicing / `str.decode()` are all builtins.

## (c) Delimiter-aware display quoting without backslash escaping

**Hand-rolled is correct; neither `shlex.quote()` nor `json.dumps()` satisfies both constraints.**
Measured live against three sample paths (a Windows path with backslashes, a path containing a
literal apostrophe, a path with a space):

| input | `shlex.quote()` | `json.dumps()` | `repr()` |
|---|---|---|---|
| `C:\Users\runner\project\_templates\nested` | `'C:\Users\runner\project\_templates\nested'` (backslashes preserved, but a bare single-quote wrap with **no delimiter present in unquoted-safe cases** — see below) | `"C:\\Users\\runner\\project\\_templates\\nested"` (backslashes **doubled** — the exact regression this milestone exists to close) | `'C:\\Users\\runner\\project\\_templates\\nested'` (backslashes **doubled**) |
| `it's/a/path/o'brien` | `'it'"'"'s/a/path/o'"'"'brien'` (POSIX shell quote-breaking — multiple quote characters spliced into the middle of the string, unreadable as a plain-English log sentence) | `"it's/a/path/o'brien"` (correct here, but only because this sample has no backslash) | `"it's/a/path/o'brien"` (switches to double-quote delimiter automatically, zero escaping needed — this is the "quote-disambiguation" behavior the CONTEXT text credits `repr()` with) |
| `plain/path` | `plain/path` (**no quoting at all** — `shlex.quote` omits delimiters entirely for shell-safe strings) | `"plain/path"` | `'plain/path'` |

- **`shlex.quote()` is POSIX-shell-command-substitution quoting, not display quoting** — wrong tool.
  Two independent problems: (1) it quote-breaks (`'...'"'"'...'`) a string containing a single quote
  into an unreadable multi-segment mess rather than a single delimited span, which fails the
  57-REVIEW IN-01 "delimited unambiguously" bar in spirit even though it is technically shell-safe;
  (2) it silently **omits delimiters** for a string containing no shell-special characters, which
  breaks this codebase's existing convention that every interpolated path always appears wrapped
  (every current `!r` and every current hardcoded `'...'` site always emits a delimiter pair).
- **`json.dumps()` escapes backslash to `\\`** — this is precisely the defect class this milestone
  exists to close (the same doubling `repr()` causes); ruled out on that basis alone, independent of
  its JSON-specific `"..."` delimiter also being an odd choice for a plain-English sentence.
- **`repr()`'s *delimiter-selection* half is exactly right and worth keeping** (this is what the
  milestone context means by "restore the quote-disambiguation `repr()` provided"): Python's `repr()`
  picks `'...'` by default, but switches to `"..."` when the string contains a single quote and no
  double quote — verified live above, zero escaping needed in that case. What must be **dropped** is
  `repr()`'s *other* half: its backslash-doubling and its control-character/non-ASCII escaping, which
  is what caused the original defect and is not needed for a filesystem path.

**Recommendation:** one small hand-rolled helper, in the same module and the same style as
`_is_drive_qualified()` / `_conf17_violation_message()` — a single source-of-truth function that:
1. Picks `'` as the delimiter, unless the value contains `'` and not `"`, in which case picks `"`
   (repr()'s own delimiter-selection rule, reimplemented — CPython exposes no public API for just this
   half; `unicode_repr()` is a C-internal implementation detail with no callable-in-parts surface).
2. If the value contains *both* quote characters (the one case that still needs an escape to stay
   unambiguous), backslash-escapes only the chosen delimiter character itself — never any other
   backslash already present in the path. This is the one narrow exception, and it does not fire for
   either of the two named regression-guard cases (a Windows path with no quotes at all; a path with a
   single quote and no double quote).
3. Wraps the (possibly delimiter-escaped) value in the chosen delimiter pair and returns it.

This is ~10 lines, zero new dependency, and slots into the same three call-site groups the existing
`_conf17_violation_message()` / `_templates_path_collision_message()` /
`_bundle_destination_collision_message()` functions already isolate — those three should call the new
helper instead of their current hardcoded `'{value}'` f-string interpolation (dropping the single-quote
hardcode per binding constraint #4/57-REVIEW WR-01), and the remaining path-valued `!r` sites census'd
in the milestone context (`builder.py:942,964,965,999,1007,1008,1015,1767,2056,2066,697`,
`writer.py:511-513`, `template_registry.py:410,422,433`) should route through it too. Identifier-valued
`!r` (registry keys, docnames, config tuples — e.g. `key!r`, `docname!r`, `entry!r` seen throughout
`builder.py`) is explicitly **out of scope and stays `!r`** — only filesystem-path-valued
interpolations change.

## (d) pytest facilities for asserting Windows-shaped behavior without a Windows runner

**Answer: plain `pytest.mark.parametrize` over hand-built literal strings — no `monkeypatch`, no
`skipif`.** This follows directly from (a): every predicate in scope
(`_is_drive_qualified`, `_is_absolute_image_uri`, `_escapes_outdir`, and the new quoting helper from
(c)) is a **pure string function** that calls `posixpath` explicitly and never touches `os.path` /
`ntpath` / any OS-native module or `sys.platform`. That is a deliberate, load-bearing property — it
is precisely *why* these functions are declared platform-independent (D-05) and *why* `_track_image()`
was moved off the OS-native `path.isabs()` it used before BLD-09 (Phase 55). Given that:

- **`monkeypatch` of `os.path`/`ntpath` is inapplicable, not merely unnecessary.** These functions
  never import or call `os.path`/`ntpath` at all (they import `posixpath` directly, plus the
  hand-rolled `_is_drive_qualified`), so there is nothing in their call graph a monkeypatch of
  `os.path` could intercept. Reaching for `monkeypatch` here would be testing the wrong layer, and
  worse, it would tempt a future edit toward re-introducing an OS-native-module dependency into code
  whose whole point is to have none. The one place `monkeypatch` legitimately belongs in this
  codebase is code that *does* branch on `sys.platform` or call the OS-native `path` module — and
  this milestone's whole thrust (a) is moving code *away* from that shape, not toward it.
- **`pytest.mark.skipif` is actively wrong for this milestone**, not just unneeded. Binding constraint
  #1 states the whole class of defects is *latent because* the `windows-latest` CI lane doesn't
  exercise these shapes today, and constraint #6's acceptance bar is the 3-OS lane green *including*
  `windows-latest`. A `skipif` gating a Windows-shaped-string assertion to `sys.platform == "win32"`
  would mean the POSIX lanes — where these bugs actually reproduce, since the predicates are pure
  string functions with no OS dependency — never run the assertion at all, which is exactly backwards:
  it would hide the defect from the two CI legs that can catch it fastest and reintroduce the
  "green at HEAD, would stay green if nothing were fixed" trap constraint #1 already names.
- **The existing test already demonstrates the correct pattern and should be extended, not
  replaced:** `TestWindowsPathEscapingRegressionGuard`
  (`tests/test_templates_path_collision_gate.py:412-452`) defines
  `WINDOWS_SHAPED_PATH = "C:\\Users\\runner\\project\\_templates\\nested"` as a plain class attribute
  and calls the real product functions (`_conf17_violation_message()`, etc.) directly with it — no
  fixture indirection, no platform mocking, runs identically and meaningfully on every CI leg. The
  new gates for `_escapes_outdir()`'s raw-vs-normalized bug, the three `_track_image()` gaps, and the
  quoting helper's apostrophe case should follow the identical shape: `pytest.mark.parametrize` (or
  the same hand-built-literal-plus-plain-`assert` style already used in the doctest blocks inside
  `_is_drive_qualified`/`_escapes_outdir`) over string literals for the five shapes in (a)'s table,
  asserted directly against the module-level functions.
- **One exception the milestone itself names (binding constraint #2):** at least one gate must be a
  real `typst.compile()` call, not a string assertion — because the `image("...")` backslash-escaping
  gap (`translator.py:4746,4749`) is invisible to any assertion that stops at `node["uri"]`. This is
  still not a platform-mocking concern: `typst-py`'s `compile()` binding is itself OS-agnostic (it
  parses Typst-language syntax, not filesystem paths), so feeding it a Windows-shaped URI string on a
  POSIX CI runner exercises the real defect (Typst's language-level refusal of an unescaped backslash
  in a string literal) with no OS simulation needed at all — this is the "real gate," not a
  monkeypatch target.

## What NOT to use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `ntpath.isabs()` / `os.path.isabs()` (bare, on either the raw or the normalized string) as the sole absolute-path test | Its answer for a driveless-absolute shape flipped between CPython 3.12 and 3.13 (verified against `Lib/ntpath.py` source and the 3.13 changelog) — version-dependent, not just OS-dependent | The existing composite: backslash-normalize, then `posixpath.isabs(normalized) or _is_drive_qualified(normalized)` |
| `pathlib.PureWindowsPath.is_absolute()` as a second, Windows-specific predicate alongside `posixpath.isabs()` | Introduces a second predicate with its own, different drive/UNC boundary rather than reusing the one already established; doubles the surface that must be kept in sync | The single existing composite predicate, applied uniformly |
| `os.pathconf()` / `os.statvfs()` to query the filesystem's `NAME_MAX` at write time | `Availability: Unix` only (verified against the stdlib docs) — raises `AttributeError` unconditionally on the `windows-latest` CI leg | A hardcoded, conservative byte-count constant (`_MAX_BASENAME_BYTES = 255`, UTF-8 byte-counted) |
| `shlex.quote()` for a human-readable log/warning message | POSIX shell quoting: quote-breaks a single-quote-containing string into an unreadable multi-segment escape, and omits delimiters entirely for "safe" strings, breaking this codebase's always-delimited convention | A small hand-rolled helper reusing `repr()`'s delimiter-selection rule without its escaping |
| `json.dumps()` for the same purpose | Escapes backslash to `\\` — reproduces the exact defect this milestone exists to close | Same hand-rolled helper |
| `repr()` unmodified, for any filesystem-path-valued interpolation | Doubles backslashes (the root defect) and escapes control/non-ASCII characters not relevant to a path | The hand-rolled helper, which keeps only `repr()`'s delimiter-selection half |
| `pytest.mark.skipif(sys.platform != "win32", ...)` on any of these predicate tests | These are pure string functions with no OS dependency; skipping them on POSIX lanes hides the exact defect class this milestone exists to surface, and contradicts binding constraint #6 (3-OS lane, all green) | `pytest.mark.parametrize` over hand-built literal strings, run unconditionally on every OS |
| `monkeypatch` of `os.path`/`ntpath`/`sys.platform` for these predicates | None of the in-scope functions import or call those modules — there is nothing for the monkeypatch to intercept, and reaching for it would pull code back toward the OS-native-module dependency this milestone (and Phase 55/BLD-09 before it) deliberately removed | Plain literal-string test inputs; no mocking layer |

## Version Compatibility

| Concern | Notes |
|---|---|
| CPython 3.12 vs 3.13 `ntpath.isabs()`/`os.path.isabs()` | Diverge on the driveless-absolute shape (3.12: `True`; 3.13: `False`) — irrelevant to the recommended fix since it never calls either function, but worth keeping in mind if any future code in this file is tempted to reach for the OS-native `path` module again |
| `posixpath`, `pathlib` | Stable across 3.12–3.13 for every shape in the table above — no compatibility concern for the recommended composite predicate |
| `typst-py` (`>=0.15,<0.16`, already pinned) | Unaffected by any of these path-handling fixes; only relevant as the real-compile gate binding constraint #2 requires (feeding an escaped-vs-unescaped `image("...")` string through `typst.compile()`) |

## Integration points (concrete, file:line)

- **`builder.py:238`** (`_escapes_outdir`) — apply `posixpath.isabs(...)` / `_is_drive_qualified(...)`
  to the same normalized string `segments` is already built from, not the raw `stem` — one-line fix,
  mirrors `_is_absolute_image_uri()`'s body exactly.
- **`builder.py:1772`** (`_track_image`, escape branch) — replace `path.basename(resolved_uri)`
  (OS-native `path`, imported `from os import path` at the top of this module) with a basename taken
  from the same backslash-normalized string `_is_absolute_image_uri()` computed for the gate check
  just above it in this same function — do not recompute the normalization a fourth time in this file;
  factor the existing `.replace("\\", "/")` line into a tiny shared normalize step if that avoids the
  duplication cleanly, otherwise inline it identically to the other three sites (`builder.py:193, 230,
  662`).
- **`builder.py:1772-1780`** (key construction) — apply the (b) truncation (`_MAX_BASENAME_BYTES`,
  digest-anchored) to the basename component only, after the normalization fix above.
- **`translator.py:4746,4749`** (`visit_image`) — route `adjusted_uri` through
  `escape_typst_string()` (`translator.py:156`, already the single source of truth for Typst
  string-literal escaping in this file) before interpolating it into `image("{adjusted_uri}"`.
- **Quoting helper (c)** — new small function, most naturally placed beside
  `_conf17_violation_message()` / `_templates_path_collision_message()` /
  `_bundle_destination_collision_message()` in `builder.py` (lines 303-403), since those three already
  own the "build the message text once, call it from every site" pattern this milestone extends. Every
  site in the census (`builder.py:942,964,965,999,1007,1008,1015,1767,2056,2066,697`,
  `writer.py:511-513`, `template_registry.py:410,422,433`) that currently interpolates a **path
  value** (not an identifier) with `!r` or a hardcoded `'...'` switches to call it.

## Sources

- CPython `Lib/ntpath.py` at tag `v3.12.8`:
  `https://github.com/python/cpython/blob/v3.12.8/Lib/ntpath.py` — `isabs()` source, fetched and
  diffed directly.
- CPython `Lib/ntpath.py` at tag `v3.13.13`:
  `https://github.com/python/cpython/blob/v3.13.13/Lib/ntpath.py` — `isabs()` source, fetched and
  diffed directly.
- CPython stdlib docs, `os.path.isabs()`:
  `https://docs.python.org/3/library/os.path.html#os.path.isabs` — quotes the "Changed in version
  3.13" note verbatim.
- CPython stdlib docs, `os.pathconf()` availability:
  `https://docs.python.org/3/library/os.html#os.pathconf` — `Availability: Unix` confirmed.
- Live measurement, this repo's own interpreter (`python3 --version` → 3.13.13): `posixpath.isabs`,
  `ntpath.isabs`, `os.path.isabs`, `pathlib.PurePosixPath.is_absolute`,
  `pathlib.PureWindowsPath.is_absolute`, `os.pathconf(".", "PC_NAME_MAX")` → `255`, and the
  `shlex.quote()` / `json.dumps()` / `repr()` comparison table — all run directly via `python3 -c`
  during this research session (commands and output preserved in the session transcript).
- Web search cross-check on ext4/APFS/NTFS component-length limits (byte-vs-UTF-16-unit distinction),
  no single canonical stdlib/vendor doc page found — MEDIUM confidence, flagged in-line above; if this
  matters for the eventual gate's exact test values, a real-filesystem measurement on each CI runner
  (`os.pathconf` on ubuntu-latest/macos-latest; a `MAX_PATH`-adjacent probe or documentation-only
  reference on windows-latest, since no stdlib call exists there) is the fallback plan, not required
  for the hardcoded-constant recommendation above.
- Existing repository code read directly, not re-derived: `typsphinx/builder.py` (`_is_drive_qualified`
  86-118, `_is_absolute_image_uri` 121-194, `_escapes_outdir` 197-238, `_track_image` ~1650-1790,
  `_conf17_violation_message`/`_templates_path_collision_message`/
  `_bundle_destination_collision_message` 303-403), `typsphinx/translator.py`
  (`escape_typst_string` ~156, `visit_image` ~4740-4760), `typsphinx/writer.py` (~500-516),
  `typsphinx/template_registry.py` (~400-436), `tests/test_templates_path_collision_gate.py`
  (`TestWindowsPathEscapingRegressionGuard` 412-452), `.planning/PROJECT.md` (v0.9.1 milestone
  section).

---
*Stack research for: typsphinx v0.9.1 "Windows path correctness"*
*Researched: 2026-08-27*
