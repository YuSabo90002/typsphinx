# Phase 45: Documentation Currency + Carried Hygiene - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-09
**Phase:** 45-documentation-currency-carried-hygiene
**Areas discussed:** DOC-12 mechanism (duplicate vs delegate), QUA-03 substance (defect already gone)

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| DOC-12 mechanism (duplicate vs delegate) | hand backfill 12 releases vs delegate to CHANGELOG.md; SC#2's "one-line addition" clause; companion sections; ja-translation fallout | ✓ |
| DOC-11 documentation surface | README only, or also the stale published docs pages | |
| QUA-03 substance (defect already gone) | verification-only vs adding the recurrence guard | ✓ |
| QUA-02 proof shape | how the warning-for-warning baseline is recorded | |

**Notes:** Presented alongside the scout measurements — including that `.planning/PROJECT.md` already
measures 34/34 with depth 0, so QUA-03 has no defect left to repair.

---

## DOC-12 mechanism (duplicate vs delegate)

### Q1 — the page mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| myst-parser include of CHANGELOG.md (recommended) | framing sections + `.. include:: ../../CHANGELOG.md :parser: …`; drift structurally impossible; Phase 46 adds zero lines; costs one `docs`-extra dependency and a docs-pdf render check | ✓ (after a detour) |
| Manual backfill | transcribe 12 releases into rST; zero toolchain change; the drift channel stays open and Phase 46 edits two files in lockstep | |
| Link-out only | delete release history from the page; no dependency, no drift, but SC#2's "carries every release" would need renegotiating | |

**User's choice:** Initially free-text — *"CHANGELOG を rst にする方が筋が良いのではないか"* (converting
`CHANGELOG.md` itself to rST would be more principled). After the blast radius was measured and
reported, the user chose the myst-parser include: *"じゃあ myst-parser で include する案でいこう"*.

**Notes:** The measurement that turned the decision — `CHANGELOG.md` supplies the **GitHub Release
body** via `scripts/extract_changelog_section.py`, wired into `release.yml` at two sites and covered
by `tests/test_changelog_extraction.py`; GitHub renders release bodies as Markdown, so an rST body
degrades to raw text. Compounding it, REL-04 is the one open requirement carried from v0.7.0 and has
never run green end to end, and Phase 46 is meant to be its first clean run.

### Q2 — the missing 0.4.4 section

| Option | Description | Selected |
|--------|-------------|----------|
| Reconstruct and add to CHANGELOG.md (recommended) | rebuild from the 148 commits in `v0.4.3..v0.4.4` and the GitHub Release; add the `[0.4.4]:` link line; satisfies SC#2 literally | ✓ |
| One-line gap note | record that no entry was written at release time and point at the tag; minimal work, keeps continuity | |
| Out of Phase 45 scope | file a separate todo; SC#2 would need a caveat | |

**Notes:** Discovered mid-discussion — `v0.4.4` is tagged and published but absent from `CHANGELOG.md`
entirely. This reconciles ROADMAP SC#2's "12 missing" against the DOC-12 todo's list of 11.

### Q3 — the duplicate `## [Unreleased]`

| Option | Description | Selected |
|--------|-------------|----------|
| Merge into the single top-of-file one (recommended) | fold line 911's "Planned for Future Releases" into line 8's `[Unreleased]`; clears the duplicate-section warning | ✓ |
| Exclude via include options | `:start-after:` etc.; leaves CHANGELOG.md untouched but makes the include range depend on file content | |
| Publish as-is | accept the duplicate warning; docs builds do not use `-W` | |

### Q4 — the stale companion sections

| Option | Description | Selected |
|--------|-------------|----------|
| Delete Development Status, correct the other two (recommended) | Development Status is a per-release hand-update site — the same drift channel D-01 closes; Migration Guides gains 0.6.x/0.7.0 entries; Release Process is restated against `release.yml` | ✓ |
| Correct all three | maximum information, one hand-update site retained | |
| Leave all three to a todo | keeps phase scope minimal | |

### Q5 — the 25 `✅` in the docs PDF

| Option | Description | Selected |
|--------|-------------|----------|
| Remove them from CHANGELOG.md (recommended) | the "Requirement N" prose already conveys completion; PDF and GitHub both stay clean | ✓ |
| Accept tofu | treat CHANGELOG.md as an untouchable historical record | |
| Measure first, decide at plan time | build docs-pdf and judge from the render | |

**Notes:** Neither typst-py's embedded fonts nor RTD's `fonts-noto-cjk` covers emoji, and Typst's font
fallback is silent — the build would report success while rendering tofu.

---

## QUA-03 substance (defect already gone)

### Q1 — what the phase delivers

| Option | Description | Selected |
|--------|-------------|----------|
| Verification + a recurrence guard in pytest (recommended) | the todo's step 3; a `test_no_stale_github_io_links.py`-shaped module pinning PROJECT.md's comment depth at 0 | |
| Verification only | record the whole-file scan as evidence and close; no code added; the drift channel stays open | ✓ |
| Guard outside pytest | pre-commit hook or a GSD-side check; cleaner separation, one new execution path | |

**Notes:** The user declined the recommendation. Additional measurement offered before the choice: a
naive `<!--`/`-->` count over all 867 `.planning/**/*.md` files flags 16 files, and its most notable
false positives are `REQUIREMENTS.md:141` and `ROADMAP.md:731` — backticked `` `<!--` `` in prose
describing QUA-03 itself — so a guard would have had to solve the same self-reference problem
`test_no_stale_github_io_links.py` solved by splitting a literal.

### Q2 — how SC#4's already-true state is recorded

| Option | Description | Selected |
|--------|-------------|----------|
| Identify the commit that closed it (recommended) | bisect `279aea5..HEAD`; distinguishes a deliberate fix from an incidental closure, which is what justifies skipping the guard | ✓ |
| Record the HEAD measurement only | runnable proof of depth 0; satisfies SC#4's wording with minimal work | |

---

## Claude's Discretion

Two areas the user chose not to discuss. Both are recorded in CONTEXT.md `<decisions>` §Claude's
Discretion with the measurements behind them.

- **DOC-11's documentation surface.** Default set during the discussion and accepted by the user in
  the closing turn: README Quick Start + `README.md:203` + `docs/source/quickstart.rst` +
  `docs/source/user_guide/configuration.rst`. Driven by the measurement that two of those sites are
  now *actively false* rather than merely incomplete — `README.md:203` says `typst_documents` is
  "required for PDF output", and `quickstart.rst` sends readers to `build/pdf/index.pdf`.
  `templates.rst` stays untouched (Phase 45.1).
- **QUA-02's refactor shape and how identity is proven.** SC#3 forbids any change to warning output,
  so the two rejection reasons must not be distinguished in the message wording; the `caplog`
  assertion pinning `repr(value)` must survive. Baseline-recording mechanism left open.

## Deferred Ideas

- A `.planning/` comment-balance guard (the QUA-03 todo's step 3) — declined; design constraint
  recorded in CONTEXT.md D-09 in case the channel reopens.
- `docs/source/user_guide/templates.rst`'s custom-template parameter contract — Phase 45.1 / DOC-13.
- The `## [0.7.1]` CHANGELOG entry and its two user-visible callouts — Phase 46.
- Regenerating the `ja` catalogs for newly-surfaced changelog content — lives in the
  `typsphinx-doc-translations` repository, outside this repo's phase scope.
