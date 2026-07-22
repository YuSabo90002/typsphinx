---
phase: 22-typstpdf-target-name-pdf-fix-issue-117
verified: 2026-07-21T14:07:13Z
status: passed
score: 27/28 must-haves verified
behavior_unverified: 0
overrides_applied: 0
behavior_unverified_items: []
human_verification:

  - test: "Confirm on an actual macOS filesystem (HFS+/APFS, NFD-normalizing) that a non-ASCII typst_documents target name (e.g. 'マニュアル.typ') round-trips to the SAME bytes on read-back as it does on Linux (byte-preserving NFC), or explicitly accept that typsphinx does not control this and the risk is documented, not mitigated."
    expected: "Either: (a) the filename is usable on both platforms without silent mojibake/duplicate-file creation, or (b) the project explicitly accepts this as an inherent OS-level limitation outside typsphinx's control (which is what 22-01-PLAN.md's `verification: backstop` marker already states in its own text)."
    why_human: "This is a `verification: backstop` truth (22-01-PLAN.md must_haves.truths, the 8th entry) — it is explicitly NOT asserted by any test in the corpus (there is no macOS CI runner and no cross-platform filesystem-encoding test), and the plan's own wording says 'is not asserted.' Per the backstop-truth contract this verifier abstains rather than silently passing it; the truth is present in the codebase only as an acknowledged, deliberately-unverified risk, not as a proven fact. A human with access to a real macOS filesystem (or an accepted policy decision) is needed to close it — grep/code-reading cannot produce OS-level filesystem-encoding evidence."
---

# Phase 22: typstpdf Target-Name PDF Fix (Issue #117) Verification Report

**Phase Goal:** `sphinx-build -b typstpdf` names the compiled PDF after the `typst_documents` target
name (`manual.pdf`), not the source docname (`index.pdf`) — an independent `builder.py` fix that does
NOT share the translator root causes of Phases 19–21. Per locked decision D-01, delivered scope is
BOTH the `.typ` and the `.pdf` filename.

