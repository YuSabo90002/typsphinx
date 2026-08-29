# Phase 59: Path-Shape Predicate and Image-URI Correctness - Research

**Researched:** 2026-08-28
**Domain:** Path-shape classification, filesystem-safe key construction, and Typst string-literal
escaping in a Sphinx→Typst build tool (stdlib-only bug-fix; zero new runtime dependencies)
**Confidence:** HIGH — every claim below is either read directly from `typsphinx/builder.py` /
`typsphinx/translator.py` at HEAD this session, executed live in this worktree's `.venv`, or copied
verbatim from `59-CONTEXT.md`'s own 2026-08-28 measurements (never re-derived).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

The owner selected **"おすすめで進める"** for all four gray areas, so every D-NN below is Claude's
recommendation locked as a decision. Every value marked *measured* was taken **this session
(2026-08-28)** against the live tree at `7d809b83` — including four real `typst.compile()` runs
through the project's own `.venv` typst-py — not from recall.

**IMG-07 — what the compile gate compiles**

- **D-01:** The gate's image URI is a real file whose basename carries BOTH a backslash and a
  double quote. Measured four `typst.compile()` runs: `image("dir\logo.png")` → `TypstError: path
  must not contain a backslash`; `image("dir\\logo.png")` (escaped, decodes to one `\`) → the SAME
  error; `image("we"ird.png")` → `TypstError: unclosed delimiter`; `image("we\"ird.png")` → OK. A
  URI whose normalized basename is `we"ird.png` and whose raw basename is `sub\we"ird.png` makes
  both halves load-bearing in all four combinations (unfixed → backslash error; IMG-04-only →
  unclosed delimiter; IMG-05-only → backslash error; both → compiles). Reversible.
- **D-02:** The gate is an end-to-end `sphinx-build -b typstpdf` run, not a hand-written `.typ`.
  Modelled on `tests/test_absolute_image_render_gate.py`, `-b typstpdf` on purpose (the fatal only
  aborts on `TypstPDFBuilder.finish()`'s compile path), with a fixture `conf.py` registering a small
  post-transform rewriting `node["uri"]` to the absolute path of a file created outside `doctreedir`.
  The file must genuinely exist — `copy_image_files()` copies from `self.images[key]` and skips with
  `Image file not found` otherwise. Reversible.
- **D-03:** The compile gate skips on a filesystem that cannot hold the name, probed — never on
  `os.name`. Measured on this machine (ext4): `open(r'dir\we"ird.png', "wb")` succeeds; both `\` and
  `"` are illegal in a Windows filename, so `windows-latest` cannot construct the fixture. The skip
  condition is an attempted `tmp_path` create wrapped in `except OSError`, with the reason recorded
  in the skip message. `pytest.mark.skipif(os.name == "nt")` is rejected. Reversible.
- **D-04:** A POSIX-runnable string-shape gate runs on EVERY lane alongside it. It asserts on the
  emitted `.typ` body from a `-b typst` build (no compile, no fixture file needed): the `image("...")`
  literal for a Windows-shaped absolute URI contains no raw backslash, and a `"` in the path appears
  escaped. The proven `TestWindowsPathEscapingRegressionGuard` pattern
  (`tests/test_templates_path_collision_gate.py:411-470`). Reversible.
- **D-05 (AMENDED):** ROADMAP constraint 5's "neither fix alone closes the compile failure" is half
  true. Escaping alone does not close it (Typst refuses by value). IMG-04 alone DOES close a
  backslash-only URI. No roadmap edit requested — D-01's fixture makes the conjunction genuinely
  necessary so SC#2's wording holds literally. Do not re-derive the claim from the constraint text
  and pick a backslash-only fixture that quietly makes SC#2 unprovable. Reversible.

**IMG-06 — where the 255-byte bound lands and how it is gated**

- **D-06:** The bound applies to the FINAL PATH COMPONENT as a whole (`{digest}-{basename}`), not to
  the basename alone. Measured on ext4: a 250-byte basename is creatable; `{sha1[:8]}-` adds 9 bytes;
  the resulting 259-byte component fails with `OSError 36 (ENAMETOOLONG)`. Budget for the basename is
  `255 - len(f"{digest}-")` = 246 bytes. Reversible.
- **D-07:** Truncation keeps the digest whole, keeps the extension, truncates the stem from the
  right, lands on a UTF-8 character boundary, and never yields an empty stem. Precedence when the
  budget is tight: digest+`-` first, then at least one byte of stem, then the extension (truncated
  too if it alone would consume the whole remaining budget). Boundary safety by encode-then-decode
  with `errors="ignore"` or an explicit continuation-byte walk — never by slicing the `str` and
  hoping. Reversible.
- **D-08:** IMG-06 needs TWO gates, because `copy_image_files()` swallows the `OSError`
  (`builder.py:1988-1992` wraps `shutil.copy2` in `except Exception as e` and logs
  `f"Failed to copy image {imguri}: {e}"`). (a) a pure-string unit gate, all lanes, no filesystem:
  call the key construction directly and assert `len(component.encode("utf-8")) <= 255`, digest
  intact, extension preserved, stem non-empty, boundary-safe — this is also where SC#3's collision
  property is re-proven for two long URIs sharing a basename; (b) an integration gate through a real
  `sphinx-build` asserting the pre-fix `Failed to copy image …: [Errno 36] File name too long`
  warning and the absent destination file, both gone after the fix. Reversible.

**PATH-01 — how "byte-identical at both call sites" is proven**

- **D-09:** Split by what each mechanism can observe — a permanent characterization test for the
  post-fix classification, a recorded two-tree measurement for the "before and after" half. The
  suite gets: the direct-call RED gate for the two shapes that flip (`\manuals\guide` and
  `\\srv\share\g`, both `False → True`), plus a characterization pin parametrized over the full shape
  table at both production call sites (`_resolve_target_stem()` at `builder.py:662`, `_track_image()`
  at `builder.py:1727`). The evidence file records the same table run against the pre-fix tree and
  shows the two outputs byte-identical. Reversible.
- **D-10:** The characterization pin goes through the call sites, the RED gate does not. ROADMAP
  constraint 8 forbids routing PATH-01's gate through either call site (both pre-normalize or always
  carry a `..`, tautologically green). That prohibition is about the gate; the characterization pin's
  job is the opposite — it must run through the call sites. Reversible.

**Cross-cutting**

- **D-11:** Evidence file is `59-WINDOWS-URI-EVIDENCE.md` — NOT `59-VERIFICATION.md` (`gsd-verifier`
  reserves and overwrites that name wholesale). Reversible.
- **D-12:** The drive-colon case (`C:logo.png`) is DEFERRED, not folded in — IMG-04 stays at its
  literal scope. Measured: `posixpath.basename("C:logo.png".replace("\\", "/"))` returns `C:logo.png`
  — the colon survives normalization and is illegal in NTFS, but this shape arises only for the
  drive-relative form (no separator after the colon), which no Sphinx image post-transform produces.
  Recorded in Deferred Ideas with the measurement. Reversible.
