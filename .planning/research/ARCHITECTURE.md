# Architecture Research

**Domain:** Bug-fix integration for a mature Sphinx→Typst extension (v0.9.1 "Windows path correctness")
**Researched:** 2026-08-27
**Confidence:** HIGH (every claim below is read directly from `typsphinx/*.py` at HEAD or verified by executing the actual predicate logic in Python; the one place confidence drops to MEDIUM is called out inline)

This is not greenfield research — it answers the four integration questions in the task prompt against the existing 5-module pipeline (`builder.py` / `writer.py` / `translator.py` / `template_registry.py` / `template_engine.py` / `pdf.py`). The generic template's "System Overview" / "Scaling" / project-structure sections do not apply to a bug-fix milestone and are omitted; the template's Integration Points / Internal Boundaries / Anti-Patterns sections are kept and filled with real answers.

## (a) Where the delimiter-aware path-quoting helper must live

### Measured import graph (module-scope imports only, read from each file's own `import`/`from` lines)

```
typsphinx/__init__.py
        │
        ▼
typsphinx/builder.py ───────► typsphinx/pdf.py                (leaf: stdlib only)
        │  │  │                     ▲
        │  │  └──────────────────────────────────────────────┐
        │  ▼                                                  │
        │  typsphinx/template_registry.py ────(module scope)──┤ NOTHING from typsphinx
        │        │                                            │
        │        └─(FUNCTION-scoped, lazy)──► typsphinx.builder.TypstBuilder
        │                                       (deliberate cycle-breaker, see below)
        ▼
typsphinx/writer.py
        │  │
        │  ├──► typsphinx/template_engine.py    (leaf: stdlib + sphinx only)
        │  ├──► typsphinx/template_registry.py  (already a dependency of builder.py too)
        │  └──► typsphinx/translator.py         (leaf: stdlib + docutils/sphinx only)

typsphinx/translator.py       — leaf. Zero `from typsphinx...` imports.
typsphinx/template_engine.py  — leaf. Zero `from typsphinx...` imports.
typsphinx/pdf.py              — leaf. Zero `from typsphinx...` imports.
```

Concretely, from the files themselves:

| File | `from typsphinx.X import ...` (module scope) |
|------|---|
| `builder.py:22-29` | `pdf`, `template_registry`, `translator` (`derive_master_edge_keys`), `writer` (`TEMPLATE_OUTPUT_DIR`, `TypstWriter`) |
| `writer.py:15-26` | `template_engine`, `template_registry`, `translator` |
| `template_registry.py` | **none** at module scope. `template_registry.py:92` (`_has_case_collision`) does `from typsphinx.builder import TypstBuilder` **inside the function body**, with an explicit comment explaining this is deliberate: importing `builder` at `template_registry.py`'s own module scope would deadlock the import graph, because `builder.py` already imports `template_registry.py` at ITS module scope. |
| `translator.py` | none |
| `template_engine.py` | none |
| `pdf.py` | none |

So the graph already has one hard fact that determines the answer: **`builder.py` and `template_registry.py` form a module-scope-import cycle in the "back" direction only** (`builder.py → template_registry.py` at module scope; `template_registry.py → builder.py` only lazily, function-scoped, at runtime). `writer.py` also already imports both `template_registry.py` and `translator.py` at module scope, and `builder.py` imports `writer.py` at module scope too.

### The answer

**New module.** Name it `typsphinx/pathfmt.py` (or `path_quoting.py` — any name distinct from the existing five role-named files; the point is it must be a **leaf**: it imports nothing from `typsphinx` itself, only stdlib, matching the shape `translator.py`/`template_engine.py`/`pdf.py` already have).

Why a new leaf module, and not one of the existing files:

