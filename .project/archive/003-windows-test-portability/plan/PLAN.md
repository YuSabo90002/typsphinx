# Plan — typsphinx

Project verify: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev --extra docs && LC_ALL=C uv run pytest tests/ && uv run black --check . && uv run ruff check . && uv run mypy typsphinx/`

## Config

- max_review_cycles: 3
- wave_budget: none
- review_panel: off
- finding_skeptics: off

## Wave 1 — Windows-portable tests and README tree

Goal: the eight Windows-only failures become platform-independent, proven on Linux by simulating Windows conditions, and README's Project Structure lists `typst_deps.py`.
Review depth: full

## Surface contract

### README.md Project Structure section — T001

Criteria: SC4
Entry: open `README.md` and go to the `### Project Structure` heading
States: success — the tree under `typsphinx/` lists `typst_deps.py` with the other modules; error — the tree omits it
Walkthrough:
1. Open README.md at `### Project Structure`.
2. Confirm the fenced tree lists `typst_deps.py` under `typsphinx/` alongside `builder.py`, `writer.py`, `translator.py`, `template_engine.py`, `pdf.py`, and `templates/`.

## Intent coverage

| Criterion | Task | Acceptance |
|-----------|------|------------|
| SC1 | T001 | AC1 |
| SC2 | T001 | AC2 |
| SC3 | T001 | AC3 |
| SC4 | T001 | AC4 |
| SC5 | T001 | AC5 |

## Held-out checks

| Edge | Task | Test |
|------|------|------|
| E1 | T001 | tests/test_template_dependency_drift_gate.py |
| E3 | T001 | tests/test_hand_compile_root_gate.py |

## Dependency notes

- Single task; no dependencies. DOCS-AUDIT queue #1 (fix-doc) is folded into T001 as SC4.
