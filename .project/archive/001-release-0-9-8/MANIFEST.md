# Archive — 001-release-0-9-8

Milestone: release-0-9-8
Shipped: 2026-11-03
Final verdict: all criteria met; project verify passed
Waves: 2  Tasks: 4 done / 4 total  Review cycles used: 1/1
Carried forward: none

## Success criteria at ship

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| In the maintainer's direnv devShell, where `dot` is on PATH, `LC_ALL=C uv run pytest tests/test_graphviz_render_gate.py` passes, including the R010 proof that diagrams render without Graphviz, whose build runs with a PATH from which every entry containing an executable `dot` has been removed; `LC_ALL=C uv run pytest tests/` reports 0 failed. `flake.nix` still provisions `pkgs.graphviz`, and a clean `tox -e docs-html` build still emits the rendered `graphviz-*.png` image (local HTML parity kept). | met | .project/build/verify-ledger.jsonl (last row, commit 5e05288f, exit_code 0); .git/gsd-path/dispatch/gsd-path-M001/T001/manual-2026-11-02T161848+0000/verify.json; flake.nix:177; .project/review/wave-1.cycle1.md T001 |
| In CHANGELOG.md, `## [Unreleased]` contains only `### Planned for Future Releases`; `## [0.9.8] - <date of the release-prep commit>` holds the existing Graphviz entries followed by the former Unreleased bibliography Added/Changed entries; the link block has `[Unreleased]` comparing `v0.9.8...HEAD` and `[0.9.8]` pointing at `releases/tag/v0.9.8`. At the CHANGELOG.md release notes surface, `uv run python scripts/extract_changelog_section.py 0.9.8` prints a section that contains both `Graphviz` and `BibTeX`. README.md's status line names v0.9.8, matching `pyproject.toml` version 0.9.8. | met | CHANGELOG.md:8-16, :1560, :1585; README.md:344; pyproject.toml:7; tests/test_release_0_9_8_docs_gate.py; .project/review/wave-2.cycle1.md T004/AC1-AC6 |
| In CLAUDE.md, `grep -nE "use_worktrees\|#683\|baseref-head\|base-check" CLAUDE.md` prints nothing; the per-worktree recipe `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` plus running commands via `uv run` remains documented; `grep -n _is_master_document CLAUDE.md` prints nothing; the `@preview` version-sync section names five packages including `diagraph`; the translator line/method figures match the code or are removed; and the `typst_documents` description documents the optional fifth element (template registry key). | met | CLAUDE.md:64, :68, :107-112; .project/review/wave-1.cycle1.md T003 |
| `typst_debug` is no longer registered in `typsphinx/__init__.py` and is listed in `typsphinx/removed_config.py`. At the sphinx-build console output surface, a `conf.py` that sets `typst_debug` (any value) prints the removed-config warning for it exactly once, the build exits 0, and the emitted `.typ` output is identical to the same project without the setting. `examples/advanced/conf.py` and `examples/advanced/README.md` no longer mention `typst_debug`, and the CHANGELOG 0.9.8 section records the removal. | met | typsphinx/removed_config.py:59-60; typsphinx/__init__.py; examples/advanced/conf.py; examples/advanced/README.md; CHANGELOG.md 0.9.8 `### Removed`; .project/review/wave-1.cycle1.md T002 |
| DOCS-AUDIT remediation queue items #3 and #9–#13 are fixed: re-running each item's recorded claim check against the shipped HEAD no longer finds the stale claim. | met | .project/research/DOCS-AUDIT.md remediation queue rows 3, 9-13; CHANGELOG.md:141; docs/S03-ARTIFACT-GATE-EVIDENCE.md:220-227; docs/S04-PUBLISHED-SITE-EVIDENCE.md:839; .project/review/wave-2.cycle1.md T004/AC7 |
| The shipped HEAD is release-ready: the milestone PR to `main` has all six required checks green, and on the shipped HEAD the `pyproject.toml` version is `0.9.8`, `uv run python scripts/extract_changelog_section.py 0.9.8` exits 0, and `uv build` followed by `uv run twine check dist/*` passes. | met | .project/intent/INTENT.md `## Corrections` C2 and `## Constraints`; pyproject.toml:7; scripts/extract_changelog_section.py; .git/gsd-path/dispatch/gsd-path-M001/T004/manual-2026-11-02T162518+0000/verify.json; .project/review/wave-2.cycle1.md T004 |

## Contents

- build/evidence.json
- build/verify-ledger.jsonl
- intent/INTENT.md
- plan/PLAN.md
- research/DOCS-AUDIT.md
- research/RESEARCH.md
- research/SYNTHESIS.md
- research/evidence-codebase.md
- review/FINAL.md
- review/final-gap-1.md
- review/wave-1.cycle1.md
- review/wave-2.cycle1.md
- tasks/T001-r010-stripped-path-proof.md
- tasks/T002-remove-typst-debug.md
- tasks/T003-correct-claude-md.md
- tasks/T004-release-prep-0-9-8.md

## Notes

- none