- **Not `builder.py`.** `writer.py` already imports `builder.py`'s sibling role — no, more precisely: `builder.py` imports `writer.py` at module scope (`builder.py:29`). If the quoting helper lived in `builder.py` and `writer.py` needed to import it, `writer.py` would need `from typsphinx.builder import quote_path` at module scope — but `builder.py` already does `from typsphinx.writer import TEMPLATE_OUTPUT_DIR, TypstWriter` at its own module scope. That is a direct, unconditional two-file cycle (`builder → writer → builder`), which Python cannot resolve at module-scope-import time (whichever module starts importing first will hit a partially-initialized sibling module and raise `ImportError`/`AttributeError` on the not-yet-defined name). This is not hypothetical — it is the identical shape `template_registry.py`'s own comment at line ~86-90 was written to avoid with `builder.py`, and that comment is the direct evidence for this conclusion.
- **Not `writer.py`.** `builder.py` already imports `writer.py` (`TEMPLATE_OUTPUT_DIR`, `TypstWriter`) at module scope. If the helper lived in `writer.py`, `builder.py`'s existing import line would need to grow to include it — no NEW cycle there — but `template_registry.py` would then need `from typsphinx.writer import quote_path` at module scope. `writer.py` does not import `template_registry.py`... wait, it does (`writer.py:21-25`, `from typsphinx.template_registry import RESERVED_REGISTRY_KEY, TemplateRegistryEntry, resolve_template_registry`). So `template_registry.py → writer.py` would create `writer.py → template_registry.py → writer.py`, a direct two-file cycle. Also structurally wrong home: `writer.py` is the per-document rendering driver, not naturally where a builder-side and registry-side message-formatting utility belongs.
- **Not `template_registry.py`.** This module already has ONE deliberately-broken cycle with `builder.py` (via the lazy, function-scoped import). Adding new content here that `builder.py` and `writer.py` both need to import back would either (i) require a second lazy-import trick at every call site in two other files (fragile, and the existing trick is scoped narrowly to a single internal predicate, not meant to be a general pattern), or (ii) create the same `builder.py ↔ template_registry.py` cycle at module scope that the existing lazy import exists specifically to avoid.
- **Not `translator.py`.** Technically safe — `translator.py` is already a leaf, `builder.py` already imports one name from it (`derive_master_edge_keys`, `builder.py:28`) and `writer.py` already imports two names from it (`translator.py:26`), so adding a quoting-helper import here creates zero NEW cycle risk. This is a legitimate technical fallback if a project-owner strongly prefers not adding a sixth file. But it is a poor thematic fit: `translator.py` is exclusively "doctree node → Typst markup" (its own existing helper, `escape_typst_string()`, is a `.typ`-*syntax* escaper for content embedded in emitted Typst source); the new helper is a *human-readable diagnostic/log/error-message* formatter for filesystem paths, consumed only by `builder.py`/`writer.py`/`template_registry.py`'s `logger.warning`/`ExtensionError`/`logger.debug` call sites — none of which touch doctree translation. Mixing the two would make `translator.py`'s already-large surface (8,009 lines) carry an unrelated responsibility.
- **A new leaf module has zero cycle risk by construction.** Since `builder.py`, `writer.py`, and `template_registry.py` all either already import each other or are imported by each other, the only shape guaranteed to be importable from all three at module scope with no cycle is a module that imports NOTHING from `typsphinx` back — exactly what `translator.py`/`template_engine.py`/`pdf.py` already are. The new module joins that leaf tier. `builder.py` gains one more `from typsphinx.pathfmt import ...` line beside its existing four; `writer.py` gains one beside its existing three; `template_registry.py` gains its FIRST module-scope `typsphinx`-internal import (previously it had none — this is a new, but safe, edge in the graph, running module→leaf, never leaf→module).

**Cycle risk, stated concretely:** the risk is not diffuse — it is exactly two named two-file cycles (`builder.py↔writer.py` if the helper lives in either one of that pair, `builder.py↔template_registry.py` if it lives in `template_registry.py`), both of which already exist as *directed* edges today and would become *bidirectional* the moment either file imports the helper from the other. A new leaf module sidesteps both by definition — it has no back-edge to create.