- **D-13:** IMG-05's escaping is computed ONCE, immediately after `_compute_relative_image_path()`,
  and used by both `add_text` sites (`translator.py:4746` in-figure, `:4749` standalone). One
  `escaped_uri = escape_typst_string(adjusted_uri)` on the line after 4742 makes "last" structural.
  Measured consequence for zero-test-edits: `escape_typst_string()` is a no-op for any path containing
  neither `\` nor `"` nor a control character, so every existing expected `image("...")` output stays
  byte-identical. Reversible.

### Claude's Discretion

- Plan decomposition within the constraint-3 rule (the three `builder.py` changes are one sequential
  plan; `translator.py` is parallel-safe alongside it; IMG-07's compile gate is the wave after).
- Whether the key-construction logic is extracted into a module-level helper (making D-08(a)'s
  pure-string gate a direct call rather than a build) or stays inline in `_track_image()`.
- Fixture and test-module naming, and whether D-04's all-lane string gate lives in a new module or
  joins an existing Windows-shape test class.
- The exact boundary-safe truncation idiom, provided D-07's precedence order holds.

### Deferred Ideas (OUT OF SCOPE)

- **The drive-relative colon in a relocation key (D-12).** Sized as its own future requirement
  (~2 lines in the key construction, reusing `_is_drive_qualified()`, plus one test case).
- **The non-escape key branches can still carry a backslash on POSIX.** `key = rel_uri` at
  `builder.py:1783` (`relpath(...).replace(path.sep, "/")`) — on a POSIX host `path.sep` is `/`, so a
  filename with a literal backslash survives into the emitted `image()` and Typst refuses it by
  value, which escaping cannot fix either. IMG-04 names the escape branch only. Record, don't widen.
- **A path containing a literal single quote (`57-REVIEW.md` IN-01).** Belongs to MSG-02's gate in
  Phase 60, unrelated to this phase's D-01 `"` fixture (that one is about the Typst string literal,
  not message quoting).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-------------------|
| PATH-01 | `_escapes_outdir()` applies its absolute-path/drive-qualified checks to the backslash-normalized string, matching `_is_absolute_image_uri()`'s idiom. Not reachable from either production call site — hardening the predicate's own contract. | § Code Examples "PATH-01 rewrite" (verified this session); § Architecture Patterns "Normalize-then-decide"; D-09/D-10 govern the two-gate split. |
| IMG-04 | `_track_image()`'s escape branch builds its relocation key from a forward-slash-normalized basename — no backslash from the original URI survives into the key. | § Code Examples "IMG-04/IMG-06 combined key construction"; § Common Pitfalls "digest must hash the raw, unnormalized `resolved_uri`". |
| IMG-05 | `visit_image()` routes `_compute_relative_image_path()`'s return value through `escape_typst_string()` before interpolation — escape runs last, on the routed value, not the raw `uri`. | § Code Examples "IMG-05 escape-last wiring"; D-13 (single computation point for both `add_text` sites). |
| IMG-06 | The relocation key's final path component is bounded to 255 UTF-8 bytes with the `{sha1[:8]}-` digest kept whole; truncation lands on a UTF-8 boundary, never empties the stem, preserves the extension. | § Code Examples "255-byte boundary-safe truncation" (verified this session, three shapes: ASCII, CJK, extension-exceeds-budget); § Validation Architecture Wave 0 gaps (a)/(b). |
| IMG-07 | A real `typst.compile()` proves a Windows-shaped absolute image URI now compiles, with IMG-04 and IMG-05 both load-bearing per D-01's fixture table. | § Code Examples "D-03 filesystem probe idiom" (verified this session); § Common Pitfalls "skipif cannot see fixtures — probe belongs inside the test body"; existing `tests/test_absolute_image_render_gate.py` as the structural template. |
</phase_requirements>

## Summary

This phase closes three related latent Windows-path defects clustered in a ~30-line region of
`typsphinx/builder.py` plus one paired fix in `typsphinx/translator.py`, and adds the milestone's
one real-compile gate. All findings in `59-CONTEXT.md` are treated as given (measured 2026-08-28
against `7d809b83`); this document adds only what that CONTEXT.md does not already carry: a
Validation Architecture mapping requirements to concrete, verified test commands; runnable, verified
code sketches for the three non-trivial transforms (the normalize-then-decide predicate rewrite, the
combined normalize+bound key construction, and the boundary-safe truncation); four pitfalls the
CONTEXT.md's five "Specific Ideas" do not name; and an ASVS L1 security mapping.

