# Archive — 006-release-0-10-0

Milestone: release-0-10-0
Shipped: 2026-11-03
Final verdict: all criteria met; project verify passed
Waves: 1  Tasks: 2 done / 2 total  Review cycles used: 1
Carried forward: none

## Success criteria at ship

| Criterion | Verdict | Evidence |
|-----------|---------|----------|
| Version and build: `pyproject.toml` version is `0.10.0`; README.md's status line names v0.10.0 (no remaining "v0.9.8" status claim); on the final HEAD, `uv build` followed by `uv run twine check dist/*` passes and the built wheel and sdist are named `typsphinx-0.10.0`. | met | .project/review/wave-1.cycle1.md — SC1; evidence: `pyproject.toml:7` 0.10.0. README status names v0.10.0, and no `v0.9.8` remains in README.md. At review HEAD a045accf, the reviewer's `uv build -o <mktemp>` built `typsphinx-0.10.0-py3-none-any.whl` and `typsphinx-0.10.0.tar.gz`, and `uv run twine check` gave `PASSED` for both. E1 and N2 are dismissed. |
| CHANGELOG release section (surface: CHANGELOG.md release notes): `## [Unreleased]` contains only `### Planned for Future Releases`; `## [0.10.0] - <date of the release-prep commit>` sits directly above `## [0.9.8]`, opens with a lead paragraph that names the codly 2.0.0 breaking change, the shared `/_typsphinx/deps.typ` contract and the custom-template migration, and holds every entry that was under `## [Unreleased]` at 81af8d6b except the Planned list; the link block has `[Unreleased]` comparing `v0.10.0...HEAD` and `[0.10.0]` pointing at `releases/tag/v0.10.0`, with `[0.9.8]` kept. `uv run python scripts/extract_changelog_section.py 0.10.0` exits 0 and prints a section containing `codly`, `2.0.0` and `deps.typ`. | met | .project/review/wave-1.cycle1.md — SC2; evidence: The extracted section starts with the breaking-change lead and is followed by `### Added` and `### Changed`. Everything that was under the 81af8d6b `[Unreleased]`, except the Planned list, appears verbatim in the 0.10.0 section. The link block lines are present. E2 (held-out boundary): the heading date 2026-11-03 equals the commit date of b85cc016, the commit that introduced the heading (`git log -S`). N1 (judgment): the lead paragraph is the first text users read under 0.10.0. It names "codly is upgraded from 1.3.0 to 2.0.0", the `<outdir>/_typsphinx/deps.typ` public contract and the "Migrating from codly 1.3" note, so the breaking change is neither omitted nor buried. Non-blocking: the notes have no Python 3.14 entry, because none existed under Unreleased at 81af8d6b (see the T001 warning). |
| CHANGELOG order: every `## [x.y.z…]` release heading in CHANGELOG.md appears in strictly descending version order (so `## [0.1.0b1]` is below `## [0.2.0]`), and the moved 0.1.0b1 section's text is unchanged. | met | .project/review/wave-1.cycle1.md — SC3 |
| charged-ieee identical output (surface: examples/charged-ieee PDFs): building approach1 and approach2 with `typstpdf` produces PDFs whose extracted abstract text, including its line breaks, is identical; the README's identical-output claim is kept. | met | .project/review/wave-1.cycle1.md — SC4; evidence: The reviewer's fresh typstpdf builds of both approaches gave byte-equal abstract text, line breaks included. README.md:154 keeps the identical-output claim. The pre-fix conf.py reproduced the difference. E4 and N4 are dismissed. |
| charged-ieee README name (surface: examples/charged-ieee/README.md): the README contains no "sphinx-typst"; the three occurrences read "typsphinx". | met | .project/review/wave-1.cycle1.md — SC5; evidence: README has 0 "sphinx-typst" matches. The diff changes exactly lines 3, 7 and 150 to "typsphinx". E5 and N5 are dismissed. |
| Release gate follows the version: the release-gate test asserts the 0.10.0 link block (`[Unreleased]` → `v0.10.0...HEAD`, `[0.10.0]` → `releases/tag/v0.10.0`) and no test asserts the `[Unreleased]` link still compares from `v0.9.8`. | met | .project/review/wave-1.cycle1.md — SC6 |
| On the final HEAD, `LC_ALL=C uv run pytest tests/` (with `--extra dev --extra docs` installed) reports 0 failed, and `black --check .`, `ruff check .`, `mypy typsphinx/` are clean. | met | .project/review/wave-1.cycle1.md — SC7 |

## Contents

- build/evidence.json
- build/verify-ledger.jsonl
- intent/INTENT.md
- plan/PLAN.md
- research/DOCS-AUDIT.md
- research/SYNTHESIS.md
- research/evidence-codebase.md
- review/FINAL.md
- review/final-gap-1.md
- review/wave-1.cycle1.md
- tasks/T001-release-0-10-0-prep.md
- tasks/T002-charged-ieee-identical-abstract-and-name.md

## Notes

- none
