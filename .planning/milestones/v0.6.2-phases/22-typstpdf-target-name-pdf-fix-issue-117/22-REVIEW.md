---
phase: 22-typstpdf-target-name-pdf-fix-issue-117
reviewed: 2026-07-21T00:00:00Z
depth: deep
files_reviewed: 11
files_reviewed_list:
  - typsphinx/builder.py
  - tests/test_builder_output_stem.py
  - tests/test_target_name_render_gate.py
  - tests/test_corpus_gate.py
  - tests/test_cross_doc_label_namespace_render_gate.py
  - tests/test_examples_basic.py
  - tests/fixtures/cross_doc_label_namespace_render_gate/conf.py
  - docs/source/user_guide/builders.rst
  - docs/source/user_guide/configuration.rst
  - examples/advanced/README.md
  - examples/charged-ieee/README.md
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 22: Code Review Report

**Reviewed:** 2026-07-21
**Depth:** deep
**Files Reviewed:** 11
**Status:** issues_found

## Summary

Reviewed `typsphinx/builder.py`'s new `_resolve_output_stem` / `_directory_preserving_relpath`
helpers and the three rewired write/read sites (`TypstBuilder.write_doc`,
`TypstPDFBuilder.write_doc`, `TypstPDFBuilder.finish`), plus the consumer-side test/doc/example
updates. This review went beyond reading: I empirically exercised the helpers with a stub builder
object (no Sphinx app required — both methods only touch `self.config.typst_documents`) to probe
degenerate/adversarial inputs (empty tuples, trailing slashes, `..` traversal, absolute paths,
drive-qualified targets, nested docnames combined with traversal), and I checked out the pre-fix
commit (`e5032a4`) into a scratch worktree to confirm the new GATE-01 render-gate test
(`tests/test_target_name_render_gate.py`) genuinely fails against the pre-fix builder (it does —
pre-fix output is `index.typ`/`index.pdf`, the assertion on `output.typ` fails cleanly).

**Core correctness claims verified true, with evidence:**
- D-03/D-04 (literal-suffix-only stripping, no `splitext`, period-bearing stems preserved) — confirmed
  by code reading and the `v1.2-manual[.typ]` unit tests; `os.path.splitext` is not used anywhere in
  the new code.
- D-06/D-07 (path/traversal/absolute/drive-qualified guard, portable separator detection) — confirmed
  correct, including for combinations not exercised by any shipped test: nested docname
  (`sub/index`) + traversal target (`../evil.typ`) resolves to `outdir/sub/evil.typ` — no escape
  outside the docname's own directory, let alone outside `outdir`. Absolute (`/etc/passwd.typ`) and
  drive-qualified (`C:manual.typ`) targets both reduce safely to their basename in every case I tried,
  nested or not.
- D-05 (directory-preserving rename) — confirmed correct for the documented example
  (`('sub/index', 'manual.typ', ...)` → `outdir/sub/manual.typ`) and for the identity-mapping
  non-regression case for nested docnames (byte-identical to pre-fix output).
- The three write/read sites agree — all three call the identical `_resolve_output_stem` +
  `_directory_preserving_relpath` pair; `finish()` resolves the stem once per `doc_tuple` and reuses
  it for both the `.typ` read-back and the `.pdf` write, so they cannot drift.
- `get_target_uri` — diff is docstring-only; the method body (`return docname + self.out_suffix`) is
  byte-identical to pre-fix.
- Project conventions — `black --check`, `mypy`, and `ruff check` all pass clean on every changed
  file; `sphinx.util.logging` (not stdlib `logging`) is used for the new warnings; no
  `@pytest.mark.parametrize` was introduced; no `Dict`/`List` typing modernization occurred.
- Test quality — `tests/test_target_name_render_gate.py` correctly asserts both halves (target-named
  artifacts present AND docname-named artifacts absent); verified this bidirectional assertion is
  load-bearing by running it against the pre-fix builder, where it fails exactly as expected.

