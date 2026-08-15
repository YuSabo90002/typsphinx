---
phase: 53-template-registry-foundation
verified: 2026-08-15T09:29:03Z
status: gaps_found
score: 4/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "SC#3 — Every malformed registry stops the build with a message naming the specific reason, and CONF-14/15/16/17 each fire once per build and order-independently, following _validate_output_path_collisions()'s 'runs once, at the very top of write()' precedent."
    status: partial
    reason: "CONF-15/16/17/D-08 (declaration-level checks inside resolve_template_registry()) genuinely run once, up front in write(), before any .typ file is written -- reproduced live: a CONF-16 violation ('typst' redeclared) writes ZERO .typ files. CONF-14 (a typst_documents entry naming an unregistered registry key) does NOT get this treatment: resolve_registry_key() is called lazily, per-wrapper, from inside _write_typst_files()'s per-docname loop (builder.py:1121) -- which runs strictly AFTER that docname's own content file, and every earlier-sorted docname's content+wrapper files, have already been written to disk. This is the literal anti-pattern the phase's own ROADMAP goal text names as the thing resolving-once-per-build exists to prevent ('make an ExtensionError for a bad registry entry surface only when the first wrapper naming it happens to be written, so failure would be order-dependent across a multi-master build')."
    artifacts:
      - path: "typsphinx/builder.py"
        issue: "write() (line 737) resolves the registry declarations up front via resolve_template_registry(), but never calls resolve_registry_key() to validate each typst_documents entry's element [4] up front in that same pass. resolve_registry_key() is only reached from _write_typst_files()'s per-entry wrapper loop at line 1121, after that docname's content file (line 1071-1072) has already been written."
      - path: "typsphinx/template_registry.py"
        issue: "resolve_registry_key() (CONF-14/D-06) is a separate function from resolve_template_registry() (CONF-15/16/17/18/D-08) and is never invoked from the once-per-build call site in write()."
    missing:
      - "In write(), immediately after self._document_template_registry = resolve_template_registry(...) and before prepare_writing(), iterate every usable typst_documents entry and call resolve_registry_key(self._document_template_registry, entry) so a bad element [4] raises before any content or wrapper file is written for ANY docname in the build, matching the same up-front treatment CONF-15/16/17/18 already get."
      - "A regression test that drives the real write() path (not resolve_registry_key() called directly against an in-memory registry) with two masters -- one naming a bad registry key -- and asserts ZERO .typ files exist on disk after the ExtensionError, mirroring the existing _validate_output_path_collisions() 'no output file is written when validation fails' test shape."
deferred: []
---

# Phase 53: Template Registry Foundation Verification Report

