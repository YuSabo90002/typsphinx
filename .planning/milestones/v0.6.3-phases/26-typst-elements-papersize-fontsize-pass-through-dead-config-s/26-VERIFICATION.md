---
phase: 26-typst-elements-papersize-fontsize-pass-through-dead-config-s
verified: 2026-07-24T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 26: `typst_elements` papersize/fontsize Pass-Through Verification Report

**Phase Goal:** A user who sets `papersize`/`fontsize` via `typst_elements` in `conf.py` sees them applied in the compiled output, with an unknown key failing loudly and baseline Sphinx metadata never leaking into the template.
**Verified:** 2026-07-24
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (mapped to ROADMAP Success Criteria)

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|------|--------|----------|
| 1 | SC#1: `typst_elements={"papersize":"us-letter"}` reaches `project()` as a quoted Typst string; compiled PDF uses that paper size | ✓ VERIFIED | `typsphinx/template_engine.py:322-325` — papersize passed through as plain `str` (STRING emission kind). `tests/test_typst_elements_pass_through_gate.py::TestPapersizePositiveGate` — real `-b typstpdf` build asserts `'papersize: "us-letter",'` (quoted) present in the show-rule region AND a valid `%PDF`-magic file is produced. `base.typ:55` forwards `paper: papersize` into `page()`, so a successful real Typst compile is proof the string was accepted as a valid paper name. Test run: PASS (see below). |
| 2 | SC#2: `typst_elements={"fontsize":"20pt"}` reaches `project()` as an UNQUOTED Typst length, proven by a SEPARATE fixture from papersize | ✓ VERIFIED | `template_engine.py:322-325` wraps fontsize in `RawTypst(value)` (RAW emission kind); `_format_typst_value` line 516 has the `isinstance(value, RawTypst)` branch checked BEFORE the `str` branch (line 524) — confirmed by direct file read. `tests/…gate.py::TestFontsizePositiveGate` uses a SEPARATE fixture dir (`fontsize_positive/`) and SEPARATE build; asserts `"fontsize: 20pt,"` (unquoted) present AND `'fontsize: "20pt"'` (quoted form) absent — the double-formatting-trap guard. Real compile produces valid PDF. |
| 3 | SC#3: An unrecognized `typst_elements` key fails loudly (raises, aborts build) rather than silently dropping or emitting an undeclared kwarg | ✓ VERIFIED | `template_engine.py:315-321` — `ELEMENTS_ALLOWLIST` membership check runs BEFORE the key is added to `params`; raises `sphinx.errors.ExtensionError` naming the key + listing supported keys. `tests/…gate.py::TestUnknownKeyNegativeGate` — real `sphinx-build -b typst` on a fixture with `bogus_unknown_key` exits non-zero (`test_build_exits_non_zero`), and no emitted `.typ` anywhere in the build tree carries the bogus key as a kwarg (`test_no_master_carries_the_bogus_key_as_a_kwarg`). Durable reconstruction (`TestPreFixBasisFailureProof::test_undeclared_kwarg_basis_raises`) proves a real `typst.compile()` raises against an undeclared-kwarg splice — the standing red proof of why the allowlist matters. |
| 4 | SC#4: Baseline Sphinx metadata (`copyright`, etc.) never leaks into `project()` | ✓ VERIFIED | `writer.py:199-207` — the gathered `sphinx_metadata` dict no longer contains a `"copyright"` key at all (structural, not filtered) and `typst_elements` is passed as `map_parameters(sphinx_metadata, typst_elements=typst_elements)` — a SEPARATE argument, never merged via `.update()`. `grep -n "sphinx_metadata.update"` returns nothing in writer.py. `tests/…gate.py::TestPapersizePositiveGate::test_copyright_never_leaks_into_show_rule_region` — a distinctive copyright canary in the fixture's `conf.py` never appears in the emitted show-rule region (checked both as literal string and bare `copyright:` key). Durable reconstruction `test_leaked_copyright_basis_raises` proves a real compile raises against a spliced-in copyright kwarg. |
| 5 | SC#5: `templates/base.typ` is byte-unchanged — 100% Python-side fix | ✓ VERIFIED | `sha256sum typsphinx/templates/base.typ` = `1d2733642a6d5540e6d8ff6786f0d35516168a3301abef96e2125f60c04751ea`, exactly matching the plan-recorded pre-change hash. `git log --oneline -- typsphinx/templates/base.typ` shows the file's last touch predates this phase entirely (commit `636eea3`, Phase 21). `git diff --exit-code typsphinx/templates/base.typ` exits 0 (no working-tree changes either). |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/template_engine.py` | `RawTypst` marker, `ELEMENTS_ALLOWLIST` constant, `_format_typst_value` RawTypst branch, `map_parameters(..., typst_elements=)` param | ✓ VERIFIED | `RawTypst` (frozen dataclass, `source: str` field) at L18-33; `_ElementsEmissionKind` sentinel L36-41; `ELEMENTS_ALLOWLIST` L54-57 (`papersize`→STRING, `fontsize`→RAW); `map_parameters` signature L231-234 with `typst_elements: Dict[str, Any] \| None = None`; allowlist merge logic L306-325. |
| `typsphinx/writer.py` | `map_parameters` called with `typst_elements` as a separate argument; dead `copyright` key dropped | ✓ VERIFIED | L199-207 gather dict has no `"copyright"` key; L215 fetches `typst_elements = getattr(config, "typst_elements", {})`; L218-220 calls `template_engine.map_parameters(sphinx_metadata, typst_elements=typst_elements)`. |
| `tests/test_template_engine.py` | New unit tests: RawTypst emission, allowlist merge, unknown-key raise, copyright-not-in-params | ✓ VERIFIED | `TestTypstElementsPassThrough` class present with 10 tests (papersize-as-str, fontsize-as-RawTypst, unknown-key raise w/ message assertion, copyright non-leak alone and combined, no-arg backward-compat, end-to-end render shape). All pass. |
| `tests/fixtures/typst_elements_pass_through_gate/` | Fixture project(s) for the 4 required real-compile cases | ✓ VERIFIED | 3 fixture dirs exist: `papersize_positive/`, `fontsize_positive/`, `unknown_key_negative/` — each with `conf.py` + `index.rst`. Content inspected — matches described intent exactly (distinctive copyright canary in papersize fixture for the shared SC#4 assertion). |
| `tests/test_typst_elements_pass_through_gate.py` | GATE-01 real-compile module (mirrors `test_package_only_config_gate.py`) + `TestPreFixBasisFailureProof` | ✓ VERIFIED | 422-line module; `TestPapersizePositiveGate`, `TestFontsizePositiveGate`, `TestUnknownKeyNegativeGate`, `TestPreFixBasisFailureProof` — 10 tests total, all real `sys.executable -m sphinx` subprocess builds (no `uv run sphinx-build`), `skipif(not TYPST_AVAILABLE)` correctly applied/omitted per case. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `writer.py` | `template_engine.map_parameters()` | `typst_elements=` keyword argument, structurally separate from `sphinx_metadata` | ✓ WIRED | Confirmed by direct read: L218-220 in writer.py. This is the exact structural closure of the copyright/metadata leak (SC#4/SC#5). |
| `template_engine._format_typst_value` | `RawTypst` isinstance branch | Checked BEFORE the `str` branch | ✓ WIRED | Line 516 (`isinstance(value, RawTypst)`) precedes line 524 (`isinstance(value, str)`) — confirmed by grep line-order. |
| `template_engine.map_parameters` | `ELEMENTS_ALLOWLIST` | Membership check runs BEFORE the key is added to `params` | ✓ WIRED | L316 (`if key not in ELEMENTS_ALLOWLIST: raise ...`) precedes L322-325 (the `params[key] = ...` assignment) — fail-loud-before-add confirmed by direct read. |
| GATE-01 fixtures | real `typst.compile()` | `sphinx-build -b typstpdf` subprocess via `sys.executable -m sphinx` | ✓ WIRED | Confirmed both by source inspection and by running the tests (all 10 pass, including 2 that produce actual `%PDF`-magic files). |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|
| Emitted `#show: project.with(...)` region | `papersize` | `conf.py`'s `typst_elements` dict → `writer.py` → `map_parameters()` → template render | Real user-configured value (`"us-letter"`), not static/hardcoded | ✓ FLOWING |
| Emitted `#show: project.with(...)` region | `fontsize` | Same chain, wrapped in `RawTypst` | Real user-configured value (`"20pt"`), emitted unquoted | ✓ FLOWING |
| `base.typ`'s `page(paper: papersize)` / `set text(size: fontsize)` | consumes the two params | `project()` signature (L39-48, byte-unchanged) | Confirmed the values are genuinely consumed downstream in the frozen template, not merely passed through and ignored | ✓ FLOWING |

### Behavioral Spot-Checks / Probe Execution

This phase is itself a GATE-01 real-compile regression phase — Step 7b/7c collapse into the phase's own required test suite. Ran directly (not relying on SUMMARY claims):

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| GATE-01 fixtures + unit tests | `uv run pytest tests/test_typst_elements_pass_through_gate.py tests/test_template_engine.py -q` | `66 passed in 1.39s` | ✓ PASS |
| Full test suite (authoritative, main tree) | `uv run pytest -q` | `615 passed, 1 skipped in 52.98s` | ✓ PASS — matches the prompt's stated authoritative baseline exactly (615 passed / 1 skipped / 0 failed). No regressions. |
| `templates/base.typ` byte-unchanged | `sha256sum typsphinx/templates/base.typ` + `git diff --exit-code` | hash `1d2733642a6d5540e6d8ff6786f0d35516168a3301abef96e2125f60c04751ea` (matches plan-recorded pre-change hash); `git diff` exit 0 | ✓ PASS |
| Marker/allowlist/param source check | `grep -n "class RawTypst\|ELEMENTS_ALLOWLIST\|def map_parameters" typsphinx/template_engine.py` | present, in expected shape | ✓ PASS |
| Laundering line removed + dead copyright key dropped | `grep -n "sphinx_metadata.update(typst_elements)\|\"copyright\""  typsphinx/writer.py` | no matches (both gone) | ✓ PASS |

Note: this verification ran on the **main tree** (`.git` is a directory, not a worktree pointer file), so the CLAUDE.md worktree-provisioning steps did not apply; `uv run` was used directly per the executor's own instructions.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| CONF-04 | 26-01, 26-02 | `typst_elements` papersize/fontsize pass-through, curated allowlist, fail-loud unknown key, non-leaking baseline metadata | ✓ SATISFIED | All 5 ROADMAP success criteria verified above with direct code inspection + passing real-compile tests. |

**Orphaned requirements check:** `.planning/REQUIREMENTS.md` maps only CONF-04 to Phase 26 (line 56: `| CONF-04 | Phase 26 | Pending |`). No other requirement IDs reference Phase 26. No orphans.

**Informational (non-blocking) note:** `.planning/REQUIREMENTS.md` line 12 (`- [ ] **CONF-04**`) and line 56 (`Pending`), and `.planning/ROADMAP.md` line 179 (`- [ ] **Phase 26: ...**`), still show unchecked/pending bookkeeping despite the code and gate tests being complete and green. This is a documentation/tracking staleness, not a code gap — it is normal for these checkboxes to be flipped during the ship/docs-update workflow rather than mid-phase. Recommend the ship workflow update these markers when this phase is shipped.

### Anti-Patterns Found

None. Scanned `typsphinx/template_engine.py`, `typsphinx/writer.py`, and `tests/test_typst_elements_pass_through_gate.py` for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` — zero matches. No stub returns, no empty handlers, no hardcoded-empty data flowing to output.

### Human Verification Required

None. All 5 success criteria are provable via direct source inspection plus real `typst.compile()`/`sphinx-build` regression tests (already executed by this verifier, not merely claimed by SUMMARY.md). No visual/UX/external-service judgment calls are needed for this backend config-plumbing phase.

### Gaps Summary

No gaps. All 5 ROADMAP Success Criteria are verified against the actual codebase (not SUMMARY claims):

1. Code was read directly — `RawTypst`, `ELEMENTS_ALLOWLIST`, `_ElementsEmissionKind`, and the allowlist merge in `map_parameters()` all exist exactly as described, with correct branch ordering (RawTypst before str; allowlist check before params assignment).
2. `writer.py` was read directly — the laundering line is gone, `copyright` is structurally absent from the metadata dict, `typst_elements` is passed as its own keyword argument.
3. `templates/base.typ` byte-identity was independently verified via sha256 and git history/diff — not just trusted from the SUMMARY's recorded hash.
4. The GATE-01 real-compile test suite (fixtures + test module) was independently executed by this verifier (`66 passed`, and the authoritative full suite `615 passed, 1 skipped`) — not accepted on SUMMARY's word alone.
5. The durable `TestPreFixBasisFailureProof` reconstructions were read and confirmed to assert `pytest.raises(Exception)` only (never matching error text, per D-06) and to derive their splice targets from the current post-fix emitted master (not hand-authored against a historical bug shape) — genuinely durable.

Phase goal achieved: a user configuring `papersize`/`fontsize` via `typst_elements` in `conf.py` will see them reach the compiled Typst/PDF output correctly typed (string vs. unquoted length), an unknown key aborts the build loudly, baseline Sphinx metadata cannot leak in, and `base.typ` was never touched.

---

_Verified: 2026-07-24_
_Verifier: Claude (gsd-verifier)_
