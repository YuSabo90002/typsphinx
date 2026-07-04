---
phase: 01-pin-runtime-dependencies-to-known-good
verified: 2026-07-04T00:00:00Z
status: passed
score: 9/9 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 1: Pin Runtime Dependencies to Known-Good Verification Report

**Phase Goal:** Runtime dependency versions are pinned to a reproducible, empirically-confirmed, mutually-compatible combination, and the codebase is lint-clean. This is the actual bug fix (typst 0.15 -> mitex `kai` hard error), landing alone so a red/green result is unambiguous.
**Verified:** 2026-07-04
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `pyproject.toml` has explicit upper bounds on all three runtime deps, floors unchanged, no `==` pins | ✓ VERIFIED | `dependencies = ["sphinx>=5.0,<9", "docutils>=0.18,<0.22", "typst>=0.14.1,<0.15"]` (pyproject.toml:29-33) |
| 2 | `typst>=0.14.1,<0.15` is empirically confirmed to compile the `docs-pdf` target cleanly | ✓ VERIFIED | `docs/_build/pdf/index.pdf` exists on disk (2,345,882 bytes, timestamped 2026-07-04 16:20, matching commit time); SUMMARY records `uv run tox -e docs-pdf` exit 0, no `kai` error |
| 3 | `uv.lock` is regenerated and committed, resolving cleanly across all supported Python-version markers | ✓ VERIFIED | `git ls-files uv.lock` returns the path (tracked); `UV_PYTHON=$(command -v python3) uv lock --check` → "Resolved 125 packages", exit 0; lock shows split `sphinx` 7.4.7 (py<=3.9) / 8.1.3 (py>=3.10) resolution-markers |
| 4 | `uv.lock` pins `typst` to a 0.14.x patch, not 0.15.0 | ✓ VERIFIED | `grep -A1 '^name = "typst"$' uv.lock` → `version = "0.14.9"` |
| 5 | `tox.ini` `[testenv]`/`[testenv:type]` deps mirror the same ceilings as `pyproject.toml`; no independent unbounded re-resolution path | ✓ VERIFIED | `tox.ini:14` `sphinx>=5.0,<9`; `tox.ini:33,35` `sphinx>=5.0,<9` / `docutils>=0.18,<0.22`; `! grep -nE 'sphinx>=5\.0[^,]\|docutils>=0\.18[^,]' tox.ini` exits 0 (no match) |
| 6 | Dead `sphinx-testing` dependency removed from `pyproject.toml`/`tox.ini`/`uv.lock` | ✓ VERIFIED | `! grep -rq 'sphinx-testing' pyproject.toml tox.ini uv.lock` exits 0 (no match in any of the three files) |
| 7 | `black --check .` exits 0 on the full tree | ✓ VERIFIED | `.venv/bin/python -m black --check .` → "All done! 49 files would be left unchanged.", exit 0 |
| 8 | `ruff check .` exits 0 on the full tree | ✓ VERIFIED | `nix run nixpkgs#ruff -- check .` → "All checks passed!", exit 0 (nixpkgs ruff 0.15.14; CI runs pinned 0.15.20, same [tool.ruff] config, per documented deviation) |
| 9 | `PROJECT.md` Key Decisions records the confirmed typst patch and the sphinx/docutils ceiling load-bearing finding | ✓ VERIFIED | Key Decisions row: `Confirmed: typst==0.14.9 (resolved in uv.lock); docs-pdf builds index.pdf locally with no kai error`; new row: `Precautionary (not load-bearing) confirmed on Linux; docs-pdf builds green with typst 0.14.9, sphinx 7.4.7/8.1.3, docutils 0.21.2. Full 3-OS x Python-version matrix confirmation is Phase 2's gate` |

