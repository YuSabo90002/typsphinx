---
phase: 42-captioned-table-drops-preceding-target-label
verified: 2026-08-04T00:00:00Z
status: passed
score: 6/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 42: Captioned Table Drops Preceding Target Label Verification Report

**Phase Goal:** A captioned table that is immediately preceded by a standalone target
(`.. _label:`) emits Typst labels for **both** ids — the `:name:`-derived one and the target's —
so the surviving reference resolves instead of failing the compile on a dangling label.

**Verified:** 2026-08-04
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria, independently re-checked)

| # | Truth (SC) | Status | Evidence |
|---|------------|--------|----------|
| 1 | A minimal `.rst` snippet reproduces the failure with the Typst error text captured verbatim, and the actual `node["ids"]`/`node["names"]` at `depart_table` are recorded | ✓ VERIFIED | `42-GATE-EVIDENCE-01.md` §2 records verbatim `sphinx-build -b typstpdf` stderr containing `TypstError: label `<index:tbl-target>` does not exist in the document`; §3 records a probe-derived per-shape table of `node["ids"]`/`node["names"]` for all four D-01 shapes plus the caption-less control. Independently confirmed: the same fix diff and RED/GREEN commit shape exist in `git log`/`git show` on the main tree (below). |
| 2 | Whether captioned figures exhibit the same drop is answered either way, with the measurement recorded | ✓ VERIFIED | `42-GATE-EVIDENCE-02.md` answers NO (figures unaffected) with a real `-b typstpdf` build (exit 0, empty stderr, valid `%PDF` produced) and a code-level root-cause explanation (`add_text` only branches on `self.in_table`, never `self.in_figure`). Confirmed: `tests/test_figure_propagated_target_render_gate.py` (7 tests) exists and passes on the current tree (ran directly, see Behavioral Spot-Checks). |
| 3 | A captioned table preceded by a standalone target compiles, and both labels resolve; no "label … occurs multiple times" fatal is introduced | ✓ VERIFIED | `42-GATE-EVIDENCE-04.md` §3 shows a real post-fix `-b typstpdf` build (exit 0), emitted `.typ` with both label forms present per shape, and a `grep \| uniq -c` proving every `<index:...>` label is defined exactly once. Independently re-ran `tests/test_captioned_table_propagated_target_render_gate.py` on the current main tree: 9/9 pass (see Behavioral Spot-Checks). Fix code independently read at `typsphinx/translator.py:3341-3370` on HEAD — matches the diff in the evidence file exactly. |
| 4 | The caption-less table path is byte-for-byte unchanged, proven by diff over an emitted fixture rather than by inspection | ✓ VERIFIED | `42-GATE-EVIDENCE-05.md` uses two isolated throwaway git worktrees (pre-fix `d28f2c8`, post-fix `e5575f3`), each independently provisioned (`uv sync`) with a confirmed *distinct* `typsphinx.__file__` resolution per worktree (the positive isolation control). §4b records a genuinely non-empty whole-file diff for the captioned shapes (proving the two builds ran different code), and §4a/§4c record empty diffs for both caption-less control tables. This is exactly the two-sided proof the verifier brief asked to check for (positive control + distinct resolved paths), and both are present. |
| 5 | Per milestone invariant #4 this is a classic GATE-01 candidate — the fixture is recorded RED as a real `TypstError` against the unfixed code before the fix lands | ✓ VERIFIED | `42-GATE-EVIDENCE-01.md` records commit `d28f2c8` with `git status --porcelain typsphinx/` empty (no production change) and 7/9 tests RED with the literal `does not exist in the document` failure. Independently re-verified on the main tree: `git merge-base --is-ancestor d28f2c8bcdf8aee49ab82b1d883145a4036acefc e5575f3ab51144405c44764a5b192b9d5f7526b2` exits 0 (RED commit is a strict ancestor of the fix commit `e5575f3`), and `git log 19a6378..HEAD -- typsphinx/` shows exactly one production commit, `e5575f3`. |
| 6 | Phase 41's release-prep artifacts are reconciled: CHANGELOG gains its TBL-03 line, and SC#4's node-handler/RED sweep is re-measured over a range including Phase 42 | ✓ VERIFIED | `CHANGELOG.md` lines 55-58 (main tree, independently grepped) contain the TBL-03 bullet under `## [0.7.0]` / `### Fixed`. `42-SC4-INVARIANTS.md` re-measures invariants 1, 2, 4, 5 over `51e02b6..d57f6d1` (a range including Phase 42's fix commit `e5575f3`, confirmed by `git merge-base --is-ancestor`), all PROVEN. `42-CLOSEOUT-GUARD.md` records REL-04/REL-05's pre-close state with a checksum; independently confirmed on the main tree that REL-04/REL-05 remain `- [ ]` / Pending in `.planning/REQUIREMENTS.md` (not auto-flipped). |

**Score:** 6/6 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py` | `depart_table`'s propagated-anchor call moved past `self.in_table = False`, gated by `was_captioned` captured before `self.table_caption` reset | ✓ VERIFIED | Read directly at HEAD (`sed -n '3340,3371p'`): matches `42-GATE-EVIDENCE-04.md`'s diff exactly — `was_captioned = self.table_colcount > 0 and bool(self.table_caption)` at line 3353, `self.in_table = False` at 3355, guarded `_emit_id_anchors` call at 3369-3370. |
| `tests/fixtures/captioned_table_propagated_target_render_gate/{conf.py,index.rst}` | Four D-01 shapes + caption-less control | ✓ VERIFIED | Present; drives `tests/test_captioned_table_propagated_target_render_gate.py`, 9/9 pass on HEAD |
| `tests/test_captioned_table_propagated_target_render_gate.py` | 9-method RED→GREEN gate | ✓ VERIFIED | Present, 9/9 PASSED on independent re-run against main tree |
| `tests/fixtures/figure_propagated_target_render_gate/{conf.py,index.rst,image.png}` | D-10 three-shape figure fixture | ✓ VERIFIED | Present |
| `tests/test_figure_propagated_target_render_gate.py` | 7-method permanent figure regression gate | ✓ VERIFIED | Present, 7/7 PASSED on independent re-run against main tree |
| `42-GATE-EVIDENCE-01.md` through `-05.md`, `42-SC4-INVARIANTS.md`, `42-CLOSEOUT-GUARD.md` | Purpose-named evidence files, not overwritten | ✓ VERIFIED | All present, read in full, internally consistent with each other and with independently re-run commands |
| `.planning/todos/pending/2026-08-03-table-whitespace-only-title-anchor-divergence.md` | D-08 todo filed, not fixed | ✓ VERIFIED | File exists in pending todos directory |
| `CHANGELOG.md` | TBL-03 bullet added to `## [0.7.0]` / `### Fixed` | ✓ VERIFIED | Confirmed present at lines 55-58 |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `_emit_id_anchors(node, skip_ids=...)` in `depart_table` | `self.body` (not `self.table_cell_content`) | Call now fires after `self.in_table = False` | ✓ WIRED | Confirmed by direct code read at HEAD; `add_text`'s single branch condition (`self.in_table`) is unchanged, so post-reset the call now routes to `self.body` |
| RED commit `d28f2c8` | Fix commit `e5575f3` | `git merge-base --is-ancestor` | ✓ WIRED | Exit 0, independently re-run on main tree |
| `depart_table` fix | `test_captioned_table_propagated_target_render_gate.py` | pytest | ✓ WIRED | 9/9 pass against current HEAD, independently re-run |
| CHANGELOG TBL-03 bullet | Phase 42 fix | Prose cross-reference `(TBL-03)` | ✓ WIRED | Grepped directly in `CHANGELOG.md` |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Table gate (9 tests) passes on main tree | `uv run python -m pytest tests/test_captioned_table_propagated_target_render_gate.py tests/test_figure_propagated_target_render_gate.py -q` | `16 passed in 0.67s` | ✓ PASS |
| Full suite (excluding the two new gate modules) unaffected | `uv run python -m pytest tests/ -q --deselect ... --deselect ...` | `805 passed, 1 skipped, 16 deselected` (805+16=821, matching orchestrator's full-suite count) | ✓ PASS |
| Fix diff present in production source | Direct `Read` of `typsphinx/translator.py:3340-3371` | Matches evidence file diff exactly | ✓ PASS |
| Ancestry: RED strictly precedes fix | `git merge-base --is-ancestor d28f2c8... e5575f3...` | exit 0 | ✓ PASS |
| Lint/format/type clean | `black --check .`, `ruff check .`, `mypy typsphinx/` | all clean | ✓ PASS |
| No debt markers introduced in the diff | `git diff 19a6378..HEAD -- typsphinx/translator.py \| grep -iE "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER"` | no output (exit 1 = no match) | ✓ PASS |
| REL-04/REL-05 not auto-flipped | `sed -n` on `.planning/REQUIREMENTS.md` lines 208/212/337/338 | still `- [ ]` / Pending | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|--------------|-------------|--------|----------|
| TBL-03 | 42-01 through 42-06 (all six plans declare `requirements: [TBL-03]`) | Captioned table + preceding standalone target emits both labels | ✓ SATISFIED | All six SCs verified above; fix present and tested on main tree; no orphaned requirements found (`REQUIREMENTS.md` line 195 traceability row at line 339 correctly still Pending — the checkbox flip is an explicit phase-close step, deliberately deferred per `42-CLOSEOUT-GUARD.md`, not a gap) |

No orphaned requirements: `grep -n "Phase 42" .planning/REQUIREMENTS.md` shows only TBL-03 mapped to this phase, and TBL-03 is claimed by every plan.

### Anti-Patterns Found

None. `git diff 19a6378..HEAD -- typsphinx/translator.py` contains no `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers. The code-review report (`42-REVIEW.md`, 0 critical / 1 warning / 2 info) flags:
- **WR-01** (warning, non-blocking): `_emit_id_anchors`'s docstring still says "the sole user is `depart_figure`" even though `depart_table` has used the same `skip_ids` pattern since Phase 25 and Phase 42 heavily extends that second call site. Independently confirmed still present at `typsphinx/translator.py:516-517` on HEAD — this was not fixed post-review. This is a documentation-accuracy issue, not a functional defect; it does not affect any of the six success criteria and does not block phase completion, but is worth a follow-up.
- **IN-01** (info): an unused pytest fixture in the new test module (dead code, no functional impact).
- **IN-02** (info): a pre-existing (not introduced by this phase), out-of-scope nested-table data-loss bug, empirically confirmed identical on both pre-fix and post-fix trees by the reviewer — correctly scoped out of this phase.

None of these three findings rises to a blocker: WR-01 is a stale comment, IN-01 is dead test code, IN-02 is explicitly pre-existing and unrelated to the diff.

### Human Verification Required

None. All six success criteria are backed by executable evidence (real Typst compiles, real pytest runs, real git ancestry checks) that this verification independently re-ran or re-derived against the main tree — not merely re-read from SUMMARY.md prose.

### Gaps Summary

No gaps. All six ROADMAP success criteria are discharged by dedicated, purpose-named evidence files that this verification cross-checked against the live main-tree codebase (not just read as claims):

- The fix code at `typsphinx/translator.py:3340-3371` matches the evidence files' diffs exactly.
- `git merge-base --is-ancestor` independently confirms the classic-RED-before-GREEN commit ordering required by milestone invariant #4.
- The two new gate test modules (16 tests total) independently pass on the current main tree.
- The full suite (821 passed, 1 skipped) matches the orchestrator's measurement exactly (805 + 16 deselected = 821).
- `black`/`ruff`/`mypy` are all clean.
- CHANGELOG.md carries the TBL-03 line; REL-04/REL-05 remain correctly un-flipped; TBL-03's own checkbox is correctly still `- [ ]` (its flip is an explicit phase-close step, not a verification-time gap).
- SC#4's byte-invariance proof includes the positive control (a genuinely non-empty diff for the captioned shapes) and distinct `typsphinx.__file__` resolutions per worktree, satisfying the specific skepticism check requested for this phase.

One non-blocking follow-up worth noting to the human: WR-01 from the code review (a stale docstring claiming `depart_figure` is the "sole user" of `_emit_id_anchors`'s `skip_ids` parameter, when `depart_table` has shared that pattern since Phase 25 and this phase's own fix heavily extends it) was not addressed post-review. It carries a real future-maintenance risk (a reader could "simplify" the helper assuming there is only one caller) but does not affect any success criterion.

---

*Verified: 2026-08-04*
*Verifier: Claude (gsd-verifier)*