The whole phase is stdlib-only (`hashlib`, `posixpath`, `os.path`) — zero new runtime dependency, so
the Package Legitimacy Gate is not applicable. The single hardest engineering constraint is ordering:
normalize the URI to forward slashes FIRST, extract the basename SECOND (via `posixpath.basename`,
never `path.basename` on a POSIX host, which is `posixpath` and does not split on `\`), split the
extension THIRD, apply the 255-byte bound FOURTH — and the digest that anchors collision-avoidance
must be computed over the ORIGINAL, un-normalized `resolved_uri` (unchanged by this phase), never the
normalized string, to avoid silently changing the collision key's formula for a shape no current test
pins.

**Primary recommendation:** Implement `_escapes_outdir()`'s normalize-then-decide rewrite,
`_track_image()`'s combined normalize+truncate key construction, and `visit_image()`'s escape-last
wiring exactly as sketched in § Code Examples below (each block was executed in this worktree's
`.venv` this session and produces the byte counts / boundary safety the CONTEXT.md's D-06/D-07 specify)
— then gate them with the five requirement-mapped test commands in § Validation Architecture, in the
wave order § Architectural Responsibility Map and the CONTEXT.md's own decomposition discretion imply.

## Architectural Responsibility Map

This project's pipeline is not a web-tiered application; the "tiers" below are this codebase's own
documented pipeline stages (`CLAUDE.md` § Architecture): **doctree → TypstTranslator → body string →
TemplateEngine → .typ file → [PDF compile]**, with `TypstBuilder` orchestrating the write loop and
image copying around that pipeline.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Path-shape classification (`_escapes_outdir`, `_is_absolute_image_uri`, `_is_drive_qualified`) | Builder (`builder.py`) | — | Pure string predicates with no filesystem/OS dependency, consumed only by Builder-tier callers (`_resolve_target_stem`, `_track_image`). |
| Relocation-key construction (normalize + digest + 255-byte bound) | Builder (`builder.py`, `_track_image`) | — | The key is written into `node["uri"]` and `self.images`, both Builder-owned state; the Translator only reads the already-constructed key. |
| Image file copy (`copy_image_files()`) | Builder (`builder.py`) | Filesystem | Consumes the same key IMG-04/IMG-06 construct; IMG-06's `ENAMETOOLONG` surfaces here, not at the Translator or compile boundary. |
| Typst string-literal escaping at image emission (`visit_image`) | Translator (`translator.py`) | — | `escape_typst_string()` is the Translator's single source of truth for string-literal safety; the Builder never touches emitted `.typ` syntax. |
| Compile-time validation (`typst.compile()`) | PDF compile (`pdf.py` / `typst-py`, driven by `TypstPDFBuilder.finish()`) | — | The only tier that can observe Typst's VALUE-level (not syntax-level) backslash refusal — an assertion stopping at `node["uri"]` or the emitted `.typ` text cannot see it (IMG-07's whole reason to exist). |

**Sanity check for the planner:** IMG-04/IMG-06 belong entirely inside the Builder tier — there is no
reason for either fix to touch `translator.py`, and no reason for IMG-05's escape-routing fix to touch
`builder.py`. A plan that crosses this boundary (e.g. normalizing backslashes inside `visit_image()`)
is the exact anti-pattern PITFALLS.md Pitfall 4 names — silently rewriting emitted CONTENT, not
classifying it, changing which file Typst opens.

## Standard Stack

### Core

No new dependency. This phase is stdlib-only by construction (per REQUIREMENTS.md's milestone
framing and `59-CONTEXT.md`'s own "zero new dependencies" statement, § Established Patterns).

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|---------------|
| `hashlib` (stdlib) | 3.12+ | SHA-1 digest for the relocation key's collision anchor (unchanged this phase — already in use) | Already the sole hashing dependency in `builder.py`; no alternative considered |
| `posixpath` (stdlib) | 3.12+ | Platform-independent path-shape classification (`isabs`, `basename`) | Established idiom in this codebase (`_is_absolute_image_uri`, `_escapes_outdir`) — `ntpath`/OS-native `path` diverges between CPython 3.12 and 3.13 (`builder.py:121-165` docstring, measured) |
| `typst` (typst-py) | `>=0.15.0,<0.16` (`pyproject.toml:30`) [VERIFIED: pyproject.toml:30] | Real `typst.compile()` for the IMG-07 gate | Already the project's sole PDF-compile dependency; confirmed importable in this worktree's `.venv` this session (`import typst` succeeded, module resolved to `.venv/lib/python3.13/site-packages/typst/__init__.py`) |

**Version verification:** `typst` is pinned `>=0.15.0,<0.16` at `pyproject.toml:30` [VERIFIED:
pyproject.toml:30] and confirmed importable in-worktree this session — no version bump needed or
proposed by this phase.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|-----------|
| `posixpath.isabs()` + `_is_drive_qualified()` composite | `pathlib.PureWindowsPath` | Rejected by prior research (SUMMARY.md § STACK.md findings): introduces a different classification boundary than the one already established in this file, and does not solve the CPython 3.12-vs-3.13 `ntpath.isabs()` divergence the composite predicate exists to sidestep |
| Hardcoded `255`-byte bound | `os.pathconf()` / `os.statvfs()` live probe | Rejected by owner decision (REQUIREMENTS.md IMG-06, "Constant, not a probe"): both are `Availability: Unix`-only and unusable on the `windows-latest` CI lane |

**Installation:** None — no new package. `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra
dev` in each worktree resolves the existing committed `uv.lock` only (CLAUDE.md's mandatory
per-worktree provisioning step).

## Package Legitimacy Audit

**Not applicable.** Zero new packages proposed by this phase — confirmed by direct inspection of
`pyproject.toml` (no diff needed; the phase's own scope statement in `59-CONTEXT.md` § Phase Boundary
names `builder.py`, `translator.py`, and new test modules as the whole write surface) and by the
Standard Stack table above, which lists only already-pinned stdlib/`typst-py`.

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

## Architecture Patterns

### System Architecture Diagram

```
Sphinx doctree (node["uri"])
        │
        ▼
TypstBuilder.post_process_images(doctree)          ◄── Builder tier
        │  walks nodes.image, calls _track_image() per node
        ▼
_track_image(node, resolved_uri)
        │
        ├─► _is_absolute_image_uri(resolved_uri)?  ── No ──► store resolved_uri as-is, return
        │       │ Yes
        │       ▼
        │   rel_uri = relpath(resolved_uri, doctreedir).replace(sep, "/")
        │       │
        │       ▼
        │   _escapes_outdir(rel_uri)  ◄── PATH-01 hardens THIS predicate's own contract
        │   (both call sites already pre-normalize before this call — the fix changes
        │    neither call site's live classification; see PATH-01's reachability note)
        │       │
        │  ┌────┴─────┐
        │  │ escaped?  │
        │  └────┬─────┘
        │   Yes │            No (real collision) │            No (clean) │
        │       ▼                                 ▼                       ▼
        │  ┌─────────────────────┐        key = "_typst_converted/"    key = rel_uri
        │  │ IMG-04: normalize    │        + rel_uri  (unchanged)      (unchanged)
        │  │ raw URI to "/" FIRST,│
        │  │ posixpath.basename() │
        │  │ SECOND               │
        │  │                      │
        │  │ IMG-06: split ext,   │
        │  │ bound {digest}-{stem}│
        │  │ to 255 UTF-8 bytes,  │
        │  │ digest anchor intact │
        │  └──────────┬───────────┘
        │             ▼
        │   key = "_typst_converted/{digest}-{bounded-basename}"
        │   node["uri"] = key ; self.images[key] = resolved_uri (RAW, unmodified)
        ▼
copy_image_files()                                  ◄── Builder tier, filesystem boundary
        │  src = self.images[key] or path.join(srcdir, key)
        │  dest = path.join(outdir, key)
        │  shutil.copy2(src, dest)  ── IMG-06's OSError(ENAMETOOLONG) is swallowed here
        │                              (except Exception → logger.warning), D-08's reason
        │                              a compile gate alone cannot see it
        ▼
(separately, per doctree write)
TypstTranslator.visit_image(node)                   ◄── Translator tier
        │  uri = node["uri"]  (the key IMG-04/IMG-06 constructed)
        │  adjusted_uri = _compute_relative_image_path(uri, current_docname)
        │  IMG-05: escaped_uri = escape_typst_string(adjusted_uri)  ── escape LAST,
        │          on the routed return value, never on the raw uri before the call
        ▼
emitted `.typ`:  image("{escaped_uri}")
        ▼
TypstPDFBuilder.finish()  →  typst.compile()         ◄── PDF-compile tier
        │  IMG-07's gate: only tier that observes Typst's VALUE-level backslash refusal
        ▼
     PDF (or, pre-fix: `TypstError: path must not contain a backslash`)
```

### Recommended Project Structure

No new files under `typsphinx/` — this phase edits `builder.py` and `translator.py` in place. New
test files only:

```
tests/
├── test_path_shape_predicate_gate.py        # PATH-01: direct-call RED gate + characterization pin
├── test_track_image_key_construction.py     # IMG-04/IMG-06(a): pure-string key-construction gate
├── test_windows_image_uri_render_gate.py    # IMG-07/D-01..D-04: the real-compile gate + POSIX string-shape sibling
├── test_copy_image_files_name_too_long.py   # IMG-06(b): integration gate for the swallowed OSError
└── fixtures/
    └── windows_shaped_image_render_gate/    # D-02's fixture project (name is discretionary — Claude's Discretion)
        ├── conf.py
        ├── index.rst
        └── _static/
```

(Names above are illustrative — fixture/test-module naming is explicitly delegated to the planner
per `59-CONTEXT.md` § Claude's Discretion. What is NOT discretionary: the four gates must exist as
requirement-mapped, independently runnable pytest targets, per § Validation Architecture below.)

### Pattern 1: Normalize-then-decide (the established idiom this phase extends)

**What:** Convert every backslash to a forward slash FIRST, then apply a pure `posixpath`-based
classification (`isabs`, drive-qualified check, or basename extraction) to the NORMALIZED string —
never to the raw, platform-shaped input.
**When to use:** Any pure string-shape decision over a path that may have originated on a different
platform than the one running the code (this codebase's whole `_is_absolute_image_uri` /
`_escapes_outdir` family).
**Example (already-shipped sibling, `_is_absolute_image_uri`, `builder.py:194`):**
```python
# Source: typsphinx/builder.py:194 (verified this session, HEAD)
def _is_absolute_image_uri(resolved_uri: str) -> bool:
    normalized = resolved_uri.replace("\\", "/")
    return posixpath.isabs(normalized) or _is_drive_qualified(normalized)
```

### Pattern 2: Escape-last (Typst string-literal safety)

**What:** Every syntax-breaking transform on a value destined for a Typst `"..."` string literal
must be the LAST operation before interpolation — any transform applied afterward risks
reintroducing an unescaped `\` or `"`.
**When to use:** Any `add_text(f'...("{value}"...')` call in `translator.py` where `value` is
derived from user/filesystem-controlled text.
**Example (already-shipped, `escape_typst_string`, `translator.py:156`):**
```python
# Source: typsphinx/translator.py:156-183 (verified this session, HEAD)
def escape_typst_string(text: str) -> str:
    text = text.replace("\\", "\\\\")  # Backslash FIRST, avoids double-escaping
    text = text.replace('"', '\\"')
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "\\r")
    text = text.replace("\t", "\\t")
    return text
```
IMG-05's fix is a routing change onto this existing helper (D-13) — not a new escaper.

### Anti-Patterns to Avoid

- **Normalizing content, not just classification.** `.replace("\\", "/")` is safe at a
  classification boundary (a false positive there only triggers an unnecessary, well-tested rehome
  branch) but unsafe at an emission boundary — it silently changes WHICH FILE Typst opens. PITFALLS.md
  Pitfall 4 names this explicitly for `visit_image()`; the correct IMG-05 fix wraps the value in
  `escape_typst_string()` only, never adds a `.replace()` call at that site.
- **Bounding the basename alone, not the whole `{digest}-{basename}` component.** IMG-06's 255-byte
  limit is on the FULL final path component (D-06) — bounding only the basename to 255 produces a
  264-byte component that still raises `ENAMETOOLONG` (measured).
- **Slicing UTF-8-encoded bytes directly instead of the `str`.** Byte-slicing a multi-byte character
  in half produces invalid UTF-8, trading one opaque `OSError` for a different one. Size-check in
  bytes, slice in `str`/character space (see § Code Examples).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Windows/POSIX path-shape classification | A new predicate module, `pathlib.PureWindowsPath`-based logic, or an `os.name` branch | The existing `posixpath.isabs(normalized) or _is_drive_qualified(normalized)` composite already established in `_is_absolute_image_uri()` | Already proven correct across CPython 3.12/3.13's `ntpath.isabs()` divergence (measured in this file's own docstring); a new predicate would need to re-derive the same five-shape truth table |
