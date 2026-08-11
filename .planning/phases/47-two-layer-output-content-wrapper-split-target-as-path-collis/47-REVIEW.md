---
phase: 47-two-layer-output-content-wrapper-split-target-as-path-collis
reviewed: 2026-08-11T00:00:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - typsphinx/builder.py
  - typsphinx/writer.py
  - tests/test_collision_validator_gate.py
  - tests/test_two_layer_output_gate.py
  - tests/test_out02_escape_target_gate.py
  - tests/test_builder_output_stem.py
  - tests/test_typst_documents_collision_gate.py
findings:
  critical: 2
  warning: 1
  info: 0
  total: 3
status: issues_found
---

# Phase 47: Code Review Report

**Reviewed:** 2026-08-11
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the two-layer content/wrapper split (`builder.py`/`writer.py`) and
the five gate test modules that encode its contracts. The OUT-02 escape
guard (`_escapes_outdir`/`_is_drive_qualified`) is sound and its
platform-independence fix is genuinely proven by a direct, non-gated unit
test (`test_resolve_output_stem_guards_absolute_target`, which exercises
the POSIX-absolute shape unconditionally, not just under an `os.name`
branch) as well as the subprocess containment-proof gate. The five gate
modules are non-vacuous: they run real `sphinx-build` subprocesses, assert
non-zero exit + `ExtensionError` + zero written `.typ` files on the
must-fail side, and a genuine `Path.resolve().is_relative_to()`
containment check on the escape-guard side.

However, the central object of scrutiny — `_validate_output_path_collisions()`
— does **not** provide the "no output file is written when any collision is
found" guarantee its own docstring claims. Two independent, reproduced gaps
let a real filename collision through the validator and reach `write()`
undetected, in direct contradiction of this phase's whole purpose (replacing
the old warn-and-fall-back CR-01 behavior with a hard, structural guarantee).
Both were confirmed by running real `sphinx-build` invocations against this
checkout, not just read through the source.

## Critical Issues

### CR-01: Malformed 1-element `typst_documents` entry silently overwrites its own docname's content file (validator false negative)

**File:** `typsphinx/builder.py:521` (validator's malformed-entry skip) vs. `typsphinx/builder.py:896-910` (`_write_typst_files`'s wrapper loop, no equivalent skip)

**Issue:**
`_validate_output_path_collisions()` treats any entry with `len(entry) < 2`
as "malformed" and silently skips it without registering a claim (by
design — "reporting a malformed entry stays `TypstPDFBuilder.finish()`'s
job alone"):

```python
for index, entry in enumerate(typst_documents):
    if not entry or len(entry) < 2 or not isinstance(entry[0], str):
        continue          # <-- 1-element entry never reaches the claims map
```

But `_write_typst_files()` — the method that actually writes wrapper
files, called from `write_doc()` for every docname, well before
`TypstPDFBuilder.finish()` ever runs — has **no equivalent length guard**:

```python
for entry in typst_documents:
    if not entry or entry[0] != docname:
        continue
    wrapper_relpath = self._wrapper_output_relpath(entry)
    ...
```

`_wrapper_output_relpath()` tolerates the missing target element by
treating it as `None` and falling back to the bare docname
(`_resolve_target_stem` → "empty target" branch → `return docname`). For a
1-element entry `("index",)`, this makes `wrapper_relpath == "index"` —
**identical** to the unconditional content file's own path (`"index.typ"`),
which was already written moments earlier in the same call.

Confirmed by running an actual `-b typst` build via
`sphinx.testing.util.SphinxTestApp` with
`typst_documents = [("index",)]` and one `index.rst`: the build exits
successfully (no error at all) and `index.typ` on disk ends up containing
the **wrapper** (template + `#include("index.typ")` — a self-referential
include) instead of the docname's own translated content, which is
silently discarded:

```
#import "_template.typ": project
#show: project.with(
  title: "Test Project", ...
)
#include("index.typ")
```

With `-b typstpdf`, the corruption is the same at write time, but is later
surfaced (only for the PDF builder) as `TypstError: cyclic import` when
`finish()` tries to compile the now-self-referential `index.typ` — i.e.
the plain `typst` builder (no PDF step) reports **success** while silently
producing a corrupted, empty-of-real-content, self-including `.typ` file
that will hard-fail if the user ever compiles it by hand.

This is a pre-existing malformed-entry shape that a prior code review
finding (CR-01, referenced in
`tests/fixtures/missing_and_malformed_master_gate/conf.py`) already
addressed for the **0-element** `()` entry — that fixture explicitly
documents guarding the empty-tuple case reaching this same scan — but the
**1-element** entry (`(docname,)`, no target) was not covered by that fix
or by any test in the reviewed suite.

**Fix:** Give `_write_typst_files()`'s wrapper-matching loop the same
malformed-entry tolerance the validator applies, so a docname that the
validator silently skipped is *also* skipped at write time (never treated
as a real wrapper-producing entry):

```python
for entry in typst_documents:
    if (
        not entry
        or len(entry) < 2
        or not isinstance(entry[0], str)
        or entry[0] != docname
    ):
        continue
```

Better still, extract one shared `_is_usable_typst_documents_entry(entry)`
helper that both `_validate_output_path_collisions()` and
`_write_typst_files()` (and `TypstPDFBuilder.finish()`) call, so this
"malformed = skip" tolerance can never drift apart between the validator
and the write path again — which is exactly how this gap was introduced
(the validator and the write path independently decided what counts as
malformed).

---

### CR-02: `_collision_key()` does not path-normalize before comparing, so equivalent-but-differently-spelled targets defeat collision detection

**File:** `typsphinx/builder.py:403-441` (`_collision_key`), `typsphinx/builder.py:528` (unnormalized relpath fed into the claim)

**Issue:**
`_collision_key()`'s docstring promises it is "the ONLY place this
normalization happens" and that "a bare `==` on two raw path strings can
never creep back in and silently miss a ... collision". In practice it
only folds `\` to `/` and applies `casefold()` — it never calls
`posixpath.normpath()`:

```python
@staticmethod
def _collision_key(relative_path: str) -> str:
    return relative_path.replace("\\", "/").casefold()
```

`_resolve_target_stem()` deliberately returns a path-bearing target
"AS-IS" (OUT-01) with no normalization beyond suffix-stripping and
backslash folding — it does *not* collapse a redundant `./` prefix, a
double `//` separator, or an embedded `/./` segment (only a literal `..`
segment is special-cased, via `_escapes_outdir`). This means two
`typst_documents` entries whose targets are textually different but
resolve to the *same physical file* once written
(`path.normpath(path.join(outdir, ...))` **does** collapse these) produce
two *different* collision keys, so the validator never claims a collision
— yet the actual on-disk write silently clobbers one with the other.