**Phase Goal:** `typst_document_templates` exists as a validated, resolved-once-per-build data
structure, and `render_wrapper()` builds its `TemplateEngine` from the resolved definition
instead of reading `typst_template` / `typst_package` / `typst_template_function` straight off
`config` — but the built-in `"typst"` key synthesizes exactly those same global values, so this
phase changes no output.
**Verified:** 2026-08-15T09:29:03Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth (ROADMAP Success Criterion) | Status | Evidence |
|---|---|---|---|
| 1 | **SC#1** — Named template definitions are declarable and resolve once per build (TPL-01, TPL-05); params-exclusivity intact | ✓ VERIFIED | Live test: two `typst_documents` entries naming the same key resolve to the identical `TemplateRegistryEntry` object (`r1 is r2 → True`); a user-defined key omitting `template_function` resolves to `None`, not an inherited global (D-10 confirmed, `r1.template_function → None`). `template_engine.py:253-266` D-B/D-D params-presence predicate untouched (module diff-free per `53-03-SUMMARY.md`, confirmed by `grep`). |
| 2 | **SC#2** — Untouched `conf.py` produces byte-identical output, proven by identity (TPL-03, TPL-04) | ✓ VERIFIED | `53-RED-EVIDENCE.md`'s pre/post SHA-256 + PDF-page-count comparison across 4 shapes + TPL-04 equivalence, all "MATCH". Independently spot-checked: re-built `tests/roots/test-basic` (Shape D) live at current HEAD and its `_template.typ`/`index.typ`/`output.typ` SHA-256 hashes are byte-identical to the artifact's recorded post-change values. |
| 3 | **SC#3** — Every malformed registry stops the build with a message naming the specific reason; CONF-14/15/16/17 each fire once per build, order-independently, before any output is written | ✗ FAILED | Live-reproduced: a 2-master build (`alpha` good, `beta` naming a nonexistent registry key) writes `_template.typ`, `alpha.typ`, `alpha_out.typ`, **and `beta.typ`** (the failing master's own content file) to disk before the `ExtensionError` fires. Reversing sort order (bad master sorts first) changes how much partial output survives (`_template.typ` + only the bad master's content) — the amount of partial output is order-dependent, the exact anti-pattern the ROADMAP goal text names. By contrast, a CONF-16 violation (declaration-level) writes **zero** `.typ` files, confirming CONF-15/16/17/18/D-08 genuinely got the up-front treatment CONF-14 did not. See Gaps below. |
| 4 | **SC#4** — Registry-key shape validated as single path segment; wrong guard (`_escapes_outdir`/`_is_drive_qualified`) not reused; case-collision routed through `_collision_key()` | ✓ VERIFIED | `template_registry.py:57-134` — exactly 7 denylist cases (`_KEY_SHAPE_REJECTION_CASES`), matching D-02 verbatim. Live-confirmed accepted shapes stay accepted (`"paper:v2"`, a control char, a leading dot, interior whitespace all return `None`). `_has_case_collision()` (line 79-98) imports and calls `TypstBuilder._collision_key()` directly, not a second folding. Module docstring records why `_escapes_outdir`/`_is_drive_qualified` are not reused. |
| 5 | **SC#5** — Milestone branch on `origin` with a completed 3-OS CI run | ✓ VERIFIED | Independently re-queried GitHub: `git ls-remote --heads origin` shows `gsd/v0.9.0-per-document-templates` present. `gh run view 31875707734` shows `conclusion: success`, `event: workflow_dispatch`, all 12 jobs `success` including both `windows-latest` and both `macos-latest` `test` legs — matches `53-CI-EVIDENCE.md` exactly. |