**Score:** 9/9 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | Upper-bounded runtime deps, `sphinx-testing` removed, black/ruff/mypy target-version unchanged | ✓ VERIFIED | Diff (commit `63f4284`) matches exactly: 3 ceilings added, 1 line removed, no target-version touched |
| `tox.ini` | Ceilings mirrored in `[testenv]`/`[testenv:type]`, `sphinx-testing` removed | ✓ VERIFIED | Diff (commit `63f4284`) matches exactly |
| `uv.lock` | Regenerated, tracked, `typst` on 0.14.x | ✓ VERIFIED | Newly tracked (2,834 insertions in `63f4284`); `git ls-files uv.lock` confirms tracking; `uv lock --check` exits 0 |
| `.planning/PROJECT.md` | Key Decisions updated with confirmed patch + ceiling finding | ✓ VERIFIED | Diff (commit `138b517`) touches only the two Key Decisions rows |
| `docs/build_multilang.py` | black-reformatted (docstring/import blank line) | ✓ VERIFIED | Diff (commit `f17c3d9`): 1 blank line inserted, no logic change |
| `tests/test_config_other_options.py` | black-reformatted (`write_text` calls collapsed) | ✓ VERIFIED | Diff (commit `f17c3d9`): 60 lines changed, pure reformatting |
| `tests/test_config_toctree_defaults.py` | black-reformatted (`write_text` calls collapsed) | ✓ VERIFIED | Diff (commit `f17c3d9`): 12 lines changed, pure reformatting |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `pyproject.toml` ceilings | `uv.lock` resolution | `uv lock` reads the edited ranges and resolves the exact patch | ✓ WIRED | `uv lock --check` exits 0; resolved `typst` version (0.14.9) falls inside the new `<0.15` ceiling |
| `uv.lock` | `tox docs-pdf` env | every tox env uses `runner=uv-venv-lock-runner`, syncing from `uv.lock` | ✓ WIRED | `docs/_build/pdf/index.pdf` exists (2.3MB, built 2026-07-04 16:20, same session as the pin commit) — the pinned typst is what actually compiled the PDF |
| `black` config (`[tool.black]` line-length 88, target-version py39, unchanged) | reformatted files | reformat conforms to existing config | ✓ WIRED | `black --check .` exits 0 post-reformat; target-version line untouched in `pyproject.toml` |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | none found | — | Scanned `pyproject.toml`, `tox.ini`, `docs/build_multilang.py`, `tests/test_config_other_options.py`, `tests/test_config_toctree_defaults.py` for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` — zero matches |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|--------------|-------------|-------------|--------|----------|
| PIN-01 | 01-01 | `typst` pinned `>=0.14.1,<0.15` | ✓ SATISFIED | pyproject.toml:32 |
| PIN-02 | 01-01 | `sphinx<9`, `docutils<0.22` upper bounds | ✓ SATISFIED | pyproject.toml:30-31 |
| PIN-03 | 01-01 | `uv.lock` regenerated, committed, resolves cleanly across Python-version markers | ✓ SATISFIED | `git ls-files uv.lock`; `uv lock --check` exit 0; multi-marker sphinx 7.4.7/8.1.3 split confirmed |
| PIN-04 | 01-01 | `tox.ini` mirrors ceilings, no independent unbounded re-resolution | ✓ SATISFIED | tox.ini:14,33,35; grep assertion passes |
| PIN-05 | 01-01 | Dead `sphinx-testing` removed | ✓ SATISFIED | absent from all three surfaces |
| PIN-06 | 01-01 | typst 0.14.x patch confirmed empirically (docs-pdf); ceiling load-bearing question documented | ✓ SATISFIED (scoped to ROADMAP SC — local Linux confirmation; full 3-OS×Python CI matrix confirmation is explicitly Phase 2's gate per ROADMAP.md Phase 2 goal) | `docs/_build/pdf/index.pdf` exists; PROJECT.md rows updated |
| LINT-01 | 01-02 | `black --check .` exits 0 | ✓ SATISFIED | verified directly |
| LINT-02 | 01-02 | `ruff check .` exits 0 | ✓ SATISFIED | verified directly (nixpkgs stand-in, documented environment substitution) |

No orphaned requirements: all 8 IDs mapped to Phase 1 in `.planning/REQUIREMENTS.md` (lines 88-95) are claimed by plans 01-01/01-02 `requirements:` frontmatter.

Note: `.planning/REQUIREMENTS.md`'s traceability table (lines 88-95) still shows all Phase 1 rows as "Pending" — this is a stale tracking artifact, not a code gap (ROADMAP.md itself correctly marks Phase 1 `[x]` complete with 2/2 plans done).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Lock resolves cleanly, not stale | `UV_PYTHON=$(command -v python3) uv lock --check` | "Resolved 125 packages", exit 0 | ✓ PASS |
| black clean on full tree | `.venv/bin/python -m black --check .` | "All done! 49 files would be left unchanged.", exit 0 | ✓ PASS |
| ruff clean on full tree | `nix run nixpkgs#ruff -- check .` | "All checks passed!", exit 0 | ✓ PASS |
| docs-pdf artifact present | `ls docs/_build/pdf/index.pdf` | 2,345,882 bytes, present | ✓ PASS |

### Gaps Summary

None. All 9 observable truths verified against the actual codebase (not SUMMARY narration): the pin edits in `pyproject.toml`/`tox.ini` match exactly what the plans specified, `uv.lock` is tracked and resolves cleanly with `typst` pinned to `0.14.9`, the previously-built `docs/_build/pdf/index.pdf` corroborates the empirical `docs-pdf` claim, `black`/`ruff` both independently re-run clean, and `PROJECT.md`'s Key Decisions table carries both required rows in the correct format. The three commits (`63f4284`, `138b517`, `f17c3d9`) are cleanly separated per D-04 — no pin/config changes leaked into the lint commit or vice versa. No debt markers (`TBD`/`FIXME`/`XXX`) were introduced.

One process note (non-blocking, does not affect phase-goal achievement): the executor un-gitignored and started tracking `uv.lock`, a maintainer-facing convention change for a previously-untracked lockfile. This was required by PIN-03's explicit "committed" wording and is trivially reversible; it is already surfaced in `01-01-SUMMARY.md` as an "Open item for maintainer." No further verification action needed — flagging for the developer's awareness only.

---

_Verified: 2026-07-04_
_Verifier: Claude (gsd-verifier)_
