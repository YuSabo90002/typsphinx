# Phase 45 Plan 02 — Post-Change Docs-Build Clean Delta

Records both real docs builds against the final tree after Task 1 (CHANGELOG.md content backfill:
D-03/D-04/D-05) and Task 2 (`docs/source/changelog.rst` framing corrections: D-06), measured the
same way plan 45-01's pre-phase baseline was measured, for a direct delta.

- post_change_sha: 66304e2ead20689ba4311fd87225f5e2c8198d7f (HEAD after Task 2's commit)
- baseline_sha (from 45-GATE-EVIDENCE-01-docs-build-baseline.md): 8c74b853f81eaac0c9233a9628928528d16f2d18
- html_warning_count: 1
- pdf_warning_count: 1
- changelog_attributable_warning_count: 0

Delta against the baseline (`html_warning_count=1`, `pdf_warning_count=1`,
`changelog_attributable_warning_count=0`): all three are unchanged — delta 0, delta 0, delta 0.

## Method

Identical method to the baseline capture: real `sphinx-build` subprocess runs (no `-W`, no `-q`,
no `-n`) against a **fresh** output directory each time (a reused/incremental output directory
under-reports warnings — Sphinx's incremental rebuild skips unchanged source files and their
docutils/myst-parser warnings do not re-fire; this was hit once during this evidence capture and
corrected by rebuilding into a clean `<scratch>` directory before recording the numbers below).

```
uv run python -m sphinx -b html docs/source <fresh-scratch>/html
uv run python -m sphinx -b typstpdf docs/source <fresh-scratch>/pdf
```

Counts are the number of lines matching the literal string `WARNING:` in each build's combined
stdout+stderr output — not docutils' `ERROR/3` console-report notation, and not Sphinx's own
end-of-build tally (`build succeeded, 3 warnings.`), which folds in the two docutils
`ERROR`-severity lines below as well. The changelog-attributable count is the subset of `WARNING:`
lines whose text mentions `changelog` (case-sensitive, matching plan 45-02's own `<verify>`
scripts).

## HTML build

Exit code: 0 (`sphinx-build -b html docs/source <scratch>/html`, fresh output directory, all 13
source files rebuilt)

Sphinx's own summary line: `build succeeded, 3 warnings.` (this tally includes the two docutils
`ERROR/3` messages emitted through the same warning stream — see below — plus the one line
matching literal `WARNING:`; identical shape to the pre-phase baseline.)

Verbatim `WARNING:` line (identical to the pre-phase baseline):

```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af1ec3bc15b7dddea/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:15: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

The same two `ERROR:`-severity docutils lines the baseline recorded also appear (not counted in
`html_warning_count` for the same literal-string reason):

```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af1ec3bc15b7dddea/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:6: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af1ec3bc15b7dddea/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:20: ERROR: Unexpected indentation. [docutils]
```

No line in the combined output mentions `changelog` and also contains `WARNING`.

## typstpdf build

Exit code: 0 (`sphinx-build -b typstpdf docs/source <scratch>/pdf`, fresh output directory, all 13
source files rebuilt)

Sphinx's own summary line: `build succeeded, 3 warnings.` (identical tally shape to the baseline —
1 literal `WARNING:` line + 2 `ERROR:`-severity docutils lines routed through the same warning
stream).

Verbatim `WARNING:` line (identical to the pre-phase baseline and to this run's own HTML build):

```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-af1ec3bc15b7dddea/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:15: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

`Generated PDF: <scratch>/pdf/typsphinx.pdf` — build produced a compiled PDF successfully.

## Delta against the baseline: every WARNING line new since the baseline

**None.** The single `WARNING:` line present in both builds above is byte-identical to the one
`45-GATE-EVIDENCE-01-docs-build-baseline.md` recorded (the pre-existing, out-of-fence
`visit_toctree` docstring defect in `typsphinx/translator.py` — unrelated to DOC-12, not touched
by this plan). No new `WARNING:` line appears in either build. Both totals (`html_warning_count`,
`pdf_warning_count`) are unchanged from baseline (1 and 1), and `changelog_attributable_warning_count`
stays at 0 both before and after — this plan's own bar
(`changelog_attributable_warning_count == 0` post-change, neither total exceeding baseline) is met
exactly, with headroom (all three deltas are 0, not merely non-positive).

## Carried consequences

1. **Japanese (`ja`) site translations.** Every line this phase's `CHANGELOG.md` content edits
   (the `## [0.4.4]` backfill, the merged `Unreleased` body, the reworded Requirements-Status
   lines) and `docs/source/changelog.rst` framing edits (the two new Migration Guides subsections,
   the restated Release Process) newly surface on the published changelog page renders
   **untranslated on the `ja` site** until the separate `typsphinx-doc-translations` repository's
   gettext catalogs are regenerated. This is the same carried consequence plan 45-01 recorded for
   the delegation mechanism itself, now extended to this plan's content. Out of this repository's
   scope; flag at the milestone close.

2. **Phase 46's `0.7.1` one-line-addition property, verified by diff inspection.** After Task 1
   and Task 2, `docs/source/changelog.rst` is 135 lines: the `.. include:: ../../CHANGELOG.md`
   directive (2 lines) followed exclusively by evergreen framing sections (`Migration Guides`,
   `Deprecation Policy`, `Upcoming Features`, `Versioning`, `Release Process`, `See Also`) — no
   release-specific content, no per-version heading, no current-release marker anywhere on the
   page (also pinned mechanically by
   `tests/test_changelog_page_gate.py::TestPublishedChangelogPageDelegates`). Adding a
   `## [0.7.1]` section to `CHANGELOG.md` alone, with no edit to `docs/source/changelog.rst`,
   is sufficient for the new release to appear on the published page — confirmed by inspection,
   not merely assumed. Phase 46 owns making that one edit; this plan's own `<prohibitions>`
   explicitly forbid adding it here.

## Environment note (unrelated to the docs content, recorded for completeness)

Same NixOS-sandbox `ruff` hazard plan 45-01 recorded for its own worktree: this worktree's
`uv sync`-installed `.venv/bin/ruff` is a generic-linux ELF the NixOS host cannot execute directly
(`Could not start dynamically linked executable`). Resolved identically: symlinked a Nix-store
`ruff` (`nix-shell -p ruff`, resolved version `0.15.14`, inside this repo's `ruff>=0.15,<0.16`
pin) over `.venv/bin/ruff`. `uv run ruff check .` then passed clean. Local, gitignored `.venv/`
change only — no repository file touched.