**Score:** 4/5 truths verified (1 failed)

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `typsphinx/template_registry.py` | Registry resolver: `resolve_template_registry()`, `resolve_registry_key()`, key-shape/CONF-14..18 validation | ✓ VERIFIED (present, substantive, wired) | 389 lines; imported by `builder.py:24-25` and `writer.py`; 57 passing tests in `tests/test_template_registry.py`. |
| `typsphinx/template_engine.py` (`TemplateResolution.path`) | Resolved template's file path recoverable through the single priority walk | ✓ VERIFIED | Widened per 53-04; `resolve_template()` remains the single priority walk (no second lookup added); existing `TestTemplateResolutionProvenance` tests pass unmodified. |
| `typsphinx/writer.py` (`render_wrapper`) | Builds `TemplateEngine` from a resolved `TemplateRegistryEntry`, not raw `config` reads | ✓ VERIFIED | `writer.py:344-386` — `resolved_entry.template` / `.package` / `.template_function` feed the engine; `typst_template_mapping` scoped to the `"typst"` key only (D-11, line 376-377); no direct `getattr(config, "typst_template"/"typst_package"/"typst_template_function")` remains in this method (confirmed by grep). |
| `tests/test_template_registry.py` | Coverage for TPL-01/05, CONF-14..18, D-06/D-08/D-09 | ✓ VERIFIED (57 tests, all passing) | — |
| `.planning/phases/53-.../53-RED-EVIDENCE.md` | SC#2 one-off identity evidence (D-12) | ✓ VERIFIED | Pre/post commit SHAs, per-file SHA-256, PDF page counts for 4 shapes + TPL-04 comparison; spot-checked one shape live (see truth #2). |
| `.planning/phases/53-.../53-CI-EVIDENCE.md` | SC#5 branch-push + CI-run evidence | ✓ VERIFIED | Independently re-queried via `gh`/`git ls-remote`; matches recorded values exactly. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `builder.write()` | `resolve_template_registry()` | `self._document_template_registry = resolve_template_registry(self.config, str(self.srcdir))` at line 737, after `_validate_output_path_collisions()`, before `prepare_writing()` | ✓ WIRED | Confirmed by direct read; matches D-03/D-09 and the goal text's stated insertion point for **declaration-level** validation. |
| `_write_typst_files()` wrapper loop | `resolve_registry_key()` | line 1121, inside the per-`typst_documents`-entry loop, called AFTER this docname's content file is written (line 1071-1072) | ⚠️ WIRED BUT MISPLACED | Data flows correctly (the resolved `TemplateRegistryEntry` reaches `render_wrapper()`), but the validation TIMING violates SC#3 — see gap above. This is a wiring-correctness pass with a validation-ordering failure, not a broken link. |
| `render_wrapper(template_entry=...)` | `TemplateEngine(...)` | `writer.py:380-386` | ✓ WIRED | `template`, `package`, `template_function` sourced from `resolved_entry`, not `config`. |

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| TPL-01 | 53-02, 53-03 | ✓ SATISFIED | Named definitions accepted, `template` xor `package`, both `template_function` forms — `test_template_registry.py`. |
| TPL-03 | 53-01, 53-02, 53-04, 53-05 | ✓ SATISFIED | Built-in `"typst"` synthesizes global config verbatim; SC#2 byte-identity. |
| TPL-04 | 53-01, 53-02, 53-05 | ✓ SATISFIED | Absent element [4] == explicit `"typst"`, live-confirmed. |
| TPL-05 | 53-02, 53-03 | ✓ SATISFIED | Shared key resolves to one object, live-confirmed. |
| CONF-14 | 53-03 | ⚠️ PARTIALLY SATISFIED | Build DOES stop with a message naming registered keys (literal REQUIREMENTS.md text met), but NOT "once per build, order-independently" as ROADMAP SC#3 additionally requires — see gap. |
| CONF-15 | 53-03 | ✓ SATISFIED | Both `template`+`package` rejected, up front, live-confirmed pattern (same code path as CONF-16 test). |
| CONF-16 | 53-03 | ✓ SATISFIED | User-declared `"typst"` rejected up front; live-confirmed ZERO `.typ` files written. |
| CONF-17 | 53-03 | ✓ SATISFIED (core case); see Anti-Patterns for an adjacent robustness gap | Parent-is-srcdir/ancestor rejected; siblings and absolute paths outside srcdir stay legal. |
| CONF-18 | 53-03 | ✓ SATISFIED | Exactly 7 denylist cases; case-collision via `_collision_key()`; live-confirmed. |

