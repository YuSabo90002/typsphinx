---
created: 2026-08-11
title: "`test_docs_contract_claims_gate.py` fails on Windows CI: `Path.relative_to()` returns backslash paths, hardcoded sets use forward slashes"
area: tests, ci
resolves_phase: null
severity: warning
source: 45.2-05 SC#4 CI dispatch (run 31445582363), Test Python 3.12/3.13 on windows-latest
files:
  - tests/test_docs_contract_claims_gate.py
---

## Problem

`tests/test_docs_contract_claims_gate.py::TestContractClaimPageEnumerationIsClosed` fails on both
`py312` and `py313` on `windows-latest`, and nowhere else. Verbatim (py313, CI run `31445582363`,
job `93638966551`):

```
AssertionError: Discovered claim pages minus exclusions
['docs\\source\\changelog.rst', 'docs\\source\\examples\\advanced.rst',
 'docs\\source\\user_guide\\configuration.rst', 'docs\\source\\user_guide\\templates.rst']
!= the reviewed set
['docs/source/examples/advanced.rst', 'docs/source/user_guide/configuration.rst',
 'docs/source/user_guide/templates.rst']
```

and

```
AssertionError: ['docs/source/changelog.rst'] are in EXCLUDED_CLAIM_PAGES but no longer
make a contract claim under the current scan -- a stale exclusion. Remove them from
EXCLUDED_CLAIM_PAGES.
```

Root cause: `_discovered_claim_pages()` (line 168-173) computes
`str(page.relative_to(REPO_ROOT))`, and on Windows `pathlib.Path.relative_to()` renders with
backslash separators (`docs\source\changelog.rst`). `REVIEWED_CLAIM_PAGES` (line 134-140) and
`EXCLUDED_CLAIM_PAGES` (line 142-148) are hardcoded with forward-slash literals
(`"docs/source/..."`). The comparison is therefore never platform-portable — it can only ever
pass on POSIX runners.

This is a genuine, pre-existing defect in the test file itself, unrelated to Phase 45.2's
`tox-uv` -> `tox-uv-bare` / `deps` -> `extras` toolchain fix. `test_docs_contract_claims_gate.py`
was added 2026-08-10 by Phase 45.1 plan 07 (`a6fa38b`), **after** the last pre-Phase-45.2 CI run on
this branch (`31287786840`, 2026-08-09) -- so 45.2-05's SC#4 dispatch is this test's first-ever
real exercise on a Windows CI runner, on any branch. It would have failed identically on Windows
regardless of `package = wheel` vs `package = editable` (45.2-05's own tox.ini fix) or any other
change in this phase; it is orthogonal to `[project] dependencies`, `pyproject.toml`, `tox.ini`'s
`requires`/`extras` lines, and `uv.lock`.

Confirmed unrelated: every non-Windows job in the same CI run (ubuntu, macos, both Python
versions, lint, type, coverage, build, both integration jobs) passed; only the two
`windows-latest` matrix legs fail, both on exactly these two assertions.

## Acceptance

- `_discovered_claim_pages()` normalizes to forward-slash (POSIX-style) relative paths on every
  platform -- e.g. `str(page.relative_to(REPO_ROOT).as_posix())` instead of
  `str(page.relative_to(REPO_ROOT))` -- so the comparison against `REVIEWED_CLAIM_PAGES`/
  `EXCLUDED_CLAIM_PAGES` is platform-independent.
- `tests/test_docs_contract_claims_gate.py::TestContractClaimPageEnumerationIsClosed` passes on a
  real Windows CI run (both `py312` and `py313`).
- No other test in this module regresses on any platform.