| Typst string-literal escaping | A second escaper specific to image paths | `escape_typst_string()` (`translator.py:156`), routed via IMG-05 | Already the single source of truth for string-literal safety across the translator; a second escaper risks drifting out of sync with the first |
| Filesystem name-length limit detection | A cross-platform `os.pathconf()`/`os.statvfs()` probe at CI time | The hardcoded `255`-byte constant (IMG-06, owner decision) | `os.pathconf()`/`os.statvfs()` are `Availability: Unix`-only and cannot run on `windows-latest`; 255 matches ext4/APFS and is conservative under NTFS's 255-UTF-16-unit limit |

**Key insight:** every "don't hand-roll" item above is a case of *reuse an already-proven-correct
sibling in this same file*, not an external library recommendation — this phase's whole engineering
discipline is applying an established idiom consistently, not introducing a new one.

## Common Pitfalls

> The CONTEXT.md § Specific Ideas already names five traps (backslash-only fixture insufficiency,
> the 9-byte `{digest}-` prefix, source-file existence for a green compile, `typst-py` presence, and
> quoting Typst's exact refusal text). The four below are NOT in that list.

### Pitfall 1: `pytest.mark.skipif` cannot see `tmp_path` — D-03's filesystem probe must run INSIDE the test body, not as a collection-time decorator

**What goes wrong:** `pytest.mark.skipif(condition)` decorators are evaluated at COLLECTION time,
before any fixture (including `tmp_path`) is instantiated. D-03 requires the skip decision to be an
"attempted `tmp_path` create wrapped in `except OSError`" — that create can only happen once
`tmp_path` exists, i.e. inside the test function body, after the fixture has been injected. A planner
reading "the compile gate skips on a filesystem that cannot hold the name, probed" may reach
instinctively for `@pytest.mark.skipif(...)` and then discover there is no path to probe yet.
**Why it happens:** Every OTHER skip condition in this codebase (`TYPST_AVAILABLE`) is a
module-level, import-time boolean — exactly the shape `skipif` is designed for — so the pattern
generalizes wrong for a fixture-dependent probe.
**How to avoid:** Perform the probe-and-skip as the FIRST lines of the test function itself, using
`pytest.skip(reason=...)` (not the decorator), immediately after `tmp_path` is available:
```python
def test_windows_shaped_uri_compiles(tmp_path):
    probe_path = tmp_path / 'dir\\we"ird.png'
    try:
        probe_path.parent.mkdir(parents=True, exist_ok=True)
        probe_path.write_bytes(b"probe")
    except OSError as e:
        pytest.skip(f"filesystem cannot hold a backslash+quote filename: {e}")
    # ... build the real fixture from here
```
**Warning signs:** A `@pytest.mark.skipif` decorator anywhere near this gate that references
`tmp_path`, `os.getcwd()`, or any other fixture-scoped value — this will raise a `NameError`/fixture
resolution error at collection time, not a graceful skip.
**Phase to address:** IMG-07's compile-gate plan (the wave after the builder/translator fixes).

### Pitfall 2: The relocation key's SHA-1 digest must hash the ORIGINAL, un-normalized `resolved_uri` — normalizing it before hashing silently changes the collision-anchor formula for exactly the shape this phase newly exercises

**What goes wrong:** `builder.py:1761` computes `digest = hashlib.sha1(resolved_uri.encode("utf-8"))
.hexdigest()[:8]` over the RAW parameter. IMG-04 only touches the BASENAME half of the key
(`path.basename(resolved_uri)` → normalize-then-`posixpath.basename`); the digest line is untouched
by the requirement's own text ("`_track_image()`'s escape branch builds its relocation key from a
forward-slash-normalized BASENAME"). It is easy, while touching the surrounding three lines, to
"clean up" by introducing one `normalized = resolved_uri.replace("\\", "/")` at the top of the branch
and reusing it for BOTH the digest input and the basename extraction — which changes the digest's
input bytes for any backslash-bearing `resolved_uri`. No CURRENT test would catch this: every existing
IMG-03 collision test builds its `abs_uri` from `os.sep`/`os.path.join`, which is backslash-free on
the POSIX CI host that runs the suite. The regression is invisible until a Windows-shaped literal (the
exact new fixture this phase introduces) is hashed both ways and compared.
**Why it happens:** The digest and the basename are constructed on adjacent lines from the SAME
parameter name (`resolved_uri`), making "normalize once, use twice" look like the obviously correct
refactor rather than a scope-widening one.
**How to avoid:** Keep `digest = hashlib.sha1(resolved_uri.encode("utf-8")).hexdigest()[:8]` reading
the untouched, raw `resolved_uri`; introduce the normalized variable ONLY for the basename-extraction
half, with a name that makes the asymmetry visible (e.g. `basename_source`, not a reused
`resolved_uri`).
**Warning signs:** A diff where the `digest = hashlib.sha1(...)` line's argument changes at all — that
line should appear in the diff ONLY if IMG-06's truncation wraps around it, never with a different
argument expression.
**Phase to address:** The builder triple-fix plan (PATH-01/IMG-04/IMG-06, ROADMAP constraint 3's
single sequential plan).

### Pitfall 3: A green `copy_image_files()` run is not evidence the key is backslash-free — POSIX filesystems happily create a file whose name literally contains a `\` byte

**What goes wrong:** If IMG-04's normalization is incomplete (e.g. applied to the digest's basename
extraction but a stray unnormalized fragment survives elsewhere in the key), the resulting `key`
string can still contain a literal `\` character. `path.join(self.outdir, imguri)` on a POSIX host
uses `posixpath.join`, which does NOT treat `\` as a separator — it becomes ONE path COMPONENT
containing a literal backslash byte, which ext4 (and most POSIX filesystems) permit in a filename.
`shutil.copy2()` then SUCCEEDS, creates the file, and logs nothing. A plan or executor that treats
"the fixture builds and `copy_image_files()` doesn't warn" as confirmation the key is properly
normalized is measuring the wrong thing — only the DOWNSTREAM Typst compile (which routes the SAME
string into a `"..."` literal, where `\` IS syntactically significant) or a direct string-shape
assertion on the key itself can catch a residual backslash.
**Why it happens:** "The build didn't warn or fail" is an intuitive success signal, and for most OTHER
defects in this codebase it correctly is one — this is the one place where a POSIX host's permissive
filename semantics mask exactly the byte an interpolation-target-platform (Windows, or Typst's own
string-literal grammar) would reject.
**How to avoid:** IMG-06's pure-string unit gate (D-08(a)) must assert directly on the constructed key
string (`"\\" not in key` or equivalent), independent of whether any filesystem operation involving it
succeeds. Do not treat `copy_image_files()`'s silence as IMG-04 evidence.
**Warning signs:** A test that only asserts `img_dest_file.exists()` after a backslash-bearing fixture,
with no assertion on the `key`/`node["uri"]` string's content.
**Phase to address:** The builder triple-fix plan's own gate design (IMG-04's RED-first fixture).

### Pitfall 4: The swallowed `OSError` at `copy_image_files()` is a `logging` call, not a `warnings.warn()` — capture it with `caplog`, not `pytest.warns()`

**What goes wrong:** `builder.py:1988-1992`'s `except Exception as e: logger.warning(f"Failed to copy
image {imguri}: {e}")` uses Python's `logging` module (via `sphinx.util.logging.getLogger`), not the
stdlib `warnings` module. `pytest.warns()` is built for `warnings.warn()`-style warnings and will not
intercept a `logger.warning()` call — a test written with `pytest.warns(UserWarning)` (or any
`Warning` subclass) around a call to `builder.copy_image_files()` will fail with "did not raise" even
when the log message DOES fire, because there is no `warnings`-module event to catch.
**Why it happens:** "Warning" is used ambiguously in both this codebase's own vocabulary (log-level
`WARNING`) and pytest's API surface (`pytest.warns` / the `warnings` module) — the two are unrelated
mechanisms that happen to share the English word.
**How to avoid:** Use `caplog.at_level("WARNING")` around the call, then assert on
`caplog.records`/`caplog.text` — this is the pattern already established at
`tests/test_builder.py:591` (`test_post_process_images_rehome_escape_relocates_with_warning`) and
required by D-08(b)'s "asserting the pre-fix … warning" gate.
**Warning signs:** `import pytest` plus `pytest.warns(...)` anywhere near a `copy_image_files()` test
— this is a strong signal the wrong capture mechanism was reached for.
**Phase to address:** IMG-06(b)'s integration gate (`copy_image_files()` ENAMETOOLONG evidence).

