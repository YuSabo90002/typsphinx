---
phase: 59-path-shape-predicate-and-image-uri-correctness
verified: 2026-08-28T22:12:57Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 59: Path-Shape Predicate and Image-URI Correctness Verification Report

**Phase Goal:** A Windows-shaped absolute image URI survives the whole pipeline. `_escapes_outdir()`
decides on the normalized string like its sibling `_is_absolute_image_uri()` already does; the
relocation key `_track_image()` builds carries no backslash and cannot exceed a portable filesystem
component limit; and the URI `visit_image()` interpolates is escaped last, after every path-shape
transform, so what reaches Typst is a string it accepts.

**Verified:** 2026-08-28T22:12:57Z
**Status:** passed
**Re-verification:** No — initial verification

All evidence below was independently re-measured against the live tree at tip `df495fdd`
(code tip `924f21d8`, the CR-01 fix commit; `df495fdd` is a docs-only evidence-file update on top of
it) — not read from SUMMARY.md claims alone. Where I quote SUMMARY/evidence-file text, I first
reproduced the underlying command myself.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `_escapes_outdir()` called directly returns `True` for `\manuals\guide` and `\\srv\share\g` (both `False` pre-fix); both production call sites classify all shapes byte-identically before/after | ✓ VERIFIED | `typsphinx/builder.py:220-233` binds one `normalized = stem.replace("\\","/")` and passes it to both the `isabs` and drive-qualified terms (matches `_is_absolute_image_uri()`'s idiom at line 202). Doctest examples at lines 227-232 confirm `True` for both shapes. `tests/test_path_shape_predicate_gate.py` (14 tests, `TestEscapesOutdirDirectCall` for the direct-call RED-turned-green pair, `TestEscapesOutdirCallSiteCharacterization` for the 10-case two-call-site pin) — re-ran locally, `14 passed`. `59-WINDOWS-URI-EVIDENCE.md` § PATH-01 carries the verbatim pre-fix `False` transcript, recorded before the edit. |
| 2 | A real `typst.compile()` accepts a Windows-shaped absolute image URI; RED against the unfixed tree with Typst's own refusal in evidence; green after; both coupled halves proven necessary | ✓ VERIFIED — substantive claim; ⚠️ literal-wording mismatch, see note below | `tests/test_windows_image_uri_render_gate.py::TestWindowsShapedImageUriCompileGate` — re-ran locally: `1 passed, 0 skipped` (real `typst.compile()` via `sphinx-build -b typstpdf`, `TYPST_AVAILABLE` guarded, skip is an in-body `tmp_path` probe never `os.name`). `59-WINDOWS-URI-EVIDENCE.md` § "IMG-07 four-combination table" records four independently reconstructed trees (`git checkout $PHASE_BASE_SHA -- typsphinx/{builder,translator}.py`, restored and `git status --porcelain` confirmed empty after each): unfixed, IMG-04-only, IMG-05-only all fail to compile; only both-fixed compiles to a 29419-byte PDF starting `%PDF`. This proves the substantive claim ("neither half alone would have closed it") independent of which exact Typst error string each row shows. |
| 3 | Relocation key is separator-free and 255-UTF-8-byte-bounded, digest anchor intact, boundary-safe, extension preserved, never empty basename, collision property re-proven | ✓ VERIFIED | `typsphinx/builder.py::_build_relocation_key()` (normalizes basename only, hashes raw `resolved_uri`) + `_bound_relocation_component()` (255-byte bound, `_decode_to_boundary()` UTF-8-safe walk-back). `tests/test_track_image_key_construction.py` — re-ran locally: `12 passed` (includes the two CR-01 regression tests added in the post-review fix). Independently reproduced the multi-byte-stem case myself (`_bound_relocation_component("a1b2c3d4", "図"+"."+"e"*244)` → stem `図` survives, 255 bytes) — see CR-01 section below. |
| 4 | The length bound has its own gate (not a compile gate); fails against unfixed tree with `ENAMETOOLONG` `OSError` at `copy_image_files()` time, passes after | ✓ VERIFIED | `tests/test_copy_image_files_name_too_long.py::TestCopyImageFilesNameTooLong` — re-ran locally: `1 passed`. `59-WINDOWS-URI-EVIDENCE.md` § "IMG-04 / IMG-06" quotes the pre-fix verbatim `Failed to copy image ...: [Errno 36] File name too long` warning (captured via `caplog`, substring-matched because Sphinx's logging filter prepends `"WARNING: "`) and confirms it is absent, with the destination file present, post-fix. |
| 5 | Zero test edits over the phase diff; full matrix (incl. `windows-latest`) green on the phase's own post-fix tip, dispatched fresh | ✓ VERIFIED | Independently re-ran `git diff --name-status ec6bd3a4714a578379ee45e02295abc31fdd8fe3..HEAD -- tests/`: 8 lines, all `A` (added), zero `M`/`D`. `git diff --name-status ... | grep -v tests/,.planning/` shows only `M typsphinx/builder.py` and `M typsphinx/translator.py` as non-test, non-planning changes. CI run `33214830110` (head SHA `924f21d818f32c79d2bcb4e3d2287e8b969c6899`) independently queried via `gh run view --json headSha,conclusion,status`: `conclusion: success`, `status: completed`, `headSha` matches. This is the CODE tip; the current branch tip `df495fdd` is a docs-only commit on top (confirmed via `git show df495fdd --stat`: only `59-WINDOWS-URI-EVIDENCE.md` changed). |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

**Note on SC#2's exact wording vs. its substance (both readings, not collapsed):**

- **(a) Substantive claim — MET.** "Neither [half] alone would have closed it" is proven by the
  four-combination measurement: A (unfixed), B (IMG-04 only), C (IMG-05 only) all fail to compile;
  only D (both) compiles. This is the property the phase goal actually depends on, and it holds.
- **(b) Literal wording — NOT met on the "unfixed" row.** SC#2 as written in `ROADMAP.md:274-278`
  names `path must not contain a backslash` as the refusal recorded for the *unfixed* tree. The
  measured refusal for the unfixed tree is `TypstError: unclosed delimiter` (the raw, unescaped `"`
  in the fixture's basename terminates the Typst string literal before the semantic backslash check
  ever runs). I independently reproduced this: checked out `typsphinx/{builder,translator}.py` at
  `ec6bd3a4` into the current tree, ran `tests/test_windows_image_uri_render_gate.py`, and got the
  same `unclosed delimiter` failure recorded in `59-WINDOWS-URI-EVIDENCE.md`; restored and confirmed
  `git status --porcelain typsphinx/` empty afterward. The exact string `path must not contain a
  backslash` DOES appear in the evidence file, but on combination **C** ("escaping only"), not on
  the unfixed row SC#2 names.
- This was a **locked decision (D-01) falsified by measurement**, correctly handled per this
  project's own established pattern: recorded, marked DIVERGENT, halted for the owner (plan 59-05
  Task 1), owner-approved amendment (`59-CONTEXT.md` `D-01a: AMENDED`, commit `ab7a42ae`,
  independently re-measured by the orchestrator before approval, per the memory note "locked
  decisions can be falsified by research"). **`ROADMAP.md` itself was NOT amended** — line 276 still
  carries the falsified prediction verbatim. This does not block the phase goal (the substantive
  property holds and is well-evidenced), but the ROADMAP text and the CONTEXT.md text now disagree,
  and the owner should decide whether to update `ROADMAP.md:274-278` to match `D-01a` for future
  readers. Flagged here rather than silently resolved.

### CR-01 Post-Review Fix (Code Review Blocker, Closed In-Phase)

`59-REVIEW.md` (2026-08-28T21:38:20Z) found `_bound_relocation_component()` violated its own
documented D-07 "the stem is never emptied" invariant: reserving one **byte** for the stem is not
the same as reserving one **character** — a multi-byte leading stem character (e.g. `図`, 3 bytes)
under a tight budget caused the UTF-8 boundary walk-back to land on `b""`, dropping the whole stem
while the lower-priority extension kept its allotment.

I independently verified this end-to-end, not from the SUMMARY's narration:

1. **Reproduced the pre-fix defect** by checking out `typsphinx/builder.py` at `924f21d8~1` and
   running the two new regression tests: both FAILED (`AssertionError: D-07 violated for the
   multibyte stem: ... assert '' != ''`), confirming the defect was real and the new tests are
   genuinely RED-first, not written against an already-fixed function.
2. **Restored** and confirmed `git status --porcelain typsphinx/` empty.
3. **Confirmed the fix** (commit `924f21d8`) resolves it: `_bound_relocation_component("a1b2c3d4", "図"+"."+"e"*244)` now returns a 255-byte result with `図` intact (ran this myself against the current tree — see truth #3 above).
4. **Confirmed WR-01 addressed**: the diff hoists the duplicated `stem_budget = budget - len(ext_bytes)` formula to a single post-branch computation, with an explicit comment ("Single source of truth for the stem's allotment").
5. **Confirmed IN-01 addressed**: `tests/test_track_image_key_construction.py` gained
   `test_length_bound_multibyte_leading_stem_survives_tight_budget` and
   `test_length_bound_multibyte_stem_kept_when_extension_exceeds_budget`, combining both of CR-01's
   load-bearing conditions (multi-byte leading character + tight `stem_budget`) that no prior test
   combined.

All three review findings (1 critical, 1 warning, 1 info) are closed with reproducible evidence, not
merely asserted closed.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/builder.py :: _escapes_outdir()` | normalize-then-decide | ✓ VERIFIED | Rewritten, doctests pass, matches `_is_absolute_image_uri()` idiom |
| `typsphinx/builder.py :: MAX_PATH_COMPONENT_BYTES`, `_bound_relocation_component()`, `_build_relocation_key()`, `_decode_to_boundary()` | new module-level helpers | ✓ VERIFIED | Present, wired into `_track_image()`'s escape branch at line 1941, exercised by 12 passing tests |
| `typsphinx/translator.py :: visit_image()` | routes `adjusted_uri` through `escape_typst_string()` once | ✓ VERIFIED | `escaped_uri = escape_typst_string(adjusted_uri)` bound once, both `add_text` sites (in-figure, standalone) interpolate it |
| `tests/test_path_shape_predicate_gate.py` | PATH-01 gate | ✓ VERIFIED | 14 tests, all pass |
| `tests/test_track_image_key_construction.py` | IMG-04/IMG-06 gate | ✓ VERIFIED | 12 tests, all pass (incl. 2 CR-01 regressions) |
| `tests/test_copy_image_files_name_too_long.py` | IMG-06 integration gate | ✓ VERIFIED | 1 test, passes |
| `tests/test_image_literal_escaping_gate.py` | IMG-05 gate | ✓ VERIFIED | 1 test, passes |
| `tests/test_windows_image_uri_render_gate.py` + `tests/fixtures/windows_shaped_image_uri_gate/` | IMG-07 gate + fixture | ✓ VERIFIED | 2 tests, both pass (`0 skipped` — TYPST_AVAILABLE satisfied, ext4 probe accepted); fixture files contain no `\` or `"` in their committed names |
| `59-WINDOWS-URI-EVIDENCE.md` | phase evidence spine | ✓ VERIFIED | 1143 lines; RED-then-GREEN transcripts for all 5 requirements, four-combination table, SC#5 measurement, 3-run CI dispatch record |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `_track_image()` escape branch | `_build_relocation_key(resolved_uri)` | direct call at `builder.py:1941` | ✓ WIRED | Single construction site, confirmed by reading the call site |
| `_build_relocation_key()` | `_bound_relocation_component()` | normalize-then-bound | ✓ WIRED | Basename normalized via `basename_source`, digest stays raw `resolved_uri` |
| `_compute_relative_image_path()` return value | `escape_typst_string()` | `escaped_uri = escape_typst_string(adjusted_uri)` | ✓ WIRED | Runs on the return value, not the raw `uri`, confirmed at `translator.py:4746` |
| relocation key | `copy_image_files()` dest write | `path.join(self.outdir, imguri)` | ✓ WIRED | 255-byte bound keeps this write under the ext4/NTFS component limit; integration gate confirms no `ENAMETOOLONG` post-fix |
| fixture `node["uri"]` | `_track_image()` → `visit_image()` → `typst.compile()` | full pipeline | ✓ WIRED | IMG-07 compile gate exercises the whole chain end to end with a real compile |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `_escapes_outdir()` direct-call shapes | `uv run pytest tests/test_path_shape_predicate_gate.py -q` | `14 passed` | ✓ PASS |
| Relocation key normalize + bound | `uv run pytest tests/test_track_image_key_construction.py -q` | `12 passed` | ✓ PASS |
| `copy_image_files()` no longer swallows `ENAMETOOLONG` | `uv run pytest tests/test_copy_image_files_name_too_long.py -q` | `1 passed` | ✓ PASS |
| `visit_image()` escape-last | `uv run pytest tests/test_image_literal_escaping_gate.py -q` | `1 passed` | ✓ PASS |
| Real `typst.compile()` on Windows-shaped URI | `uv run pytest tests/test_windows_image_uri_render_gate.py -q` | `2 passed, 0 skipped` | ✓ PASS |
| CR-01 fix RED-then-GREEN | checkout `924f21d8~1`, run the 2 new regression tests, restore | `2 failed` pre-fix → `2 passed` post-fix | ✓ PASS |
| Full suite | `uv run pytest -q` | `1471 passed, 1 skipped` (the 1 skip is the pre-existing env-gated `TYPSPHINX_CORPUS_REPORT` corpus check, unrelated to this phase) | ✓ PASS |
| Format / types / lint | `uv run black --check .`, `uv run mypy typsphinx/`, `uv run ruff check .` | all clean | ✓ PASS |
| Zero test edits | `git diff --name-status $PHASE_BASE_SHA..HEAD -- tests/` | 8 lines, all `A` | ✓ PASS |
| Product surface confined to `builder.py`/`translator.py` | `git diff --name-status` filtered | only those two `M` lines outside `tests/`/`.planning/` | ✓ PASS |
| CI acceptance run matches phase tip | `gh run view 33214830110 --json headSha,conclusion,status` | `headSha=924f21d8...`, `conclusion=success`, `status=completed` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| PATH-01 | 59-01 | `_escapes_outdir()` normalize-then-decide | ✓ SATISFIED | Code + 14 passing tests + RED-first evidence, see Truth #1 |
| IMG-04 | 59-02 (+59-05) | Relocation key backslash-free | ✓ SATISFIED | Code + tests + RED-first evidence, see Truth #3 |
| IMG-05 | 59-03 (+59-05) | `visit_image()` escape-last | ✓ SATISFIED | Code + 1 passing test + RED-first evidence, see Truth #2/artifacts |
| IMG-06 | 59-02 | 255-byte bound, collision anchor intact | ✓ SATISFIED | Code + 12 passing tests (incl. CR-01 regressions) + RED-first evidence, see Truth #3/#4 |
| IMG-07 | 59-04 (+59-05) | Real `typst.compile()` gate | ✓ SATISFIED | 2 passing tests, 4-combination measurement, see Truth #2 |

**REQUIREMENTS.md is stale for four of these five IDs — flagged explicitly per this verification's
instructions, not silently reconciled.**

`.planning/REQUIREMENTS.md`'s checkbox list (lines 21-72) still shows `[ ]` for **PATH-01, IMG-04,
IMG-05, IMG-07** and only `[x]` for **IMG-06**; its Traceability table (lines 194-201) shows
`Pending` for the same four and `Complete` only for IMG-06. Only one commit in this phase's entire
history (`850fddb2`, plan 59-02's own completion commit) touched `REQUIREMENTS.md` at all — it
correctly flipped IMG-06 (sole owner, no shared-ID gate) and correctly left IMG-04 pending at that
point (59-05 hadn't produced a SUMMARY yet, so the shared-ID gate legitimately held it back). No
subsequent plan (59-01, 59-03, 59-04, or 59-05) updated `REQUIREMENTS.md` at all — not even PATH-01,
which was never shared-ID-gated in the first place (`59-01` is its sole owner) and should have
flipped on 59-01's own completion.

I ran this project's own read-only check independently rather than inferring from the plan
frontmatter:

```
$ node .claude/gsd-core/bin/gsd-tools.cjs requirements ready-ids <59-01-PLAN.md> PATH-01
{"ready": ["PATH-01"], "blocked": [], "total": 1}

$ node .claude/gsd-core/bin/gsd-tools.cjs requirements ready-ids <59-03-PLAN.md> IMG-05
{"ready": ["IMG-05"], "blocked": [], "total": 1}

$ node .claude/gsd-core/bin/gsd-tools.cjs requirements ready-ids <59-05-PLAN.md> IMG-04,IMG-05,IMG-07
{"ready": ["IMG-04", "IMG-05", "IMG-07"], "blocked": [], "total": 3}
```

**Conclusion: all four (PATH-01, IMG-04, IMG-05, IMG-07) are now ready to mark Complete** — every
plan that declares any of them has a SUMMARY, and the codebase evidence above independently confirms
each is actually implemented and gated, not just SUMMARY-claimed. This is a documentation-sync gap,
not a functional gap — the code is correct and tested regardless of what `REQUIREMENTS.md`'s
checkboxes say — so it does not block the phase goal and is not recorded as a `gaps` entry below.
The orchestrator should run `requirements mark-complete` for PATH-01, IMG-04, IMG-05, and IMG-07 (and
update the Traceability table's four `Pending` rows to `Complete`) as part of closing this phase,
before the milestone's "Mapped to phases: 11 / Unmapped: 0" coverage claim can be trusted at face
value against the checkbox state.

### Anti-Patterns Found

None. Scanned every file this phase modified or created
(`typsphinx/builder.py`, `typsphinx/translator.py`, all 5 new test modules, the 2 new fixture files)
for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` and placeholder-language patterns. The one `TODO` hit in
`typsphinx/translator.py:6268` (`"...TODO-01, T-16-01..."`) predates this phase (`git blame` →
2026-07-16, commit `5f3ec4c3c`) and is a formal requirement-ID cross-reference, not a debt marker;
this phase's own diff to `translator.py` is the minimal 6-line change shown in the Key Link table
above and does not touch that line.

### Human Verification Required

None. Every must-have is either directly re-measured (code read, tests re-run, CI run independently
queried via `gh run view`) or covered by a real `typst.compile()` gate that exercises the full
pipeline end to end — there is no runtime/visual/UX property left unverified by automation for this
phase's scope.

### Gaps Summary

No gaps block the phase goal. All five requirements (PATH-01, IMG-04, IMG-05, IMG-06, IMG-07) are
implemented, gated RED-first, and independently re-verified against the live codebase — not merely
asserted by SUMMARY.md. The one post-plan code-review defect (CR-01) was fixed in-phase with a
reproduced pre-fix RED and a confirmed post-fix GREEN, and the fix's own regression tests were
themselves independently re-verified RED-then-GREEN by this verification. CI's acceptance run
(`33214830110`) is green across all 12 jobs including both `windows-latest` jobs, dispatched fresh on
the exact commit (`924f21d8`) that carries the CR-01 fix, with no older run cited as current.

Two non-blocking items are recorded for the owner/orchestrator, not as gaps:

1. **`REQUIREMENTS.md` is stale** for PATH-01, IMG-04, IMG-05, IMG-07 (all four should flip to
   `Complete`/`[x]`, confirmed ready via `requirements ready-ids`) — a documentation-sync action, not
   a code defect.
2. **`ROADMAP.md:274-278` (SC#2) still names the falsified `path must not contain a backslash`
   refusal for the unfixed-tree row.** `59-CONTEXT.md` was amended (`D-01a`) after the divergence was
   measured and owner-approved, but the ROADMAP text itself was not. The phase's substantive claim
   holds regardless (see the SC#2 note above); this is a documentation-consistency item for the
   owner to decide on, not a functional gap.

---

*Verified: 2026-08-28T22:12:57Z*
*Verifier: Claude (gsd-verifier)*