No orphaned requirements — all 9 IDs ROADMAP maps to Phase 53 appear in at least one plan's `requirements` field.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `typsphinx/template_registry.py` | 101-134 (`_validate_registry_key_shape`) | A bare Windows drive-qualified key (e.g. `"C:"`) is accepted, unrejected | ℹ️ INFO — NOT a gap | Explicitly, deliberately out of scope: D-02/CONTEXT's "Deferred Ideas" section names `< > : " | ? *` (which includes `:`) as accepted in Phase 53 by design, filed for a later phase. The code-review's CR-01 finding is real but pre-scoped out by the phase's own locked decision. |
| `typsphinx/template_registry.py` | 137-158 (`_violates_conf17`) | `os.path.commonpath()` raises unhandled `ValueError` for cross-drive absolute paths on Windows, instead of the module's own clean `ExtensionError` contract | ⚠️ WARNING | A legal case per D-07 ("absolute paths outside srcdir stay legal") crashes with a raw Python traceback rather than a clean error, on a Windows-only, likely rarely-exercised cross-drive scenario. Not literally one of SC#3's four enumerated malformed shapes (this is a *legal* case crashing, not a malformed one), so not scored as a gap against the phase's stated Success Criteria, but a genuine robustness defect worth a follow-up. |
| `typsphinx/template_registry.py` | 239-247, 266-317 | A non-`str` registry key or a non-`dict` definition value crashes with a raw `AttributeError` (`'int' object has no attribute 'strip'`, `'str' object has no attribute 'get'`) instead of the module's clean `ExtensionError` contract | ⚠️ WARNING | Live-reproduced both. Plausible authoring mistakes (stray int key, forgetting the `{...}` wrapper). Not one of SC#3's four literally-enumerated cases, so not scored as a gap, but undercuts the general "every malformed registry stops the build with a message naming the specific reason" framing sentence. |

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers found in any of the 5 files this phase modified.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full test suite | `uv run pytest tests/ -q` | `1232 passed, 5 skipped in 107.60s` | ✓ PASS |
| CONF-16 violation writes zero `.typ` output | live 1-master build with `typst_document_templates = {"typst": {...}}` | `ExtensionError` raised, `find out -name '*.typ'` → empty | ✓ PASS (confirms up-front declaration validation works) |
| CONF-14 violation (bad master sorts LAST) | live 2-master build, `alpha` good / `beta` bad key | `_template.typ`, `alpha.typ`, `alpha_out.typ`, `beta.typ` written before raise | ✗ FAIL (confirms the SC#3 gap) |
| CONF-14 violation (bad master sorts FIRST) | live 2-master build, `aaa_bad` bad key / `zzz_good` good | `_template.typ`, `aaa_bad.typ` written before raise (different partial set) | ✗ FAIL (confirms order-DEPENDENCE of partial output) |
| SC#2 Shape D byte-identity | live rebuild of `tests/roots/test-basic` at current HEAD | SHA-256 of all 3 `.typ` files match `53-RED-EVIDENCE.md`'s recorded post-change values exactly | ✓ PASS |
| TPL-05 shared-key resolution | live `resolve_registry_key()` call with 2 entries naming the same key | `r1 is r2 → True` | ✓ PASS |
| SC#5 CI run | `gh run view 31875707734 --json jobs` | all 12 jobs `success`, both `windows-latest`/`macos-latest` `test` legs present and `success` | ✓ PASS |

### Human Verification Required

None. Every truth was resolvable programmatically (code read + live reproduction), including the CI/branch evidence for SC#5, which was independently re-queried against the live GitHub API rather than trusted from the artifact.

### Gaps Summary

Four of five ROADMAP Success Criteria are genuinely met, each independently re-measured rather than
taken from SUMMARY claims — including a live byte-for-byte re-verification of one of SC#2's four
shapes and an independent `gh`/`git` re-query for SC#5.

**SC#3 is not fully met.** The phase's own goal text is explicit about *why* resolution must happen
once, up front, in `write()`: "Per-wrapper resolution would repeat the validation work and, worse,
make an `ExtensionError` for a bad registry entry surface only when the first wrapper naming it
happens to be written, so failure would be order-dependent across a multi-master build." This is
exactly what was measured to happen for CONF-14 specifically: `resolve_registry_key()` — the function
that validates a `typst_documents` entry's element [4] against the resolved registry — is never
called from `write()`'s once-per-build pass (which only calls `resolve_template_registry()`, covering
CONF-15/16/17/18/D-08). It is reached only from inside `_write_typst_files()`'s per-docname,
per-entry wrapper loop, strictly after that docname's own content file — and every earlier-sorted
docname's content and wrapper files — have already been written. Two live builds prove this is not
theoretical: the SET of `.typ` files left on disk after a `CONF-14` failure differs depending on
where the offending master falls in `sorted(docnames)` order, which is precisely the "order-dependent
... across a multi-master build" failure mode CONF-15/16/17/18 were correctly hoisted out of.

`53-03-SUMMARY.md`'s and `53-02-SUMMARY.md`'s own module docstrings only claim order-independence for
the *message content* `resolve_registry_key()` produces when called directly against an in-memory
registry (`test_resolve_registry_key_bad_key_fails_identically_regardless_of_master_order`) — that
test never drives the real `write()` path, so the partial-write behavior these two live builds surface
was never observed by the existing test suite. This matches code-review finding WR-01 in
`53-REVIEW.md`, independently reproduced here rather than taken on the review's word.

The fix is narrow — loop over `typst_documents` and call `resolve_registry_key()` once, in `write()`,
in the same pass that already resolves the registry declarations, before `prepare_writing()` — and does
not require touching `template_registry.py`'s validation logic itself, only its call site.

---

_Verified: 2026-08-15T09:29:03Z_
_Verifier: Claude (gsd-verifier)_