## Code Examples

Every snippet below was executed in this worktree's `.venv` this session (`uv run python3 -c '...'`)
and its printed output is recorded inline — these are not paraphrased from training knowledge.

### PATH-01: `_escapes_outdir()` normalize-then-decide rewrite

```python
# Verified this session: uv run python3 -c '...' — driveless-absolute and unc both
# print True (were False pre-fix, per REQUIREMENTS.md's measured reachability note).
import posixpath

def _is_drive_qualified(stem: str) -> bool:
    # Unchanged — existing sibling, builder.py:86-118.
    return len(stem) >= 2 and stem[0].isalpha() and stem[1] == ":"

def _escapes_outdir(stem: str) -> bool:
    normalized = stem.replace("\\", "/")          # <-- the whole fix: normalize FIRST
    segments = normalized.split("/")
    return (
        ".." in segments
        or posixpath.isabs(normalized)             # <-- decide on the NORMALIZED string
        or _is_drive_qualified(normalized)          # <-- ditto
    )

# Measured output this session:
#   driveless-absolute r'\manuals\guide' -> True
#   unc                r'\\srv\share\g'  -> True
```
Note the pre-fix body (`builder.py:197-238`, read this session) splits on `"/"`/`"\\"` for the `..`
check ALREADY, but calls `posixpath.isabs(stem)` and `_is_drive_qualified(stem)` on the RAW `stem` for
the other two terms — the fix is exactly making those two calls also read the normalized string, per
`_is_absolute_image_uri()`'s already-shipped idiom.

### IMG-04/IMG-06 combined key construction (normalize, then bound)