No BLOCKER-level defects were found: I could not construct an input that escapes `outdir`, crashes
the write path, or silently produces a compatibility-shim (dual) output. The findings below are
robustness/coverage gaps, not incorrect behavior in the paths the phase's own D-01..D-12 contract
covers.

## Warnings

### WR-01: `TypstPDFBuilder.finish()`'s per-entry loop can raise an uncaught `IndexError` before `_resolve_output_stem`'s own defenses ever run

**File:** `typsphinx/builder.py:857` (inside `finish()`, unchanged by this diff except for a comment)
**Issue:** `_resolve_output_stem` explicitly guards against a `typst_documents` entry shorter than 2
elements (`if entry and len(entry) >= 2 and entry[0] == docname`), and this is unit-tested
(`test_resolve_output_stem_falls_back_on_short_tuple`). However, that guard only protects entries
being *scanned inside the helper*. The caller in `finish()` still does:
```python
for doc_tuple in typst_documents:
    docname = doc_tuple[0]          # <-- unconditional, no length check
    stem = self._resolve_output_stem(docname)
    ...
```
If a `typst_documents` entry is itself an empty tuple/list (`typst_documents = [()]`), line 857
raises `IndexError: tuple index out of range` *before* `_resolve_output_stem` is ever called, and
this is outside the `try/except` block (which starts at line 866, only around the compile-and-write
section). The whole `finish()` call — and therefore the entire `-b typstpdf` build — crashes
uncaught. This is pre-existing behavior (the line is unchanged by this phase's diff other than a
comment), but this phase's own stated goal for this exact loop was to make the read-back/write pair
"never drift" and resolve the stem "safely" — the adjacent, easily-reachable crash on a malformed
entry was not addressed even though the analogous defense was added one call away, in
`_resolve_output_stem`.
**Fix:** Mirror `_resolve_output_stem`'s length guard in the `finish()` loop, e.g.:
```python
for doc_tuple in typst_documents:
    if not doc_tuple or len(doc_tuple) < 1:
        logger.warning(f"Skipping malformed typst_documents entry: {doc_tuple!r}")
        continue
    docname = doc_tuple[0]
    ...
```

### WR-02: D-05's directory-preserving behavior (`_directory_preserving_relpath`) has zero test coverage for its core case — a nested docname combined with a non-identity target