## (b) `escape_typst_string()` / `visit_image()` — confirmed local to translator.py

Both live in `typsphinx/translator.py`:

- `escape_typst_string()` — `translator.py:156-187`. Pure string function, no dependencies beyond stdlib `str` methods (already imported `re` is unused by it). Escapes `\`, `"`, `\n`, `\r`, `\t` in that order, for embedding inside a Typst `"..."` string literal — this is the module's "single source of truth for string-literal escaping" per its own docstring, already consumed elsewhere in the file (e.g. `visit_literal`, per the docstring's own claim, and the Phase-38 IND-04 comment at `translator.py:6090` referenced in PROJECT.md's footer).
- `visit_image()` — `translator.py:4718-4766`. The two unescaped emission sites are:
  - `translator.py:4746`: `self.add_text(f'  image("{adjusted_uri}"')` (inside a figure — 2-space indent variant)
  - `translator.py:4749`: `self.add_text(f'image("{adjusted_uri}"')` (block-level, no `#` prefix, code-mode variant)

Both are in the SAME method, in the SAME file as `escape_typst_string()`. **Confirmed: defect 2 gap 2 is a pure local change — one file (`translator.py`), no cross-module import needed at all**, since the helper is already module-local.

### Ordering relative to `_compute_relative_image_path()`

`translator.py:4736-4749`:
```python
uri = node.get("uri", "")
current_docname = getattr(self.builder, "current_docname", None)
adjusted_uri = self._compute_relative_image_path(uri, current_docname)   # transform FIRST
if self.in_figure:
    self.add_text(f'  image("{adjusted_uri}"')                          # emit SECOND — unescaped today
else:
    self.add_text(f'image("{adjusted_uri}"')                            # emit SECOND — unescaped today
```

`_compute_relative_image_path()` (`translator.py:5047-5140+`) is a `PurePosixPath`-only computation — it never touches `os.path`/`ntpath`, so its OWN internal arithmetic always produces forward-slash-joined output (`str(rel_path)`, `"/".join(down_parts)`, `"../" * up_count`). It does **not**, however, strip or reject backslashes that were already present in its `image_uri` input (the `node["uri"]` value, which for a rehomed absolute image is the key `_track_image()` built — see part (c) — and for an ordinary image is the source-root-relative URI Sphinx supplied, verbatim). So `adjusted_uri` can still contain a literal backslash character today (e.g. if `_track_image()`'s gap-1 basename bug — part (c) below — carries one through into the relocation key, or if a third-party extension sets `node["uri"]` to a raw backslash-separated string that never reached `_track_image()`'s absolute-URI branch at all).

**Escaping must happen AFTER `_compute_relative_image_path()`, at the interpolation point** — i.e. wrap `adjusted_uri` itself, not `uri`:

```python
adjusted_uri = self._compute_relative_image_path(uri, current_docname)
escaped_uri = escape_typst_string(adjusted_uri)
...
self.add_text(f'  image("{escaped_uri}"')   # and the non-figure branch identically
```

Escaping `uri` before the `_compute_relative_image_path()` call instead would be wrong: that method does its own `PurePosixPath(...)`/`.relative_to(...)`/`.parts` arithmetic on the raw value, and feeding it an already-`\\`-doubled or `\"`-escaped string would corrupt that arithmetic (e.g. a doubled backslash is no longer recognized as a single path separator by anything downstream, and `PurePosixPath` never treated backslash as a separator to begin with — the corruption would be in the STRING CONTENT, not the parsing, but it is still the wrong value to relativize). `escape_typst_string()` is a syntax-literal escaper, not a path-shape transform, so it belongs strictly after every path-shape transform is finished and immediately before the value is written into Typst source.

