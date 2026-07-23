# Roadmap: typsphinx

## Milestones

- ✅ **v0.4.4 — CI-repair + modernize** — Phases 1–5 (shipped 2026-07-05) → [archive](milestones/v0.4.4-ROADMAP.md)
- ✅ **v0.5.0 — forward-ecosystem** — Phases 6–10 + 8.1 (shipped 2026-07-11) → [archive](milestones/v0.5.0-ROADMAP.md)
- ✅ **v0.6.0 — real-world robustness** — Phases 11–15 (shipped 2026-07-13) → [archive](milestones/v0.6.0-ROADMAP.md)
- ✅ **v0.6.1 — rendering fidelity** — Phases 16–18 (shipped 2026-07-19) → [archive](milestones/v0.6.1-ROADMAP.md)
- ✅ **v0.6.2 — rendering fidelity round 2** — Phases 19–23 (+22.1–22.4) (shipped 2026-07-23) → [archive](milestones/v0.6.2-ROADMAP.md)
- 🚧 **v0.6.3 — config & docs 実測整合 + captioned tables** — Phases 24–28 (in progress)

## Phases

**Phase Numbering:**

- Integer phases (24, 25, 26): Planned milestone work
- Decimal phases (24.1, 24.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order. Numbering is
**continuous across milestones** — each milestone continues from the prior one's last phase
(never resets to 1). v0.6.3 continues from v0.6.2's last phase (23), so it starts at Phase 24.

<details>
<summary>✅ v0.4.4 — CI-repair + modernize (Phases 1–5) — SHIPPED 2026-07-05</summary>

Restored a fully green CI pipeline on `main` by pinning the runtime dependency graph back to a
known-good, reproducible combination, then modernized the Python floor (3.10–3.13) and dev tooling
and installed durability guardrails so the drift cannot silently recur. Full phase detail, success
criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.4.4-ROADMAP.md`](milestones/v0.4.4-ROADMAP.md).

- [x] Phase 1: Pin Runtime Dependencies to Known-Good (2/2 plans) — completed 2026-07-04
- [x] Phase 2: Verify the Green Baseline (3/3 plans) — completed 2026-07-04
- [x] Phase 3: Modernize Python Floor (3.10–3.13) (2/2 plans) — completed 2026-07-04
- [x] Phase 4: Refresh Dev Tooling (4/4 plans) — completed 2026-07-04
- [x] Phase 5: Durability Guardrails (4/4 plans) — completed 2026-07-05

</details>

<details>
<summary>✅ v0.5.0 — forward-ecosystem (Phases 6–10 + 8.1) — SHIPPED 2026-07-11</summary>

Ported typsphinx forward from the v0.4.4 known-good pins to the current ecosystem — Sphinx 9.1,
docutils 0.22, typst 0.15, Python 3.12–3.13 — bumping the four bundled `@preview` packages in
lockstep to compile cleanly (empirically closing the `unknown variable: kai` break), modernizing the
soft-deprecated docutils/Sphinx API, fixing a long-latent admonition markup/code-mode render bug,
adding a `typst compile` smoke gate, keeping the full 3-OS × Python 3.12–3.13 CI matrix green, and
releasing v0.5.0 to PyPI. Latest-only, no compatibility range. Full phase detail, success criteria,
decisions, and tech-debt notes are preserved in
[`milestones/v0.5.0-ROADMAP.md`](milestones/v0.5.0-ROADMAP.md).

- [x] Phase 6: Raise Runtime Pins + Python Floor (1/1 plan) — completed 2026-07-09
- [x] Phase 7: Bump @preview Packages + typst 0.15 (kai fix) (1/1 plan) — completed 2026-07-11
- [x] Phase 8: API & Test Compatibility (Sphinx 9 / docutils 0.22) (3/3 plans) — completed 2026-07-11
- [x] Phase 8.1: Admonition Rendering Fix (INSERTED) (4/4 plans) — completed 2026-07-11
- [x] Phase 9: Green CI Matrix + Smoke Test + Guardrails (2/2 plans) — completed 2026-07-11
- [x] Phase 10: Version-String Fix + v0.5.0 Release (2/2 plans) — completed 2026-07-11

</details>

<details>
<summary>✅ v0.6.0 — real-world robustness (Phases 11–15) — SHIPPED 2026-07-13</summary>

Compiled a large real-world documentation set (Sphinx's own `doc/` tree) end-to-end through the
`typstpdf` builder with no fatal Typst errors (GATE-02: ~14.4 MiB PDF, 0 errors), and added correct,
compilable rendering for the most-frequent previously-dropped docutils/Sphinx nodes. Driven by
Issue #114: fixed the two fatal figure/image bugs first (px→pt length conversion + `:target:`/caption
buffer-swap), stood up a standing real-`typst.compile()` acceptance gate (GATE-01) extended by every
node-handler phase, then landed the high-frequency handlers (versionmodified, `refid` cross-refs,
autodoc `desc_*`, footnotes via a doctree pre-pass, transition/topic/line_block/glossary/
tabular_col_spec/abbr) and a graphviz/inheritance_diagram graceful-degrade net. Zero new runtime
dependencies; the 3-way `@preview` version-sync surface untouched. Full phase detail, success
criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.6.0-ROADMAP.md`](milestones/v0.6.0-ROADMAP.md).

