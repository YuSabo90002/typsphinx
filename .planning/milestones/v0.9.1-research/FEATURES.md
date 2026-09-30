# Feature Research

**Domain:** Bug-fix milestone — Windows path correctness for a Sphinx→Typst extension (v0.9.1)
**Researched:** 2026-08-27
**Confidence:** HIGH (claims (a)-(c) verified against locally-installed Sphinx 9.1.0 / mypy source and pip's documented cache layout; claim (d) verified with a real `typst.compile()` run in this repo's own `.venv`, not documentation-only)

This is a bug-fix round, not a new-capability milestone. "Features" below means the **observable
correct behaviours** the three defect-family fixes must produce, framed against how comparable
tools handle the same three situations (escape-guarding a config path, relocating an unusable
filename, quoting a path in a diagnostic) and against what Typst itself actually accepts.

## Evidence summary (answers to the four research questions)

### (a) Escape-guarding a path-shaped config value — Sphinx's own answer is "not our problem"

Read directly from the installed Sphinx 9.1.0 tree
(`.venv/lib/python3.13/site-packages/sphinx/builders/latex/__init__.py`):

- `LaTeXBuilder.init_document_data()` (line 151) validates only that `entry[0]` (the **docname**)
  is a known document (`docname not in self.env.all_docs` → `logger.warning(...)`, entry skipped).
  It performs **zero validation** of `entry[1]` (`targetname`, the LaTeX/PDF output filename —
  `latex_documents`' direct analogue of typsphinx's `typst_documents` target stem).
- `write_documents()` (line 299) uses `targetname` completely unguarded:
  `destination_path = self.outdir / targetname` (line 343), then
  `destination_path.write_text(output, ...)`.
- `validate_config_values()` (line 526) only checks `latex_elements` dict keys against a known
  set — no path-shape validation anywhere in the file.

I confirmed the consequence with real `pathlib` semantics (not assumed):
```
>>> Path('/outdir') / '/etc/cron.d/evil'
PosixPath('/etc/cron.d/evil')      # outdir silently discarded — Path.__truediv__ on an
                                     # absolute right operand drops the left operand entirely
>>> Path('/outdir') / '../../etc/evil'
PosixPath('/outdir/../../etc/evil') # traversal segment passed straight through
```
So Sphinx's own most comparable builder does **none of the three candidate behaviours** the
question asked about (refuse loudly / sanitize silently / derive-and-warn) — it does nothing at
all. `conf.py` is treated as fully-trusted first-party content, not untrusted input, and a
malformed `latex_documents` target is the documentation author's problem to notice from the output
tree, not Sphinx's to guard against.

**Implication for typsphinx:** typsphinx's `_escapes_outdir()` (builder.py:197) already goes
*beyond* Sphinx's own bar — refusing the escaping stem and falling back to a basename, per its own
docstring's "OUT-02" contract. That policy predates this milestone and is not up for
reconsideration here (see Anti-Features below); v0.9.1's job is narrower: make the *detection*
itself platform-shape-correct, matching the idiom `_is_absolute_image_uri()` (builder.py:190)
already uses (normalize backslashes to `/` **before** applying `posixpath.isabs()` /
`_is_drive_qualified()`), rather than applying those predicates to the raw, unnormalized `stem` as
`_escapes_outdir()` currently does at builder.py:238.

### (b) Relocating a file whose name is unusable — human-recognizable, hash-anchored, silent by default

Two real, load-bearing precedents, both read from source rather than assumed:

1. **Sphinx's own `FilenameUniqDict`** (`sphinx/util/_files.py`, used for `env.images` — the
   closest upstream analogue of typsphinx's image relocation), on a basename collision:
   ```python
   unique_name = new_file.name
   base, ext = new_file.stem, new_file.suffix
   i = 0
   while unique_name in self._existing:
       i += 1
       unique_name = f'{base}{i}{ext}'
   ```
   Fully human-recognizable (`figure1.png`, `figure2.png`, ...), **no warning at all** — this is
   the "ordinary, expected" collision case, exactly the register typsphinx's own D-01/D-03/D-04
   silent-relocation branch (builder.py, `_track_image()`) already occupies for its collision
   case.
