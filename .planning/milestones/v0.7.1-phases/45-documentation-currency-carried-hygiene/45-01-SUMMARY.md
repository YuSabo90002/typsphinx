---
phase: 45-documentation-currency-carried-hygiene
plan: 01
subsystem: docs
tags: [myst-parser, sphinx, docutils, changelog, typstpdf, uv]

# Dependency graph
requires: []
provides:
  - "docs/source/changelog.rst delegates its release history to repo-root CHANGELOG.md via a single `.. include:: ../../CHANGELOG.md` with `:parser: myst_parser.sphinx_` (no `:start-line:` — see Deviations)"
  - "myst-parser>=5.0 registered in [project.optional-dependencies].docs and docs/source/conf.py's extensions list"
  - "A pre-phase docs-build warning baseline (45-GATE-EVIDENCE-01-docs-build-baseline.md) for wave-2's build-clean delta check"
  - "45-GATE-EVIDENCE-01-include-shape.md — the four-shape investigation (ladder rungs i/ii/iii plus the working shape), root-caused via myst-parser source, with both real builds' measured results"
affects: [45-02-plan, 45-03-plan, 45-04-plan]

# Actuals (#2632)
actuals:
  tokens: 6475
  tasks: 3
  commits: 2

tech-stack:
  added: [myst-parser>=5.0]
  patterns:
    - "Markdown-in-rST delegation via docutils' `include::` `:parser:` option, letting the included fragment's own H1 + preamble supply the host page's title (required to avoid myst-parser's per-fragment 'headings start at H1' consistency check, which is isolated from ambient rST section nesting — see evidence file)"

key-files:
  created:
    - .planning/phases/45-documentation-currency-carried-hygiene/45-GATE-EVIDENCE-01-docs-build-baseline.md
    - .planning/phases/45-documentation-currency-carried-hygiene/45-GATE-EVIDENCE-01-include-shape.md
  modified:
    - pyproject.toml
    - uv.lock
    - docs/source/conf.py
    - docs/source/changelog.rst

key-decisions:
  - "myst-parser package-legitimacy checkpoint approved by human review (PyPI + GitHub source checked live); `unknown-downloads` SUS verdict confirmed as a data-availability artifact, not an adverse signal"
  - "Deviated from the plan's literal include shape (hand-authored rST title/framing + :start-line: 7) after measuring 19 changelog-attributable myst.header warnings from that exact shape; root-caused via installed myst-parser source rather than guessed"
  - "Ladder rung (ii) (nest the include one rST section deeper) was tried and empirically falsified — myst-parser's per-fragment section-level state is isolated from the host document's ambient nesting (docutils' Include.custom_parse() parses into a brand-new document per include call)"
  - "Chosen final shape: include CHANGELOG.md unclipped (no :start-line:), dropping the hand-authored rST title and two framing paragraphs so the page's single title/preamble comes from CHANGELOG.md's own H1 — the only shape proven warning-clean without editing CHANGELOG.md (prohibited) or suppressing warnings (prohibited)"

patterns-established:
  - "Docs-build warning baseline capture (grep for literal 'WARNING:' in combined stdout+stderr, not exit code or Sphinx's own summary count, which folds in docutils ERROR-severity messages too) — reusable by any future doc-page-generation phase in this repo"

requirements-completed: [DOC-12]

coverage:
  - id: D1
    description: "Pre-phase docs-build warning baseline captured against the untouched tree (html_warning_count=1, pdf_warning_count=1, changelog_attributable_warning_count=0), giving wave-2's build-clean check a delta reference rather than an assumed-zero baseline"
    verification:
      - kind: other
        ref: "45-GATE-EVIDENCE-01-docs-build-baseline.md (real `sphinx-build -b html` / `-b typstpdf` subprocess runs against HEAD 8c74b853, both exit 0, verbatim WARNING: lines recorded)"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/source/changelog.rst delegates to CHANGELOG.md via myst-parser; both -b html and -b typstpdf build clean of changelog-attributable warnings; all 11 in-scope release versions render; exactly one Changelog heading; no stale current-release marker"
    requirement: DOC-12
    verification:
      - kind: other
        ref: "Plan 45-01's own <verify> script run verbatim (real sphinx-build subprocess calls against both builders) — printed 'OK both builders'"
        status: pass
      - kind: unit
        ref: "tests/test_changelog_extraction.py -v (6/6 passed — REL-04's extractor surface undisturbed, CHANGELOG.md untouched)"
        status: pass
    human_judgment: false

