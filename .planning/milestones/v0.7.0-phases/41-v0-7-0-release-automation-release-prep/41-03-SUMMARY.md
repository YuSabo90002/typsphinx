---
phase: 41-v0-7-0-release-automation-release-prep
plan: 03
subsystem: docs
tags: [docstring, docutils, autodoc, planning-record-hygiene, todo-management]

# Dependency graph
requires:
  - phase: 37-signature-typography-the-desc-family
    provides: "visit_desc_sig_name's rule-2 unresolved-C-domain-type measurement, whose docstring contained the unbalanced asterisk fixed here"
  - phase: 38-structural-indentation-info-fields
    provides: "the two already-fixed code facts (_desc_break_marker tuple shape; EXPECTED_PAGE_COUNT_CEILING rename) re-verified and filed here"
provides:
  - "A clean visit_desc_sig_name docstring that parses through docutils with no inline-emphasis warning, removing one warning line from the tox -e docs-pdf build plan 41-05 collects as SC#3 evidence"
  - "Two resolved todos filed to .planning/todos/completed/ with re-measured evidence, leaving exactly 7 files under .planning/todos/pending/"
  - "PROJECT.md with balanced HTML comment markers (31 open / 31 close, zero unterminated)"
affects: [41-05-release-prep-evidence, 41-06-milestone-invariant-sweep, 41-07-handoff]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Mechanical HTML-comment-balance scan (regex-count <!-- vs -->, per-opener next-opener-boundary check) as a repeatable planning-record hygiene check"

key-files:
  created: []
  modified:
    - typsphinx/translator.py
    - .planning/PROJECT.md
    - .planning/todos/pending/ (2 files removed)
    - .planning/todos/completed/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md
    - .planning/todos/completed/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md

key-decisions:
  - "D-12 fix shape: wrap the C type expression in double-backtick RST inline literal (``PyTypeObject *type``) rather than rephrasing the sentence or escaping the asterisk with a backslash -- keeps the prose unchanged."
  - "D-13: both todos re-verified against the live worktree code (not transcribed from CONTEXT.md's already-measured claim) before moving; both facts held exactly as recorded."
  - "The visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md and release-notes-body-from-changelog-section.md todos are deliberately left under pending/ per the plan -- their filing is a plan-41-07 close-side handoff item, not this plan's job."

patterns-established: []

requirements-completed: []  # REL-05 is only fully satisfied when all of Phase 41's plans land; this plan is prep-half groundwork, not a requirement-closing plan on its own.

coverage:
  - id: D1
    description: "visit_desc_sig_name's docstring parses as clean reStructuredText (no docutils inline-emphasis warning), with the pre-fix RED captured first"
    requirement: REL-05
    verification:
      - kind: unit
        ref: "manual docutils.core.publish_doctree probe (see below) -- pre-fix non-empty, post-fix empty"
        status: pass
      - kind: unit
        ref: "tests/test_translator.py -x -q"
        status: pass
    human_judgment: false
  - id: D2
    description: "The change is provably docstring-only (no executable line of typsphinx/translator.py touched)"
    requirement: REL-05
    verification:
      - kind: other
        ref: "git diff c81ca29~1..c81ca29 -- typsphinx/translator.py (1 line changed, inside the docstring only)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Two D-13 todos filed to todos/completed/ with re-measured resolution evidence; nothing else moved"
    requirement: REL-05
    verification:
      - kind: other
        ref: "test -f .planning/todos/completed/2026-08-01-*.md (both) && test ! -e .planning/todos/pending/2026-08-01-*.md (both) && ls .planning/todos/pending | wc -l == 7"
        status: pass
    human_judgment: false
  - id: D4
    description: "PROJECT.md's HTML comment markers are balanced (31/31), pre-fix offender list recorded"
    requirement: REL-05
    verification:
      - kind: other
        ref: "python regex scan over .planning/PROJECT.md -- 31 opens, 31 closes, zero unterminated"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-08-03