**Verified:** 2026-07-21T14:07:13Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | (ROADMAP SC#1) `typst_documents = [('index','manual.typ',...)]` → `sphinx-build -b typstpdf` emits `manual.pdf`, not `index.pdf` | ✓ VERIFIED | `tests/test_target_name_render_gate.py` proves the equivalent case (`output.typ`/`output.pdf` present, `index.typ`/`index.pdf` absent) with a real `typst.compile()`; independently confirmed with a direct `sphinx-build -b typst examples/basic` run in this session, which emitted `basic-example.typ` (target name), not `index.typ` |
| 2 | (ROADMAP SC#2) `TypstPDFBuilder.finish()` and both `write_doc()` sites derive the filename from `typst_documents` via one shared helper `_resolve_output_stem`, so `.pdf`/`.typ` always agree | ✓ VERIFIED | Read `typsphinx/builder.py`: all 3 sites (`TypstBuilder.write_doc:475`, `TypstPDFBuilder.write_doc:794`, `TypstPDFBuilder.finish:858`) call `self._resolve_output_stem(docname)` exactly once per doc and derive both `typ_file`/`pdf_file` from the same `relative_path` in `finish()` |
| 3 | (ROADMAP SC#3) A regression test asserts the compiled PDF filename matches the configured target and fails against pre-fix `index.pdf` behavior | ✓ VERIFIED | `tests/test_target_name_render_gate.py::TestTargetNameRenderGate::test_typstpdf_emits_target_named_artifacts_and_not_docname_named` asserts BOTH presence of `output.typ`/`output.pdf` AND absence of `index.typ`/`index.pdf` — bidirectional, so it fails on both counts against the pre-fix builder |
| 4 | (ROADMAP SC#4) Zero new runtime deps, no `@preview` bump, 3-way version-sync surface untouched | ✓ VERIFIED | `git diff --name-only e5032a4..HEAD` lists no `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/`, or `pyproject.toml`; `tests/test_preview_version_sync.py` passes |
| 5 | `_resolve_output_stem` strips a literal trailing `.typ` only (D-03/D-04); never uses `os.path.splitext` | ✓ VERIFIED | `grep -c splitext typsphinx/builder.py` = 0; `test_resolve_output_stem_strips_trailing_typ_suffix`, `test_resolve_output_stem_preserves_period_in_stem(_with_suffix)` pass |
| 6 | Extension-less target names are valid input (no warning/error) | ✓ VERIFIED | `test_resolve_output_stem_accepts_extensionless_target` passes; confirmed live via `docs/source/conf.py`'s `"typsphinx"` target producing `typsphinx.typ`/`typsphinx.pdf` in a real dogfood build (see Data-Flow Trace) |
| 7 | Docname with no `typst_documents` entry (or empty/None config) returns docname unchanged, silently (D-02) | ✓ VERIFIED | `test_resolve_output_stem_falls_back_to_docname_when_unlisted`, `..._falls_back_when_config_missing` pass |
| 8 | Path-bearing / traversal / absolute / drive-qualified target emits exactly one warning and resolves to `os.path.basename` (D-06/D-07) | ✓ VERIFIED | 5 dedicated tests pass (`..._guards_posix_path_separator`, `..._backslash_path_separator`, `..._parent_traversal`, `..._absolute_target`, `..._drive_qualified_target`); `test_resolve_output_stem_warns_on_path_bearing_target` asserts the warning substring via `caplog` |
| 9 | Degenerate target (empty, bare `.typ`, whitespace, non-str, short tuple) falls back to docname with a warning (edge: empty) | ✓ VERIFIED | `test_resolve_output_stem_falls_back_on_{empty_target,bare_typ_target,whitespace_target,short_tuple,non_str_target}` all pass; `test_resolve_output_stem_warns_on_degenerate_target` asserts the warning substring |
| 10 | Non-ASCII target resolves verbatim, no normalization/case-folding/transliteration (edge: encoding) | ✓ VERIFIED | `test_resolve_output_stem_preserves_non_ascii_target` (target `"マニュアル.typ"` → stem `"マニュアル"`) passes |
| 11 | (backstop) Non-ASCII target round-trips identically through macOS (NFD) vs Linux (NFC) filesystems | ⚠️ insufficient_spec (backstop, not asserted) | No test exists (none is claimed to exist — the plan's own text says "is not asserted"); no macOS environment available in this verification session. Routed to human verification, not silently passed. |
| 12 | Identity target (`'index','index'`) resolves byte-identical to pre-fix behavior — the ~60-fixture non-regression | ✓ VERIFIED | `test_resolve_output_stem_identity_target_is_unchanged` passes; full fast suite green (473 passed) including all identity-mapping fixtures |
| 13 | `get_target_uri('index')` still returns `'index' + self.out_suffix`, unchanged, after this plan (D-02, cross-doc identity) | ✓ VERIFIED | `git diff e5032a4..HEAD -- typsphinx/builder.py`: only a docstring paragraph was added; the `return docname + self.out_suffix` line is untouched (confirmed no `-.*return docname + self.out_suffix` in diff) |
| 14 | GATE-01 render gate is bidirectional (target-named present AND docname-named absent) | ✓ VERIFIED | Read `tests/test_target_name_render_gate.py` concern (4): explicit `assert not (temp_build_dir / "index.typ").exists()` and `.../"index.pdf"` |
| 15 | D-12: corpus gate (`tests/test_corpus_gate.py`) asserts the target-derived `sphinx-corpus.pdf`, stays green post-fix | ✓ VERIFIED | Ran `uv run python -m pytest tests/test_corpus_gate.py -k TestCorpusRenderGate -m slow -q` (real network, cached corpus) → 1 passed |
| 16 | D-12: `docs/source/conf.py`'s extension-less target `"typsphinx"` produces `typsphinx.typ`/`typsphinx.pdf`, not `index.*`, under a real dogfood build | ✓ VERIFIED | Ran `sphinx-build -b typstpdf docs/source <tmp>` directly in this session (tox's `docs-pdf` shells to `uv` which fails in this sandbox per documented limitation) — produced `typsphinx.typ` + `typsphinx.pdf` (1.6MB, `%PDF` magic confirmed), no `index.*` present |
| 17 | Cross-document `:ref:` into a renamed master still resolves; `get_target_uri` staying docname-based does not break cross-doc labels | ✓ VERIFIED | `tests/fixtures/cross_doc_label_namespace_render_gate/conf.py` target flipped to `"namespace-gate"`; ran `tests/test_cross_doc_label_namespace_render_gate.py` → 1 passed; `pagea:shared-topic` namespace assertions intact, `namespace-gate.pdf` present, `index.pdf` absent |
| 18 | `examples/basic`'s target-derived artifact (`basic-example.typ`) surface is closed — the blast-radius gap CONTEXT.md/RESEARCH.md missed | ✓ VERIFIED | Ran `tests/test_examples_basic.py` → all 15 passed (main tree); independently confirmed via a direct `sphinx-build -b typst examples/basic <tmp>` run in this session: emitted `basic-example.typ`, not `index.typ` |
| 19 | No example `conf.py` under `examples/` was edited to accommodate a stale assertion | ✓ VERIFIED | `git status --porcelain examples/basic/conf.py examples/advanced/conf.py examples/charged-ieee/approach{1,2}/conf.py` — empty |
| 20 | `examples/advanced/README.md`, `examples/charged-ieee/README.md` name the artifacts their configs actually produce | ✓ VERIFIED | `grep -c advanced-example.typ examples/advanced/README.md` = 3; `grep -c paper.typ examples/charged-ieee/README.md` = 2; `chapter1.typ` count unchanged |
| 21 | User guide (`builders.rst`, `configuration.rst`) states which filenames a `typst_documents` config produces | ✓ VERIFIED | `builders.rst` gained the `main.typ`/`api-ref.typ` note; `configuration.rst` states suffix-stripping + no-path-component rules including `v1.2-manual` preservation |
| 22 | ROADMAP Phase 22 SC#2 no longer asserts a pre-existing correct `.typ` mapping; Phase 23 SC#2 carries the D-09 CHANGELOG hand-off | ✓ VERIFIED | Read `.planning/ROADMAP.md`: SC#2 now cites `_resolve_output_stem`; Phase 23 SC#2 mentions "user-visible output filename change" |
| 23 | D-11: the five named regression modules are unmodified and green | ✓ VERIFIED | `git diff --name-only e5032a4..HEAD \| grep -E "test_builder.py\|test_builder_requirement13.py\|test_integration_nested_toctree.py\|test_config_template_mapping.py\|test_config_toctree_defaults.py"` → no output; full suite green |
| 24 | `tests/roots/test-basic/conf.py` (the D-10 fixture) was not modified | ✓ VERIFIED | `git status --porcelain tests/roots/` — no output |
| 25 | `docs/configuration.rst` (top-level, non-toctree'd copy) deliberately left unedited | ✓ VERIFIED | `git status --porcelain docs/configuration.rst` — no output |

**Score:** 27/28 truths verified (1 backstop truth routed to human verification, not counted as verified per the backstop contract — it is also not counted as failed).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/builder.py::TypstBuilder._resolve_output_stem` | New private method implementing D-02/D-03/D-04/D-06/D-07 + edge cases | ✓ VERIFIED | Exists at line 131, full logic present, exercised by 21 unit tests |
| `typsphinx/builder.py::TypstBuilder._directory_preserving_relpath` | Helper keeping nested-docname output in its own directory (D-05) | ✓ VERIFIED | Exists at line 224; used by all 3 write/read sites |
| `tests/test_builder_output_stem.py` | New pytest module, ≥18 plain `def test_*` (no parametrize) | ✓ VERIFIED | 21 test functions, zero `@pytest.mark.parametrize` (`grep -c parametrize` = 0), all pass |
| `tests/test_target_name_render_gate.py` | New GATE-01 real-compile render gate | ✓ VERIFIED | Exists, 1 test, bidirectional, passes |
| `tests/test_corpus_gate.py` (updated) | GATE-02 assertion realigned to target-derived name | ✓ VERIFIED | `sphinx-corpus.pdf` asserted, `index.pdf` absent from file, slow test passes with real network |
| `tests/fixtures/cross_doc_label_namespace_render_gate/conf.py` (updated) | Non-identity target `"namespace-gate"` | ✓ VERIFIED | Confirmed via grep + passing test |
| `tests/test_examples_basic.py` (updated) | Target-derived assertion for `examples/basic` | ✓ VERIFIED | Confirmed via grep + passing test on main tree |
| `examples/advanced/README.md`, `examples/charged-ieee/README.md` (updated) | Corrected artifact filenames | ✓ VERIFIED | grep counts match acceptance criteria |
| `docs/source/user_guide/builders.rst`, `configuration.rst` (updated) | Filename-governance prose | ✓ VERIFIED | Present and builds cleanly (HTML build succeeded) |
| `.planning/ROADMAP.md` (updated) | Corrected SC#2 text, Phase 23 D-09 hand-off | ✓ VERIFIED | Scoped edits confirmed; phase-heading count unaffected |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `TypstBuilder.write_doc` | `_resolve_output_stem` | direct call, `.typ` destination | WIRED | `builder.py:473` |
| `TypstPDFBuilder.write_doc` | `_resolve_output_stem` | direct call, literal `.typ` destination | WIRED | `builder.py:794` |
| `TypstPDFBuilder.finish` | `_resolve_output_stem` | single call per `doc_tuple`, feeds BOTH `typ_file` and `pdf_file` | WIRED | `builder.py:858` — read-back and write path guaranteed to agree |
| `tests/roots/test-basic/conf.py` target | `_resolve_output_stem` | `output.typ` → `output.typ`/`output.pdf` | WIRED | proven by real `typst.compile()` in `test_target_name_render_gate.py` |
| `wire_typsphinx_into_corpus_conf`'s injected target | corpus gate's asserted PDF path | `sphinx-corpus` → `sphinx-corpus.pdf` | WIRED | `tests/test_corpus_gate.py` slow test passes with real network |
| `cross_doc_label_namespace_render_gate/conf.py` target | renamed-master compile + docname-keyed labels | `namespace-gate` → `.typ`/`.pdf`, labels still `pagea:`/`pageb:`-namespaced | WIRED | real compile passes, `pagea:shared-topic` assertions unweakened |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|
| `docs/_build`-equivalent dogfood output | `stem`/`relative_path` in `TypstPDFBuilder.finish()` | `_resolve_output_stem("index")` against `docs/source/conf.py`'s `("index","typsphinx",...,"typst")` 5-tuple | Yes — real `typst.compile()` output, 1.6MB `%PDF`-magic PDF | ✓ FLOWING |
| `examples/basic` build output | same helper, target `"basic-example.typ"` | `examples/basic/conf.py` | Yes — direct `sphinx-build -b typst` run in this session emitted `basic-example.typ` | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| New unit tests pass | `uv run python -m pytest tests/test_builder_output_stem.py tests/test_target_name_render_gate.py tests/test_cross_doc_label_namespace_render_gate.py -q` | 23 passed | ✓ PASS |
| Fast suite green (main tree, environmentally-clean run) | `uv run python -m pytest -m "not slow" -q --ignore=...4 integration modules` | 473 passed, 0 failed, 23 deselected | ✓ PASS |
| Slow corpus gate (real network) | `uv run python -m pytest tests/test_corpus_gate.py -k TestCorpusRenderGate -m slow -q` | 1 passed | ✓ PASS |
| Real dogfood PDF build (`docs/source`) | `sphinx-build -b typstpdf docs/source <tmp>` (direct, since `tox -e docs-pdf` fails in this sandbox per documented `uv`-subprocess limitation) | `typsphinx.typ` + `typsphinx.pdf` (1.6MB, `%PDF` magic), no `index.*` | ✓ PASS |
| Real `examples/basic` build | `sphinx-build -b typst examples/basic <tmp>` | `basic-example.typ` emitted, no `index.typ` | ✓ PASS |
| black/ruff/mypy on all phase-modified files | see commands run | all exit 0 | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` convention exists in this project and none is declared by this phase's PLAN/SUMMARY files. Step 7c: SKIPPED (no probes declared or conventional for this phase).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| PDF-01 | 22-01, 22-02, 22-03 (all three) | `sphinx-build -b typstpdf` names the PDF after the target, not the docname; `finish()` derives from the target tuple | ✓ SATISFIED | All 4 ROADMAP success criteria verified above; no orphaned requirements — `REQUIREMENTS.md` maps only PDF-01 to Phase 22, and all three plans declare it |

No requirement IDs from `REQUIREMENTS.md` mapped to Phase 22 are missing from a plan's `requirements:` field. `REQUIREMENTS.md:95` already marks PDF-01 "Complete", consistent with the codebase evidence gathered above.

### Anti-Patterns Found

None. Scanned all phase-modified files (`typsphinx/builder.py` + 10 test/docs/example files) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`/stub-return patterns — zero hits in the diff introduced by this phase. (`tests/test_corpus_gate.py` contains pre-existing `TODO-01`/`MAN-01` requirement-ID references from Phase 16, unrelated to and unmodified by this phase's diff — not a debt marker, a requirement-ID citation.)

### Human Verification Required

#### 1. Non-ASCII filesystem round-trip across macOS/Linux (backstop truth)

**Test:** On a real macOS filesystem (HFS+/APFS, which NFD-normalizes filenames), configure
`typst_documents = [("index", "マニュアル.typ", ...)]` and run `sphinx-build -b typstpdf`. Compare the
resulting on-disk filename bytes against the same build run on Linux (byte-preserving NFC).
**Expected:** Either the filenames are usable and consistent enough not to silently duplicate or
corrupt files across platforms, or the project explicitly documents this as an accepted, out-of-scope
OS-level limitation (which 22-01-PLAN.md's own `verification: backstop` marker already states in
prose, but no code or test enforces or proves it).
**Why human:** This is a `verification: backstop` truth — 22-01-PLAN.md's `must_haves.truths` list
includes it with an explicit `verification: backstop` tag and states in its own text that "filesystem-
level Unicode normalization is outside typsphinx's control and is not asserted." No test in the corpus
exercises this (there is no macOS runner available), so per the backstop-truth contract this verifier
abstains rather than silently marking it VERIFIED or FAILED — the codebase behavior here is genuinely
unproven, only reasoned about in prose. This does not block the phase (D-01/D-08's clean-break
requirement and the primary Issue #117 fix are fully proven), but it should not be silently absorbed
into a "passed" verdict.

### Gaps Summary

No gaps found. All 4 ROADMAP Phase 22 success criteria are verified against the actual codebase (not
SUMMARY claims): the shared `_resolve_output_stem` helper exists and is the single source of the
target-name normalization rule; all three output-path sites (`TypstBuilder.write_doc`,
`TypstPDFBuilder.write_doc`, `TypstPDFBuilder.finish`) call it exactly once per document, so `finish()`
cannot read back a `.typ` the write path did not produce; `get_target_uri` is functionally byte-
identical (docstring-only diff, confirmed via `git diff`); the D-11 five-module regression guard is
unmodified and green; the GATE-01 render gate is genuinely bidirectional; the corpus gate (D-12,
network + `-m slow`) and the dogfood `docs/source` build (D-12) were both re-run live in this session
and pass; the previously-missed `examples/` consumer surface (orchestrator deviation, Task 3 of 22-03)
is closed and independently re-confirmed with a direct build in this session; and the milestone
invariant (zero new deps, no `@preview` bump, `writer.py`/`template_engine.py`/`templates/base.typ`
untouched) holds per `git diff --name-only e5032a4..HEAD`.

The only open item is a single `verification: backstop` truth (non-ASCII filename round-trip across
macOS vs. Linux filesystem normalization) that the plan itself declares as "not asserted" — this is
routed to human verification per the backstop-truth contract rather than silently passed, which is why
overall status is `human_needed` rather than `passed`. This does not represent a defect in the
delivered work; it is an honest disclosure of an unverifiable-in-this-environment claim.

---

*Verified: 2026-07-21T14:07:13Z*
*Verifier: Claude (gsd-verifier)*
