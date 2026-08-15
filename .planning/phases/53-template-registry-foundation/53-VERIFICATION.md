---
phase: 53-template-registry-foundation
verified: 2026-08-15T12:00:00Z
status: gaps_found
score: 4/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 4/5
  gaps_closed:
    - "SC#3 — Every malformed registry stops the build with a message naming the specific reason, and CONF-14/15/16/17 each fire once per build and order-independently. `TypstBuilder._validate_registry_key_references()` now runs in `write()` between `resolve_template_registry()` and `prepare_writing()`, closing the order-dependent partial-write gap for CONF-14. Live-reproduced in both master orders: zero `.typ` files survive, byte-identical `ExtensionError` message."
  gaps_remaining: []
  regressions: []
gaps:
  - truth: "SC#5 — The milestone branch is on origin with a completed 3-OS CI run covering the code actually shipping in this phase."
    status: failed
    reason: "origin/gsd/v0.9.0-per-document-templates is at 48c957cd (confirmed via `git ls-remote --heads origin`), 17 commits behind local HEAD 8f638768. The only recorded green CI run (31875707734, head d1eff100) predates three production commits that landed afterward via the 53-06/53-07 gap-closure waves: c9d1eb3b (feat, adds `_validate_registry_key_references()` to builder.py), 8d45e0b5 (fix, adds a Windows-specific `except ValueError` cross-drive guard to `_violates_conf17()` in template_registry.py), and eb69904f (fix, adds non-str-key/non-dict-definition guards to template_registry.py). `git merge-base --is-ancestor d1eff100 8f638768` confirms d1eff100 is an ancestor, and `git log d1eff100..8f638768 -- typsphinx/` lists exactly those three commits with no CI run over any of them. 8d45e0b5 in particular is a Windows-drive-path handler -- precisely the class of change the `windows-latest` CI lane exists to exercise -- and it has never run there. SC#5's evidence (`53-CI-EVIDENCE.md`) is stale relative to the code it is meant to certify."
    artifacts:
      - path: ".planning/phases/53-template-registry-foundation/53-CI-EVIDENCE.md"
        issue: "Records only Run 1 (failed, unrelated pre-existing defect) and Run 2 (success) at head d1eff100 -- three production commits later, no new CI evidence exists."
    missing:
      - "Push the current branch tip (or the tip after any further phase-53 commits) to origin: `git push origin gsd/v0.9.0-per-document-templates`."
      - "Dispatch CI over the new tip: `gh workflow run CI --ref gsd/v0.9.0-per-document-templates` (push alone triggers no CI per `.github/workflows/ci.yml:3-8`'s main/develop-only push/pull_request scoping)."
      - "Poll to completion (`gh run list --branch gsd/v0.9.0-per-document-templates --limit 5`) and capture `gh run view <run-id> --json jobs`, confirming both `windows-latest` `test` legs and both `macos-latest` `test` legs conclude `success`."
      - "Record the new run's evidence (append to `53-CI-EVIDENCE.md` or a new dated section) naming the head SHA it covers."
deferred: []
---

# Phase 53: Template Registry Foundation Verification Report

**Phase Goal:** `typst_document_templates` exists as a validated, resolved-once-per-build data
structure, and `render_wrapper()` builds its `TemplateEngine` from the resolved definition
instead of reading `typst_template` / `typst_package` / `typst_template_function` straight off
`config` — but the built-in `"typst"` key synthesizes exactly those same global values, so this
phase changes no output.
**Verified:** 2026-08-15T12:00:00Z
**Status:** gaps_found
**Re-verification:** Yes — after gap closure (plans 53-06, 53-07)

## Goal Achievement

### Observable Truths