- [x] Phase 11: Issue #114 Fatal Fixes + Graceful-Degrade Net (3/3 plans) — completed 2026-07-12
- [x] Phase 12: High-Volume Independent Node Handlers (4/4 plans) — completed 2026-07-12
- [x] Phase 13: Shared Dispatch-Point Changes (topic + line blocks) (3/3 plans) — completed 2026-07-12
- [x] Phase 14: Footnotes (doctree pre-pass) (2/2 plans) — completed 2026-07-12
- [x] Phase 15: Full-Corpus Validation (3/3 plans) — completed 2026-07-12

</details>

<details>
<summary>✅ v0.6.1 — rendering fidelity (Phases 16–18) — SHIPPED 2026-07-19</summary>

Moved `typstpdf` output from "compiles fatal-free" (achieved in v0.6.0) to "renders faithfully":
implemented the last two silently-dropped nodes (`todo_node` → gentle-clues `task()` box gated on
`todo_include_todos`; `manpage` → italic literal page text via `visit_emphasis` delegation),
generalized v0.6.0's `visit_image`-local px→pt fix into one shared `_convert_length_to_typst` helper
reused at every length-bearing figure/table site (LEN-01), then ran a full 151/151-docname
human-assisted visual audit of the Sphinx v9.1.0 `doc/` corpus PDF against its `-b html` baseline —
15 systemic findings catalogued, human-confirmed (14 accepted / 1 rejected), the sole high-severity
finding (F12 wide-table glyph collision + right-margin clip) fixed via fr-weighted `columns:` from
docutils colwidth + in-table U+200B break injection (FID-01a) with a real-compile regression fixture,
and the milestone closed on the full ~684-page corpus regression gate (fatal-free, `unknown_visit`
catalogue empty). Zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched.
The 13 medium/low audit findings are recorded as a Future-Requirements pointer. Full phase detail,
success criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.6.1-ROADMAP.md`](milestones/v0.6.1-ROADMAP.md).

- [x] Phase 16: Silent-Drop Node Handlers + Length-Converter Refactor (3/3 plans) — completed 2026-07-16
- [x] Phase 17: Rendering-Fidelity Audit (4/4 plans) — completed 2026-07-19
- [x] Phase 18: Fidelity Fixes + Regression-Gate Close (2/2 plans) — completed 2026-07-19

</details>

<details>
<summary>✅ v0.6.2 — rendering fidelity round 2 (Phases 19–23, +22.1–22.4) — SHIPPED 2026-07-23</summary>

Resolved the 13 medium/low silent mis-render findings the v0.6.1 audit left open, delivered as one
coherent series of `translator.py` fixes grouped by root cause (clusters A–F) rather than 13 unrelated
tickets — block separation (FID-02..FID-06), intra-signature token spacing (FID-07..FID-09), and the
residual inline-literal overflow / paragraph reflow / codly-wrapper leak / meaning-bearing inline
styling findings (FID-10..FID-14) — each pinned by a fail-pre-fix real-`typst.compile()` GATE-01
fixture. Alongside the translator series, five inserted builder/config/docs phases: Issue #117
`typstpdf` target-name PDF fix (PDF-01), nested-master compile-root alignment (PDF-02), a dead-config
sweep that deleted `typst_output_dir`/`typst_author_params` and repaired the broken `typst_package`
Typst-Universe path end-to-end (CONF-01..CONF-03), builder-warning hardening so a missing/malformed
master fails loudly instead of a silent successful build (WR-01/WR-02), and a full-text README/CLAUDE.md
accuracy pass that removed unverifiable numeric claims rather than re-measuring them (DOC-01..DOC-05).
Closed on the full ~684-page corpus regression gate (fatal-free, valid `%PDF`, `unknown_visit`
catalogue empty). Zero new runtime dependencies; the 3-way `@preview` version-sync surface untouched.
Closeout `override_closeout` — a single non-blocking pytest-xdist backstop item on Phase 22.3 abstained
to human per the honest-verifier rule (all ROADMAP SCs independently verified with direct evidence).
Full phase detail, success criteria, decisions, and tech-debt notes are preserved in
[`milestones/v0.6.2-ROADMAP.md`](milestones/v0.6.2-ROADMAP.md).

- [x] Phase 19: Block Separation Fixes (Cluster A) (3/3 plans) — completed 2026-07-20
- [x] Phase 20: Signature Token Spacing (Cluster B) (2/2 plans) — completed 2026-07-20
- [x] Phase 21: Residual Fidelity Fixes (Clusters C/D/E/F) (3/3 plans) — completed 2026-07-20
- [x] Phase 22: typstpdf Target-Name PDF Fix (Issue #117) (3/3 plans) — completed 2026-07-21
- [x] Phase 22.1: typstpdf Compile-Root Alignment for Nested Masters (INSERTED) (4/4 plans) — completed 2026-07-22
- [x] Phase 22.2: Dead Config-Value Sweep (INSERTED) (6/6 plans) — completed 2026-07-22
- [x] Phase 22.3: typstpdf Builder Warning Hardening (INSERTED) (3/3 plans) — completed 2026-07-22
- [x] Phase 22.4: README 記述の実測乖離解消 (INSERTED) (3/3 plans) — completed 2026-07-23
- [x] Phase 23: v0.6.2 Release Prep + Regression-Gate Close (3/3 plans) — completed 2026-07-23

</details>

### 🚧 v0.6.3 — config & docs 実測整合 + captioned tables (Phases 24–28) — IN PROGRESS

**Milestone goal:** Make the documented configuration actually take effect and make the docs match the
implementation. Three tracks over five phases: (1) dead-config sweep round 2 — delete the inert
`typst_toctree_defaults` (part B) and implement the `typst_elements` `papersize`/`fontsize`
pass-through (part A) so PDF-relevant keys reach the template's `project()`; (2) reimplement external
PR#98 — a `.. table:: Caption` renders as a numbered `figure(table(...), caption, kind: table)`
("Table N") that is cross-referenceable, while caption-less tables stay plain; (3) docs 実測整合 —
delete the unreachable orphan `docs/configuration.rst`, correct the phantom config names in
`user_guide/configuration.rst`, and delete the redundant phantom-bearing config table in
`api/index.rst` (config documented in one canonical place). A prep-only Release phase closes the milestone.

**Ordering rationale (research-driven, honored):** trivial 0-risk deletion first (Phase 24) → the
translator captioned-table work (Phase 25, its own state-machine risk) → the config `typst_elements`
pass-through (Phase 26, its own type-mismatch risk, kept in a **separate** phase from the table work)
→ docs cleanup (Phase 27, **must** follow Phase 26 so the phantom `typst_papersize`/`typst_fontsize`
lines are rewritten into *working* `typst_elements` examples, not a fatal one) → Release (Phase 28).
TBL-01 and TBL-02 share Phase 25, TBL-01 first (the figure must exist to be labeled).

**Standing bar (GATE-01):** every node-handler change (Phase 25) and every config→output change
(Phase 26) ships a fail-pre-fix real `typst.compile()` regression fixture (template:
`tests/test_package_only_config_gate.py`). Phase 25's fixture MUST exercise a 2+-table document (the
stale-cell-buffer bug is invisible with one table) plus a caption+width case and a `:numref:`-resolves
case. Phase 26's fixture MUST test `papersize` AND `fontsize` separately, a negative unknown-key case,
and a copyright-non-leak case. String-agreement asserts alone never suffice. (Pure-removal Phase 24 and
docs-only Phase 27 carry no config→output change, so GATE-01 does not apply there — a grep-zero /
grep-cross-check proof + green suite is the honest bar.)

**Milestone invariant (every phase):** zero new runtime deps, no `@preview` version bump — the 3-way
version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`) stays untouched
(CONF-04 is a 100% Python-side fix; `base.typ` is byte-unchanged). Flag during planning if a phase
needs otherwise (none expected).

