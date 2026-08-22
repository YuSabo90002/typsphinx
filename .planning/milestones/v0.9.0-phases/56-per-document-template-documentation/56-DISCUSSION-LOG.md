# Phase 56: Per-Document Template Documentation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-16
**Phase:** 56-per-document-template-documentation
**Areas discussed:** Registry documentation placement & element [4] naming; Error catalogue depth & verification

---

## Gray area selection

Four areas were offered. The owner selected two.

| Option | Description | Selected |
|--------|-------------|----------|
| Registry documentation placement & element [4] naming | Where `typst_document_templates` is documented; what element [4] is called; what happens to the 15 published five-element examples; whether `output_layout.rst` carries the `_template/<key>/` story | ✓ |
| Error catalogue depth & verification | How exhaustively the fail-loud errors are documented; whether doc↔code agreement is test-pinned | ✓ |
| Asset-example real-build proof shape (DOC-16) | New GATE-01 fixture vs. binding prose to an existing fixture vs. grep-only | |
| Migration guidance placement & history scope (DOC-17) | `configuration.rst` section vs. changelog-only; whether the sweep rewrites historical release notes | |

---

## Registry documentation placement & element [4] naming

### Q1 — Where does `typst_document_templates` live?

| Option | Description | Selected |
|--------|-------------|----------|
| `configuration.rst`, one subsection | Fifth subsection of "Template Configuration"; minimum surface; DOC-15 names only this file | ✓ |
| Split `configuration.rst` + `templates.rst` | Reference vs. task-shaped walkthrough; matches existing page roles but adds cross-page drift risk (45.1 CR-01 precedent) | |
| New `user_guide/per_document_templates.rst` | Puts the v0.9.0 headline feature at top level; but element [4] still needs a `configuration.rst` edit, so the two-place problem survives | |

**User's choice:** `configuration.rst` に 1 サブ節だけ
**Notes:** Recorded as D-01. `configuration.rst` grows 390 → ~470 lines.

### Q2 — Element [4] rename and the existing five-element examples

| Option | Description | Selected |
|--------|-------------|----------|
| Rename only; all 15 existing examples untouched | `"typst"` is always synthesized as the reserved key, so every published example is measurably still correct; SC#1 satisfied by one line | ✓ (Claude's recommendation, owner delegated) |
| Rename + drop element [4] from default-key examples | Removes the "why does every example say 'typst'?" question; ~12 sites of churn and a tuple-length mismatch against historical changelog entries | |
| Rename + rewrite `advanced.rst:258-259` with a non-default key | Ties the reference to a real usage example; but that section would gain a `charged-ieee` package dependency under a real-build gate | |

**User's choice:** おすすめ (delegated to Claude) → option 1
**Notes:** Recorded as D-02. The non-default-key worked example lives inside the new registry subsection only.

### Q3 — How far the layout rewrite goes