## (c) `_escapes_outdir()` — blast radius of normalizing it, per call site (measured, not asserted)

`_escapes_outdir()` (`builder.py:197-238`) has exactly **two** call sites in the whole package (grep-verified — no third site exists in `builder.py`, and it is not imported/re-called from `writer.py`, `translator.py`, or `template_registry.py`):

1. `builder.py:670`, inside `_resolve_target_stem()` (the `typst_documents` target-stem guard, OUT-02).
2. `builder.py:1727`, inside `_track_image()` (the image-rehome escape decision).

The current body:
```python
def _escapes_outdir(stem: str) -> bool:
    segments = stem.replace("\\", "/").split("/")          # normalized, used only for the ".." test
    return ".." in segments or posixpath.isabs(stem) or _is_drive_qualified(stem)  # RAW stem
```

The candidate fix (mirroring `_is_absolute_image_uri()`'s own idiom, `builder.py:121-194`): normalize once, then test everything against the normalized string:
```python
def _escapes_outdir(stem: str) -> bool:
    normalized = stem.replace("\\", "/")
    segments = normalized.split("/")
    return ".." in segments or posixpath.isabs(normalized) or _is_drive_qualified(normalized)
```

**Called in isolation (bypassing both production call sites), this fix DOES flip two shapes** — verified by direct execution on this machine (CPython 3, Linux, `posixpath`):

| Input (raw, as if `_escapes_outdir()` were called directly) | Current (buggy) | Fixed |
|---|---|---|
| `"\foo\bar"` (driveless-absolute, one leading backslash) | `False` | `True` |
| `"\\server\share\bar"` (UNC) | `False` | `True` |
| `"C:manual"` (drive-qualified) | `True` (unaffected — `_is_drive_qualified` never looked at slashes) | `True` |
| `"manuals/guide"` (ordinary relative) | `False` | `False` (unaffected) |
| `"/abs/manual"` (posix-absolute) | `True` (unaffected — already starts with `/`) | `True` |

This confirms the function-level defect PROJECT.md describes is real: `_escapes_outdir()` is not, by itself, the platform-independent pure-string predicate its sibling `_is_absolute_image_uri()` already is (and which its own docstring's doctest style — `_escapes_outdir("/abs/manual")` — implies it should be).

**But at BOTH of the two actual production call sites, the fix changes NOTHING**, because both callers already hand `_escapes_outdir()` an argument that has already been backslash-normalized before the call — the two shapes that flip in isolation never reach `_escapes_outdir()` in their raw form through either call site:

- **Call site 1 (`_resolve_target_stem()`, `builder.py:608-732`).** Line 662, `stem = stem.replace("\\", "/")`, runs UNCONDITIONALLY before `_escapes_outdir(stem)` is called at line 670 (comment at 654-661 names this "OUT-01: normalize a Windows-authored separator to POSIX style up front, unconditionally"). By the time `_escapes_outdir()` sees `stem`, it already contains zero backslash characters — normalizing again inside `_escapes_outdir()` is an idempotent no-op. Verified by simulating the exact call-site sequence:
  ```
  raw target            → pre-normalized stem → _escapes_outdir(stem) BEFORE fix → AFTER fix
  '\foo\bar.typ'         '/foo/bar'             True                              True   (no flip)
  '\\server\share\file.typ' '//server/share/file' True                            True   (no flip)
  'C:manual.typ'          'C:manual'             True                              True   (no flip)
  'manuals/guide.typ'     'manuals/guide'        False                             False  (no flip)
  '../escape.typ'         '../escape'            True                              True   (no flip)
  ```
- **Call site 2 (`_track_image()`, `builder.py:1637-1790`).** Line 1719-1721, `rel_uri = path.relpath(resolved_uri, self.doctreedir).replace(path.sep, "/")`, runs before `_escapes_outdir(rel_uri)` at line 1727. On POSIX (`path` = `posixpath`), `path.sep` is `"/"`, so this `.replace()` call is literally a no-op for backslash characters — it does NOT strip them the way call site 1's literal `.replace("\\", "/")` does. Despite that, no flip was observed for any of five tested absolute/UNC/drive-qualified shapes, because `posixpath.relpath()` itself — called with a `resolved_uri` that doesn't start with `/` — treats the whole string as ONE relative path component and prepends `os.getcwd()`-derived `"../"` segments to reach `doctreedir`; the resulting `rel_uri` therefore already contains a literal `".."` segment, which the PRE-EXISTING (never-buggy) `".." in segments` disjunct already catches, before the isabs/drive-qualified disjuncts are even relevant. Verified directly (Linux, this repo's actual `doctreedir` shape):
  ```
  resolved_uri                  rel_uri (both before/after fix, identical string)                          before  after
  '\foo\bar.png'                 '../../home/.../typsphinx/\foo\bar.png'                                    True    True
  '\\server\share\bar.png'       '../../home/.../typsphinx/\\server\share\bar.png'                          True    True
  'C:\foo\bar.png'               '../../home/.../typsphinx/C:\foo\bar.png'                                  True    True
  'C:foo/bar.png'                '../../home/.../typsphinx/C:foo/bar.png'                                   True    True
  '/abs/foo/bar.png'             '../../abs/foo/bar.png'                                                    True    True
  ```

**Precise blast-radius conclusion:** normalizing `_escapes_outdir()` changes the CLASSIFICATION OF NEITHER call site for any shape tested (both remain byte-identical before/after, `escaped=True` for every escaping shape, unchanged). The fix's value is (i) making the function correct and self-sufficient as a standalone predicate — matching this module's own D-05 platform-independence precedent and closing the gap a future third call site or a direct unit test would otherwise hit, and (ii) removing the latent inconsistency between `_escapes_outdir()` and its sibling `_is_absolute_image_uri()`, which the PROJECT.md milestone text explicitly calls out as the reason to fix it now. It is **not** a fix that changes observed build behavior at either of today's two call sites — a regression test asserting on `_resolve_target_stem()`'s or `_track_image()`'s OUTPUT for these shapes would already pass both before and after this change; a test must call `_escapes_outdir()` directly (as its own doctests already do) to observe the flip. This has a direct planning consequence: the RED-first gate for this defect must be a **direct unit test on `_escapes_outdir()` itself**, not an integration assertion through either call site (an integration-level test would be tautologically green both before and after, which is exactly the "no test covers it, CI is green" trap PROJECT.md's footer already names for all three defects in this milestone).

## (d) Build order — files touched per fix, and the two named hazards

### Files each fix touches (function/line granularity)

| Fix | New file | `builder.py` | `translator.py` | `writer.py` | `template_registry.py` |
|---|---|---|---|---|---|
| **1. `_escapes_outdir()` normalization** | — | `197-238` (`_escapes_outdir` body only) | — | — | — |
| **2. `_track_image()` escape branch** (3 gaps) | — | `~1761-1772` (gap 1 basename, gap 3 key length) | `4746`, `4749` (gap 2, `visit_image`) | — | — |
| **3. Path-quoting helper rollout** | new leaf module (part a) | `303-402` (3 message-builder fns), `697`, `942/964/965/999/1007/1008/1015`, `1767`, `2056/2066` | — | `511-513` | `410/422/433` |

Two overlaps are load-bearing for the wave decomposition:

1. **File-level overlap: Fix 1, Fix 2, and Fix 3 ALL touch `builder.py`.** Per this project's own standing hazard (`.claude` memory: "disjoint files still collide at merge" / worktree isolation is the standing execution mode per `CLAUDE.md`) — even where the edited LINE RANGES within `builder.py` don't literally overlap in a diff, this project's convention is that same-file edits across parallel plans in the same wave are treated as a collision risk, not treated as safe-by-line-range.
2. **Line-level adjacency, not just same-file: Fix 1's `_escapes_outdir()` (lines 197-238) is called FROM inside `_track_image()` at line 1727** — i.e. the exact method Fix 2 is editing at lines ~1761-1772 (13 lines further down the SAME method). **Fix 3's quoting-helper migration explicitly names `builder.py:1767`** (the `_track_image()` escape-branch warning, `"could not rehome image URI {resolved_uri!r} ... relocated to {key!r}"`) as one of its 20 target sites — and `key` at line 1767 is exactly the value Fix 2's gap 1 (basename normalization) and gap 3 (length bound) change. **All three fixes converge on the same ~30-line region of `_track_image()` and its immediate caller `_escapes_outdir()`.** This is not a hand-wavy "same file" claim — it is the same method plus the function it calls, and the same emitted warning string that Fix 2 changes the VALUE of and Fix 3 changes the QUOTING of.
3. **Shared test file: `TestWindowsPathEscapingRegressionGuard`** (`tests/test_templates_path_collision_gate.py:412` onward) is the existing regression-guard class 57-11 wrote for the three `builder.py` message sites it already fixed (`_conf17_violation_message`, `_templates_path_collision_message`, `_bundle_destination_collision_message`, lines 303-402). PROJECT.md's footer states the quoting helper "must ... be gated by both `TestWindowsPathEscapingRegressionGuard` and the single-quote case 57-REVIEW IN-01 named as missing" — i.e. this ONE class is the natural home for Fix 3's new coverage across ALL of `builder.py`/`writer.py`/`template_registry.py`'s sites. If Fix 3 is split into parallel plans (one per file) that each extend this same class/file with new test methods in the same wave, that is exactly the "one plan changes an emitted string, another plan asserts on it, same wave" hazard this project has already hit once (57-11's own CI-matrix cost) and named as a standing risk in the operator's own memory.

### Proposed decomposition

**Wave 1 — two genuinely independent plans, zero file overlap with anything else in this milestone, safe to run in parallel:**

- **Plan 1a — new quoting-helper module.** Create the new leaf module (part a) with the delimiter-aware helper and its own unit tests (including the single-quote-in-path case 57-REVIEW named as missing, `.planning/PROJECT.md:71-72`). Touches only the new file + its own new test file. No existing file is edited yet — this plan does not wire the helper into any call site.
- **Plan 1b — `visit_image()` escaping (defect 2 gap 2).** Wrap `adjusted_uri` in `escape_typst_string()` at both `translator.py:4746` and `4749` (part b). Touches only `translator.py` + its own test file. Fully independent of Plan 1a (uses the PRE-EXISTING `escape_typst_string()`, not the new helper) and of everything in Wave 2 below (never touches `builder.py`).

**Wave 2 — depends on Wave 1 Plan 1a (the helper must exist to be imported); internally sequenced, not parallel, for the `builder.py`-touching parts:**

- **Plan 2a (sequential, single plan) — the whole `builder.py` change set: Fix 1 + Fix 2 gaps 1/3 + Fix 3's `builder.py` rollout, as ONE plan.** Given finding (c) — Fix 1 changes NOTHING observable at either call site, so it carries near-zero risk to bundle — and given the tight line-level adjacency named above (Fix 2's gap 1/3 sit 13-45 lines from the `_escapes_outdir()` call Fix 1 touches, and Fix 3's line-1767 message site is the SAME warning Fix 2 changes the value of), splitting these three into separate parallel plans against the same file/method is the exact hazard this project has already paid for once. Doing them as one sequential plan (or, if the executing agent prefers smaller reviewable units, as 2-3 STRICTLY SEQUENTIAL sub-plans in the SAME wave-ordinal — never parallel worktrees — each waiting on the prior one's merge) removes both the same-file and the same-string hazards structurally, because there is only ever one active edit to `builder.py` at a time. This plan also extends `TestWindowsPathEscapingRegressionGuard` for every `builder.py` site (owns that file exclusively for this wave).
- **Plan 2b (parallel-safe alongside 2a — disjoint file, `writer.py` only) — Fix 3's `writer.py` rollout.** `writer.py:511-513`, the wrapper-render debug log. Genuinely independent of `builder.py` (no shared import, no shared emitted string, no shared assertion target) — safe to parallelize with 2a PROVIDED it does not also extend `TestWindowsPathEscapingRegressionGuard` (route its own new assertions through a writer-scoped test module/class instead, to avoid the same-test-file hazard named above even though the files under test differ).
- **Plan 2c (parallel-safe alongside 2a — disjoint file, `template_registry.py` only) — Fix 3's `template_registry.py` rollout.** `template_registry.py:410/422/433`, the declared-template validation messages. Same independence argument and same same-test-file caveat as 2b.