| # | Truth (ROADMAP Success Criterion) | Status | Evidence |
|---|---|---|---|
| 1 | **SC#1** — Named template definitions are declarable and resolve once per build (TPL-01, TPL-05); params-exclusivity intact | ✓ VERIFIED | Re-measured live at HEAD 8f638768: two `typst_documents` entries naming the same registered key resolve to the identical `TemplateRegistryEntry` object (`r1 is r2 → True`). `resolve_template_registry()`/`resolve_registry_key()` unchanged in this area by 53-06/53-07 (both plans touch only validation guards, not the resolution/identity logic). `tests/test_template_registry.py` — 67 passed (57 baseline + 10 from 53-07). |
| 2 | **SC#2** — Untouched `conf.py` produces byte-identical output, proven by identity (TPL-03, TPL-04) | ✓ VERIFIED | `tests/fixtures/conf14_prewrite_control_gate` (a four-element entry, an explicit `typst` fifth element, an unusable one-element entry, a declared-but-unreferenced registry key) re-built live: exit 0, exactly the six expected `.typ` files (`_template.typ`, `four.typ`, `four_out.typ`, `five.typ`, `five_out.typ`, `index.typ`), matching `53-06-SUMMARY.md`'s claim. Full suite green (1252 passed, 5 skipped, 0 failed) confirms no output-shape regression from either gap-closure plan. |
| 3 | **SC#3** — Every malformed registry stops the build with a message naming the specific reason; CONF-14/15/16/17 each fire once per build, order-independently, before any output is written | ✓ VERIFIED (literal ROADMAP enumeration); see caveat below | Gap closed. Live-reproduced both fixture builds (`conf14_prewrite_bad_last_gate`, `conf14_prewrite_bad_first_gate`): both exit non-zero via `write()` → `TypstBuilder._validate_registry_key_references()` → `resolve_registry_key()` raising `ExtensionError` **before** `prepare_writing()` runs, and `find <outdir> -name '*.typ'` is empty for **both** master orders. The two raised messages are byte-identical (`typst_documents entry names registry key 'nope', which is not a registered typst_document_templates key -- registered keys: ['good', 'typst']`). CONF-16 (user-declared `"typst"`) independently re-confirmed live: `ExtensionError` raised with the CONF-16 message. This closes exactly the gap the prior verification recorded (order-dependent partial output for CONF-14). **Caveat:** see the "SC#3 framing-sentence caveat" note below and the two new Anti-Patterns rows — this verdict covers the four literally-enumerated malformed shapes (CONF-14/15/16/17), not the module's entire input surface. |
| 4 | **SC#4** — Registry-key shape validated as single path segment; wrong guard (`_escapes_outdir`/`_is_drive_qualified`) not reused; case-collision routed through `_collision_key()` | ✓ VERIFIED | `_KEY_SHAPE_REJECTION_CASES` still exactly 7 distinct entries (re-measured live). `_has_case_collision()` still imports and calls `TypstBuilder._collision_key()` directly (`template_registry.py:94`). Untouched by 53-06/53-07 (neither plan's `files_modified` includes this validator). |
| 5 | **SC#5** — Milestone branch on `origin` with a completed 3-OS CI run over the code actually shipping | ✗ FAILED | `git ls-remote --heads origin gsd/v0.9.0-per-document-templates` → `48c957cd`, 17 commits behind local HEAD `8f638768`. The only green CI run on record (`31875707734`, head `d1eff100`) predates three production commits that shipped afterward via 53-06/53-07: `c9d1eb3b` (new `_validate_registry_key_references()` call site in `builder.py`), `8d45e0b5` (Windows-specific cross-drive `ValueError` guard in `template_registry.py`), `eb69904f` (non-str-key/non-dict-definition guards in `template_registry.py`). `git merge-base --is-ancestor d1eff100 8f638768` confirms ancestry; `git log d1eff100..8f638768 -- typsphinx/` lists exactly those three commits. None of them has ever run on `windows-latest`/`macos-latest` CI. See Gaps below. |

**Score:** 4/5 truths verified (1 failed)

### SC#3 framing-sentence caveat

