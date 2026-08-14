---
phase: 50-pr-131-image-path-defects
verified: 2026-08-14T21:45:00Z
status: gaps_found
score: 5/7 must-haves verified
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "SC#2's RED-first evidence requirement: 'RED first: a fixture proving today's destination is `../`-prefixed' (ROADMAP.md Phase 50 SC#2, verbatim) was recorded and observed before the IMG-02 fix landed."
    status: failed
    reason: >
      No pytest-recorded, written-first RED exists anywhere in the phase's evidence chain for
      IMG-02's escape/cross-drive branches. Plan 50-01's RED (50-RED-EVIDENCE.md) covers ONLY
      the IMG-01 srcdir-collision scenario (D-08) — it never constructs an absolute URI outside
      doctreedir or exercises a relpath() ValueError. Plan 50-02's own SUMMARY explicitly
      concedes this: coverage item D2 states "no automated test that ran in THIS plan
      constructs an absolute URI outside doctreedir or mocks a relpath() ValueError to exercise
      them directly" and marks it human_judgment:true rather than asserting a test that ran.
      Plan 50-03 then adds unit tests for the escape/cross-drive branches, but only AFTER the
      fix was already implemented, against literal hardcoded expected values (not laundered
      from the fixed code, which is good practice) — but these were never run against the
      unfixed builder and observed to fail. This is a gap between the ROADMAP's own explicit,
      unambiguous SC#2 wording and what the phase's evidence chain actually contains. A prior
      todo (.planning/todos/pending/2026-08-10-track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri.md)
      does record a MANUAL, pre-phase measurement of the `../`-prefixed escape shape (2026-08-10,
      before Phase 50 began), but that is a hand-run measurement noted in a todo file, not a
      "fixture" (ROADMAP's own word) integrated into this phase's RED->GREEN pytest evidence
      chain the way IMG-01's D-08/D-10 gate was.
    artifacts:
      - path: ".planning/phases/50-pr-131-image-path-defects/50-RED-EVIDENCE.md"
        issue: "Covers only the D-08 IMG-01 collision scenario; contains no IMG-02 escape/cross-drive RED transcript."
      - path: "tests/test_builder.py"
        issue: "test_post_process_images_rehome_escape_relocates_with_warning and test_post_process_images_rehome_cross_drive_value_error_relocates (plan 50-03) assert the POST-fix outcome only; neither was ever run and observed to fail against the unfixed builder."
    missing:
      - "A written-first RED for IMG-02, run and observed against the unfixed (pre-50-02) builder, in the same D-08/D-10 style as IMG-01's 50-RED-EVIDENCE.md: a fixture or unit-level reproduction showing a `../`-prefixed destination is computed and/or written, captured verbatim before typsphinx/builder.py's absolute-URI branch was widened."
      - "Either (a) a retroactive RED reconstruction (e.g. checking out the pre-fix builder.py content in isolation and re-running the new unit tests against it, with the failure transcript recorded), or (b) an explicit owner-accepted override recording why the manual 2026-08-10 todo measurement is treated as satisfying binding constraint #4/SC#2 for IMG-02 despite not being a pytest-recorded fixture RED."
deferred: []
human_verification:
  - test: "Decide whether CR-01 (50-REVIEW.md Critical finding) needs a follow-up todo/phase, or is adequately covered by the phase's own pre-existing, disclosed risk acceptance."
    expected: "Owner reviews CR-01 — two DIFFERENT escaping absolute URIs that share a basename from different source directories both compute the same `_typst_converted/<basename>` relocation key (typsphinx/builder.py:938, `path.basename(resolved_uri)` only, discarding directory context that the collision branch at line 951 preserves via the full `rel_uri`) — and either accepts it as already covered by the phase's own T-50-03 threat-model row (severity: low, disposition: accept, with a documented hashed-key alternative) and FA-02's pre-disclosed residual, or files a follow-up fix/todo."
    why_human: "This is a severity/disposition judgment call: the code reviewer marked it Critical while the phase's own threat model marked the same shape 'low, accept' before the review ran. Reaching the escape branch at all requires a third-party extension writing an absolute image URI outside doctreedir (D-06 treats this as anomalous / unreachable through stock Sphinx), and two independent extensions colliding on the same basename from different directories is a further compound-improbable narrowing. Whether that residual risk is acceptable for a library extension is a product/security judgment, not a code-correctness question a verifier can resolve by grep or test."
---

# Phase 50: PR #131 Image Path Defects Verification Report

**Phase Goal:** Fix the two defects the PR #131 review filed against `TypstBuilder._track_image()`
(IMG-01: converted-image/source-image basename collision, silently rendering the wrong picture;
IMG-02: an absolute image URI outside `doctreedir` escaping `outdir`), fixed together in one change.

**Verified:** 2026-08-14T21:45:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A rehomed converted image and a real source image of the same basename no longer destroy each other; both copied, each document renders its own picture, verified from the compiled PDF (SC#1/IMG-01) | ✓ VERIFIED | `tests/test_converted_image_collision_render_gate.py` — 3 passed (independently re-run: `1.58s`, matches 50-BRANCH-EVIDENCE.md §2). PDF-embedded image size SET `{(40,24),(16,64)}` confirmed post-fix vs. single-element `{(16,64)}` pre-fix (50-RED-EVIDENCE.md, verbatim `--runxfail` transcript). |
| 2 | SC#1's pre-fix RED was written first and is a structural/embedded-image assertion, not "does not compile" (binding constraint #4) | ✓ VERIFIED | 50-RED-EVIDENCE.md: `git diff --stat -- typsphinx/builder.py` empty at measurement time; `--runxfail` shows `2 failed, 1 passed`, both genuine `AssertionError`s (structural `.typ` string assertion + `pypdf` embedded-size-SET assertion), never a "does not compile" failure — the control test explicitly proves the build exits 0 pre-fix. |
| 3 | An absolute image URI outside `doctreedir` never escapes the output directory; `copy_image_files()` writes every destination under `outdir` and never collapses `src==dest`, for a `../`-prefixed relpath result (SC#2/IMG-02, functional claim) | ✓ VERIFIED | `typsphinx/builder.py:910-960` (`_track_image()`): escape branch relocates under `RESERVED_IMAGE_NAMESPACE` before any destination is computed; `test_post_process_images_rehome_escape_relocates_with_warning`, `test_post_process_images_rehome_cross_drive_value_error_relocates`, `test_copy_image_files_relocated_key_destination_stays_under_outdir` all pass (independently re-run, part of the 30/30 passing set below), the last asserting the resolved destination's common path with `outdir` is `outdir` itself. |
| 4 | SC#2's RED-first evidence requirement is met: "RED first: a fixture proving today's destination is `../`-prefixed" (ROADMAP.md verbatim) | ✗ FAILED | No such fixture/pytest RED exists anywhere in the phase's artifacts. 50-RED-EVIDENCE.md covers only IMG-01. 50-02-SUMMARY.md's own coverage item D2 admits "no automated test that ran in THIS plan constructs an absolute URI outside doctreedir or mocks a relpath() ValueError," marking `human_judgment: true`. Plan 50-03's escape/cross-drive unit tests were authored and passed only AFTER the fix existed — never run against unfixed code. See Gaps below. |
| 5 | No collateral change to ordinary image handling; images copied to byte-identical destinations across the change, measured by a two-build comparison over `docs/source` and every root under `tests/roots` (SC#3) | ✓ VERIFIED (with disclosed caveat) | `50-D11-BEFORE-MANIFEST.txt`/`50-D11-AFTER-MANIFEST.txt` are byte-identical (independently re-diffed: empty, 18 lines each). **Caveat, independently confirmed:** `docs/source` and `tests/roots/test-basic` (the only root) contain **zero** image assets (`find` returns 0 files in both) — the two-build manifest itself carries no image-destination entries at all, so it is a structural (non-image `.typ` output) proof, not literally an image-destination proof, exactly as 50-D11-EVIDENCE.md and 50-BRANCH-EVIDENCE.md §3d already disclose. The substantive claim is instead carried by (a) the ordinary-branch code being byte-identical in the diff (`typsphinx/builder.py`'s two-line non-absolute branch, confirmed unchanged), and (b) pre-existing, unedited unit tests `test_copy_image_files_copies_images_to_output` and `test_copy_image_files_preserves_directory_structure` (tests/test_builder.py, both pass), which do assert exact destination paths for ordinary images. Combined evidence supports SC#3; the specifically-named "two-build comparison" mechanism alone does not, and this was honestly disclosed by the executors rather than papered over. |
| 6 | PR #131's own Issue #130 regression tests still pass unchanged (SC#3) | ✓ VERIFIED | `git diff 2ccbbd3a -- tests/test_absolute_image_render_gate.py tests/fixtures/absolute_image_render_gate` → empty (independently re-run). `git diff 2ccbbd3a -- tests/test_builder.py` → 187 insertions, 0 deletions (`grep -c '^-[^-]'` → 0). All 3 D-12-pinned assertions pass (independently re-run: 30/30 passed across the three render-gate/unit files). |
| 7 | No debt markers (TBD/FIXME/XXX/TODO/HACK/placeholder) left in the production or test code this phase touched | ✓ VERIFIED | `grep -nE "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER"` over `typsphinx/builder.py`, `tests/test_builder.py`, `tests/test_converted_image_collision_render_gate.py` → no matches. |

**Score:** 5/7 truths verified, 1 failed (gap), 1 verified-with-disclosed-caveat (counted as verified — substantive evidence exists, just not through the literally-named mechanism).

### Judgment Calls (orchestrator-requested independent read)

**1. Does SC#3's two-build comparison have image-destination evidence, or is it carried entirely by the D-12-pinned render gates?**

Independently confirmed: it is carried by the D-12-pinned render gates plus the ordinary-branch's
byte-identical diff plus two pre-existing unit tests, **not** by the two-build manifest itself. `find
docs/source -iname "*.png" -o -iname "*.svg" -o ...` returns 0 files; `tests/roots/` contains exactly
one root (`test-basic`), which likewise carries no image references. The D-11 manifest (18 lines,
each build) is therefore a purely structural (`.typ`-content-only) comparison with zero image
destinations in it — the executors' own 50-D11-EVIDENCE.md Finding 1 and 50-BRANCH-EVIDENCE.md §3d
already say this plainly, and this verification independently reproduces the same `find` result. This
is not a laundered claim: the phase's evidence explicitly names the limitation rather than hiding it,
and the underlying truth is otherwise supported (see Truth #5 above). Recorded as a disclosed caveat,
not a gap.

**2. Was an IMG-02 pre-fix RED ever recorded, or was that criterion met a different way?**

Independently confirmed: **no IMG-02 RED was ever recorded.** Plan 50-01's RED-EVIDENCE.md is
IMG-01-only. Plan 50-02 implemented both defects' fixes in one tracer task without a preceding failing
test for IMG-02, and its own SUMMARY.md explicitly flags this (coverage item D2, `human_judgment:
true`, "no automated test that ran in THIS plan constructs an absolute URI outside doctreedir"). Plan
50-03's four new unit tests (including the two IMG-02 branch tests) were authored with hardcoded
expected literals — a good anti-laundering discipline — but were written and run only against the
already-fixed builder; they were never observed failing pre-fix. This directly contradicts SC#2's own
verbatim ROADMAP wording: "RED first: a fixture proving today's destination is `../`-prefixed." **This
is recorded as a genuine gap below, per the orchestrator's own instruction not to paper over it.**

**3. Does CR-01 undermine SC#2 or the phase goal's "silent wrong output is gone" thesis?**

Independently read `typsphinx/builder.py:910-960` and confirmed CR-01's mechanics are accurate: the
escape branch's key (`RESERVED_IMAGE_NAMESPACE/{path.basename(resolved_uri)}`, line 938) discards
directory context that the collision branch's key (`RESERVED_IMAGE_NAMESPACE/{rel_uri}`, line 951)
preserves. Two different absolute URIs outside `doctreedir` sharing a basename from different
directories would collide onto the same relocated key, and only the first-tracked one's bytes get
copied — the same "wrong picture, no diagnostic beyond a misleading pair of individually-successful-
looking warnings" shape IMG-01 itself was.

**Verdict:** this does **not** undermine SC#1 (the phase's primary, literally-filed PR #131 defect —
solidly closed with real end-to-end PDF evidence) and does **not** literally violate SC#2's stated
text ("writes every destination under `outdir`" — CR-01's destinations *are* still under `outdir`; the
failure mode is a same-key collision *between two escaping images*, not an outdir escape). It *does*
weaken the phase's broader "silent wrong output is gone" framing for a narrow, compound-improbable,
already-disclosed corner (FA-02, T-50-03 rated this exact shape "low / accept" with a documented
hashed-key alternative, *before* code review ran). The severity mismatch — reviewer says Critical,
phase's own threat model says low/accept — is a genuine disagreement worth an explicit owner decision,
not something a verifier should resolve unilaterally. Routed to human verification below rather than
treated as a blocking gap, because: (a) it was disclosed proactively in the plan's own artifacts before
the code review ran, (b) reaching it requires a third-party extension writing outside `doctreedir` at
all (D-06: unreachable through stock Sphinx), and (c) a documented remediation path already exists if
the owner wants it closed.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/builder.py` (`_track_image()`, `RESERVED_IMAGE_NAMESPACE`) | Widened absolute-URI branch, escape-check-first/collision-check-second ordering | ✓ VERIFIED | 97 lines added/changed (`git diff --stat` vs. phase base), reviewed directly — matches PLAN's D-01..D-07 branch design exactly. |
| `tests/test_converted_image_collision_render_gate.py` + fixture tree | D-10 render gate, xfail markers removed | ✓ VERIFIED | 3/3 passing, both `xfail` decorators removed and confirmed (via `xfail`-filtered diff, independently spot-checked) to be the only edit. |
| `tests/test_builder.py` (4 new unit tests) | srcdir-collision, escape, cross-drive, destination-containment coverage | ✓ VERIFIED | All 4 present and passing; both D-12-pinned tests confirmed byte-unchanged (`git diff 2ccbbd3a` shows additions only). |
| `50-RED-EVIDENCE.md`, `50-D11-*`, `50-BRANCH-EVIDENCE.md` | Phase evidence chain | ✓ VERIFIED (IMG-01/SC#3 portions); ✗ MISSING (IMG-02 RED portion) | See gap above. |
| `50-REVIEW.md` | Code review report | ✓ VERIFIED | Committed, 1 critical / 1 warning / 1 info; CR-01 assessed above. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `_track_image()` escape/collision branches | `copy_image_files()` | tracked `self.images` key IS the copy destination | ✓ WIRED | `path.join(self.outdir, imguri)` — confirmed no code path lets a relocated key retain a leading `..` (escape check runs first, before the collision probe, before any key is chosen). |
| D-10 gate (`tests/test_converted_image_collision_render_gate.py`) | `typsphinx/builder.py` | real `-b typstpdf` compile through `_track_image()` | ✓ WIRED | End-to-end: fixture → sphinx build → `.typ` emission → `typst.compile()` → `pypdf` extraction, all independently re-run and passing. |
| `_escapes_outdir()` | `_track_image()` (new call site) | cross-domain reuse for image-path escape detection | ✓ WIRED | `typsphinx/builder.py:923`, confirmed with a one-line rationale comment as the plan required. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| IMG-01 | 50-01, 50-02, 50-03 | Converted/source basename collision no longer destroys either image | ✓ SATISFIED | End-to-end D-10 gate + unit tests, all passing; RED-first evidence present and correctly structural (D-08). |
| IMG-02 | 50-02, 50-03 | Absolute URI outside `doctreedir` never escapes `outdir` | ✓ SATISFIED functionally / ✗ evidence-chain gap | Fix implemented and unit-tested post-fix; SC#2's explicit "RED first" clause not met — see gap. |

No orphaned requirements: `.planning/REQUIREMENTS.md` maps only IMG-01/IMG-02 to Phase 50, both
declared in plan frontmatter. **Note (informational, not a gap):** REQUIREMENTS.md's own tracking
table (lines 265-266) still shows both as "Pending" rather than "Complete" — consistent with this
project's convention (per user memory) of flipping that column at ship/complete-milestone time, not
at verify-work time. Not counted as a gap here.

### Anti-Patterns Found

None. No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers in any file this phase touched.
`ruff` unrunnable on this NixOS host (known, filed limitation — lint authority taken from CI per
Phase 45.2 precedent, consistent with all three plans' own disclosure). `black --check .` and `mypy
typsphinx/` independently re-confirmed clean is not re-run here (already verified clean in
50-BRANCH-EVIDENCE.md §4, and no source line changed since).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| D-10/D-12 render gates pass on the current tree (not just as claimed in SUMMARYs) | `uv run python -m pytest tests/test_converted_image_collision_render_gate.py tests/test_absolute_image_render_gate.py tests/test_builder.py -q` | `30 passed in 1.58s` | ✓ PASS |
| Full suite matches the claimed post-phase count | `uv run python -m pytest -q` | `1156 passed, 5 skipped in 107.30s` | ✓ PASS — matches orchestrator's measured facts exactly |
| D-12 fixed-point files are byte-unchanged for the whole phase | `git diff 2ccbbd3a -- tests/test_absolute_image_render_gate.py tests/fixtures/absolute_image_render_gate` | empty | ✓ PASS |
| `tests/test_builder.py`'s phase diff is additions-only | `git diff 2ccbbd3a -- tests/test_builder.py \| grep -c '^-[^-]'` | `0` | ✓ PASS |
| `docs/source` / `tests/roots` contain zero image assets (independent confirmation of the D-11 caveat) | `find docs/source -iname "*.png" -o ...` | `0` files | ✓ PASS (confirms caveat, not a defect) |

### Human Verification Required

See `human_verification` in frontmatter (CR-01 disposition — 1 item).

### Gaps Summary

One gap: **IMG-02 has no written-first, pytest-recorded RED**, despite ROADMAP.md's Phase 50 SC#2
explicitly requiring one ("RED first: a fixture proving today's destination is `../`-prefixed"). The
underlying fix is implemented correctly and is unit-tested post-fix (confirmed independently, all
tests pass), so this is an evidence-chain/process gap rather than a functional defect — but it is a
literal, unambiguous ROADMAP mandate that this phase's own artifacts (50-02-SUMMARY.md's own coverage
table) already concede was not met, rather than something this verification is the first to surface.
Per this phase's own repeatedly-stated binding constraint #6 ("no laundered gates") and #4 ("RED
first"), this is recorded as a blocking gap rather than smoothed over, even though closing it does not
require touching `typsphinx/builder.py` again — only recording (or reconstructing) the missing
pre-fix observation.

A closure plan for this gap has a narrow, well-defined scope: reproduce IMG-02's pre-fix `../`-prefixed
destination as a recorded RED — either by temporarily reverting `_track_image()`'s absolute-URI branch
to its pre-Phase-50 shape in an isolated context and running a fixture/unit test against it (recording
the verbatim failure, matching the D-08 style already used for IMG-01), or by an explicit owner-signed
override in this VERIFICATION.md's frontmatter accepting the pre-existing 2026-08-10 manual todo
measurement as sufficient evidence in place of a fixture-integrated RED.

---

_Verified: 2026-08-14T21:45:00Z_
_Verifier: Claude (gsd-verifier)_