status: complete
---

# Phase 41 Plan 03: Docstring Fix + Planning-Record Hygiene Summary

**Fixed the unbalanced asterisk in `visit_desc_sig_name`'s docstring (D-12), filed two already-fixed
todos to `completed/` with re-measured evidence, and terminated PROJECT.md's two unterminated HTML
comments (D-13) -- no `typsphinx/` behavior change, no irreversible release action.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-08-03T20:28:55+09:00
- **Tasks:** 3/3
- **Files modified:** 4 (1 code, 1 docs, 2 todo-file moves)

## Accomplishments

- `TypstTranslator.visit_desc_sig_name`'s docstring now parses through `docutils.core.publish_doctree`
  with an empty warning stream (was: `Inline emphasis start-string without end-string`), by wrapping
  the C type expression `PyTypeObject *type` in an RST double-backtick inline literal. Diff is exactly
  one line inside the docstring; no executable line of `typsphinx/translator.py` changed.
- Two todos describing defects already fixed in Phase 38 were re-verified against this worktree's live
  code (not transcribed from `41-CONTEXT.md`'s recorded claim) and filed to `.planning/todos/completed/`
  with a `## Resolved` section quoting the measured evidence. `.planning/todos/pending/` now holds
  exactly 7 files.
- `.planning/PROJECT.md`'s two unterminated `<!-- Prior: ...` comments (measured this session at lines
  761 and 775, not the stale 492/506 CONTEXT.md figures) were closed with an appended ` -->`. Marker
  count is now balanced at 31 opens / 31 closes.

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix the visit_desc_sig_name docstring, RED first** - `c81ca29` (fix)
2. **Task 2: Re-verify and file the two already-fixed todos to completed/** - `15db2db` (docs)
3. **Task 3: Terminate PROJECT.md's two unterminated HTML comments** - `43a2a78` (docs)

_No plan-metadata commit in this worktree -- SUMMARY.md is committed as part of this same branch per
the worktree-execution protocol; STATE.md/ROADMAP.md are updated centrally by the orchestrator after
merge._

## Files Created/Modified

- `typsphinx/translator.py` - `visit_desc_sig_name`'s docstring: wrapped `PyTypeObject *type` in
  double-backtick RST inline literal, closing the unbalanced-asterisk inline-emphasis warning.
- `.planning/PROJECT.md` - appended a closing ` -->` to the two unterminated "Prior footer" comments
  at lines 761 and 775.
- `.planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md` -> moved to
  `.planning/todos/completed/`, with a `## Resolved` section added.
- `.planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md` ->
  moved to `.planning/todos/completed/`, with a `## Resolved` section added.

## Planned deletions

This plan intentionally deletes two paths from `.planning/todos/pending/` (moved to
`.planning/todos/completed/` under the same filenames) — this is expected per the plan's
`<planned_deletion_notice>` and is NOT a defect. The `worktree.cleanup-wave` merge helper will
hard-block this branch on `branch_contains_deletions`; that block should route to a manual,
scope-verified merge rather than being treated as a failure.

**Exact deleted paths** (verbatim):
```
.planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md
.planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md
```

**Measured proof — `git diff --no-renames --diff-filter=D --name-only c81ca29~1..HEAD`** (git's default
rename detection hides these as renames rather than deletions; `--no-renames` is required to see them
as the plan's `<planned_deletion_notice>` describes):
```
.planning/todos/pending/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md
.planning/todos/pending/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md
```
Output lists exactly the two paths above and nothing else — the deletion scope matches the plan's
declared `files_modified` exactly.

## Decisions Made

- **D-12 fix shape:** double-backtick RST inline literal around `PyTypeObject *type`, per
  `41-PATTERNS.md`'s named acceptable fix shape. Chosen over rephrasing the sentence (would restate
  the docutils diagnostic prose, which the plan forbids) or moving the asterisk (changes the literal
  C type expression being quoted).
- **D-13 re-verification, not transcription:** both todo facts were independently re-measured by grep
  in this worktree rather than trusting `41-CONTEXT.md`'s already-recorded claim, per this project's
  standing rule and the plan's third `must_haves.prohibitions` entry. Both held exactly as recorded;
  no todo was left pending due to a stale premise.
- **Two todos deliberately NOT moved:** `2026-08-01-visit-desc-sig-name-docstring-unbalanced-asterisk-warning.md`
  and `2026-07-29-release-notes-body-from-changelog-section.md` remain under `pending/` even though
  both are resolved by this phase's own code work (the former by this plan's own Task 1; the latter by
  plan 41-01/41-02's REL-04 work) -- per the plan's explicit instruction, their filing to `completed/`
  is a plan-41-07 close-side handoff item, not this plan's job.

## Deviations from Plan

None - plan executed exactly as written. The RED-first sequencing in Task 1 worked on the first
attempt (the probe immediately reproduced the recorded `Inline emphasis start-string without
end-string` diagnostic; no substitute probe was needed). Both D-13 facts held on first re-verification
(no todo required a "stop and report" divergence). The mechanical PROJECT.md scan found exactly two
unterminated openers, matching the plan's expectation of "exactly two."

## Evidence — Task 1 RED/GREEN (verbatim)

**Pre-fix probe (RED):**
```
$ uv run python -c "
import io, inspect, docutils.core
from typsphinx.translator import TypstTranslator
doc = inspect.cleandoc(TypstTranslator.visit_desc_sig_name.__doc__)
w = io.StringIO()
docutils.core.publish_doctree(doc, settings_overrides={'report_level':2,'halt_level':5,'warning_stream':w})
print('--- WARNING STREAM ---')
print(w.getvalue())
print('--- END ---')
"
--- WARNING STREAM ---
<string>:33: (WARNING/2) Inline emphasis start-string without end-string.

--- END ---
```

**Post-fix probe (GREEN):**
```
$ uv run python -c "
import io, inspect, docutils.core
from typsphinx.translator import TypstTranslator
doc = inspect.cleandoc(TypstTranslator.visit_desc_sig_name.__doc__)
w = io.StringIO()
docutils.core.publish_doctree(doc, settings_overrides={'report_level':2,'halt_level':5,'warning_stream':w})
assert w.getvalue()=='', 'docutils still reports:\n'+w.getvalue()
print('docstring parses clean')
"
docstring parses clean
```

**Full verification run (Task 1 `<verify>` block):**
```
$ uv run pytest tests/test_translator.py -x -q
117 passed in 0.16s

$ uv run black --check .
All done! (205 files would be left unchanged.)

$ ruff check .   # run via the main checkout's patchelf'd binary -- the worktree's own uv-installed
                 # ruff copy is a generic-linux ELF that NixOS's stub loader cannot exec (exit 127,
                 # STATE.md's documented NixOS shim hazard); the main checkout's ruff is
                 # functionally identical (same version, 0.15.20) and only lints file contents, so
                 # invoking it against the worktree's own tree is equivalent to `uv run ruff check .`
All checks passed!

$ uv run mypy typsphinx/
Success: no issues found in 6 source files

$ uv run pytest -m "not slow" -q
771 passed, 29 deselected in 54.38s
```

## Evidence — Task 2 re-measured facts (verbatim)

**`_desc_break_marker` buffer-identity tuple shape:**
```
$ grep -n "_desc_break_marker" typsphinx/translator.py
261:        self._desc_break_marker: tuple[int, int] | None = None
5542:        if not self.in_table and self._desc_break_marker == (
5548:        self._desc_break_marker = (id(self.body), len(self.body))
5885:        marker_was_untouched = not self.in_table and self._desc_break_marker == (
5891:            self._desc_break_marker = (id(self.body), len(self.body))
```
All three sites (init + two comparison/assignment pairs) carry the `(id(self.body), len(self.body))`
tuple shape.

**`EXPECTED_PAGE_COUNT_CEILING` rename:**
```
$ grep -n "EXPECTED_PAGE_COUNT" tests/test_signature_page_boundary_render_gate.py
147:EXPECTED_PAGE_COUNT_CEILING = 7
...
$ grep -rn "EXPECTED_PAGE_COUNT_PRE_PHASE" tests/
tests/test_signature_page_boundary_render_gate.py:112:# the identifier `EXPECTED_PAGE_COUNT_PRE_PHASE` had already held a
tests/test_signature_page_boundary_render_gate.py:305:        7, and the rename from EXPECTED_PAGE_COUNT_PRE_PHASE this phase
```
Old name appears only in two historical prose comments narrating the rename, never as a live
identifier.

## Evidence — Task 3 mechanical scan (verbatim)

**Pre-fix scan** (offending lines, line number + first 120 chars):
```
761 '<!-- Prior: 2026-07-23 at v0.6.2 milestone close (`/gsd-complete-milestone`) — full evolution review complete. v0.6.2 (r'
775 '<!-- Prior: 2026-07-11 after Phase 10 (Version-String Fix + v0.5.0 Release) complete — the FINAL phase of the v0.5.0 mil'
opens: 31 closes: 29
```

**Post-fix scan:**
```
PROJECT.md comment markers balanced: 31 pairs
```

## Verification — plan-level invariants (verbatim)

```
$ git diff --stat c81ca29~1..HEAD -- pyproject.toml uv.lock .planning/REQUIREMENTS.md
(empty)

$ git tag -l v0.7.0
(empty)

$ git ls-remote --tags origin v0.7.0
(empty)
```
No version-literal, lockfile, or requirements-traceability file was touched; no local or remote
`v0.7.0` tag exists -- the prep/publish fence held. This plan took no irreversible release action.

## Issues Encountered

None beyond the routine NixOS `ruff` shim hazard (documented above in the Task 1 evidence block and
in `STATE.md`'s standing operator note) -- worked around by invoking the main checkout's already-
patchelf'd `ruff` binary directly rather than through the worktree's own `.venv/bin/uv run ruff`,
since `ruff check` only lints file contents and does not import the `typsphinx` package (so it carries
none of the editable-install isolation hazard that motivates running everything else via `uv run`).

## Next Phase Readiness

- The `visit_desc_sig_name` docstring is clean going into plan 41-05's `tox -e docs-pdf` SC#3
  evidence collection -- one fewer warning line in that build's output.
- `.planning/todos/pending/` is down to 7 files, all either D-14-deferred (4) or intentionally left
  for plan 41-07's close-side handoff (2 -- the `release-notes-body-from-changelog-section` and
  `visit-desc-sig-name-docstring-unbalanced-asterisk-warning` todos).
- No blocker for downstream plans. The two-file deletion in this branch requires a manual,
  scope-verified merge past `worktree.cleanup-wave`'s deletion guard -- see "Planned deletions" above
  for the exact measured scope the merge should be checked against.

---
*Phase: 41-v0-7-0-release-automation-release-prep*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: `.planning/phases/41-v0-7-0-release-automation-release-prep/41-03-SUMMARY.md`
- FOUND: `.planning/todos/completed/2026-08-01-desc-break-marker-stale-across-body-buffer-swaps.md`
- FOUND: `.planning/todos/completed/2026-08-01-expected-page-count-pre-phase-misnamed-post-phase-value.md`
- FOUND commit `c81ca29` (Task 1: docstring fix)
- FOUND commit `15db2db` (Task 2: todo filing)
- FOUND commit `43a2a78` (Task 3: PROJECT.md comment termination)
- FOUND commit `0b7275a` (this SUMMARY.md)