Confirmed by running a real `-b typst` build with:

```python
typst_documents = [
    ("index", "./manual.typ", "T1", "A1"),
    ("other", "manual.typ", "T2", "A2"),
]
```

The build succeeds with **no** `ExtensionError`, and only one
`build/manual.typ` exists on disk — containing entry `"other"`'s wrapper
(`#include("other.typ")`, title `"T2"`), while entry `"index"`'s wrapper
was silently overwritten and never survives the build at all. This is
precisely the CR-01-era "warn (or not even that) and silently overwrite"
failure mode the whole content/wrapper split + validator was built to
eliminate (per D-01/D-02's stated intent), reproduced through a shape
(`./`) the validator's own unit tests (`TestCollisionKeyUnit` in
`tests/test_collision_validator_gate.py`) never exercise — that class only
pins case-folding and the deliberate NFC/NFD non-normalization, not
path-shape normalization.

The same gap also lets a `./`-prefixed (or `//`-doubled, or
`/./`-embedded) target silently clobber the reserved `_template.typ`
infrastructure file without the validator ever naming it (e.g. a target
resolving to `"./_template"`), and affects `TypstPDFBuilder.finish()`
identically, since it resolves the same unnormalized `wrapper_relpath`.

**Fix:** Normalize the path shape (not the case) before hashing/comparing,
keeping the normalization strictly comparison-only (never touching what
gets literally written to disk, consistent with the function's existing
"Folding is COMPARISON-ONLY" contract):

```python
@staticmethod
def _collision_key(relative_path: str) -> str:
    normalized = posixpath.normpath(relative_path.replace("\\", "/"))
    return normalized.casefold()
```

(`posixpath.normpath` is already imported and used elsewhere in this
module for exactly this kind of platform-independent path reasoning, e.g.
`_escapes_outdir`.) Add a `TestCollisionKeyUnit` case pinning
`_collision_key("./manual.typ") == _collision_key("manual.typ")` and
`_collision_key("a//b.typ") == _collision_key("a/b.typ")` so this class of
gap cannot silently regress again, plus a subprocess must-fail gate
mirroring `test_bld02_duplicate_target_rejected_typst` but with a
`./`-prefixed target on one of the two colliding entries.

## Warnings

### WR-01: `_resolve_entry_element()` is dead production code, tested but never called

**File:** `typsphinx/writer.py:104-156`

**Issue:** `_resolve_entry_element()` is fully implemented, extensively
documented, and directly unit-tested (`tests/test_entry_metadata_precedence.py`
imports and calls it ~15 times), but nothing in `typsphinx/` actually calls
it — `render_wrapper()` uses `_entry_element_value()` (the positional,
per-entry sibling) exclusively for title/author resolution (D-08). A
repository-wide grep confirms zero production call sites:

```
$ grep -rn "_resolve_entry_element(" typsphinx/*.py
typsphinx/writer.py:104:def _resolve_entry_element(
```

The function's own docstring even documents that its docname first-match
semantics are "deliberately NOT used for a wrapper's own title/author
(D-08)" — i.e. the code acknowledges its own replacement but the
superseded implementation was never removed. This is easy to miss because
its test suite still passes (it tests the dead function directly, not
through any real code path), giving false confidence that this logic is
exercised in the actual build.

**Fix:** Either delete `_resolve_entry_element()` and retarget
`tests/test_entry_metadata_precedence.py`'s direct-call assertions onto
`_entry_element_value()` (if the semantics genuinely still need coverage),
or, if it is being deliberately retained as a historical/reference
implementation, say so explicitly in its docstring and exclude it from
coverage expectations — leaving it as ordinary, uncommented dead code
invites a future maintainer to assume it is load-bearing.

---

_Reviewed: 2026-08-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
