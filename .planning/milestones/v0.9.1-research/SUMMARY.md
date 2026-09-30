# Research Synthesis: typsphinx v0.9.1 "Windows Path Correctness"

**Synthesized:** 2026-08-27  
**Milestone:** v0.9.1 — Windows path-shape correctness (bug-fix, three defect families)  
**Research Status:** Complete (STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md all synthesized)

---

## Executive Summary

typsphinx is a mature Sphinx extension with three latent path-handling defects related to Windows path shapes (backslash separators, drive letters, UNC paths). The defects are invisible on Windows CI today because the extension runs on Linux CI with pure string functions — platform-shape testing is fully decoupled from platform identity, per deliberate Phase-55 architecture. This milestone closes all three by normalizing paths to forward slashes before classification/emission, adding delimiter-aware quoting for diagnostics, and bounding relocation-key basename length against the portable 255-byte filesystem limit.

**Core technical thrust:** The defects cluster around two functions (`_escapes_outdir` in builder.py and image-path handling in both builder.py/translator.py) that apply Windows-shape classification or emit paths without first normalizing backslashes to forward slashes. The fixes are low-complexity (three to four one-line or ~10-line changes) but depend critically on **two technical constraints that must carry forward into planning:**

1. **Typst's rejection of backslash is value-level, not syntax-level** — escaping the backslash in Typst source (`\\`) does not stop Typst's refusal; the backslash must be removed from the *value* before it reaches the string literal. Therefore, `escape_typst_string()` at image-emission sites is necessary for defense-in-depth (syntax-breaking characters like `"`) but **cannot by itself fix** the backslash-in-path defect — relocation-key normalization (removing backslash at the builder layer) and escaping (handling other chars at the translator layer) are **coupled, not independent fixes**. Landing only one without the other leaves the defect active.

2. **The "zero test edits" discipline cannot hold for this milestone** — exactly two existing tests hard-code `repr()`'s backslash-doubling behavior as their pass criterion. When the quoting-helper fix switches these sites from `!r` to the new delimiter-aware helper, both tests WILL FAIL on POSIX immediately. These two test edits are **expected and required work**, not regressions to revert. They must land in the same wave as the source fixes.

The recommended approach applies the composite path-classification idiom `_is_drive_qualified() + posixpath.isabs()` (already established in this codebase) uniformly across all three defect families, uses a new leaf module for the quoting helper to avoid import cycles, and structures gates to exercise both POSIX-runnable string assertions and one real `typst.compile()` call to catch value-level behaviors.

---

## Key Findings

### From STACK.md (Technical Recommendations)

**Path-shape classification authority:**
- Use composite: backslash-normalize first, then `posixpath.isabs(normalized) or _is_drive_qualified(normalized)`
- This idiom is already in `_is_absolute_image_uri()`; `_escapes_outdir()` must match it
- Do NOT use `ntpath.isabs()` / `os.path.isabs()` directly — diverged between CPython 3.12 and 3.13
- Do NOT use `pathlib.PureWindowsPath` — introduces a different boundary

**Filesystem component-length limit:**
- Hardcode `_MAX_BASENAME_BYTES = 255` (ext4/APFS limit, conservative for NTFS)
- Truncate after UTF-8 encoding but slice in `str` space (never split multi-byte UTF-8)