```python
# Verified this session: 250-char ASCII basename -> 255-byte component (digest-anchored);
# 100-char CJK basename -> 253-byte component, valid UTF-8 round-trip, extension preserved.
import os

def _bound_relocation_component(digest: str, raw_basename: str, limit: int = 255) -> str:
    """IMG-04 (normalize) + IMG-06 (bound), in the order that matters.

    ``raw_basename`` must already be the IMG-04-normalized basename
    (posixpath.basename() of the forward-slash-normalized URI) -- this
    helper does not itself normalize backslashes; it only bounds length.
    """
    prefix = f"{digest}-"
    prefix_bytes = prefix.encode("utf-8")
    budget = limit - len(prefix_bytes)              # D-06: 255 - 9 = 246

    stem, ext = os.path.splitext(raw_basename)
    ext_bytes = ext.encode("utf-8")

    if len(ext_bytes) >= budget:
        # D-07: extension alone would consume the whole remaining budget --
        # truncate it too rather than squeeze the stem to nothing.
        ext_bytes = ext_bytes[: max(budget - 1, 0)]
        while ext_bytes:
            try:
                ext = ext_bytes.decode("utf-8")
                break
            except UnicodeDecodeError:
                ext_bytes = ext_bytes[:-1]           # walk back to a UTF-8 boundary
        stem_budget = budget - len(ext_bytes)
    else:
        stem_budget = budget - len(ext_bytes)

    stem_bytes = stem.encode("utf-8")
    if len(stem_bytes) > stem_budget:
        stem_bytes = stem_bytes[: max(stem_budget, 1)]   # D-07: never empty the stem
        while True:
            try:
                stem = stem_bytes.decode("utf-8")
                break
            except UnicodeDecodeError:
                stem_bytes = stem_bytes[:-1]         # walk back to a UTF-8 boundary

    return f"{prefix}{stem}{ext}"

# Measured this session:
#   digest="a1b2c3d4", basename="x"*250 + ".png"
#     -> component byte length 255, starts with "a1b2c3d4-", tail "...xxxxx.png"
#   digest="deadbeef", basename=("図"*100) + ".png"  (each char 3 UTF-8 bytes)
#     -> component byte length 253, round-trips through .encode/.decode cleanly,
#        ends with ".png"
```
Caller wiring (`_track_image()`'s escape branch, `builder.py:1761-1765`): keep
`digest = hashlib.sha1(resolved_uri.encode("utf-8")).hexdigest()[:8]` reading the RAW `resolved_uri`
(Pitfall 2 above); compute `normalized_basename = posixpath.basename(resolved_uri.replace("\\", "/"))`
separately for IMG-04; pass both into `_bound_relocation_component()` for IMG-06.

### IMG-05: escape-last wiring in `visit_image()`

```python
# translator.py:4742-4749 -- the routing change (D-13), verified against the
# existing escape_typst_string() this session (no-op on paths with neither
# "\" nor '"' nor a control character -- the zero-test-edit guarantee).
adjusted_uri = self._compute_relative_image_path(uri, current_docname)
escaped_uri = escape_typst_string(adjusted_uri)      # <-- the whole fix, computed ONCE

if self.in_figure:
    self.add_text(f'  image("{escaped_uri}"')        # <-- was adjusted_uri
else:
    self.add_text(f'image("{escaped_uri}"')           # <-- was adjusted_uri
```

### D-03 filesystem probe idiom (verified this session, ext4)

```python
# Verified this session: succeeds on this machine's ext4 (both \ and " permitted
# in a POSIX filename) -- confirms D-03's premise that windows-latest cannot
# construct this fixture and the skip must be measured, not os.name-branched.
import tempfile, os

with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, 'dir\\we"ird.png')
    try:
        with open(p, "wb") as f:
            f.write(b"x")
        print("created OK:", p)   # <-- this branch ran on this session's host
        os.remove(p)
    except OSError as e:
        print("OSError:", e)      # <-- the branch that fires on a real Windows filesystem
```

## State of the Art

Not applicable in the usual "library version drift" sense — this phase touches no third-party
version boundary. The one relevant "old vs current" shift is internal to this codebase's own history:

| Old Approach | Current Approach | When Changed | Impact |
|--------------|-------------------|---------------|--------|
| `_track_image()`'s escape-branch key was `{namespace}/{basename}` (basename-only, no digest) | `{namespace}/{digest8}-{basename}` (SHA-1-anchored) | IMG-03, Phase 55 | Restored injectivity for two escaping URIs sharing a basename — this phase's IMG-06 must preserve that anchor under truncation, not merely add a length cap |
| OS-native `path.isabs()` for absolute-URI classification | `posixpath.isabs(normalized) or _is_drive_qualified(normalized)` | BLD-09, Phase 55 | The precedent PATH-01 extends to `_escapes_outdir()`; CPython 3.13 narrowed `ntpath.isabs()`, diverging from 3.12 on the same OS |

**Deprecated/outdated:** None specific to this phase's dependency surface.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|-----------------|
| A1 | The digest-hashing-raw-URI constraint (Pitfall 2) is inferred from reading `builder.py:1761` and the requirement text's literal scope ("builds its relocation key from a forward-slash-normalized BASENAME") — no existing test currently pins the digest's exact hex value for a backslash-bearing input, so this is a reasoned inference about intended scope, not a measured test failure. | Common Pitfalls, Code Examples | Low — if wrong, the worst case is a digest formula change for Windows-shaped URIs only, which is new behavior this phase introduces anyway (no existing green test regresses either way); worth a planner decision, not a blocker |
| A2 | Illustrative test/fixture file names in § Recommended Project Structure (`test_path_shape_predicate_gate.py`, `windows_shaped_image_render_gate/`, etc.) are suggestions, not measured or locked — `59-CONTEXT.md` explicitly delegates naming to the planner | Architecture Patterns § Recommended Project Structure | None — explicitly marked illustrative, discretionary per CONTEXT.md |

**All other claims in this research were verified this session (code read + executed) or copied
verbatim from `59-CONTEXT.md`'s own measured decisions — no other assumption requires confirmation.**

## Open Questions

1. **Should the key-construction logic be extracted into a module-level helper function?**
   - What we know: `59-CONTEXT.md` § Claude's Discretion explicitly leaves this open, noting
     extraction "would make D-08(a)'s pure-string gate a direct call rather than a build."
   - What's unclear: whether the planner should decide this now or leave it to the executor.
   - Recommendation: extract (mirrors this file's existing pattern of standalone, directly-testable
     predicates like `_is_drive_qualified`/`_escapes_outdir`/`_is_absolute_image_uri`) — the pure-string
     unit gate (IMG-06 D-08(a)) is cleaner as a direct call to a named function than as a build
     driving `_track_image()` end-to-end through a hand-built doctree.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|--------------|-----------|---------|-----------|
| `typst` (typst-py) | IMG-07's compile gate; D-01/D-02/D-03's fixture | ✓ (verified this session, `.venv`) | `>=0.15.0,<0.16` [VERIFIED: pyproject.toml:30] | `TYPST_AVAILABLE` import-guard skip (existing pattern, `tests/test_absolute_image_render_gate.py`) |
| `uv` | All test/lint/type commands, per-worktree provisioning | ✓ (this session used `uv run` throughout) | — | None needed — CLAUDE.md's per-worktree `uv sync` is mandatory, not optional |
| A filesystem permitting `\`+`"` in a filename | D-01/D-02's fixture creation | ✓ on this session's ext4; ✗ on NTFS/`windows-latest` (measured, D-03) | — | D-03's runtime probe + `pytest.skip()` (see Common Pitfalls #1) — this IS the designed fallback, not a gap |
| `mypy`, `black`, `ruff` | CI lint/type gate | Present in `dev` extra; `ruff` locally unrunnable on this NixOS dev machine per project memory (`ruff は未解消... lint 権威は CI`) | — | CI is the sole lint authority for this phase; do not gate local commits on a worktree `ruff` run |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** the backslash+quote-permissive filesystem for D-01/D-02's
fixture (fallback is the probe-and-skip mechanism itself, per D-03 — this is by design, not a gap to
close).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (`pyproject.toml:35` pins `>=8.4,<10`) [VERIFIED: pyproject.toml:35] |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`pyproject.toml:79-99`) — `testpaths = ["tests"]`, `addopts = "-v --strict-markers"`, `filterwarnings` escalates `DeprecationWarning`/`PendingDeprecationWarning` to `error` [VERIFIED: pyproject.toml:79-99] |
| Quick run command | `uv run pytest tests/test_path_shape_predicate_gate.py tests/test_track_image_key_construction.py -q` (planner-named files; substitute actual names once chosen) |
| Full suite command | `uv run pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|--------------|
| PATH-01 | `_escapes_outdir()` called DIRECTLY returns `True` for driveless-absolute (`\manuals\guide`) and UNC (`\\srv\share\g`), recorded `False` pre-fix (RED-first, D-09) | unit | `uv run pytest tests/test_path_shape_predicate_gate.py -k escapes_outdir_direct -x` | ❌ Wave 0 — new file |
| PATH-01 | Both production call sites (`_resolve_target_stem()` `builder.py:608`, `_track_image()` `builder.py:1637`) classify every tested shape byte-identically before and after (characterization pin, D-10) | unit (parametrized, through call sites) | `uv run pytest tests/test_path_shape_predicate_gate.py -k characterization -x` | ❌ Wave 0 — new file |
| IMG-04 | `_track_image()`'s escape-branch key contains no raw `\` for a Windows-shaped `resolved_uri` (RED-first against the unfixed `path.basename()` call) | unit | `uv run pytest tests/test_track_image_key_construction.py -k no_backslash -x` | ❌ Wave 0 — new file |
| IMG-05 | `visit_image()`'s emitted `image("...")` literal has no raw backslash and a `"` appears escaped, for a Windows-shaped absolute URI, via a `-b typst` build (D-04's all-lane sibling) | integration (subprocess `sphinx-build -b typst`) | `uv run pytest tests/test_windows_image_uri_render_gate.py -k string_shape -x` | ❌ Wave 0 — new file |
| IMG-06 | Relocation-key final component `<= 255` UTF-8 bytes, digest intact, extension preserved, boundary-safe, collision preserved for two long URIs sharing a basename (D-08(a), pure-string, all lanes) | unit | `uv run pytest tests/test_track_image_key_construction.py -k length_bound -x` | ❌ Wave 0 — new file |
| IMG-06 | `copy_image_files()`'s pre-fix `Failed to copy image …: [Errno 36] File name too long` warning (`caplog`, not `pytest.warns` — Pitfall 4) and absent destination file, both gone post-fix (D-08(b), integration) | integration | `uv run pytest tests/test_copy_image_files_name_too_long.py -x` | ❌ Wave 0 — new file |
| IMG-07 | A real `typst.compile()` succeeds for D-01's four-combination fixture, RED pre-fix with `path must not contain a backslash` quoted verbatim, GREEN post-fix; skips via D-03's runtime probe, never `os.name` | integration (subprocess `sphinx-build -b typstpdf`, `TYPST_AVAILABLE`-guarded) | `uv run pytest tests/test_windows_image_uri_render_gate.py -k compile -x` | ❌ Wave 0 — new file |

