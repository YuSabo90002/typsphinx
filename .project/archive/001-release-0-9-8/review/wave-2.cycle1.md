# Review — wave 2, cycle 1

Repo root: /home/yuta/Documents/typsphinx
Review base: 2394c2f0c2e6ffe09bc6f48de22e6765f2cebd89
Inspection mode: reconstructed product (verify sidecar at review base; T004 isolated diff `git diff c76c3e23 e9b854ce`)

Wave verdict: pass
Cycle: 1
Depth: full
Tasks reviewed: 1

## T004 — Fold Unreleased into 0.9.8, fix the remaining stale doc claims, and prove release readiness: pass

Provenance: task `base` c76c3e238a828e75daf1fe922d064afa4979bfb6; landing e9b854ce5d3c19d44eec2bd24fa8d56240313e9b has parent c76c3e23 (`git log -1 --format=%P`), committer date 2026-11-03 01:25:18 +0900. Recorded Verify: `/home/yuta/Documents/typsphinx/.git/gsd-path/dispatch/gsd-path-M001/T004/manual-2026-11-02T162518+0000/verify.json`, base c76c3e23, exit_code 0, regressions []; stdout `34 passed`, `3 passed` (run with `-rs`, no skips listed), `All checks passed!`, twine `PASSED` for wheel and sdist; stderr shows black `1 file would be left unchanged`. Only commit between landing and review base is 2394c2f0, which touches `.project/build/verify-ledger.jsonl` only.

- ✅ T004/AC1 — CHANGELOG.md:8-14: first `## [Unreleased]` holds only `### Planned for Future Releases`; `## [0.9.8] - 2026-11-03` (line 16) `### Added` holds the Graphviz GVZ items then the moved R001-R010 and R013 bibliography items (text byte-identical to the removed Unreleased items per diff), `### Changed` holds the DEG-01 item then the moved README item; `test_first_unreleased_holds_only_planned_for_future_releases` in the recorded 34 passed.
- ✅ T004/AC2 — E2 held-out: `test_0_9_8_graphviz_items_precede_bibliography_items[Added]` and `[Changed]` pass in the recorded second pytest run (`3 passed`); the test classifies each top-level item as exactly one of graphviz/bibliography (asserting exclusivity) and requires both kinds present, so it can fail.
- ✅ T004/AC3 — E4 held-out: `test_0_9_8_date_is_release_prep_commit_date` passes in the recorded `3 passed`. Independently at review base (non-shallow sidecar): `git log --reverse -S'## [0.9.8] - 2026-11-03' --format='%h %cs' -- CHANGELOG.md` prints `e9b854ce 2026-11-03`, the release-prep commit and its committer date; the test reads no tag date.
- ✅ T004/AC4 — CHANGELOG.md:1585 `[Unreleased]: https://github.com/YuSabo90002/typsphinx/compare/v0.9.8...HEAD`, CHANGELOG.md:1560 `[0.9.8]: https://github.com/YuSabo90002/typsphinx/releases/tag/v0.9.8`; README.md:344 `**Status**: Stable (v0.9.8)`; pyproject.toml:7 `version = "0.9.8"`; `test_link_block_targets_v0_9_8` and `tests/test_readme_version_sync.py` in recorded 34 passed.
- ✅ T004/AC5 — recorded Verify chain greps Graphviz, BibTeX and typst_debug in the extractor output (exit 0). Read-only re-observation at review base (`python3 -I scripts/extract_changelog_section.py 0.9.8`): rc=0, Graphviz items first under `### Added` (line 20 onward), 2 `BibTeX` and 3 `typst_debug` occurrences, subsections Added, Changed, Known Limitations, Removed, Fixed.
- ✅ T004/AC6 — CHANGELOG.md `### Removed` in 0.9.8: says `typst_debug` was registered but never read, warns once by name, is ignored, output identical; matches `typsphinx/removed_config.py:59-63` message and absence from `typsphinx/__init__.py` (grep empty); `test_0_9_8_records_typst_debug_removal` passed.
- ✅ T004/AC7 — DOCS-AUDIT re-checks all in recorded 34 passed, and confirmed by reading files at review base: #3 no `0.9.4 entry` text, Fixed item (CHANGELOG.md:141) names the 0.6.0 entry and the "Graceful degradation" line is at CHANGELOG.md:992 inside `## [0.6.0]` (line 950); #9 S03 appended `## Correction` citing run 41152681591, original sentence kept (append-only); #10 S04 appended `## Post-merge results` with A1/A2/A3 measured results and merge `6c55e5b1` PR #165; #11/#12 `examples/advanced/README.md` has no `_templates/`, no `uncomment` text, no `typst_debug`; #13 charged-ieee README no longer says "on both approaches" and states Approach 2 hardcodes department/organization/location and derives email, matching `examples/charged-ieee/approach2/source/_typst/_template.typ:30-33`. `tests/test_examples_charged_ieee_gate.py` and `tests/test_bundle_layout_sweep_gate.py` are in the recorded 34 passed.
- ✅ T004/AC8 — pyproject.toml version 0.9.8; recorded Verify: extractor exit 0, `rm -rf dist && uv build` built `typsphinx-0.9.8.tar.gz` and `typsphinx-0.9.8-py3-none-any.whl`, `twine check` PASSED for both. The PR's six required checks are explicitly out of this task (ship-owned per PLAN.md Dependency notes).
- ✅ T004/IF1 — `typsphinx/removed_config.py:59` key `"typst_debug"` with message starting `'typst_debug' was removed in v0.9.8` (landed by T002 at base, unchanged by T004).
- ✅ T004/IF2 — `examples/advanced/README.md` contains no `_templates/` line and no "edit `conf.py` and uncomment" text (grep empty; `test_audit_11`/`test_audit_12` passed).