**Delimiter-aware path-quoting without backslash-escaping:**
- Keep `repr()`'s quote-disambiguation (prefer `'`; switch to `"` if value contains `'` and not `"`)
- Drop `repr()`'s backslash-doubling
- Hand-rolled ~10-line helper in a new leaf module: pick delimiter, interpolate raw value

**Test strategy:**
- Use `pytest.mark.parametrize` over hand-built Windows-shaped string literals on every CI lane
- Exception: gap 2 needs real `typst.compile()` call to surface value-level rejection

### From FEATURES.md (Verified Observable Behaviors)

**Escape-guarding config path:**
- Sphinx's `latex_documents` does zero path-shape checking; typsphinx already refuses overescaping
- This milestone makes detection platform-independent (normalize before predicates)
- Mechanical fix: swap raw `stem` for normalized string at `builder.py:238`

**Relocation key construction:**
- Three precedents (Sphinx's `FilenameUniqDict`, `DownloadFiles`, pip wheel cache) preserve human-readable portion
- Truncate only basename half; keep 8-hex-char SHA-1 digest intact (collision-anchor)

**Image-path escaping:**
- Typst rejects backslash BY VALUE, not syntax — escaping doesn't help
- Normalization (removing backslash) is necessary AND sufficient
- `escape_typst_string()` needed for OTHER syntax-breaking characters (`"`, newlines)

**Diagnostic path quoting:**
- Sphinx/pip/mypy use plain interpolation or double-quote delimiters with no escaping
- "Restore `repr()`'s quote-disambiguation without backslash-doubling" matches ecosystem convention

### From ARCHITECTURE.md (Integration Constraints)

**Module structure:**
- `builder.py` ↔ `writer.py` form direct module-scope cycle if helper lives in either
- `builder.py` ↔ `template_registry.py` have pre-existing deliberate cycle-break
- **Solution: New leaf module** (e.g., `typsphinx/pathfmt.py`) importing nothing from typsphinx

**Defect 1 blast radius** (`_escapes_outdir()` normalization):
- Called at exactly two production sites; both pre-normalize input
- Fix changes CLASSIFICATION OF NEITHER call site (both remain byte-identical)
- Fix's value: make function correct as standalone predicate, remove inconsistency with `_is_absolute_image_uri()`
- RED-first gate MUST call `_escapes_outdir()` directly (integration test would be tautologically green)

**Three fixes converge on same method region:**
- Defect 1: `_escapes_outdir()` 197-238 (called from 1727 inside `_track_image()`)
- Defect 2: `_track_image()` 1761-1772 + `visit_image()` at `translator.py:4746,4749`
- Defect 3: `builder.py:1767` rehome warning + ~12 other sites
- File/line/string adjacency makes parallel plans risky; sequential bundling recommended

**Wave structure:**
- **Wave 1 (parallel):** New leaf module + its tests; translator.py escaping (independent)
- **Wave 2 (sequential within builder.py, parallel outside):** Builder.py triple-fix bundled; writer.py separate; registry.py separate

### From PITFALLS.md (Critical Hazards)

**Pitfall 1 — two tests WILL break on intended fix (EXPECTED):**
- `test_out02_escape_target_gate.py::test_escape_shape_refused_with_containment_proof[drive]` line 134
- `test_builder.py::test_post_process_images_rehome_escape_relocates_with_warning` line 598
- Both explicitly expect `repr()`'s doubling; both fail when sites switch to new helper
- **Recovery:** edit both assertions for new helper's output

**Pitfall 2 — `template_registry.py:410` type-check site must NOT use new helper:**
- Line 408-412 fires when `template` is NOT `str`/`os.PathLike` (type error case)
- Leave this site on `!r`; route only lines 422/433 through helper

**Pitfall 3 — `os.PathLike` values need stringification:**
- `template_registry.py` accepts `pathlib.Path` templates; existing test exercises it
- Helper's first action: `value = str(value)`

**Pitfall 4 — do NOT silently fold backslash to slash at image-emission:**
- At classification: safe (wrong classification = unnecessary rehome + warning)
- At emission: unsafe (silent rewriting changes which file Typst opens)
- Correct fix: `escape_typst_string(adjusted_uri)` only

**Pitfall 5 — length-bound truncation has five failure modes:**
- Wrong component truncated; UTF-8 mid-character split; extension lost; collision reintroduced; empty-stem edge
- Correct: split extension; truncate stem in `str` space; size-check in UTF-8 bytes; anchor digest; verify collision preservation

