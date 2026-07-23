# Phase 27: Docs 実測整合 — Orphan Delete + Phantom Config Names - Context

**Gathered:** 2026-07-24
**Status:** Ready for planning
**Mode:** `--auto` (decisions auto-selected; single pass — see logged rationale below)

<domain>
## Phase Boundary

Truth-align the user-facing docs so every documented `typst_*` name maps to a value
actually registered in `typsphinx/__init__.py`, delete the unreachable orphan config
doc, and collapse config documentation to ONE canonical place so it cannot re-drift.

Three surfaces, exactly:
1. **Delete** `docs/configuration.rst` (orphan, wrong package name `sphinxcontrib.typst`).
2. **Fix** `docs/source/user_guide/configuration.rst` phantom names → registered names / working `typst_elements`.
3. **Delete** the redundant "Available Configuration Values" `list-table` in
   `docs/source/api/index.rst` (+ follow its `docs/locale/ja/LC_MESSAGES/api/index.po`),
   keeping only the `See :doc:/user_guide/configuration` pointer.

This is docs-only. No config→output behavior changes → **GATE-01 does not apply**
(per ROADMAP). Honest bar = grep-zero / grep-cross-check proof + green docs build.
No `@preview` bump, no touching the 3-way version-sync surface, no runtime deps.
</domain>

<decisions>
## Implementation Decisions

### Registered config — source of truth (verified this session)
- **D-01:** The 11 registered `typst_*` values (`typsphinx/__init__.py:44-60`) are the
  ONLY legal names: `typst_documents`, `typst_template`, `typst_template_mapping`,
  `typst_use_mitex`, `typst_elements`, `typst_package`, `typst_package_imports`,
  `typst_template_function`, `typst_authors`, `typst_debug`, `typst_template_assets`.
  Any `typst_*` outside this set anywhere under `docs/source/` is phantom and must go.
- **D-02:** `typst_elements` accepts EXACTLY two keys per the CONF-04 allowlist
  (`template_engine.py:55-56`): `papersize` (string, e.g. `"a4"`/`"us-letter"`) and
  `fontsize` (raw length, e.g. `"20pt"`). These are the *real* mirror of the phantom
  `typst_papersize`/`typst_fontsize` — the rewrite target, not a new phantom.

### DOC-06 — orphan delete (`docs/configuration.rst`)
- **D-03:** `git rm docs/configuration.rst`. It is a **true orphan**: the root `docs/`
  directory has **no `conf.py`** (verified) — it is a legacy/dead tree; the live Sphinx
  project is `docs/source/`. Nothing Sphinx builds references it → SC#1 "no live
  toctree/xref remaining" is satisfied by deletion alone.
