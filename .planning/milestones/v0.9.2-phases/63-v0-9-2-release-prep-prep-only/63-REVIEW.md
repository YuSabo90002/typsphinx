---
phase: 63-v0-9-2-release-prep-prep-only
reviewed: 2026-08-30T14:05:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - CHANGELOG.md
  - README.md
  - pyproject.toml
  - tests/test_changelog_page_gate.py
  - uv.lock
findings:
  critical: 0
  warning: 0
  info: 1
  total: 1
status: issues_found
---

# Phase 63: Code Review Report (Re-Review After Gap Closure)

**Reviewed:** 2026-08-30T14:05:00Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found (Info only — no Critical or Warning findings)

## Summary

This is a re-review of the corrected tree after plans 63-05/63-06 closed the prior run's CR-01
(the false "confined to `typsphinx/translator.py`" claim in the `## [0.9.2]` intro paragraph).
Every claim in the `## [0.9.2]` section, and the version consistency across `pyproject.toml` /
`uv.lock` / `README.md`, was independently re-measured rather than assumed fixed:

- **CR-01 does not recur.** The blanket file-scope claim is gone from the intro paragraph
  (`CHANGELOG.md:17-24`). The narrower claim now lives only on the IMG-08/09/10 `### Fixed` bullet
  ("This fix is confined to `typsphinx/translator.py`; no other file under `typsphinx/` was
  touched for it.", `CHANGELOG.md:35-36`). I measured `git diff --stat e3399825..dd385436 --
  typsphinx/` myself: `typsphinx/translator.py | 23 +++++++++++++++++++++++`, one file, 23
  insertions, 0 deletions — the claim holds exactly.
- The intro's own broader claim — "the Windows-shaped path-handling hardening ... together with a
  separate compile-blocking defect" spans PATH-01, IMG-04–07, MSG-02–05, and IMG-08–10 — makes no
  single-file assertion, so it is not falsified by `git diff --stat v0.9.0..HEAD -- typsphinx/`
  showing five touched files (`builder.py`, `pathfmt.py`, `template_registry.py`,
  `translator.py`, `writer.py`). That five-file spread is expected and correctly unclaimed-away.
- **The `### Verified` "zero new runtime or dev dependencies ... the only change to
  `pyproject.toml` and `uv.lock` is the version literal itself" claim is true.**
  `git diff v0.9.0..HEAD -- pyproject.toml` shows exactly one changed line (`version = "0.9.0"` →
  `"0.9.2"`); `git diff v0.9.0..HEAD -- uv.lock` shows exactly one changed line, `typsphinx`'s own
  recorded `version` field. No dependency line moved in either file.
- **The four-surface `@preview` version-sync claim is true.** `git diff v0.9.0..HEAD` over
  `writer.py`, `template_engine.py`, `templates/base.typ`, and `examples/**/*.typ` shows zero
  `@preview` line changes.
- **The PATH-01 and IMG-04/IMG-06 technical claims match the actual code.** `typsphinx/builder.py`
  carries `# PATH-01 (Phase 59): both the isabs/drive-qualified terms now read [the normalized
  string]` at the exact site the CHANGELOG describes (`_escapes_outdir()`), and
  `_build_relocation_key()`'s docstring literally reads "IMG-04 (normalize) + IMG-06 (bound)".
  `MAX_PATH_COMPONENT_BYTES = 255` backs the "bounded to 255 UTF-8 bytes" claim.
- **Version consistency across `pyproject.toml` / `uv.lock` / `README.md` holds.**
  `pyproject.toml`'s `version = "0.9.2"`, `uv.lock`'s `typsphinx` package record
  `version = "0.9.2"`, and README's closing "Status: Stable (v0.9.2)" line all agree.
- **The CHANGELOG's bottom link block is release-shaped and consistent.** `[0.9.2]:
  .../releases/tag/v0.9.2` and `[Unreleased]: .../compare/v0.9.2...HEAD` both point at the new
  version, matching the pattern every prior release used at its own prep time (the tag itself
  need not exist yet at this prep-only phase — it is cut by the actual release workflow).
- **The changelog page gate is non-vacuous and still passes.** `RELEASE_VERSIONS` in
  `tests/test_changelog_page_gate.py` includes `"0.9.2"`, so `TestChangelogPageContentCoverage`
  and `TestChangelogIncludeCompilesToPdf` do exercise the new release string once their build
  dependencies (`myst-parser`, `typst-py`) are present. I ran the one class that always executes
  in CI (`TestPublishedChangelogPageDelegates`) directly: 2/2 pass on the current tree.
- **IN-01 (declined, not re-raised as an escalation).** The `RELEASE_VERSIONS` tuple's preceding
  comment still says "The 16 releases the published page was frozen without (0.4.4 through 0.9.2,
  inclusive)" while the tuple itself actually starts at `"0.4.1"`, not `"0.4.4"` — a pre-existing
  off-by-three-releases inaccuracy in the comment's stated range versus its own tuple contents,
  unrelated to this phase's edits. Per the phase context and owner decision D-24
  (`63-CONTEXT.md`), this was already raised in the prior review round and explicitly declined —
  `tests/test_changelog_page_gate.py` was deliberately left untouched in this closure. Recording
  it below at Info severity per the task instructions, not escalating it.

No Critical or Warning findings. All file-scope and behavioral claims added in this phase's
`CHANGELOG.md` edit were independently re-derived from the git history and the current source,
not merely re-read.

## Info

### IN-01: `RELEASE_VERSIONS` comment's stated range does not match its own tuple (declined, D-24)

**File:** `tests/test_changelog_page_gate.py:47-49`
**Issue:** The comment above `RELEASE_VERSIONS` reads "The 16 releases the published page was
frozen without (0.4.4 through 0.9.2, inclusive)", but the tuple's first three entries are
`"0.4.1"`, `"0.4.2"`, `"0.4.3"` — i.e. the actual range is 0.4.1 through 0.9.2, not 0.4.4 through
0.9.2. This is cosmetic (the tuple itself, which is what the test logic actually consumes, is
correct and does include `"0.9.2"`) but a future reader skimming only the comment would
undercount the covered releases by three.
**Fix:** Not required this phase — this finding was raised in the prior review round and the
project owner explicitly declined it via decision D-24 (`63-CONTEXT.md`), deliberately leaving
`tests/test_changelog_page_gate.py` unedited in this closure. If ever addressed, correct the
comment to "0.4.1 through 0.9.2, inclusive" (or equivalent) to match the tuple's actual first
element.

---

_Reviewed: 2026-08-30T14:05:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