### Sampling Rate

- **Per task commit:** the specific requirement's quick command above, scoped to the file(s) that
  task touched.
- **Per wave merge:** `uv run pytest` (full suite) — this phase edits `builder.py` and `translator.py`
  in the SAME milestone, and ROADMAP constraint 4 forbids a plan changing an emitted string sharing a
  wave with a plan asserting on it; a full-suite run at each merge boundary is the cheapest way to
  confirm no cross-wave collision (§ same-wave-evidence-dependency-blind-spot, project memory).
- **Phase gate:** full suite green, `black --check .` clean, `mypy typsphinx/` clean (both apply to
  the two touched product files), `ruff check .` deferred to CI per project memory (locally unrunnable
  on this NixOS dev machine), before `/gsd-verify-work`. Local RED→green confirmed BEFORE the first
  `windows-latest` CI dispatch (binding constraint 10 / Pitfall 6 in PITFALLS.md — CI is final
  confirmation, never first discovery).

### Wave 0 Gaps

- [ ] `tests/test_path_shape_predicate_gate.py` — PATH-01's direct-call RED gate + characterization
  pin (D-09/D-10)
- [ ] `tests/test_track_image_key_construction.py` — IMG-04's no-backslash gate + IMG-06(a)'s
  pure-string length-bound gate (both new; no filesystem needed for either)
- [ ] `tests/test_windows_image_uri_render_gate.py` — IMG-05/D-04's POSIX string-shape sibling +
  IMG-07/D-01..D-03's real-compile gate + its own new fixture project (name discretionary)
- [ ] `tests/test_copy_image_files_name_too_long.py` — IMG-06(b)'s integration gate for the swallowed
  `OSError`