**Pitfall 6 — POSIX-only unit tests necessary; CI dispatch not first discovery:**
- Phase 57 burned two CI matrix runs
- Proven pattern: `TestWindowsPathEscapingRegressionGuard` calling real functions directly on POSIX
- Correct discipline: commit RED-first fixture, confirm failure locally, fix, reconfirm green, THEN dispatch CI

---

## Implications for Roadmap

### Phase Structure (Recommended)

**Phase A (Wave 1):** Create delimiter-aware path-quoting helper module + unit tests (new `pathfmt.py` leaf module). Parallel safe.

**Phase B (Wave 1):** Escape image URIs in Typst `image()` emission (`translator.py:4746,4749`). Parallel safe with A. Uses pre-existing `escape_typst_string()`.

**Phase C (Wave 2):** Normalize and bound image-relocation keys, fix escape-detection normalization (bundled defects 1/2 gaps 1/3 in `builder.py`). Sequential single plan.

**Phase D (Wave 2):** Wire delimiter-aware helper into `builder.py` warning sites (~10 sites). Edit two broken tests (lines 134, 598). Parallel safe (separate from C).

**Phase E (Wave 2):** Wire delimiter-aware helper into `writer.py` debug log. Separate test class. Parallel safe with D.

**Phase F (Wave 2):** Wire delimiter-aware helper into `template_registry.py:422,433` (exclude line 410). Separate test class. Parallel safe with D/E.

### Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| **Stack** | HIGH | CPython source diff, live measurements, composite predicate pattern proven by existing `_is_absolute_image_uri()` |
| **Features** | HIGH | Verified against Sphinx 9.1.0, mypy, pip, real `typst.compile()`. Value-level rejection finding directly measured. |
| **Architecture** | HIGH | Import graph claims read from module blocks; line numbers verified; call site pre-normalization confirmed. Import-cycle analysis concrete. |
| **Pitfalls** | HIGH | Every pitfall anchored to line number/file. Test-breakage cases guaranteed on POSIX. Pitfalls 2/3 read from source. Pitfalls 4/5/6 verified via measurement/Phase-57 precedent. |

### Gaps to Address

1. Exact UTF-8 boundary-safe truncation algorithm implementation (spec complete, needs prototyping in Phase C)
2. Extension preservation in truncation implementation choice
3. Grep-confirm exact site census during planning (`builder.py:942,964,965,999,1007,1008,1015,1767,2056,2066,697`, `writer.py:511-513`, `template_registry.py:410,422,433`)

---

## Research Flags for Roadmap

**No phases require targeted research** — all technical patterns and call sites fully mapped. Phase 57's existing `TestWindowsPathEscapingRegressionGuard` infrastructure is already in-repo and can be reused directly.

---

## Summary of Established Cross-Cutting Facts

These four findings are independently re-measured and carried forward as established facts:

1. **Typst rejects backslash at VALUE level, not syntax level** — escaped backslash in source still fails. `escape_typst_string()` is necessary but not sufficient; backslash must be removed from value first. Fixes are coupled, not independent.

2. **`_escapes_outdir()` normalization gap is not user-reachable** — both call sites pre-normalize. Fix changes nothing observable. Any gate must call predicate directly, not through call sites.

3. **New quoting helper must live in NEW LEAF MODULE with zero typsphinx imports** — placing it in builder/writer/registry creates cycles. Must join translator/template_engine/pdf as a leaf.

4. **"Zero test edits" discipline cannot hold — exactly two tests must be edited** — `test_out02_escape_target_gate.py:134` and `test_builder.py:598` hard-code `repr()` doubling and will fail when target sites switch to new helper. Edits are expected and required.

---

## Sources

Synthesized from:
- `.planning/research/STACK.md` (2026-08-27)
- `.planning/research/FEATURES.md` (2026-08-27)
- `.planning/research/ARCHITECTURE.md` (2026-08-27)
- `.planning/research/PITFALLS.md` (2026-08-27)

---

*Research synthesis for: typsphinx v0.9.1 "Windows path correctness"*  
*Synthesized: 2026-08-27 by GSD Research Synthesizer*