**Why this order and not, e.g., Fix-1-then-Fix-2-then-Fix-3 as three fully separate waves:** part (c)'s finding that Fix 1 has zero observable effect at either production call site means there is no CORRECTNESS dependency forcing Fix 1 to land before Fix 2 (Fix 2's gap 1/3 do not read `_escapes_outdir()`'s return value at all — they touch the KEY CONSTRUCTION inside the `escaped` branch, which is already reached correctly today). The only real ordering constraint in this milestone is Wave 1 → Wave 2 (the quoting helper must exist before anything imports it), plus the internal sequencing of `builder.py`'s three fixes to avoid the file/line/string collisions documented above. Fix 2's gap 2 (`translator.py`) and Fix 3's `writer.py`/`template_registry.py` legs have no dependency on `builder.py`'s internal sequencing and should not be blocked behind it.

## Internal Boundaries (template section, filled)

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `builder.py` ↔ new `pathfmt.py` (leaf) | direct function import, module scope | New edge, no cycle risk (leaf has no back-import) |
| `writer.py` ↔ new `pathfmt.py` (leaf) | direct function import, module scope | New edge, no cycle risk |
| `template_registry.py` ↔ new `pathfmt.py` (leaf) | direct function import, module scope | New edge — `template_registry.py`'s FIRST module-scope `typsphinx`-internal import; still safe because the target is a leaf |
| `builder.py` ↔ `writer.py` | `builder.py` imports `writer.py` at module scope (pre-existing) | Do NOT add a `writer.py → builder.py` import for the quoting helper — direct cycle |
| `builder.py` ↔ `template_registry.py` | `builder.py` imports `template_registry.py` at module scope; `template_registry.py` imports `builder.py` only lazily/function-scoped (pre-existing, deliberate) | Do NOT add a second module-scope `template_registry.py → builder.py` import for the quoting helper — would re-create the exact cycle the lazy import already works around |
| `_escapes_outdir()` (builder.py:197) ↔ `_resolve_target_stem()` (builder.py:608) | direct call, same file | Call site 1; argument already backslash-normalized by caller (part c) |
| `_escapes_outdir()` (builder.py:197) ↔ `_track_image()` (builder.py:1637) | direct call, same file, "cross-domain reuse" per the existing comment at builder.py:1719-1725 | Call site 2; argument already backslash-normalized by caller (part c) |
| `escape_typst_string()` (translator.py:156) ↔ `visit_image()` (translator.py:4718) | direct call, same file, same method | Gap 2's whole fix; must wrap `adjusted_uri` (post-`_compute_relative_image_path()`), never `uri` (part b) |