| Option | Description | Selected |
|--------|-------------|----------|
| `output_layout.rst` becomes the canonical layout page | Full `_template/<key>/` story, corrected file-count rule, and the `--root build/typst` note in its existing "Which File to Compile" section | ✓ (Claude's recommendation, owner delegated) |
| Minimal string-level corrections everywhere | Smallest diff; but separates the `--root` consequence from the page whose whole purpose is "which file do I compile" | |
| Layout in `output_layout.rst`, `--root` in `builders.rst` | Faithful to existing page roles; sends the reader between two pages | |

**User's choice:** おすすめ (delegated to Claude) → option 1
**Notes:** Recorded as D-03. Measured during discussion:
`test_output_layout_docs_gate.py::test_three_master_project_emits_ten_typ_files` was already updated
in Phase 54 to assert a nine-file root set plus `_template/typst/base.typ`, while
`output_layout.rst:159` still publishes "ten". The prose is provably behind the measured build in a
place no current assertion catches.

### Q4 — The registry subsection's central worked example

| Option | Description | Selected |
|--------|-------------|----------|
| `template` route, two masters, no network | Local files only, so a real-build gate over this example needs no Typst Universe fetch | ✓ (Claude's recommendation, owner delegated) |
| Both `template` and `package` routes side by side | Makes the xor rule visually obvious; a real-build gate would need network | |
| This repository's own `docs/source` config | Dogfooding; but leaves a gap if `docs/source/conf.py` is not actually migrated | |

**User's choice:** おすすめ (delegated to Claude) → option 1
**Notes:** Recorded as D-04. The `package` route is still shown, as a short schema-level example.

---

## Error catalogue depth & verification

Measured going in: nine distinct `ExtensionError` message shapes across `template_registry.py`
(`:303`, `:438`, `:513`, `:523`) and `builder.py` (`:950`, `:1312`, `:1992`, `:2002`, `:2174`), two
of which are I/O-caused rather than config-caused.

### Q1 — Catalogue granularity

| Option | Description | Selected |
|--------|-------------|----------|
| Condition → outcome table, seven config-caused shapes only | Leading clauses only, no verbatim aggregate bodies | |
| Verbatim quotation of every message | Matches `output_layout.rst:127-140`'s existing style and lets users search the error text; large, and brittle against wording tweaks | |
| Seven config-caused shapes in the table + I/O shapes noted separately | Satisfies SC#1's "every fail-loud error a user can hit" literally, and the note tells the reader whether to fix `conf.py` or look at their filesystem | ✓ (Claude's recommendation, owner delegated) |

**User's choice:** おすすめ (delegated to Claude) → option 3
**Notes:** Recorded as D-05. Rows quote the identifying leading clause only, not the aggregated body.

### Q2 — What pins doc↔code agreement

| Option | Description | Selected |
|--------|-------------|----------|
| Two-way leading-clause gate test | Run-time discovery, no `typst-py`, no subprocess, never skips; catches a new `raise` that was not documented | ✓ (Claude's recommendation, owner delegated) |
| Real-build reproduction of each error | Strongest evidence, but duplicates `test_registry_prewrite_validation_gate.py` and adds seven-plus subprocess builds to CI | |
| Eyeball review only | Smallest phase; but this milestone exists because eyeball review already failed twice (DOC-13, DOC-14) | |

**User's choice:** おすすめ (delegated to Claude) → option 1
**Notes:** Recorded as D-06.

### Q3 — CONF-18's key-shape sub-cases

| Option | Description | Selected |
|--------|-------------|----------|
| Separate "registry key naming rules" subsection | These are rules for writing a key, not symptoms for looking one up; error-table row links to it | ✓ (Claude's recommendation, owner delegated) |
| Expand the error table to one row per condition | Users look up their own symptom directly; ~15 rows, and the leading-clause gate loses its 1:1 row↔shape mapping | |
| One aggregate = one row, sub-cases in the row's prose | No extra heading; a reader naming a key must read the error table to find the rules | |

**User's choice:** おすすめ (delegated to Claude) → option 1
**Notes:** Recorded as D-07.

### Q4 — Where the `templates_path` collision refusal is documented

| Option | Description | Selected |
|--------|-------------|----------|
| Both "Custom Template File" and the error table | Prevents at placement time and is findable after the fact | ✓ (Claude's recommendation, owner delegated) |
| Error table only | Phase 54.1 already purged `_templates/` recommendations, so the preventive note may be redundant | |
| "Custom Template File" only | The refusal is a consequence of a placement rule; but the catalogue would then not cover every error a user can hit | |

**User's choice:** おすすめ (delegated to Claude) → option 1
**Notes:** Recorded as D-08. Either placement must satisfy
`test_docs_template_layout_gate.py::test_every_surviving_jinja_dir_mention_names_templates_path` —
a surviving bare `_templates` token must name `templates_path` on the same line.

---

## Claude's Discretion

The owner was offered the two unselected gray areas again before CONTEXT.md was written and chose
to leave them to Claude with recommendations recorded:

- **DOC-16 — what "exercised by a real build" means.** Recommendation: extend
  `tests/fixtures/user_template_relative_asset_gate/` with a `refs.bib`, and bind both published
  asset examples (`templates.rst:79-118`, `advanced.rst:122-131`) to that fixture's measured
  destination paths. One fixture, no new network dependency.
- **DOC-17 — where migration guidance is published, and how far the sweep reaches into history.**
  Recommendation: a new "Removed configuration values" subsection in `configuration.rst`, bound by a
  test to `typsphinx/removed_config.py`'s `REMOVED_CONFIG_VALUES` dict; historical release notes
  (`changelog.rst:16,39,59,63` and pre-0.9.0 `CHANGELOG.md` entries) are **not** rewritten.
- Section titles, table headers, RST directive choices, test file naming and placement, and whether
  the `examples/**/README.md` corrections share a plan with the `user_guide/` sweep.

## Deferred Ideas

- Phase 57 — CHANGELOG entries for `typst_document_templates` itself, the `_template.typ` →
  `_template/<key>/` layout change, and the `typst_template_assets` removal (WR-02).
- Later milestone — a runnable `examples/` project demonstrating the registry.
- Later milestone — a `sphinx-build -b linkcheck` CI job.
- Later milestone — a published caveat about stale bundle files on incremental rebuilds (Phase 54
  D-01 accepts the behaviour; whether to document it is a separate question).