**Ship unit = milestone** (`branching_strategy: milestone`): Phase 28 is prep-only; the irreversible
publish (tag `v0.6.3` → `release.yml` → PyPI + GitHub Release) executes at `/gsd-complete-milestone`.

- [x] **Phase 24: Delete `typst_toctree_defaults`** - Pure removal of the inert config value from every surface (registration, docs, examples, README, its test file) — grep-zero, 0-risk (completed 2026-07-23)
- [x] **Phase 25: Captioned Table Figure Wrap + Cross-References** - `.. table:: Caption` → `figure(table, caption, kind: table)` "Table N" + `:numref:`/`:ref:` `<label>`; caption-less stays plain; caption+width compose; 2nd-table stale-buffer fix (completed 2026-07-24)
- [ ] **Phase 26: `typst_elements` papersize/fontsize Pass-Through** - `typst_elements` `papersize`/`fontsize` reach `project()` (string vs. unquoted length); unknown key fails loud; copyright never leaks; `base.typ` unchanged
- [ ] **Phase 27: Docs 実測整合 — Orphan Delete + Phantom Names** - Delete orphan `docs/configuration.rst`; fix phantom config names in `user_guide/configuration.rst` (papersize/fontsize → working `typst_elements` examples) AND delete the redundant phantom-bearing config table in `api/index.rst` (+ its `.po`) so config lives in one canonical place
- [ ] **Phase 28: v0.6.3 Release Prep + Regression-Gate Close** - Prep-only: bump 0.6.3 + `uv.lock` + `CHANGELOG` + README Status, close on the full-corpus gate; publish at `/gsd-complete-milestone`