## Anti-Patterns (specific to this integration)

### Anti-Pattern 1: Putting the quoting helper in `builder.py` or `writer.py` "because that's where the call sites are"

**What people do:** Add the new helper as a private function inside `builder.py` (most call sites are there) and have `writer.py`/`template_registry.py` import it from there.
**Why it's wrong:** `builder.py` already imports `writer.py` at module scope; `writer.py` importing back from `builder.py` is an unconditional two-file import cycle that fails at interpreter start, not at call time — this is not a style objection, it is a hard `ImportError`.
**Do this instead:** New leaf module (part a).

### Anti-Pattern 2: Treating Fix 1 as a blocking prerequisite for Fix 2

**What people do:** Sequence "fix `_escapes_outdir()` first, then fix `_track_image()`'s basename/key-length gaps, because they're in the same function family."
**Why it's wrong:** Part (c) shows Fix 1 changes nothing observable at either call site; Fix 2's gaps 1 and 3 are about the KEY STRING CONSTRUCTION inside the already-correctly-reached `escaped` branch, not about whether that branch is reached. Treating them as strictly ordered adds a false dependency and unnecessarily serializes work that could, in principle, be reviewed independently — the real reason to keep them in one plan is the file/line-adjacency collision risk (item 2 under "two overlaps"), not a correctness dependency.

