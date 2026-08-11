---
id: SEED-003
status: dormant
planted: 2026-08-10
planted_during: v0.7.1 (bug-fix round) — Phase 45.2 discussion
trigger_when: when relevant
scope: tooling
---

# SEED-003: Split the `dev` extra into PEP 735 `[dependency-groups]` so each tox environment installs only what it needs

**Captured during the Phase 45.2 discussion (2026-08-10)** as the deliberately-rejected
alternative to that phase's decision D-06. Phase 45.2 chose `extras = dev` because it keeps
`pyproject.toml`'s only change inside the `dev` extra, which its own SC#7 requires and which
Phase 46's SC#3 depends on. This seed is the better long-term shape, deferred on scope grounds
rather than on merit.

## Why This Matters

`tox.ini` uses `runner = uv-venv-lock-runner` on every environment. That runner builds each env
from `uv.lock` via `uv sync`, so it can only install what `pyproject.toml` declares — extras and
dependency-groups. `tox.ini`'s own `deps = …` lists are silently ignored (this is the defect
Phase 45.2 fixes as D-05).

With `extras = dev`, every tox environment installs the whole `dev` extra. Measured 2026-08-10:
`.tox/lint` currently holds 25 distributions; the `dev` extra adds 13 direct packages
(`pytest`, `pytest-cov`, `black`, `ruff`, `mypy`, `tox`, `tox-uv-bare`, `pre-commit`,
`types-docutils`, `twine`, `build`, `pypdf`, `pillow`) plus transitive deps. A `lint` environment
that needs only `black` and `ruff` ends up carrying `twine`, `build`, `pillow` and `pre-commit`,
and the same cost is paid by every CI job.

The PEP 735 shape:

```toml
[dependency-groups]
test = ["pytest>=8.4,<10", "pytest-cov>=4.0", "pypdf>=6.14,<7", "pillow>=12.3,<13"]
lint = ["black>=26,<27", "ruff>=0.15,<0.16"]
type = ["mypy>=1.13,<3.0", "types-docutils>=0.21"]
```

```ini
[testenv:lint]
dependency_groups = lint
```

This is the form `uv` and `tox-uv` document as preferred, and it makes each environment's real
tool surface explicit rather than inherited.

## Open Questions This Seed Must Answer

- What happens to the existing `dev` extra — kept as an aggregate that references the groups, or
  retired in favour of them? Contributors currently install with `uv sync --extra dev` and
  `pip install -e ".[dev]"`, and `docs/source/contributing.rst` documents that form.
- How large is the resulting `uv.lock` diff, and does anything in CI (`uv sync --extra dev
  --locked`) need to change in lockstep?

## When to Surface

**Trigger:** when relevant — most naturally at the next milestone that touches build/dev tooling,
or alongside the separate `ruff` generic-linux-ELF item Phase 45.2 routes out (see that phase's
CONTEXT `<deferred>`).