2. **Sphinx's `DownloadFiles`** (same module) for downloadable-file collisions takes the opposite
   shape: `digest = hashlib.md5(filename.as_posix()...).hexdigest(); dest_path = digest/filename.name`
   — hash as a **directory** component, original filename preserved **in full** as the leaf, no
   truncation, no warning. This is architecturally identical to typsphinx's own
   `{RESERVED_IMAGE_NAMESPACE}/{digest[:8]}-{basename}` key (builder.py:1772-1776) — a
   collision-avoidance digest paired with a human-readable basename — except Sphinx's own version
   has the **same unbounded-length gap** v0.9.1 must close (Sphinx has never hit it in practice
   because `latex`/`html` builders don't relocate arbitrary-URI images the way typsphinx's
   third-party-extension rehome path does).
3. **pip's wheel cache** (documented behaviour, `pip cache dir` / Simon Willison's TIL,
   cross-checked against pip's own docs): `wheels/<hash>/<hash>/<hash>/<original-filename>.whl` —
   hash-bucketed **directories**, original filename kept **byte-for-byte** as the leaf component.
   Same shape again: hash for uniqueness, human-readable name preserved, not mangled.

**Convergent convention across all three:** the collision-avoidance token (counter or hash) is
kept **separate** from the human-readable name rather than replacing it, and the human-readable
portion is preserved **in full** wherever the tool doesn't hit a hard filesystem limit — none of
the three precedents truncate, because none of them anchors the digest to the *whole* original
identifier (URL, absolute path) the way typsphinx's IMG-03 digest already correctly does
(`hashlib.sha1(resolved_uri.encode()).hexdigest()[:8]`, builder.py — a comment there already notes
this is deliberately "a pure function of resolved_uri alone", so injectivity is not at risk from
truncating the *basename* half of the key). **Truncating only the basename half while keeping the
8-hex-char digest intact preserves both properties this milestone needs**: collision-avoidance
(digest, untouched) and human recognizability (as much of the original name as the length budget
allows). No warning text is warranted for the truncation itself — silent, by the same convention
as cases 1 and 2 above, which is also consistent with the "SILENTLY" wording already in
`_track_image()`'s own docstring for its D-01 collision branch. (The **escape** branch is the one
that already warns, per D-05/D-06 — truncation is orthogonal to escape and should not borrow its
warning.)

**Length bound:** the standard, portable filesystem limit both ext4 and NTFS enforce is 255 bytes
per path *component* (not per path). A conservative bound (well under 255, leaving room for the
`{digest8}-` prefix and any multi-byte UTF-8 basename characters) is the correct target — this is
an implementation detail for the roadmap/plan stage, not a research finding requiring a specific
number here.

### (c) Quoting a filesystem path in a diagnostic — `repr()`/`!r` is wrong for Windows paths, for a documented reason

Verified directly, not from memory:
```python
>>> repr(r"C:\Users\foo")
"'C:\\\\Users\\\\foo'"        # displays as 'C:\\Users\\foo' — backslashes DOUBLED
>>> repr(r"C:\Users\foo's file")
'"C:\\\\Users\\\\foo\'s file"'  # repr() DOES switch quote character ' -> " when the
                                  # string contains ' and not " (quote-disambiguation) —
                                  # but STILL doubles every backslash regardless of which
                                  # quote character it picked
```
This is the exact hazard the milestone context names: `!r` is correct for *identifiers* (docnames,
registry keys, config tuples — values a user typed as Python source, where doubled backslashes are
either absent or already meaningful) and wrong for *filesystem paths* (values that came from the
OS, where a doubled backslash is pure visual noise the user did not write and must mentally
undo). Confirmed from the installed **mypy** source
(`.venv/lib/python3.13/site-packages/mypy/build.py:4296`,
`.venv/lib/python3.13/site-packages/mypy/modulefinder.py:92`) that the convention among Python
static-analysis/tooling diagnostics is to quote paths and module names with **double quotes**,
verbatim, no escaping applied to the interpolated value at all:
```python
f'Duplicate module named "{st.id}" (also at "{graph[st.id].xpath}")'
msg = 'Cannot find implementation or library stub for module named "{module}"'
```
mypy does not defend against an embedded `"` in its own diagnostics either — this class of tooling
generally accepts that a pathological path (one containing the chosen delimiter) is a rare enough
edge case that it is handled by *picking* a safe delimiter for the common case rather than by
building a general escaping scheme.