ROADMAP SC#3's header sentence ("Every malformed registry stops the build with a message naming
the specific reason") is broader than the four shapes it literally enumerates (CONF-14/15/16/17).
The fresh code review (`53-REVIEW.md`, dated after 53-06/53-07 landed) found and live-reproduced
two further raw-exception crash paths in `resolve_template_registry()` that sit outside that
literal enumeration — the exact same defect class WR-02/WR-03 (this phase's own prior WARNING
rows) just closed, one level "up" (the container) and one level "deeper" (a field inside a
definition):

- **WR-01 (new numbering in `53-REVIEW.md`'s current pass):** a truthy non-`dict`
  `typst_document_templates` (e.g. a `list`, a plausible copy-paste-from-`typst_documents` typo)
  crashes `declared.keys()` with a raw `AttributeError: 'list' object has no attribute 'keys'`.
  Independently reproduced this session: confirmed live, unfixed at HEAD 8f638768
  (`typsphinx/template_registry.py:261-262`).
- **WR-02 (new numbering):** a non-`str` `template` field inside an otherwise well-formed
  definition (e.g. `{"template": ["a", "b"]}`) crashes `os.path.join(srcdir, template)` with a raw
  `TypeError: join() argument must be str, bytes, or os.PathLike object, not 'list'`. Independently
  reproduced this session: confirmed live, unfixed at HEAD 8f638768
  (`typsphinx/template_registry.py:322-340`).

**Judgment:** these two findings leave SC#3 **only partially met against its own framing
sentence**, but they do **not** reopen SC#3 as a scored gap, for the same reason the prior
verification did not score the (now-fixed) cross-drive/non-str-key/non-dict-definition findings as
gaps: they fall outside SC#3's literal four-case enumeration (CONF-14/15/16/17), which is what this
phase's plans were scoped against, and this phase already demonstrated (twice, via 53-06 and
53-07) that the project treats this exact defect class as owner-optional robustness debt rather
than a phase-blocking criterion. Recorded here as two new ⚠️ WARNING Anti-Patterns rows (below) so
the debt is visible and not silently dropped, consistent with how the now-closed WR-02/WR-03/CR-02
findings were carried forward from the previous verification pass into 53-07's plan.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `typsphinx/builder.py` | `_validate_registry_key_references()` + `write()` call site (CONF-14 gap closure) | ✓ VERIFIED (present, substantive, wired) | Defined at line 630, immediately after `_validate_output_path_collisions()`; called from `write()` at line 813, between the `resolve_template_registry()` assignment (line 805) and `prepare_writing()` (line 816). Confirmed by direct read and by live build (zero `.typ` files on a bad-key build). |
| `typsphinx/template_registry.py` | Registry resolver + CONF-14..18 validation + 53-07 robustness guards | ✓ VERIFIED (present, substantive, wired) | `except ValueError: return False` in `_violates_conf17()` (line 164); non-`str` key type guard (line 285-286); non-`dict` definition guard (line 315-320). All three re-confirmed present by grep and by direct read this session. |
| `tests/test_registry_prewrite_validation_gate.py` | CONF-14 pre-write gate coverage (53-06) | ✓ VERIFIED | 10 tests, all passing (re-run this session). |
| `tests/test_template_registry.py` | TPL-01/05, CONF-14..18, 53-07 robustness coverage | ✓ VERIFIED | 67 tests, all passing (re-run this session; 57 baseline + 10 from 53-07). |
| `.planning/phases/53-.../53-06-RED-EVIDENCE.md` | Pre-fix partial-output transcript for SC#3 gap closure | ✓ VERIFIED (exists) | Present on disk, referenced by 53-06-SUMMARY.md. |
| `.planning/phases/53-.../53-CI-EVIDENCE.md` | SC#5 branch-push + CI-run evidence | ⚠️ STALE | Present and internally accurate for the run it records, but that run (head `d1eff100`) does not cover the current HEAD's production changes — see SC#5 gap. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `builder.write()` | `resolve_template_registry()` | `self._document_template_registry = resolve_template_registry(...)` at line ~805 | ✓ WIRED | Confirmed by direct read; unchanged by 53-06/53-07. |
| `builder.write()` | `_validate_registry_key_references()` | Line 813, between the registry assignment and `prepare_writing()` | ✓ WIRED | New in 53-06. Confirmed by direct read and by two live builds proving zero `.typ` output on failure in both master orders. |
| `_write_typst_files()` wrapper loop | `resolve_registry_key()` | Per-entry, deliberately retained as the data-flow lookup feeding `render_wrapper()` | ✓ WIRED | No longer the FIRST place a bad key surfaces (that's now `write()`'s up-front pass), but still load-bearing for tests driving `write_doc()`/`_write_typst_files()` directly. |
| `render_wrapper(template_entry=...)` | `TemplateEngine(...)` | `writer.py:350-386` | ✓ WIRED | `resolved_entry.template` / `.package` / `.template_function` / `.key` feed the engine; `typst_template_mapping` stays scoped to the `"typst"` key only. No direct `getattr(config, "typst_template"/"typst_package"/"typst_template_function")` in this method. |

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| TPL-01 | 53-02, 53-03 | ✓ SATISFIED (code); ⚠️ REQUIREMENTS.md tracking stale | Named definitions accepted, `template` xor `package`, both `template_function` forms — live-confirmed shared-key identity this session. **REQUIREMENTS.md's traceability table still lists TPL-01 as `Pending`** despite `53-03-SUMMARY.md`'s `requirements-completed: [TPL-01, TPL-05, CONF-14, CONF-15, CONF-16, CONF-17, CONF-18]`. Documentation-tracking gap, not a functional one — see Anti-Patterns. |
| TPL-03 | 53-01, 53-02, 53-04, 53-05 | ✓ SATISFIED | REQUIREMENTS.md shows `Complete`. Built-in `"typst"` synthesizes global config verbatim; SC#2 byte-identity re-confirmed this session via the control fixture. |
| TPL-04 | 53-01, 53-02, 53-05, 53-06 | ✓ SATISFIED | REQUIREMENTS.md shows `Complete`. Absent element [4] == explicit `"typst"`, re-confirmed via the control fixture's four/five-element entries. |
| TPL-05 | 53-02, 53-03 | ✓ SATISFIED (code); ⚠️ REQUIREMENTS.md tracking stale | Shared key resolves to one object, live-confirmed this session. **REQUIREMENTS.md still lists TPL-05 as `Pending`** — same tracking gap as TPL-01. |
| CONF-14 | 53-03, 53-06 | ✓ SATISFIED | REQUIREMENTS.md shows `Complete`. Now fires once-per-build, order-independently, zero partial output — the gap this re-verification closes. |
| CONF-15 | 53-03, 53-07 | ✓ SATISFIED | REQUIREMENTS.md shows `Complete`. `template`+`package` both-set rejected up front. |
| CONF-16 | 53-03 | ✓ SATISFIED (code); ⚠️ REQUIREMENTS.md tracking stale | User-declared `"typst"` rejected up front, re-confirmed live this session. **REQUIREMENTS.md still lists CONF-16 as `Pending`** — same tracking gap. |
| CONF-17 | 53-03, 53-07 | ✓ SATISFIED | REQUIREMENTS.md shows `Complete`. Parent-is-srcdir/ancestor rejected; cross-drive `ValueError` now caught and returns `False` (legal, D-07) instead of crashing. |
| CONF-18 | 53-03, 53-07 | ✓ SATISFIED | REQUIREMENTS.md shows `Complete`. Exactly 7 denylist cases; case-collision via `_collision_key()`; non-`str` key excluded from that comparison and reported separately. |