### Phase 24: Delete `typst_toctree_defaults` (dead-config sweep round 2, part B)

**Goal**: The registered-but-inert `typst_toctree_defaults` config value is gone from every surface, so it is no longer presented as a supported option — per-directive `:maxdepth:` etc. remains the documented path.
**Depends on**: Nothing (first phase of the milestone; functionally independent — sequenced first only because it is trivial and 0-risk)
**Requirements**: CONF-05
**Success Criteria** (what must be TRUE):

  1. Searching the whole repo (`typsphinx/__init__.py` registration, docs, `examples/advanced`, README, tests) for `typst_toctree_defaults` returns zero hits — a user can no longer discover it as a supported option.
  2. The extension still imports, both builders register, and a documentation project builds green via `sphinx-build -b typst` with the value removed; the full existing test suite stays green and the registration-only `tests/test_config_toctree_defaults.py` is deleted (`tests/test_documentation_configuration.py` updated to drop its reference).
  3. No `typst_toctree_defaults` example remains in any user-facing surface; documented toctree control is via per-directive options (`:maxdepth:` etc.).

**Plans**: 1/1 plans executed

- [x] 24-01-PLAN.md — Remove inert `typst_toctree_defaults` from all surfaces (registration + README/examples/docs), delete the registration-only test file, drop its doc-list entry; grep-zero + green suite

**Note**: Pure removal of a grep-proven-inert value (zero consumers in `translator.py`/`writer.py`/`builder.py`/`template_engine.py`) — no config→output change, so GATE-01 does not apply; a grep-zero proof + green suite is the honest bar.

### Phase 25: Captioned Table Figure Wrap + Cross-References (reimplement PR#98)

**Goal**: A captioned table renders as a numbered "Table N" figure that can be cross-referenced, while a caption-less table stays a plain table.
**Depends on**: Phase 24 (sequential order only — no functional dependency)
**Requirements**: TBL-01, TBL-02
**Success Criteria** (what must be TRUE):

  1. A `.. table:: Caption` directive renders in the compiled PDF as `figure(table(...), caption: {...}, kind: table)` with native "Table N" numbering and **no** stray `heading()` above the table; the caption preserves inline markup.
  2. A table **without** a caption still renders as a plain `table()` — never speculatively figure-wrapped.
  3. A captioned table that also sets `:width:` renders with **both** the caption and the existing block-width wrap composed correctly (verified together, not separately).
  4. The 2nd-and-later captioned table in a single document keeps its own caption — none lost to a stale cell buffer — proven by a 2+-table real-`typst.compile()` fixture.
  5. A `:numref:` / `:ref:` to a captioned table resolves to a working "Table N" link in the compiled PDF: the `figure(..., kind: table)` carries a Typst `<label>` derived from the table's docutils target id, with no dangling/duplicate-label error and no collision with the table's existing `_emit_id_anchors` id anchors.