**What this means for the required helper:** the correct shape — already implied by PROJECT.md's
own language ("the quote-disambiguation `repr()` provided ... dropped") — is `repr()`'s **quote
selection** algorithm (prefer `'`; switch to `"` if the string contains `'` and not `"`; escape a
literal `'` only when both are present) applied to the **raw path text**, without also running
`repr()`'s backslash-doubling step. That is: pick a delimiter unambiguous for the specific string,
then interpolate the path verbatim inside it — never `!r` (doubles backslashes) and never a
hardcoded `'...'` f-string (breaks the moment the path contains an apostrophe, which is exactly
57-REVIEW WR-01, a real regression 57-11 already introduced once).

### (d) What Typst's `image("...")` actually accepts — measured with a real `typst.compile()` in this repo

Ran directly against the `typst-py` version already pinned in this project's `.venv`
(`uv run --project /home/yuta/Documents/typsphinx python3 -c "import typst; typst.compile(...)"`),
against real files on disk (a synthesized 1×1 PNG), not documentation alone:

| Typst source | Compiles? | Error |
|---|---|---|
| `#image("images/normal.png")` (forward slashes, real file) | **Yes** | — |
| `#image("images\slash.png")` (one literal backslash in the string) | **No** | `TypstError: path must not contain a backslash` |
| `#image("images\\slash.png")` (an *escaped* backslash — decodes to the same one literal backslash character, pointed at a real file literally named `back\slash.png` which POSIX filesystems permit) | **No** | `TypstError: path must not contain a backslash` |
| `#image("images/quo'te.png")` (unescaped single quote, no such file) | Parses fine, fails on lookup | `TypstError: file not found (searched at .../images/quo'te.png)` |
| `#image("images/quo"te.png")` (unescaped double quote — breaks the string literal itself) | **No** | `TypstError: unclosed delimiter` |

