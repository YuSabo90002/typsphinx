# Intent — typsphinx

Lane: standard   <!-- six independent deliverables (test, CHANGELOG/README, CLAUDE.md, config removal, doc fixes, release readiness) exceed the two-task quick bound -->

Review panel: off

Finding skeptics: off

Surfaces: CHANGELOG.md release notes, sphinx-build console output

## Summary

typsphinx's README and CHANGELOG present 0.9.8 as released, but no `v0.9.8` tag exists and PyPI still serves 0.9.7, so users installing typsphinx do not get the Graphviz rendering or bibliography support the docs describe. Inspection also found four loose ends: a graphviz test that fails by construction on the maintainer's dev shell, a stale CLAUDE.md, an inert `typst_debug` config value, and small stale doc claims. This milestone clears those loose ends and leaves `main` release-ready as 0.9.8 (Unreleased folded into 0.9.8). Tagging `v0.9.8` and confirming PyPI happen after the milestone PR merges, as a separate owner-approved step.

## Problem

Users reading README/CHANGELOG believe 0.9.8 (Graphviz diagrams via diagraph) is installable; `pip install typsphinx` gives 0.9.7. The maintainer cannot get a green full local suite on the NixOS dev shell because `test_no_graphviz_binary_is_installed` asserts no `dot` on PATH while `flake.nix` provisions graphviz for the local HTML docs build. CLAUDE.md, loaded into every agent, describes functions and counts that no longer exist and a retired GSD Core workflow. `typst_debug` is registered but read nowhere, contrary to the project rule against inert configuration.

## Users

typsphinx users installing from PyPI (Sphinx authors producing Typst/PDF output); the single maintainer working on NixOS through the direnv devShell; coding agents reading CLAUDE.md.

## Success criteria

1. In the maintainer's direnv devShell, where `dot` is on PATH, `LC_ALL=C uv run pytest tests/test_graphviz_render_gate.py` passes, including the R010 proof that diagrams render without Graphviz, whose build runs with a PATH from which every entry containing an executable `dot` has been removed; `LC_ALL=C uv run pytest tests/` reports 0 failed. `flake.nix` still provisions `pkgs.graphviz`, and a clean `tox -e docs-html` build still emits the rendered `graphviz-*.png` image (local HTML parity kept).
2. In CHANGELOG.md, `## [Unreleased]` contains only `### Planned for Future Releases`; `## [0.9.8] - <date of the release-prep commit>` holds the existing Graphviz entries followed by the former Unreleased bibliography Added/Changed entries; the link block has `[Unreleased]` comparing `v0.9.8...HEAD` and `[0.9.8]` pointing at `releases/tag/v0.9.8`. At the CHANGELOG.md release notes surface, `uv run python scripts/extract_changelog_section.py 0.9.8` prints a section that contains both `Graphviz` and `BibTeX`. README.md's status line names v0.9.8, matching `pyproject.toml` version 0.9.8.
3. In CLAUDE.md, `grep -nE "use_worktrees|#683|baseref-head|base-check" CLAUDE.md` prints nothing; the per-worktree recipe `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` plus running commands via `uv run` remains documented; `grep -n _is_master_document CLAUDE.md` prints nothing; the `@preview` version-sync section names five packages including `diagraph`; the translator line/method figures match the code or are removed; and the `typst_documents` description documents the optional fifth element (template registry key).
4. `typst_debug` is no longer registered in `typsphinx/__init__.py` and is listed in `typsphinx/removed_config.py`. At the sphinx-build console output surface, a `conf.py` that sets `typst_debug` (any value) prints the removed-config warning for it exactly once, the build exits 0, and the emitted `.typ` output is identical to the same project without the setting. `examples/advanced/conf.py` and `examples/advanced/README.md` no longer mention `typst_debug`, and the CHANGELOG 0.9.8 section records the removal.
5. DOCS-AUDIT remediation queue items #3 and #9–#13 are fixed: re-running each item's recorded claim check against the shipped HEAD no longer finds the stale claim.
6. The shipped HEAD is release-ready: the milestone PR to `main` has all six required checks green, and on the shipped HEAD the `pyproject.toml` version is `0.9.8`, `uv run python scripts/extract_changelog_section.py 0.9.8` exits 0, and `uv build` followed by `uv run twine check dist/*` passes.

## Edge coverage

| Edge | Criterion | Category | Disposition | Detail |
|------|-----------|----------|-------------|--------|
| E1 | SC1 | boundary | held-out | every PATH entry that contains an executable `dot` is removed for the proof build, not only the first; the proof passes whether or not the host PATH has `dot` |
| E2 | SC2 | ordering | held-out | within 0.9.8's Added and Changed lists, the existing Graphviz items come first and the former Unreleased bibliography items follow |
| E3 | SC2 | empty | criterion SC2 | |
| E4 | SC2 | boundary | held-out | the 0.9.8 date is the release-prep commit's date and is not corrected to the later tag date |
| E5 | SC3 | empty | criterion SC3 | |
| E6 | SC4 | idempotency | criterion SC4 | |
| E7 | SC5 | none | dismissed | text-only doc corrections with no data shape |
| E8 | SC6 | none | dismissed | read-only checks on one fixed HEAD |