**Plans**: 2/2 plans executed
**Wave 1**

- [x] 25-01-PLAN.md — Caption buffering + figure-wrap + `<label>` + deferred anchor in `translator.py`, with adapted PR#98 unit tests (TBL-01, TBL-02) — Wave 1

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 25-02-PLAN.md — GATE-01 real-compile render fixture (2+-table, caption+width, `:numref:`-resolves, csv/list) + pre-fix-basis failure proof (TBL-01, TBL-02) — Wave 2

**Note**: GATE-01 fixture mandatory (template `tests/test_pdf_render_gate.py` — sentinel + pypdf pattern, per RESEARCH template correction) — MUST include a 2+-table document, the caption+width composition case, and a `:numref:`-resolves case, with red→green proof (durable pre-fix-basis reconstruction). Isolated from Phase 26 to keep the translator state-machine risk separate from the config type-mismatch risk.

### Phase 26: `typst_elements` papersize/fontsize Pass-Through (dead-config sweep round 2, part A)

**Goal**: A user who sets `papersize`/`fontsize` via `typst_elements` in `conf.py` sees them applied in the compiled output, with an unknown key failing loudly and baseline Sphinx metadata never leaking into the template.
**Depends on**: Phase 25 (sequential — keeps the config-wiring/type risk isolated from the translator state-machine risk)
**Requirements**: CONF-04
**Success Criteria** (what must be TRUE):

  1. `typst_elements = {"papersize": "us-letter"}` in `conf.py` reaches the template's `project()` and the compiled PDF uses that paper size, with `papersize` emitted as a Typst **string**.
  2. `typst_elements = {"fontsize": "20pt"}` reaches `project()` with `fontsize` emitted as an **unquoted Typst length** (not a quoted string) and the compiled PDF uses that font size — proven by a fixture separate from the `papersize` case.
  3. An unrecognized `typst_elements` key (one `base.typ`'s `project()` does not declare) **fails loudly** via the curated allowlist, rather than silently dropping it or emitting an undeclared kwarg that aborts the Typst compile.
  4. Baseline Sphinx metadata (`copyright`, etc.) is **never** leaked into `project()` as a parameter.
  5. `templates/base.typ` is byte-unchanged — the fix is 100% Python-side (`writer.py` keeps `typst_elements` separate; `template_engine.py`'s `map_parameters` merges the curated allowlist additively, leaving the Phase 22.2 guards intact).

**Plans**: 2/2 plans executed

**Wave 1**

- [x] 26-01-PLAN.md — Python-side pass-through: `RawTypst` marker + `ELEMENTS_ALLOWLIST` + `map_parameters(typst_elements=)` additive merge/fail-loud in `template_engine.py`; `writer.py` passes `typst_elements` separately + drops dead `copyright`; unit tests + `base.typ` byte-unchanged (CONF-04) — Wave 1

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 26-02-PLAN.md — GATE-01 real-`typst.compile()` fixtures: positive papersize, separate positive fontsize, negative unknown-key abort, copyright-non-leak + durable pre-fix-basis failure proof (CONF-04) — Wave 2

**Note**: GATE-01 fixtures mandatory — positive `papersize`, positive `fontsize` (separately), negative unknown-key (fails loudly), and copyright-non-leak — each a real-`typst.compile()` case with red→green proof.

### Phase 27: Docs 実測整合 — Orphan Delete + Phantom Config Names

**Goal**: Every documented `typst_*` name across the user-facing docs matches a registered config value; the unreachable orphan config doc is removed; and config is documented in ONE canonical place so it cannot re-drift.
**Depends on**: Phase 26 (CONF-04 must ship first so the phantom `typst_papersize`/`typst_fontsize` lines can be rewritten into *working* `typst_elements` examples instead of delete-only — Pitfall 11 prevention)
**Requirements**: DOC-06, DOC-07
**Success Criteria** (what must be TRUE):

  1. The orphan `docs/configuration.rst` (526 lines, unreachable from any toctree, containing the wrong package name `sphinxcontrib.typst`) is deleted, with no live toctree/xref reference to it remaining and no unique useful content lost.
  2. In `docs/source/user_guide/configuration.rst`: `typst_author` → `typst_authors`; the unregistered `typst_use_codly` / `typst_code_line_numbers` examples removed; `typst_papersize`/`typst_fontsize` rewritten as **working** `typst_elements` examples (e.g. `typst_elements = {"papersize": "us-letter", "fontsize": "20pt"}`) leveraging Phase 26 — NOT the phantom top-level names (Sphinx's LaTeX builder exposes papersize/pointsize only via `latex_elements`, so `typst_elements` is the faithful mirror; no top-level `typst_papersize` is implemented).
  3. The redundant "Available Configuration Values" `list-table` in `docs/source/api/index.rst` (lists 4 phantom names + omits 6 registered ones) is **deleted**, keeping only the existing `See :doc:/user_guide/configuration` pointer — config documented in one canonical place; `docs/locale/ja/LC_MESSAGES/api/index.po` updated to follow.
  4. Every `typst_*` name remaining anywhere under `docs/source/` maps to a value registered in `typsphinx/__init__.py` (grep cross-check over BOTH `user_guide/configuration.rst` and `api/index.rst`).
  5. The docs still build (`sphinx-build`/`docs-multilang` green); no broken `:doc:`/`:ref:` left by the api-table deletion.

**Plans**: TBD

### Phase 28: v0.6.3 Release Prep + Regression-Gate Close

**Goal**: Prep-only — single-source the version bump to 0.6.3, curate the CHANGELOG entry, update the README status line, and close the milestone on the full-corpus regression gate. The irreversible publish is deferred to `/gsd-complete-milestone`.
**Depends on**: Phase 27 (all six v1 requirements delivered)
**Requirements**: none (release/close phase — carries no requirement)
**Success Criteria** (what must be TRUE):

  1. `pyproject.toml` is bumped to `0.6.3` as the **sole** version literal, with `uv.lock` regenerated in lockstep (`uv sync --locked` green) and the `README.md` `**Status**` line updated to reflect v0.6.3.
  2. `CHANGELOG.md` has a curated `## [0.6.3]` entry covering all 6 v1 requirements (CONF-04, CONF-05, TBL-01, TBL-02, DOC-06, DOC-07); the `## [Unreleased]` compare link is advanced and the `[0.6.3]` release/tag link block appended (release-prep's own job — does not violate a prior release phase's version-literal invariant).
  3. The full-corpus real `typst.compile()` regression gate passes (valid `%PDF`, `unknown_visit` catalogue empty), confirming no regression from the milestone's changes.
  4. The milestone invariant holds: zero new runtime deps, no `@preview` version bump, the 3-way version-sync surface (`writer.py` / `template_engine.py` / `templates/base.typ`) untouched.
  5. Scope fence: no tag, no PyPI publish, no merge — the irreversible publish (tag `v0.6.3` → `release.yml` → PyPI + GitHub Release) executes at `/gsd-complete-milestone` on the confirmed-green merge commit.

**Plans**: TBD

## Progress

**Execution Order:**
Active milestone phases execute in numeric order (decimal insertions between their surrounding integers): 24 → 25 → 26 → 27 → 28.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Pin Runtime Dependencies to Known-Good | v0.4.4 | 2/2 | Complete | 2026-07-04 |
| 2. Verify the Green Baseline | v0.4.4 | 3/3 | Complete | 2026-07-04 |
| 3. Modernize Python Floor (3.10–3.13) | v0.4.4 | 2/2 | Complete | 2026-07-04 |
| 4. Refresh Dev Tooling | v0.4.4 | 4/4 | Complete | 2026-07-04 |
| 5. Durability Guardrails | v0.4.4 | 4/4 | Complete | 2026-07-05 |
| 6. Raise Runtime Pins + Python Floor | v0.5.0 | 1/1 | Complete | 2026-07-09 |
| 7. Bump @preview Packages + typst 0.15 (kai fix) | v0.5.0 | 1/1 | Complete | 2026-07-11 |
| 8. API & Test Compatibility (Sphinx 9 / docutils 0.22) | v0.5.0 | 3/3 | Complete | 2026-07-11 |
| 8.1 Admonition Rendering Fix (INSERTED) | v0.5.0 | 4/4 | Complete | 2026-07-11 |
| 9. Green CI Matrix + Smoke Test + Guardrails | v0.5.0 | 2/2 | Complete | 2026-07-11 |
| 10. Version-String Fix + v0.5.0 Release | v0.5.0 | 2/2 | Complete | 2026-07-11 |
| 11. Issue #114 Fatal Fixes + Graceful-Degrade Net | v0.6.0 | 3/3 | Complete | 2026-07-12 |
| 12. High-Volume Independent Node Handlers | v0.6.0 | 4/4 | Complete | 2026-07-12 |
| 13. Shared Dispatch-Point Changes (topic + line blocks) | v0.6.0 | 3/3 | Complete | 2026-07-12 |
| 14. Footnotes (doctree pre-pass) | v0.6.0 | 2/2 | Complete | 2026-07-12 |
| 15. Full-Corpus Validation | v0.6.0 | 3/3 | Complete | 2026-07-12 |
| 16. Silent-Drop Node Handlers + Length-Converter Refactor | v0.6.1 | 3/3 | Complete | 2026-07-16 |
| 17. Rendering-Fidelity Audit | v0.6.1 | 4/4 | Complete | 2026-07-19 |
| 18. Fidelity Fixes + Regression-Gate Close | v0.6.1 | 2/2 | Complete | 2026-07-19 |
| 19. Block Separation Fixes (Cluster A) | v0.6.2 | 3/3 | Complete | 2026-07-20 |
| 20. Signature Token Spacing (Cluster B) | v0.6.2 | 2/2 | Complete | 2026-07-20 |
| 21. Residual Fidelity Fixes (Clusters C/D/E/F) | v0.6.2 | 3/3 | Complete | 2026-07-20 |
| 22. typstpdf Target-Name PDF Fix (Issue #117) | v0.6.2 | 3/3 | Complete | 2026-07-21 |
| 22.1 typstpdf Compile-Root Alignment (INSERTED) | v0.6.2 | 4/4 | Complete | 2026-07-22 |
| 22.2 Dead Config-Value Sweep (INSERTED) | v0.6.2 | 6/6 | Complete | 2026-07-22 |
| 22.3 typstpdf Builder Warning Hardening (INSERTED) | v0.6.2 | 3/3 | Complete | 2026-07-22 |
| 22.4 README 記述の実測乖離解消 (INSERTED) | v0.6.2 | 3/3 | Complete | 2026-07-23 |
| 23. v0.6.2 Release Prep + Regression-Gate Close | v0.6.2 | 3/3 | Complete | 2026-07-23 |
| 24. Delete `typst_toctree_defaults` | v0.6.3 | 1/1 | Complete    | 2026-07-23 |
| 25. Captioned Table Figure Wrap + Cross-References | v0.6.3 | 2/2 | Complete    | 2026-07-24 |
| 26. `typst_elements` papersize/fontsize Pass-Through | v0.6.3 | 2/2 | In Progress|  |
| 27. Docs 実測整合 — Orphan Delete + Phantom Names | v0.6.3 | 0/TBD | Not started | - |
| 28. v0.6.3 Release Prep + Regression-Gate Close | v0.6.3 | 0/TBD | Not started | - |

## Backlog

Candidate work not yet scoped into a milestone. Promote items with `/gsd-review-backlog`, or
pull a whole cluster into the next milestone via `/gsd-new-milestone`.
Numbered 999.x so milestone reorganization never renumbers or drops them.

**The backlog is currently empty.** New items land here as `999.x` entries. The dead-config sweep
(`typst_elements` keys / `typst_toctree_defaults`), the PR#98 captioned-table reimplementation, the
orphan `docs/configuration.rst` deletion, and the user-guide phantom config names were **promoted into
v0.6.3** (Phases 24–27). Remaining discrete follow-up work stays in `.planning/todos/pending/` — RTD
migration, sphinx-linkcheck CI, citation-node support, non-str-docname TypeError hardening,
typing-import modernization, and github.io doc-link 404s (folded into the RTD migration) — see also
STATE.md Deferred Items.

---
*Roadmap created: 2026-07-04 · Reorganized at each milestone close: v0.4.4 (2026-07-05), v0.5.0 (2026-07-11), v0.6.0 (2026-07-13), v0.6.1 (2026-07-19), v0.6.2 (2026-07-23). v0.6.3 milestone added 2026-07-23 (Phases 24–28). Per-milestone phase detail, success criteria, and decisions for shipped milestones live in `milestones/vX.Y-ROADMAP.md`.*