- [ ] `59-WINDOWS-URI-EVIDENCE.md` — the recorded two-tree PATH-01 measurement (D-09's "before and
  after" half) and IMG-07's verbatim `TypstError` RED quote (D-11 names the file, not its contents)
- [ ] No framework install needed — `pytest`, `hashlib`, `posixpath`, `os` all already present;
  `typst`/`typst-py` already pinned and confirmed importable this session.

## Security Domain

`security_enforcement` is `true` in `.planning/config.json` (`security_asvs_level: 1`,
`security_block_on: "high"`) [VERIFIED: .planning/config.json], so this section is required.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|----------------|---------|---------------------|
| V2 Authentication | no | N/A — no auth surface; this is a local build-tool path-handling fix |
| V3 Session Management | no | N/A |
| V4 Access Control | no | N/A |
| V5 Input Validation | yes | `_escapes_outdir()` and `_is_absolute_image_uri()` are exactly this — pure-string validation of a path SHAPE before it is used to construct a filesystem destination (`copy_image_files()`'s `dest = path.join(self.outdir, imguri)`). No new validation surface is added by this phase; PATH-01 hardens an EXISTING validator's own contract. |
| V6 Cryptography | no | The SHA-1 digest is an explicitly-documented (`builder.py`, inline comment above `digest = hashlib.sha1(...)`) non-cryptographic collision-avoidance key over a build-local path string, not a security boundary — this project's ruff selection does not include the security rule set (per PITFALLS.md "Security Mistakes" table, already measured). This phase does not change the digest's algorithm or add a new cryptographic use. |
| V12 File and Resources | yes | `_escapes_outdir()` is this codebase's directory-traversal / outdir-containment guard (`OUT-02`) — the `".."`-segment check plus the absolute/drive-qualified checks PATH-01 hardens. `copy_image_files()`'s `dest = path.join(self.outdir, imguri)` is the write sink this guard protects. This phase does not weaken the guard's existing `".."` term; it only widens the absolute/drive-qualified terms to also fire on a backslash-normalized shape — strictly more restrictive, never less. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----------------------|
| Path-shape classification gap allowing an absolute or traversal-shaped image/target path to escape the intended output directory (`_escapes_outdir()`'s own reason to exist, OUT-02) | Tampering (of the build's own output tree, not an external actor — this is a single-user local build tool, not a network service) | `posixpath.isabs(normalized) or _is_drive_qualified(normalized)` composite, applied to a backslash-normalized string — PATH-01 is a strictly-more-restrictive widening of this exact mitigation, never a relaxation |
| Filename-length overflow at a filesystem write boundary (`copy_image_files()`'s swallowed `ENAMETOOLONG`) | Denial of Service (a build silently drops an image rather than crashing loudly — the CURRENT, pre-fix behavior is itself the more dangerous shape: a swallowed exception plus a missing file, discovered only much later at Typst-compile time or not at all if the image was optional) | IMG-06's 255-byte bound proactively prevents the write from ever exceeding the limit, rather than relying on the `except Exception` catch-and-log to mask it after the fact |
| Un-escaped filesystem-derived text reaching a Typst string literal (`visit_image()`'s current unescaped `image("{adjusted_uri}")`) | Tampering (a filename containing `"` could, in principle, break out of the intended string-literal boundary in the emitted `.typ` — though Typst's own parser refuses the malformed literal rather than executing anything, so the practical impact here is a compile fatal, not code execution; `.typ` is not an executable/scripting boundary in the security sense) | `escape_typst_string()`, IMG-05's routing target — already this codebase's single source of truth for the mitigation, being extended to a site that currently lacks it |

No injection, auth, session, or crypto surface is introduced or modified by this phase. The security
posture here is entirely about this project's own OUTPUT containment (never writing outside `outdir`)
and SYNTAX validity (never emitting a `.typ` literal Typst's own parser would refuse or misinterpret)
— not about defending against an adversarial external actor, since `typsphinx` is a local
Sphinx-extension build tool with no network-facing input surface.

## Sources

### Primary (HIGH confidence)

- `typsphinx/builder.py` (this repository, HEAD `7d809b83`+, read live this session): lines 86-118
  (`_is_drive_qualified`), 121-194 (`_is_absolute_image_uri`, including its five-shape measured
  docstring table), 197-238 (`_escapes_outdir`), 608-700 (`_resolve_target_stem`, the
  `stem.replace("\\", "/")` normalization at line 662), 1637-1792 (`_track_image`, including exact
  line numbers 1761-1769 for the digest/key/warning construction — verified byte-identical to
  `59-CONTEXT.md`'s citations), 1957-1992 (`copy_image_files`, including the `except Exception`
  swallow at 1988-1992).
- `typsphinx/translator.py` (this repository, HEAD, read live this session): lines 156-183
  (`escape_typst_string`), 4718-4766 (`visit_image`, confirming `add_text` sites at exact lines
  4746/4749), 5047-5070 (`_compute_relative_image_path`).
- `pyproject.toml` (this repository, HEAD, read live this session): lines 5-11 (`requires-python
  ">=3.12"`), 30 (`typst>=0.15.0,<0.16`), 35 (`pytest>=8.4,<10`), 79-99
  (`[tool.pytest.ini_options]`), 136-149 (`[tool.mypy]`, confirming lenient `typsphinx.*` overrides).
- `.planning/config.json` (this repository, read live this session): `workflow.security_enforcement:
  true`, `security_asvs_level: 1`, `security_block_on: "high"`, `workflow.nyquist_validation: true`.
- `.github/workflows/ci.yml` (this repository, read live this session): lines 12-17, confirming the
  3-OS matrix (`ubuntu-latest`, `windows-latest`, `macos-latest`).
- `tests/test_absolute_image_render_gate.py` + its fixture directory (this repository, read live
  this session) — the structural template for D-01/D-02's compile gate, including the
  `TYPST_AVAILABLE` import-guard idiom and the `sys.executable -m sphinx` subprocess invocation
  pattern.
- `tests/test_templates_path_collision_gate.py:411-470` (this repository, read live this session) —
  `TestWindowsPathEscapingRegressionGuard`, D-04's proven all-lane pattern.
- `tests/test_builder.py:512-598,680-746` (this repository, read live this session) — existing
  `_track_image()`/`post_process_images()` regression tests, confirming the digest-computation
  pattern (`hashlib.sha1(abs_uri.encode("utf-8"))` over the RAW test-constructed URI) and the
  `caplog.at_level("WARNING")` capture idiom (Pitfall 4's recommended pattern).
- Live execution this session, `uv run python3 -c '...'` (this worktree's `.venv`, Python 3.13.13,
  `typst` module confirmed importable): the `_escapes_outdir` normalize-then-decide rewrite (both
  measured shapes correctly flip `False → True`), the D-03 filesystem probe (backslash+quote filename
  creatable on this ext4 host), and the 255-byte boundary-safe truncation prototype (three cases:
  250-byte ASCII stem → 255-byte component; 100-char CJK stem → 253-byte component, valid UTF-8
  round-trip; both preserve the digest prefix and the extension).

### Secondary (MEDIUM confidence)

- `.planning/phases/59-path-shape-predicate-and-image-uri-correctness/59-CONTEXT.md` — all D-01
  through D-13, treated as given per this phase's explicit instruction not to re-derive or
  re-litigate; copied/summarized, not independently re-measured in this session (the CONTEXT.md's own
  measurements were taken 2026-08-28 in the same worktree state).
- `.planning/research/SUMMARY.md`, `.planning/research/PITFALLS.md` — synthesized 2026-08-27,
  cross-referenced against this session's live code reads and found consistent (line numbers,
  function names, and the six named pitfalls all confirmed against HEAD).
- `.planning/phases/58-repr-format-decoupling-test-side-only/58-RESEARCH.md` § Validation Architecture
  / § Security Domain — used as the shape reference for this document's corresponding sections, per
  this task's explicit instruction.

### Tertiary (LOW confidence)

None — every claim in this document is either read/executed live this session or copied verbatim
from an already-measured upstream artifact (CONTEXT.md, PITFALLS.md, SUMMARY.md).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dependencies, existing pin verified live (`pyproject.toml:30`,
  `import typst` succeeded this session).
- Architecture: HIGH — every line number and function name cross-checked against a live read of
  `builder.py`/`translator.py` at HEAD this session; matches `59-CONTEXT.md`'s citations exactly.
- Pitfalls: HIGH — all four new pitfalls are grounded in a specific line number or a specific,
  demonstrated Python/pytest mechanic (the `skipif`-vs-fixture-timing behavior and the
  `logging`-vs-`warnings` distinction are both standard library/pytest documented behavior, not
  speculation).
- Code Examples: HIGH — every snippet executed this session with recorded output; none are
  paraphrased from training data.

**Research date:** 2026-08-28
**Valid until:** Stable — this is a bug-fix phase against a fixed, already-measured code region with
no external version dependency; treat as valid for the life of this milestone (through Phase 61's
release), not on the usual 30-day drift clock.