Warnings (non-blocking):
- Coder deviation recorded in Log: #13 text names the directory `approach2/source/_typst/` rather than the `_template.typ` file because `tests/test_bundle_layout_sweep_gate.py` forbids that basename in the README; the AC (no "on both approaches", Approach 2 hardcoding stated) is still met.
- E4 test skips on shallow checkouts, so in CI (`actions/checkout` depth 1) it never runs; it ran and passed in the isolated non-shallow Verify sidecar, which is the held-out evidence.

Contract violations (blocking):
- none — changed paths are exactly the six declared `files` plus the task file; task-file changes are orchestrator fields `status`, `agent`, `base` and append-only Log entries. No tag `v0.9.8` exists in the sidecar (`git tag -l v0.9.8` empty).

## Intent coverage

### SC2 — In CHANGELOG.md, `## [Unreleased]` contains only `### Planned for Future Releases`; `## [0.9.8] - <date of the release-prep commit>` holds the existing Graphviz entries followed by the former Unreleased bibliography Added/Changed entries; the link block has `[Unreleased]` comparing `v0.9.8...HEAD` and `[0.9.8]` pointing at `releases/tag/v0.9.8`. At the CHANGELOG.md release notes surface, `uv run python scripts/extract_changelog_section.py 0.9.8` prints a section that contains both `Graphviz` and `BibTeX`. README.md's status line names v0.9.8, matching `pyproject.toml` version 0.9.8.: pass
- ✅ Structure, date, link block and README/pyproject as in T004/AC1, AC3, AC4. E2 (held-out): `test_0_9_8_graphviz_items_precede_bibliography_items[Added|Changed]` passed in recorded Verify (`3 passed`). E3 is `criterion SC2` (empty Unreleased) — CHANGELOG.md:8-14. E4 (held-out): `test_0_9_8_date_is_release_prep_commit_date` passed; heading date 2026-11-03 equals `%cs` of e9b854ce, no tag date read.
- ✅ CHANGELOG.md release notes surface walkthrough (PLAN.md Surface contract): step 2 recorded in Verify chain (extractor exit 0, greps Graphviz/BibTeX/typst_debug) and re-observed read-only at review base (rc=0; Graphviz Added/Changed items before bibliography items, then `### Removed` typst_debug entry); step 3 CHANGELOG top shows only Planned under Unreleased, dated heading, both links; step 4 README.md:344 Stable (v0.9.8) = pyproject.toml:7.
- ✅ N3 (judgment): 0.9.8 claims checked against code at review base — `grep -rc bibtex typsphinx/` totals 0 as claimed; `docs/source/user_guide/bibliography.rst` exists; `diagraph` imported in `writer.py`, `templates/base.typ`, used in `translator.py`; `_visit_graphical_placeholder` keeps two callers (inheritance diagram translator.py:6788, external-dot path translator.py:6761); `typst_debug` removal wording matches `removed_config.py` and never claims it did anything; README.md:34 bibliography claim matches the same facts.

### SC4 — `typst_debug` is no longer registered in `typsphinx/__init__.py` and is listed in `typsphinx/removed_config.py`. At the sphinx-build console output surface, a `conf.py` that sets `typst_debug` (any value) prints the removed-config warning for it exactly once, the build exits 0, and the emitted `.typ` output is identical to the same project without the setting. `examples/advanced/conf.py` and `examples/advanced/README.md` no longer mention `typst_debug`, and the CHANGELOG 0.9.8 section records the removal.: pass
- ✅ CHANGELOG part (owned here by T004/AC6): 0.9.8 `### Removed` records the removal, consistent with code. T002-owned parts (registration, console surface, examples) were judged pass in `.project/review/wave-1.cycle1.md` and are unchanged at review base (`__init__.py` has no `typst_debug`; `removed_config.py:59`; examples grep empty). E6 and N6 are `criterion SC4`, covered in wave 1.

### SC5 — DOCS-AUDIT remediation queue items #3 and #9–#13 are fixed: re-running each item's recorded claim check against the shipped HEAD no longer finds the stale claim.: pass
- ✅ Per T004/AC7: each item's claim from `.project/research/DOCS-AUDIT.md` rows 3, 9, 10, 11, 12, 13 is absent or corrected at review base, and one re-check per item passed in the recorded Verify. #2 (aspirational 0.9.8 dated heading / tag link) is resolved by the owner's fold ruling: the section now holds the folded content dated by the release-prep commit, with the tag published post-merge (out of milestone per INTENT Constraints). E7 and N7 are dismissed.

### SC6 — The shipped HEAD is release-ready: the milestone PR to `main` has all six required checks green, and on the shipped HEAD the `pyproject.toml` version is `0.9.8`, `uv run python scripts/extract_changelog_section.py 0.9.8` exits 0, and `uv build` followed by `uv run twine check dist/*` passes.: pass
- ✅ Wave-owned part (T004/AC8): version 0.9.8, extractor exit 0, `uv build` + `twine check` PASSED for both dists in recorded Verify. The "six required checks green on the PR" subclaim cannot be observed before ship opens the PR; PLAN.md assigns it to ship, and this review does not judge it. E8 dismissed. N1/N2 (judgment): no tag created or moved (`git tag -l v0.9.8` empty; landing diff touches no tags or release workflow); nothing published from `gsd-path/M001`.

## Summary for orchestrator

- blocked findings: none
- repeat offenders: none
- warnings worth a human eye: SC6 PR-checks subclaim remains for ship; E4 test skips in CI's shallow checkout by design.