### Anti-Pattern 3: Parallel plans that each extend `TestWindowsPathEscapingRegressionGuard` in the same wave

**What people do:** Split Fix 3's rollout into "builder.py plan", "writer.py plan", "template_registry.py plan" and let each add its own new test methods to the existing `TestWindowsPathEscapingRegressionGuard` class for coverage symmetry.
**Why it's wrong:** All three plans editing the same test class/file in the same wave reproduces exactly the "emitted string changed by one plan, asserted on by another, same wave" hazard already named in this project's own operating history (57-11's two burned CI matrices were a variant of this same class of defect — a message-formatting change whose test coverage didn't match the real message builder).
**Do this instead:** Either keep all `TestWindowsPathEscapingRegressionGuard` edits inside the single sequential `builder.py` plan (2a) and give the parallel `writer.py`/`template_registry.py` plans (2b/2c) their own separate test classes/modules, or run 2b/2c strictly after 2a merges if shared-class coverage is required.

## Sources

- `typsphinx/builder.py` (read in full, 2440 lines) — import block (8-29), `_is_drive_qualified` (86-118), `_is_absolute_image_uri` (121-194), `_escapes_outdir` (197-238), the three 57-11 message builders (303-402), `_validate_output_path_collisions` (866-1019, the census lines 942/964/965/999/1007/1008/1015), `_track_image` (1637-1790, including the 1767 warning and the 1761-1772 key construction), `_copy_bundle_directory` (the 2056/2066 census lines)
- `typsphinx/translator.py` lines 1-200 (`escape_typst_string`, 156-187) and 4690-4770 (`visit_image`/`depart_image`, 4718-4769), plus `_compute_relative_image_path` (5047-5140+)
- `typsphinx/writer.py` (read in full, 515 lines) — import block (8-26), `render_wrapper`'s debug log (511-513)
- `typsphinx/template_registry.py` (read in full, 529 lines) — import block (27-31), the lazy cycle-breaking comment (`_has_case_collision`, ~79-98), the three census lines (410/422/433)
- `/home/yuta/Documents/typsphinx/CLAUDE.md` (Architecture section, worktree-isolated execution section)
- `/home/yuta/Documents/typsphinx/.planning/PROJECT.md` (top "Current Milestone: v0.9.1" section, plus the 2026-08-27 and 2026-08-22 footer entries for the 57-11 prior-art and `TestWindowsPathEscapingRegressionGuard` context)
- `tests/test_templates_path_collision_gate.py` (grep-verified location and line number of `TestWindowsPathEscapingRegressionGuard`, line 412)
- Direct execution (Python 3, this machine, `posixpath`) of both the current and the candidate-fixed `_escapes_outdir()` bodies against all five documented shapes, at both call sites' actual invocation contexts — the basis for the part (c) blast-radius table

---
*Architecture research for: typsphinx v0.9.1 Windows path correctness (bug-fix integration, not greenfield)*
*Researched: 2026-08-27*