duration: 44min
completed: 2026-08-10
status: complete
---

# Phase 45 Plan 01: Documentation Currency + Carried Hygiene (Changelog Delegation Tracer) Summary

**`docs/source/changelog.rst` now renders live from repo-root `CHANGELOG.md` via myst-parser's `include::` `:parser:` mechanism — both `-b html` and `-b typstpdf` build clean of changelog-attributable warnings, closing the drift channel that left the published page stale at v0.4.0 for two years.**

## Performance

- **Duration:** 44 min (Task 1 commit `06:51:33+09:00` → Task 3 commit `07:11:06+09:00`; includes a `checkpoint:human-verify` pause for the package-legitimacy gate, resolved by human approval)
- **Started:** 2026-08-10T06:35:00+09:00 (approx., first Bash call)
- **Completed:** 2026-08-10T07:11:06+09:00
- **Tasks:** 3 (Task 1: auto; Task 2: checkpoint:human-verify, approved; Task 3: tracer)
- **Files modified:** 4 source files + 2 evidence files created

## Accomplishments

- `myst-parser>=5.0` added to the `docs` extra only (`[project].dependencies` untouched, still exactly 3 entries); `uv.lock` regenerated additively (+31 lines, no unrelated drift)
- `docs/source/conf.py` registers `myst_parser` in `extensions`
- `docs/source/changelog.rst` replaced 78 lines of hand-maintained, two-year-stale release history (and the stale "Development Status: v0.3.x is current" section) with a single `.. include:: ../../CHANGELOG.md` directive
- Root-caused, via the installed myst-parser source (not guessed), why the plan's literally-specified include shape produces 19 spurious warnings, empirically falsified the plan's rung-(ii) fallback, and landed on the one shape proven warning-clean by two real builds
- Backstop truth measured live: a missing `CHANGELOG.md` produces a loud `CRITICAL` docutils error, not a silently-empty page (confirmed by temporarily moving the file aside and restoring it — `git status` shows zero diff on `CHANGELOG.md`)
- Fixed a NixOS-sandbox `ruff` shim issue local to this worktree's venv (documented, not a repo change) so `ruff check .` could actually run and confirm clean

## Task Commits