- **D-04:** Actual size is **489 lines**, not the 526 the ROADMAP/REQUIREMENTS quote
  (stale figure — don't gate on it). The file uses the wrong package name
  `sphinxcontrib.typst` throughout (lines 20, 299, 449), so its content is actively
  wrong, not merely stale.
- **D-05:** "No unique useful content lost" (SC#1) = a targeted salvage-CHECK, not a
  content migration. Executor diffs the orphan's sections against the canonical
  `docs/source/user_guide/configuration.rst`; migrate a section ONLY if it is both
  genuinely unique AND still correct after the `sphinxcontrib.typst`→`typsphinx` rename.
  Default expectation: salvage nothing (superseded + wrong package name). Do NOT bulk-copy
  489 lines back in — that re-introduces the drift this phase removes.

### DOC-07 surface A — `docs/source/user_guide/configuration.rst`
- **D-06:** Codly section (lines 144-160): `typst_use_codly` / `typst_code_line_numbers`
  are unregistered → **remove both examples**. Do NOT invent a factual "codly is applied
  automatically" note unless it can be stated without documenting unverified behavior;
  minimal-faithful default = delete the phantom-knob examples. Net requirement: neither
  name survives anywhere in the file.
- **D-07:** Author "Simple Format" (line 170) `typst_author = ("John Doe", "Jane Smith")`
  is phantom AND type-invalid as `typst_authors` (which is dict-only). DOC-07's
  "`typst_author` → `typst_authors`" rename cannot be a literal token swap — a tuple is
  not a valid `typst_authors`. Decision: **delete the "Simple Format" tuple subsection**;
  keep the existing "Detailed Format" dict block as the single canonical author example.
  (Renaming the tuple in place would mint a *new* phantom.)
- **D-08:** Paper-size section (lines 192-200): rewrite the top-level phantoms into one
  working block — `typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}` —
  exactly per SC#2, using the D-02 verified keys.
- **D-09:** "Complete Example" (lines 245-246): drop the two phantom codly lines; KEEP
  `typst_use_mitex = True` (real). If a papersize/fontsize demo belongs in the complete
  example, express it as `typst_elements` too.

### DOC-07 surface B — `docs/source/api/index.rst` + `.po`
- **D-10:** **Delete the entire `list-table`** (lines 45-84, incl. the
  "Available Configuration Values" heading). Keep the `Configuration` heading + intro
  (lines 40-43) and the `See :doc:/user_guide/configuration` pointer (line 86). Config
  now lives in ONE canonical place (user_guide) → structurally prevents re-drift.
- **D-11:** `docs/locale/ja/LC_MESSAGES/api/index.po` must follow so the multilang build
  stays green (SC#5). Preferred mechanism = regenerate via the project's
  `docs-multilang` / sphinx-intl toolchain rather than hand-deleting msgids, to avoid
  `.po`↔`.pot` drift. Planner picks the exact command; lock = build green, no orphaned
  msgids referencing the deleted table.

### Verification (all SCs)
- **D-12:** Proof bar: (a) grep-zero for every phantom name (`typst_author` [tuple form],
  `typst_use_codly`, `typst_code_line_numbers`, `typst_papersize`, `typst_fontsize`)
  across BOTH `user_guide/configuration.rst` and `api/index.rst`; (b) grep-cross-check
  that every surviving `typst_*` under `docs/source/` ∈ the D-01 registered set;
  (c) `sphinx-build` + `docs-multilang` green with no broken `:doc:`/`:ref:` from the
  api-table deletion; (d) full test suite green.

### ⚠ Deletion-guard warning for planner/executor (STANDING project constraint)
- **D-13:** This phase deletes a tracked file (`docs/configuration.rst`) and removes
  content (api list-table + `.po` msgids). The `worktree.cleanup-wave` gate **blocks any
  branch containing deletions with no bypass** — this is the exact recurrence flagged for
  Phase 27. Plan for it: measure the deletion scope, then the deletion-bearing branch is
  **merged manually** after scope confirmation (do not expect the cleanup-wave gate to
  auto-pass). Worktree-isolated execution stays ON (standing mode); provision per-worktree
  (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` + `uv run`).

### Claude's Discretion
- Exact prose wording of the rewritten user_guide sections (D-06..D-09) and whether the
  "Complete Example" gains a `typst_elements` demo — planner/executor's call, within D-01/D-02.
- Exact `.po` regeneration command (D-11).

### Folded Todos
- **孤児の `docs/configuration.rst` を削除する** (`2026-07-22-delete-orphan-docs-configuration-rst.md`,
  score 0.9) — IS DOC-06; auto-closes on completion.
- **`user_guide/configuration.rst` が実在しない設定名 5 個を記載** (`2026-07-22-user-guide-configuration-phantom-config-names.md`,
  score 0.9) — IS DOC-07 surface A; auto-closes on completion.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase spec & requirements
- `.planning/ROADMAP.md` — Phase 27 section: 5 success criteria (SC#1–5) are the exact bar.
- `.planning/REQUIREMENTS.md` §DOC-06, §DOC-07 — the two requirements this phase closes.

### Config source of truth (the anti-phantom oracle)
- `typsphinx/__init__.py:44-60` — the 11 registered `add_config_value` calls. THE legal-name set.
- `typsphinx/template_engine.py:44-56` — CONF-04 `typst_elements` key allowlist
  (`papersize`=STRING, `fontsize`=RAW). Defines the D-08 rewrite target.
- `.planning/phases/26-typst-elements-papersize-fontsize-pass-through-dead-config-s/26-CONTEXT.md`
  — CONF-04 context (why `typst_elements` is the faithful mirror; Pitfall 11 prevention).

### Files edited/deleted by this phase
- `docs/configuration.rst` — DELETE (orphan, 489 lines, wrong package name).
- `docs/source/user_guide/configuration.rst` — canonical config doc; phantom fixes (D-06..D-09).
- `docs/source/api/index.rst` — delete list-table lines 45-84, keep pointer at line 86 (D-10).
- `docs/locale/ja/LC_MESSAGES/api/index.po` — follow the api-table deletion (D-11).
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `typst_elements` pass-through (CONF-04, shipped Phase 26) makes the paper-size rewrite
  (D-08) a *working* example rather than a delete — `template_engine.py:315-319` validates
  keys against the allowlist and raises on unknown keys, so the documented example is
  self-verifying against the code.

### Established Patterns
- Live Sphinx source is `docs/source/` with `docs/source/conf.py`; `docs/source/index.rst:43`
  toctrees `user_guide/configuration` (the canonical doc — NOT the orphan).
- Root `docs/*.rst` (`configuration.rst`, `usage.rst`, `installation.rst`, …) is a legacy
  dead tree with no `conf.py` — never built. This is the same orphan-cluster class as DOC-06.

### Integration Points
- api/index.rst → user_guide/configuration via `:doc:` pointer (line 86) is the single
  surviving link after D-10; must remain valid (SC#5).
- Deleting `docs/configuration.rst` leaves dangling `:doc:\`configuration\`` refs in the
  dead siblings `docs/usage.rst` (lines 554, 582, 601) and `docs/installation.rst` (line 213).
  Harmless (those files are never built), but noted as a deferred cluster cleanup below —
  NOT fixed here (out of DOC-06 scope; would touch non-scoped files).
</code_context>

<specifics>
## Specific Ideas

- SC#2's literal example is the target string: `typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}`.
- "ONE canonical place" = `docs/source/user_guide/configuration.rst`. api/index.rst becomes a pure pointer.
</specifics>

<deferred>
## Deferred Ideas

- **Legacy root-`docs/` dead-tree sweep** — `docs/usage.rst`, `docs/installation.rst`
  (and any other root `docs/*.rst`) are the same unreachable-orphan class as
  `docs/configuration.rst` and still cross-`:doc:`-reference it. Deleting the whole dead
  cluster is beyond DOC-06's single-file scope → its own future docs-cleanup phase.
  (Discovered this session; the root `docs/` has no `conf.py`.)

### Reviewed Todos (not folded)
- **ホスティング先を Read the Docs に変更** (`2026-07-21-move-documentation-hosting-to-read-the-docs.md`,
  score 0.9) — DEFERRED. Standing decision: RTD migration is planned ~2026-07-30 as its own
  effort; not part of this phantom/orphan pass.
- **README の github.io リンク 7 本が 404** (`2026-07-22-github-io-doc-links-404-missing-en-prefix.md`,
  score 0.9) — DEFERRED. Standing decision: the 404/`/en/`-prefix link fixes are folded into
  the RTD migration, not fixed piecemeal now.
- **`sphinx-build -b linkcheck` CI ジョブ追加** (`2026-07-22-add-sphinx-linkcheck-ci-job.md`,
  score 0.6) — DEFERRED. CI infra addition, out of this docs-content phase; revisit with RTD move.
- Lower-relevance matches (citation nodes, non-str docname TypeError, typing modernize) —
  unrelated subsystems; not this phase.
</deferred>

---

*Phase: 27-docs-orphan-delete-phantom-config-names*
*Context gathered: 2026-07-24*
