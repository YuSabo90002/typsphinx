---
phase: 47
slug: two-layer-output-content-wrapper-split-target-as-path-collis
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-12
---

# Phase 47 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: **authored at plan time** — all 14 PLAN files carry a parseable
`<threat_model>` block. Verification depth: ASVS L1 (grep/reference depth).
Blocking threshold: `workflow.security_block_on: high`.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `conf.py` → builder config | `typst_documents` entries are project-owner-supplied Python. Sphinx does not type-check config values, so a well-meaning typo (wrong shape, wrong type, path-bearing target) crosses here | Tuples of arbitrary Python objects; `entry[0]` docname, `entry[1]` target |
| builder → filesystem (`outdir`) | Every emitted path is joined under `outdir`; a target string decides part of that path. A `..`-bearing, absolute or drive-qualified target would place a write outside the build directory | Output file paths; `.typ` file contents |
| wrapper file → content file | The two-layer split means two independently-computed paths must never resolve to the same physical file, on any filesystem including case-insensitive ones | Physical output paths |
| Sphinx doctree docname → path computation | Docnames are Sphinx-normalized and cannot carry traversal segments, but reach the same path-computation and set operations as targets | Docname strings |
| builder → build log | Diagnostics embed `repr(entry)` from the user's own `conf.py` | Warning/error message text |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-47-01 | Tampering / Elevation of Privilege | `_escapes_outdir()` / `_resolve_target_stem()` outdir containment | high | mitigate | `builder.py:62-103` — three-term predicate (`".." in segments`, `posixpath.isabs`, `_is_drive_qualified`) routed to warn-and-fallback-to-basename. Unit guards `tests/test_builder_output_stem.py:168,184,200`; build-level containment proof `tests/test_out02_escape_target_gate.py` | closed |
| T-47-02 | Tampering | wrapper file physically overwriting a content file | high | mitigate | `_validate_output_path_collisions()` `builder.py:530-...`, invoked at the top of `write()` (`builder.py:742`) so no partial write can precede it. Real-`sphinx-build` subprocess gate asserts zero `.typ` files emitted on collision | closed |
| T-47-03 | Denial of Service (silent content loss) | two `typst_documents` entries resolving to one target | medium | mitigate | Same validator, BLD-02 kind; the raised error names both claimants. Fixture `bld02_duplicate_target_gate` + on-disk sentinel-count assertion | closed |
| T-47-04 | Tampering | case-insensitive filesystem overwrite, unobservable on Linux | high | mitigate | `_collision_key()` `builder.py:525-528` applies `casefold()` with **no `sys.platform` branch**. Observed for real on the Windows and macOS CI lanes — run `31492380799`, all lanes green | closed |
| T-47-05 | Information Disclosure | build-time file generation | low | accept | No network or data-egress surface; output is written only under `outdir`. See R-47-02 | closed |
| T-47-06 | Tampering | wrapper `#include()` / `_template.typ` import path | medium | mitigate | Both computed from the wrapper's resolved directory via `posixpath.relpath` and a segment count, never from a raw docname. Parametrized matrix over wrapper directories incl. the `_template`-named-directory case | closed |
| T-47-07 | Tampering | an undiscovered second path-rejection site | high | mitigate | RESEARCH.md Assumptions-Log A3 closed by exhaustive grep; every rejection routes through the single `_escapes_outdir()` predicate | closed |
| T-47-08 | Elevation of Privilege | drive-qualified target on a POSIX runner | medium | mitigate | `_is_drive_qualified()` `builder.py:27-56` is a string-shape test asserted on every platform. Executed and passed on the Windows lane (see Audit Note 1) | closed |
| T-47-09 | Tampering (test-integrity) | a laundered gate — an expected value quietly changed to match new output | high | mitigate | Every fixture-corpus plan (47-04..47-08) carries an acceptance criterion asserting `git diff` shows no marker/count/page-index/label/template-parameter change and no golden-file regeneration; each SUMMARY records an explicit zero count | closed |
| T-47-10 | Spoofing | a cross-document label following the wrapper name instead of the source docname | high | mitigate | `get_target_uri()` `builder.py:655-670` stays docname-based; `translator.py::_namespace_label` untouched. Label expectations forbidden from being rewritten | closed |
| T-47-11 | Spoofing | a wrapper rendering another entry's title via docname first-match | medium | mitigate | `tests/test_document_metadata_render_gate.py:169` — repeated-docname fixture whose two wrappers must carry different titles (D-08 end-to-end proof) | closed |
| T-47-12 | Denial of Service | non-`str` docname reaching path computation, raising a raw `TypeError` | medium | mitigate | BLD-01 guard re-verified against the rewritten path computation; `builder.py:1424-1426` reports rather than raises | closed |
| T-47-13 | Repudiation | a published documentation claim silently falsified by OUT-01 | medium | **transfer** | The plan's conditional strict-xfail did not trigger — no test module asserts the claim text (confirmed by `grep -rln` across `tests/*.py`). Instead the falsified claim in `docs/source/user_guide/configuration.rst:49-50` is recorded verbatim in `47-08-SUMMARY.md:212` as an explicit inheritance note, and DOC-14 / Phase 51 owns the rewrite (`REQUIREMENTS.md:94`, `ROADMAP.md:760`, `STATE.md:57`). Accepted as a transfer — see R-47-01 | closed |
| T-47-14 | Tampering | reserved `_template.typ` infrastructure file overwritten by a master's target | high | mitigate | `builder.py:599` — the reserved name is the FIRST key inserted into the collision map, so any later claimant is reported | closed |
| T-47-15 | Denial of Service | a malformed entry crashing the validator before `finish()` can report it | medium | mitigate | `builder.py:614-625` — skip-don't-index tolerance preserved, with a once-per-build warning naming the entry index | closed |
| T-47-16 | Repudiation | CI success criterion asserted from memory rather than measured | medium | mitigate | `47-CI-EVIDENCE.md` records run ids (`31491228938`, `31492380799`), commit SHAs, per-lane conclusions and quoted log lines verbatim | closed |
| T-47-17 | Elevation of Privilege | an unreviewed workflow change riding along with the push | low | accept | Plan 47-10 changed no file under `.github/`; the two triage fixes were confined to `typsphinx/` and `tests/` and are recorded with SHA `be4c4d5`. See R-47-03 | closed |
| T-47-11-01 | Tampering | `_collision_key()` normalization vs. the `_escapes_outdir()` containment guard | medium | mitigate | Separation (key is a `dict` key only, no write site consumes it), monotonicity (`normpath` is many-to-one, collisions can only grow), and measured non-collapse (`posixpath.normpath("../x.typ") == "../x.typ"`). Pinned by `test_collision_key_does_not_collapse_leading_parent_traversal`; `_resolve_target_stem`/`_escapes_outdir`/`_is_drive_qualified` asserted byte-identical | closed |
| T-47-11-02 | Tampering | `typst_documents` target → `_write_typst_files()` / `write()` D-07 report | high | mitigate | A `./`-prefixed duplicate, `./_template.typ`, or a 1-element entry can no longer destroy already-written data with an exit-0 build: shape-equivalent claims now collide and refuse before any write, and an unusable entry produces no wrapper write. Three real-`sphinx-build` subprocess gates assert on on-disk content, never on exit code | closed |
| T-47-11-03 | Information Disclosure | validator warning embedding `repr(entry)` | low | accept | The repr originates in the user's own `conf.py` and is already echoed by `finish()`'s existing aggregate message. Build logs are not a trust boundary in this tool. See R-47-04 | closed |
| T-47-11-04 | Tampering | `posixpath.normpath()` vs. symlinked directories inside `outdir` | low | accept | Not reachable from a target (`_escapes_outdir` refuses `..` before a key is computed) nor from a docname (Sphinx normalizes docnames). `Path.resolve()` deliberately not added — it would put filesystem I/O and TOCTOU exposure inside a pure comparison function. See R-47-05 | closed |
| T-47-12-01 | Tampering | `writer.py::_entry_element_value()` guard perturbation | medium | mitigate | The sibling-resolver deletion changed the survivor's DOCSTRING only, never its body; the non-`str`-warns-then-falls-back assertion is among the nine retargeted tests; `tests/test_entry_metadata_route_uniformity.py` and `tests/test_multi_master_metadata_no_leak.py` pass unmodified | closed |
| T-47-12-02 | Repudiation | `.planning/REQUIREMENTS.md` checkbox state | medium | mitigate | The six flipping IDs enumerated in the action; BLD-02/BLD-03 pinned unchecked by explicit acceptance criterion; diff-shape criterion proves no requirement text reworded | closed |
| T-47-12-03 | Information Disclosure | none | low | accept | No output, log line or error message added, removed or reshaped; no new data path. See R-47-06 | closed |
| T-47-13-01 | Tampering | `master_included_docnames` → `translator.py:3073-3075` → emitted `link(<label>)` | high | mitigate | The include-set filter routes through `_is_usable_typst_documents_entry()` (`builder.py:308`), so an entry producing no wrapper contributes no docnames. Proven end-to-end on BOTH builders by FIXTURE D, asserting on emitted content and on artifacts rather than exit code | closed |
| T-47-13-02 | Denial of Service | `_compute_master_included_docnames()` BFS `set` operations | medium | mitigate | The predicate's `isinstance(entry[0], str)` term (`builder.py:164`) runs before any value reaches a `set` operation, making them total. FIXTURE E on both builders + a direct unit test | closed |
| T-47-13-03 | Information Disclosure | existing `produces no wrapper file` warning embedding `repr(entry)` | low | accept | Same rationale as T-47-11-03; no new message and no wording change. See R-47-04 | closed |
| T-47-13-04 | Tampering | the predicate's own behaviour changed under cover of a docstring edit | medium | mitigate | Acceptance criterion asserts the four documented input/output pairs at the Python level; diff-scope criterion pins the `return` expression byte-identical; three gate modules covering the four pre-existing consumers pass with source unmodified | closed |
| T-47-14-01 | Tampering | unit-level coverage of the OUT-02 containment guard deleted with the dead module | high | mitigate | All three escape-shape tests were RETARGETED, not deleted — `tests/test_builder_output_stem.py:168` (parent traversal), `:184` (absolute), `:200` (drive-qualified), with their `"manual"` expected values unchanged. `tests/test_out02_escape_target_gate.py` passes with `git diff --stat` empty | closed |
| T-47-14-02 | Tampering | the retargeted assertions themselves (gate laundering) | medium | mitigate | Every `(docname, target) -> expected` triple enumerated in the plan so the executor copies from the plan, not from a test run; two distinctive expected values (`"v1.2-manual"`, the non-ASCII stem) spot-checked for verbatim survival; each of the three deletions named with its reason | closed |
| T-47-14-03 | Repudiation | `.planning/REQUIREMENTS.md` checkbox state | medium | mitigate | Exactly one ID flips and it is named; BLD-03 pinned unchecked by its own acceptance criterion; diff-shape criterion plus exact `--numstat` line count prove no text reworded and no second row moved | closed |
| T-47-14-04 | Information Disclosure | none | low | accept | Plan removes code and edits prose; no output, log line, error message or data path added. See R-47-06 | closed |
| T-47-SC | Tampering (supply chain) | npm/pip/cargo installs | low | accept | Zero new packages this phase (binding constraint #7). `47-RESEARCH.md` Package Legitimacy Audit records "Not applicable"; no plan contains a package-manager install task; the `@preview` package count stays at four with no new version-lockstep site. Restated per-plan as `T-47-{11,12,13,14}-SC`. See R-47-07 | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above `workflow.security_block_on` count toward `threats_open`*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-47-01 | T-47-13 | The published claim at `docs/source/user_guide/configuration.rst:49-50` ("A path component is not supported") is falsified by OUT-01 and no test asserts it. Rather than deleting the record, the falsified text is captured verbatim in `47-08-SUMMARY.md:212` and the rewrite is transferred to DOC-14 / Phase 51, which is tracked open in `REQUIREMENTS.md:94` and `STATE.md:57`. Residual: users reading current docs may believe path-bearing targets are rejected when they are now supported — a documentation-accuracy defect, not a code-execution or containment defect | Yu-Sabo (project owner) | 2026-08-12 |
| R-47-02 | T-47-05 | Build-time file generation has no network or data-egress surface; every write lands under `outdir`, which T-47-01/T-47-14 enforce | Phase 47 planning (all 14 PLAN threat models) | 2026-08-12 |
| R-47-03 | T-47-17 | Plan 47-10 changed no file under `.github/`; the two CI-triage fixes are confined to `typsphinx/` and `tests/` and recorded with SHA `be4c4d5` | Phase 47 planning (47-10-PLAN.md) | 2026-08-12 |
| R-47-04 | T-47-11-03, T-47-13-03 | Warnings embed `repr(entry)` sourced from the user's own `conf.py`, already echoed verbatim by `finish()`'s pre-existing aggregate message. Build logs are not a trust boundary in this tool; no new disclosure surface | Phase 47 planning (47-11, 47-13 PLAN threat models) | 2026-08-12 |
| R-47-05 | T-47-11-04 | `normpath` collapses `a/../b` textually, which would not track a symlinked `a`. Unreachable from a target or a docname. `Path.resolve()` deliberately not adopted — filesystem I/O and TOCTOU exposure inside a pure comparison function is a worse trade. Recorded as a flagged assumption under 47-11's BLD-02 `unclassified` edge | Phase 47 planning (47-11-PLAN.md) | 2026-08-12 |
| R-47-06 | T-47-12-03, T-47-14-04 | Plans 47-12 and 47-14 add no output, log line, error message or data path; there is nothing new to disclose | Phase 47 planning (47-12, 47-14 PLAN threat models) | 2026-08-12 |
| R-47-07 | T-47-SC (and `T-47-{11,12,13,14}-SC`) | Zero dependencies added. Binding constraint #7 holds: no new runtime dependency, `@preview` package count stays at four, no new version-lockstep site. The package-legitimacy gate has nothing to audit, so no `[ASSUMED]`/`[SUS]` human checkpoint is owed | Phase 47 planning (all PLAN threat models) | 2026-08-12 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-12 | 33 | 33 | 0 | /gsd-secure-phase (ASVS L1, orchestrator-verified) |

### Audit Note 1 — a real defect found and fixed by this phase's CI gate

The phase's cross-platform CI plan (47-10) is what turned T-47-01 / T-47-08 from a
paper mitigation into a measured one, and it caught a genuine escape-guard defect:

- Run `31491228938` (over `6f8a23c`) **failed** on both `windows-latest` lanes.
- Cause: `_escapes_outdir()` and `_resolve_target_stem()`'s fallback-basename computation
  called OS-native `from os import path` (`ntpath` on a Windows runner), contradicting their
  own docstrings' platform-independence contract (D-05).
  - `ntpath.isabs("/abs/manual")` is `False` where `posixpath.isabs(...)` is `True` — a
    POSIX-shaped absolute target passed through **unrefused** on Windows.
  - `ntpath.basename("//escape")` returns `''` where `posixpath.basename(...)` returns
    `'escape'` — producing an empty fallback basename that mis-routed into the empty-target
    branch and collided with the docname's own content file.
- Fix: both call sites switched to `posixpath.isabs` / `posixpath.basename` (commit `be4c4d5`).
  No other `path.*` call site touched — every other use is genuine OS-native filesystem I/O.
- Re-verified: run `31492380799` (over `be4c4d5`) — `conclusion: success`, all lanes green.

Full evidence in `47-CI-EVIDENCE.md`.

### Audit Note 2 — verification depth

This audit ran at ASVS L1 (grep/reference depth) per `workflow.security_asvs_level: 1`.
Every `mitigate` disposition was confirmed present at a named file:line or a named test
module; no L2 boundary-placement or L3 end-to-end trace analysis was performed. Raising
`workflow.security_asvs_level` to 2 or 3 and re-running would spawn `gsd-security-auditor`
for deeper verification of this same register.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-12