**The critical finding, decisive for how defect family 2 must be fixed:** Typst's rejection is
**value-level**, not syntax-level. Escaping the backslash so it survives Typst's own string-literal
parsing (`\\` in source → one `\` in the decoded string) does **not** help — Typst decodes the
literal first and then refuses the *resulting path string* because it contains a backslash
character at all, in any position, whether used as a directory separator or as an ordinary
character inside a filename. `escape_typst_string()` (translator.py:156) is therefore **necessary
but not sufficient** for this defect: it must be applied at the two emission sites
(translator.py:4746, 4749) for defense-in-depth against other syntax-breaking characters (quotes,
newlines) already handled correctly for the plain-URI path, but it **cannot** by itself make a
backslash-bearing path acceptable to Typst — the backslash has to be gone from the *value* before
it ever reaches the string literal.

I traced why a backslash currently survives into that value even though this project runs its
Windows-affecting logic on Linux CI: `builder.py` imports `from os import path` (platform-native,
line 12) — **not** `posixpath`, which the file also imports separately and uses elsewhere (e.g.
`_is_absolute_image_uri()`, `_escapes_outdir()`). `_track_image()`'s escape branch builds its
relocation key with `path.basename(resolved_uri)` (builder.py:1772), and confirmed directly:
```python
>>> from os import path
>>> path.basename(r"C:\Users\x\img.png")   # on this POSIX CI runner
'C:\\Users\\x\\img.png'                     # unsplit — posixpath.basename only splits on "/"
>>> path.basename("C:/Users/x/img.png")
'img.png'                                    # splits correctly once slashes are forward
```
On the `windows-latest` CI lane, `path` resolves to `ntpath` and this same call *would* split
correctly — which is exactly why the milestone context notes "the `windows-latest` lane is green
at HEAD and would stay green if nothing were fixed" (the gap is invisible unless a gate constructs
a Windows-shaped URI and runs it through the POSIX-native code path, or runs a real backslash
end-to-end through `typst.compile()` on Windows). The fix for the relocation-key half of this
defect is therefore **normalize before `path.basename()`, the same idiom `_is_absolute_image_uri()`
already uses** — not a change to `escape_typst_string()`'s own escaping rules.

## Feature Landscape

### Table Stakes (must ship in v0.9.1 — required to close the three named defect families)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `_escapes_outdir()` normalizes `stem` (backslash→`/`) before applying `posixpath.isabs()` / `_is_drive_qualified()`, matching `_is_absolute_image_uri()`'s existing idiom | A driveless-absolute Windows-shaped target (`\manuals\guide`) must be refused exactly like its POSIX-shaped equivalent (`/manuals/guide`) already is — cross-platform-correctness is this project's own stated contract (D-05 in `_escapes_outdir()`'s own docstring) | LOW | Single-function fix: `builder.py:238`. `segments` (line 230) is already built from the normalized string — only the two predicate calls on the raw `stem` need to switch to the normalized value. Gate must be RED-first (currently no test drives a driveless-absolute Windows-shaped stem) |
| Relocation key built from a **normalized** (forward-slash) basename, not `os.path.basename()` on a possibly-Windows-shaped raw URI | Root cause of defect family 2's compile failure — see (d) above. The key must never carry a literal `\` into the value that reaches `image("...")` | LOW-MEDIUM | `_track_image()`'s escape branch, `builder.py:1772`. Same normalize-before-decide idiom as the `_escapes_outdir()` fix — a shared helper for "normalize a possibly-foreign-shaped URI's basename" is a reasonable single source of truth for both this and the length-bound truncation below |
| `escape_typst_string()` applied at both `image("...")` emission sites | Defense-in-depth for the *other* syntax-breaking characters a basename can legally contain (`"`, embedded newlines from a pathological third-party URI) — proven necessary in general by the `unclosed delimiter` result in the (d) table, even though it does **not** by itself fix the backslash defect | LOW | `translator.py:4746` and `:4749`. Must land together with the key-normalization fix above — escaping alone leaves the backslash-refusal in place, per (d) |
| Relocation key's basename half truncated against a length bound, digest (`{digest8}-`) kept intact and un-truncated | `ENAMETOOLONG` at `copy_image_files()` time for a long basename; the digest is the only injective/collision-avoidance element (IMG-03 comment: "a PURE function of resolved_uri alone") and must never be the truncated half | MEDIUM | Same call site as above (`builder.py:1772-1776`). Sphinx's own `DownloadFiles` has an identical unbounded-length gap (see (b)) — no upstream precedent to crib the exact bound from; pick a conservative bound under the portable 255-byte-per-component filesystem limit. **No compile-visible symptom** (PROJECT.md constraint 3) — needs its own gate, a compile gate will not surface this |
| One path-quoting helper: `repr()`'s quote-disambiguation (prefer `'`, switch to `"` if the value contains `'` and not `"`) applied to the raw path text, with **no** backslash-doubling | Verified in (c): plain `!r` doubles backslashes (wrong for Windows paths); a hardcoded `'...'` breaks on an embedded apostrophe (57-REVIEW WR-01, a real prior regression). Neither is correct in isolation | MEDIUM | New helper, routed through all ~13 call sites the milestone's own census names: `builder.py:942,964,965,999,1007,1008,1015,2056,2066,697,1767`, `writer.py:511-513`, `template_registry.py:410,422,433`. Identifier-valued `!r` sites (registry keys, docnames, config tuples) are explicitly **out of scope** and must stay `!r` |
| Both quoting-gate halves pass | The existing no-doubled-separator property (`TestWindowsPathEscapingRegressionGuard`, `tests/test_templates_path_collision_gate.py`) plus the missing case 57-REVIEW IN-01 names: a path containing a literal `'`, delimited unambiguously | LOW (test-only; implementation is the helper above) | Both halves must gate the *same* helper, not two independently-passing partial implementations |
| POSIX output byte-identical to pre-fix | Constraint 5 — proven the way 57-11 proved it: zero test edits to existing POSIX-only assertions | N/A (verification discipline, not a feature) | Applies to all four fixes above |

### Differentiators (beyond the minimum bar — worth doing if cheap, not required to close the named defects)

| Feature | Value Proposition | Complexity | Notes |
|---------|--------------------|------------|-------|
| Quoting helper also handles a path containing **both** `'` and `"` (repr()'s own fallback: pick `'`, backslash-escape only the `'` characters) | Slightly more robust than the minimum the milestone's own gate (57-REVIEW IN-01) requires — real Windows paths can never contain `"` at all (it's a reserved character NTFS/Windows itself refuses), so this case is nearly unreachable in production, but costs almost nothing once the quote-selection logic already exists | LOW (incremental over the table-stakes helper) | Purely a robustness margin — do not let it expand the helper's scope beyond "select delimiter, interpolate raw" |
| Shared "normalize a possibly-foreign-shaped basename" helper used by *both* the relocation-key fix and any future Windows-shaped-input fix elsewhere in the codebase | Single source of truth, same rationale `_is_absolute_image_uri()` and `_escapes_outdir()` already share | LOW | Nice factoring, not required — the three sites could each inline `.replace("\\", "/")` and still close the defect |

### Anti-Features (would seem plausible, explicitly do NOT do)

| Anti-Feature | Why It Seems Appealing | Why Problematic | Correct Alternative |
|---|---|---|---|
| Silently rewrite/sanitize a Windows-shaped escaping `typst_documents` target into a derived relative path, no warning | Matches the surface behaviour of "just make it work" | This project has **already decided** (pre-milestone) on refuse-loudly + fallback-to-basename for `_escapes_outdir()`'s escape cases; silently rewriting would hide a real config mistake from the author and contradicts the existing OUT-02 contract this milestone is only extending to Windows shapes, not revisiting | Keep the existing refuse+fallback+warn behaviour; only fix the *detection* (normalize before deciding) |
| Copy Sphinx's own `latex_documents` policy of validating nothing | Sphinx is the closest upstream precedent and does literally zero path-shape validation (see (a)) | typsphinx already exceeds that bar; reverting to Sphinx's laissez-faire policy for consistency-with-upstream would be a regression the project has never asked for | Treat Sphinx's silence as evidence there is no external convention to defer to — keep typsphinx's stricter, already-built guard |
| Use `!r` (bare `repr()`) for path-valued interpolation, for consistency with the identifier-valued sites | Looks uniform, `!r` is already used everywhere else in the file for identifiers | Doubles every backslash in a Windows path (verified in (c)) — directly reintroduces the class of defect this milestone exists to close | The new delimiter-aware helper, routed through path-valued sites only; identifier-valued `!r` stays untouched |
| Hardcode a `'...'` f-string delimiter around a path (57-11's original approach) | Simple, one extra character | Breaks the moment the path contains an apostrophe — this is exactly 57-REVIEW WR-01, a real regression already caught once | The quote-disambiguation helper (table stakes, above) |
| Generalize the relocation-key fix into full illegal-character sanitization for *all* Windows-reserved filename characters (`<>:"|?*`, reserved device names `CON`/`PRN`/`AUX`/`NUL`/`COM1-9`/`LPT1-9`) | Feels like "doing Windows path handling properly" while already in this code | Out of scope: none of these has a demonstrated compile-visible or copy-time failure the way backslash (Typst-level refusal) and length (`ENAMETOOLONG`) do; PROJECT.md's own defect-family enumeration names exactly two vectors for gap 2/3, not a general filename-sanitization pass | Leave as an explicit gap for a future milestone if a real report surfaces one of these characters in practice; do not speculatively build for it now |
| Try to make the quoting helper losslessly round-trip *any* path (e.g. full shell-style escaping) | Feels more "correct" | No comparable tool (Sphinx, pip, mypy — see (c)) attempts this for human-facing diagnostics; the convention is delimiter selection for the common case, not general escaping | Delimiter-disambiguation only, matching the ecosystem convention actually observed |

## Feature Dependencies

```
Defect family 1 (escape-outdir normalization)
    -- independent of families 2 and 3, single-function change (builder.py:238)

Defect family 2 (image path safety)
    [Normalize basename before path.basename()] ──required-precondition-for──> [Length-bound truncation]
                                                                                     (truncation must act on
                                                                                      the ALREADY-normalized
                                                                                      basename, else it could
                                                                                      truncate mid-backslash-
                                                                                      run and reintroduce noise)
    [Normalize basename before path.basename()] ──insufficient-alone,-needs──> [escape_typst_string() at
                                                                                  both emission sites]
        (see (d): escaping the backslash in Typst source does NOT stop Typst's
         value-level refusal -- normalization removes the backslash from the
         VALUE; escaping is still needed for OTHER syntax-breaking characters)

Defect family 3 (path-quoting helper)
    -- independent of families 1 and 2; one helper, ~13 call sites, two gate halves
       (no-doubled-separator + embedded-single-quote) must both pass against the
       SAME helper implementation, not two partial ones
```

### Dependency Notes

- **Family 2's two sub-fixes are not substitutable for each other.** Landing only the
  `escape_typst_string()` call (translator.py:4746/4749) without normalizing the relocation key
  (builder.py:1772) still fails to compile — proven by the `test2_escaped_backslash.typ` result in
  the (d) evidence table, where an *escaped* backslash still triggers `path must not contain a
  backslash`. Landing only the key normalization without adding `escape_typst_string()` closes the
  named defect but leaves the general syntax-breaking-character gap (`"` in a basename) unguarded —
  both must ship in the same slice per PROJECT.md's own framing ("All three `_track_image()`
  escape-branch gaps close in one slice").
- **Truncation must run after normalization**, not before — truncating a not-yet-normalized
  Windows-shaped basename risks truncating in the middle of a backslash run rather than a clean
  forward-slash-delimited path segment, which would produce a nonsensical partial filename.
- **The quoting helper (family 3) has no ordering dependency on families 1/2** — it touches
  different files (`writer.py`, `template_registry.py`, unrelated `builder.py` warning sites) and
  can be built and gated independently, though all three share the same underlying "Windows path
  correctness" root cause and are reasonably sequenced together for the milestone's single
  3-OS-CI acceptance bar (constraint 6).

## Sources

- `sphinx.builders.latex` — read directly from the installed Sphinx 9.1.0 package
  (`.venv/lib/python3.13/site-packages/sphinx/builders/latex/__init__.py`, lines 151-175, 299-350,
  417-505, 526-533). HIGH confidence (primary source, this repo's own pinned dependency).
- `sphinx.util._files.FilenameUniqDict` / `DownloadFiles` — read directly
  (`.venv/lib/python3.13/site-packages/sphinx/util/_files.py`, full file). HIGH confidence.
- `sphinx.util.osutil.make_filename` / `_no_fn_re` — read directly
  (`.venv/lib/python3.13/site-packages/sphinx/util/osutil.py:147-155`). HIGH confidence.
- pip wheel cache layout — [pip cache CLI docs](https://pip.pypa.io/en/stable/cli/pip_cache/) and
  [Simon Willison's TIL on the pip cache directory](https://til.simonwillison.net/python/pip-cache),
  cross-checked against the documented `wheels/<hash>/<hash>/<hash>/<name>.whl` layout. MEDIUM
  confidence (web source, but corroborated by two independent descriptions and consistent with
  pip's own documented "makes a subdirectory... places the resulting wheels inside" behaviour).
- mypy diagnostic quoting — read directly from the installed mypy package
  (`.venv/lib/python3.13/site-packages/mypy/build.py:4296`,
  `.venv/lib/python3.13/site-packages/mypy/modulefinder.py:92,95`). HIGH confidence (primary
  source, this repo's own pinned dev dependency).
- Python `repr()` quote-selection and backslash-doubling behaviour — measured directly,
  `python3` one-liners in this repo's environment (see (c) above for the exact transcript). HIGH
  confidence (reproduced, not recalled).
- Typst `image("...")` path acceptance — measured directly with `typst.compile()` against the
  `typst-py` version pinned in this repo's `.venv`, using synthesized real PNG files on disk (see
  (d) above for the full transcript, including the exact `TypstError` strings). HIGH confidence
  (reproduced against this repo's own pinned Typst version, not documentation-only).
- typsphinx's own `builder.py` / `translator.py` — read directly at the line ranges the milestone
  context names (`_escapes_outdir` builder.py:190-300, `_track_image` builder.py:1650-1800,
  `escape_typst_string` translator.py:156-186, `visit_image` translator.py:4718-4760). HIGH
  confidence (primary source, this repository).

---
*Feature research for: typsphinx v0.9.1 "Windows path correctness"*
*Researched: 2026-08-27*