## Prohibitions

| Prohibition | Criterion | Must not | Disposition | Detail |
|-------------|-----------|----------|-------------|--------|
| N1 | SC6 | let the published 0.9.8 differ from the CI-green `main` merge commit | judgment | the post-merge tag `v0.9.8` is placed only on the `main` merge commit whose required checks passed; nothing is published from `gsd-path/M001` |
| N2 | SC6 | delete or overwrite existing release tags or published PyPI releases | judgment | tags up to v0.9.7 and PyPI releases up to 0.9.7 stay untouched |
| N3 | SC2 | claim behaviour the shipped package lacks | judgment | every 0.9.8 CHANGELOG/README claim matches the code at the shipped HEAD |
| N4 | SC1 | none | dismissed | test-harness change; affects no user's output |
| N5 | SC3 | none | dismissed | contributor/agent guidance only; affects no user's output |
| N6 | SC4 | silently change a user's build output | criterion SC4 | |
| N7 | SC5 | none | dismissed | text-only doc corrections; no values, safety or privacy dimension |

## Scope: in

- Rewrite the R010 graphviz proof test to build with `dot` stripped from PATH (SC1).
- Fold Unreleased into 0.9.8 in CHANGELOG.md; align README status (SC2).
- Correct CLAUDE.md: drop GSD Core-specific worktree text, keep the per-worktree uv recipe, fix DOCS-AUDIT #4–#7 (SC3).
- Remove `typst_debug` through `removed_config.py`; remove it from examples (SC4).
- Fix DOCS-AUDIT #3, #9–#13 (SC5).
- Release readiness checks (SC6).

## Scope: out (vetoes)

- Rewriting the 34 code/test comments that cite `.planning/` paths — "全部推奨で" (owner accepted: out of scope this milestone).
- Removing graphviz from `flake.nix` — "dotの扱いはローカルでhtmlビルドを通すのもある" (local HTML build needs `dot`).
- Publishing 0.9.8 from any commit other than the CI-green `main` merge commit.
- Implementing `typst_debug` behaviour (owner chose removal).

## Constraints

- Python 3.12+, black/ruff/mypy clean as CI runs them; Typst `@preview` versions stay in lockstep across `writer.py`, `template_engine.py`, `templates/base.typ`.
- `main` is protected with six required checks; integration mode is `pull-request` — Path opens the PR, the owner merges.
- Releases run through `.github/workflows/release.yml` on a `v*` tag push (PyPI trusted publishing). After the milestone PR merges, Claude pushes `v0.9.8` on the merge commit only with the owner's approval and then confirms `pip install typsphinx==0.9.8`; this is a post-ship step, not a milestone criterion.
- The milestone PR to `main` must have all six required checks green before the owner merges it; `main`'s branch protection enforces this at merge time. It is observed at integration, not judged as a final-review criterion (C2).
- If pre-release checks find a regression, the release stops until it is fixed (owner ruling).
- Test commands that assert warning text run under `LC_ALL=C`.

## Current state (brownfield only)

- **What exists**: Sphinx extension (Python ≥3.12, setuptools, typst-py) adding `typst` and `typstpdf` builders; builder → writer (content file + per-document wrapper) → 8149-line translator; PyPI at 0.9.7, `pyproject.toml` at 0.9.8. Locally 1711 passed / 1 failed / 18 skipped (uv-managed CPython 3.14 sidecar); black, ruff, mypy clean.
- **Must not break**: local HTML docs build rendering graphviz via `flake.nix`'s `pkgs.graphviz`; Typst/PDF graphviz rendering without any `dot` binary (diagraph WASM); existing removed-config warnings; existing tags and PyPI releases.
- **Doc-vs-code rulings**: #1 fix-code (publish v0.9.8; post-merge tag); #2 fix-doc (fold Unreleased into 0.9.8); #3–#7 fix-doc; #8 fix-doc (remove GSD Core worktree text, keep per-worktree uv recipe); #9–#13 fix-doc.
- **Ground truth**: `.project/research/evidence-codebase.md`, `.project/research/DOCS-AUDIT.md`

## Risks

- Dependabot bumps since 2026-09-30 (black, mypy, tox, tox-uv, sphinx-autodoc-typehints) could change CI results on the release-prep HEAD.
- The PATH-stripping test must not also remove tools the proof build needs (the build itself only needs Python and typst-py).

## Open questions

- None.

## Corrections

- C1 2026-11-03: "すまんdotの扱いはローカルでhtmlビルドを通すのもあるし、dotをflakeでインストールするのはどうだ"
- C2 2026-11-03: "本来SC6は書かれる要件ではないってことかな" → ruling "1": SC6's clause "the milestone PR to `main` has all six required checks green" is not a final-review criterion. The PR is opened by ship integration after final review, and `main` branch protection enforces the six checks at merge, so that clause is observed at integration (see Constraints). Final review judges SC6 on its remaining clauses at the reviewed HEAD. The SC6 text is kept verbatim so earlier wave-review quotes stay valid. This was recorded outside `$gsd-path-define` by owner ruling, because GSD Path 1.7.1 has no route from `ship/active` back to define: undo refuses `build: complete milestone`, and build recovery does not reopen ship.