1. **Task 1: Capture the pre-phase docs-build warning baseline** - `ac805f6` (docs)
2. **Task 2: Package-legitimacy gate for myst-parser** - checkpoint only, no file changes; approved via human review (no separate commit — nothing to commit per the task's own `<what-built>`: "Nothing yet")
3. **Task 3: End-to-end changelog delegation** - `b6b1778` (feat)

_Note: Task 2 is a `checkpoint:human-verify` gate with no files of its own; the plan execution paused after Task 1, returned a structured checkpoint, and resumed here after the coordinator relayed the human's "approved" response._

## Files Created/Modified

- `pyproject.toml` - added `myst-parser>=5.0` to `[project.optional-dependencies].docs`
- `uv.lock` - regenerated (myst-parser + mdit-py-plugins resolved and locked)
- `docs/source/conf.py` - added `"myst_parser"` to `extensions`, before `"typsphinx"`
- `docs/source/changelog.rst` - replaced 78 lines of hand-maintained release history + the stale "Development Status" section with a 2-line `.. include::` directive; "Migration Guides" through "See Also" retained unedited (content correction is Plan 45-02's D-06 share)
- `.planning/phases/45-documentation-currency-carried-hygiene/45-GATE-EVIDENCE-01-docs-build-baseline.md` - pre-phase warning baseline (created)
- `.planning/phases/45-documentation-currency-carried-hygiene/45-GATE-EVIDENCE-01-include-shape.md` - the full four-shape investigation, root cause, and measured answers to RESEARCH's two open questions (created)

## Decisions Made

- **Package legitimacy (Task 2, human-approved):** `myst-parser`'s automated `SUS`/`unknown-downloads` verdict was accepted as a data-availability artifact (cross-checked independently via pypistats: ~1.5M downloads/week), not an adverse signal. Approved adding `myst-parser>=5.0` to the `docs` extra only.
- **Include shape (Task 3, auto-fixed per deviation Rule 1 — see Deviations below):** the plan's literally-specified shape (hand-authored rST title/framing + `:start-line: 7`) fails the plan's own zero-changelog-warning bar. Root-caused and replaced with the only shape that is provably clean without touching `CHANGELOG.md` or suppressing warnings.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's literal include shape produces 19 changelog-attributable warnings; ladder rung (ii) empirically falsified; landed on a fourth, root-caused shape**

- **Found during:** Task 3 (end-to-end changelog delegation)
- **Issue:** The plan's `<action>` instructed keeping the page's hand-authored rST title + two framing paragraphs, with the include clipped via `:start-line: 7` to skip `CHANGELOG.md`'s own `# Changelog` H1. Building against that exact shape produced 19 `WARNING: Document headings start at H2, not H1 [myst.header]` lines (one per `##`-level release heading in the fragment), all changelog-attributable — failing the plan's own `changelog_attributable_warning_count == 0` bar by a wide margin (baseline was 0).
- **Root cause (read from installed myst-parser source, not guessed):** `myst_parser/mdit_to_docutils/base.py`'s `update_section_level_state()` tracks heading levels per-fragment via `self._level_to_section`, seeded fresh as `{0: <root>}` for every `.. include:: :parser:` call (`docutils/parsers/rst/directives/misc.py::Include.custom_parse()` parses into a brand-new, isolated `document`). For a flat sequence of same-level (`##`) headings with no preceding `#`, its strict-`<` parent-level lookup returns `0` for *every* heading (not just the first), so the "headings start at H2, not H1" warning fires once per heading — and this state is provably isolated from the host document's own ambient section nesting.
- **Fix attempt 1 (the plan's ladder rung ii — nest the include one rST section deeper):** tried exactly as specified (added an intermediate `Full History` H3 wrapper). Measured: still 19 identical warnings — empirically confirms the root-cause analysis (ambient nesting has zero effect on this fragment-internal check).
- **Fix attempt 2 (ladder rung iii, analyzed not tried):** `:end-before:` only bounds the *end* of the range; cannot address a *missing-H1-at-the-start* problem. Ruled out by analysis.
- **Actual fix:** Include `CHANGELOG.md` unclipped (omit `:start-line:` entirely), so the fragment's own H1 satisfies myst-parser's internal consistency check with zero warnings — and drop the hand-authored rST title + framing paragraphs (since keeping both would duplicate the "Changelog" heading text, failing the "exactly one Changelog heading" truth). The page's title and framing now come directly from `CHANGELOG.md`'s own H1 and preamble.
- **Side effect, measured and documented (not hidden):** the six retained sections (`Migration Guides`, `Deprecation Policy`, `Upcoming Features`, `Versioning`, `Release Process`, `See Also`) now render as sibling `<h1>` top-level sections rather than `<h2>` children nested under one `Changelog` title — a consequence of the document no longer having exactly one top-level section (docutils' title-promotion heuristic requires exactly one). Content is unedited (matches "keep... in place for now"); only the heading *level* changed. **Flagged for Plan 45-02**, which owns correcting these sections' contents (D-06) and should be aware of this heading-level shift.
- **Files modified:** `docs/source/changelog.rst`
- **Verification:** Both `-b html` and `-b typstpdf` measured live: exit 0, zero changelog-attributable warnings (matching the pre-phase baseline's `changelog_attributable_warning_count=0`), `html_warning_count`/`pdf_warning_count` held at parity with baseline (1/1, both the pre-existing out-of-fence `visit_toctree` docstring defect). The plan's own `<verify>` subprocess script, run verbatim, printed `OK both builders`. All acceptance-criteria checks (tomllib dependency-count check, `myst_parser` in `extensions`, `uv.lock` grep, stale-marker greps) independently re-run and passing.
- **Committed in:** `b6b1778` (Task 3 commit)

**2. [Rule 3 - Blocking, environment-local] NixOS-sandboxed `ruff` binary could not execute in this fresh worktree venv**

- **Found during:** Task 3's broader `<verification>` sweep (running `ruff check .` as instructed by the plan's `<verification>` block)
- **Issue:** `uv sync`-installed `.venv/bin/ruff` is a generic-linux dynamically-linked ELF the NixOS host cannot execute directly (`Could not start dynamically linked executable`) — the same class of pre-existing environment hazard PROJECT.md's Phase 39/40 footers record for `.venv/bin/uv`.
- **Fix:** Resolved a Nix-store `ruff` via `nix-shell -p ruff` (resolved version `0.15.14`, within this repo's `ruff>=0.15,<0.16` pin) and symlinked it over `.venv/bin/ruff`, following the project's established `uv` shim precedent. This is a local, gitignored `.venv/` change only — no repository file was touched.
- **Files modified:** none (repo); `.venv/bin/ruff` (local, gitignored)
- **Verification:** `uv run ruff check .` then printed `All checks passed!`. `black --check .` and `mypy typsphinx/` also confirmed clean.
- **Committed in:** N/A (no repo change)

---

**Total deviations:** 2 auto-fixed (1 bug/Rule 1, 1 blocking/Rule 3 — environment-local, no repo change)
**Impact on plan:** The Rule 1 fix was necessary to meet the plan's own explicit acceptance bar (zero changelog-attributable warnings) after its literally-specified shape and both named ladder rungs were measured and found insufficient; the plan itself granted discretion to iterate within this task. The visible-heading-level side effect is real but does not violate any `must_haves.truths`, `acceptance_criteria`, or `prohibitions` in the plan, and is flagged forward for Plan 45-02. The Rule 3 fix is environment-local and does not touch the repository.

## Issues Encountered

None beyond the two deviations documented above.

## User Setup Required

None — no external service configuration required. The package-legitimacy checkpoint (Task 2) required human review, not setup, and was already resolved via the coordinator's relayed "approved" response.

## Next Phase Readiness

- The `docs/source/changelog.rst` ↔ `CHANGELOG.md` delegation mechanism is proven end-to-end on real builds — Plan 45-02 (also DOC-12) can now proceed with its own share: the `CHANGELOG.md` content edits (D-03 backfill `## [0.4.4]`, D-04 merge the duplicate `## [Unreleased]`, D-05 the emoji removal) and correcting the retained framing sections' *content* (D-06), which must also account for this plan's heading-level side effect (documented above and in the evidence file) when it verifies its own rendered output.
- **Important for Plan 45-02:** the `:start-line:` offset assumption in the original plan text ("Plan 45-02 pins CHANGELOG.md lines 1-7 as byte-invariant so this offset stays correct") no longer applies — this plan's shipped shape does not use `:start-line:` at all. Plan 45-02 does not need to preserve any specific line-1-through-7 byte range for that reason (though other reasons to keep the preamble stable may still apply).
- No blockers for Plan 45-03 (DOC-11) or Plan 45-04 (QUA-02, QUA-03) — neither touches `docs/source/changelog.rst`, `pyproject.toml`, `conf.py`, or `uv.lock`.

---
*Phase: 45-documentation-currency-carried-hygiene*
*Completed: 2026-08-10*
