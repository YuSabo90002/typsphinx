# Plan — typsphinx

Project verify: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/`

## Config

- max_review_cycles: 3
- wave_budget: none
- review_panel: off
- finding_skeptics: off

## Wave 1 — housekeeping and Python 3.14

Goal: CLAUDE.md matches the code, the gsd-pi evidence files and their gate checks are gone, three stale doc claims are fixed (T001), and Python 3.14 is declared in classifiers, black, CI and tox and passes `tox -e py314` (T002).
Review depth: full

## Surface contract

### CLAUDE.md — T001

Criteria: SC1
Entry: open `CLAUDE.md`
States: success — Architecture lists `template_registry.py`, `removed_config.py`, `pathfmt.py` with roles; Tests describes the `tests/fixtures/` subprocess-gate convention and `tests/roots/` holding only `test-basic`; CI statements name ubuntu/windows/macos × py312/py313/py314; error — any of these missing or a "py312–py313" matrix statement remains
Walkthrough:
1. Open CLAUDE.md § Architecture and find an entry for each of the three modules.
2. Open § Tests and confirm the fixture-subprocess convention and `tests/roots/` statement.
3. Search CLAUDE.md for `py312–py313` and confirm no matrix statement remains; confirm the CI bullet names the three OSes and py312/py313/py314.

### README.md — T001

Criteria: SC4
Entry: open `README.md` at the Features codly bullet
States: success — no "Automatic line numbering"; states line numbers appear with `:linenos:`; error — old claim remains
Walkthrough:
1. Open README.md and find the "Code blocks with syntax highlighting" bullet.
2. Confirm its sub-bullet says line numbers appear for code blocks with `:linenos:`.

### CHANGELOG.md — T001

Criteria: SC5
Entry: open `CHANGELOG.md` at `## [Unreleased]` → `### Planned for Future Releases`
States: success — "Glossary generation" absent, the other three items and the heading kept, released sections unchanged; error — item still listed or a released section edited
Walkthrough:
1. Open the Unreleased `### Planned for Future Releases` list and confirm "Glossary generation" is gone.
2. Confirm `git diff` touches no line below `## [0.9.8]`.

### examples/charged-ieee/README.md — T001

Criteria: SC6
Entry: open `examples/charged-ieee/README.md` at the limitations bullets
States: success — says setting both `typst_package` and `typst_template` is unsupported, the build warns and ignores `typst_package`; error — "cannot be set together" claim remains
Walkthrough:
1. Open the README limitations list.
2. Confirm the `typst_package` / `typst_template` bullet states the warn-and-ignore behaviour.

## Intent coverage

| Criterion | Task | Acceptance |
|-----------|------|------------|
| SC1 | T001 | AC1 |
| SC2 | T001 | AC2 |
| SC3 | T002 | AC1 |
| SC4 | T001 | AC3 |
| SC5 | T001 | AC4 |
| SC6 | T001 | AC5 |
| SC7 | T002 | AC2 |

## Held-out checks

| Edge | Task | Test |
|------|------|------|

## Dependency notes

- T001 and T002 are independent (disjoint `files`). DOCS-AUDIT queue #1–#3 (fix-doc) are folded into T001 as SC4–SC6; #4–#5 are resolved by T001's file deletion (SC2).
- T002 owns SC7 (whole-repository green); its Verify runs the full suite on its own landing base.