**File:** `tests/test_builder_output_stem.py` (whole file), `tests/test_target_name_render_gate.py`,
`tests/fixtures/cross_doc_label_namespace_render_gate/conf.py`
**Issue:** `_directory_preserving_relpath` is the function that specifically satisfies D-05 ("rename
the basename in place... `outdir/sub/manual.typ`, NOT `outdir/manual.typ`") and was called out in
the review focus as a path-injection-relevant surface (threat T-22-01..03, "block on high"). Yet no
shipped test — unit or render-gate — exercises it: `tests/test_builder_output_stem.py` only tests
`_resolve_output_stem` in isolation, always against a root-level docname `"index"` (never
`"sub/index"`); `test_resolve_output_stem_falls_back_to_docname_when_unlisted` uses
`"chapter1/section"` but that hits the D-02 "no entry matched" early return, never reaching
`_directory_preserving_relpath`'s directory-prefixing branch at all. Every render-gate fixture with a
`target != docname` entry (`test-basic`, `cross_doc_label_namespace_render_gate`, `examples/basic`,
the corpus gate's injected entry) uses a root-level master docname (`index`). I confirmed by direct
invocation that `_directory_preserving_relpath` behaves correctly for the nested case (see Summary),
but this is unverified by the test suite that ships with this phase — a future refactor of this
function (or of the call sites) could silently break directory preservation for nested masters with
no test catching the regression.
**Fix:** Add either (a) a unit test directly calling `_directory_preserving_relpath("sub/index",
"manual")` and asserting `"sub/manual"`, or (b) extend one existing multi-doc fixture (e.g. add a
`typst_documents` entry whose docname lives in a subdirectory) so a render gate exercises this
end-to-end, matching the "reuse an existing fixture over building a new one" pattern already used
elsewhere in this phase's plans.

### WR-03: Degenerate path-bearing targets that reduce to an empty basename produce two confusing, back-to-back warnings instead of one

**File:** `typsphinx/builder.py:196-221` (the path-guard block followed by the empty-stem check)
**Issue:** When a path-bearing target's basename itself is empty — e.g. a trailing separator
(`"sub/manual.typ/"`), a bare root (`"/"`), or a 2-character drive prefix with nothing after it
(`"C:"`) — the path guard fires first (`"a path is not supported ... using '' instead"`), setting
`stem = ""`, and then the subsequent empty-stem check fires a *second* warning
(`"empty typst_documents target name ... falling back to <docname>"`). Verified by direct
invocation:
```
a path is not supported in a typst_documents target name: 'sub/manual.typ/' -- using '' instead
empty typst_documents target name for docname 'index' -- falling back to 'index'
```
Both fallbacks are safe (final result is the docname, as intended), but a user debugging their
`typst_documents` config sees two warnings that don't obviously connect ("using '' instead" reads
like a *successful* resolution to an empty string, not a re-triggered failure).
**Fix:** After the path-guard branch computes `fallback`, check `if not fallback.strip()` immediately
and route directly to the single "empty target" warning/return instead of falling through to a
second warning:
```python
if is_guarded:
    fallback_source = stem[2:] if is_drive_qualified else stem
    fallback = path.basename(fallback_source.replace("\\", "/"))
    if not fallback.strip():
        logger.warning(
            "empty typst_documents target name for docname "
            f"{docname!r} after removing an unsupported path -- falling back to {docname!r}"
        )
        return docname
    logger.warning(...)
    stem = fallback
```

## Info

### IN-01: A target value of exactly `"..typ"` strips to a bare `"."` stem, producing unwarned artifacts literally named `..typ` / `..pdf`

**File:** `typsphinx/builder.py:180-221`
**Issue:** `"..typ".endswith(".typ")` is `True`, so `_resolve_output_stem` strips it to `stem = "."`.
The traversal guard checks for the *exact segment* `".."` (correctly avoiding false positives on
names like `"..manual"`), so a lone `"."` segment is not flagged; the empty-stem check also passes
since `".".strip()` is truthy. The result: a document configured with this target silently produces
`outdir/..typ` and `outdir/..pdf` (unusual but not `..`-equal, so not a directory-traversal escape —
verified no escape occurs). This is an extremely unlikely real-world input (no corpus entry is close
to it) and is arguably consistent with the letter of D-03/D-04 ("strip only a literal trailing
`.typ`, nothing else"), so this is flagged for awareness rather than as an actionable defect.
**Fix:** Optional — if desired, treat an all-`.`/whitespace stem the same as the existing
empty-stem guard (`if not stem.strip("."):` in addition to `not stem.strip()`).

### IN-02: The drive-letter guard also fires on legitimate POSIX filenames that happen to start with `"<letter>:"`

**File:** `typsphinx/builder.py:191` (`is_drive_qualified = len(stem) >= 2 and stem[0].isalpha() and stem[1] == ":"`)
**Issue:** Colons are valid in POSIX filenames. A deliberately chosen stem like `"v2:draft"` (no
directory intent at all) is detected as `is_drive_qualified` and silently reduced to `"draft"` with a
warning, even when running on Linux/macOS, where `v2:draft.typ` would be a perfectly legal filename.
This is a direct, and likely intentional, consequence of D-07's mandate ("drive-qualified targets ...
detected on POSIX too" — confirmed by
`test_resolve_output_stem_guards_drive_qualified_target`), so this is not a bug against the locked
decision, just a documented trade-off worth surfacing: portability safety here costs a small amount
of expressiveness for legitimate colon-bearing stems on non-Windows platforms.
**Fix:** None required; flagging for awareness only, since D-07 explicitly locks in this behavior.

---

_Reviewed: 2026-07-21_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: deep_