No orphaned requirements — all 9 IDs ROADMAP maps to Phase 53 appear in at least one plan's
`requirements` field.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `typsphinx/template_registry.py` | 101-134 (`_validate_registry_key_shape`) | A bare Windows drive-qualified key (e.g. `"C:"`) is accepted, unrejected | ℹ️ INFO — NOT a gap | Unchanged from prior verification. Deliberately out of scope: `53-CONTEXT.md`'s "Deferred Ideas" locks `< > : " \| ? *` as accepted in Phase 53 by design (`53-REVIEW.md` CR-01). |
| `typsphinx/template_registry.py` | 261-262 (`resolve_template_registry`) | A truthy non-`dict` `typst_document_templates` config value (e.g. a `list`) crashes `declared.keys()` with a raw `AttributeError` instead of this module's own `ExtensionError` contract | ⚠️ WARNING (new) | Live-reproduced this session (unfixed at HEAD). Same defect class as the now-closed WR-02/WR-03; found by the fresh `53-REVIEW.md` review one container level "up". Plausible authoring mistake (copy-pasting a `typst_documents`-shaped list). Not one of SC#3's four literally-enumerated cases — see SC#3 caveat above. |
| `typsphinx/template_registry.py` | 322-340 (`resolve_template_registry`) | A non-`str` `template` field inside an otherwise well-formed definition crashes `os.path.join()` with a raw `TypeError` instead of this module's own `ExtensionError` contract | ⚠️ WARNING (new) | Live-reproduced this session (unfixed at HEAD). Same defect class one field "deeper" than the now-closed WR-02/WR-03. Not one of SC#3's four literally-enumerated cases — see SC#3 caveat above. |
| `typsphinx/template_registry.py` | 323 (`package` field) | The `package` field is never type-validated; a non-`str` value silently f-string-interpolates into `#import "{value}"`, producing syntactically valid but semantically nonsensical Typst | ℹ️ INFO — NOT a gap | Mirrors pre-existing (out-of-scope) global `typst_package` behavior; recorded in `53-REVIEW.md` IN-01, not reproduced independently this session (low-severity, cosmetic-failure-mode finding). |
| `.planning/REQUIREMENTS.md` | 155, 159, 162 | TPL-01, TPL-05, CONF-16 remain marked `Pending` in the traceability table despite `53-03-SUMMARY.md` listing all three in `requirements-completed` and this session's live re-confirmation that all three are functionally satisfied | ⚠️ WARNING | Documentation/tracking gap only — not a code defect. Does not block phase-goal achievement (the code is verified correct) but should be corrected before milestone close so REQUIREMENTS.md accurately reflects delivered scope. |

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers found in any file modified by this
phase (re-scanned `builder.py`, `template_registry.py`, `writer.py`, `template_engine.py` this
session).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full test suite | `uv run pytest tests/ -q` | `1252 passed, 5 skipped in 111.89s` | ✓ PASS |
| `black --check .` | `uv run black --check .` | `308 files would be left unchanged` | ✓ PASS |
| `ruff check .` | `uv run ruff check .` | `All checks passed!` | ✓ PASS |
| `mypy typsphinx/` | `uv run mypy typsphinx/` | `Success: no issues found in 7 source files` | ✓ PASS |
| CONF-14 violation (bad master sorts LAST) | live 2-master build, `alpha` good / `beta` bad key | Non-zero exit; `find <outdir> -name '*.typ'` → empty | ✓ PASS (gap closed) |
| CONF-14 violation (bad master sorts FIRST) | live 2-master build, `aaa_bad` bad key / `zzz_good` good | Non-zero exit; `find <outdir> -name '*.typ'` → empty | ✓ PASS (gap closed) |
| CONF-14 message identity across both orders | grep `sphinx.errors.ExtensionError` from both tracebacks | Byte-identical message string | ✓ PASS |
| CONF-16 violation (user-declared `"typst"`) | direct `resolve_template_registry()` call | `ExtensionError` raised with CONF-16 message | ✓ PASS |
| SC#2 control fixture (no-op) | live build of `conf14_prewrite_control_gate` | Exit 0; exactly the 6 expected `.typ` files | ✓ PASS |
| TPL-01/05 shared-key resolution | live `resolve_registry_key()` call, 2 entries naming the same key | `r1 is r2 → True` | ✓ PASS |
| SC#4 denylist count | `len(_KEY_SHAPE_REJECTION_CASES)` | `7`, all distinct | ✓ PASS |
| WR-01 (new) reproduction | direct `resolve_template_registry()` call, `typst_document_templates = ["a", "b"]` | Raw `AttributeError: 'list' object has no attribute 'keys'` | ✗ FAIL (confirms unfixed, recorded as Anti-Pattern, not a scored gap) |
| WR-02 (new) reproduction | direct `resolve_template_registry()` call, `template: ["a", "b"]` | Raw `TypeError: join() argument must be str...` | ✗ FAIL (confirms unfixed, recorded as Anti-Pattern, not a scored gap) |
| SC#5 evidence staleness | `git merge-base --is-ancestor d1eff100 8f638768` + `git log d1eff100..8f638768 -- typsphinx/` | Ancestor confirmed; 3 production commits post-date the recorded CI run | ✗ FAIL (SC#5 gap) |
| `git ls-remote --heads origin` | `git ls-remote --heads origin gsd/v0.9.0-per-document-templates` | `48c957cd` (17 commits behind local HEAD `8f638768`) | ✗ FAIL (SC#5 gap) |

### Human Verification Required

None. Every truth was resolvable programmatically (code read + live reproduction), including the
CI/branch evidence for SC#5, which was independently re-measured against `git`/`git ls-remote`
rather than trusted from the artifact.

### Gaps Summary

**Four of five ROADMAP Success Criteria are met on measured, independently re-verified evidence.**
SC#3, the single criterion the prior verification scored `✗ FAILED`, is now closed:
`TypstBuilder._validate_registry_key_references()` runs once, in `write()`, before
`prepare_writing()`, and two live builds (bad master sorting last, bad master sorting first) both
prove zero `.typ` files survive a CONF-14 failure with a byte-identical error message — exactly
what the prior verification's `missing:` items asked for. SC#1, SC#2, and SC#4 remain verified
exactly as before, re-confirmed live rather than carried forward on trust.

**SC#5 is not currently met and is the one blocking gap.** The milestone branch on `origin` is 17
commits behind local HEAD, and the one CI run on record predates three production commits
(`c9d1eb3b`, `8d45e0b5`, `eb69904f`) that shipped via the very gap-closure plans (53-06, 53-07)
this re-verification is checking. One of those three commits is a Windows-drive-path handler that
has never been exercised on the `windows-latest` CI lane it was written for. This is not a code
defect — it is an evidence-currency gap: the fix is to push the current tip and dispatch a fresh
3-OS CI run over it, per the sequence ROADMAP SC#5 itself specifies (`git push origin <branch>` →
`gh workflow run CI --ref <branch>` → poll → capture `gh run view <run-id> --json jobs`).

**SC#3's own framing sentence is not fully true across the module's entire input surface**, but
this is recorded as two new ⚠️ WARNING Anti-Patterns rows, not a reopened gap — consistent with how
this same phase already treated the identical defect class (cross-drive crash, non-str key,
non-dict definition) before 53-07 optionally closed it. The two new findings (non-dict
`typst_document_templates` container, non-str `template` field) sit outside SC#3's literal
four-case enumeration and are owner-optional robustness debt, exactly as their predecessors were.

**REQUIREMENTS.md's traceability table is stale** for TPL-01, TPL-05, and CONF-16 (still `Pending`
despite `53-03-SUMMARY.md` listing them `requirements-completed` and this session's live
re-confirmation that all three are functionally satisfied). Recorded as a documentation anti-
pattern; does not block phase-goal achievement.

---

_Verified: 2026-08-15T12:00:00Z_
_Verifier: Claude (gsd-verifier)_
